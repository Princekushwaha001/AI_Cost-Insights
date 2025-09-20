# backend/analytics.py
import pandas as pd
import io, base64
import matplotlib.pyplot as plt
import re
from pathlib import Path

def is_numeric_question(query: str) -> bool:
    keywords = ["trend", "per month", "per service", "cost trend", "top", "sum", "average", "usage"]
    q = query.lower()
    return any(k in q for k in keywords)

def compute_simple_stats(billing_csv, query):
    df = pd.read_csv(billing_csv, parse_dates=["invoice_month"], infer_datetime_format=True, low_memory=False)
    # heuristics
    if "per service" in query.lower() or "usage per service" in query.lower():
        agg = df.groupby("service")["cost"].sum().reset_index().sort_values("cost", ascending=False)
        return {"type":"service", "table":agg}
    if "trend" in query.lower() or "per month" in query.lower():
        agg = df.groupby("invoice_month")["cost"].sum().reset_index().sort_values("invoice_month")
        return {"type":"month", "table":agg}
    # fallback: top 10 expensive resources
    agg = df.groupby("resource_id")["cost"].sum().reset_index().sort_values("cost", ascending=False).head(10)
    return {"type":"top_resources", "table":agg}

def render_table_to_base64(df):
    buf = io.BytesIO()
    fig, ax = plt.subplots(figsize=(6, max(2, min(6, len(df)/3))))
    ax.axis('off')
    table = ax.table(cellText=df.values, colLabels=df.columns, loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    fig.tight_layout()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def render_plot_to_base64(df, plot_type="bar"):
    buf = io.BytesIO()
    fig, ax = plt.subplots(figsize=(6,3))
    if df.shape[1] >= 2:
        x = df.iloc[:,0].astype(str)
        y = df.iloc[:,1].astype(float)
        ax.bar(x, y)
        ax.set_xticklabels(x, rotation=45, ha='right')
    fig.tight_layout()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')
