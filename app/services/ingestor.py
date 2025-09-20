# import pandas as pd
# from app.db.base import SessionLocal, engine
# from app.db import models, crud
# from sqlalchemy.exc import IntegrityError
#
# def create_tables():
#     models.Base.metadata.create_all(bind=engine)
#
# def ingest_csv_to_sqlite(billing_csv_path, resources_csv_path):
#     create_tables()
#     session = SessionLocal()
#     try:
#         df_res = pd.read_csv(resources_csv_path)
#         for row in df_res.to_dict(orient="records"):
#             try:
#                 crud.create_resource(session, row)
#             except IntegrityError:
#                 session.rollback()
#         session.commit()
#
#         df_bill = pd.read_csv(billing_csv_path)
#         for row in df_bill.to_dict(orient="records"):
#             # ensure numeric cast
#             row["usage_qty"] = float(row.get("usage_qty") or 0)
#             row["unit_cost"] = float(row.get("unit_cost") or 0)
#             row["cost"] = float(row.get("cost") or 0)
#             try:
#                 crud.create_billing(session, row)
#             except IntegrityError:
#                 session.rollback()
#         session.commit()
#     finally:
#         session.close()



# #!/usr/bin/env python3
# """
# recreate_db_from_csvs.py
#
# Creates a fresh SQLite DB from your CSVs. Safe for development.
# WARNING: This will overwrite the DB path if you choose overwrite=True.
# """
#
# import os
# import sqlite3
# import pandas as pd
# from pathlib import Path
#
# # === Configure these paths ===
# DB_PATH = Path(r"D:\all_proz\AI_Cost & Insights\data\db\app_data.sqlite")
# RESOURCES_CSV = Path(r"D:\all_proz\AI_Cost & Insights\data\synthetic\resources.csv")
# BILLING_CSV = Path(r"D:\all_proz\AI_Cost & Insights\data\synthetic\billing.csv")
# # If True, this will remove the existing DB file and create a new one.
# OVERWRITE = True
#
# # === Schema definition (simple, matches your CSV columns) ===
# CREATE_RESOURCES_SQL = """
# CREATE TABLE resources (
#     resource_id TEXT PRIMARY KEY,
#     name TEXT,
#     -- add other columns if your resources.csv has them
#     -- e.g. created_at TEXT
#     -- This is a flexible starting point; adjust as needed.
#     dummy TEXT
# );
# """
#
# CREATE_BILLING_SQL = """
# CREATE TABLE billing (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     invoice_month TEXT,
#     account_id TEXT,
#     subscription TEXT,
#     service TEXT,
#     resource_group TEXT,
#     resource_id TEXT,
#     region TEXT,
#     usage_qty REAL,
#     unit_cost REAL,
#     cost REAL
# );
# """
#
# def recreate_db(db_path: Path, overwrite: bool = False):
#     if db_path.exists():
#         if overwrite:
#             print(f"Overwriting existing DB: {db_path}")
#             db_path.unlink()
#         else:
#             raise FileExistsError(f"DB file already exists at {db_path}. Use overwrite=True to replace it.")
#     # ensure parent dir exists
#     db_path.parent.mkdir(parents=True, exist_ok=True)
#
#     conn = sqlite3.connect(str(db_path))
#     cur = conn.cursor()
#     print("Creating tables...")
#     cur.execute(CREATE_RESOURCES_SQL)
#     cur.execute(CREATE_BILLING_SQL)
#     conn.commit()
#     conn.close()
#     print("DB created at:", db_path)
#
# def ingest_csvs(db_path: Path, resources_csv: Path, billing_csv: Path):
#     print("Reading CSVs:")
#     print(" - resources:", resources_csv, "exists?", resources_csv.exists())
#     print(" - billing:", billing_csv, "exists?", billing_csv.exists())
#
#     if not resources_csv.exists() or not billing_csv.exists():
#         raise FileNotFoundError("One or both CSV files are missing. Check paths.")
#
#     df_res = pd.read_csv(resources_csv)
#     df_bill = pd.read_csv(billing_csv)
#
#     print("resources rows:", len(df_res))
#     print("billing rows:", len(df_bill))
#
#     # Normalize column names (strip, lower) if needed - keep as-is for now.
#     # Insert into DB using pandas (fast) or executemany.
#
#     conn = sqlite3.connect(str(db_path))
#
#     # Insert resources — try to infer primary key column exists
#     # If resource_id not present, create a dummy id column
#     if "resource_id" not in df_res.columns:
#         df_res["resource_id"] = df_res.index.astype(str)
#     # Keep only columns present in table (resource_id, name, dummy)
#     # Attempt to map columns; if name not present create blank
#     insert_res = pd.DataFrame({
#         "resource_id": df_res.get("resource_id"),
#         "name": df_res.get("name", ""),
#         "dummy": df_res.get("dummy", "")
#     })
#     insert_res.to_sql("resources", conn, if_exists="append", index=False)
#
#     # Prepare billing: ensure numeric columns are castable
#     for col in ("usage_qty", "unit_cost", "cost"):
#         if col in df_bill.columns:
#             df_bill[col] = pd.to_numeric(df_bill[col], errors="coerce").fillna(0.0)
#         else:
#             df_bill[col] = 0.0
#
#     # Ensure required columns exist (invoice_month, account_id, subscription, service, resource_group, resource_id, region)
#     expected_cols = ["invoice_month","account_id","subscription","service","resource_group","resource_id","region","usage_qty","unit_cost","cost"]
#     for c in expected_cols:
#         if c not in df_bill.columns:
#             df_bill[c] = None
#
#     insert_bill = df_bill[expected_cols]
#     insert_bill.to_sql("billing", conn, if_exists="append", index=False)
#
#     # verify counts
#     cur = conn.cursor()
#     cur.execute("SELECT COUNT(*) FROM resources")
#     rcount = cur.fetchone()[0]
#     cur.execute("SELECT COUNT(*) FROM billing")
#     bcount = cur.fetchone()[0]
#     conn.close()
#
#     print("Insertion complete. resources_count=", rcount, "billing_count=", bcount)
#     return rcount, bcount
#
# if __name__ == "__main__":
#     print("Backing up any existing DB first is recommended.")
#     # create fresh DB
#     recreate_db(DB_PATH, overwrite=OVERWRITE)
#     # ingest CSVs
#     rcount, bcount = ingest_csvs(DB_PATH, RESOURCES_CSV, BILLING_CSV)
#     print("Done. Recreated DB and ingested CSVs.")


