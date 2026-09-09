# FactLens REST API Specification

Base URL: `/api/v1`

## 1. Document Endpoints (`/documents`)

### `POST /documents/upload`
Uploads and registers an arbitrary PDF document.
* **Request**: `multipart/form-data` with `file: binary`
* **Response**:
```json
{
  "success": true,
  "data": {
    "id": "doc_8f1c4a92",
    "filename": "apple_10k_2023.pdf",
    "file_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "file_size": 4194304,
    "num_pages": 78,
    "status": "PROCESSED"
  }
}
```

### `GET /documents/`
Lists all uploaded documents with metadata and extracted fact counts.

### `GET /documents/{document_id}`
Retrieves document details, parsed pages, and layout blocks.

---

## 2. Fact Extraction & Knowledge Layer (`/facts`)

### `POST /facts/extract/{document_id}`
Triggers extraction and grounding pipeline for a document.

### `GET /facts/`
Queries facts with filtering parameters (`document_id`, `entity`, `attribute`, `time_period`, `status`, `search_query`).

* **Fact Schema Example**:
```json
{
  "id": "fact_01a87b",
  "document_id": "doc_8f1c4a92",
  "page_number": 23,
  "statement": "Total net sales were $383.29 billion in fiscal year 2023.",
  "entity": "Apple Inc.",
  "attribute": "Net Sales",
  "raw_value": "$383,285 million",
  "normalized_value": 383285000000.0,
  "unit": "USD",
  "currency": "USD",
  "time_period": "FY2023",
  "evidence_quote": "Total net sales for fiscal year 2023 were $383,285 million compared to $394,328 million for fiscal year 2022.",
  "bounding_box": [72.0, 310.5, 520.0, 335.0],
  "confidence": 0.98,
  "status": "VERIFIED",
  "uncertainty_notes": null
}
```

---

## 3. Comparison & Reconciliation (`/reconciliation` & `/comparison`)

### `POST /comparison/compare-pair`
Compares two specific facts and classifies their relationship.

### `POST /reconciliation/reconcile`
Runs cross-document reconciliation between 2 or more documents.
* **Request**:
```json
{
  "document_ids": ["doc_8f1c4a92", "doc_b3e71d49"],
  "session_title": "Apple FY23 10-K vs Press Release Reconciliation"
}
```
* **Response**:
```json
{
  "id": "session_9921e",
  "title": "Apple FY23 10-K vs Press Release Reconciliation",
  "summary_stats": {
    "total_comparisons": 14,
    "corroborated_count": 11,
    "contradicted_count": 1,
    "contextually_different_count": 2,
    "uncertain_count": 0
  },
  "relationships": [
    {
      "id": "rel_5521a",
      "fact_a_id": "fact_01a87b",
      "fact_b_id": "fact_99c30f",
      "relationship": "CORROBORATED",
      "confidence": 0.95,
      "rationale": "Both facts report identical FY2023 revenue of $383.3B USD for Apple Inc."
    }
  ]
}
```
