"""Cross-document reconciliation orchestration, deterministic comparison, and 4-way classification."""
import uuid
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.fact import Fact, FactStatus, ValueStatus
from app.models.document import Document
from app.models.comparison import (
    FactRelationship,
    RelationshipType,
    FactCandidateMatch,
    ReconciliationSession
)
from app.schemas.comparison import (
    ValueComparisonResult,
    ContextComparisonResult,
    SupportingEvidence,
    SupportingEvidenceItem,
    ReconciliationLLMResult,
    ReconciliationSummaryStats
)
from app.core.config import settings
from app.core.logging import logger
from app.services.llm.factory import get_llm_provider
from app.services.llm.prompts import FACT_COMPARISON_SYSTEM_PROMPT


class ValueComparisonEngine:
    """Deterministic numeric comparison engine."""

    @staticmethod
    def compare(
        fact_a: Fact,
        fact_b: Fact,
        match_tolerance: float = settings.MATCH_TOLERANCE
    ) -> ValueComparisonResult:
        val_a = fact_a.normalized_value
        val_b = fact_b.normalized_value

        res = ValueComparisonResult(
            source_raw=fact_a.raw_value,
            source_normalized=val_a,
            source_formatted=fact_a.normalized_value_str,
            candidate_raw=fact_b.raw_value,
            candidate_normalized=val_b,
            candidate_formatted=fact_b.normalized_value_str,
            match_tolerance=match_tolerance,
            within_tolerance=False,
            direction="INCOMPARABLE"
        )

        if val_a is None or val_b is None:
            return res

        abs_diff = abs(val_a - val_b)
        max_val = max(abs(val_a), abs(val_b))

        if val_a == val_b or max_val == 0.0:
            rel_diff = 0.0
        else:
            rel_diff = abs_diff / max_val

        pct_diff = rel_diff * 100.0
        within_tol = rel_diff <= match_tolerance

        direction = "EQUAL" if within_tol else ("INCREASE" if val_b > val_a else "DECREASE")

        res.absolute_difference = round(abs_diff, 4)
        res.relative_difference = round(rel_diff, 6)
        res.percentage_difference = round(pct_diff, 4)
        res.within_tolerance = within_tol
        res.direction = direction

        return res


