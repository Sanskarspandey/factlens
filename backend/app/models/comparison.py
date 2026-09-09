"""Cross-document Fact comparison and candidate matching models."""
import enum
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Enum, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship as sa_relationship
from app.db.base import Base


class RelationshipType(str, enum.Enum):
    CORROBORATED = "CORROBORATED"
    CONTRADICTED = "CONTRADICTED"
    CONTEXTUALLY_DIFFERENT = "CONTEXTUALLY_DIFFERENT"
    UNCERTAIN = "UNCERTAIN"


class MatchType(str, enum.Enum):
    LIKELY_SAME_FACT = "LIKELY_SAME_FACT"
    RELATED_FACT = "RELATED_FACT"
    TEMPORAL_VARIANT = "TEMPORAL_VARIANT"
    INCOMPATIBLE_CONTEXT = "INCOMPATIBLE_CONTEXT"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"


class FactCandidateMatch(Base):
    """
    Phase 2 structured candidate match between two facts.
    Represents semantic similarity + structured compatibility scoring before final reconciliation.
    """
    __tablename__ = "fact_candidate_matches"

    id = Column(String(36), primary_key=True, index=True)
    source_fact_id = Column(String(36), ForeignKey("facts.id", ondelete="CASCADE"), nullable=False, index=True)
    candidate_fact_id = Column(String(36), ForeignKey("facts.id", ondelete="CASCADE"), nullable=False, index=True)

    # Detailed similarity & compatibility dimensions
    semantic_similarity = Column(Float, default=0.0)
    entity_score = Column(Float, default=0.0)
    attribute_score = Column(Float, default=0.0)
    time_score = Column(Float, default=0.0)
    scope_score = Column(Float, default=0.0)
    geography_score = Column(Float, default=0.0)
    definition_score = Column(Float, default=0.0)
    currency_score = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0, index=True)

    match_type = Column(Enum(MatchType), default=MatchType.RELATED_FACT, index=True)
    reason = Column(Text, nullable=False)
    structured_diff = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    source_fact = sa_relationship("Fact", foreign_keys=[source_fact_id])
    candidate_fact = sa_relationship("Fact", foreign_keys=[candidate_fact_id])


class FactRelationship(Base):
    """Phase 3 final reconciliation classification and structured diagnosis."""
    __tablename__ = "fact_relationships"

    id = Column(String(64), primary_key=True, index=True)
    
    fact_a_id = Column(String(36), ForeignKey("facts.id", ondelete="CASCADE"), nullable=False, index=True)
    fact_b_id = Column(String(36), ForeignKey("facts.id", ondelete="CASCADE"), nullable=False, index=True)
    
    relationship = Column(Enum(RelationshipType), nullable=False, index=True)
    confidence = Column(Float, default=1.0)
    similarity_score = Column(Float, nullable=True)
    
    # Detailed reconciliation diagnosis
    rationale = Column(Text, nullable=False)
    value_comparison = Column(JSON, nullable=True)
    context_comparison = Column(JSON, nullable=True)
    supporting_evidence = Column(JSON, nullable=True)
    uncertainty_notes = Column(Text, nullable=True)
    reasoning_method = Column(String(32), default="DETERMINISTIC", index=True)  # DETERMINISTIC, LLM_ASSISTED
    difference_analysis = Column(JSON, nullable=True)  # Backwards compatibility alias
    
    session_id = Column(String(36), ForeignKey("reconciliation_sessions.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    fact_a = sa_relationship("Fact", foreign_keys=[fact_a_id], back_populates="relationships_as_a")
    fact_b = sa_relationship("Fact", foreign_keys=[fact_b_id], back_populates="relationships_as_b")
    session = sa_relationship("ReconciliationSession", back_populates="relationships")


class ReconciliationSession(Base):
    __tablename__ = "reconciliation_sessions"

    id = Column(String(36), primary_key=True, index=True)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    document_ids = Column(JSON, nullable=False)  # List of document IDs included in the session
    summary_stats = Column(JSON, nullable=True)   # Counts: corroborated, contradicted, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

    relationships = sa_relationship("FactRelationship", back_populates="session", cascade="all, delete-orphan")
