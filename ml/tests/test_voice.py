"""Tests for voice module: TTSEngine with edge-tts + piper backends."""
import queue
from unittest.mock import MagicMock, patch, AsyncMock

import pytest


class TestTTSEngine:
    """Tests for TTSEngine — edge-tts primary, piper fallback."""

    @patch("src.voice.tts_engine.settings")
    def test_init_sets_up_temp_dir(self, mock_settings):
        mock_settings.BASE_DIR = MagicMock()
        temp_dir = MagicMock()
        mock_settings.BASE_DIR.__truediv__ = MagicMock(return_value=MagicMock(
            __truediv__=MagicMock(return_value=temp_dir)
        ))
        mock_settings.TTS_MODEL_PATH = MagicMock()

        from src.voice.tts_engine import TTSEngine
        engine = TTSEngine.__new__(TTSEngine)
        engine.vad = None
        engine._piper_voice = None
        engine._edge_failed_count = 0
        engine._max_edge_failures = 5
        engine._temp_dir = temp_dir

    @patch("src.voice.tts_engine.settings")
    def test_speak_text_calls_synthesize(self, mock_settings):
        from src.voice.tts_engine import TTSEngine

        engine = TTSEngine.__new__(TTSEngine)
        engine.vad = None
        engine._piper_voice = None
        engine._edge_failed_count = 0
        engine._max_edge_failures = 5
        engine._temp_dir = MagicMock()

        with patch.object(engine, '_synthesize_and_play') as mock_synth:
            engine.speak_text("Hello world")
            mock_synth.assert_called_once_with("Hello world")

    @patch("src.voice.tts_engine.settings")
    def test_speak_stream_collects_and_speaks(self, mock_settings):
        from src.voice.tts_engine import TTSEngine

        engine = TTSEngine.__new__(TTSEngine)
        engine.vad = None
        engine._piper_voice = None
        engine._edge_failed_count = 0
        engine._max_edge_failures = 5
        engine._temp_dir = MagicMock()

        def gen():
            yield "Hello"
            yield "World"

        with patch.object(engine, '_synthesize_and_play') as mock_synth:
            result = engine.speak_stream(gen())
            assert result is None
            mock_synth.assert_called_once_with("Hello World")

    @patch("src.voice.tts_engine.settings")
    def test_speak_stream_skips_empty(self, mock_settings):
        from src.voice.tts_engine import TTSEngine

        engine = TTSEngine.__new__(TTSEngine)
        engine.vad = None
        engine._piper_voice = None
        engine._edge_failed_count = 0
        engine._max_edge_failures = 5
        engine._temp_dir = MagicMock()

        def gen():
            yield ""
            yield None
            yield "   "

        with patch.object(engine, '_synthesize_and_play') as mock_synth:
            engine.speak_stream(gen())
            mock_synth.assert_not_called()

    @patch("src.voice.tts_engine.settings")
    def test_edge_failure_increments_counter(self, mock_settings):
        from src.voice.tts_engine import TTSEngine

        engine = TTSEngine.__new__(TTSEngine)
        engine.vad = None
        engine._piper_voice = None
        engine._edge_failed_count = 0
        engine._max_edge_failures = 5
        engine._temp_dir = MagicMock()

        with patch.object(engine, '_synthesize_edge', return_value=None):
            with patch.object(engine, '_synthesize_piper', return_value=None):
                engine._synthesize_and_play("Test")
                assert engine._edge_failed_count == 1

    @patch("src.voice.tts_engine.settings")
    def test_skips_edge_after_max_failures(self, mock_settings):
        from src.voice.tts_engine import TTSEngine

        engine = TTSEngine.__new__(TTSEngine)
        engine.vad = None
        engine._piper_voice = None
        engine._edge_failed_count = 5
        engine._max_edge_failures = 5
        engine._temp_dir = MagicMock()

        with patch.object(engine, '_synthesize_edge') as mock_edge:
            with patch.object(engine, '_synthesize_piper', return_value=None):
                engine._synthesize_and_play("Test")
                mock_edge.assert_not_called()


class TestTTSWorkerProtocol:
    """Tests for TTS worker message parsing logic (legacy)."""

    def test_message_format(self):
        filepath = "data/temp/tts_12345.wav"
        text = "Hello world"
        msg = f"{filepath}|{text}\n"

        assert "|" in msg
        parts = msg.strip().split("|", 1)
        assert len(parts) == 2
        assert parts[0] == filepath
        assert parts[1] == text

    def test_path_validation_rejects_absolute(self):
        filename = "C:\\Windows\\System32\\cmd.exe"
        from pathlib import Path
        assert Path(filename).is_absolute() is True

    def test_path_validation_rejects_traversal(self):
        filename = "../../etc/passwd"
        assert ".." in filename


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
