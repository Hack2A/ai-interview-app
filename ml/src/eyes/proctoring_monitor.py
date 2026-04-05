"""Proctoring Monitor — threaded webcam monitor with smooth display, adaptive risk scoring, and tiered alerts.

Key improvements over original:
- Display at 30 FPS, analyze at 5 FPS (smooth video, no choppiness)
- Rolling-window RiskScorer instead of simple counters
- Tiered alert escalation (info → warning → critical)
- Rich HUD overlay with color-coded status indicators
- Enhanced violation timeline for post-interview reports
"""
import cv2
import threading
import time
import logging
import numpy as np
from collections import defaultdict, deque
from dataclasses import dataclass, field

from src.eyes.proctoring_engine import ProctoringEngine
from config import settings

logger = logging.getLogger("ProctoringMonitor")

LOG_COOLDOWN_SECONDS = 5.0

# ── Violation severity weights for risk calculation ──
VIOLATION_WEIGHTS = {
    "user_left": 1.0,
    "multiple_people": 1.0,
    "looking_away": 0.4,
    "looking_down": 0.5,
    "head_tilted_down": 0.5,
    "head_turned_away": 0.6,
    "mouth_open": 0.2,
    "earpiece_suspected": 0.8,
    "phone_near_ear": 0.9,
    "object_cell_phone": 0.9,
    "object_book": 0.6,
    "object_laptop": 0.5,
    "object_remote": 0.3,
    "object_handbag": 0.1,
}

# HUD colors (BGR)
COLOR_GREEN = (0, 220, 0)
COLOR_YELLOW = (0, 220, 255)
COLOR_RED = (0, 0, 255)
COLOR_WHITE = (255, 255, 255)
COLOR_DARK_BG = (30, 30, 30)


# ══════════════════════════════════════════════════════════════════
#  RiskScorer — rolling window adaptive scoring
# ══════════════════════════════════════════════════════════════════

@dataclass
class ViolationEvent:
    violation_type: str
    timestamp: float
    weight: float
    sustained: bool = False
    duration: float = 0.0


class RiskScorer:
    """Adaptive risk scorer using a time-windowed violation history."""

    def __init__(self, window_seconds: float = 30.0) -> None:
        self.window_seconds = window_seconds
        self._events: deque[ViolationEvent] = deque()
        self._all_events: list[ViolationEvent] = []
        self.violation_counters: dict[str, int] = defaultdict(int)
        self._peak_risk: float = 0.0

    def add_violation(self, violation_type: str, sustained: bool = False, duration: float = 0.0) -> None:
        weight = VIOLATION_WEIGHTS.get(violation_type, 0.3)
        if sustained:
            weight *= 1.5  # Sustained violations are more severe

        event = ViolationEvent(
            violation_type=violation_type,
            timestamp=time.time(),
            weight=weight,
            sustained=sustained,
            duration=duration,
        )
        self._events.append(event)
        self._all_events.append(event)
        self.violation_counters[violation_type] += 1

    def get_risk_score(self) -> float:
        """Calculate current risk score (0.0 - 1.0) from recent violations."""
        self._prune_old_events()

        if not self._events:
            return 0.0

        total_weight = sum(e.weight for e in self._events)
        # Normalize: 5 weighted events in the window = score of 1.0
        score = min(total_weight / 5.0, 1.0)
        self._peak_risk = max(self._peak_risk, score)
        return score

    def get_alert_level(self) -> str:
        """Get current alert level based on risk score."""
        score = self.get_risk_score()
        thresholds = settings.RISK_ALERT_THRESHOLDS

        if score >= thresholds["critical"]:
            return "critical"
        elif score >= thresholds["warning"]:
            return "warning"
        elif score >= thresholds["info"]:
            return "info"
        return "clear"

    def _prune_old_events(self) -> None:
        cutoff = time.time() - self.window_seconds
        while self._events and self._events[0].timestamp < cutoff:
            self._events.popleft()

    def get_summary(self) -> dict:
        """Full summary for the final report."""
        current_score = self.get_risk_score()
        total = sum(self.violation_counters.values())

        severity = "low"
        if current_score >= settings.RISK_ALERT_THRESHOLDS["critical"]:
            severity = "critical"
        elif current_score >= settings.RISK_ALERT_THRESHOLDS["warning"]:
            severity = "high"
        elif current_score >= settings.RISK_ALERT_THRESHOLDS["info"]:
            severity = "medium"

        violation_timeline = [
            {
                "type": e.violation_type,
                "timestamp": e.timestamp,
                "duration": round(e.duration, 2),
                "sustained": e.sustained,
                "weight": round(e.weight, 2),
            }
            for e in self._all_events
        ]

        return {
            "total_violations": total,
            "violation_counts": dict(self.violation_counters),
            "current_risk_score": round(current_score, 3),
            "peak_risk_score": round(self._peak_risk, 3),
            "severity": severity,
            "alert_level": self.get_alert_level(),
            "violation_timeline": violation_timeline,
        }


# ══════════════════════════════════════════════════════════════════
#  ProctoringMonitor — smooth video + smart analysis
# ══════════════════════════════════════════════════════════════════

