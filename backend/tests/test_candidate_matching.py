"""Tests for Phase 2: Semantic embedding, ChromaDB vector indexing, and structured candidate matching."""
import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from app.models.fact import Fact, FactStatus, ValueStatus
from app.models.document import Document, DocumentStatus
from app.models.comparison import FactCandidateMatch, MatchType
from app.services.vector.embeddings import SentenceTransformerEmbeddingProvider, build_fact_semantic_representation
from app.services.vector.chroma_store import ChromaVectorStore
from app.services.comparison_service import CandidateMatchingService


@pytest.fixture
def mock_embedding_provider():
    return SentenceTransformerEmbeddingProvider()


def test_embedding_generation_and_semantic_text(mock_embedding_provider):
    fact = Fact(
        id="fact_test_emb",
        document_id="doc_1",
        page_number=1,
        statement="Delhivery reported revenue from operations of ₹8,142 crore in FY2024.",
        entity="Delhivery",
        attribute="Revenue from operations",
        raw_value="₹8,142 crore",
        normalized_value=81420000000.0,
        normalized_value_str="₹81.42 billion",
        unit="INR",
        currency="INR",
        time_period="FY2024",
        fiscal_year="FY2024",
        scope="Consolidated",
        evidence_quote="Delhivery reported revenue from operations of ₹8,142 crore in FY2024.",
        confidence=0.98,
        status=FactStatus.EXTRACTED
    )

    sem_text = build_fact_semantic_representation(fact)
    assert "Entity: Delhivery" in sem_text
    assert "Metric: Revenue from operations" in sem_text
    assert "Period: FY2024" in sem_text
    assert "Value: ₹81.42 billion" in sem_text

    emb = mock_embedding_provider.encode_text(sem_text)
    assert isinstance(emb, list)
    assert len(emb) == mock_embedding_provider.get_dimension()


def test_vector_indexing_and_deduplication():
    vstore = ChromaVectorStore()
    
    item1 = {
        "fact_id": "f_1",
        "embedding": [0.1] * 384,
        "metadata": {"entity": "Acme", "attribute": "Revenue", "document_id": "doc_1"},
        "document": "Acme Revenue"
    }

    # First add
    vstore.add_facts([item1])
    # Repeated add with same ID (upsert) must not crash or duplicate uncontrollably
    vstore.add_facts([item1])

    res = vstore.query_similar_facts([0.1] * 384, n_results=5)
    assert len(res) >= 1
    assert res[0]["fact_id"] == "f_1"


def test_candidate_matching_likely_same_fact(db_session: Session):
    matcher = CandidateMatchingService(db_session)

    # Fact A: ₹100 crore in FY2024
    fact_a = Fact(
        id="fact_same_a",
        document_id="doc_1",
        page_number=1,
        statement="Company X achieved total revenue of ₹100 crore in FY2024.",
        entity="Company X",
        attribute="Revenue",
        raw_value="₹100 crore",
        normalized_value=1000000000.0,
        normalized_value_str="₹1.00 billion",
        unit="INR",
        currency="INR",
        time_period="FY2024",
        fiscal_year="FY2024",
        evidence_quote="Company X achieved total revenue of ₹100 crore in FY2024.",
        status=FactStatus.EXTRACTED
    )

    # Fact B: ₹1 billion in FY2024 (Equivalent scale representation)
    fact_b = Fact(
        id="fact_same_b",
        document_id="doc_2",
        page_number=5,
        statement="Company X reported ₹1 billion in sales for fiscal year 2024.",
        entity="Company X",
        attribute="Revenue",
        raw_value="₹1 billion",
        normalized_value=1000000000.0,
        normalized_value_str="₹1.00 billion",
        unit="INR",
        currency="INR",
        time_period="FY2024",
        fiscal_year="FY2024",
        evidence_quote="Company X reported ₹1 billion in sales for fiscal year 2024.",
        status=FactStatus.EXTRACTED
    )

    db_session.add(fact_a)
    db_session.add(fact_b)
    db_session.commit()

    matcher.index_fact(fact_a)
    matcher.index_fact(fact_b)

    matches = matcher.find_and_score_candidates_for_fact(fact_a, top_k=5)
    assert len(matches) >= 1

    # Check self-match exclusion
    for m in matches:
        assert m.candidate_fact_id != fact_a.id

    match_b = next(m for m in matches if m.candidate_fact_id == fact_b.id)
    assert match_b.match_type == MatchType.LIKELY_SAME_FACT
    assert match_b.overall_score >= 0.70
    assert match_b.entity_score == 1.0
    assert match_b.attribute_score == 1.0
    assert match_b.time_score >= 0.8
    assert match_b.currency_score == 1.0


