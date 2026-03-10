# Epic 2: PySpark Data Pipelines
**Status:** Completed

## Description
Develop a suite of Apache Spark data pipelines to ingest raw flat files, standardize them into Canonical Parquet formats, and calculate primary/secondary FinCEN aggregation triggers for CTRs, SARs, and MILs.

## User Stories

### Story 2.1: Ingestion Pipeline
**As** a Data Engineer,
**I want** a standard ingestion PySpark job
**So that** raw CSV data from core banking systems is validated and strongly typed into high-performance Parquet format.

- **Acceptance Criteria:**
  - `data_pipelines/ingestion.py` exists and successfully reads all `raw/*.csv` files.
  - Applies schemas defined in `schemas.py`.
  - Saves the output as partitioned Parquet to `data/canonical/`.

### Story 2.2: Universal Entity View
**As** an AML Analyst,
**I want** CTR forms to contain PII for both account holders AND courier/conductors
**So that** the bank fulfills its "Know Your Customer" (KYC) shadow-profile obligations.

- **Acceptance Criteria:**
  - During CTR generation, `canonical_customers` and `canonical_non_customers` are joined via `unionByName` to construct a unified lookup table.
  - Conductors who do not own accounts are still successfully mapped to their PII profile on the resulting Form 112.

### Story 2.3: PySpark Modularization
**As** a DevOps Engineer,
**I want** the PySpark code refactored to share utility methods
**So that** we minimize code duplication between CTR, SAR, and aggregation scripts.

- **Acceptance Criteria:**
  - `data_pipelines/utils/spark.py` contains `get_spark_session()` initialization.
  - All PySpark jobs import from this central utility instead of bootstrapping their own Spark Contexts.