class ProctoringMonitor:
    """Threaded webcam proctoring monitor with smooth display and adaptive risk scoring.

    Display runs at PROCTORING_DISPLAY_FPS (30) for smooth video.
    Analysis runs at PROCTORING_FPS (5) to save CPU.
    """

    def __init__(self) -> None:
        self.engine = ProctoringEngine()
        self.is_running = False
        self.thread = None
        self.cap = None
        self._lock = threading.Lock()

        # Risk scoring replaces simple counters
        self.risk_scorer = RiskScorer(window_seconds=settings.RISK_WINDOW_SECONDS)

        # Continuous violation tracking for sustained detection
        self.continuous_violation_tracker: dict[str, float] = {}
        self._last_log_time: dict[str, float] = {}
        self.threshold_seconds = settings.VIOLATION_THRESHOLD_SECONDS

        # Analysis cache — reused between display frames
        self._last_violations: list[str] = []
        self._last_metadata: dict = {}
        self._last_alert_level: str = "clear"
        self._last_risk_score: float = 0.0

    def start(self) -> bool:
        """Start proctoring with user consent. Returns True on success."""
        if self.is_running:
            return True

        print("\n" + "=" * 60)
        print("PROCTORING NOTICE:")
        print("This interview session will use your webcam to monitor")
        print("for violations such as looking away, phone usage, or multiple people.")
        print("=" * 60)
        consent = input("Do you consent to webcam proctoring? (yes/no): ").strip().lower()

        if consent not in ['yes', 'y']:
            logger.info("User declined webcam proctoring")
            print("[Proctoring] Skipped — User declined consent")
            return False

        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                logger.error("Failed to open webcam")
                return False

            # Set webcam resolution for better quality
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

            self.is_running = True
            self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.thread.start()
            logger.info("Proctoring monitor started (display: %d FPS, analysis: %d FPS)",
                        settings.PROCTORING_DISPLAY_FPS, settings.PROCTORING_FPS)
            return True
        except Exception as e:
            logger.error(f"Failed to start proctoring: {e}")
            return False

    def _monitor_loop(self):
        """Main loop: display at 30 FPS, analyze at 5 FPS."""
        analysis_fps = settings.PROCTORING_FPS
        analysis_interval = 1.0 / analysis_fps

        last_analysis_time = 0

        while self.is_running:
            loop_start = time.time()

            try:
                ret, frame = self.cap.read()
                if not ret:
                    time.sleep(0.05)
                    continue

                current_time = time.time()

                # ── Analysis pass (every analysis_interval) ──
                if current_time - last_analysis_time >= analysis_interval:
                    last_analysis_time = current_time
                    violations, metadata = self.engine.analyze_frame(frame)

                    with self._lock:
                        self._last_violations = violations
                        self._last_metadata = metadata

                    # Process violations into risk scorer
                    self._process_violations(violations, current_time)

                    with self._lock:
                        self._last_risk_score = self.risk_scorer.get_risk_score()
                        self._last_alert_level = self.risk_scorer.get_alert_level()

                # Sleep slightly to prevent maxing out CPU if frame capture is too fast
                # We do not use imshow anymore, doing silent background capture
                elapsed = time.time() - loop_start
                sleep_time = (1.0 / 30.0) - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)

            except Exception as e:
                logger.error(f"Proctoring loop error: {e}")
                time.sleep(0.1)

    def _process_violations(self, violations: list[str], current_time: float) -> None:
        """Process raw violations into the risk scorer with sustained tracking."""
        for violation_type in violations:
            if violation_type not in self.continuous_violation_tracker:
                # New violation — log and start tracking
                self._log_violation(violation_type, 0, is_sustained=False)
                self.continuous_violation_tracker[violation_type] = current_time
            else:
                # Ongoing violation — check if sustained
                duration = current_time - self.continuous_violation_tracker[violation_type]
                if duration >= self.threshold_seconds:
                    self._log_violation(violation_type, duration, is_sustained=True)
                    self.continuous_violation_tracker[violation_type] = current_time

        # Clear trackers for violations that stopped
        active_violations = set(violations)
        for vtype in list(self.continuous_violation_tracker.keys()):
            if vtype not in active_violations:
                del self.continuous_violation_tracker[vtype]

    def _log_violation(self, violation_type: str, duration: float, is_sustained: bool = False) -> None:
        now = time.time()

        # Cooldown for non-sustained violations
        last_time = self._last_log_time.get(violation_type, 0)
        if not is_sustained and (now - last_time) < LOG_COOLDOWN_SECONDS:
            return

        self._last_log_time[violation_type] = now
        self.risk_scorer.add_violation(violation_type, sustained=is_sustained, duration=duration)

        if is_sustained:
            logger.warning(f"⚠ Sustained: {violation_type} for {duration:.1f}s")
        else:
            logger.debug(f"Violation: {violation_type}")



    # ── Public API ────────────────────────────────────────────────

    def get_violations_summary(self) -> dict:
        """Return the full risk-scored summary for the interview report."""
        return self.risk_scorer.get_summary()

    def stop(self) -> None:
        """Stop the proctoring monitor and release resources."""
        if not self.is_running:
            return

        self.is_running = False

        try:
            if self.thread:
                self.thread.join(timeout=3)
        except (KeyboardInterrupt, OSError):
            pass

        try:
            if self.cap:
                self.cap.release()
        except (cv2.error, OSError) as e:
            logger.warning(f"Failed to release webcam: {e}")

        try:
            self.engine.cleanup()
        except (AttributeError, RuntimeError) as e:
            logger.warning(f"Failed to cleanup proctoring engine: {e}")

        logger.info("Proctoring monitor stopped")
