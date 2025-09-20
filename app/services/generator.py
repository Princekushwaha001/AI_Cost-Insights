import pandas as pd
import random
from faker import Faker
from app.configs import SYNTHETIC_BILLING_CSV, SYNTHETIC_RESOURCES_CSV
from datetime import datetime
fake = Faker()

SYNTHETIC_BILLING_CSV = r"D:\all_proz\AI_Cost & Insights\synthetic\billing.csv"
SYNTHETIC_RESOURCES_CSV = r"D:\all_proz\AI_Cost & Insights\synthetic\resources.csv"

SERVICE_CHOICES = ["Compute", "Storage", "DB", "Networking", "AI"]
REGIONS = ["eastus", "westus", "centralus", "ukwest", "indiawest"]
ENVS = ["prod", "staging", "dev", "test"]

def gen_billing_row():
    resource_id = f"res-{fake.uuid4()[:8]}"
    usage = round(random.uniform(0.1, 500.0), 4)
    unit_cost = round(random.uniform(0.001, 5.0), 4)
    return {
        "invoice_month": fake.date_between(start_date='-120d', end_date='today').strftime("%Y-%m"),
        "account_id": f"acct-{random.randint(1000,9999)}",
        "subscription": f"sub-{random.randint(1,50)}",
        "service": random.choice(SERVICE_CHOICES),
        "resource_group": f"rg-{fake.word()}",
        "resource_id": resource_id,
        "region": random.choice(REGIONS),
        "usage_qty": usage,
        "unit_cost": unit_cost,
        "cost": round(usage * unit_cost, 4)
    }

def gen_resource_row(resource_id=None):
    if resource_id is None:
        resource_id = f"res-{fake.uuid4()[:8]}"
    return {
        "resource_id": resource_id,
        "owner": fake.name(),
        "env": random.choice(ENVS),
        "tags_json": fake.json(data_columns={"app":"word","team":"word"})
    }

def generate_csvs(billing_rows=1000, resources_rows=300):
    # generate resources set (some resource ids reused)
    resources = []
    resource_ids = [f"res-{fake.uuid4()[:8]}" for _ in range(resources_rows)]
    for rid in resource_ids:
        resources.append(gen_resource_row(resource_id=rid))
    df_res = pd.DataFrame(resources)
    df_res.to_csv(SYNTHETIC_RESOURCES_CSV, index=False)

    # generate billing rows, random mapping to resources
    bill_rows = []
    for _ in range(billing_rows):
        r = gen_billing_row()
        # pick some existing resource id half the time
        if random.random() < 0.6:
            r["resource_id"] = random.choice(resource_ids)
        bill_rows.append(r)
    df_bill = pd.DataFrame(bill_rows)
    df_bill.to_csv(SYNTHETIC_BILLING_CSV, index=False)
    return SYNTHETIC_BILLING_CSV, SYNTHETIC_RESOURCES_CSV

if __name__ == "__main__":
    b, r = generate_csvs(500, 200)
    print("Generated:", b, r)
