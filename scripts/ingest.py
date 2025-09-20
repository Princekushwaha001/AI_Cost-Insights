# scripts/ingest.py
from backend.ingest import ingest
import sys
billing = sys.argv[1] if len(sys.argv)>1 else "data/synthetic/billing.csv"
resources = sys.argv[2] if len(sys.argv)>2 else "data/synthetic/resources.csv"
finops = sys.argv[3] if len(sys.argv)>3 else "data/finops_tips.md"
ingest(billing, resources, finops)
