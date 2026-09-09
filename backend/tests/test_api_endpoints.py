"""Integration tests for all Phase 1 REST API endpoints."""
import io
import pytest
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app"] == "FactLens"
    assert data["database"] == "sqlite"


def test_upload_and_duplicate_detection(client: TestClient, sample_pdf_bytes):
    # 1. Upload valid PDF
    files = {"file": ("acme_report.pdf", sample_pdf_bytes, "application/pdf")}
    response = client.post("/api/v1/documents/upload", files=files)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["success"] is True
    doc = res_data["data"]
    doc_id = doc["id"]
    assert doc_id.startswith("doc_")
    assert doc["filename"] == "acme_report.pdf"
    assert doc["status"] == "PENDING"
    assert doc["num_pages"] == 2

    # 2. Upload the exact same PDF -> Must fail with 409 Conflict
    files_dup = {"file": ("acme_report_copy.pdf", sample_pdf_bytes, "application/pdf")}
    response_dup = client.post("/api/v1/documents/upload", files=files_dup)
    assert response_dup.status_code == 409
    assert "Duplicate document" in response_dup.json()["detail"]


def test_invalid_upload_formats(client: TestClient):
    # Non-PDF file
    files = {"file": ("notes.txt", b"Some random text file content", "text/plain")}
    response = client.post("/api/v1/documents/upload", files=files)
    assert response.status_code == 400
    assert "Only PDF documents" in response.json()["detail"]

    # Empty 0-byte file
    files_empty = {"file": ("empty.pdf", b"", "application/pdf")}
    response_empty = client.post("/api/v1/documents/upload", files=files_empty)
    assert response_empty.status_code == 400


def test_document_processing_and_facts_lifecycle(client: TestClient, sample_pdf_bytes):
    # 1. Upload PDF
    files = {"file": ("financial_statement.pdf", sample_pdf_bytes, "application/pdf")}
    upload_res = client.post("/api/v1/documents/upload", files=files)
    assert upload_res.status_code == 201
    doc_id = upload_res.json()["data"]["id"]

    # 2. Process Document
    process_res = client.post(f"/api/v1/documents/{doc_id}/process")
    assert process_res.status_code == 200
    proc_data = process_res.json()["data"]
    assert proc_data["document_id"] == doc_id
    assert proc_data["status"] == "PROCESSED"
    assert proc_data["num_pages"] == 2
    assert proc_data["facts_count"] > 0
    assert len(proc_data["facts"]) > 0

    first_fact = proc_data["facts"][0]
    fact_id = first_fact["id"]
    assert first_fact["document_id"] == doc_id
    assert first_fact["page_number"] in [1, 2]
    assert len(first_fact["evidence_quote"]) > 0

    # 3. List Documents
    list_docs_res = client.get("/api/v1/documents/")
    assert list_docs_res.status_code == 200
    docs = list_docs_res.json()["data"]
    assert len(docs) >= 1
    found_doc = next(d for d in docs if d["id"] == doc_id)
    assert found_doc["status"] == "PROCESSED"
    assert found_doc["fact_count"] > 0

    # 4. Get Document Detail
    detail_res = client.get(f"/api/v1/documents/{doc_id}")
    assert detail_res.status_code == 200
    detail_data = detail_res.json()["data"]
    assert len(detail_data["pages"]) == 2

    # 5. List Facts
    facts_res = client.get(f"/api/v1/facts/?document_id={doc_id}")
    assert facts_res.status_code == 200
    facts_list = facts_res.json()["data"]
    assert len(facts_list) >= 1

    # 6. Get Fact by ID
    fact_res = client.get(f"/api/v1/facts/{fact_id}")
    assert fact_res.status_code == 200
    fact_detail = fact_res.json()["data"]
    assert fact_detail["id"] == fact_id
    assert fact_detail["document_id"] == doc_id
    assert fact_detail["document_filename"] == "financial_statement.pdf"


def test_reconciliation_api_endpoints(client: TestClient, sample_pdf_bytes):
    # Upload and process document
    files = {"file": ("report_recon.pdf", sample_pdf_bytes, "application/pdf")}
    upload_res = client.post("/api/v1/documents/upload", files=files)
    doc_id = upload_res.json()["data"]["id"]
    client.post(f"/api/v1/documents/{doc_id}/process")

    # 1. Run Reconciliation
    run_res = client.post("/api/v1/reconciliation/run", json={"min_candidate_score": 0.20})
    assert run_res.status_code == 200
    run_data = run_res.json()["data"]
    assert "total_evaluated" in run_data

    # 2. List Reconciliations
    list_res = client.get("/api/v1/reconciliation")
    assert list_res.status_code == 200
    assert list_res.json()["success"] is True

    # 3. List with filter
    filter_res = client.get("/api/v1/reconciliation?relationship=CORROBORATED")
    assert filter_res.status_code == 200
