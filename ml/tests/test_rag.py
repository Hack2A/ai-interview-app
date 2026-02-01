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

def test_rag_engine_index_and_query(jd_text):
    rag = RAGEngine(jd_text=jd_text)
    
    assert rag is not None, "RAGEngine should initialize successfully"
    
    results = rag.query_jd("technical skills", top_k=2)
    
    assert isinstance(results, list), "query_jd should return a list"
    assert len(results) > 0, "query_jd should return at least one result"
    
    for i, chunk in enumerate(results, 1):
        assert isinstance(chunk, str), f"Chunk {i} should be a string, got {type(chunk)}"
        chunk_preview = chunk[:100] if isinstance(chunk, str) else repr(chunk)
        print(f"\n  [{i}] {chunk_preview}...")
    
    combined_results = " ".join(results).lower()
    expected_terms = ["python", "fastapi", "postgresql"]
    found_terms = [term for term in expected_terms if term in combined_results]
    
    assert len(found_terms) > 0, f"Expected to find at least one of {expected_terms} in results"
    print(f"\n✅ Found expected terms: {found_terms}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
