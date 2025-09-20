# # #!/usr/bin/env python3




# """
# Populate the empty owner/env/tags_json columns in the existing
# `resources` table.  It works in two modes:
#
# • CLI  :  python tools/update_resources.py  resources.csv      # comma
# • CLI  :  python tools/update_resources.py  resources.tsv "\t" # tab
# • No args → defaults to  resources.csv  and  comma separator
# """
#
# """
# Populate missing owner / env / tags_json fields in the resources table.
# """
#
# import sys
# from pathlib import Path
# import pandas as pd
#
# from app.db.base import SessionLocal          # already returns a Session
# from app.db import models
#
# # ----------------------------------------------------------------------
# def update_resources(csv_path: str, sep: str = ",") -> None:
#     if not Path(csv_path).exists():
#         print(f"❌ file not found: {csv_path}")
#         return
#
#     df = pd.read_csv(
#         csv_path,
#         sep=sep,
#         keep_default_na=False,
#         converters={"tags_json": str},         # keep JSON as raw text
#     )
#
#     added, patched = 0, 0
#     # -------- use SessionLocal() directly -----------------------------
#     with SessionLocal() as session:
#         for _, row in df.iterrows():
#             rid   = row["resource_id"].strip()
#             owner = row["owner"].strip()
#             env   = row["env"].strip()
#             tags  = row["tags_json"].strip()
#
#             res = (
#                 session.query(models.Resource)
#                        .filter(models.Resource.resource_id == rid)
#                        .one_or_none()
#             )
#
#             # INSERT
#             if res is None:
#                 session.add(
#                     models.Resource(
#                         resource_id=rid,
#                         owner=owner or None,
#                         env=env or None,
#                         tags_json=tags or None,
#                     )
#                 )
#                 added += 1
#                 continue
#
#             # PATCH empty columns only
#             changed = False
#             if not res.owner and owner:
#                 res.owner = owner
#                 changed = True
#             if not res.env and env:
#                 res.env = env
#                 changed = True
#             if not res.tags_json and tags:
#                 res.tags_json = tags
#                 changed = True
#             if changed:
#                 session.add(res)
#                 patched += 1
#
#         session.commit()
#
#     print(f"✅ Update finished | inserted: {added}  patched: {patched}")
#
# # ----------------------------------------------------------------------
# if __name__ == "__main__":
#     if len(sys.argv) == 1:
#         print("Usage: python tools/update_resources.py <file> [separator]")
#         sys.exit(1)
#
#     csv_path = sys.argv[1]
#     sep      = sys.argv[2] if len(sys.argv) > 2 else ","
#     update_resources(csv_path, sep)
#
#
#



# # find_missing_in_faiss.py
# import sqlite3, numpy as np, faiss
# from app.configs import FAISS_INDEX_FILE
# DB = r"D:\all_proz\AI_Cost & Insights\data\db\app_data.sqlite"
#
# idx = faiss.read_index(str(FAISS_INDEX_FILE))
# # If IndexIDMap, try to grab ids. If not available use search trick.
# try:
#     arr = faiss.vector_to_array(idx.id_map)
#     faiss_ids = set(int(x) for x in arr)
# except Exception:
#     # fallback: sample query or treat as can't extract id_map
#     print("Could not directly extract id_map; skipping detailed compare.")
#     faiss_ids = None
#
# conn = sqlite3.connect(DB)
# cur = conn.cursor()
# cur.execute("SELECT vector_id FROM vectors")
# meta_ids = set(r[0] for r in cur.fetchall())
# conn.close()
#
# if faiss_ids is None:
#     print("No faiss id_map available to compare.")
# else:
#     missing_in_faiss = meta_ids - faiss_ids
#     missing_in_meta = faiss_ids - meta_ids
#     print("meta_count:", len(meta_ids), "faiss_count:", len(faiss_ids))
#     print("missing_in_faiss (meta but not faiss):", list(missing_in_faiss)[:20])
#     print("missing_in_meta (faiss but not meta):", list(missing_in_meta)[:20])




# # Run these to make sure the FAISS index, DB vectors metadata, and source tables line up
# # check_counts.py
# import sqlite3
# from pathlib import Path
# import faiss
# from app.configs import FAISS_INDEX_FILE
#
# DB = r"D:\all_proz\AI_Cost & Insights\data\db\app_data.sqlite"
# conn = sqlite3.connect(DB)
# cur = conn.cursor()
# cur.execute("SELECT COUNT(*) FROM vectors")
# vec_count = cur.fetchone()[0]
# cur.execute("SELECT COUNT(DISTINCT vector_id) FROM vectors")
# distinct_count = cur.fetchone()[0]
# conn.close()
#
# idx = faiss.read_index(str(FAISS_INDEX_FILE))
# print("vectors table rows:", vec_count)
# print("vectors distinct vector_id:", distinct_count)
# print("FAISS ntotal:", getattr(idx, "ntotal", None))


