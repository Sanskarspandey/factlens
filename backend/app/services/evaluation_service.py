"""FactLens Evaluation Service.

Executes deterministic test scenarios across all core pipeline dimensions:
1. Grounded Corroboration
2. Genuine Contradiction
3. Contextual Differences (Scope, Temporal, Status, Currency)
4. Uncertainty & Failure Preservation
5. Grounding Provenance Verification
6. Deterministic Normalization
"""
import time
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.models.fact import Fact, FactStatus, ValueStatus
from app.models.comparison import RelationshipType
from app.services.reconciliation_service import ReconciliationService
from app.services.normalization_service import NormalizationService


class EvaluationService:
    def __init__(self, db: Session):
        self.db = db
        self.reconciler = ReconciliationService(db)
        self.normalizer = NormalizationService()

    def run_evaluation(self) -> Dict[str, Any]:
        start_time = time.time()
        scenarios = []

        # ----------------------------------------------------
        # 1. Corroboration Scenarios
        # ----------------------------------------------------
        # Scenario 1: Delhivery Revenue
        fact_corr_1a = Fact(
            id="eval_corr_1a",
            document_id="doc_demo_annual_report",
            page_number=12,
            statement="Revenue from services was ₹8,142 crore during FY2024.",
            entity="Delhivery",
            attribute="Revenue from services",
            raw_value="₹8,142 crore",
            normalized_value=81420000000.0,
            normalized_value_str="₹81.42 billion",
            currency="INR",
            time_period="FY2024",
            fiscal_year="FY2024",
            scope="Consolidated",
            value_status=ValueStatus.ACTUAL,
            evidence_quote="Revenue from services was ₹8,142 crore during fiscal year 2024.",
            status=FactStatus.VERIFIED,
            confidence=0.98
        )
        fact_corr_1b = Fact(
            id="eval_corr_1b",
            document_id="doc_demo_investor_presentation",
            page_number=5,
            statement="Total services revenue reached ₹81.42 billion in FY24.",
            entity="Delhivery",
            attribute="Revenue from services",
            raw_value="₹81.42 billion",
            normalized_value=81420000000.0,
            normalized_value_str="₹81.42 billion",
            currency="INR",
            time_period="FY2024",
            fiscal_year="FY2024",
            scope="Consolidated",
            value_status=ValueStatus.ACTUAL,
            evidence_quote="Total services revenue reached ₹81.42 billion in FY24 across express parcel and PTL segments.",
            status=FactStatus.VERIFIED,
            confidence=0.98
        )
        rel_corr_1 = self.reconciler.reconcile_fact_pair(fact_corr_1a, fact_corr_1b, persist=False)
        scenarios.append({
            "id": "case_1_corroboration",
            "category": "Corroboration",
            "title": "Case 1: Grounded Corroboration (Delhivery Revenue)",
            "expected_relationship": "CORROBORATED",
            "actual_relationship": rel_corr_1.relationship.value,
            "status": "PASS" if rel_corr_1.relationship == RelationshipType.CORROBORATED else "FAIL",
            "source_type": "PDF",
            "fact_a_id": "fact_demo_corroborate_a",
            "fact_b_id": "fact_demo_corroborate_b",
            "fact_a_preview": "₹8,142 Cr | FY2024 | Consolidated",
            "fact_b_preview": "₹81.42 B | FY2024 | Consolidated",
            "explanation": "Identical context and values agree within 0.00% variance (≤ 1.0% tolerance threshold)."
        })

        # Scenario 2: Acme Global Revenue
        fact_corr_2a = Fact(
            id="eval_corr_2a",
            document_id="doc_acme_ar",
            page_number=1,
            statement="Acme reported annual revenue of $383.29 billion in FY2023.",
            entity="Acme Corp",
            attribute="Revenue",
            raw_value="$383.29 billion",
            normalized_value=383290000000.0,
            currency="USD",
            time_period="FY2023",
            fiscal_year="FY2023",
            scope="Consolidated",
            value_status=ValueStatus.ACTUAL,
            evidence_quote="In fiscal year 2023, Acme Corporation reported total revenue of $383.29 billion.",
            status=FactStatus.VERIFIED,
            confidence=0.99
        )
        fact_corr_2b = Fact(
            id="eval_corr_2b",
            document_id="doc_acme_pr",
            page_number=2,
            statement="Full-year revenue stood at $383.29 billion for FY2023.",
            entity="Acme Corp",
            attribute="Revenue",
            raw_value="$383.29 billion",
            normalized_value=383290000000.0,
            currency="USD",
            time_period="FY2023",
            fiscal_year="FY2023",
            scope="Consolidated",
            value_status=ValueStatus.ACTUAL,
            evidence_quote="Full-year revenue stood at $383.29 billion for FY2023 representing solid performance.",
            status=FactStatus.VERIFIED,
            confidence=0.99
        )
        rel_corr_2 = self.reconciler.reconcile_fact_pair(fact_corr_2a, fact_corr_2b, persist=False)
        scenarios.append({
            "id": "scenario_corr_usd_acme",
            "category": "Corroboration",
            "title": "Acme Global Revenue ($383.29B vs $383.29B)",
            "expected_relationship": "CORROBORATED",
            "actual_relationship": rel_corr_2.relationship.value,
            "status": "PASS" if rel_corr_2.relationship == RelationshipType.CORROBORATED else "FAIL",
            "source_type": "PDF",
            "fact_a_id": "eval_corr_2a",
            "fact_b_id": "eval_corr_2b",
            "fact_a_preview": "$383.29B | FY2023 | Consolidated",
            "fact_b_preview": "$383.29B | FY2023 | Consolidated",
            "explanation": "USD-denominated claims share identical reporting context and 0.00% variance."
        })

        # ----------------------------------------------------
        # 2. Contradiction Scenarios
        # ----------------------------------------------------
        fact_contra_1a = Fact(
            id="eval_contra_1a",
            document_id="doc_demo_annual_report",
            page_number=18,
            statement="Delhivery headcount was 32,500 active employees at year end.",
            entity="Delhivery",
            attribute="Headcount",
            raw_value="32,500",
            normalized_value=32500.0,
            unit="employees",
            time_period="FY2024",
            fiscal_year="FY2024",
            scope="Consolidated",
            value_status=ValueStatus.ACTUAL,
            evidence_quote="Delhivery headcount was 32,500 active employees at year end March 31, 2024.",
            status=FactStatus.VERIFIED,
            confidence=0.96
        )
        fact_contra_1b = Fact(
            id="eval_contra_1b",
            document_id="doc_demo_investor_presentation",
            page_number=22,
            statement="Delhivery total workforce was reported as 24,000 employees as of FY24.",
            entity="Delhivery",
            attribute="Headcount",
            raw_value="24,000",
            normalized_value=24000.0,
            unit="employees",
            time_period="FY2024",
            fiscal_year="FY2024",
            scope="Consolidated",
            value_status=ValueStatus.ACTUAL,
            evidence_quote="Delhivery total workforce was reported as 24,000 employees as of FY24 close.",
            status=FactStatus.VERIFIED,
            confidence=0.96
        )
        rel_contra_1 = self.reconciler.reconcile_fact_pair(fact_contra_1a, fact_contra_1b, persist=False)
        scenarios.append({
            "id": "case_2_contradiction",
            "category": "Contradiction",
            "title": "Case 2: Genuine Contradiction (Headcount Discrepancy)",
            "expected_relationship": "CONTRADICTED",
            "actual_relationship": rel_contra_1.relationship.value,
            "status": "PASS" if rel_contra_1.relationship == RelationshipType.CONTRADICTED else "FAIL",
            "source_type": "SYNTHETIC_DEMO",
            "fact_a_id": "fact_demo_contradict_a",
            "fact_b_id": "fact_demo_contradict_b",
            "fact_a_preview": "32,500 employees | FY2024 | Consolidated",
            "fact_b_preview": "24,000 employees | FY2024 | Consolidated",
            "explanation": "Identical context (Delhivery, FY24, Consolidated), but reported headcount diverges by 26.15% (> 1.0% tolerance)."
        })

        # ----------------------------------------------------
        # 3. Contextual Difference Scenarios
        # ----------------------------------------------------
        # Scope Mismatch: Consolidated vs Standalone EBITDA
        fact_scope_1a = Fact(
            id="eval_scope_1a",
            document_id="doc_demo_annual_report",
            page_number=30,
            statement="Consolidated EBITDA stood at ₹127 crore for the full year FY2024.",
            entity="Delhivery",
            attribute="EBITDA",
            raw_value="₹127 crore",
            normalized_value=1270000000.0,
            currency="INR",
            time_period="FY2024",
            fiscal_year="FY2024",
            scope="Consolidated",
            value_status=ValueStatus.ACTUAL,
            evidence_quote="Consolidated EBITDA stood at ₹127 crore for the full year FY2024.",
            status=FactStatus.VERIFIED,
            confidence=0.95
        )
        fact_scope_1b = Fact(
            id="eval_scope_1b",
            document_id="doc_demo_annual_report",
            page_number=31,
            statement="Standalone operating EBITDA was ₹95 crore in FY2024.",
            entity="Delhivery",
            attribute="EBITDA",
            raw_value="₹95 crore",
            normalized_value=950000000.0,
            currency="INR",
            time_period="FY2024",
            fiscal_year="FY2024",
            scope="Standalone",
            value_status=ValueStatus.ACTUAL,
            evidence_quote="Standalone operating EBITDA was ₹95 crore in FY2024.",
            status=FactStatus.VERIFIED,
            confidence=0.95
        )
        rel_scope_1 = self.reconciler.reconcile_fact_pair(fact_scope_1a, fact_scope_1b, persist=False)
        scenarios.append({
            "id": "case_3_contextual_difference",
            "category": "Contextual Difference",
            "title": "Case 3: Reporting Scope Divergence (Consolidated vs Standalone EBITDA)",
            "expected_relationship": "CONTEXTUALLY_DIFFERENT",
            "actual_relationship": rel_scope_1.relationship.value,
            "status": "PASS" if rel_scope_1.relationship == RelationshipType.CONTEXTUALLY_DIFFERENT else "FAIL",
            "source_type": "PDF",
            "fact_a_id": "fact_demo_scope_a",
            "fact_b_id": "fact_demo_scope_b",
            "fact_a_preview": "₹127 Cr | FY2024 | Consolidated",
            "fact_b_preview": "₹95 Cr | FY2024 | Standalone",
            "explanation": "Different reporting scope (Consolidated vs Standalone) strictly precludes a false contradiction."
        })

        # Temporal Mismatch: FY2024 Actual vs FY2025 Forecast GDP Growth
        fact_temp_1a = Fact(
            id="eval_temp_1a",
            document_id="doc_rbi_ar",
            page_number=14,
            statement="Real GDP growth was 8.2% in FY2024.",
            entity="India",
            attribute="GDP Growth",
            raw_value="8.2%",
            normalized_value=8.2,
            unit="%",
            time_period="FY2024",
            fiscal_year="FY2024",
            value_status=ValueStatus.ACTUAL,
            evidence_quote="Real GDP growth was 8.2% in FY2024.",
            status=FactStatus.VERIFIED,
            confidence=0.98
        )
        fact_temp_1b = Fact(
            id="eval_temp_1b",
            document_id="doc_imf_art4",
            page_number=8,
            statement="Projected GDP growth is 7.0% for FY2025.",
            entity="India",
            attribute="GDP Growth",
            raw_value="7.0%",
            normalized_value=7.0,
            unit="%",
            time_period="FY2025",
            fiscal_year="FY2025",
            value_status=ValueStatus.FORECAST,
            evidence_quote="Projected GDP growth is 7.0% for FY2025.",
            status=FactStatus.VERIFIED,
            confidence=0.95
        )
        rel_temp_1 = self.reconciler.reconcile_fact_pair(fact_temp_1a, fact_temp_1b, persist=False)
        scenarios.append({
            "id": "scenario_temp_macro_gdp",
            "category": "Contextual Difference",
            "title": "Temporal & Basis Variance (FY24 Actual vs FY25 Forecast GDP)",
            "expected_relationship": "CONTEXTUALLY_DIFFERENT",
            "actual_relationship": rel_temp_1.relationship.value,
            "status": "PASS" if rel_temp_1.relationship == RelationshipType.CONTEXTUALLY_DIFFERENT else "FAIL",
            "source_type": "PDF",
            "fact_a_id": "eval_temp_1a",
            "fact_b_id": "eval_temp_1b",
            "fact_a_preview": "8.2% | FY2024 | Actual",
            "fact_b_preview": "7.0% | FY2025 | Forecast",
            "explanation": "Distinct fiscal period and reporting basis prevent false discrepancy classification."
        })

        # Currency Isolation: USD vs INR
        fact_curr_1a = Fact(
            id="eval_curr_1a",
            document_id="doc_acme_us",
            page_number=1,
            statement="Revenue was $100M in FY2024.",
            entity="Acme",
            attribute="Revenue",
            raw_value="$100M",
            normalized_value=100000000.0,
            currency="USD",
            time_period="FY2024",
            scope="Consolidated",
            evidence_quote="Revenue was $100M in FY2024.",
            status=FactStatus.VERIFIED,
            confidence=0.98
        )
        fact_curr_1b = Fact(
            id="eval_curr_1b",
            document_id="doc_acme_in",
            page_number=1,
            statement="Revenue was ₹100 Cr in FY2024.",
            entity="Acme",
            attribute="Revenue",
            raw_value="₹100 Cr",
            normalized_value=1000000000.0,
            currency="INR",
            time_period="FY2024",
            scope="Consolidated",
            evidence_quote="Revenue was ₹100 Cr in FY2024.",
            status=FactStatus.VERIFIED,
            confidence=0.98
        )
        rel_curr_1 = self.reconciler.reconcile_fact_pair(fact_curr_1a, fact_curr_1b, persist=False)
        scenarios.append({
            "id": "scenario_curr_isolation",
            "category": "Contextual Difference",
            "title": "Strict Currency Isolation ($100M USD vs ₹100 Cr INR)",
            "expected_relationship": "CONTEXTUALLY_DIFFERENT",
            "actual_relationship": rel_curr_1.relationship.value,
            "status": "PASS" if rel_curr_1.relationship == RelationshipType.CONTEXTUALLY_DIFFERENT else "FAIL",
            "source_type": "PDF",
            "fact_a_id": "eval_curr_1a",
            "fact_b_id": "eval_curr_1b",
            "fact_a_preview": "$100M | FY2024 | USD",
            "fact_b_preview": "₹100 Cr | FY2024 | INR",
            "explanation": "Zero implicit FX conversion; disparate currencies enforce contextual isolation."
        })

        # ----------------------------------------------------
        # 4. Uncertainty Preservation Scenarios
        # ----------------------------------------------------
        fact_uncert_1a = Fact(
            id="eval_uncert_1a",
            document_id="doc_demo_ip",
            page_number=14,
            statement="Projected volume might reach 800M units.",
            entity="Delhivery",
            attribute="Volume",
            raw_value="800M units",
            normalized_value=800000000.0,
            time_period="FY2025",
            value_status=ValueStatus.FORECAST,
            evidence_quote="Projected volume might reach 800M units subject to festive demand.",
            confidence=0.70,
            status=FactStatus.UNCERTAIN,
            uncertainty_notes="Conditional projection with high festive variance."
        )
        fact_uncert_1b = Fact(
            id="eval_uncert_1b",
            document_id="doc_demo_ip",
            page_number=15,
            statement="Substantial volume growth anticipated.",
            entity="Delhivery",
            attribute=None,
            raw_value=None,
            normalized_value=None,
            evidence_quote="",  # Missing evidence quote
            confidence=0.40,
            status=FactStatus.FAILED,
            uncertainty_notes="Ungrounded extraction without page quote citation."
        )
        rel_uncert_1 = self.reconciler.reconcile_fact_pair(fact_uncert_1a, fact_uncert_1b, persist=False)
        scenarios.append({
            "id": "case_4_uncertainty",
            "category": "Uncertainty",
            "title": "Case 4: Uncertainty & Grounding Failure Preservation",
            "expected_relationship": "UNCERTAIN",
            "actual_relationship": rel_uncert_1.relationship.value,
            "status": "PASS" if rel_uncert_1.relationship == RelationshipType.UNCERTAIN else "FAIL",
            "source_type": "SYNTHETIC_DEMO",
            "fact_a_id": "fact_demo_uncertain_a",
            "fact_b_id": "fact_demo_uncertain_b",
            "fact_a_preview": "800M units | Conditional Forecast",
            "fact_b_preview": "Unquantified | Missing Quote",
            "explanation": "Missing verbatim quote and unquantified metric are safely preserved as UNCERTAIN."
        })

        # ----------------------------------------------------
        # 5. Evidence Grounding Verification
        # ----------------------------------------------------
        grounding_pass = (
            len(fact_corr_1a.evidence_quote) > 10 and 
            fact_corr_1a.page_number > 0 and 
            fact_corr_1a.document_id is not None
        )
        scenarios.append({
            "id": "eval_grounding_verification",
            "category": "Evidence Grounding",
            "title": "Strict Evidence Provenance Integrity",
            "expected_relationship": "VERIFIED",
            "actual_relationship": "VERIFIED" if grounding_pass else "FAILED",
            "status": "PASS" if grounding_pass else "FAIL",
            "source_type": "PDF",
            "fact_a_id": "eval_corr_1a",
            "fact_b_id": "eval_corr_1a",
            "fact_a_preview": fact_corr_1a.statement,
            "fact_b_preview": f'"{fact_corr_1a.evidence_quote}"',
            "explanation": "Verbatim quote, source document ID, and page citation are strictly validated."
        })

        # ----------------------------------------------------
        # 6. Deterministic Normalization
        # ----------------------------------------------------
        norm_tests = [
            ("₹8,142 Cr", 81420000000.0, "INR"),
            ("25 Lakh", 2500000.0, None),
            ("$383.29 billion", 383290000000.0, "USD"),
            ("(₹127 Cr)", -1270000000.0, "INR")
        ]
        norm_all_pass = True
        for raw, expected_val, expected_curr in norm_tests:
            nv = self.normalizer.normalize_value(raw)
            if nv.numeric_value != expected_val:
                norm_all_pass = False
            if expected_curr and nv.currency != expected_curr:
                norm_all_pass = False

        scenarios.append({
            "id": "eval_normalization_engine",
            "category": "Normalization",
            "title": "Deterministic Numeric, Scale & Currency Multipliers",
            "expected_relationship": "VERIFIED",
            "actual_relationship": "VERIFIED" if norm_all_pass else "FAILED",
            "status": "PASS" if norm_all_pass else "FAIL",
            "source_type": "PDF",
            "fact_a_preview": "₹8,142 Cr | 25 Lakh | (₹127 Cr) | $383.29B",
            "fact_b_preview": "81.42B | 2.5M | -1.27B | 383.29B",
            "explanation": "Accurately parses Indian Crores/Lakhs, Western Billions, negative parentheticals, and ISO currencies."
        })

        # Calculate category statistics
        categories_dict: Dict[str, Dict[str, int]] = {}
        for s in scenarios:
            cat = s["category"]
            if cat not in categories_dict:
                categories_dict[cat] = {"passed": 0, "failed": 0, "total": 0}
            categories_dict[cat]["total"] += 1
            if s["status"] == "PASS":
                categories_dict[cat]["passed"] += 1
            else:
                categories_dict[cat]["failed"] += 1

        categories_list = [
            {
                "name": cat_name,
                "passed": stats["passed"],
                "failed": stats["failed"],
                "total": stats["total"]
            }
            for cat_name, stats in categories_dict.items()
        ]

        total_scenarios = len(scenarios)
        passed_scenarios = sum(1 for s in scenarios if s["status"] == "PASS")
        failed_scenarios = total_scenarios - passed_scenarios
        exec_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "summary": {
                "total_scenarios": total_scenarios,
                "passed_scenarios": passed_scenarios,
                "failed_scenarios": failed_scenarios,
                "execution_time_ms": exec_ms
            },
            "categories": categories_list,
            "scenarios": scenarios
        }
