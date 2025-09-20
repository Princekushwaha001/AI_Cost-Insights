from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
from app.services.generator import generate_csvs
from app.services.ingestor import ingest_csv_to_sqlite
from app.services import embedder
from app.configs import SYNTHETIC_BILLING_CSV, SYNTHETIC_RESOURCES_CSV
from app.api.schemas import GenerateResponse, EmbedResponse, QueryRequest, QueryResult
from pathlib import Path
import shutil
import tempfile

router = APIRouter()

@router.post("/generate", response_model=GenerateResponse)
def generate_data(billing_rows: int = 1000, resources_rows: int = 300):
    b, r = generate_csvs(billing_rows=billing_rows, resources_rows=resources_rows)
    return {"billing_csv": str(b), "resources_csv": str(r)}

@router.post("/ingest_from_files", response_model=EmbedResponse)
def ingest_from_files(billing_file: UploadFile = File(...), resources_file: UploadFile = File(...)):
    # save uploaded files to temp and call ingestor
    tmpdir = tempfile.mkdtemp()
    bf = Path(tmpdir) / "billing.csv"
    rf = Path(tmpdir) / "resources.csv"
    with open(bf, "wb") as f:
        shutil.copyfileobj(billing_file.file, f)
    with open(rf, "wb") as f:
        shutil.copyfileobj(resources_file.file, f)
    # ingest
    ingest_csv_to_sqlite(str(bf), str(rf))
    # embed
    count = embedder.embed_all_and_store()
    return {"count": count}

@router.post("/ingest_from_server_csv", response_model=EmbedResponse)
def ingest_from_server_csv():
    # ingest CSVs generated earlier in configs
    ingest_csv_to_sqlite(str(SYNTHETIC_BILLING_CSV), str(SYNTHETIC_RESOURCES_CSV))
    count = embedder.embed_all_and_store()
    return {"count": count}

@router.post("/query", response_model=list[QueryResult])
def query_knn(req: QueryRequest):
    results = embedder.query_knn(req.query, k=req.k)
    return results