# #!/usr/bin/env python3
# """
# recreate_db_from_csvs.py
# Creates a fresh SQLite DB (overwrites existing app_data.sqlite if OVERWRITE=True)
# and ingests resources.csv and billing.csv into simple schemas that match your CSVs.
# """
#
# import sqlite3
# import pandas as pd
# from pathlib import Path
#
# # Configure paths
# DB_PATH = Path(r"D:\all_proz\AI_Cost & Insights\data\db\app_data.sqlite")
# RESOURCES_CSV = Path(r"D:\all_proz\AI_Cost & Insights\data\synthetic\resources.csv")
# BILLING_CSV = Path(r"D:\all_proz\AI_Cost & Insights\data\synthetic\billing.csv")
# OVERWRITE = True  # set False to protect existing DB
#
# CREATE_RESOURCES_SQL = """
# CREATE TABLE resources (
#     resource_id TEXT PRIMARY KEY,
#     name TEXT,
#     -- add more columns if needed
#     dummy TEXT
# );
# """
#
# CREATE_BILLING_SQL = """
# CREATE TABLE billing (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     invoice_month TEXT,
#     account_id TEXT,
#     subscription TEXT,
#     service TEXT,
#     resource_group TEXT,
#     resource_id TEXT,
#     region TEXT,
#     usage_qty REAL,
#     unit_cost REAL,
#     cost REAL
# );
# """
#
# def recreate_db(db_path: Path, overwrite: bool = False):
#     if db_path.exists():
#         if overwrite:
#             print("Overwriting existing DB:", db_path)
#             db_path.unlink()
#         else:
#             raise FileExistsError(f"DB already exists at {db_path}; set OVERWRITE=True to replace it.")
#     db_path.parent.mkdir(parents=True, exist_ok=True)
#     conn = sqlite3.connect(str(db_path))
#     cur = conn.cursor()
#     cur.execute(CREATE_RESOURCES_SQL)
#     cur.execute(CREATE_BILLING_SQL)
#     conn.commit()
#     conn.close()
#     print("Created DB at:", db_path)
#
# def ingest_csvs(db_path: Path, resources_csv: Path, billing_csv: Path):
#     if not resources_csv.exists() or not billing_csv.exists():
#         raise FileNotFoundError("Missing CSVs. Check paths.")
#     df_res = pd.read_csv(resources_csv)
#     df_bill = pd.read_csv(billing_csv)
#
#     # Normalize resources
#     if "resource_id" not in df_res.columns:
#         df_res["resource_id"] = df_res.index.astype(str)
#     insert_res = pd.DataFrame({
#         "resource_id": df_res.get("resource_id"),
#         "name": df_res.get("name", ""),
#         "dummy": df_res.get("dummy", "")
#     })
#
#     # Prepare billing numeric columns
#     for col in ("usage_qty", "unit_cost", "cost"):
#         if col in df_bill.columns:
#             df_bill[col] = pd.to_numeric(df_bill[col], errors="coerce").fillna(0.0)
#         else:
#             df_bill[col] = 0.0
#
#     expected_cols = ["invoice_month","account_id","subscription","service","resource_group","resource_id","region","usage_qty","unit_cost","cost"]
#     for c in expected_cols:
#         if c not in df_bill.columns:
#             df_bill[c] = None
#
#     insert_bill = df_bill[expected_cols]
#
#     conn = sqlite3.connect(str(db_path))
#     # write using pandas to_sql
#     insert_res.to_sql("resources", conn, if_exists="append", index=False)
#     insert_bill.to_sql("billing", conn, if_exists="append", index=False)
#
#     cur = conn.cursor()
#     cur.execute("SELECT COUNT(*) FROM resources")
#     rcount = cur.fetchone()[0]
#     cur.execute("SELECT COUNT(*) FROM billing")
#     bcount = cur.fetchone()[0]
#     conn.close()
#     print("Ingest complete: resources_count =", rcount, "billing_count =", bcount)
#     return rcount, bcount
#
# if __name__ == "__main__":
#     recreate_db(DB_PATH, overwrite=OVERWRITE)
#     ingest_csvs(DB_PATH, RESOURCES_CSV, BILLING_CSV)
#     print("DB recreate + ingest finished.")


