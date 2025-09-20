# run_and_check_embeddings.py
import os
from pathlib import Path
import numpy as np
import faiss
import sqlite3

# adjust these imports if your project layout differs
from app.services.embedder import embed_all_and_store, query_knn
from app.configs import FAISS_INDEX_FILE
from app.db.base import engine

def print_db_vectormeta_stats():
    q = "SELECT COUNT(*) FROM vector_metadata"
    try:
        conn = sqlite3.connect(str(engine.url.database)) if hasattr(engine.url, "database") else sqlite3.connect(str(engine.url).replace("sqlite:///", ""))
    except Exception:
        conn = sqlite3.connect(str(engine.url).replace("sqlite:///", ""))
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM vector_metadata")
        cnt = cur.fetchone()[0]
    except Exception:
        cnt = None
    # sample a few rows
    sample = []
    try:
        cur.execute("SELECT vector_id, table_name, row_id, snippet FROM vector_metadata LIMIT 10")
        sample = cur.fetchall()
    except Exception:
        sample = []
    cur.close()
    conn.close()
    print("VectorMetadata rows in DB:", cnt)
    if sample:
        print("Sample rows from vector_metadata (up to 10):")
        for r in sample:
            print(" ", r)
    return cnt

def inspect_faiss_index(index_path):
    if not os.path.exists(index_path):
        print("FAISS index file not found at", index_path)
        return None
    idx = faiss.read_index(index_path)
    try:
        n = idx.ntotal
        d = idx.d
    except Exception:
        # some FAISS builds use attributes differently
        n = getattr(idx, "ntotal", None)
        d = getattr(idx, "d", None)
    print("FAISS index:", index_path)
    print(" - ntotal:", n)
    print(" - dim:", d)
    # list some ids (works only for IndexIDMap)
    try:
        if isinstance(idx, faiss.IndexIDMap):
            # attempt to extract ids (works on many builds)
            id_map = faiss.vector_to_array(idx.id_map)
            # print first 20 ids
            sample_ids = id_map[:20] if len(id_map) > 20 else id_map
            print(" - sample vector ids (first 20):", sample_ids.tolist() if hasattr(sample_ids, 'tolist') else sample_ids)
    except Exception as e:
        print(" - could not list IDs from index (faiss version detail):", e)
    return idx

if __name__ == "__main__":
    print("1) Running embed_all_and_store() ...")
    added = embed_all_and_store()
    print("embed_all_and_store returned (vectors added):", added)

    print("\n2) Inspect DB vector_metadata ...")
    db_count = print_db_vectormeta_stats()

    print("\n3) Inspect FAISS index ...")
    idx = inspect_faiss_index(FAISS_INDEX_FILE)

    print("\n4) Quick sample KNN query for 'cost compute' ...")
    try:
        res = query_knn("cost compute", k=5)
        for r in res:
            print("  ", r)
    except Exception as e:
        print("KNN query failed:", e)

    print("\nSummary:")
    print(" - Vectors added by run:", added)
    print(" - VectorMetadata rows in DB (after run):", db_count)
    if idx is not None:
        print(" - FAISS ntotal:", getattr(idx, "ntotal", None))
