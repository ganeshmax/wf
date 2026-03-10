# Tier-1 AML Compliance Hub: Demonstration Guide

This guide provides a step-by-step script for demonstrating the advanced Anti-Money Laundering (AML) capabilities of the Currency Transaction Reporting (CTR) engine.

## Prerequisites

Before starting the demo, ensure the backend server and frontend application are running:
1. Terminal 1: `source venv/bin/activate && uvicorn backend.main:app --reload`
2. Terminal 2: `cd frontend && npm run dev`
3. Navigate to `http://localhost:5173` in your browser.

---

## 🟢 Part 1: The Data Engineering Pipelines
Start by showing the robustness of the data ingestion and PySpark pipelines.

1. **Click "Run Ingestion"** in the sidebar. This parses raw CSVs into columnar Parquet files instantly.
2. **Click "Run Aggregations"**. Explain that this evaluates raw transactions, maps Business Days (grouping Saturday/Sunday into Monday), and aggregates deposits/withdrawals across multi-entity Joint Accounts.
3. **Click "Generate CTRs"**. Explain that this applies the DOEP Exemption logic (dropping Phase I/II exempt entities) and groups massive transaction clusters into singular, readable Form 112s.

---

## 🟢 Part 2: The Compliance Hub (Maker/Checker Workflow)
This is the core of the demo. Navigate to the **"Form 112 (Maker Queue)"** tab.

**1. Explain the Queue System by pointing out the distinct Statuses:**
- You will see a combination of Yellow `[PENDING REVIEW]` forms and Red `[ACTION REQUIRED]` forms.
- Explain that the PySpark engine automatically flagged the Red forms because they are missing critical Personally Identifiable Information (PII) like a TIN.

**2. Demonstrate the "Maker" Resolution:**
- Scroll down to an `[ACTION REQUIRED]` form.
- Expand the entity rows (using the arrow on the left).
- Point out the red warning `Missing TIN...` input box next to the customer's name.
- Click into the input box and fake-type a Social Security Number (e.g., `123-45-6789`).
- Click the purple **"Save PII & Submit to Checker"** button at the bottom of the card.
- *Watch as the form instantly transforms into a Yellow `[PENDING REVIEW]` status.*

**3. Demonstrate the "Checker" Approval:**
- Acting as a senior analyst (the Checker), review the newly updated `[PENDING REVIEW]` form.
- Click the green **"Approve & Generate XML"** button.
- *Watch as the form lock into a Green `[APPROVED]` status, indicating it's ready for FinCEN transmission.*

---

## 🟢 Part 3: Advanced FinCEN Relational Scenarios
Show off the true power of the aggregation engine by exploring the expanded Form 112s.

**1. The Complex Entity Hierarchy:**
- Find a form with a high Entity Count (e.g. 3+ entities). 
- Point out the color-coded badges indicating `Primary Beneficiary` vs `Primary Conductor` vs `Secondary Beneficiary`.
- Explain that an employee (Conductor) depositing money into 3 different business accounts triggers a *single* CTR mapping 4 human beings tightly together.

**2. Full Transaction Hydration:**
- Expand a row by clicking the arrow. Notice the localized loading indicator perfectly populating the underlying `Underlying Transactions` sub-table in real-time.
- Emphasize that analysts no longer have to guess *why* an aggregation happened; the exact receipts are pinned to the bottom of the Form.

**3. Joint Accounts & The Weekend Rule:**
- Find a massive Monday deposit Form 112 (Date will likely be the most recent Monday in the mock data, typically $11,000+).
- Expand the two `Primary Beneficiary` rows. Notice they are both explicitly listed for the exact same dollar amount.
- Open the transaction layer. You will explicitly see sub-transactions occurring on *Saturday* and *Sunday*, successfully rolled-forward by PySpark into the Monday queue and safely "exploded" across both Joint Account owners.

---

## 🟢 Part 4: Advanced AML Modules (SARs & MILs)
Wrap up the demo by exploring the interconnected compliance ledgers.

**1. Structuring Alerts (SARs):**
- Navigate to the **"Structuring Alerts (SAR)"** tab on the sidebar.
- Show the table of alerts. Explain that this PySpark job calculates 7-day rolling cash deposit windows. 
- Point out the massive $19,000 flag where a Structurer deposited $9,500 on consecutive days to successfully evade the $10,000 CTR trigger, but was actively caught by this specialized SAR logic.

**2. Monetary Instruments (MIL):**
- Navigate to the **"Monetary Log (MIL)"** tab.
- Explain that cash purchases of Cashier's Checks strictly between $3,000 and $10,000 sidestep CTRs entirely, but BSA compliance requires a pristine electronic ledger for these events.
- Highlight the exact timestamps, branch locations, and physical addresses collected automatically by the system.
