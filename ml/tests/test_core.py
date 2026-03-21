"""Tests for core module: SessionState, CacheManager, ResumeLoader, JDLoader."""
import json
import os
import tempfile
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import numpy as np
import pytest


class TestSessionState:
    def test_default_initialization(self):
        from src.core.session_state import SessionState
        s = SessionState()
        assert s.difficulty == "Medium"
        assert s.is_active is True
        assert s.question_count == 0
        assert len(s.session_id) == 32

    def test_update_difficulty_valid(self):
        from src.core.session_state import SessionState
        s = SessionState()
        s.difficulty = "Hard"
        assert s.difficulty == "Hard"

    def test_update_difficulty_invalid(self):
        from src.core.session_state import SessionState
        s = SessionState()
        result = s.update_difficulty("Impossible")
        assert result is False
        assert s.difficulty == "Medium"  # unchanged

    def test_increment_question(self):
        from src.core.session_state import SessionState
        s = SessionState()
        s.increment_question()
        assert s.question_count == 1

    def test_elapsed_seconds(self):
        from src.core.session_state import SessionState
        s = SessionState()
        time.sleep(0.1)
        assert s.elapsed_seconds() >= 0.05

    def test_to_dict(self):
        from src.core.session_state import SessionState
        s = SessionState()
        d = s.to_dict()
        assert "session_id" in d
        assert "difficulty" in d

    def test_repr(self):
        from src.core.session_state import SessionState
        s = SessionState()
        r = repr(s)
        assert "Session" in r


class TestCacheManager:
    def _make_cm(self):
        from src.core.cache_manager import CacheManager
        with tempfile.TemporaryDirectory() as tmpdir:
            cm = CacheManager(cache_dir=tmpdir)
            return cm, tmpdir

    def test_embedding_cache_roundtrip(self):
        cm, _ = self._make_cm()
        vec = np.array([1.0, 2.0, 3.0])
        cm.set_embedding_cache("hello", vec)
        result = cm.get_embedding_cache("hello")
        assert result is not None
        assert np.allclose(result, vec)

    def test_embedding_cache_miss(self):
        cm, _ = self._make_cm()
        assert cm.get_embedding_cache("miss") is None

    def test_llm_cache_roundtrip(self):
        cm, _ = self._make_cm()
        cm.set_llm_cache("resume", "jd", {"score": 80})
        result = cm.get_llm_cache("resume", "jd")
        assert result is not None
        assert result["score"] == 80

    def test_llm_cache_miss(self):
        cm, _ = self._make_cm()
        assert cm.get_llm_cache("a", "b") is None

    def test_clear_cache(self):
        cm, _ = self._make_cm()
        cm.set_embedding_cache("x", np.array([1.0]))
        cm.clear_cache()
        assert cm.get_embedding_cache("x") is None

    def test_cache_uses_sha256(self):
        cm, _ = self._make_cm()
        import hashlib
        vec = np.array([1.0])
        cm.set_embedding_cache("test_key", vec)
        expected_hash = hashlib.sha256("test_key".encode()).hexdigest()
        # Check in-memory cache uses sha256 key
        assert expected_hash in cm.embedding_cache


class TestResumeLoader:
    def test_no_resume_found(self):
        from src.core.resume_loader import ResumeLoader
        loader = ResumeLoader()
        with patch.object(Path, 'glob', return_value=[]):
            result = loader.load_resume()
        assert result is None

    def test_path_traversal_guard(self):
        from src.core.resume_loader import ResumeLoader
        loader = ResumeLoader()
        with pytest.raises(ValueError):
            loader.load_from_path(Path("../../etc/passwd.pdf"))


class TestJDLoader:
    def test_chunk_text(self):
        from src.core.jd_loader import JDLoader
        loader = JDLoader()
        text = " ".join([f"word{i}" for i in range(300)])
        chunks = loader.chunk_text(text, chunk_size=150, overlap=50)
        assert len(chunks) >= 2
        if len(chunks) >= 2:
            words_0 = set(chunks[0].split())
            words_1 = set(chunks[1].split())
            assert len(words_0 & words_1) > 0

    def test_chunk_empty_text(self):
        from src.core.jd_loader import JDLoader
        loader = JDLoader()
        assert loader.chunk_text("") == []
        assert loader.chunk_text(None) == []

    def test_no_jd_found(self):
        from src.core.jd_loader import JDLoader
        loader = JDLoader()
        with patch.object(Path, 'glob', return_value=[]):
            result = loader.load_jd()
        assert result is None

    def test_load_txt_file(self):
        from src.core.jd_loader import JDLoader
        loader = JDLoader()
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, dir=str(loader.jd_dir), mode='w') as f:
            f.write("We need a Python developer with 5 years experience")
            temp_path = Path(f.name)
        try:
            result = loader._load_txt(temp_path)
            assert "Python" in result
        finally:
            temp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
