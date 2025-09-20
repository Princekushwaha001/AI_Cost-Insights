# # backend/evaluate.py
# from backend.get_embedding_function import get_embedding_function
# from langchain_chroma import Chroma
# import numpy as np
#
# CHROMA_DIR = "backend/chroma"
#
# # Example test set: 10-15 Q/A pairs. For each QA we include an expected doc metadata signature
# TEST_SET = [
#     {"q":"Which service had highest total cost in 2025-07?", "expected_source": {"source_table":"billing"} },
#     {"q":"Who owns resource res-abc123?", "expected_source": {"source_table":"resources"} },
#     # ... add 10-15 items here tuned to your synthetic data
# ]
#
# def recall_at_k(query, expected_predicate, k=5, emb_fn=None):
#     if emb_fn is None:
#         emb_fn = get_embedding_function()
#     db = Chroma(persist_directory=CHROMA_DIR, embedding_function=emb_fn)
#     results = db.similarity_search_with_score(query, k=k)
#     # check if any returned doc matches expected predicate
#     for doc, score in results:
#         meta = doc.metadata
#         ok = True
#         for k2,v2 in expected_predicate.items():
#             if meta.get(k2) != v2:
#                 ok = False; break
#         if ok:
#             return 1
#     return 0
#
# def run_recall_eval(k=5):
#     emb = get_embedding_function()
#     total = len(TEST_SET)
#     hits = 0
#     for t in TEST_SET:
#         hits += recall_at_k(t["q"], t["expected_source"], k=k, emb_fn=emb)
#     recall = hits / total
#     print(f"Recall@{k} = {recall:.3f} ({hits}/{total})")
#     return recall
#
# # rubric: human evaluator rates 1-5 on correctness, completeness, and evidence usage
# RUBRIC = {
#     "1": "Incorrect or misleading, no evidence.",
#     "2": "Partially correct but incomplete, weak or missing evidence.",
#     "3": "Correct but misses some detail; evidence provided but limited.",
#     "4": "Good answer with clear evidence and a few actionable suggestions.",
#     "5": "Accurate, detailed, with precise evidence and actionable next steps."
# }

# backend/evaluate.py
import os
from backend.get_embedding_function import get_embedding_function

# Try both import paths for Chroma depending on installed package
try:
    from langchain_chroma import Chroma
except ImportError:
    try:
        from langchain.vectorstores import Chroma
    except ImportError as e:
        raise ImportError(
            "Chroma not found. Please install with: pip install langchain-chroma"
        ) from e

CHROMA_DIR = os.getenv("CHROMA_DIR", "backend/chroma")

# Example test set: 10-15 Q/A pairs. For each QA we include an expected doc metadata signature
TEST_SET = [
    {"q": "Which service had highest total cost in 2025-07?", "expected_source": {"source_table": "billing"}},
    {"q": "Who owns resource res-abc123?", "expected_source": {"source_table": "resources"}},
    # ... add 10-15 items here tuned to your synthetic data
]


def recall_at_k(query, expected_predicate, k=5, emb_fn=None):
    """
    Check if any of the top-k retrieved docs has metadata matching the expected predicate.
    Returns 1 if found, else 0.
    """
    if emb_fn is None:
        emb_fn = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_DIR, embedding_function=emb_fn)
    results = db.similarity_search_with_score(query, k=k)
    for doc, score in results:
        meta = getattr(doc, "metadata", {})
        ok = True
        for k2, v2 in expected_predicate.items():
            if meta.get(k2) != v2:
                ok = False
                break
        if ok:
            return 1
    return 0


def run_recall_eval(k=5):
    """
    Run recall@k evaluation across TEST_SET.
    """
    emb = get_embedding_function()
    total = len(TEST_SET)
    hits = 0
    for t in TEST_SET:
        hits += recall_at_k(t["q"], t["expected_source"], k=k, emb_fn=emb)
    recall = hits / total if total > 0 else 0
    print(f"Recall@{k} = {recall:.3f} ({hits}/{total})")
    return recall


# rubric: human evaluator rates 1–5 on correctness, completeness, and evidence usage
RUBRIC = {
    "1": "Incorrect or misleading, no evidence.",
    "2": "Partially correct but incomplete, weak or missing evidence.",
    "3": "Correct but misses some detail; evidence provided but limited.",
    "4": "Good answer with clear evidence and a few actionable suggestions.",
    "5": "Accurate, detailed, with precise evidence and actionable next steps.",
}


if __name__ == "__main__":
    # Allow running directly with python -m backend.evaluate
    run_recall_eval(k=5)
