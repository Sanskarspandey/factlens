"""Pytest fixtures and PDF test helpers."""
import os
import io
import pytest
import pymupdf as fitz
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.db.base import Base
from app.db.session import get_db
from app.main import app

TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def reset_vector_store():
    """Ensures ChromaDB/vector store is cleanly reset before each test."""
    from app.services.vector.chroma_store import vector_store
    vector_store.reset()
    yield
    vector_store.reset()



@pytest.fixture(scope="function")
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session_factory = sessionmaker(bind=connection)
    session = session_factory()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_pdf_bytes():
    """Generates a real 2-page PDF document in memory using PyMuPDF."""
    doc = fitz.open()
    
    # Page 1
    page1 = doc.new_page()
    text_p1 = (
        "Acme Corporation Annual Financial Report for FY2023.\n\n"
        "In fiscal year 2023, Acme Corporation reported total revenue of $383.29 billion.\n"
        "The company's operating margin expanded to 15.4% during this period.\n"
        "Net income reached $96.99 billion as of December 31, 2023.\n"
    )
    page1.insert_text((50, 72), text_p1, fontsize=11)

    # Page 2
    page2 = doc.new_page()
    text_p2 = (
        "India Operations Review:\n\n"
        "The India subsidiary achieved total revenues of INR 8,142 Cr in FY2023.\n"
        "Total capital expenditure for expansion was INR 25 Lakh.\n"
        "The workforce grew to 12,500 full-time employees in Q4 2023.\n"
    )
    page2.insert_text((50, 72), text_p2, fontsize=11)

    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes
