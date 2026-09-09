# FactLens: Fact Knowledge Layer for PDF Extraction, Grounding & Reconciliation

> **Evidence-grounded cross-document fact intelligence**  
> *"Don't just extract facts. Verify them."*

- 🌐 **Live Demo**: [https://sanskarspandey.github.io/factlens/](https://sanskarspandey.github.io/factlens/)
- 🏗️ **Architecture**: React 18 / TypeScript Frontend (GitHub Pages) ──► FastAPI REST Backend (Render / Local Python 3.10+) ──► SQLite + ChromaDB Vector Layer


---

## 1. Project Overview

Financial reports, investor decks, earnings releases, and enterprise audit PDFs frequently present conflicting, updated, or contextually distinct numbers for key business metrics. **FactLens** replaces manual cross-referencing and hallucination-prone black-box LLM queries with an evidence-grounded pipeline:
- Ingests arbitrary PDFs and parses layout blocks using PyMuPDF.
- Extracts structured facts with exact verbatim evidence quotes and page numbers.
- Standardizes metrics using deterministic normalization (units, ISO currencies, fiscal periods).
- Embeds and indexes facts locally in ChromaDB using `sentence-transformers/all-MiniLM-L6-v2`.
- Performs multi-dimensional candidate matching and 4-way deterministic reconciliation.
- Presents results in a dark-mode React + TypeScript SaaS dashboard.

---

## 2. Problem Statement

Enterprises struggle to cross-verify claims across multiple PDF releases due to:
1. **Unverifiable Claims**: LLMs often generate plausible-sounding summaries without strict page-level grounding.
2. **Surface Notation Variance**: Values appear in different formats (`₹8,142 Cr` vs `₹81.42 B` vs `81,420,000,000 INR`), causing false discrepancy alerts.
3. **Context Conflation**: Legitimate differences—such as Consolidated vs Standalone reporting scopes, different fiscal periods, or actuals vs forecasts—are erroneously flagged as contradictions.
4. **Opaque Reasoning**: Black-box comparisons lack auditable arithmetic delta calculations and dimensional diagnostics.

---

## 3. Key Features

- **Generic PDF Ingestion**: PyMuPDF-based text and layout parsing for arbitrary PDF layouts without hardcoded document assumptions.
- **Strict Evidence Grounding**: Every extracted fact retains source document ID, page citation, and an exact verbatim quote verified against source page text.
- **Canonical Multi-Currency Normalization**:
  - Scales: Thousand, Million, Billion, Lakh, Crore, percentages, parenthetical negatives `(₹100 Cr)`.
  - Currencies: INR (`₹`), USD (`$`), EUR (`€`), GBP (`£`), JPY (`¥`) with strict currency isolation.
  - Temporal: Fiscal years (FY2023, FY24), quarters (Q1–Q4), and standardized date intervals.
- **Local Semantic Vector Store**: ChromaDB integration with `sentence-transformers/all-MiniLM-L6-v2` for offline embeddings.
- **Structured Candidate Matching**: Scored matching across Entity, Metric synonyms, Fiscal Period, Scope, Geography, and Currency.
- **4-Way Cross-Document Reconciliation Engine**:
  - `CORROBORATED`: Identical context with values within relative tolerance ($\le 1.0\%$).
  - `CONTRADICTED`: Identical context with material numerical variance (with delta %, absolute diff, tolerance).
  - `CONTEXTUALLY_DIFFERENT`: Scope differences (Consolidated vs Standalone), period shifts (FY23 vs FY24), or currency mismatches.
  - `UNCERTAIN`: Ambiguous metrics, ungrounded extractions, or unparseable numbers.
- **Enterprise SaaS Dashboard**: React 18 + TypeScript interface with live stats, cross-document comparison matrix, side-by-side evidence diffs, failure/uncertainty audit logs, and one-click evaluator demo scenarios.

---

## 4. Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           FactLens Frontend UI                          │
│  (React 18 + TypeScript + Vite + Lucide Icons + CSS Custom Properties)  │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ REST APIs
┌────────────────────────────────────▼────────────────────────────────────┐
│                             FastAPI Backend                             │
├─────────────────────────────────────────────────────────────────────────┤
│  1. Ingestion Layer      : PyMuPDF (fitz) page & layout parser          │
│  2. Extraction Layer     : Gemini 2.5 / OpenAI / Mock JSON Extractor    │
│  3. Normalization Engine : ISO currency, Indian/Western scales, periods │
│  4. Vector Store         : ChromaDB + all-MiniLM-L6-v2 embeddings       │
│  5. Reconciliation Core  : 4-way deterministic verification & checks    │
│  6. Persistence & Audit  : SQLite metadata store & failure logging      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Technology Stack

- **Backend**: Python 3.10+, FastAPI, SQLAlchemy, PyMuPDF (fitz), ChromaDB, SentenceTransformers, PyTorch, google-genai, openai, Pydantic v2
- **Vector Search**: Local persistent ChromaDB (`data/vector_store/`)
- **Embeddings**: SentenceTransformers (`all-MiniLM-L6-v2`, 384 dimensions)
- **Database**: SQLite with foreign keys and cascade rules
- **Frontend**: React 18, TypeScript 5, Vite 5, Lucide React, Vanilla CSS design tokens
- **Testing**: Pytest & pytest-asyncio (100% pass rate across 35 unit and integration tests)


---

## 6. End-to-End Pipeline

```
PDF Document
 ↓
PyMuPDF (fitz) [DETERMINISTIC]
 ↓
Document Pages & Text Layout Blocks [DETERMINISTIC]
 ↓
Structured Fact Extraction (LLM / Mock Provider) [LLM / EXTRACTOR]
 ↓
Evidence Grounding Verification [DETERMINISTIC]
 ↓
Deterministic Normalization & Context Enrichment [DETERMINISTIC]
 ↓
SQLite Storage & Metadata Persistence [DETERMINISTIC]
 ↓
Local Embeddings (SentenceTransformers all-MiniLM-L6-v2) [DETERMINISTIC]
 ↓
Persistent ChromaDB Vector Store [DETERMINISTIC]
 ↓
Multi-Dimensional Candidate Matching [DETERMINISTIC]
 ↓
Deterministic 4-Way Reconciliation Core [DETERMINISTIC]
 ↓
FastAPI Backend REST Layer [DETERMINISTIC]
 ↓
React 18 + TypeScript Enterprise SaaS UI [DETERMINISTIC]
```

---

## 7. Evidence Grounding & Provenance Lineage

Every extracted fact is strictly anchored to its verifiable source origin. The **Provenance Drawer** renders an auditable 6-stage lineage stepper:

```
[SOURCE DOCUMENT] ──► [SOURCE PAGE] ──► [EXACT QUOTE] ──► [EXTRACTED FACT] ──► [NORMALIZATION + CONTEXT] ──► [RECONCILIATION RESULT]
```

- **`document_id` & `document_filename`**: Source file identity.
- **`page_number`**: 1-indexed page where claim appears.
- **`evidence_quote`**: Exact verbatim substring present in the source PDF.
- **`bounding_box`**: `[x0, y0, x1, y1]` spatial coordinates.
- **Grounding Status**: `VERIFIED` (found verbatim in page text), `UNCERTAIN` (ambiguous match), or `FAILED` (hallucination prevented).

> **Integrity Guarantee**: Hallucinated quotes not present verbatim in source text are rejected or tagged as `UNCERTAIN`/`FAILED` in the Audit log. The frontend displays stored backend quotes and never synthesizes evidence.

---

## 8. Numeric Normalization

Standardizes diverse surface notations into canonical float values while preserving original raw strings:
- **Indian Notation**: `₹8,142 Cr` $\rightarrow$ `81,420,000,000.0 INR`, `25 Lakh` $\rightarrow$ `2,500,000.0`.
- **Western Notation**: `$383.29 billion` $\rightarrow$ `383,290,000,000.0 USD`, `15.4%` $\rightarrow$ `15.4 %`.
- **Parenthetical Negatives**: `(₹127 Cr)` $\rightarrow$ `-1,270,000,000.0 INR`.
- **Temporal Standard**: Standardizes `FY2024`, `FY24`, `Q4FY24`, and ISO dates.
- **Strict Currency Isolation**: Zero implicit currency conversion ($100 $\neq$ ₹100).

---

## 9. Candidate Matching

Candidate retrieval avoids naive string equality by combining vector search with dimensional scoring across 7 dimensions:
1. **Semantic Similarity**: Cosine similarity from ChromaDB vector search.
2. **Entity Score**: Exact/fuzzy token match.
3. **Attribute Score**: Synonym-aware metric matching (e.g., "Revenue from operations" $\approx$ "Total revenue").
4. **Time Score**: Fiscal year and quarter alignment.
5. **Scope Score**: Consolidated vs Standalone match.
6. **Geography Score**: Geographic jurisdiction alignment.
7. **Currency Score**: ISO currency code compatibility.

---

## 10. Reconciliation Engine & "Why This Verdict?"

Reconciliation enforces a **deterministic, context-first decision hierarchy**. Black-box LLMs are never allowed to make final numerical verdicts.

For every reconciled pair, the system generates an auditable, step-by-step diagnostic checklist:

### Why This Verdict? Examples

#### Case 1: Corroboration
```text
✓ Same entity: Delhivery
✓ Same metric: Revenue from Operations
✓ Same fiscal period: FY2024
✓ Same reporting scope: Consolidated
✓ Compatible currency: INR
✓ Values normalized: ₹81.42B vs ₹81.42B
✓ Difference: 0.00% (Allowed tolerance: 1.00%)
──► FINAL DETERMINATION: CORROBORATED
```

#### Case 2: Contradiction
```text
✓ Same entity: Delhivery
✓ Same metric: Total Employees / Headcount

✓ Same fiscal period: FY2024
✓ Same reporting scope: Consolidated
✓ Compatible units: Count
⚠ Material numerical disagreement:
  Fact A: 32,500  |  Fact B: 24,000
  Difference: 26.15% (Tolerance: 1.00%)
──► FINAL DETERMINATION: CONTRADICTED
```

#### Case 3: Contextual Difference
```text
✓ Same entity & metric: EBITDA
⚠ Context mismatch detected:
  Dimension: Reporting Scope
  Fact A: Consolidated (₹127 Cr)
  Fact B: Standalone (₹95 Cr)
  Therefore the values are not directly comparable.
──► FINAL DETERMINATION: CONTEXTUALLY DIFFERENT
```

#### Case 4: Preserved Uncertainty
```text
⚠ Insufficient evidence / Unverified grounding
  Fact B evidence could not be verified verbatim against source page text.
──► FINAL DETERMINATION: UNCERTAIN
```

---

## 11. Evaluation Lab (`/evaluation`)

The **Evaluation Lab** provides a transparent, deterministic testing workbench:

- **Live Category Execution**: Runs real deterministic test suites across 6 dimensions:
  1. Corroboration
  2. Contradiction
  3. Contextual Difference
  4. Uncertainty Preservation
  5. Evidence Grounding Verification
  6. Value & Currency Normalization
- **Scenario Cards**: Interactive cards for all 4 benchmark cases with direct one-click navigation to the Compare UI.
- **System Decision Pipeline**: Visual 7-step inspection showing which steps are strictly **DETERMINISTIC** vs **LLM-ASSISTED**.
- **System Principles**: The 5 non-negotiable architectural tenets of FactLens.

> **Honest Evaluation Policy**: Test counts reflect actual automated fixture executions (e.g. 6/6 Normalization, 1/1 Corroboration) and never fabricate synthetic "99.9% AI accuracy" metrics.

---

## 12. Synthetic Evaluator Fixtures Disclosure

Real-world financial reporting filings rarely contain blatant internal numerical contradictions within the same audit cycle. To allow evaluators to test the contradiction detection engine deterministically:
- FactLens includes labeled **Synthetic Evaluator Fixtures** (e.g., Headcount discrepancy demo).
- All synthetic records are permanently tagged with `source_type: "SYNTHETIC_DEMO"` and render with distinct `[Evaluator Demo Fixture]` warning badges.
- Genuine PDF extractions are labeled `[PDF Source]`.
- Synthetic data is never masqueraded as real source-derived evidence.

---

## 13. System Principles

1. **GROUND EVERYTHING**: Every source-derived fact must point to verifiable source evidence.
2. **NORMALIZE BEFORE COMPARING**: Values are compared only after unit, currency, and period normalization.
3. **CONTEXT BEFORE CONTRADICTION**: Different scopes, periods, or definitions do not mean contradiction.
4. **UNCERTAINTY IS A VALID RESULT**: When evidence is ambiguous or incomplete, FactLens returns `UNCERTAIN`.
5. **DETERMINISTIC FIRST**: Deterministic rules and structured comparisons resolve reliable cases before LLM reasoning.

---

## 14. API Overview

- `GET /api/v1/stats`: Live database aggregation metrics.
- `POST /api/v1/documents/upload`: PDF ingestion with SHA-256 deduplication.
- `POST /api/v1/documents/{id}/process`: Parse, extract, normalize, and index.
- `GET /api/v1/documents`: List document catalog.
- `GET /api/v1/facts`: Grounded facts ledger with filters.
- `GET /api/v1/facts/{id}/matches`: ChromaDB candidate matches.
- `POST /api/v1/comparison/compare-pair`: Pairwise fact reconciliation with `verdict_checklist`.
- `GET /api/v1/reconciliation`: Reconciled pairs with filters.
- `GET /api/v1/evaluation/latest` & `POST /api/v1/evaluation/run`: Evaluation Lab test runner.
- `GET /api/v1/audit/failures` & `GET /api/v1/audit/uncertainties`: Preserved audit logs.
- `GET /api/v1/demo/cases` & `POST /api/v1/demo/seed`: Evaluator test cases.

---

## 15. Frontend Overview

The React + TypeScript UI provides:
- **Dashboard**: Real-time KPI summary cards, product positioning, and recent activity streams.
- **Documents**: Arbitrary text-based PDF uploader, pipeline status badges, and page/fact counts.
- **Facts**: Filterable fact catalogue with a slide-out Provenance & Lineage drawer.
- **Compare**: Interactive 1-on-1 comparison with **"Why This Verdict?"** diagnostic checklists.
- **Reconciliation**: Filterable relationship ledger and cross-document comparison grid.
- **Evaluation Lab**: Deterministic test runner, benchmark scenario cards, and decision pipeline.
- **Audit / Failures**: Preserved extraction caveats, ungrounded quotes, and synthetic fixture logs.

---

## 16. Installation

```bash
# Clone the repository
cd factlens

# Set up Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

---

## 17. Environment Variables

Create `.env` in the project root:

```bash
cp .env.example .env
```

Key variables:
```ini
# Optional: Set for live Gemini 2.5 extraction; defaults to offline mock provider if unset
GEMINI_API_KEY=""

# Vector store and upload directories
VECTOR_STORE_PATH="./data/vector_store"
UPLOAD_DIR="./data/uploads"
DATABASE_URL="sqlite:///./data/factlens.db"
```

---

## 18. Running Backend

```bash
source .venv/bin/activate
uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

OpenAPI Documentation is live at: `http://127.0.0.1:8000/docs`

---

## 19. Running Frontend

```bash
cd frontend
npm run dev
```

Frontend application opens at: `http://localhost:5173`

---

## 20. Evaluator Demo (5-Minute Walkthrough)

1. **Dashboard (`/`)**: Note product positioning: *"Don't just extract facts. Verify them."*
2. **Documents (`/documents`)**: Upload any text-based PDF or view existing parsed documents.
3. **Facts (`/facts`)**: Click any fact to open the **Fact Trust & Provenance Drawer** showing source page, exact evidence quote, and the 6-stage lineage stepper.
4. **Compare (`/compare`)**: Select Fact A and Fact B, click **Run Comparison**, and inspect the **"Why This Verdict?"** deterministic checklist.
5. **Evaluation Lab (`/evaluation`)**: Click **"Run Evaluation"** to observe live deterministic test category counts (Corroboration, Contradiction, Contextual Difference, Uncertainty, Grounding, Normalization) and click any scenario card to jump directly into the Comparison view.
6. **Audit (`/audit`)**: Inspect preserved grounding failures, extraction errors, and synthetic demo fixtures.

---

## 21. Four Required Benchmark Cases

| Case | Scenario | Fact A | Fact B | Verdict |
|---|---|---|---|---|
| **Case 1** | Grounded Corroboration | Revenue ₹8,142 Cr (Annual Report P.12) | Revenue ₹81.42 B (Investor Deck P.5) | **CORROBORATED** |
| **Case 2** | Genuine Contradiction | Headcount 32,500 (Annual Report P.18) | Headcount 24,000 (Investor Deck P.22) | **CONTRADICTED** `[Demo Fixture]` |
| **Case 3** | Contextual Difference | EBITDA ₹127 Cr (Consolidated) | EBITDA ₹95 Cr (Standalone) | **CONTEXTUALLY DIFFERENT** |
| **Case 4** | Preserved Uncertainty | Projected volume 800M | Unquantified claim | **UNCERTAIN** |

---

## 22. Testing & Quality Verification

Run all 35 backend unit and integration tests:

```bash
source .venv/bin/activate
PYTHONPATH=backend pytest backend/tests -v
```

Expected output:
```
======================= 35 passed in ~19s ========================
```

Run frontend build verification:

```bash
cd frontend && npm run build
```

Expected output:
```
✓ built in <1s (0 TypeScript errors)
```

---

## 23. Limitations & Engineering Trade-offs

- **Cloud Hosting & Ephemeral Filesystem**: On free-tier cloud hosting (e.g. Render), instances sleep after inactivity and have ephemeral disk storage. If the instance restarts, click **"Reset & Seed Demo Fixtures"** or **"Run Evaluation"** on the dashboard to immediately repopulate SQLite and ChromaDB in-memory/on disk.
- **Text-Based PDFs**: PyMuPDF extraction requires digital text streams; scanned images require an OCR pre-processor.
- **Currency Isolation**: FactLens maintains currency isolation ($100 $\neq$ ₹100) and does not perform unverified spot FX conversions.
- **Deterministic Rules vs End-to-End LLM**: FactLens prioritizes deterministic arithmetic and context rules over LLM-generated summaries to ensure 100% auditability and zero hallucinated reconciliations.
- **Local Embeddings**: Uses `all-MiniLM-L6-v2` locally to ensure offline usability and complete data privacy.
- **Complex Multi-Table Visual Spanning**: Borderless multi-page tables rely on block-order parsing.


---

## 24. AI Usage & Architecture

- An LLM extraction layer structures narrative text into machine-readable JSON schemas.
- Deterministic regex, vector search, and arithmetic delta functions perform all normalization, matching, and reconciliation.

---

## 25. Future Improvements

- OCR pre-processing for legacy scanned document archives.
- User-configurable daily FX spot rate feeds for cross-currency normalizations.
- Multi-page tabular bounding box visualization overlays in PDF viewers.
