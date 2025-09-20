from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
SYNTHETIC_DIR = DATA_DIR / "synthetic"
DB_DIR = DATA_DIR / "db"
# DB_FILE = DB_DIR / "app_data.sqlite"
DB_FILE = r"D:\all_proz\AI_Cost & Insights\data\db\app_data.sqlite"
# FAISS_INDEX_FILE = DB_DIR / "faiss_index.faiss"
FAISS_INDEX_FILE = r"D:\all_proz\AI_Cost & Insights\data\db\faiss_index.faiss"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
# SYNTHETIC_BILLING_CSV = SYNTHETIC_DIR / "billing.csv"
# SYNTHETIC_RESOURCES_CSV = SYNTHETIC_DIR / "resources.csv"
SYNTHETIC_BILLING_CSV = r"D:\all_proz\AI_Cost & Insights\data\synthetic\billing.csv"
SYNTHETIC_RESOURCES_CSV = r"D:\all_proz\AI_Cost & Insights\data\synthetic\resources.csv"
# ensure dirs
for d in [SYNTHETIC_DIR, DB_DIR]:
    d.mkdir(parents=True, exist_ok=True)


