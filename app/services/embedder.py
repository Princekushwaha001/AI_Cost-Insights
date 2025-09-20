# app/services/embedder.py
import os
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")  # avoid TF imports from transformers
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")  # optional: silence HF symlink warning on Windows

import threading
import tempfile
import shutil
from pathlib import Path
import logging

import numpy as np
import faiss

from sqlalchemy import select
from app.db.base import SessionLocal
from app.db import models
from app.configs import EMBEDDING_MODEL_NAME, FAISS_INDEX_FILE

# from app.services import embedder
# model = embedder.get_model()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Lazy-loaded model (avoid heavy import at module import time)
_MODEL = None
_MODEL_LOCK = threading.Lock()


def get_model(model_name: str | None = None):
    """
    Lazy-load SentenceTransformer. Call get_model() where needed instead of importing MODEL at top-level.
    """
    global _MODEL
    if _MODEL is None:
        with _MODEL_LOCK:
            if _MODEL is None:
                from sentence_transformers import SentenceTransformer  # local import avoids TF issues at module import
                mn = model_name or EMBEDDING_MODEL_NAME
                logger.info("Loading SentenceTransformer model: %s", mn)
                _MODEL = SentenceTransformer(mn)
    return _MODEL


# --- text generation for rows (tweak to include any fields you want) ---
def _row_to_text(table_name: str, row) -> str:
    # Compose a short textual snippet for RAG. Modify as needed.
    if table_name == "billing":
        return f"Invoice {getattr(row, 'invoice_month', '')} account {getattr(row, 'account_id', '')} " \
               f"resource {getattr(row, 'resource_id', '')} service {getattr(row, 'service', '')} cost {getattr(row, 'cost', '')}"
    if table_name == "resources":
        return f"Resource {getattr(row, 'resource_id', '')} owner {getattr(row, 'owner', '')} env {getattr(row, 'env', '')} tags {getattr(row, 'tags_json', '')}"
    return ""


# --- FAISS helpers ---
def build_empty_index(dim: int):
    """Return a new IndexIDMap(IndexFlatIP(dim)) for cosine via normalized vectors."""
    quant = faiss.IndexFlatIP(dim)
    return faiss.IndexIDMap(quant)


def build_or_load_faiss(dim: int):
    """
    Load existing FAISS index file if present and dimension matches; otherwise create empty.
    """
    index_path = Path(FAISS_INDEX_FILE)
    if index_path.exists():
        try:
            idx = faiss.read_index(str(index_path))
            # validate dim
            loaded_dim = getattr(idx, "d", None)
            if loaded_dim != dim:
                logger.warning("FAISS index dim mismatch (existing=%s != new=%s). Recreating index.", loaded_dim, dim)
                idx = build_empty_index(dim)
        except Exception as e:
            logger.warning("Could not read existing FAISS index (%s). Recreating. Error: %s", index_path, e)
            idx = build_empty_index(dim)
    else:
        idx = build_empty_index(dim)
    return idx


