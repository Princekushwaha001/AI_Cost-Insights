# backend/ingest.py
import os, json
from pathlib import Path
import pandas as pd
from typing import List
from .get_embedding_function import get_embedding_function

CHROMA_DIR = os.getenv("CHROMA_DIR", "backend/chroma")

# simple splitter for long docs (for md/pdf converted text)
def chunk_text(text: str, chunk_size=1000, overlap=200):
    out=[]
    i=0
    L=len(text)
    while i < L:
        chunk = text[i: i+chunk_size]
        out.append(chunk)
        i += chunk_size - overlap
    return out

def prepare_documents_from_csv(billing_csv, resources_csv, finops_md=None):
    docs = []
    # billing
    df = pd.read_csv(billing_csv)
    for idx,row in df.reset_index().iterrows():
        text = (f"invoice_month: {row['invoice_month']}; account_id: {row['account_id']}; "
                f"subscription: {row['subscription']}; service: {row['service']}; "
                f"resource_group: {row.get('resource_group','')}; resource_id: {row['resource_id']}; "
                f"region: {row['region']}; usage_qty: {row['usage_qty']}; unit_cost: {row['unit_cost']}; cost: {row['cost']}")
        metadata = {"source_table":"billing", "row_index": int(row['index']) if 'index' in row else idx}
        docs.append((text, metadata))

    # resources
    df2 = pd.read_csv(resources_csv)
    for idx,row in df2.reset_index().iterrows():
        text = (f"resource_id: {row['resource_id']}; owner: {row['owner']}; env: {row['env']}; tags: {row['tags_json']}")
        metadata = {"source_table":"resources", "row_index": int(row['index']) if 'index' in row else idx}
        docs.append((text, metadata))

    # finops md
    if finops_md and os.path.exists(finops_md):
        txt = open(finops_md,"r",encoding="utf-8").read()
        chunks = chunk_text(txt, chunk_size=1000, overlap=200)
        for i,c in enumerate(chunks):
            docs.append((c, {"source_table":"finops_tips", "chunk": i}))

    return docs

def persist_to_chroma(docs: List[tuple], embedding_fn):
    # using langchain_chroma (as in your project)
    from langchain_chroma import Chroma
    texts = [d[0] for d in docs]
    metas = [d[1] for d in docs]
    # create or load
    db = Chroma(persist_directory=CHROMA_DIR, embedding_function=embedding_fn)
    db.add_texts(texts=texts, metadatas=metas)
    db.persist()
    return db

def ingest(billing_csv, resources_csv, finops_md=None):
    emb = get_embedding_function()
    docs = prepare_documents_from_csv(billing_csv, resources_csv, finops_md)
    db = persist_to_chroma(docs, emb)
    print(f"Ingested {len(docs)} documents to Chroma at {CHROMA_DIR}")
    return db
