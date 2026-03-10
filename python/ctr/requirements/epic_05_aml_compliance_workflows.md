# Epic 5: AML Compliance Workflows
**Status:** Completed

## Description
Construct the interconnected AML detection modules encompassing DOEP Exemptions, SAR Structuring Alerts, Monetary Instrument Logs (MIL), and Maker/Checker form validation ending in FinCEN XML E-Filing representations.

## User Stories

### Story 5.1: DOEP Exemptions Logic
**As** a Bank Regulatory Manager,
**I want** Phase I and Phase II exempt entities (governments, domestic banks) to be stripped from the CTR payload
**So that** we do not over-report and violate the Designation of Exempt Person (DOEP) guidelines.

- **Acceptance Criteria:**
  - `data_pipelines/ingestion.py` processes an `exemptions.csv` list.
  - `data_pipelines/ctr_generation.py` executes a PySpark `left_anti` join, dropping any `customer_id` located on the `exemptions` table from the final CTR candidates list before the $10k sum is calculated.
  - The UI accurately lists all exempt entities under `Compliance Hub > DOEP Exemptions`.

### Story 5.2: Suspicious Activity Reports (SARs)
**As** a Fraud Investigator,
**I want** automated alerts for Structuring patterns 
**So that** I identify actors deliberately keeping deposits under $10,000 to evade CTRs.

- **Acceptance Criteria:**
  - `data_pipelines/sar_generation.py` leverages PySpark windowing to calculate rolling 3-day and 7-day deposit sums.
  - Generates SAR triggers for recurring identical sub-$10k deposits (e.g. $9k, $9k).
  - Flags clustered days hitting exactly ~$10.5k across a 3-day window.
  - The Compliance Hub contains a `Structuring Alerts (SAR)` view detailing the customer, alert type, triggered dates, and total velocity.

### Story 5.3: Monetary Instrument Logs (MILs)
**As** a BSA Officer,
**I want** a ledger of all official cash instrument purchases between $3k and $10k
**So that** I can track anonymous cash movements as mandated by the BSA recordkeeping rules.

- **Acceptance Criteria:**
  - `data_pipelines/mil_generation.py` filters `transactions` for `type='MONETARY_INSTRUMENT_PURCHASE'`.
  - Enforces the strict $3,000 to $10,000 bounds inclusive.
  - Stores outputs in `data/canonical/mils`.
  - The Compliance Hub presents this under `Monetary Log (MIL)`.

### Story 5.4: Maker/Checker Compliance Queue
**As** a CTR Preparer ("Maker"),
**I want** to manually review, edit, and approve auto-generated CTR drafts
**So that** incomplete reports are not filed with missing Tax Identification Numbers (TIN) or Addresses.

- **Acceptance Criteria:**
  - `ctr_generation.py` stamps each CTR with a `status`. If any entity has a blank TIN or Address, it is stamped `ACTION_REQUIRED`. If complete, `PENDING_REVIEW`.
  - The `Form 112 (Maker Queue)` UI highlights missing fields natively in the data table warning colors.
  - The UI allows inline text edits to `Address` and `TIN`.
  - Submitting changes transitions the underlying pandas database (`data/ctr/reports`) status from `ACTION_REQUIRED` to `PENDING_REVIEW`.

### Story 5.5: FinCEN E-Filing XML Generation
**As** a CTR Approver ("Checker"),
**I want** to convert my approved Forms into FinCEN BSA E-Filing XML payloads
**So that** they can be transmitted to the government batch API endpoint.

- **Acceptance Criteria:**
  - Provide an "Approve & Generate XML" button on `PENDING_REVIEW` CTR cards in the UI.
  - Button triggers `PUT /api/data/ctr_forms/{id}` to mark status `APPROVED`.
  - Instantly launches a subsequent `GET /api/data/ctr_forms/{id}/xml`.
  - `backend/services/data_service.py` intercepts the complex relational JSON form and translates it directly into structured XML tags (`<Activity>`, `<Party>`, `<PartyIdentification>`).
  - Displays the raw XML string successfully to the Checker inside a React Modal window visually.