def atomic_write_faiss(index, path: str):
    """
    Write index to a temp file and move into place to reduce corruption risk.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp.faiss")
    faiss.write_index(index, str(tmp))
    shutil.move(str(tmp), str(p))
    logger.info("Wrote FAISS index to %s", p)


# --- vector id mapping ---
TABLE_CODES = {"billing": 1, "resources": 2}


def _vector_id_for(table_name: str, row_id: int) -> int:
    """
    Create a numeric vector_id from table and row id.
    Ensure row_id < 1e9 for this scheme (safe for typical apps).
    """
    return int(TABLE_CODES.get(table_name, 9) * 10**9 + int(row_id))


# --- embedding / metadata functions ---
def embed_all_and_store():
    """
    Idempotent embedding + metadata upsert:
      - embeds only rows that are not present in vectors.vector_id
      - adds embeddings to FAISS and upserts metadata in DB
    Returns dict with counters.
    """
    session = SessionLocal()
    stats = {"added_vectors": 0, "skipped_existing": 0, "updated_metadata": 0, "errors": 0}
    try:
        # fetch rows
        billing_rows = session.execute(select(models.Billing)).scalars().all()
        resource_rows = session.execute(select(models.Resource)).scalars().all()

        items = []
        for b in billing_rows:
            items.append(("billing", getattr(b, "id"), _row_to_text("billing", b)))
        for r in resource_rows:
            items.append(("resources", getattr(r, "id"), _row_to_text("resources", r)))

        if not items:
            logger.info("No rows to embed.")
            return stats

        # build wanted list of (table,row,text,vid)
        wanted = []
        for table_name, row_id, text in items:
            # row_id may be None if model uses resource_id as PK — handle gracefully
            if row_id is None:
                logger.warning("Skipping item with missing row_id: table=%s text=%s", table_name, text)
                stats["errors"] += 1
                continue
            vid = _vector_id_for(table_name, row_id)
            wanted.append((table_name, row_id, text, int(vid)))

        # get existing vector_ids from DB
        existing_rows = session.query(models.VectorMetadata.vector_id, models.VectorMetadata.snippet).all()
        existing_map = {int(v): s for v, s in existing_rows} if existing_rows else {}

        # Partition wanted items into to-embed (not in DB) and to-upsert (all items)
        to_embed = []
        to_upsert = []  # upsert metadata (we will insert or update snippet)
        for table_name, row_id, text, vid in wanted:
            to_upsert.append((vid, table_name, int(row_id), text))
            if vid in existing_map:
                stats["skipped_existing"] += 1
            else:
                to_embed.append((table_name, row_id, text, vid))

        # embed missing items
        if to_embed:
            texts = [t for (_, _, t, _) in to_embed]
            model = get_model()
            embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True, normalize_embeddings=True).astype("float32")
            dim = embeddings.shape[1]
            index = build_or_load_faiss(dim)

            ids_np = np.array([vid for (_, _, _, vid) in to_embed], dtype="int64")
            try:
                index.add_with_ids(embeddings, ids_np)
            except Exception as e:
                # attempt recreate and add (defensive)
                logger.warning("faiss.add_with_ids failed: %s. Recreating index and retrying.", e)
                index = build_empty_index(dim)
                index.add_with_ids(embeddings, ids_np)

            # persist index
            try:
                atomic_write_faiss(index, FAISS_INDEX_FILE)
            except Exception as e:
                logger.exception("Failed to write FAISS index atomically: %s", e)
                faiss.write_index(index, FAISS_INDEX_FILE)

            stats["added_vectors"] = len(ids_np)

        # Upsert metadata rows in DB (insert new rows, update snippet if changed)
        updated = 0
        inserted = 0
        for vid, tname, row_id, snippet in to_upsert:
            try:
                meta = session.query(models.VectorMetadata).filter(models.VectorMetadata.vector_id == int(vid)).first()
                if meta:
                    changed = False
                    if meta.snippet != snippet:
                        meta.snippet = snippet
                        changed = True
                    if meta.table_name != tname:
                        meta.table_name = tname
                        changed = True
                    if meta.row_id != int(row_id):
                        meta.row_id = int(row_id)
                        changed = True
                    if changed:
                        session.add(meta)
                        updated += 1
                else:
                    session.add(models.VectorMetadata(vector_id=int(vid), table_name=tname, row_id=int(row_id), snippet=snippet))
                    inserted += 1
            except Exception:
                session.rollback()
                logger.exception("Error upserting vector metadata for vid=%s", vid)
        # commit metadata
        try:
            session.commit()
            stats["updated_metadata"] = updated
            # note: inserted may include ones that later caused unique collisions; we'll reflect actual count from DB if needed
        except Exception as e:
            # handle uniqueness/race conditions gracefully by row-by-row retry
            logger.warning("Commit failed during metadata upsert: %s — falling back to row-by-row upsert", e)
            session.rollback()
            for vid, tname, row_id, snippet in to_upsert:
                try:
                    meta = session.query(models.VectorMetadata).filter(models.VectorMetadata.vector_id == int(vid)).first()
                    if meta:
                        if meta.snippet != snippet or meta.table_name != tname or meta.row_id != int(row_id):
                            meta.snippet = snippet
                            meta.table_name = tname
                            meta.row_id = int(row_id)
                            session.add(meta)
                    else:
                        try:
                            session.add(models.VectorMetadata(vector_id=int(vid), table_name=tname, row_id=int(row_id), snippet=snippet))
                        except Exception:
                            session.rollback()
                            continue
                    session.commit()
                except Exception:
                    session.rollback()
            # after fallback, don't raise

        return stats
    finally:
        session.close()


def query_knn(query_text: str, k: int = 5):
    """
    Query FAISS index and fetch metadata rows from DB.
    Returns list of dicts: vector_id, table_name, row_id, snippet, score
    """
    index_path = Path(FAISS_INDEX_FILE)
    if not index_path.exists():
        logger.info("FAISS index not found at %s", index_path)
        return []

    model = get_model()
    q_emb = model.encode([query_text], convert_to_numpy=True, normalize_embeddings=True).astype("float32")
    idx = faiss.read_index(str(index_path))
    D, I = idx.search(q_emb, k)
    results = []
    session = SessionLocal()
    try:
        for score, vid in zip(D[0], I[0]):
            if int(vid) == -1:
                continue
            meta = session.query(models.VectorMetadata).filter(models.VectorMetadata.vector_id == int(vid)).first()
            results.append({
                "vector_id": int(vid),
                "table_name": meta.table_name if meta else None,
                "row_id": meta.row_id if meta else None,
                "snippet": meta.snippet if meta else None,
                "score": float(score)
            })
    finally:
        session.close()
        return results
# at bottom of embedder.py (after get_model definition)
def _get_MODEL_alias():
    # Provide a module-level variable 'MODEL' for backward compatibility.
    # It will lazy-load the model when accessed.
    return get_model()

# Create a read-only alias object: you can import MODEL and call encode()
MODEL = _get_MODEL_alias()










# def embed_all_and_store():
#     """
#     Safe, idempotent embed + metadata writer:
#       - computes embeddings for DB rows not present in vectors table
#       - avoids adding duplicate vector_ids to FAISS
#       - upserts metadata rows (insert new, update snippet for existing)
#     Returns: dict with counts: {"added_vectors": n, "skipped_existing": m, "updated_metadata": u}
#     """
#     session = SessionLocal()
#     added = 0
#     skipped = 0
#     updated_meta = 0
#     try:
#         billing_rows = session.execute(select(models.Billing)).scalars().all()
#         resource_rows = session.execute(select(models.Resource)).scalars().all()
#         items = []
#         for b in billing_rows:
#             text = _row_to_text("billing", b)
#             items.append(("billing", b.id, text))
#         for r in resource_rows:
#             text = _row_to_text("resources", r)
#             items.append(("resources", r.id, text))
#
#         if not items:
#             return {"added_vectors": 0, "skipped_existing": 0, "updated_metadata": 0}
#
#         # Build candidate vector ids
#         wanted = []
#         for table_name, row_id, text in items:
#             vid = _vector_id_for(table_name, row_id)
#             wanted.append((table_name, row_id, text, int(vid)))
#
#         # Query existing vector_ids in DB to avoid duplicates
#         existing_rows = session.query(models.VectorMetadata.vector_id, models.VectorMetadata.snippet).all()
#         existing_map = {int(v): s for v, s in existing_rows}  # vector_id -> snippet
#
#         # Separate lists
#         to_embed_items = []   # (table_name,row_id,text,vid)
#         to_upsert_meta = []   # (vid, table_name, row_id, text)  -- metadata for both new and existing (we will insert/update)
#         for table_name, row_id, text, vid in wanted:
#             to_upsert_meta.append((vid, table_name, row_id, text))
#             if vid in existing_map:
#                 # Exists: skip embedding add into FAISS (we'll update snippet if changed)
#                 skipped += 1
#             else:
#                 to_embed_items.append((table_name, row_id, text, vid))
#
#         if to_embed_items:
#             # embed in batches (reuse MODEL encode pipeline)
#             texts = [t for (_, _, t, _) in to_embed_items]
#             embeddings = MODEL.encode(texts, show_progress_bar=True, convert_to_numpy=True, normalize_embeddings=True).astype("float32")
#             dim = embeddings.shape[1]
#             index = build_or_load_faiss(dim)
#
#             ids_to_add = np.array([vid for (_, _, _, vid) in to_embed_items], dtype="int64")
#
#             # Add embeddings, but guard against faiss duplicate exceptions by trying add_with_ids and catching errors.
#             try:
#                 index.add_with_ids(embeddings, ids_to_add)
#             except Exception as e:
#                 # If adding fails (e.g., because some ids slipped in), recreate a fresh index and add only non-colliding ids
#                 logger.warning("FAISS add_with_ids failed: %s. Recreating index and re-adding only non-colliding ids.", e)
#                 index = build_empty_index(dim)
#                 index.add_with_ids(embeddings, ids_to_add)
#
#             # persist faiss atomically
#             try:
#                 atomic_write_faiss(index, FAISS_INDEX_FILE)
#             except Exception:
#                 faiss.write_index(index, FAISS_INDEX_FILE)
#
#             added = len(ids_to_add)
#
#         # Upsert metadata rows in DB: for every to_upsert_meta entry, insert if new, update snippet if different
#         for vid, table_name, row_id, text in to_upsert_meta:
#             meta = session.query(models.VectorMetadata).filter(models.VectorMetadata.vector_id == int(vid)).first()
#             if meta:
#                 # update snippet/table/row if changed
#                 changed = False
#                 if meta.snippet != text:
#                     meta.snippet = text
#                     changed = True
#                 if meta.table_name != table_name:
#                     meta.table_name = table_name
#                     changed = True
#                 if meta.row_id != int(row_id):
#                     meta.row_id = int(row_id)
#                     changed = True
#                 if changed:
#                     session.add(meta)
#                     updated_meta += 1
#             else:
#                 new = models.VectorMetadata(vector_id=int(vid), table_name=table_name, row_id=int(row_id), snippet=text)
#                 session.add(new)
#
#         # commit all metadata changes
#         try:
#             session.commit()
#         except IntegrityError as ie:
#             # UNIQUE constraint: possible race/dup insertion — handle by rolling back and trying safer per-row upsert
#             logger.warning("IntegrityError during commit of metadata: %s. Attempting row-by-row upsert.", ie)
#             session.rollback()
#             # row-by-row safe upsert
#             for vid, table_name, row_id, text in to_upsert_meta:
#                 try:
#                     meta = session.query(models.VectorMetadata).filter(models.VectorMetadata.vector_id == int(vid)).first()
#                     if meta:
#                         if meta.snippet != text or meta.table_name != table_name or meta.row_id != int(row_id):
#                             meta.snippet = text
#                             meta.table_name = table_name
#                             meta.row_id = int(row_id)
#                             session.add(meta)
#                     else:
#                         session.add(models.VectorMetadata(vector_id=int(vid), table_name=table_name, row_id=int(row_id), snippet=text))
#                     session.commit()
#                 except IntegrityError:
#                     session.rollback()
#                 except Exception:
#                     session.rollback()
#             # end row-by-row
#         except Exception as e:
#             session.rollback()
#             logger.exception("Unexpected error committing metadata: %s", e)
#
#         return {"added_vectors": added, "skipped_existing": skipped, "updated_metadata": updated_meta}
#     finally:
#         session.close()
