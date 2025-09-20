import pandas as pd
from app.services.generator import generate_csvs
from app.configs import SYNTHETIC_BILLING_CSV, SYNTHETIC_RESOURCES_CSV
SYNTHETIC_BILLING_CSV = r"D:\all_proz\AI_Cost & Insights\synthetic\billing.csv"
SYNTHETIC_RESOURCES_CSV = r"D:\all_proz\AI_Cost & Insights\synthetic\resources.csv"

if __name__ == "__main__":
    b, r = generate_csvs(billing_rows=1000, resources_rows=300)
    print("Generated files:", b, r)
