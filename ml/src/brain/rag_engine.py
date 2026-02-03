import chromadb
from sentence_transformers import SentenceTransformer
from config import settings
import logging

logger = logging.getLogger("RAGEngine")

class RAGEngine:
    def __init__(self, jd_text=None):
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        settings.CHROMADB_DIR.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=str(settings.CHROMADB_DIR))
        
        try:
            self.collection = self.client.get_collection(name="job_context")
            logger.info("Loaded existing job_context collection")
        except:
            self.collection = self.client.create_collection(name="job_context")
            logger.info("Created new job_context collection")
        
        if jd_text and self.collection.count() == 0:
            self._index_jd(jd_text)
    
    def _index_jd(self, jd_text):
        from src.core.jd_loader import JDLoader
        
        loader = JDLoader()
        chunks = loader.chunk_text(jd_text, chunk_size=200)
        
        if not chunks:
            return
        
        embeddings = self.embedding_model.encode(chunks).tolist()
        
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        
        self.collection.add(
            embeddings=embeddings,
            documents=chunks,
            ids=ids
        )
        
        logger.info(f"Indexed {len(chunks)} JD chunks into ChromaDB")
    
    def query_jd(self, query_term, top_k=3):
        if self.collection.count() == 0:
            return []
        
        query_embedding = self.embedding_model.encode([query_term]).tolist()
        
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=min(top_k, self.collection.count())
        )
        
        if results and results['documents']:
            return results['documents'][0]
        return []
    
    def reset_index(self):
        self.client.delete_collection(name="job_context")
        self.collection = self.client.create_collection(name="job_context")
        logger.info("Reset job_context collection")
