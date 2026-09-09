"""Fact database model."""
import enum
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Enum, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base


class FactStatus(str, enum.Enum):
    EXTRACTED = "EXTRACTED"
    VERIFIED = "VERIFIED"
    UNCERTAIN = "UNCERTAIN"
    FAILED = "FAILED"
    FLAGGED = "FLAGGED"


class ValueStatus(str, enum.Enum):
    ACTUAL = "ACTUAL"
    ESTIMATE = "ESTIMATE"
    FORECAST = "FORECAST"
    GUIDANCE = "GUIDANCE"
    TARGET = "TARGET"
    UNKNOWN = "UNKNOWN"


class Fact(Base):
    __tablename__ = "facts"

    id = Column(String(36), primary_key=True, index=True)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    page_id = Column(String(36), ForeignKey("document_pages.id", ondelete="SET NULL"), nullable=True)
    page_number = Column(Integer, nullable=False, index=True)  # 1-indexed

    # Semantic Fact Structure
    statement = Column(Text, nullable=False)
    entity = Column(String(255), nullable=True, index=True)      # e.g., "Delhivery", "Acme Corp"
    attribute = Column(String(255), nullable=True, index=True)   # e.g., "Revenue from operations", "Operating Margin"
    
    # Grounding & Provenance
    evidence_quote = Column(Text, nullable=False)               # Verbatim text snippet from PDF
    bounding_box = Column(JSON, nullable=True)                  # Grounding coordinates [x0, y0, x1, y1]
    
    # Normalized Data Points
    raw_value = Column(String(255), nullable=True)              # e.g., "₹8,142 Cr", "$383.29 billion"
    normalized_value = Column(Float, nullable=True)             # e.g., 81420000000.0
    normalized_value_str = Column(String(255), nullable=True)   # canonical string representation
    unit = Column(String(64), nullable=True)                    # e.g., "INR", "USD", "%"
    currency = Column(String(16), nullable=True)                # e.g., "INR", "USD", "EUR"
    time_period = Column(String(64), nullable=True, index=True) # e.g., "FY2024", "2023-Q4"
    fiscal_year = Column(String(32), nullable=True, index=True) # e.g., "FY2024"
    quarter = Column(String(16), nullable=True, index=True)     # e.g., "Q1", "Q4"

    # Contextual Dimensions
    geography = Column(String(128), nullable=True, index=True)  # e.g., "India", "Global"
    scope = Column(String(128), nullable=True, index=True)      # e.g., "Consolidated", "Standalone"
    definition = Column(String(128), nullable=True, index=True) # e.g., "GAAP", "Non-GAAP", "Adjusted EBITDA"
    source_section = Column(String(255), nullable=True)         # e.g., "Management Discussion"
    value_status = Column(Enum(ValueStatus), default=ValueStatus.ACTUAL, index=True)

    # Extraction Quality & Uncertainty Preservation
    confidence = Column(Float, default=1.0)
    status = Column(Enum(FactStatus), default=FactStatus.EXTRACTED, index=True)
    uncertainty_notes = Column(Text, nullable=True)             # Preserves ambiguity / parsing caveats
    
    # Vector Indexing
    embedding_id = Column(String(64), nullable=True, index=True)
    indexing_status = Column(String(32), default="PENDING", index=True)  # PENDING, INDEXED, FAILED
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="facts")
    page = relationship("DocumentPage", back_populates="facts")
    relationships_as_a = relationship("FactRelationship", foreign_keys="[FactRelationship.fact_a_id]", back_populates="fact_a", cascade="all, delete-orphan")
    relationships_as_b = relationship("FactRelationship", foreign_keys="[FactRelationship.fact_b_id]", back_populates="fact_b", cascade="all, delete-orphan")