# # check_sqlite_file.py
# import sqlite3
# from pathlib import Path
# from app.configs import FAISS_INDEX_FILE
#
# DB_PATH = Path(r"D:\all_proz\AI_Cost & Insights\data\db\app_data.sqlite")
#
# # Safe import of embedder module (do NOT import MODEL directly)
# from app.services import embedder
#
# def print_schema():
#     print("DB:", DB_PATH)
#     conn = sqlite3.connect(str(DB_PATH))
#     cur = conn.cursor()
#     for t in ("resources", "billing", "vectors"):
#         try:
#             cur.execute(f"PRAGMA table_info('{t}')")
#             rows = cur.fetchall()
#             print(f"\nSchema for table '{t}':")
#             if rows:
#                 for r in rows:
#                     print(" ", r)
#             else:
#                 print("  (table not present or empty)")
#         except Exception as e:
#             print(f"  Error reading schema for {t}: {e}")
#     conn.close()
#
# def quick_embedding_test():
#     """
#     Optional: test that embedding model can be loaded and produce a vector.
#     This calls get_model() lazily.
#     """
#     try:
#         model = embedder.get_model()
#         v = model.encode(["test embedding"], convert_to_numpy=True, normalize_embeddings=True)
#         print("\nModel test: encoded vector shape:", v.shape)
#     except Exception as e:
#         print("\nModel test failed:", e)
#
# def show_faiss_info():
#     import faiss, os
#     if not Path(FAISS_INDEX_FILE).exists():
#         print("\nFAISS index file not found at:", FAISS_INDEX_FILE)
#         return
#     idx = faiss.read_index(str(FAISS_INDEX_FILE))
#     print("\nFAISS info:")
#     print(" ntotal:", getattr(idx, "ntotal", None))
#     print(" dim:", getattr(idx, "d", None))
#     # try to show some ids if IndexIDMap
#     try:
#         if isinstance(idx, faiss.IndexIDMap):
#             arr = faiss.vector_to_array(idx.id_map)
#             sample = arr[:20] if len(arr) > 0 else arr
#             print(" sample ids:", sample.tolist() if hasattr(sample, "tolist") else sample)
#     except Exception as e:
#         print(" Could not list id_map:", e)
#
# if __name__ == "__main__":
#     print_schema()

    # optionally run a small model test — uncomment if you want to test model load
    # quick_embedding_test()

    # optionally inspect FAISS file
    # show_faiss_info()

    # If you want to rebuild FAISS from metadata here, call the rebuild script safely:
    # from rebuild_faiss_from_metadata import rebuild_index
    # rebuild_index()



# # rebuild_faiss_from_metadata.py
# import numpy as np, faiss
# from app.db.base import SessionLocal
# from app.db import models
# from app.services.embedder import MODEL, _row_to_text, atomic_write_faiss, build_empty_index, TABLE_CODES
# from app.configs import FAISS_INDEX_FILE
# from sqlalchemy import select
#
# BATCH = 256
#
# def rebuild_index():
#     session = SessionLocal()
#     try:
#         metas = session.query(models.VectorMetadata).all()
#         items = []
#         for m in metas:
#             # Try to re-create snippet text from the referenced row if present, else use stored snippet
#             if m.table_name == "billing":
#                 row = session.query(models.Billing).filter(models.Billing.id == m.row_id).first()
#             else:
#                 row = session.query(models.Resource).filter(models.Resource.id == m.row_id).first()
#             text = _row_to_text(m.table_name, row) if row else (m.snippet or "")
#             items.append((m.vector_id, text))
#
#         if not items:
#             print("No vector metadata found.")
#             return
#
#         texts = [t for (_, t) in items]
#         # embed batches
#         emb_batches = []
#         for i in range(0, len(texts), BATCH):
#             emb = MODEL.encode(texts[i:i+BATCH], convert_to_numpy=True, normalize_embeddings=True)
#             emb_batches.append(emb.astype('float32'))
#         embeddings = np.vstack(emb_batches)
#         dim = embeddings.shape[1]
#         idx = build_empty_index(dim)
#         ids = np.array([int(vid) for (vid, _) in items], dtype='int64')
#         idx.add_with_ids(embeddings, ids)
#         atomic_write_faiss(idx, FAISS_INDEX_FILE)
#         print("Rebuilt FAISS index with", len(ids), "vectors.")
#     finally:
#         session.close()
#
# if __name__ == "__main__":
#     rebuild_index()





#
# import sqlite3
# from pathlib import Path
#
# DB = Path(r"D:\all_proz\AI_Cost & Insights\data\db\app_data.sqlite")
# conn = sqlite3.connect(str(DB))
# cur = conn.cursor()
#
# # Keep the smallest id for each vector_id; delete others
# sql = """
# DELETE FROM vectors
# WHERE id NOT IN (
#     SELECT MIN(id) FROM vectors GROUP BY vector_id
# );
# """
# cur.execute(sql)
# conn.commit()
#
# # Show remaining count
# cur.execute("SELECT COUNT(*), COUNT(DISTINCT vector_id) FROM vectors;")
# print("rows, distinct_vector_ids:", cur.fetchone())
# conn.close()




