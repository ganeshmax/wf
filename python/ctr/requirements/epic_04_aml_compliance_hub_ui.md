# Epic 4: AML Compliance Hub (Frontend UI)
**Status:** Completed

## Description
Replace the monolithic vanilla HTML/JS dashboard with a scalable React-based web application. Introduce specialized routes, theming, datatables, and contextual detail views for Compliance personnel.

## User Stories

### Story 4.1: React & Vite Refactoring
**As** an App Developer,
**I want** to use Vite, React, and React Router to build a dynamic Single Page Application (SPA)
**So that** we have rapid hot-module reloading and strict component reusability.

- **Acceptance Criteria:**
  - `frontend/` utilizes `npm run dev` and `vite.config.js`.
  - Core views (`/customers`, `/transactions`, `/forms`) are correctly routed using `react-router-dom`.
  - A persistent, sticky sidebar tracks active routes.

### Story 4.2: Data Presentation & Pagination
**As** a Data Analyst,
**I want** clean, sortable tables for all Canonical Datasets
**So that** I can easily spot-check the PySpark ingestion quality.

- **Acceptance Criteria:**
  - Global `DataTable.jsx` component built.
  - Supports client-side pagination (e.g. 10/25/50 rows per page).
  - Integrates nicely with the `DatasetResponse` (FastAPI).

### Story 4.3: Dark Theme Interoperability
**As** an employee working late,
**I want** a universal Dark Mode toggle
**So that** using the Compliance Hub does not strain my eyes.

- **Acceptance Criteria:**
  - `ThemeContext.jsx` manages the global `theme` state.
  - CSS custom properties (`var(--bg-main)`, `var(--text-color)`, etc.) automatically adjust based on `data-theme="dark"`.
  - Forms, Tables, and Sidebar completely invert their visual footprint smoothly.

### Story 4.4: Dynamic CTR Form 112 Expansion
**As** an investigator,
**I want** to drill down into the specific transactions that triggered a Form 112
**So that** I don't need to manually cross-reference the raw Database.

- **Acceptance Criteria:**
  - The Form 112 Card view has expandable accordion rows for each `Entity` involved in the Event.
  - Expanding the row triggers an asynchronous API call to `/api/data/transactions/batch` which hydrates the raw `transaction_id` text into a detailed mini-table displaying the Date, Amount, Type, and Location Code of the exact transactions that person executed.
