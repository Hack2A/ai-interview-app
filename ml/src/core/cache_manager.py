import hashlib
import json
import logging
import threading
import time
from pathlib import Path
from typing import Any, Optional

import numpy as np

from config import settings

logger = logging.getLogger("CacheManager")

DEFAULT_CACHE_TTL = 86400  # 24 hours


class CacheManager:
    """Thread-safe, TTL-based cache for embeddings and LLM results."""

    def __init__(self, cache_dir: str | Path | None = None) -> None:
        self.cache_dir = Path(cache_dir) if cache_dir else settings.BASE_DIR / "data" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.embedding_cache: dict[str, dict] = {}
        self.llm_cache: dict[str, dict] = {}
        self.cache_ttl = DEFAULT_CACHE_TTL
        self._lock = threading.RLock()

    def _hash_content(self, content: str) -> str:
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def get_embedding_cache(self, text: str) -> Optional[np.ndarray]:
        """Retrieve cached embedding for text, or None if expired/missing."""
        cache_key = self._hash_content(text)

        with self._lock:
            if cache_key in self.embedding_cache:
                cached_data = self.embedding_cache[cache_key]
                if time.time() - cached_data['timestamp'] < self.cache_ttl:
                    return cached_data['embedding']
                del self.embedding_cache[cache_key]

        cache_file = self.cache_dir / f"emb_{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    if time.time() - data['timestamp'] < self.cache_ttl:
                        embedding = np.array(data['embedding'])
                        with self._lock:
                            self.embedding_cache[cache_key] = {
                                'embedding': embedding,
                                'timestamp': data['timestamp'],
                            }
                        return embedding
            except (json.JSONDecodeError, KeyError, FileNotFoundError, OSError):
                logger.debug(f"Failed to read embedding cache file: {cache_file}")
        return None

    def set_embedding_cache(self, text: str, embedding: Any) -> None:
        """Store embedding in memory and disk cache."""
        cache_key = self._hash_content(text)
        embedding_array = embedding if isinstance(embedding, np.ndarray) else np.array(embedding)
        embedding_list = embedding_array.tolist()

        with self._lock:
            self.embedding_cache[cache_key] = {
                'embedding': embedding_array,
                'timestamp': time.time(),
            }

        cache_file = self.cache_dir / f"emb_{cache_key}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump({'embedding': embedding_list, 'timestamp': time.time()}, f)
        except (OSError, IOError) as e:
            logger.warning(f"Failed to write embedding cache: {e}")

    def get_llm_cache(self, resume_text: str, jd_text: str) -> Optional[dict]:
        """Retrieve cached LLM result for resume+JD pair."""
        cache_key = self._hash_content(
            f"{self._hash_content(resume_text)}:{self._hash_content(jd_text)}"
        )

        with self._lock:
            if cache_key in self.llm_cache:
                cached_data = self.llm_cache[cache_key]
                if time.time() - cached_data['timestamp'] < self.cache_ttl:
                    return cached_data['result']
                del self.llm_cache[cache_key]

        cache_file = self.cache_dir / f"llm_{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    if time.time() - data['timestamp'] < self.cache_ttl:
                        with self._lock:
                            self.llm_cache[cache_key] = data
                        return data['result']
            except (json.JSONDecodeError, KeyError, FileNotFoundError, OSError):
                logger.debug(f"Failed to read LLM cache file: {cache_file}")
        return None

    def set_llm_cache(self, resume_text: str, jd_text: str, result: dict) -> None:
        """Store LLM result in memory and disk cache."""
        cache_key = self._hash_content(
            f"{self._hash_content(resume_text)}:{self._hash_content(jd_text)}"
        )

        cache_data = {'result': result, 'timestamp': time.time()}
        with self._lock:
            self.llm_cache[cache_key] = cache_data

        cache_file = self.cache_dir / f"llm_{cache_key}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)
        except (OSError, IOError) as e:
            logger.warning(f"Failed to write LLM cache: {e}")

    def clear_cache(self) -> None:
        """Clear all in-memory and disk caches."""
        with self._lock:
            self.embedding_cache.clear()
            self.llm_cache.clear()
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
            except (OSError, PermissionError) as e:
                logger.warning(f"Failed to delete cache file {cache_file}: {e}")


_global_cache: Optional[CacheManager] = None
_cache_lock = threading.Lock()


def get_cache_manager() -> CacheManager:
    """Return singleton CacheManager instance."""
    global _global_cache
    if _global_cache is None:
        with _cache_lock:
            if _global_cache is None:
                _global_cache = CacheManager()
    return _global_cache
