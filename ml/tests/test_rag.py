"""Tests for RAG engine: ChromaDB indexing, querying, overlap chunking."""
import pytest
from src.brain.rag_engine import RAGEngine


@pytest.fixture
def jd_text():
    return """
    Senior Backend Engineer
    We are looking for an experienced backend engineer with strong skills in:
    - Python and FastAPI
    - PostgreSQL and Redis
    - Docker and Kubernetes
    - AWS cloud services
    - REST API design
    Must have 5+ years experience in scalable systems.
    """


@pytest.fixture(autouse=True)
def clean_chromadb():
    """Clean the job_context collection before each test to avoid stale data."""
    import chromadb
    from config import settings

    settings.CHROMADB_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(settings.CHROMADB_DIR))
    try:
        client.delete_collection(name="job_context")
    except Exception:
        pass
    yield
    try:
        client.delete_collection(name="job_context")
    except Exception:
        pass


def test_rag_engine_index_and_query(jd_text):
    rag = RAGEngine(jd_text=jd_text)

    assert rag is not None
    assert rag.collection.count() > 0

    results = rag.query_jd("technical skills", top_k=2)
    assert isinstance(results, list)
    assert len(results) > 0

    combined = " ".join(results).lower()
    expected = ["python", "fastapi", "postgresql"]
    found = [t for t in expected if t in combined]
    assert len(found) > 0, f"Expected at least one of {expected} in results"


def test_rag_engine_empty_query():
    rag = RAGEngine(jd_text=None)
    results = rag.query_jd("anything")
    assert results == []


def test_rag_engine_reset_index(jd_text):
    rag = RAGEngine(jd_text=jd_text)
    assert rag.collection.count() > 0
    rag.reset_index()
    assert rag.collection.count() == 0


def test_rag_engine_multi_query(jd_text):
    rag = RAGEngine(jd_text=jd_text)
    results = rag.query_jd_multi(["python skills", "cloud services"], top_k=2)
    assert isinstance(results, list)
    assert len(results) > 0


def test_rag_engine_always_reindexes(jd_text):
    """Test that providing jd_text always forces reindex."""
    rag1 = RAGEngine(jd_text="Old JD about Java and Spring Boot")
    rag2 = RAGEngine(jd_text=jd_text)  # Should replace old data
    results = rag2.query_jd("Python FastAPI")
    combined = " ".join(results).lower()
    # Should find new JD content, not old
    assert "python" in combined or "fastapi" in combined


def test_rag_engine_chunk_overlap(jd_text):
    rag = RAGEngine(jd_text=None)
    chunks = rag._chunk_text("word " * 300, chunk_size=150, overlap=50)
    assert len(chunks) > 2  # With overlap, should get more chunks than without


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