# app/services/ingestor.py
import logging
from pathlib import Path
import pandas as pd
from sqlalchemy.exc import IntegrityError
from app.db.base import SessionLocal, engine
from app.db import models, crud

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

def create_tables():
    """
    Ensure tables exist. This uses SQLAlchemy models' metadata.
    It will NOT alter existing tables (create_all is additive only).
    """
    models.Base.metadata.create_all(bind=engine)

def ingest_csv_to_sqlite(billing_csv_path: str, resources_csv_path: str) -> dict:
    """
    Ingest CSV files into the DB.

    Args:
        billing_csv_path: path to billing.csv (string)
        resources_csv_path: path to resources.csv (string)

    Returns:
        dict with counts: {"resources_inserted": n, "resources_failed": m, "billing_inserted": x, "billing_failed": y}
    """
    create_tables()
    session = SessionLocal()
    results = {
        "resources_inserted": 0,
        "resources_failed": 0,
        "billing_inserted": 0,
        "billing_failed": 0,
    }

    try:
        # ---------- Resources ----------
        rf = Path(resources_csv_path)
        if not rf.exists():
            raise FileNotFoundError(f"resources CSV not found: {rf}")
        df_res = pd.read_csv(rf)
        logger.info("Loaded resources CSV: %s rows", len(df_res))

        for i, row in enumerate(df_res.to_dict(orient="records"), start=1):
            try:
                crud.create_resource(session, row)
                session.flush()  # run SQL so DB-level errors surface here
                results["resources_inserted"] += 1
            except IntegrityError as ie:
                session.rollback()
                results["resources_failed"] += 1
                logger.warning("IntegrityError resources row #%d: %s; row=%s", i, getattr(ie, "orig", ie), row)
            except Exception as e:
                session.rollback()
                results["resources_failed"] += 1
                logger.exception("Error inserting resource row #%d: %s; row=%s", i, e, row)
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            logger.exception("Commit failed after resources: %s", e)

        # ---------- Billing ----------
        bf = Path(billing_csv_path)
        if not bf.exists():
            raise FileNotFoundError(f"billing CSV not found: {bf}")
        df_bill = pd.read_csv(bf)
        logger.info("Loaded billing CSV: %s rows", len(df_bill))

        # Ensure numeric columns exist and are cast
        for col in ("usage_qty", "unit_cost", "cost"):
            if col in df_bill.columns:
                df_bill[col] = pd.to_numeric(df_bill[col], errors="coerce").fillna(0.0)
            else:
                df_bill[col] = 0.0

        # Insert rows
        for i, row in enumerate(df_bill.to_dict(orient="records"), start=1):
            try:
                # ensure keys exist according to your model contract
                # e.g., if your Billing model requires invoice_month etc., ensure they're present
                crud.create_billing(session, row)
                session.flush()
                results["billing_inserted"] += 1
            except IntegrityError as ie:
                session.rollback()
                results["billing_failed"] += 1
                logger.warning("IntegrityError billing row #%d: %s; row=%s", i, getattr(ie, "orig", ie), row)
            except Exception as e:
                session.rollback()
                results["billing_failed"] += 1
                logger.exception("Error inserting billing row #%d: %s; row=%s", i, e, row)
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            logger.exception("Commit failed after billing: %s", e)

        return results

    finally:
        session.close()
