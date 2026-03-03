"""Tests for eyes module: ProctoringEngine, ProctoringMonitor (webcam/mediapipe mocked)."""
from unittest.mock import MagicMock, patch

import numpy as np
import pytest


class TestProctoringEngine:
    """Tests for ProctoringEngine — frame analysis with mocked MediaPipe."""

    def _make_engine(self):
        """Create ProctoringEngine with fully mocked MediaPipe."""
        with patch("src.eyes.proctoring_engine.mp") as mock_mp, \
             patch("src.eyes.proctoring_engine.cv2"):
            mock_face_mesh_cls = MagicMock()
            mock_face_mesh_instance = MagicMock()
            mock_face_mesh_cls.return_value = mock_face_mesh_instance
            mock_mp.solutions.face_mesh.FaceMesh = mock_face_mesh_cls

            from src.eyes.proctoring_engine import ProctoringEngine
            engine = ProctoringEngine()
            return engine, mock_face_mesh_instance

    def test_detect_faces_none(self):
        engine, mock_fm = self._make_engine()
        mock_result = MagicMock()
        mock_result.multi_face_landmarks = None
        mock_fm.process.return_value = mock_result

        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        with patch("src.eyes.proctoring_engine.cv2") as mock_cv2:
            mock_cv2.cvtColor.return_value = frame
            count, landmarks = engine.detect_faces(frame)

        assert count == 0
        assert landmarks is None

    def test_analyze_frame_no_face(self):
        engine, mock_fm = self._make_engine()
        mock_result = MagicMock()
        mock_result.multi_face_landmarks = None
        mock_fm.process.return_value = mock_result

        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        with patch("src.eyes.proctoring_engine.cv2") as mock_cv2:
            mock_cv2.cvtColor.return_value = frame
            violations, metadata = engine.analyze_frame(frame)

        assert "user_left" in violations
        assert metadata["face_count"] == 0

    def test_cleanup(self):
        engine, _ = self._make_engine()
        # Replace face_mesh with a MagicMock for cleanup verification
        mock_face_mesh = MagicMock()
        engine.face_mesh = mock_face_mesh
        engine.cleanup()
        mock_face_mesh.close.assert_called_once()


class TestProctoringMonitor:
    """Tests for ProctoringMonitor — violation logging, summary generation."""

    @patch("src.eyes.proctoring_monitor.ProctoringEngine")
    def test_violation_logging(self, mock_engine_cls):
        from src.eyes.proctoring_monitor import ProctoringMonitor

        monitor = ProctoringMonitor()
        monitor._log_violation("looking_away", 0, is_sustained=False)
        monitor._log_violation("looking_away", 3.0, is_sustained=True)

        assert monitor.violation_counters["looking_away"] == 2
        assert len(monitor.violation_log) == 2

    @patch("src.eyes.proctoring_monitor.ProctoringEngine")
    def test_get_violations_summary_low(self, mock_engine_cls):
        from src.eyes.proctoring_monitor import ProctoringMonitor

        monitor = ProctoringMonitor()
        summary = monitor.get_violations_summary()

        assert summary["total_violations"] == 0
        assert summary["severity"] == "low"

    @patch("src.eyes.proctoring_monitor.ProctoringEngine")
    def test_get_violations_summary_high(self, mock_engine_cls):
        from src.eyes.proctoring_monitor import ProctoringMonitor

        monitor = ProctoringMonitor()
        # Use different violation types to bypass per-type cooldown
        violation_types = [
            "looking_away", "head_tilted_down", "user_left",
            "multiple_people", "looking_left", "looking_right",
            "looking_up", "looking_down", "phone_detected",
            "book_detected", "screen_sharing", "tab_switch",
        ]
        for vtype in violation_types:
            monitor._log_violation(vtype, 3.0, is_sustained=True)

        summary = monitor.get_violations_summary()
        assert summary["total_violations"] == 12
        assert summary["severity"] == "high"

    @patch("src.eyes.proctoring_monitor.ProctoringEngine")
    def test_stop_when_not_running(self, mock_engine_cls):
        from src.eyes.proctoring_monitor import ProctoringMonitor

        monitor = ProctoringMonitor()
        monitor.is_running = False
        monitor.stop()  # should not raise


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