# #!/usr/bin/env python3
# """
# migrate_all_tables.py
#
# Safely migrate/ensure three tables in the SQLite DB:
#  - billing
#  - resources
#  - vectors
#
# Strategy:
#  - Back up DB first (creates app_data.sqlite.backup_TIMESTAMP)
#  - For each table:
#     * If table does not exist -> create desired schema
#     * If table exists -> create <table>_new with desired schema,
#       copy over columns that appear in both old and desired,
#       drop old table, rename new table -> original name.
#  - Prints before/after PRAGMA table_info for transparency.
#
# Run:
#     python migrate_all_tables.py


# """
# from pathlib import Path
# import sqlite3
# import shutil
# import datetime
# import sys
# import traceback
#
# DB_PATH = Path(r"D:\all_proz\AI_Cost & Insights\data\db\app_data.sqlite")
#
# def backup_db(db_path: Path) -> Path:
#     ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
#     backup = db_path.with_name(db_path.stem + f".backup_{ts}" + db_path.suffix)
#     print(f"[backup] copying {db_path} -> {backup}")
#     shutil.copy2(db_path, backup)
#     return backup
#
# def table_exists(conn: sqlite3.Connection, name: str) -> bool:
#     cur = conn.cursor()
#     cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (name,))
#     return cur.fetchone() is not None
#
# def get_table_columns(conn: sqlite3.Connection, name: str):
#     cur = conn.cursor()
#     cur.execute(f"PRAGMA table_info('{name}');")
#     rows = cur.fetchall()  # (cid, name, type, notnull, dflt_value, pk)
#     return [r[1] for r in rows]
#
# def show_table_info(conn: sqlite3.Connection, name: str):
#     cur = conn.cursor()
#     cur.execute(f"PRAGMA table_info('{name}');")
#     rows = cur.fetchall()
#     for r in rows:
#         print("   ", r)
#
# def create_table_sql(conn: sqlite3.Connection, sql: str):
#     cur = conn.cursor()
#     cur.execute(sql)
#     conn.commit()
#
# def recreate_table_preserving_columns(conn: sqlite3.Connection, table: str, desired_sql: str, desired_cols: list):
#     """
#     If table does not exist -> create with desired_sql.
#     If exists -> create table_new with desired_sql, copy matching columns, swap.
#     """
#     cur = conn.cursor()
#     if not table_exists(conn, table):
#         print(f"[{table}] does not exist -> creating from desired schema.")
#         cur.execute(desired_sql)
#         conn.commit()
#         return
#
#     # get existing columns
#     existing_cols = get_table_columns(conn, table)
#     print(f"[{table}] existing columns: {existing_cols}")
#     print(f"[{table}] desired columns:  {desired_cols}")
#
#     new_table = f"{table}_new"
#
#     # If the existing already matches desired exactly, skip recreate
#     if set(existing_cols) == set(desired_cols):
#         print(f"[{table}] existing columns match desired columns -> skipping recreate.")
#         return
#
#     print(f"[{table}] creating temporary table '{new_table}' with desired schema...")
#     # create new table
#     cur.execute(desired_sql.replace(f"CREATE TABLE {table}", f"CREATE TABLE {new_table}"))
#     conn.commit()
#
#     # determine columns to copy (intersection, preserve order of desired_cols where possible)
#     cols_to_copy = [c for c in desired_cols if c in existing_cols]
#     if cols_to_copy:
#         col_list = ", ".join(cols_to_copy)
#         copy_sql = f"INSERT INTO {new_table} ({col_list}) SELECT {col_list} FROM {table};"
#         print(f"[{table}] copying columns: {cols_to_copy}")
#         try:
#             cur.execute(copy_sql)
#             conn.commit()
#         except Exception as e:
#             print(f"[{table}] WARNING: copying data failed: {e}")
#             print(traceback.format_exc())
#             # If copying fails, we will still try to swap (but data loss possible). Stop to be safe.
#             raise
#
#     else:
#         print(f"[{table}] No overlapping columns to copy (the new table will be empty).")
#
#     # swap: drop old and rename new
#     try:
#         cur.execute(f"DROP TABLE {table};")
#         cur.execute(f"ALTER TABLE {new_table} RENAME TO {table};")
#         conn.commit()
#         print(f"[{table}] Recreated and swapped successfully.")
#     except Exception as e:
#         print(f"[{table}] ERROR during swap: {e}")
#         print(traceback.format_exc())
#         raise
#
# def migrate_all(db_path: Path):
#     if not db_path.exists():
#         print("DB path does not exist:", db_path)
#         sys.exit(1)
#
#     backup = backup_db(db_path)
#
#     conn = sqlite3.connect(str(db_path))
#     try:
#         print("\n=== billing ===")
#         # desired billing schema (matches your SQLAlchemy model)
#         desired_billing_sql = """
#         CREATE TABLE billing (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             invoice_month TEXT,
#             account_id TEXT,
#             subscription TEXT,
#             service TEXT,
#             resource_group TEXT,
#             resource_id TEXT,
#             region TEXT,
#             usage_qty REAL,
#             unit_cost REAL,
#             cost REAL
#         );
#         """
#         billing_cols = ["id","invoice_month","account_id","subscription","service","resource_group","resource_id","region","usage_qty","unit_cost","cost"]
#         recreate_table_preserving_columns(conn, "billing", desired_billing_sql, billing_cols)
#         print("After migration billing schema:")
#         show_table_info(conn, "billing")
#
#         print("\n=== resources ===")
#         desired_resources_sql = """
#         CREATE TABLE resources (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             resource_id TEXT UNIQUE,
#             owner TEXT,
#             env TEXT,
#             tags_json TEXT
#         );
#         """
#         resources_cols = ["id","resource_id","owner","env","tags_json"]
#         recreate_table_preserving_columns(conn, "resources", desired_resources_sql, resources_cols)
#         print("After migration resources schema:")
#         show_table_info(conn, "resources")
#
#         print("\n=== vectors ===")
#         desired_vectors_sql = """
#         CREATE TABLE vectors (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             vector_id INTEGER UNIQUE,
#             table_name TEXT,
#             row_id INTEGER,
#             snippet TEXT,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         );
#         """
#         vectors_cols = ["id","vector_id","table_name","row_id","snippet","created_at"]
#         recreate_table_preserving_columns(conn, "vectors", desired_vectors_sql, vectors_cols)
#         print("After migration vectors schema:")
#         show_table_info(conn, "vectors")
#
#         print("\nMigration completed. Backup stored at:", backup)
#     finally:
#         conn.close()
#
# if __name__ == "__main__":
#     try:
#         migrate_all(DB_PATH)
#     except Exception as exc:
#         print("Migration failed:", exc)
#         print("If migration partially applied, restore from backup:", DB_PATH.with_name(DB_PATH.stem + ".backup_" + "[timestamp]" + DB_PATH.suffix))
#         sys.exit(1)



