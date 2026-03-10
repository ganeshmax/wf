# Epic 3: FinCEN CTR Aggregation Rules
**Status:** Completed

## Description
Design the core PySpark intelligence to aggregate individual structured transactions into reportable $10k+ events according to established FinCEN BSA filing regulations. This involves multi-dimensional grouped sums and entity relational mapping.

## User Stories

### Story 3.1: Strict Transaction Directionality
**As** a AML Analyst,
**I want** cash-in and cash-out transactions to be aggregated independently
**So that** simultaneous deposits and withdrawals do not artificially inflate or mask a CTR trigger.

- **Acceptance Criteria:**
  - `data_pipelines/aggregation.py` must split the raw dataset by `TransactionDirection` (`Cash-In` vs `Cash-Out`).
  - CTR evaluation only sums amounts within their directional silos.

### Story 3.2: Weekend-to-Monday Business Logic
**As** a Bank Teller,
**I want** transactions occurring on Saturday and Sunday to be treated as if they occurred on Monday
**So that** split deposits over the weekend are accurately flagged as structuring/reportable by Monday's EOD sweep.

- **Acceptance Criteria:**
  - `data_pipelines/aggregation.py` includes a PySpark UDF for 'Business Day Mapping'.
  - Any transaction stamped on Saturday (`dayofweek = 7`) has `+2 days` added.
  - Sunday (`dayofweek = 1`) has `+1 day`.
  - The CTR trigger date matches the `BusinessDate` rather than the exact raw `timestamp`.

### Story 3.3: Joint Account Aggregation
**As** a Compliance Officer,
**I want** $15k deposited into a Joint Account to trigger $15k totals for BOTH account owners
**So that** all individuals profiting from the deposit are investigated.

- **Acceptance Criteria:**
  - PySpark executes an implicit `join` between the aggregated `transaction_id` and the multiple `customer_id` rows in `account_owners`.
  - Triggers correctly multiply. $15k deposited into Account A (owned by John and Mary) results in a $15k Primary Beneficiary trigger for John, and a $15k Primary Beneficiary trigger for Mary.

### Story 3.4: Primary and Secondary Structuring
**As** a FinCEN regulator,
**I want** a 360-degree view of all conductors and beneficiaries on a single Form 112
**So that** I understand the entire web of relationships participating in a $10k event.

- **Acceptance Criteria:**
  - `ctr_generation.py` processes Primary Triggers (total sums >= $10k for a specific Beneficiary) and creates a unique `report_id`.
  - Evaluates Secondary Triggers (who exactly deposited that money? who else benefited from those specific deposits if the money went into joint accounts?).
  - Maps `Primary Beneficiary`, `Primary Conductor`, `Secondary Beneficiary`, and `Secondary Conductor` roles.
  - Uses `collect_list(transaction_id)` to bundle the exact transactional evidence linking these entities to that `report_id`.
