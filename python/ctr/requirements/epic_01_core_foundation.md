# Epic 1: AML System Foundation & Mock Data
**Status:** Completed

## Description
Establish the foundational data structures, configurations, and mock data generators required to simulate a Tier-1 Banking AML (Anti-Money Laundering) system, specifically focusing on Currency Transaction Reporting (CTR) and Monetary Instrument Logs (MIL).

## User Stories

### Story 1.1: Core Data Schemas
**As** a Data Engineer,
**I want** to define the canonical schemas for all banking entities
**So that** the downstream aggregation engines have a consistent, strongly-typed foundation.

- **Acceptance Criteria:**
  - `data_pipelines/schemas.py` must contain PySpark `StructType` definitions for Customers, Non-Customers, Accounts, Account Owners, Locations, Exemptions, and Transactions.

### Story 1.2: Configurable Environment
**As** a System Administrator,
**I want** all file paths and Spark connection URIs externalized into a configuration file
**So that** I can easily test the system locally or deploy it to a distributed cluster.

- **Acceptance Criteria:**
  - `data_pipelines/config.py` defines all `RAW_` and `CANONICAL_` dataset paths.
  - Paths are relative to a root `DATA_DIR` that can be overridden.

### Story 1.3: Mock Data Generator
**As** a compliance tester,
**I want** a Python script to generate realistic, simulated banking activity
**So that** I can validate the CTR rules engine without using real PII.

- **Acceptance Criteria:**
  - `scripts/generate_mock_data.py` outputs CSVs for all core entities to `data/raw/`.
  - Generates realistic entities including Individuals, LLCs, Partnerships, and Corporations.
  - Supports "Non-Customers" (people who conduct transactions but do not own accounts at the bank).
  - Generates overlapping transactions across a weekend (Saturday to Monday) to test Business Day logic.
  - Injects specific edge cases: High-value Structuring ($9k deposits), Joint Accounts, and DOEP-Exempt entities.
  - Generates sequential, readable UUIDs (`TX_000001`, `CUST_000001`) to make debugging easier.