class ContextComparisonEngine:
    """Deterministic context compatibility engine across 8 dimensions."""

    FINANCIAL_SYNONYMS = [
        {"revenue", "revenue from operations", "revenue from services", "total revenue", "net sales", "sales", "turnover"},
        {"net income", "profit after tax", "net profit", "pat", "profit for the period", "net earnings"},
        {"operating income", "operating profit", "ebit", "operating margin"},
        {"ebitda", "adjusted ebitda"},
        {"total assets", "assets"},
        {"headcount", "employees", "full-time employees", "workforce"}
    ]

    @classmethod
    def compare(cls, fact_a: Fact, fact_b: Fact) -> ContextComparisonResult:
        diffs: Dict[str, str] = {}

        # 1. Entity
        e1 = (fact_a.entity or "").strip().lower()
        e2 = (fact_b.entity or "").strip().lower()
        entity_match = True
        if not e1 or not e2:
            entity_match = False
            diffs["entity"] = "Ambiguous or missing entity"
        elif e1 != e2 and e1 not in e2 and e2 not in e1:
            entity_match = False
            diffs["entity"] = f"{fact_a.entity} vs {fact_b.entity}"

        # 2. Attribute
        a1 = (fact_a.attribute or "").strip().lower()
        a2 = (fact_b.attribute or "").strip().lower()
        attr_match = True
        if not a1 or not a2:
            attr_match = False
            diffs["attribute"] = "Ambiguous or missing metric"
        elif a1 != a2 and a1 not in a2 and a2 not in a1:
            if not any(a1 in syn and a2 in syn for syn in cls.FINANCIAL_SYNONYMS):
                attr_match = False
                diffs["attribute"] = f"{fact_a.attribute} vs {fact_b.attribute}"

        # 3. Time Period / Fiscal Year / Quarter
        p1 = (fact_a.time_period or "").strip().lower()
        p2 = (fact_b.time_period or "").strip().lower()
        fy1 = (fact_a.fiscal_year or "").strip().lower()
        fy2 = (fact_b.fiscal_year or "").strip().lower()
        q1 = (fact_a.quarter or "").strip().lower()
        q2 = (fact_b.quarter or "").strip().lower()

        time_match = True
        fy_match = True
        q_match = True

        if fy1 and fy2 and fy1 != fy2:
            fy_match = False
            time_match = False
            diffs["fiscal_year"] = f"{fact_a.fiscal_year} vs {fact_b.fiscal_year}"
        elif q1 and q2 and q1 != q2:
            q_match = False
            time_match = False
            diffs["quarter"] = f"{fact_a.quarter} vs {fact_b.quarter}"
        elif p1 and p2 and p1 != p2 and (not fy1 or not fy2):
            time_match = False
            diffs["time_period"] = f"{fact_a.time_period} vs {fact_b.time_period}"

        # 4. Scope (e.g. Consolidated vs Standalone)
        s1 = (fact_a.scope or "").strip().lower()
        s2 = (fact_b.scope or "").strip().lower()
        scope_match = True
        if s1 and s2 and s1 != s2:
            scope_match = False
            diffs["scope"] = f"{fact_a.scope} vs {fact_b.scope}"

        # 5. Geography
        g1 = (fact_a.geography or "").strip().lower()
        g2 = (fact_b.geography or "").strip().lower()
        geo_match = True
        if g1 and g2 and g1 != g2:
            geo_match = False
            diffs["geography"] = f"{fact_a.geography} vs {fact_b.geography}"

        # 6. Definition (e.g. GAAP vs Non-GAAP, Gross vs Net)
        d1 = (fact_a.definition or "").strip().lower()
        d2 = (fact_b.definition or "").strip().lower()
        def_match = True
        if d1 and d2 and d1 != d2:
            def_match = False
            diffs["definition"] = f"{fact_a.definition} vs {fact_b.definition}"

        # 7. Value Status (ACTUAL, ESTIMATE, FORECAST, GUIDANCE, TARGET)
        v1 = fact_a.value_status
        v2 = fact_b.value_status
        status_match = True
        if v1 and v2 and v1 != ValueStatus.UNKNOWN and v2 != ValueStatus.UNKNOWN:
            v1_str = v1.value if hasattr(v1, "value") else str(v1)
            v2_str = v2.value if hasattr(v2, "value") else str(v2)
            if v1_str != v2_str:
                status_match = False
                diffs["value_status"] = f"{v1_str} vs {v2_str}"

        # 8. Currency (Strict Isolation)
        c1 = fact_a.currency
        c2 = fact_b.currency
        curr_match = True
        if c1 and c2 and c1 != c2:
            curr_match = False
            diffs["currency"] = f"{c1} vs {c2}"

        # 9. Unit
        u1 = fact_a.unit
        u2 = fact_b.unit
        unit_match = True
        if u1 and u2 and u1 != u2:
            unit_match = False
            diffs["unit"] = f"{u1} vs {u2}"

        is_compatible = len(diffs) == 0

        return ContextComparisonResult(
            entity_match=entity_match,
            attribute_match=attr_match,
            time_match=time_match,
            fiscal_year_match=fy_match,
            quarter_match=q_match,
            scope_match=scope_match,
            geography_match=geo_match,
            definition_match=def_match,
            value_status_match=status_match,
            currency_match=curr_match,
            unit_match=unit_match,
            dimension_differences=diffs,
            is_contextually_compatible=is_compatible
        )


