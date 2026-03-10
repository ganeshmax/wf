import os

# Base paths
RAW_DIR = "data/raw"
CANONICAL_DIR = "data/canonical"
AGGREGATED_DIR = "data/aggregated"
CTR_DIR = "data/ctr"

# Raw inputs
RAW_CUSTOMERS = os.path.join(RAW_DIR, "customers.csv")
RAW_NON_CUSTOMERS = os.path.join(RAW_DIR, "non_customers.csv")
RAW_LOCATIONS = os.path.join(RAW_DIR, "locations.csv")
RAW_TRANSACTIONS = os.path.join(RAW_DIR, "transactions.csv")
RAW_ACCOUNTS = os.path.join(RAW_DIR, "accounts.csv")
RAW_ACCOUNT_OWNERS = os.path.join(RAW_DIR, "account_owners.csv")
RAW_EXEMPTIONS = os.path.join(RAW_DIR, "exemptions.csv")

# Canonical outputs
CANONICAL_CUSTOMERS = os.path.join(CANONICAL_DIR, "customers")
CANONICAL_NON_CUSTOMERS = os.path.join(CANONICAL_DIR, "non_customers")
CANONICAL_LOCATIONS = os.path.join(CANONICAL_DIR, "locations")
CANONICAL_TRANSACTIONS = os.path.join(CANONICAL_DIR, "transactions")
CANONICAL_ACCOUNTS = os.path.join(CANONICAL_DIR, "accounts")
CANONICAL_ACCOUNT_OWNERS = os.path.join(CANONICAL_DIR, "account_owners")
CANONICAL_EXEMPTIONS = os.path.join(CANONICAL_DIR, "exemptions")
CANONICAL_SARS = os.path.join(CANONICAL_DIR, "sars")
CANONICAL_MILS = os.path.join(CANONICAL_DIR, "mils")

# Aggregated outputs
AGG_BEN_IN = os.path.join(AGGREGATED_DIR, "beneficiary_cash_in")
AGG_BEN_OUT = os.path.join(AGGREGATED_DIR, "beneficiary_cash_out")
AGG_COND_IN = os.path.join(AGGREGATED_DIR, "conductor_cash_in")
AGG_COND_OUT = os.path.join(AGGREGATED_DIR, "conductor_cash_out")

# CTR outputs
CTR_REPORTS = os.path.join(CTR_DIR, "reports")
CTR_STATS = os.path.join(CTR_DIR, "stats.json")

# Limits
CTR_THRESHOLD = 10000.0
