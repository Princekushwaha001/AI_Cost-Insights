from app.services.ingestor import ingest_csv_to_sqlite
from app.services.embedder import embed_all_and_store
from app.configs import SYNTHETIC_BILLING_CSV, SYNTHETIC_RESOURCES_CSV

if __name__ == "__main__":
    print("Ingesting CSVs into SQLite...")
    ingest_csv_to_sqlite(str(SYNTHETIC_BILLING_CSV), str(SYNTHETIC_RESOURCES_CSV))
    print("Building embeddings and FAISS index...")
    count = embed_all_and_store()
    print("Indexed vectors:", count)
