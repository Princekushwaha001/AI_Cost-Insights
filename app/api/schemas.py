from pydantic import BaseModel
from typing import List, Optional

class GenerateResponse(BaseModel):
    billing_csv: str
    resources_csv: str

class EmbedResponse(BaseModel):
    count: int

class QueryRequest(BaseModel):
    query: str
    k: int = 5

class QueryResult(BaseModel):
    vector_id: int
    table_name: Optional[str]
    row_id: Optional[int]
    snippet: Optional[str]
    score: float
