"""Audit and extraction failure tracking models."""
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base


class ExtractionFailure(Base):
    """Preserves failures, ambiguous snippets, or parsing anomalies explicitly."""
    __tablename__ = "extraction_failures"

    id = Column(String(36), primary_key=True, index=True)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    page_number = Column(Integer, nullable=True)
    
    stage = Column(String(64), nullable=False)  # "PDF_PARSING", "LLM_EXTRACTION", "NORMALIZATION", "EMBEDDING"
    raw_content = Column(Text, nullable=True)   # The snippet/text that caused the error
    error_type = Column(String(128), nullable=False)
    error_message = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)
    context_data = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="extraction_logs")
