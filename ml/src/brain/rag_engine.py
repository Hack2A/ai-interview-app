"""Retrieval-Augmented Generation engine using ChromaDB for JD context."""
import logging
from typing import Optional

import chromadb
from sentence_transformers import SentenceTransformer

from config import settings

logger = logging.getLogger("RAGEngine")

DEFAULT_CHUNK_SIZE = 150
DEFAULT_CHUNK_OVERLAP = 50
DEFAULT_TOP_K = 5


class RAGEngine:
    """Retrieval-Augmented Generation engine using ChromaDB for JD context."""

    def __init__(self, jd_text: str | None = None) -> None:
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

        settings.CHROMADB_DIR.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(settings.CHROMADB_DIR))
        self.collection = self.client.get_or_create_collection(name="job_context")

        # Always reindex when JD text is provided (ensures fresh data)
        if jd_text:
            self.reset_index()
            self._index_jd(jd_text)

    def _index_jd(self, jd_text: str) -> None:
        """Chunk and embed JD text into ChromaDB with overlap."""
        chunks = self._chunk_text(jd_text, chunk_size=DEFAULT_CHUNK_SIZE, overlap=DEFAULT_CHUNK_OVERLAP)
        if not chunks:
            return

        embeddings = self.embedding_model.encode(chunks).tolist()
        ids = [f"chunk_{i}" for i in range(len(chunks))]

        self.collection.add(embeddings=embeddings, documents=chunks, ids=ids)
        logger.info(f"Indexed {len(chunks)} JD chunks into ChromaDB (size={DEFAULT_CHUNK_SIZE}, overlap={DEFAULT_CHUNK_OVERLAP})")

    def _chunk_text(self, text: str, chunk_size: int = 150, overlap: int = 50) -> list[str]:
        """Split text into overlapping word-level chunks for better retrieval."""
        if not text:
            return []

        words = text.split()
        chunks = []
        step = max(chunk_size - overlap, 1)

        for i in range(0, len(words), step):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
            if i + chunk_size >= len(words):
                break

        return chunks

    def query_jd(self, query_term: str, top_k: int = DEFAULT_TOP_K) -> list[str]:
        """Query JD context for relevant chunks."""
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

    def query_jd_multi(self, queries: list[str], top_k: int = 3) -> list[str]:
        """Query with multiple terms and return deduplicated results."""
        if self.collection.count() == 0:
            return []

        all_results = []
        seen = set()

        for query in queries:
            results = self.query_jd(query, top_k=top_k)
            for chunk in results:
                chunk_key = chunk[:80]
                if chunk_key not in seen:
                    seen.add(chunk_key)
                    all_results.append(chunk)

        return all_results

    def reset_index(self) -> None:
        """Delete and recreate the JD collection."""
        try:
            self.client.delete_collection(name="job_context")
        except (ValueError, Exception):
            pass
        self.collection = self.client.get_or_create_collection(name="job_context")
        logger.info("Reset job_context collection")