class ReconciliationService:
    """
    Orchestrates fact reconciliation, applying the deterministic decision hierarchy:
    1. Grounding verification
    2. Missing value detection
    3. Contextual difference identification (precedes numeric comparison)
    4. Deterministic numeric tolerance evaluation
    5. Fallback LLM reasoning for ambiguous cases
    6. Idempotent persistence
    """

    def __init__(self, db: Session):
        self.db = db
        self.llm_provider = get_llm_provider()

    def reconcile_fact_pair(
        self,
        fact_a: Fact,
        fact_b: Fact,
        similarity_score: Optional[float] = None,
        use_llm_for_ambiguous: bool = False,
        persist: bool = True
    ) -> FactRelationship:
        """
        Executes the deterministic 7-step reconciliation decision hierarchy for a pair of facts.
        """
        value_comp = ValueComparisonEngine.compare(fact_a, fact_b, match_tolerance=settings.MATCH_TOLERANCE)
        context_comp = ContextComparisonEngine.compare(fact_a, fact_b)
        supporting_evidence = self._build_supporting_evidence(fact_a, fact_b)

        relationship: RelationshipType
        confidence: float = 1.0
        rationale: str
        uncertainty_notes: Optional[str] = None
        reasoning_method: str = "DETERMINISTIC"

        # -------------------------------------------------------------
        # STEP 1: Verify Evidence Grounding
        # -------------------------------------------------------------
        if not fact_a.evidence_quote or not fact_a.evidence_quote.strip() or \
           not fact_b.evidence_quote or not fact_b.evidence_quote.strip() or \
           fact_a.status == FactStatus.FAILED or fact_b.status == FactStatus.FAILED:
            relationship = RelationshipType.UNCERTAIN
            confidence = 0.85
            missing_fact_id = fact_a.id if not fact_a.evidence_quote else fact_b.id
            rationale = f"Reconciliation uncertain: Fact {missing_fact_id} lacks verbatim evidence grounding quote in source document."
            uncertainty_notes = "Evidence grounding failure: missing or unverified evidence quote in PDF source."

        # -------------------------------------------------------------
        # STEP 2: Verify Normalized Values
        # -------------------------------------------------------------
        elif fact_a.normalized_value is None or fact_b.normalized_value is None:
            relationship = RelationshipType.UNCERTAIN
            confidence = 0.70
            missing_val_id = fact_a.id if fact_a.normalized_value is None else fact_b.id
            rationale = f"Reconciliation uncertain: Normalized numeric value unavailable for {missing_val_id} ('{fact_a.raw_value if fact_a.normalized_value is None else fact_b.raw_value}')."
            uncertainty_notes = "Cannot perform numeric reconciliation due to unparseable or missing normalized value."

        # -------------------------------------------------------------
        # STEP 3: Verify Entity & Metric Plausibility
        # -------------------------------------------------------------
        elif not context_comp.entity_match or not context_comp.attribute_match:
            if not fact_a.entity or not fact_b.entity or not fact_a.attribute or not fact_b.attribute:
                relationship = RelationshipType.UNCERTAIN
                confidence = 0.60
                rationale = "Reconciliation uncertain: Ambiguous or missing entity/metric name prevents definitive reconciliation."
                uncertainty_notes = "Entity or metric context could not be established with high confidence."
            else:
                relationship = RelationshipType.CONTEXTUALLY_DIFFERENT
                confidence = 0.95
                rationale = f"Contextually different claims: Different metrics or entities ({fact_a.entity}/{fact_a.attribute} vs {fact_b.entity}/{fact_b.attribute})."

        # -------------------------------------------------------------
        # STEP 4: Context Differences (Context PRECEDES Numerical Check)
        # -------------------------------------------------------------
        elif not context_comp.is_contextually_compatible:
            relationship = RelationshipType.CONTEXTUALLY_DIFFERENT
            confidence = 0.95
            reasons = []

            if "scope" in context_comp.dimension_differences:
                reasons.append(f"Reporting scope difference: {context_comp.dimension_differences['scope']}")
            if "fiscal_year" in context_comp.dimension_differences:
                reasons.append(f"Distinct fiscal periods: {context_comp.dimension_differences['fiscal_year']}")
            if "quarter" in context_comp.dimension_differences:
                reasons.append(f"Distinct quarters: {context_comp.dimension_differences['quarter']}")
            if "time_period" in context_comp.dimension_differences:
                reasons.append(f"Distinct time horizons: {context_comp.dimension_differences['time_period']}")
            if "value_status" in context_comp.dimension_differences:
                reasons.append(f"Reporting basis difference: {context_comp.dimension_differences['value_status']}")
            if "currency" in context_comp.dimension_differences:
                reasons.append(f"Incompatible currencies ({context_comp.dimension_differences['currency']}) without currency conversion")
            if "geography" in context_comp.dimension_differences:
                reasons.append(f"Geographic scope difference: {context_comp.dimension_differences['geography']}")
            if "definition" in context_comp.dimension_differences:
                reasons.append(f"Accounting definition difference: {context_comp.dimension_differences['definition']}")

            rationale = f"Contextually different: Values describe different contexts. {'; '.join(reasons)}."

        # -------------------------------------------------------------
        # STEP 5 & 6: Numerical Comparison on Identical Context
        # -------------------------------------------------------------
        elif value_comp.within_tolerance:
            # STEP 5: Values match within tolerance -> CORROBORATED
            relationship = RelationshipType.CORROBORATED
            confidence = 0.98
            val_str = fact_a.normalized_value_str or fact_a.raw_value
            period_str = fact_a.time_period or fact_a.fiscal_year or "the reporting period"
            rationale = (
                f"Corroborated: Both documents agree on '{fact_a.attribute}' for '{fact_a.entity}' in {period_str}. "
                f"Source reported {value_comp.source_formatted or value_comp.source_raw} and candidate reported "
                f"{value_comp.candidate_formatted or value_comp.candidate_raw} "
                f"(Relative difference: {value_comp.relative_difference:.2%}, within {value_comp.match_tolerance:.1%} tolerance)."
            )

        else:
            # STEP 6: Context is identical but values materially disagree -> CONTRADICTED
            relationship = RelationshipType.CONTRADICTED
            confidence = 0.95
            period_str = fact_a.time_period or fact_a.fiscal_year or "the reporting period"
            scope_str = fact_a.scope or "Standard"
            curr_str = fact_a.currency or fact_a.unit or "units"

            rationale = (
                f"Contradicted: Material numerical discrepancy on '{fact_a.attribute}' for '{fact_a.entity}' in {period_str}. "
                f"Source reported {value_comp.source_formatted or value_comp.source_raw} ({fact_a.normalized_value:,.2f} {curr_str}), "
                f"Candidate reported {value_comp.candidate_formatted or value_comp.candidate_raw} ({fact_b.normalized_value:,.2f} {curr_str}). "
                f"Absolute difference: {value_comp.absolute_difference:,.2f} {curr_str}, "
                f"Percentage difference: {value_comp.percentage_difference:.2f}%. "
                f"All reporting context (Scope: {scope_str}, Currency: {fact_a.currency or 'N/A'}, Period: {period_str}) is identical."
            )

        # -------------------------------------------------------------
        # Optional: LLM Assistance for Ambiguous Cases
        # -------------------------------------------------------------
        if use_llm_for_ambiguous and relationship == RelationshipType.UNCERTAIN:
            llm_res = self._run_llm_reconciliation(fact_a, fact_b)
            if llm_res:
                relationship = llm_res.relationship
                confidence = llm_res.confidence
                rationale = llm_res.rationale
                reasoning_method = "LLM_ASSISTED"
                if llm_res.uncertainty_notes:
                    uncertainty_notes = llm_res.uncertainty_notes

        # Construct and persist record
        rel_id = f"rel_{fact_a.id}_{fact_b.id}"

        diff_payload = {
            "value_diff": value_comp.model_dump(),
            "context_diff": context_comp.model_dump(),
            "dimension_differences": context_comp.dimension_differences
        }

        if not persist:
            return FactRelationship(
                id=rel_id,
                fact_a_id=fact_a.id,
                fact_b_id=fact_b.id,
                relationship=relationship,
                confidence=confidence,
                similarity_score=similarity_score,
                rationale=rationale,
                value_comparison=value_comp.model_dump(),
                context_comparison=context_comp.model_dump(),
                supporting_evidence=supporting_evidence.model_dump(),
                uncertainty_notes=uncertainty_notes,
                reasoning_method=reasoning_method,
                difference_analysis=diff_payload
            )

        existing_rel = self.db.query(FactRelationship).filter(FactRelationship.id == rel_id).first()

        if not existing_rel:
            existing_rel = FactRelationship(
                id=rel_id,
                fact_a_id=fact_a.id,
                fact_b_id=fact_b.id,
                relationship=relationship,
                confidence=confidence,
                similarity_score=similarity_score,
                rationale=rationale,
                value_comparison=value_comp.model_dump(),
                context_comparison=context_comp.model_dump(),
                supporting_evidence=supporting_evidence.model_dump(),
                uncertainty_notes=uncertainty_notes,
                reasoning_method=reasoning_method,
                difference_analysis=diff_payload
            )
            self.db.add(existing_rel)
        else:
            existing_rel.relationship = relationship
            existing_rel.confidence = confidence
            existing_rel.similarity_score = similarity_score
            existing_rel.rationale = rationale
            existing_rel.value_comparison = value_comp.model_dump()
            existing_rel.context_comparison = context_comp.model_dump()
            existing_rel.supporting_evidence = supporting_evidence.model_dump()
            existing_rel.uncertainty_notes = uncertainty_notes
            existing_rel.reasoning_method = reasoning_method
            existing_rel.difference_analysis = diff_payload

        self.db.commit()
        self.db.refresh(existing_rel)
        return existing_rel

    def _build_supporting_evidence(self, fact_a: Fact, fact_b: Fact) -> SupportingEvidence:
        doc_a = self.db.query(Document).filter(Document.id == fact_a.document_id).first()
        doc_b = self.db.query(Document).filter(Document.id == fact_b.document_id).first()

        item_a = SupportingEvidenceItem(
            fact_id=fact_a.id,
            document_id=fact_a.document_id,
            document_filename=doc_a.filename if doc_a else None,
            page_number=fact_a.page_number,
            evidence_quote=fact_a.evidence_quote or "",
            statement=fact_a.statement
        )
        item_b = SupportingEvidenceItem(
            fact_id=fact_b.id,
            document_id=fact_b.document_id,
            document_filename=doc_b.filename if doc_b else None,
            page_number=fact_b.page_number,
            evidence_quote=fact_b.evidence_quote or "",
            statement=fact_b.statement
        )
        return SupportingEvidence(source_evidence=item_a, candidate_evidence=item_b)

    def _run_llm_reconciliation(self, fact_a: Fact, fact_b: Fact) -> Optional[ReconciliationLLMResult]:
        """Calls the LLM provider with structured schema validation for ambiguous cases."""
        prompt = f"""
Compare the following two extracted facts from different documents:

FACT A:
Entity: {fact_a.entity}
Metric: {fact_a.attribute}
Raw Value: {fact_a.raw_value}
Normalized: {fact_a.normalized_value_str} ({fact_a.normalized_value})
Time Period: {fact_a.time_period} (FY: {fact_a.fiscal_year}, Quarter: {fact_a.quarter})
Scope: {fact_a.scope}
Definition: {fact_a.definition}
Evidence: "{fact_a.evidence_quote}"

FACT B:
Entity: {fact_b.entity}
Metric: {fact_b.attribute}
Raw Value: {fact_b.raw_value}
Normalized: {fact_b.normalized_value_str} ({fact_b.normalized_value})
Time Period: {fact_b.time_period} (FY: {fact_b.fiscal_year}, Quarter: {fact_b.quarter})
Scope: {fact_b.scope}
Definition: {fact_b.definition}
Evidence: "{fact_b.evidence_quote}"

Classify into EXACTLY ONE of: CORROBORATED, CONTRADICTED, CONTEXTUALLY_DIFFERENT, UNCERTAIN.
"""
        try:
            import asyncio
            # If running in sync context, use asyncio.run or check event loop
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as pool:
                        res = pool.submit(asyncio.run, self.llm_provider.generate_structured(prompt, ReconciliationLLMResult, FACT_COMPARISON_SYSTEM_PROMPT)).result()
                        return res
                else:
                    return loop.run_until_complete(self.llm_provider.generate_structured(prompt, ReconciliationLLMResult, FACT_COMPARISON_SYSTEM_PROMPT))
            except Exception:
                return asyncio.run(self.llm_provider.generate_structured(prompt, ReconciliationLLMResult, FACT_COMPARISON_SYSTEM_PROMPT))
        except Exception as e:
            logger.warning(f"LLM reconciliation fallback error: {e}")
            return None

    def reconcile_candidate_matches(
        self,
        min_candidate_score: float = 0.30,
        document_ids: Optional[List[str]] = None,
        use_llm_for_ambiguous: bool = False
    ) -> List[FactRelationship]:
        """
        Iterates over candidate matches from the Phase 2 candidate matching layer
        and computes deterministic 4-way reconciliations.
        """
        query = self.db.query(FactCandidateMatch).filter(FactCandidateMatch.overall_score >= min_candidate_score)
        if document_ids:
            query = query.join(Fact, FactCandidateMatch.source_fact_id == Fact.id).filter(Fact.document_id.in_(document_ids))

        candidate_matches = query.all()
        reconciled: List[FactRelationship] = []

        for cm in candidate_matches:
            fact_a = self.db.query(Fact).filter(Fact.id == cm.source_fact_id).first()
            fact_b = self.db.query(Fact).filter(Fact.id == cm.candidate_fact_id).first()

            if not fact_a or not fact_b or fact_a.id == fact_b.id:
                continue

            rel = self.reconcile_fact_pair(
                fact_a=fact_a,
                fact_b=fact_b,
                similarity_score=cm.overall_score,
                use_llm_for_ambiguous=use_llm_for_ambiguous
            )
            reconciled.append(rel)

        return reconciled

    def reconcile_fact(
        self,
        fact_id: str,
        top_k: int = 10,
        min_score: float = 0.30,
        use_llm_for_ambiguous: bool = False
    ) -> List[FactRelationship]:
        """Runs candidate matching and reconciliation for a single target fact."""
        fact = self.db.query(Fact).filter(Fact.id == fact_id).first()
        if not fact:
            return []

        from app.services.comparison_service import CandidateMatchingService
        matcher = CandidateMatchingService(self.db)
        candidates = matcher.find_and_score_candidates_for_fact(fact, top_k=top_k, min_score_threshold=min_score)

        relationships = []
        for cand in candidates:
            cand_fact = self.db.query(Fact).filter(Fact.id == cand.candidate_fact_id).first()
            if not cand_fact or cand_fact.id == fact.id:
                continue

            rel = self.reconcile_fact_pair(
                fact_a=fact,
                fact_b=cand_fact,
                similarity_score=cand.overall_score,
                use_llm_for_ambiguous=use_llm_for_ambiguous
            )
            relationships.append(rel)

        return relationships

    async def reconcile_documents(
        self,
        document_ids: List[str],
        title: Optional[str] = None,
        similarity_threshold: float = 0.30
    ) -> ReconciliationSession:
        """
        Executes cross-document reconciliation across multiple documents,
        clusters candidate pairs, assigns 4-way classifications, and records a ReconciliationSession.
        """
        session_id = f"session_{uuid.uuid4().hex[:12]}"
        relationships = self.reconcile_candidate_matches(
            min_candidate_score=similarity_threshold,
            document_ids=document_ids
        )

        counts = {
            "corroborated": 0,
            "contradicted": 0,
            "contextually_different": 0,
            "uncertain": 0
        }

        for rel in relationships:
            rel.session_id = session_id
            if rel.relationship == RelationshipType.CORROBORATED:
                counts["corroborated"] += 1
            elif rel.relationship == RelationshipType.CONTRADICTED:
                counts["contradicted"] += 1
            elif rel.relationship == RelationshipType.CONTEXTUALLY_DIFFERENT:
                counts["contextually_different"] += 1
            elif rel.relationship == RelationshipType.UNCERTAIN:
                counts["uncertain"] += 1

        summary = {
            "total_comparisons": len(relationships),
            "corroborated_count": counts["corroborated"],
            "contradicted_count": counts["contradicted"],
            "contextually_different_count": counts["contextually_different"],
            "uncertain_count": counts["uncertain"]
        }

        session = ReconciliationSession(
            id=session_id,
            title=title or f"Cross-Document Reconciliation ({len(document_ids)} Documents)",
            description=f"Automated 4-way reconciliation evaluated across {len(document_ids)} documents.",
            document_ids=document_ids,
            summary_stats=summary
        )

        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session