# import sqlite3
# from pathlib import Path
#
# DB_PATH = Path(r"D:\all_proz\AI_Cost & Insights\data\db\app_data.sqlite")
#
# conn = sqlite3.connect(DB_PATH)
# cur = conn.cursor()
#
# # Show schema info (column names + types)
# print("=== Table schema: resources ===")
# cur.execute("PRAGMA table_info('resources');")
# for row in cur.fetchall():
#     # row: (cid, name, type, notnull, dflt_value, pk)
#     print(row)
#
# # Show a few rows of actual data
# print("\n=== Sample rows: resources ===")
# try:
#     cur.execute("SELECT * FROM resources LIMIT 10;")
#     cols = [d[0] for d in cur.description]
#     print("Columns:", cols)
#     for r in cur.fetchall():
#         print(r)
# except Exception as e:
#     print("Error reading rows:", e)
#
# conn.close()



# #!/usr/bin/env python3
# from pathlib import Path
# import sqlite3
#
# INPATH = Path(r"D:\all_proz\AI_Cost & Insights\data\db\app_data.sqlite")
# OUTPATH = INPATH.with_name("carved_from_signature.sqlite")
# SIG = b"SQLite format 3"
#
# def try_carve():
#     b = INPATH.read_bytes()
#     idx = b.find(SIG)
#     print("File size:", len(b), "bytes. Signature index:", idx)
#     if idx == -1:
#         print("Signature not found.")
#         return False
#     # write from the found index to a new file
#     data = b[idx:]
#     OUTPATH.write_bytes(data)
#     print("Wrote carved file:", OUTPATH, "size:", len(data))
#     # try integrity_check
#     try:
#         conn = sqlite3.connect(f"file:{OUTPATH}?mode=ro", uri=True)
#         cur = conn.cursor()
#         cur.execute("PRAGMA integrity_check;")
#         res = cur.fetchone()
#         cur.close(); conn.close()
#         print("PRAGMA integrity_check ->", res)
#         return True
#     except Exception as e:
#         print("Could not open carved file:", repr(e))
#         return False
#
# if __name__ == "__main__":
#     ok = try_carve()
#     if ok:
#         print("Carve produced a readable DB (PRAGMA ok). If ok, replace original after verifying.")
#     else:
#         print("Carve did not produce a valid DB.")



