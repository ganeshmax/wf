# AML Tier-1 CTR System Requirements

This directory contains the documented Epics, User Stories, and Acceptance Criteria representing all completed architecture overhauls and features delivered to the system. 

It serves as the definitive Source of Truth for existing functionality and must be updated before kicking off any new PySpark or Fullstack engineering efforts.

## Epics Inventory

1. **[Epic 1: AML System Foundation & Mock Data](./epic_01_core_foundation.md)**
   - Initial Python scripts, configuration models, and CSV mock data generators covering complex entity types (LLC, Corporate, Non-Customers) and transactional edge-case logic.

2. **[Epic 2: PySpark Data Pipelines](./epic_02_data_pipelines.md)**
   - The modularization of `utils/spark.py`, implementation of Canonical Parquet ingestion, and Universal View generation connecting Non-Customer Profiles to transactions.

3. **[Epic 3: FinCEN CTR Aggregation Rules](./epic_03_fincen_aggregation_rules.md)**
   - Strict BSA Logic including directional silos (Cash-In vs Cash-Out), Weekend-to-Monday rollforwards, Joint Account trigger duplication, and cascading Primary/Secondary relations.

4. **[Epic 4: AML Compliance Hub (Frontend UI)](./epic_04_aml_compliance_hub_ui.md)**
   - Modernization into a React & Vite single-page application. Features client-side routing, Pagination tables, Light/Dark theming, and Form 112 transaction expansion hydration.

5. **[Epic 5: AML Compliance Workflows](./epic_05_aml_compliance_workflows.md)**
   - Integration of advanced AML sub-systems: DOEP phase exemptions, SAR structuring thresholds, MIL purchase logs, and the end-to-end Form 112 Maker/Checker queue culminating in FinCEN XML representations.
