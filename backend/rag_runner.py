# backend/rag_runner.py
from langchain_chroma import Chroma
from .get_embedding_function import get_embedding_function
from .prompts import build_prompt
from .query_data import query_open_source_llm   # reuse your existing LLM routing
import os

CHROMA_DIR = os.getenv("CHROMA_DIR", "backend/chroma")
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.65"))

def retrieve_with_scores(query, k=5):
    emb = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_DIR, embedding_function=emb)
    results = db.similarity_search_with_score(query, k=k)
    # results: list of (Document, score)
    # convert to easily-consumable dicts
    out = []
    for doc, score in results:
        out.append({
            "content": doc.page_content,
            "metadata": doc.metadata,
            "score": float(score)
        })
    return out

def answer_with_rag(query, k=5):
    retrieved = retrieve_with_scores(query, k=k)
    relevant = [r for r in retrieved if r["score"] >= SIMILARITY_THRESHOLD]
    if not relevant:
        # fallback: call open-source LLM purely
        prompt = f"Answer this question without additional context: {query}"
        resp = query_open_source_llm(prompt)
        return {"answer": resp, "source": "fallback", "retrieved": []}
    # build context by concatenating top-k content
    ctx = "\n\n---\n\n".join([r["content"] for r in relevant])
    prompt = build_prompt(ctx, query)
    resp = query_open_source_llm(prompt)
    return {"answer": resp, "source": "rag", "retrieved": relevant}
