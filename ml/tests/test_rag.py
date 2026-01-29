from src.brain.rag_engine import RAGEngine

print("="*60)
print("     Testing RAG Engine (Module 1)")
print("="*60)

jd_text = """
Senior Backend Engineer
We are looking for an experienced backend engineer with strong skills in:
- Python and FastAPI
- PostgreSQL and Redis
- Docker and Kubernetes
- AWS cloud services
- REST API design
Must have 5+ years experience in scalable systems.
"""

print("\n📄 Indexing Job Description...")
rag = RAGEngine(jd_text=jd_text)

print("✅ JD indexed in ChromaDB!")

print("\n🔍 Querying for 'technical skills'...")
results = rag.query_jd("technical skills", top_k=2)

print("\n✅ Retrieved Context:")
for i, chunk in enumerate(results, 1):
    print(f"\n  [{i}] {chunk[:100]}...")

print("\n" + "="*60)
print("✅ RAG Module Working!")
print("="*60)
