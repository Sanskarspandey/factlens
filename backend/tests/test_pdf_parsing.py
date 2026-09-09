"""Unit tests for PyMuPDF PDF parsing and visual grounding."""
import os
import tempfile
import pymupdf as fitz
from app.services.pdf_service import PDFService
from app.core.exceptions import InvalidPDFError


def test_pdf_validation_and_hashing(sample_pdf_bytes):
    pdf_service = PDFService()
    
    # Check SHA-256 calculation
    file_hash = pdf_service.calculate_file_hash(sample_pdf_bytes)
    assert len(file_hash) == 64
    assert isinstance(file_hash, str)

    # Validate temporary PDF file
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(sample_pdf_bytes)
        temp_path = f.name

    try:
        is_valid, num_pages, err = pdf_service.validate_pdf(temp_path)
        assert is_valid is True
        assert num_pages == 2
        assert err == ""
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_extract_pages_and_layout(sample_pdf_bytes):
    pdf_service = PDFService()
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(sample_pdf_bytes)
        temp_path = f.name

    try:
        pages = pdf_service.extract_pages(temp_path)
        assert len(pages) == 2
        
        # Check Page 1
        p1 = pages[0]
        assert p1["page_number"] == 1
        assert "Acme Corporation" in p1["raw_text"]
        assert "$383.29 billion" in p1["raw_text"]
        assert len(p1["layout_blocks"]) > 0
        assert p1["width"] > 0 and p1["height"] > 0

        # Check Page 2
        p2 = pages[1]
        assert p2["page_number"] == 2
        assert "INR 8,142 Cr" in p2["raw_text"]
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_find_quote_bounding_box(sample_pdf_bytes):
    pdf_service = PDFService()
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(sample_pdf_bytes)
        temp_path = f.name

    try:
        # Ground quote on page 1
        quote_p1 = "total revenue of $383.29 billion"
        bbox = pdf_service.find_quote_bounding_box(temp_path, 1, quote_p1)
        assert bbox is not None
        assert len(bbox) == 4
        assert bbox[2] > bbox[0] and bbox[3] > bbox[1]

        # Ground quote on page 2
        quote_p2 = "total revenues of INR 8,142 Cr"
        bbox_p2 = pdf_service.find_quote_bounding_box(temp_path, 2, quote_p2)
        assert bbox_p2 is not None
        assert len(bbox_p2) == 4

        # Non-existent quote on page 1
        fake_quote = "This text does not exist anywhere in the PDF"
        fake_bbox = pdf_service.find_quote_bounding_box(temp_path, 1, fake_quote)
        assert fake_bbox is None
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
