"""Document management, PDF upload, and processing endpoints."""
import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.document import Document, DocumentStatus
from app.models.fact import Fact
from app.schemas.document import DocumentRead, DocumentDetailRead
from app.schemas.fact import FactRead
from app.schemas.common import APIResponse
from app.services.pdf_service import PDFService
from app.services.extraction_service import ExtractionService
from app.core.config import settings
from app.core.logging import logger

router = APIRouter()
pdf_service = PDFService()


@router.post("/upload", response_model=APIResponse[DocumentRead], status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Accepts arbitrary PDF files only.
    Calculates SHA-256 hash, prevents duplicates, saves file under data/uploads/,
    and creates a Document record in PENDING state.
    """
    # 1. Validate file extension
    filename = file.filename or "unknown.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF documents (.pdf) are supported."
        )

    # 2. Read contents and calculate SHA-256
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not read uploaded file: {str(e)}"
        )

    if not content or len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty (0 bytes)."
        )

    file_hash = pdf_service.calculate_file_hash(content)

    # 3. Prevent duplicate files via SHA-256
    existing_doc = db.query(Document).filter(Document.file_hash == file_hash).first()
    if existing_doc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Duplicate document detected. File already exists with ID: {existing_doc.id} ('{existing_doc.filename}')"
        )

    # 4. Save file to disk
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    clean_filename = os.path.basename(filename).replace(" ", "_")
    saved_filename = f"{file_hash[:12]}_{clean_filename}"
    saved_path = os.path.join(settings.UPLOAD_DIR, saved_filename)

    try:
        with open(saved_path, "wb") as f:
            f.write(content)
    except Exception as e:
        logger.error(f"Failed to write file {saved_path}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save document file on disk: {str(e)}"
        )

    # 5. Validate that it is a parseable PDF
    is_valid, num_pages, err = pdf_service.validate_pdf(saved_path)
    if not is_valid:
        if os.path.exists(saved_path):
            os.remove(saved_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Corrupted or invalid PDF format: {err}"
        )

    # 6. Create Document record
    doc_id = f"doc_{uuid.uuid4().hex[:12]}"
    document = Document(
        id=doc_id,
        filename=filename,
        file_path=saved_path,
        file_hash=file_hash,
        file_size=len(content),
        num_pages=num_pages,
        status=DocumentStatus.PENDING,
        metadata_json={"original_name": filename}
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return APIResponse(
        success=True,
        message="Document uploaded and registered successfully.",
        data=DocumentRead(
            id=document.id,
            filename=document.filename,
            file_path=document.file_path,
            file_hash=document.file_hash,
            file_size=document.file_size,
            num_pages=document.num_pages,
            status=document.status,
            error_message=document.error_message,
            metadata_json=document.metadata_json,
            created_at=document.created_at,
            updated_at=document.updated_at,
            fact_count=0
        )
    )


@router.post("/{document_id}/process", response_model=APIResponse[dict])
async def process_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Executes PDF processing:
    PyMuPDF page extraction -> DocumentPage records -> Grounded Fact Extraction -> Normalization -> Persistence.
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found."
        )

    extractor = ExtractionService(db)
    try:
        facts = await extractor.process_and_extract_document(document_id)
        db.refresh(document)

        fact_reads = [
            FactRead(
                id=f.id,
                document_id=f.document_id,
                page_id=f.page_id,
                page_number=f.page_number,
                document_filename=document.filename,
                statement=f.statement,
                entity=f.entity,
                attribute=f.attribute,
                raw_value=f.raw_value,
                normalized_value=f.normalized_value,
                normalized_value_str=f.normalized_value_str,
                unit=f.unit,
                currency=f.currency,
                time_period=f.time_period,
                evidence_quote=f.evidence_quote,
                bounding_box=f.bounding_box,
                confidence=f.confidence,
                status=f.status,
                uncertainty_notes=f.uncertainty_notes,
                created_at=f.created_at,
                updated_at=f.updated_at
            ).model_dump()
            for f in facts
        ]

        return APIResponse(
            success=True,
            message=f"Document processed successfully. Extracted {len(facts)} facts.",
            data={
                "document_id": document.id,
                "filename": document.filename,
                "status": document.status.value,
                "num_pages": document.num_pages,
                "facts_count": len(facts),
                "facts": fact_reads
            }
        )
    except Exception as e:
        logger.error(f"Failed processing document {document_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document extraction failed: {str(e)}"
        )


@router.get("", response_model=APIResponse[List[DocumentRead]])
@router.get("/", response_model=APIResponse[List[DocumentRead]], include_in_schema=False)
async def list_documents(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Lists all uploaded documents with processing status and extracted fact counts."""
    docs = db.query(Document).order_by(Document.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for d in docs:
        fact_count = db.query(Fact).filter(Fact.document_id == d.id).count()
        result.append(
            DocumentRead(
                id=d.id,
                filename=d.filename,
                file_path=d.file_path,
                file_hash=d.file_hash,
                file_size=d.file_size,
                num_pages=d.num_pages,
                status=d.status,
                error_message=d.error_message,
                metadata_json=d.metadata_json,
                created_at=d.created_at,
                updated_at=d.updated_at,
                fact_count=fact_count
            )
        )

    return APIResponse(
        success=True,
        data=result
    )


@router.get("/{document_id}", response_model=APIResponse[DocumentDetailRead])
async def get_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """Retrieves detailed information, parsed pages, and layout metadata for a document."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found."
        )

    fact_count = db.query(Fact).filter(Fact.document_id == doc.id).count()

    return APIResponse(
        success=True,
        data=DocumentDetailRead(
            id=doc.id,
            filename=doc.filename,
            file_path=doc.file_path,
            file_hash=doc.file_hash,
            file_size=doc.file_size,
            num_pages=doc.num_pages,
            status=doc.status,
            error_message=doc.error_message,
            metadata_json=doc.metadata_json,
            created_at=doc.created_at,
            updated_at=doc.updated_at,
            fact_count=fact_count,
            pages=doc.pages
        )
    )


@router.delete("/{document_id}", response_model=APIResponse[dict])
async def delete_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """Deletes a document, removing its file and cascading associated database records."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found."
        )

    # Remove physical file
    if doc.file_path and os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception as e:
            logger.warning(f"Could not remove physical file {doc.file_path}: {e}")

    db.delete(doc)
    db.commit()

    return APIResponse(
        success=True,
        message=f"Document '{document_id}' deleted successfully.",
        data={"deleted_document_id": document_id}
    )
