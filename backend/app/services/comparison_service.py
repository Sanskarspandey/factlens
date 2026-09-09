"""Candidate retrieval, structured scoring, and fact comparison service."""
import uuid
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.fact import Fact
from app.models.comparison import FactCandidateMatch, MatchType
from app.services.vector.embeddings import embedding_service, build_fact_semantic_representation
from app.services.vector.chroma_store import vector_store
from app.core.logging import logger


class CandidateMatchingService:
    """
    Retrieves and evaluates candidate matching facts using vector search
    combined with structured dimensional scoring (entity, attribute, time, currency, scope).
    """

    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    def index_fact(self, fact: Fact) -> bool:
        """Generates embedding and upserts a single fact into vector store."""
        try:
            semantic_text = build_fact_semantic_representation(fact)
            embedding = self.embedding_service.encode_text(semantic_text)
            
            metadata = {
                "fact_id": fact.id,
                "document_id": fact.document_id,
                "entity": fact.entity or "",
                "attribute": fact.attribute or "",
                "time_period": fact.time_period or "",
                "fiscal_year": fact.fiscal_year or "",
                "quarter": fact.quarter or "",
                "geography": fact.geography or "",
                "currency": fact.currency or "",
                "unit": fact.unit or "",
                "status": fact.status.value if fact.status else ""
            }

            self.vector_store.add_facts([{
                "fact_id": fact.id,
                "embedding": embedding,
                "metadata": metadata,
                "document": semantic_text
            }])

            fact.embedding_id = fact.id
            fact.indexing_status = "INDEXED"
            return True
        except Exception as e:
            logger.error(f"Failed to index fact {fact.id}: {e}")
            fact.indexing_status = "FAILED"
            return False

    def index_all_facts(self) -> int:
        """Re-indexes all facts from SQLite into ChromaDB."""
        facts = self.db.query(Fact).all()
        indexed_count = 0
        items = []
        for f in facts:
            semantic_text = build_fact_semantic_representation(f)
            items.append((f, semantic_text))

        if not items:
            return 0

        texts = [item[1] for item in items]
        embeddings = self.embedding_service.encode_many(texts)

        vector_items = []
        for (f, sem_text), emb in zip(items, embeddings):
            metadata = {
                "fact_id": f.id,
                "document_id": f.document_id,
                "entity": f.entity or "",
                "attribute": f.attribute or "",
                "time_period": f.time_period or "",
                "fiscal_year": f.fiscal_year or "",
                "quarter": f.quarter or "",
                "geography": f.geography or "",
                "currency": f.currency or "",
                "unit": f.unit or "",
                "status": f.status.value if f.status else ""
            }
            vector_items.append({
                "fact_id": f.id,
                "embedding": emb,
                "metadata": metadata,
                "document": sem_text
            })
            f.embedding_id = f.id
            f.indexing_status = "INDEXED"
            indexed_count += 1

        self.vector_store.add_facts(vector_items)
        self.db.commit()
        return indexed_count

    def find_and_score_candidates_for_fact(
        self,
        fact: Fact,
        top_k: int = 10,
        min_score_threshold: float = 0.30
    ) -> List[FactCandidateMatch]:
        """
        1. Embeds source fact.
        2. Queries top-K candidates from vector store.
        3. Excludes self-matches.
        4. Calculates structured multi-dimensional compatibility scores.
        5. Assigns MatchType and persists/returns candidate matches.
        """
        semantic_text = build_fact_semantic_representation(fact)
        query_embedding = self.embedding_service.encode_text(semantic_text)

        # Retrieve top candidates from vector store
        store_count = self.vector_store.count() or 50
        raw_candidates = self.vector_store.query_similar_facts(
            query_embedding=query_embedding,
            n_results=max(store_count, 100)
        )

        matches: List[FactCandidateMatch] = []

        for cand in raw_candidates:
            cand_id = cand["fact_id"]
            if cand_id == fact.id:
                # Exclude self-match
                continue

            cand_fact = self.db.query(Fact).filter(Fact.id == cand_id).first()
            if not cand_fact:
                continue

            scores = self._calculate_structured_scores(fact, cand_fact, cand["similarity"])
            overall_score = scores["overall_score"]

            if overall_score < min_score_threshold:
                continue

            match_type, reason = self._classify_match(fact, cand_fact, scores)

            # Check if match record already exists in DB
            match_id = f"match_{fact.id}_{cand_fact.id}"
            match_record = self.db.query(FactCandidateMatch).filter(
                FactCandidateMatch.source_fact_id == fact.id,
                FactCandidateMatch.candidate_fact_id == cand_fact.id
            ).first()

            if not match_record:
                match_record = FactCandidateMatch(
                    id=match_id,
                    source_fact_id=fact.id,
                    candidate_fact_id=cand_fact.id,
                    semantic_similarity=scores["semantic_similarity"],
                    entity_score=scores["entity_score"],
                    attribute_score=scores["attribute_score"],
                    time_score=scores["time_score"],
                    scope_score=scores["scope_score"],
                    geography_score=scores["geography_score"],
                    definition_score=scores["definition_score"],
                    currency_score=scores["currency_score"],
                    overall_score=overall_score,
                    match_type=match_type,
                    reason=reason,
                    structured_diff={
                        "source_value": fact.normalized_value_str or fact.raw_value,
                        "candidate_value": cand_fact.normalized_value_str or cand_fact.raw_value,
                        "source_period": fact.time_period,
                        "candidate_period": cand_fact.time_period,
                        "currency_match": scores["currency_score"] == 1.0,
                        "unit_match": fact.unit == cand_fact.unit
                    }
                )
                self.db.add(match_record)
            else:
                match_record.semantic_similarity = scores["semantic_similarity"]
                match_record.entity_score = scores["entity_score"]
                match_record.attribute_score = scores["attribute_score"]
                match_record.time_score = scores["time_score"]
                match_record.scope_score = scores["scope_score"]
                match_record.geography_score = scores["geography_score"]
                match_record.definition_score = scores["definition_score"]
                match_record.currency_score = scores["currency_score"]
                match_record.overall_score = overall_score
                match_record.match_type = match_type
                match_record.reason = reason

            matches.append(match_record)

        self.db.commit()
        matches.sort(key=lambda m: m.overall_score, reverse=True)
        return matches[:top_k]

    def _calculate_structured_scores(
        self,
        f1: Fact,
        f2: Fact,
        semantic_sim: float
    ) -> Dict[str, float]:
        """Calculates multi-dimensional compatibility scores across facts."""
        # 1. Entity Score
        e1 = (f1.entity or "").strip().lower()
        e2 = (f2.entity or "").strip().lower()
        if e1 and e2 and (e1 == e2 or e1 in e2 or e2 in e1):
            entity_score = 1.0
        elif not e1 or not e2:
            entity_score = 0.5
        else:
            entity_score = 0.0

        # 2. Attribute / Metric Score
        a1 = (f1.attribute or "").strip().lower()
        a2 = (f2.attribute or "").strip().lower()
        synonyms = [
            {"revenue", "revenue from operations", "total revenue", "net sales", "sales", "turnover"},
            {"net income", "profit after tax", "net profit", "pat"},
            {"operating income", "operating profit", "ebit", "operating margin"},
            {"ebitda", "adjusted ebitda"},
            {"headcount", "employees", "full-time employees", "workforce"}
        ]
        if a1 and a2 and (a1 == a2 or a1 in a2 or a2 in a1):
            attribute_score = 1.0
        elif any(a1 in syn and a2 in syn for syn in synonyms):
            attribute_score = 1.0
        elif not a1 or not a2:
            attribute_score = 0.5
        else:
            attribute_score = 0.1

        # 3. Time Period Compatibility
        p1 = (f1.time_period or f1.fiscal_year or "").strip().lower()
        p2 = (f2.time_period or f2.fiscal_year or "").strip().lower()
        fy1 = (f1.fiscal_year or "").strip().lower()
        fy2 = (f2.fiscal_year or "").strip().lower()
        q1 = (f1.quarter or "").strip().lower()
        q2 = (f2.quarter or "").strip().lower()

        if p1 and p2 and p1 == p2:
            time_score = 1.0
        elif fy1 and fy2 and fy1 == fy2 and (not q1 or not q2 or q1 == q2):
            time_score = 0.8
        elif fy1 and fy2 and fy1 != fy2:
            # Different fiscal years -> related concept but temporal variant
            time_score = 0.2
        elif not p1 or not p2:
            time_score = 0.5
        else:
            time_score = 0.2

        # 4. Currency Compatibility (Strict - No implicit currency conversion)
        c1 = f1.currency
        c2 = f2.currency
        if (c1 and c2 and c1 == c2) or (not c1 and not c2):
            currency_score = 1.0
        elif (c1 and not c2) or (c2 and not c1):
            currency_score = 0.7
        else:
            # Conflicting currencies (e.g. INR vs USD)
            currency_score = 0.0

        # 5. Scope & Geography
        s1 = (f1.scope or "").strip().lower()
        s2 = (f2.scope or "").strip().lower()
        scope_score = 1.0 if s1 == s2 or not s1 or not s2 else 0.4

        g1 = (f1.geography or "").strip().lower()
        g2 = (f2.geography or "").strip().lower()
        geography_score = 1.0 if g1 == g2 or not g1 or not g2 else 0.2

        d1 = (f1.definition or "").strip().lower()
        d2 = (f2.definition or "").strip().lower()
        definition_score = 1.0 if d1 == d2 or not d1 or not d2 else 0.4

        # Overall weighted score
        overall_score = (
            0.30 * semantic_sim
            + 0.25 * entity_score
            + 0.20 * attribute_score
            + 0.10 * time_score
            + 0.05 * scope_score
            + 0.05 * geography_score
            + 0.05 * currency_score
        )

        # Penalize if currencies strictly conflict
        if currency_score == 0.0 and c1 and c2:
            overall_score *= 0.65

        return {
            "semantic_similarity": round(semantic_sim, 4),
            "entity_score": round(entity_score, 4),
            "attribute_score": round(attribute_score, 4),
            "time_score": round(time_score, 4),
            "scope_score": round(scope_score, 4),
            "geography_score": round(geography_score, 4),
            "definition_score": round(definition_score, 4),
            "currency_score": round(currency_score, 4),
            "overall_score": round(overall_score, 4)
        }

    def _classify_match(
        self,
        f1: Fact,
        f2: Fact,
        scores: Dict[str, float]
    ) -> Tuple[MatchType, str]:
        """Categorizes candidate match type based on structured dimensional scores."""
        reasons = []

        # 1. Incompatible Context (Currency or Geography conflict)
        if scores["currency_score"] == 0.0 and f1.currency and f2.currency:
            reasons.append(f"Incompatible currencies ({f1.currency} vs {f2.currency})")
            return MatchType.INCOMPATIBLE_CONTEXT, "; ".join(reasons)

        if scores["geography_score"] <= 0.2:
            reasons.append(f"Different geographic scopes ({f1.geography} vs {f2.geography})")
            return MatchType.INCOMPATIBLE_CONTEXT, "; ".join(reasons)

        # 2. Temporal Variant (Same entity & attribute, but distinct time periods)
        if scores["entity_score"] >= 0.7 and scores["attribute_score"] >= 0.7 and scores["time_score"] <= 0.3:
            reasons.append(f"Same metric/entity across different time periods ({f1.time_period or f1.fiscal_year} vs {f2.time_period or f2.fiscal_year})")
            return MatchType.TEMPORAL_VARIANT, "; ".join(reasons)

        # 3. Likely Same Fact (High semantic, entity, attribute, and temporal alignment)
        if scores["entity_score"] >= 0.7 and scores["attribute_score"] >= 0.7 and scores["time_score"] >= 0.7 and scores["overall_score"] >= 0.65:
            reasons.append(f"High multi-dimensional alignment for entity '{f1.entity or f2.entity}' on '{f1.attribute or f2.attribute}' ({f1.time_period})")
            return MatchType.LIKELY_SAME_FACT, "; ".join(reasons)

        # 4. Related Fact
        if scores["overall_score"] >= 0.45 or (scores["entity_score"] >= 0.7 and scores["semantic_similarity"] >= 0.6):
            reasons.append(f"Contextually related facts with score {scores['overall_score']}")
            return MatchType.RELATED_FACT, "; ".join(reasons)

        return MatchType.LOW_CONFIDENCE, f"Low compatibility score ({scores['overall_score']})"


# Alias / backwards compatibility for existing imports
ComparisonService = CandidateMatchingService
