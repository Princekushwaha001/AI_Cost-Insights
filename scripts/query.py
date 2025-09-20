# scripts/query.py
from backend.rag_runner import answer_with_rag
from backend.analytics import is_numeric_question, compute_simple_stats, render_plot_to_base64, render_table_to_base64
import sys, json

q = " ".join(sys.argv[1:]) if len(sys.argv)>1 else input("Query: ")
resp = answer_with_rag(q, k=5)
out = {"answer":resp["answer"], "source": resp["source"], "retrieved": resp["retrieved"]}
# if numeric question, compute chart
from backend.analytics import is_numeric_question, compute_simple_stats, render_plot_to_base64
if is_numeric_question(q):
    stats = compute_simple_stats("data/synthetic/billing.csv", q)
    png = render_plot_to_base64(stats["table"])
    out["chart_base64"] = png
print(json.dumps(out, indent=2))
