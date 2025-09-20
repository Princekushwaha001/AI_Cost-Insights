from sqlalchemy.orm import Session
from app.db import models
from typing import Dict, Any

def create_billing(session: Session, row: Dict[str, Any]):
    obj = models.Billing(**row)
    session.add(obj)
    session.flush()  # to get id
    return obj

def create_resource(session: Session, row: Dict[str, Any]):
    obj = models.Resource(**row)
    session.add(obj)
    session.flush()
    return obj

def create_vector_meta(session: Session, vector_id: int, table_name: str, row_id: int, snippet: str):
    obj = models.VectorMetadata(vector_id=vector_id, table_name=table_name, row_id=row_id, snippet=snippet)
    session.add(obj)
    return obj
