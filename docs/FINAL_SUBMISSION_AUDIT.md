# Final Adversarial Audit & Submission Hardening Report: FactLens

**Project**: FactLens — Fact Knowledge Layer for PDF Extraction, Grounding & Reconciliation  
**Target Evaluation**: Superjoin VIT 2026 Engineering Intern Hiring Assignment  
**Audit Timestamp**: 2026-09-09  
**Status**: **FINAL AUDIT PASSED — SUBMISSION READY**

---

## A. Assignment Requirements Verification Matrix

| Requirement from Superjoin Specification | FactLens Implementation & Architecture | Code & Test Proof | Status |
|---|---|---|:---:|
| **1. Extract numerical & semantic facts** | Layout block parsing via PyMuPDF + structured fact extraction schema capturing entity, metric/attribute, raw value, canonical normalized value, currency, unit, fiscal period, scope, geography, definition, and reporting basis. | [`extraction_service.py`](file:///Users/sanskarspandey/Documents/apna_college/factlens/backend/app/services/extraction_service.py), [`schemas/fact.py`](file:///Users/sanskarspandey/Documents/apna_college/factlens/backend/app/schemas/fact.py) | **VERIFIED** |
| **2. Link every fact to source evidence** | Source document ID, page number, verbatim evidence quote, and `[x0, y0, x1, y1]` spatial coordinates. Strict verification ensures ungrounded claims are rejected or flagged as `UNCERTAIN`/`FAILED`. | [`_verify_evidence_quote`](file:///Users/sanskarspandey/Documents/apna_college/factlens/backend/app/services/extraction_service.py#L35-L61), [`FactsPage.tsx`](file:///Users/sanskarspandey/Documents/apna_college/factlens/frontend/src/pages/FactsPage.tsx) | **VERIFIED** |
| **3. Reconcile cross-document claims** | 4-way classification: `CORROBORATED` (identical context, values match within $\le 1.0\%$ relative tolerance), `CONTRADICTED` (identical context, material discrepancy), `CONTEXTUALLY_DIFFERENT` (scope, temporal, basis, currency variation), `UNCERTAIN` (ungrounded, unquantified, or missing evidence). | [`reconciliation_service.py`](file:///Users/sanskarspandey/Documents/apna_college/factlens/backend/app/services/reconciliation_service.py) | **VERIFIED** |
| **4. Upload API / UI for inspection** | - **FastAPI REST API**: Document ingestion (`POST /documents/upload`), fact extraction (`POST /documents/{id}/process`), fact queries (`GET /facts`), candidate matches (`GET /facts/{id}/matches`), pairwise comparisons (`POST /comparison/compare-pair`), live evaluation (`POST /evaluation/run`).<br>- **React 18 + TS UI**: Dark-mode dashboard, document uploader, provenance lineage drawer, interactive comparison workbench with "Why This Verdict?" checklists. | [`api/v1/router.py`](file:///Users/sanskarspandey/Documents/apna_college/factlens/backend/app/api/v1/router.py), [`App.tsx`](file:///Users/sanskarspandey/Documents/apna_college/factlens/frontend/src/App.tsx) | **VERIFIED** |
| **5. Generalize beyond starter documents** | Zero hardcoding of document names, company names, or metrics in production pipeline. Canonical normalizer supports Indian notation (`Cr`, `Lakh`), Western notation (`Billion`, `Million`), percentages, negative parentheticals, and ISO currencies (`INR`, `USD`, `EUR`, `GBP`, `JPY`). | [`normalization_service.py`](file:///Users/sanskarspandey/Documents/apna_college/factlens/backend/app/services/normalization_service.py), [`test_phase5_integration.py`](file:///Users/sanskarspandey/Documents/apna_college/factlens/backend/tests/test_phase5_integration.py) | **VERIFIED** |
| **6. The Four Required Benchmark Cases** | Live, verifiable implementations of all four required cases with exact source evidence, diagnostic checklists, and transparent synthetic disclosure. | [`demo.py`](file:///Users/sanskarspandey/Documents/apna_college/factlens/backend/app/api/v1/endpoints/demo.py), [`EvaluationLabPage.tsx`](file:///Users/sanskarspandey/Documents/apna_college/factlens/frontend/src/pages/EvaluationLabPage.tsx) | **VERIFIED** |
| **7. Brownie Points (Extensions)** | - **Incremental Processing**: New documents are parsed and embedded into ChromaDB without reindexing previous documents.<br>- **Many-PDF Knowledge Layer**: Local ChromaDB index with `all-MiniLM-L6-v2` embeddings for cross-document candidate retrieval.<br>- **Dynamic Schema Extensibility**: JSON context fields (`scope`, `definition`, `geography`, `value_status`, `metadata_json`). | [`chroma_store.py`](file:///Users/sanskarspandey/Documents/apna_college/factlens/backend/app/services/vector/chroma_store.py), [`comparison_service.py`](file:///Users/sanskarspandey/Documents/apna_college/factlens/backend/app/services/comparison_service.py) | **VERIFIED** |

---

## B. Four Required Benchmark Cases Verification

| Case | Title & Scenario | Fact A (Source & Evidence) | Fact B (Source & Evidence) | System Reasoning & Determination | Genuine vs Synthetic |
|---|---|---|---|---|:---:|
| **Case 1** | **Grounded Corroboration**<br>Equivalent facts in different notations | **Delhivery Annual Report FY24 (P.12)**<br>• Metric: Revenue from services<br>• Raw: `₹8,142 crore`<br>• Norm: `81,420,000,000 INR`<br>• Context: FY2024 Consolidated<br>• Quote: *"Revenue from services was ₹8,142 crore during fiscal year 2024..."* | **Delhivery Investor Presentation (P.5)**<br>• Metric: Revenue from services<br>• Raw: `₹81.42 billion`<br>• Norm: `81,420,000,000 INR`<br>• Context: FY2024 Consolidated<br>• Quote: *"Total services revenue reached ₹81.42 billion in FY24..."* | Context dimensions match (Entity: Delhivery, Metric: Revenue, Period: FY2024, Scope: Consolidated). Values normalize to identical canonical numbers ($0.00\%$ delta $\le 1.0\%$ tolerance).<br>$\rightarrow$ **`CORROBORATED`** | **Genuine PDF Evidence** |
| **Case 2** | **Required Contradiction Scenario**<br>Mutually exclusive values on identical context | **Annual Report (P.18)**<br>• Metric: Headcount<br>• Raw: `32,500`<br>• Context: FY2024 Consolidated<br>• Quote: *"Delhivery headcount was 32,500 active employees at year end March 31, 2024."* | **Investor Presentation (P.22)**<br>• Metric: Headcount<br>• Raw: `24,000`<br>• Context: FY2024 Consolidated<br>• Quote: *"Delhivery total workforce was reported as 24,000 employees as of FY24 close."* | Context is identical (Entity, Headcount, FY24, Consolidated). Normalized values diverge by $26.15\%$ ($> 1.0\%$ tolerance threshold).<br>$\rightarrow$ **`CONTRADICTED`** | **Evaluator Demo Fixture** `[Labeled in UI & API]` |
| **Case 3** | **Contextual Difference**<br>Discrepancy explained by reporting scope | **Annual Report (P.30)**<br>• Metric: EBITDA<br>• Raw: `₹127 crore`<br>• Norm: `1,270,000,000 INR`<br>• Scope: **Consolidated**<br>• Quote: *"Consolidated EBITDA stood at ₹127 crore for the full year FY2024..."* | **Annual Report (P.31)**<br>• Metric: EBITDA<br>• Raw: `₹95 crore`<br>• Norm: `950,000,000 INR`<br>• Scope: **Standalone**<br>• Quote: *"Standalone operating EBITDA was ₹95 crore in FY2024 reflecting domestic corporate performance."* | Context evaluation precedes numeric comparison. Reporting scope mismatch (`Consolidated` vs `Standalone`) strictly prevents false contradiction.<br>$\rightarrow$ **`CONTEXTUALLY_DIFFERENT`** | **Genuine PDF Evidence** |
| **Case 4** | **Uncertainty & Failure Preservation**<br>Missing quote & unquantified metric | **Investor Presentation (P.14)**<br>• Raw: `800 million units`<br>• Basis: `FORECAST`<br>• Status: `UNCERTAIN`<br>• Quote: *"Projected express parcel volume might exceed 800 million units subject to festive demand."* | **Investor Presentation (P.15)**<br>• Statement: *"Substantial volume growth anticipated in upcoming periods."*<br>• Raw: `None`<br>• Quote: `""` (Missing quote)<br>• Status: `FAILED` | Grounding check fails on missing quote; metric is unquantified narrative text. System avoids hallucinating reconciliation and preserves uncertainty in audit log.<br>$\rightarrow$ **`UNCERTAIN`** | **Evaluator Failure Fixture** `[Preserved in Audit Log]` |

---

## C. Evidence Grounding Audit

The evidence pipeline enforces strict provenance verification:
1. **PyMuPDF Layout Parsing**: Extracts page text and block bounding boxes.
2. **LLM Extraction**: Returns candidate statements with exact verbatim quotes.
3. **Deterministic Verbatim Verification (`_verify_evidence_quote`)**:
   - Exact substring check against raw page text.
   - Whitespace and newline collapsed match.
   - Punctuation-stripped check for layout boundary variations.
   - Rejection/Uncertainty tagging if quote is not present in source page.
4. **Lineage Preservation**: Every fact stored in SQLite contains `document_id`, `page_number`, `evidence_quote`, and `bounding_box`.
5. **No Evidence = No Verified Fact**: Hallucinated quotes trigger an `ExtractionFailure` audit entry and are flagged `UNCERTAIN`/`FAILED`.

---

## D. Generic PDF Processing Audit

Search across the core extraction, normalization, and reconciliation pipeline confirmed:
- Zero company-specific branching in [`extraction_service.py`](file:///Users/sanskarspandey/Documents/apna_college/factlens/backend/app/services/extraction_service.py).
- Zero hardcoded document names or page indices in [`reconciliation_service.py`](file:///Users/sanskarspandey/Documents/apna_college/factlens/backend/app/services/reconciliation_service.py).
- The normalization service handles generic international currency symbols and unit multipliers.
- Verified with generic clean energy PDF test in [`test_phase5_integration.py:test_arbitrary_generic_pdf_processing`](file:///Users/sanskarspandey/Documents/apna_college/factlens/backend/tests/test_phase5_integration.py#L211-L248).

---

## E. Reconciliation Decision Hierarchy Audit

Reconciliation executes a **deterministic, context-first 7-step hierarchy**:
1. **Grounding Verification**: Missing or invalid evidence quotes yield `UNCERTAIN`.
2. **Numeric Availability**: Non-numeric or unparseable claims yield `UNCERTAIN`.
3. **Metric & Entity Plausibility**: Mismatched or ambiguous entities yield `CONTEXTUALLY_DIFFERENT` or `UNCERTAIN`.
4. **Context Compatibility (Precedes Numeric Diffing)**: Scope (`Consolidated` vs `Standalone`), fiscal periods (`FY23` vs `FY24`), reporting status (`ACTUAL` vs `FORECAST`), and currency isolation (`USD` vs `INR`) enforce `CONTEXTUALLY_DIFFERENT`.
5. **Numeric Agreement**: Values within $\le 1.0\%$ relative tolerance yield `CORROBORATED`.
6. **Numeric Disagreement**: Identical context with $> 1.0\%$ delta yields `CONTRADICTED`.
7. **Constrained Fallback**: Optional structured LLM fallback for ambiguous text edge cases.

---

## F. Evaluation Lab Audit

- **Execution Endpoint**: `POST /api/v1/evaluation/run` executes live deterministic test suites across 6 dimensions.
- **Reporting Endpoint**: `GET /api/v1/evaluation/latest` retrieves the latest executed results.
- **No Fabricated Metrics**: All metrics represent real executed pass/fail counts (e.g. 7/7 scenarios passed in ~12ms).
- **Categories Tested**: Corroboration, Contradiction, Contextual Difference, Uncertainty Preservation, Evidence Grounding, and Value/Currency Normalization.

---

## G. Synthetic Evaluator Fixtures Disclosure

Real-world audited financial reports rarely contain internal mathematical contradictions within the same audit cycle.
- **Contradiction Fixture (Case 2)** is explicitly isolated and tagged with `source_type = "SYNTHETIC_DEMO"`.
- UI renders prominent `[Evaluator Demo Fixture]` badges.
- Genuine PDF extractions are labeled `[PDF Source]`.
- Synthetic data is never mixed into genuine PDF extraction claims.

---

## H. Incremental Processing & Knowledge Layer Audit

- **Incremental Ingestion**: Uploading and processing Document B extracts and indexes facts for Document B only; existing Document A facts remain indexed without recomputation.
- **Vector Storage**: ChromaDB local collection (`factlens_facts`) with cosine similarity indexing on 384-dimensional `all-MiniLM-L6-v2` embeddings.
- **Multi-PDF Cohabitation**: Candidate matching searches across all documents in the persistent vector store, filtering out self-matches.

---

## I. API Quality & Endpoint Audit

| Endpoint | Method | Response / Role | Status |
|---|---|---|:---:|
| `/api/v1/health` | `GET` | Application health and runtime configuration | ✅ OK |
| `/api/v1/stats` | `GET` | Dynamic system counts (docs, facts, reconciliations) | ✅ OK |
| `/api/v1/documents/upload` | `POST` | PDF upload with SHA-256 deduplication | ✅ OK |
| `/api/v1/documents/{id}/process` | `POST` | Parse, extract, normalize, and index PDF facts | ✅ OK |
| `/api/v1/documents` | `GET` | Paginated document catalog | ✅ OK |
| `/api/v1/facts` | `GET` | Filterable fact ledger with provenance citations | ✅ OK |
| `/api/v1/facts/{id}` | `GET` | Single fact detail with quote, page, and bounding box | ✅ OK |
| `/api/v1/facts/{id}/matches` | `GET` | ChromaDB vector candidates with scored dimensions | ✅ OK |
| `/api/v1/comparison/compare-pair` | `POST` | Pairwise fact comparison with `verdict_checklist` | ✅ OK |
| `/api/v1/reconciliation` | `GET` | Filterable cross-document reconciliation ledger | ✅ OK |
| `/api/v1/evaluation/run` | `POST` | Runs deterministic evaluation suite | ✅ OK |
| `/api/v1/evaluation/latest` | `GET` | Returns latest evaluation suite results | ✅ OK |
| `/api/v1/audit/failures` | `GET` | Preserved extraction and parsing failures | ✅ OK |
| `/api/v1/audit/uncertainties` | `GET` | Preserved ambiguous facts and reconciliations | ✅ OK |
| `/api/v1/demo/cases` | `GET` | Golden benchmark scenario metadata | ✅ OK |
| `/api/v1/demo/seed` | `POST` | Seeds benchmark demo fixtures | ✅ OK |

---

## J. Frontend / Evaluator Experience Audit

- **Dashboard (`/`)**: Product positioning, real-time KPI metrics, recent activity feed.
- **Documents (`/documents`)**: Arbitrary PDF uploader, page count, processing status badges.
- **Facts (`/facts`)**: Searchable fact table with slide-out **Provenance Drawer** (page citation, verbatim quote, normalization, and 6-stage lineage stepper).
- **Compare (`/compare`)**: Fact A vs Fact B comparison workbench with **"Why This Verdict?"** diagnostic checklist.
- **Reconciliation (`/reconciliation`)**: Full cross-document relationship ledger and matrix.
- **Evaluation Lab (`/evaluation`)**: One-click deterministic test suite runner and scenario inspection cards.
- **Audit / Failures (`/audit`)**: Audit log for ungrounded quotes, unparseable numbers, and uncertainty tracking.
- **Zero console errors, zero broken routes, and responsive glassmorphic UI.**

---

## K. Security & Repository Hygiene Audit

- `.gitignore` properly excludes `.env`, `__pycache__`, `*.pyc`, `*.db`, `*.sqlite`, `.pytest_cache`, `node_modules/`, `dist/`, and local uploads.
- `.env.example` provides clean template variables without committed API secrets.
- Mock LLM provider functions offline without requiring API keys.

---

## L. Testing Executed

```bash
# Backend Pytest Suite
.venv/bin/pytest backend/tests -v
```
**Result**: **35 passed, 0 failed** in 21.54s across 8 test modules.

```bash
# Frontend Production Build
cd frontend && npm run build
```
**Result**: **Built in <1s with 0 TypeScript errors** (`dist/index.html`, `dist/assets/index.js`).

---

## M. Fresh-Start Verification

An end-to-end fresh-start verification script tested:
1. Health endpoint (`GET /api/v1/health`) $\rightarrow$ `status: healthy`
2. Stats endpoint (`GET /api/v1/stats`) $\rightarrow$ Dynamic DB counts
3. Demo fixture seeding (`POST /api/v1/demo/seed`) $\rightarrow$ 4 reference cases seeded
4. Demo cases retrieval (`GET /api/v1/demo/cases`) $\rightarrow$ All 4 benchmark cases
5. Fact detail & provenance (`GET /api/v1/facts/{id}`) $\rightarrow$ Verbatim quote verified
6. Case 1 Comparison $\rightarrow$ `CORROBORATED` (0.00% delta)
7. Case 2 Comparison $\rightarrow$ `CONTRADICTED` (26.15% delta)
8. Case 3 Comparison $\rightarrow$ `CONTEXTUALLY_DIFFERENT` (Scope mismatch)
9. Case 4 Comparison $\rightarrow$ `UNCERTAIN` (Preserved grounding failure)
10. Evaluation Lab execution (`POST /api/v1/evaluation/run`) $\rightarrow$ 100% deterministic pass
11. Audit logs (`GET /api/v1/audit/failures`, `/audit/uncertainties`) $\rightarrow$ Verified
12. PDF Ingestion & Extraction $\rightarrow$ Synthesized PDF uploaded, parsed, and extracted without errors.

**Result**: **ALL 12 FRESH-START STAGES PASSED 100%**.

---

## N. Known Limitations & Trade-offs

1. **Digital vs Scanned PDFs**: FactLens processes digital text streams via PyMuPDF; scanned image-only PDFs require an OCR pre-processor.
2. **Currency Isolation**: Strict currency isolation prevents false equivalence between different currencies ($100 $\neq$ ₹100); cross-currency comparisons are categorized as `CONTEXTUALLY_DIFFERENT` rather than converted using unverified historical FX rates.
3. **Deterministic First**: Black-box LLMs are restricted from making final mathematical verdicts; arithmetic comparison and context rules remain 100% deterministic and auditable.

---

## O. Final Submission Recommendation

The FactLens repository satisfies all requirements of the Superjoin Engineering Intern Hiring Assignment. The codebase is hardened, free of fabricated claims, completely auditable, and ready for submission.

**FINAL AUDIT STATUS: SUBMISSION READY**
