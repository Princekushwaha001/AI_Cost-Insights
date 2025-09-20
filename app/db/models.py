from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, Text, LargeBinary
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
import datetime
from sqlalchemy.sql import func

class Billing(Base):
    __tablename__ = "billing"
    id = Column(Integer, primary_key=True, index=True)
    invoice_month = Column(String, index=True)
    account_id = Column(String, index=True)
    subscription = Column(String)
    service = Column(String)
    resource_group = Column(String)
    resource_id = Column(String, index=True)
    region = Column(String)
    usage_qty = Column(Float)
    unit_cost = Column(Float)
    cost = Column(Float)

class Resource(Base):
    __tablename__ = "resources"
    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(String, unique=True, index=True)
    owner = Column(String)
    env = Column(String)
    tags_json = Column(Text)

class VectorMetadata(Base):
    __tablename__ = "vectors"
    id = Column(Integer, primary_key=True, index=True)
    vector_id = Column(Integer, index=True, unique=True)  # id inside FAISS
    table_name = Column(String, index=True)  # e.g., 'billing' or 'resources'
    row_id = Column(Integer)  # primary key from the original table
    snippet = Column(Text)  # short textual snippet to show in RAG return
    created_at = Column(DateTime(timezone=True), server_default=func.now())
