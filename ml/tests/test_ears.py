"""Tests for ears module: STTEngine, VoiceRecorder, SentimentAnalyzer (all mocked)."""
import re
from unittest.mock import MagicMock, patch, PropertyMock

import numpy as np
import pytest


class TestSentimentAnalyzerFillers:
    """Tests for SentimentAnalyzer.detect_fillers — no hardware needed."""

    def _make_analyzer(self):
        with patch("src.ears.sentiment_analyzer.Wav2Vec2FeatureExtractor"), \
             patch("src.ears.sentiment_analyzer.Wav2Vec2ForSequenceClassification"):
            from src.ears.sentiment_analyzer import SentimentAnalyzer
            analyzer = SentimentAnalyzer()
            analyzer.model = None  # disable emotion model
            return analyzer

    def test_detect_fillers_basic(self):
        analyzer = self._make_analyzer()
        result = analyzer.detect_fillers("umm I think umm basically it works")
        assert result["total_fillers"] >= 3
        assert "umm" in result["filler_breakdown"]

    def test_detect_fillers_no_fillers(self):
        analyzer = self._make_analyzer()
        result = analyzer.detect_fillers("I am proficient in Python and Java")
        assert result["total_fillers"] == 0
        assert result["filler_breakdown"] == {}

    def test_detect_fillers_case_insensitive(self):
        analyzer = self._make_analyzer()
        result = analyzer.detect_fillers("UMM Like BASICALLY")
        assert result["total_fillers"] >= 2

    def test_detect_fillers_empty_string(self):
        analyzer = self._make_analyzer()
        result = analyzer.detect_fillers("")
        assert result["total_fillers"] == 0

    def test_analyze_emotion_without_model(self):
        analyzer = self._make_analyzer()
        result = analyzer.analyze_emotion("fake_path.wav")
        assert result == {"neutral": 1.0}


class TestSTTEngine:
    """Tests for STTEngine.transcribe — file validation logic (model mocked)."""

    @patch("src.ears.stt_engine.WhisperModel")
    def test_transcribe_empty_path(self, mock_whisper):
        from src.ears.stt_engine import STTEngine
        engine = STTEngine()
        text, lang = engine.transcribe("", language=None)
        assert text == ""
        assert lang == "en"

    @patch("src.ears.stt_engine.WhisperModel")
    def test_transcribe_invalid_extension(self, mock_whisper):
        from src.ears.stt_engine import STTEngine
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as f:
            f.write(b"fake content")
            tmp_path = f.name

        try:
            engine = STTEngine()
            text, lang = engine.transcribe(tmp_path)
            assert text == ""
        finally:
            os.unlink(tmp_path)

    @patch("src.ears.stt_engine.WhisperModel")
    def test_transcribe_nonexistent_file(self, mock_whisper):
        from src.ears.stt_engine import STTEngine
        engine = STTEngine()
        text, lang = engine.transcribe("nonexistent_file.wav")
        assert text == ""

    @patch("src.ears.stt_engine.WhisperModel")
    def test_transcribe_empty_file(self, mock_whisper):
        from src.ears.stt_engine import STTEngine
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            tmp_path = f.name  # 0 bytes

        try:
            engine = STTEngine()
            text, lang = engine.transcribe(tmp_path)
            assert text == ""
        finally:
            os.unlink(tmp_path)


class TestVoiceRecorder:
    """Tests for VoiceRecorder — VAD threshold modes (model mocked)."""

    @patch("src.ears.vad.torch.hub.load")
    def test_set_mode_listening(self, mock_load):
        mock_model = MagicMock()
        mock_load.return_value = (mock_model, None)

        from src.ears.vad import VoiceRecorder
        vr = VoiceRecorder()
        vr.set_mode("listening")
        assert vr.current_threshold == vr.base_threshold

    @patch("src.ears.vad.torch.hub.load")
    def test_set_mode_speaking(self, mock_load):
        mock_model = MagicMock()
        mock_load.return_value = (mock_model, None)

        from src.ears.vad import VoiceRecorder
        vr = VoiceRecorder()
        vr.set_mode("speaking")
        assert vr.current_threshold == vr.speaking_threshold

    @patch("src.ears.vad.torch.hub.load")
    def test_check_speech_wrong_size(self, mock_load):
        mock_model = MagicMock()
        mock_load.return_value = (mock_model, None)

        from src.ears.vad import VoiceRecorder
        vr = VoiceRecorder()
        chunk = np.zeros(256, dtype=np.float32)
        assert vr._check_speech(chunk, 0.5) is False

    @patch("src.ears.vad.torch.hub.load")
    def test_is_speech_chunk_correct_size(self, mock_load):
        mock_model = MagicMock()
        mock_model.return_value = MagicMock(item=MagicMock(return_value=0.8))
        mock_load.return_value = (mock_model, None)

        from src.ears.vad import VoiceRecorder
        vr = VoiceRecorder()
        chunk = np.random.randn(512).astype(np.float32)
        result = vr.is_speech_chunk(chunk)
        assert isinstance(result, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