#!/usr/bin/env python3
# import os, sqlite3
# from pathlib import Path
#
# CORRUPT = Path(r"D:\all_proz\AI_Cost & Insights\data\db\app_data.sqlite")
# OUT_EVEN = CORRUPT.with_name("recovered_even_bytes.sqlite")
# OUT_ODD  = CORRUPT.with_name("recovered_odd_bytes.sqlite")
#
# def detect_utf16_pattern(b: bytes) -> dict:
#     # count zeros in even/odd positions
#     even_zero = sum(1 for i in range(0, len(b), 2) if b[i] == 0)
#     odd_zero = sum(1 for i in range(1, len(b), 2) if b[i] == 0)
#     total_even = (len(b)+1)//2
#     total_odd = len(b)//2
#     return {
#         "even_zero": even_zero, "odd_zero": odd_zero,
#         "total_even": total_even, "total_odd": total_odd,
#         "even_zero_ratio": even_zero / max(1, total_even),
#         "odd_zero_ratio": odd_zero / max(1, total_odd),
#     }
#
# def extract_bytes(b: bytes, take='even'):
#     # take='even' -> take bytes at indices 0,2,4,... ; 'odd' -> 1,3,5,..
#     if take == 'even':
#         return b[0::2]
#     else:
#         return b[1::2]
#
# def try_open_and_check(path: Path):
#     try:
#         conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
#         cur = conn.cursor()
#         cur.execute("PRAGMA integrity_check;")
#         res = cur.fetchone()
#         cur.close()
#         conn.close()
#         return res
#     except Exception as e:
#         return repr(e)
#
# def main():
#     print("Corrupt path:", CORRUPT)
#     if not CORRUPT.exists():
#         print("File not found:", CORRUPT)
#         return
#
#     b = CORRUPT.read_bytes()
#     print("File size:", len(b), "bytes")
#
#     info = detect_utf16_pattern(b)
#     print("Zero counts and ratios (even_index zeros, odd_index zeros):")
#     print(info)
#
#     # Heuristic: if one side has very high zero ratio (>0.6) then the other side likely contains original bytes.
#     cand = []
#     if info["even_zero_ratio"] > 0.6:
#         print("Even positions are mostly zero -> original bytes likely in odd indices. Will try odd extraction.")
#         cand.append(('odd', OUT_ODD))
#     if info["odd_zero_ratio"] > 0.6:
#         print("Odd positions are mostly zero -> original bytes likely in even indices. Will try even extraction.")
#         cand.append(('even', OUT_EVEN))
#     # If both low or ambiguous, try both
#     if not cand:
#         print("Could not strongly detect pattern; will try both even- and odd-index extraction.")
#         cand = [('even', OUT_EVEN), ('odd', OUT_ODD)]
#
#     for take, outp in cand:
#         data = extract_bytes(b, take=take)
#         print(f"Writing recovered candidate ({take}) to: {outp}  size={len(data)}")
#         outp.write_bytes(data)
#         # try opening
#         print("Trying to open and run PRAGMA integrity_check on", outp)
#         res = try_open_and_check(outp)
#         print("Result for", outp, "->", res)
#
#     print("\nDone. Inspect the two output files (if created). If one reports 'ok' from integrity_check, that's likely recovered.")
#     print("If neither works, fallback: recreate DB from CSVs (I can provide script).")
#
# if __name__ == "__main__":
#     main()

# import sqlite3
# p = r"D:\all_proz\AI_Cost & Insights\data\db\app_data.sqlite"
# conn = sqlite3.connect(p)
# print("Tables:", conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall())
# print("Billing sample:", conn.execute("SELECT * FROM billing LIMIT 3").fetchall())
# conn.close()

# # check_sqlite_file.py
# import os, sqlite3, sys
# path = r"D:\all_proz\AI_Cost & Insights\data\db\app_data.sqlite"
#
# print("Path exists:", os.path.exists(path))
# print("Size (bytes):", os.path.getsize(path))
# with open(path, "rb") as f:
#     hdr = f.read(64)
# print("Header (first 64 bytes raw):", hdr[:64])
# print("Header (ascii):", hdr[:64].decode("ascii", errors="replace"))
#
# if hdr.startswith(b"SQLite format 3"):
#     print("Header looks like SQLite format 3 — attempting PRAGMA integrity_check (read-only)...")
#     try:
#         conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
#         cur = conn.cursor()
#         cur.execute("PRAGMA integrity_check;")
#         res = cur.fetchall()
#         print("PRAGMA integrity_check:", res)
#         cur.close()
#         conn.close()
#     except Exception as e:
#         print("Could not open DB in read-only mode:", repr(e))
# else:
#     print("Header is NOT 'SQLite format 3' — file is not a valid sqlite DB.")

# import sqlite3
#
# path = r"D:\all_proz\AI_Cost & Insights\data\db\app_data.sqlite"
# conn = sqlite3.connect(path)
# cur = conn.cursor()
# cur.execute("PRAGMA table_info(billing);")
# for col in cur.fetchall():
#     print(col)
# conn.close()