def test_candidate_matching_temporal_variant(db_session: Session):
    matcher = CandidateMatchingService(db_session)

    # Fact A: Revenue FY2023
    fact_2023 = Fact(
        id="fact_temp_2023",
        document_id="doc_1",
        page_number=1,
        statement="Company X achieved revenue of ₹100 crore in FY2023.",
        entity="Company X",
        attribute="Revenue",
        raw_value="₹100 crore",
        normalized_value=1000000000.0,
        unit="INR",
        currency="INR",
        time_period="FY2023",
        fiscal_year="FY2023",
        evidence_quote="Company X achieved revenue of ₹100 crore in FY2023.",
        status=FactStatus.EXTRACTED
    )

    # Fact B: Revenue FY2024
    fact_2024 = Fact(
        id="fact_temp_2024",
        document_id="doc_2",
        page_number=1,
        statement="Company X achieved revenue of ₹100 crore in FY2024.",
        entity="Company X",
        attribute="Revenue",
        raw_value="₹100 crore",
        normalized_value=1000000000.0,
        unit="INR",
        currency="INR",
        time_period="FY2024",
        fiscal_year="FY2024",
        evidence_quote="Company X achieved revenue of ₹100 crore in FY2024.",
        status=FactStatus.EXTRACTED
    )

    db_session.add(fact_2023)
    db_session.add(fact_2024)
    db_session.commit()

    matcher.index_fact(fact_2023)
    matcher.index_fact(fact_2024)

    matches = matcher.find_and_score_candidates_for_fact(fact_2023, top_k=5)
    match = next(m for m in matches if m.candidate_fact_id == fact_2024.id)

    # Must be identified as TEMPORAL_VARIANT (not contradiction!)
    assert match.match_type == MatchType.TEMPORAL_VARIANT
    assert match.time_score <= 0.3
    assert "different time periods" in match.reason


def test_candidate_matching_incompatible_currencies(db_session: Session):
    matcher = CandidateMatchingService(db_session)

    # Fact A: ₹100 crore (INR)
    fact_inr = Fact(
        id="fact_curr_inr",
        document_id="doc_1",
        page_number=1,
        statement="Company X revenue reached ₹100 crore in FY2024.",
        entity="Company X",
        attribute="Revenue",
        raw_value="₹100 crore",
        normalized_value=1000000000.0,
        unit="INR",
        currency="INR",
        time_period="FY2024",
        fiscal_year="FY2024",
        evidence_quote="Company X revenue reached ₹100 crore in FY2024.",
        status=FactStatus.EXTRACTED
    )

    # Fact B: $100 million (USD)
    fact_usd = Fact(
        id="fact_curr_usd",
        document_id="doc_2",
        page_number=1,
        statement="Company X revenue reached $100 million in FY2024.",
        entity="Company X",
        attribute="Revenue",
        raw_value="$100 million",
        normalized_value=100000000.0,
        unit="USD",
        currency="USD",
        time_period="FY2024",
        fiscal_year="FY2024",
        evidence_quote="Company X revenue reached $100 million in FY2024.",
        status=FactStatus.EXTRACTED
    )

    db_session.add(fact_inr)
    db_session.add(fact_usd)
    db_session.commit()

    matcher.index_fact(fact_inr)
    matcher.index_fact(fact_usd)

    matches = matcher.find_and_score_candidates_for_fact(fact_inr, top_k=5)
    match = next(m for m in matches if m.candidate_fact_id == fact_usd.id)

    # Must be marked as INCOMPATIBLE_CONTEXT due to currency mismatch
    assert match.match_type == MatchType.INCOMPATIBLE_CONTEXT
    assert match.currency_score == 0.0
    assert "Incompatible currencies" in match.reason


def test_candidate_matches_api_endpoints(client: TestClient, db_session: Session):
    # Setup test facts in DB
    f1 = Fact(
        id="fact_api_1",
        document_id="doc_api_1",
        page_number=1,
        statement="Global Corp total revenue was $500 million in FY2024.",
        entity="Global Corp",
        attribute="Revenue",
        raw_value="$500 million",
        normalized_value=500000000.0,
        unit="USD",
        currency="USD",
        time_period="FY2024",
        fiscal_year="FY2024",
        evidence_quote="Global Corp total revenue was $500 million in FY2024.",
        status=FactStatus.EXTRACTED
    )
    f2 = Fact(
        id="fact_api_2",
        document_id="doc_api_2",
        page_number=2,
        statement="Global Corp generated $500M net sales during FY2024.",
        entity="Global Corp",
        attribute="Net sales",
        raw_value="$500M",
        normalized_value=500000000.0,
        unit="USD",
        currency="USD",
        time_period="FY2024",
        fiscal_year="FY2024",
        evidence_quote="Global Corp generated $500M net sales during FY2024.",
        status=FactStatus.EXTRACTED
    )
    db_session.add(f1)
    db_session.add(f2)
    db_session.commit()

    # 1. Rebuild index endpoint POST /api/v1/index/rebuild
    rebuild_res = client.post("/api/v1/index/rebuild")
    assert rebuild_res.status_code == 200
    assert rebuild_res.json()["success"] is True

    # 2. Get fact candidate matches endpoint GET /api/v1/facts/{fact_id}/matches
    matches_res = client.get(f"/api/v1/facts/{f1.id}/matches")
    assert matches_res.status_code == 200
    matches_data = matches_res.json()["data"]
    assert len(matches_data) >= 1
    match_item = matches_data[0]
    assert match_item["source_fact_id"] == f1.id
    assert match_item["candidate_fact_id"] == f2.id
    match_id = match_item["id"]

    # 3. List matches endpoint GET /api/v1/matches
    list_matches_res = client.get("/api/v1/matches")
    assert list_matches_res.status_code == 200
    all_matches = list_matches_res.json()["data"]
    assert len(all_matches) >= 1

    # 4. Get single match endpoint GET /api/v1/matches/{match_id}
    single_match_res = client.get(f"/api/v1/matches/{match_id}")
    assert single_match_res.status_code == 200
    single_data = single_match_res.json()["data"]
    assert single_data["id"] == match_id
    assert single_data["source_fact"]["id"] == f1.id
    assert single_data["candidate_fact"]["id"] == f2.id