def build_verdict_checklist(
    relationship: RelationshipType,
    fact_a: Optional[Fact],
    fact_b: Optional[Fact],
    val_comp: Optional[Any],
    ctx_comp: Optional[Any],
    uncertainty_notes: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Generates structured deterministic checklist items explaining why a verdict was reached."""
    checklist = []
    
    val_dict = val_comp if isinstance(val_comp, dict) else (val_comp.model_dump() if hasattr(val_comp, 'model_dump') else {})
    ctx_dict = ctx_comp if isinstance(ctx_comp, dict) else (ctx_comp.model_dump() if hasattr(ctx_comp, 'model_dump') else {})

    if relationship == RelationshipType.CORROBORATED:
        checklist.append({"label": "Same entity", "status": "PASS", "detail": getattr(fact_a, 'entity', None) or "Identical"})
        checklist.append({"label": "Same metric", "status": "PASS", "detail": getattr(fact_a, 'attribute', None) or "Identical"})
        period = getattr(fact_a, 'fiscal_year', None) or getattr(fact_a, 'time_period', None) or "Identical"
        checklist.append({"label": "Same fiscal period", "status": "PASS", "detail": period})
        scope = getattr(fact_a, 'scope', None) or "Consolidated"
        checklist.append({"label": "Same reporting scope", "status": "PASS", "detail": scope})
        curr = getattr(fact_a, 'currency', None) or getattr(fact_a, 'unit', None) or "Compatible"
        checklist.append({"label": "Compatible currency/unit", "status": "PASS", "detail": curr})
        
        pct = val_dict.get("percentage_difference", 0.0) or 0.0
        tol = (val_dict.get("match_tolerance", 0.01) or 0.01) * 100.0
        src_fmt = val_dict.get("source_formatted") or val_dict.get("source_raw") or "Normalized"
        cand_fmt = val_dict.get("candidate_formatted") or val_dict.get("candidate_raw") or "Normalized"
        
        checklist.append({"label": "Values normalized", "status": "PASS", "detail": f"{src_fmt} ≈ {cand_fmt}"})
        checklist.append({"label": f"Difference: {pct:.2f}%", "status": "PASS", "detail": f"≤ {tol:.2f}% allowed tolerance"})

    elif relationship == RelationshipType.CONTRADICTED:
        checklist.append({"label": "Same entity", "status": "PASS", "detail": getattr(fact_a, 'entity', None) or "Identical"})
        checklist.append({"label": "Same metric", "status": "PASS", "detail": getattr(fact_a, 'attribute', None) or "Identical"})
        period = getattr(fact_a, 'fiscal_year', None) or getattr(fact_a, 'time_period', None) or "Identical"
        checklist.append({"label": "Same period", "status": "PASS", "detail": period})
        scope = getattr(fact_a, 'scope', None) or "Consolidated"
        checklist.append({"label": "Same scope", "status": "PASS", "detail": scope})
        curr = getattr(fact_a, 'currency', None) or getattr(fact_a, 'unit', None) or "Compatible"
        checklist.append({"label": "Compatible units", "status": "PASS", "detail": curr})
        
        pct = val_dict.get("percentage_difference", 0.0) or 0.0
        tol = (val_dict.get("match_tolerance", 0.01) or 0.01) * 100.0
        src_val = val_dict.get("source_formatted") or val_dict.get("source_raw") or "Val A"
        cand_val = val_dict.get("candidate_formatted") or val_dict.get("candidate_raw") or "Val B"
        
        checklist.append({
            "label": "Material numerical disagreement",
            "status": "WARN",
            "detail": f"Fact A: {src_val} | Fact B: {cand_val} (Delta: {pct:.2f}%, Tolerance: {tol:.2f}%)"
        })

    elif relationship == RelationshipType.CONTEXTUALLY_DIFFERENT:
        attr_a = getattr(fact_a, 'attribute', '') or ''
        attr_b = getattr(fact_b, 'attribute', '') or ''
        checklist.append({"label": "Same / related metric", "status": "PASS", "detail": f"{attr_a} & {attr_b}" if attr_a != attr_b else attr_a})
        
        diffs = ctx_dict.get("dimension_differences", {})
        if diffs:
            for dim, desc in diffs.items():
                checklist.append({"label": f"Context mismatch: {dim.replace('_', ' ').title()}", "status": "WARN", "detail": desc})
        else:
            checklist.append({"label": "Context mismatch", "status": "WARN", "detail": "Reporting scope, period, currency, or basis divergence"})
        
        checklist.append({"label": "Values not directly comparable", "status": "INFO", "detail": "Contextual divergence strictly precludes numerical contradiction"})

    elif relationship == RelationshipType.UNCERTAIN:
        checklist.append({"label": "Grounding / numeric verification", "status": "WARN", "detail": "Insufficient verified grounding or unparseable metric"})
        if uncertainty_notes:
            checklist.append({"label": "Uncertainty preserved", "status": "WARN", "detail": uncertainty_notes})
        else:
            checklist.append({"label": "Preserved without fabricating conclusions", "status": "INFO", "detail": "Ambiguity strictly flagged for audit"})

    return checklist