#
# import sqlite3
#
# # Connect to the database file
# conn = sqlite3.connect('app_data.sqlite')
# cursor = conn.cursor()
#
# # Execute your table creation or data insertion commands
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS billing (
#         id INTEGER PRIMARY KEY,
#         date TEXT,
#         amount REAL
#     );
# ''')
#
# # --- This is the crucial step! ---
# # Save the changes to the database file
# conn.commit()
#
# # --- This is also important ---
# # Close the connection
# conn.close()
#
# print("Database operations completed and changes saved.")

# """
# check_sqlite_file.py
#
# Compare CSV files against SQLite DB tables (schema + data) with a clear validation report.
#
# Defaults are set to your paths so you can run:
#     python check_sqlite_file.py
#
# You may still override any of these via command-line args.
# """
# import argparse
# import sqlite3
# import pandas as pd
# import numpy as np
# import sys
#
# # ---------- Type helpers ----------
# SQLITE_TO_PANDAS_TYPE = {
#     "INT": "int64", "INTEGER": "int64", "BIGINT": "int64",
#     "CHAR": "object", "VARCHAR": "object", "TEXT": "object", "CLOB": "object",
#     "REAL": "float64", "DOUBLE": "float64", "FLOAT": "float64",
#     "NUMERIC": "float64", "DECIMAL": "float64",
#     "DATE": "object", "DATETIME": "object",
# }
#
# def normalize_sqlite_type(raw: str) -> str:
#     if raw is None:
#         return "object"
#     s = raw.strip().upper()
#     for tok in SQLITE_TO_PANDAS_TYPE.keys():
#         if tok in s:
#             return SQLITE_TO_PANDAS_TYPE[tok]
#     if "INT" in s:
#         return "int64"
#     if "CHAR" in s or "CLOB" in s or "TEXT" in s:
#         return "object"
#     if "REAL" in s or "FLOA" in s or "DOUB" in s:
#         return "float64"
#     return "object"
#
# def safe_type_name(dtype) -> str:
#     return str(dtype)
#
# def compare_types(db_type: str, csv_dtype: str):
#     if db_type == csv_dtype:
#         return True, f"Exact match ({db_type})"
#     if db_type == "int64" and csv_dtype == "float64":
#         return True, "DB int vs CSV float (nullable ints in CSV)"
#     if db_type == "object":
#         return True, "DB object vs CSV (text-like) -- accepted"
#     if db_type == "float64" and csv_dtype in ("int64", "float64"):
#         return True, "Numeric compatible"
#     return False, f"Type mismatch DB:{db_type} CSV:{csv_dtype}"
#
# # ---------- DB helpers ----------
# def get_db_schema(conn: sqlite3.Connection, table: str) -> pd.DataFrame:
#     cur = conn.cursor()
#     cur.execute(f"PRAGMA table_info('{table}')")
#     cols = cur.fetchall()
#     if not cols:
#         raise ValueError(f"Table '{table}' not found in database.")
#     df = pd.DataFrame(cols, columns=["cid", "name", "type", "notnull", "dflt_value", "pk"])
#     df["normalized_type"] = df["type"].apply(normalize_sqlite_type)
#     df["notnull"] = df["notnull"].astype(int)
#     return df
#
# def load_table_from_db(conn: sqlite3.Connection, table: str) -> pd.DataFrame:
#     return pd.read_sql_query(f"SELECT * FROM '{table}'", conn)
#
# # ---------- Comparison helpers ----------
# def detect_key_columns(df_csv: pd.DataFrame, df_db: pd.DataFrame, provided_keys):
#     if provided_keys:
#         missing_csv = [k for k in provided_keys if k not in df_csv.columns]
#         missing_db = [k for k in provided_keys if k not in df_db.columns]
#         if missing_csv or missing_db:
#             raise ValueError(f"Provided key columns not found. missing_csv={missing_csv}, missing_db={missing_db}")
#         return provided_keys
#     common = list(set(df_csv.columns).intersection(df_db.columns))
#     candidates = [c for c in common if any(tok in c.lower() for tok in ("id", "resource", "key", "uuid"))]
#     if candidates:
#         if "resource_id" in candidates:
#             return ["resource_id"]
#         return [candidates[0]]
#     if common:
#         return common
#     raise ValueError("No key columns found in common. Provide --key_columns.")
#
# def compare_row_counts(df_csv: pd.DataFrame, df_db: pd.DataFrame):
#     c_csv = len(df_csv); c_db = len(df_db)
#     return (c_csv == c_db), {"csv_count": c_csv, "db_count": c_db, "difference": c_csv - c_db}
#
# def find_missing_rows(df_csv: pd.DataFrame, df_db: pd.DataFrame, keys):
#     merged = df_csv.merge(df_db, on=keys, how="outer", indicator=True)
#     return merged[merged["_merge"] == "left_only"].drop(columns=["_merge"]), merged[merged["_merge"] == "right_only"].drop(columns=["_merge"])
#
# def find_mismatched_values(df_csv: pd.DataFrame, df_db: pd.DataFrame, keys, float_tol=1e-6):
#     common_cols = [c for c in df_csv.columns if c in df_db.columns and c not in keys]
#     if not common_cols:
#         return pd.DataFrame()
#     left = df_csv.set_index(keys); right = df_db.set_index(keys)
#     both_index = left.index.intersection(right.index)
#     if len(both_index) == 0:
#         return pd.DataFrame()
#     left_common = left.loc[both_index, common_cols]
#     right_common = right.loc[both_index, common_cols]
#     diffs = []
#     for idx in both_index:
#         row_left = left_common.loc[idx]
#         row_right = right_common.loc[idx]
#         row_diffs = {}
#         for col in common_cols:
#             v1 = row_left[col]; v2 = row_right[col]
#             if pd.isna(v1) and pd.isna(v2):
#                 continue
#             # numeric compare
#             if (isinstance(v1, (int, float, np.number)) or isinstance(v2, (int, float, np.number))):
#                 try:
#                     num1 = float(v1) if not pd.isna(v1) else np.nan
#                     num2 = float(v2) if not pd.isna(v2) else np.nan
#                     if pd.isna(num1) and pd.isna(num2):
#                         continue
#                     if pd.isna(num1) or pd.isna(num2) or abs(num1 - num2) > float_tol:
#                         row_diffs[col] = {"csv": v1, "db": v2}
#                 except Exception:
#                     if v1 != v2:
#                         row_diffs[col] = {"csv": v1, "db": v2}
#             else:
#                 if pd.isna(v1) and not pd.isna(v2):
#                     row_diffs[col] = {"csv": v1, "db": v2}
#                 elif pd.isna(v2) and not pd.isna(v1):
#                     row_diffs[col] = {"csv": v1, "db": v2}
#                 else:
#                     if str(v1) != str(v2):
#                         row_diffs[col] = {"csv": v1, "db": v2}
#         if row_diffs:
#             if isinstance(idx, tuple):
#                 key_dict = dict(zip(keys, idx))
#             else:
#                 key_dict = {keys[0]: idx}
#             diffs.append({**key_dict, **{"diffs": row_diffs}})
#     rows = []
#     for d in diffs:
#         key_part = {k: d[k] for k in keys}
#         for col, vals in d["diffs"].items():
#             rows.append({**key_part, "column": col, "csv_value": vals["csv"], "db_value": vals["db"]})
#     return pd.DataFrame(rows)
#
# def notnull_violations(df: pd.DataFrame, db_schema_df: pd.DataFrame):
#     notnull_cols = db_schema_df[db_schema_df["notnull"] == 1]["name"].tolist()
#     violations = []
#     for col in notnull_cols:
#         if col in df.columns:
#             null_rows = df[df[col].isna()]
#             if not null_rows.empty:
#                 sample = null_rows.head(10).copy()
#                 sample["_null_col"] = col
#                 violations.append(sample.assign(_num_null=len(null_rows)))
#     if violations:
#         return pd.concat(violations, ignore_index=True)
#     return pd.DataFrame()
#
# # ---------- Reporting ----------
# def print_report_section(title: str):
#     print("\n" + "=" * 80)
#     print(title)
#     print("=" * 80 + "\n")
#
# def main(args):
#     # Connect DB
#     try:
#         conn = sqlite3.connect(args.db)
#     except Exception as e:
#         print(f"❌ Could not open DB at {args.db}: {e}")
#         sys.exit(1)
#
#     report = {"passed": [], "failed": []}
#
#     # Load CSVs
#     try:
#         df_resources_csv = pd.read_csv(args.csv_resources)
#         df_billing_csv = pd.read_csv(args.csv_billing)
#     except Exception as e:
#         print(f"❌ Failed to read CSV files: {e}")
#         sys.exit(1)
#
#     # Load DB tables
#     try:
#         db_schema_resources = get_db_schema(conn, args.table_resources)
#         db_schema_billing = get_db_schema(conn, args.table_billing)
#         df_resources_db = load_table_from_db(conn, args.table_resources)
#         df_billing_db = load_table_from_db(conn, args.table_billing)
#     except Exception as e:
#         print(f"❌ DB error: {e}")
#         sys.exit(1)
#
#     # Schema validation
#     print_report_section("SCHEMA VALIDATION")
#
#     def schema_validate_one(name, df_csv, df_db, db_schema_df):
#         csv_cols = list(df_csv.columns)
#         db_cols = list(db_schema_df["name"])
#         missing_in_csv = [c for c in db_cols if c not in csv_cols]
#         extra_in_csv = [c for c in csv_cols if c not in db_cols]
#         if not missing_in_csv and not extra_in_csv:
#             report["passed"].append(f"{name}: Columns match exactly ({len(csv_cols)} columns).")
#             print(f"✅ {name}: Columns match exactly ({len(csv_cols)} columns).")
#         else:
#             report["failed"].append(f"{name}: Column name mismatch. missing_in_csv={missing_in_csv}, extra_in_csv={extra_in_csv}")
#             print(f"❌ {name}: Column name mismatch.")
#             if missing_in_csv:
#                 print(f"    Columns in DB but missing in CSV: {missing_in_csv}")
#             if extra_in_csv:
#                 print(f"    Extra columns in CSV not in DB: {extra_in_csv}")
#
#         common = [c for c in db_cols if c in csv_cols]
#         type_mismatches = []
#         for c in common:
#             csv_dtype = safe_type_name(df_csv[c].dtype)
#             db_dtype = db_schema_df.loc[db_schema_df["name"] == c, "normalized_type"].iloc[0]
#             ok, explanation = compare_types(db_dtype, csv_dtype)
#             if not ok:
#                 type_mismatches.append((c, db_dtype, csv_dtype, explanation))
#         if not type_mismatches:
#             report["passed"].append(f"{name}: Column types compatible for common columns.")
#             print(f"✅ {name}: Column types compatible for common columns.")
#         else:
#             report["failed"].append(f"{name}: Type mismatches: {type_mismatches}")
#             print(f"❌ {name}: Type mismatches for some columns:")
#             for col, dbt, csdt, expl in type_mismatches:
#                 print(f"    - {col}: DB={dbt}, CSV={csdt} -> {expl}")
#
#     schema_validate_one("resources", df_resources_csv, df_resources_db, db_schema_resources)
#     schema_validate_one("billing", df_billing_csv, df_billing_db, db_schema_billing)
#
#     # Data validation
#     print_report_section("DATA VALIDATION")
#
#     def data_validate_one(name, df_csv, df_db, db_schema_df):
#         print(f"Validating table: {name}")
#         ok_count, counts = compare_row_counts(df_csv, df_db)
#         if ok_count:
#             report["passed"].append(f"{name}: Row count identical ({counts['csv_count']}).")
#             print(f"✅ {name}: Row counts identical ({counts['csv_count']}).")
#         else:
#             report["failed"].append(f"{name}: Row count mismatch CSV={counts['csv_count']} DB={counts['db_count']}")
#             print(f"❌ {name}: Row count mismatch. CSV={counts['csv_count']}, DB={counts['db_count']}")
#
#         provided_keys = [k for k in args.key_columns] if args.key_columns else []
#         try:
#             keys = detect_key_columns(df_csv, df_db, provided_keys)
#             print(f"    Using key columns: {keys}")
#         except Exception as e:
#             report["failed"].append(f"{name}: Key detection failed: {e}")
#             print(f"❌ {name}: Key detection failed: {e}")
#             return
#
#         in_csv_not_db, in_db_not_csv = find_missing_rows(df_csv, df_db, keys)
#         if in_csv_not_db.empty and in_db_not_csv.empty:
#             report["passed"].append(f"{name}: No missing rows between CSV and DB (based on keys={keys}).")
#             print(f"✅ {name}: No missing rows between CSV and DB.")
#         else:
#             if not in_csv_not_db.empty:
#                 report["failed"].append(f"{name}: {len(in_csv_not_db)} rows in CSV not present in DB.")
#                 print(f"❌ {name}: {len(in_csv_not_db)} rows present in CSV but not in DB. Sample:")
#                 print(in_csv_not_db.head(10).to_string(index=False))
#             if not in_db_not_csv.empty:
#                 report["failed"].append(f"{name}: {len(in_db_not_csv)} rows in DB not present in CSV.")
#                 print(f"❌ {name}: {len(in_db_not_csv)} rows present in DB but not in CSV. Sample:")
#                 print(in_db_not_csv.head(10).to_string(index=False))
#
#         mismatches = find_mismatched_values(df_csv, df_db, keys)
#         if mismatches.empty:
#             report["passed"].append(f"{name}: No value mismatches found for common rows.")
#             print(f"✅ {name}: No mismatched values found for rows present in both.")
#         else:
#             report["failed"].append(f"{name}: {len(mismatches)} mismatched value entries found.")
#             print(f"❌ {name}: {len(mismatches)} mismatched value entries found. Showing up to 10 samples:")
#             print(mismatches.head(10).to_string(index=False))
#
#         null_viol = notnull_violations(df_csv, db_schema_df)
#         if null_viol.empty:
#             report["passed"].append(f"{name}: No NOT NULL violations found in CSV according to DB schema.")
#             print(f"✅ {name}: No NOT NULL column violations in CSV against DB NOT NULL constraints.")
#         else:
#             report["failed"].append(f"{name}: NOT NULL violations in CSV for columns: {null_viol['_null_col'].unique().tolist()}")
#             print(f"❌ {name}: NOT NULL violations found in CSV for columns: {null_viol['_null_col'].unique().tolist()}. Sample rows:")
#             print(null_viol.head(10).to_string(index=False))
#
#     data_validate_one("resources", df_resources_csv, df_resources_db, db_schema_resources)
#     data_validate_one("billing", df_billing_csv, df_billing_db, db_schema_billing)
#
#     # Summary
#     print_report_section("SUMMARY REPORT")
#     print("Passed checks:")
#     for p in report["passed"]:
#         print("  ✅ " + p)
#     print("\nFailed checks:")
#     if not report["failed"]:
#         print("  ✅ None — all checks passed.")
#     else:
#         for f in report["failed"]:
#             print("  ❌ " + f)
#     print("\nEnd of validation.\n")
#     conn.close()

    # import sqlite3
    #
    # # Connect to the database file
    # conn = sqlite3.connect('app_data.sqlite')
    # cursor = conn.cursor()
    #
    # # Execute your table creation or data insertion commands
    # cursor.execute('''
    #     CREATE TABLE IF NOT EXISTS billing (
    #         id INTEGER PRIMARY KEY,
    #         date TEXT,
    #         amount REAL
    #     );
    # ''')
    #
    # # --- This is the crucial step! ---
    # # Save the changes to the database file
    # conn.commit()
    #
    # # --- This is also important ---
    # # Close the connection
    # conn.close()
    #
    # print("Database operations completed and changes saved.")

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Validate CSVs vs SQLite DB tables (schema + data).")
#     parser.add_argument("--db", default=r"D:\all_proz\AI_Cost & Insights\data\db\app_data.sqlite",
#                         help="Path to sqlite DB file")
#     parser.add_argument("--csv_resources", default=r"D:\all_proz\AI_Cost & Insights\data\synthetic\resources.csv",
#                         help="Path to resources CSV")
#     parser.add_argument("--csv_billing", default=r"D:\all_proz\AI_Cost & Insights\data\synthetic\billing.csv",
#                         help="Path to billing CSV")
#     parser.add_argument("--table_resources", default="resources", help="Name of resources table in DB")
#     parser.add_argument("--table_billing", default="billing", help="Name of billing table in DB")
#     parser.add_argument("--key_columns", default="resource_id", help="Comma-separated key columns to use for matching")
#     args = parser.parse_args()
#     args.key_columns = [k.strip() for k in args.key_columns.split(",") if k.strip()]
#     main(args)
