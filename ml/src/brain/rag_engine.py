"""Retrieval-Augmented Generation engine using ChromaDB.

Contains two engines:
- RAGEngine: Original JD-context retrieval (unchanged)
- QuestionBankRAG: Interview question bank retrieval with metadata filtering
"""
import json
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


# ══════════════════════════════════════════════════════════════════
#  QuestionBankRAG — Interview question retrieval with filtering
# ══════════════════════════════════════════════════════════════════

class QuestionBankRAG:
    """Retrieves interview questions from the curated question bank.

    Supports filtering by category, difficulty, and candidate skills.
    Uses a separate ChromaDB collection from the JD engine.
    """

    def __init__(self) -> None:
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

        settings.CHROMADB_DIR.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(settings.CHROMADB_DIR))
        try:
            self.collection = self.client.get_or_create_collection(
                name="question_bank",
                metadata={"hnsw:space": "cosine"},
            )
            self._indexed = self.collection.count() > 0
        except Exception as e:
            logger.warning(f"Corrupted question_bank collection detected: {e}. Recreating...")
            try:
                self.client.delete_collection("question_bank")
            except:
                pass
            self.collection = self.client.get_or_create_collection(
                name="question_bank",
                metadata={"hnsw:space": "cosine"},
            )
            self._indexed = False

    @property
    def is_indexed(self) -> bool:
        return self._indexed and self.collection.count() > 0

    def index_questions(self, questions: list[dict], batch_size: int = 100) -> int:
        """Index the question bank into ChromaDB with metadata.

        Args:
            questions: List of dicts matching InterviewQuestion schema.
            batch_size: Number of questions to embed per batch.

        Returns:
            Number of questions indexed.
        """
        if not questions:
            return 0

        # Reset collection for fresh index
        try:
            self.client.delete_collection(name="question_bank")
        except (ValueError, Exception):
            pass
        self.collection = self.client.get_or_create_collection(
            name="question_bank",
            metadata={"hnsw:space": "cosine"},
        )

        total = 0
        for i in range(0, len(questions), batch_size):
            batch = questions[i:i + batch_size]

            documents = []
            metadatas = []
            ids = []

            for j, q in enumerate(batch):
                q_text = q.get("question", "")
                if not q_text or len(q_text.strip()) < 10:
                    continue

                doc_text = q_text
                documents.append(doc_text)

                metadatas.append({
                    "answer": q.get("answer", "")[:1500],
                    "category": q.get("category", "general_technical"),
                    "difficulty": q.get("difficulty", "medium"),
                    "tags": json.dumps(q.get("tags", [])),
                    "company": q.get("company", "generic"),
                    "evaluation_points": json.dumps(q.get("evaluation_points", [])),
                    "source": q.get("source", "unknown"),
                })

                ids.append(f"qb_{i + j}")

            if documents:
                embeddings = self.embedding_model.encode(documents).tolist()
                self.collection.add(
                    embeddings=embeddings,
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids,
                )
                total += len(documents)

        self._indexed = True
        logger.info(f"Indexed {total} questions into question_bank collection")
        return total

    def retrieve_questions(
        self,
        query: str,
        top_k: int = 5,
        category: str | None = None,
        difficulty: str | None = None,
        exclude_ids: list[str] | None = None,
    ) -> list[dict]:
        """Retrieve relevant questions with optional metadata filters.

        Args:
            query: Semantic search query (e.g., skills from resume).
            top_k: Max number of results.
            category: Filter by category (e.g., "dsa", "ml").
            difficulty: Filter by difficulty ("easy", "medium", "hard").
            exclude_ids: ChromaDB IDs to exclude (already-asked questions).

        Returns:
            List of dicts with question, answer, metadata.
        """
        if not self.is_indexed:
            logger.warning("Question bank not indexed yet")
            return []

        # Build ChromaDB where filter
        where_filter = {}
        conditions = []
        if category:
            conditions.append({"category": {"$eq": category}})
        if difficulty:
            conditions.append({"difficulty": {"$eq": difficulty}})

        if len(conditions) == 1:
            where_filter = conditions[0]
        elif len(conditions) > 1:
            where_filter = {"$and": conditions}

        query_embedding = self.embedding_model.encode([query]).tolist()

        try:
            n_results = min(top_k + len(exclude_ids or []), self.collection.count())
            if n_results <= 0:
                return []

            kwargs = {
                "query_embeddings": query_embedding,
                "n_results": n_results,
            }
            if where_filter:
                kwargs["where"] = where_filter

            results = self.collection.query(**kwargs)
        except Exception as e:
            logger.warning(f"Question bank query failed: {e}")
            # Retry without filter
            try:
                results = self.collection.query(
                    query_embeddings=query_embedding,
                    n_results=min(top_k, self.collection.count()),
                )
            except Exception as e2:
                logger.error(f"Question bank query failed completely: {e2}")
                return []

        if not results or not results.get("documents"):
            return []

        output = []
        exclude_set = set(exclude_ids or [])

        for idx in range(len(results["documents"][0])):
            doc_id = results["ids"][0][idx]
            if doc_id in exclude_set:
                continue

            meta = results["metadatas"][0][idx] if results.get("metadatas") else {}
            output.append({
                "id": doc_id,
                "question": results["documents"][0][idx],
                "answer": meta.get("answer", ""),
                "category": meta.get("category", "general_technical"),
                "difficulty": meta.get("difficulty", "medium"),
                "tags": json.loads(meta.get("tags", "[]")),
                "evaluation_points": json.loads(meta.get("evaluation_points", "[]")),
                "source": meta.get("source", "unknown"),
                "distance": results["distances"][0][idx] if results.get("distances") else None,
            })

            if len(output) >= top_k:
                break

        return output

    def retrieve_by_skills(
        self,
        skills: list[str],
        category: str | None = None,
        difficulty: str | None = None,
        top_k: int = 5,
        exclude_ids: list[str] | None = None,
    ) -> list[dict]:
        """Resume-aware retrieval: build query from skills list."""
        if not skills:
            query = "general software engineering interview questions"
        else:
            query = "interview questions about " + ", ".join(skills[:10])

        return self.retrieve_questions(
            query=query,
            top_k=top_k,
            category=category,
            difficulty=difficulty,
            exclude_ids=exclude_ids,
        )

    def get_question_count(self) -> int:
        """Return total questions in the index."""
        return self.collection.count() if self._indexed else 0
