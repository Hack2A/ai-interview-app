import hashlib
import json
from pathlib import Path
from functools import lru_cache
from typing import Any, Optional
import time

class CacheManager:
    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.embedding_cache = {}
        self.llm_cache = {}
        self.cache_ttl = 86400
    
    def _hash_content(self, content: str) -> str:
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def get_embedding_cache(self, text: str) -> Optional[Any]:
        cache_key = self._hash_content(text)
        
        if cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]
        
        cache_file = self.cache_dir / f"emb_{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    if time.time() - data['timestamp'] < self.cache_ttl:
                        import numpy as np
                        embedding = np.array(data['embedding'])
                        self.embedding_cache[cache_key] = embedding
                        return embedding
            except:
                pass
        return None
    
    def set_embedding_cache(self, text: str, embedding: Any):
        cache_key = self._hash_content(text)
        import numpy as np
        if isinstance(embedding, np.ndarray):
            embedding_list = embedding.tolist()
        else:
            embedding_list = embedding
        
        self.embedding_cache[cache_key] = embedding if isinstance(embedding, np.ndarray) else np.array(embedding)
        
        cache_file = self.cache_dir / f"emb_{cache_key}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    'embedding': embedding_list,
                    'timestamp': time.time()
                }, f)
        except:
            pass
    
    def get_llm_cache(self, resume_text: str, jd_text: str) -> Optional[dict]:
        cache_key = self._hash_content(resume_text + jd_text)
        
        if cache_key in self.llm_cache:
            cached_data = self.llm_cache[cache_key]
            if time.time() - cached_data['timestamp'] < self.cache_ttl:
                return cached_data['result']
        
        cache_file = self.cache_dir / f"llm_{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    if time.time() - data['timestamp'] < self.cache_ttl:
                        self.llm_cache[cache_key] = data
                        return data['result']
            except:
                pass
        return None
    
    def set_llm_cache(self, resume_text: str, jd_text: str, result: dict):
        cache_key = self._hash_content(resume_text + jd_text)
        cache_data = {
            'result': result,
            'timestamp': time.time()
        }
        self.llm_cache[cache_key] = cache_data
        
        cache_file = self.cache_dir / f"llm_{cache_key}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)
        except:
            pass
    
    def clear_cache(self):
        self.embedding_cache.clear()
        self.llm_cache.clear()
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
            except:
                pass

_global_cache = None

def get_cache_manager() -> CacheManager:
    global _global_cache
    if _global_cache is None:
        _global_cache = CacheManager()
    return _global_cache
