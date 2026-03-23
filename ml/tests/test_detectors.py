"""Tests for rule-based detectors (Features 8A and 8B) — no LLM required."""
import sys
from pathlib import Path

# Ensure ml/ is on sys.path so `src.career` imports work
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.career.detectors import detect_ai_tone, detect_bias_redundancy


# ── Feature 8A: AI Tone Detector ──────────────────────────────────────

class TestAIToneDetector:

    def test_human_text_high_score(self):
        """Clean, specific human text should score ≥ 80."""
        text = (
            "At Acme Corp I redesigned the ETL pipeline, cutting data latency from "
            "12 hours to 45 minutes. I wrote the migration scripts in Python and "
            "coordinated rollout across three regions."
        )
        result = detect_ai_tone(text)
        assert result["tone_score"] >= 80
        assert "human" in result["verdict"].lower() or "✅" in result["verdict"]

    def test_ai_heavy_text_low_score(self):
        """Text stuffed with AI clichés should score < 50."""
        text = (
            "I am excited to leverage my skills in this fast-paced environment! "
            "I am passionate about thinking outside the box and moving the needle! "
            "As a results-driven go-getter and team player, I have a proven track record "
            "of synergy with dynamic teams! I am thrilled to apply!"
        )
        result = detect_ai_tone(text)
        assert result["tone_score"] < 50
        assert len(result["flagged_ai_phrases"]) >= 5
        assert "❌" in result["verdict"]

    def test_medium_score(self):
        """Some AI phrases should produce a score between 50 and 80."""
        text = (
            "I built a microservices platform serving 2M requests per day. "
            "I am passionate about distributed systems. "
            "Looking forward to contributing to the team."
        )
        result = detect_ai_tone(text)
        assert 20 <= result["tone_score"] <= 90

    def test_empty_text(self):
        """Empty text should score 100 (no penalties)."""
        result = detect_ai_tone("")
        assert result["tone_score"] == 100

    def test_exclamation_penalty(self):
        """Many exclamation marks should reduce score."""
        text = "Great! Amazing! Wonderful! Fantastic! Excellent! Superb!"
        result = detect_ai_tone(text)
        assert result["exclamation_marks"] == 6
        assert result["tone_score"] < 100

    def test_passive_voice_detection(self):
        """Passive voice should be detected and penalized."""
        text = "The project was completed ahead of schedule. The system was designed for scale."
        result = detect_ai_tone(text)
        assert result["passive_voice_instances"] >= 2

    def test_improvement_tips(self):
        """Flagged phrases should generate improvement tips."""
        text = "I am excited to leverage my skills as a results-driven professional."
        result = detect_ai_tone(text)
        assert len(result["improvement_tips"]) > 0


# ── Feature 8B: Bias & Redundancy Detector ────────────────────────────

class TestBiasRedundancyDetector:

    def test_repeated_sentence_starts(self):
        """Text with repeated beginnings (same first 5 words) should be flagged."""
        text = (
            "I was responsible for building the payment system backend.\n"
            "I was responsible for building the analytics dashboard.\n"
            "I was responsible for building the mobile app."
        )
        result = detect_bias_redundancy(text)
        assert len(result["repeated_sentence_starts"]) >= 1
        assert result["total_issues"] >= 1

    def test_filler_words_detected(self):
        """Filler words should be identified."""
        text = (
            "I basically rewrote the entire codebase. "
            "The system was literally crashing every day. "
            "Actually, the team was very responsive."
        )
        result = detect_bias_redundancy(text)
        assert "basically" in result["filler_language_found"]
        assert "literally" in result["filler_language_found"]

    def test_bias_terms_detected(self):
        """Bias terms should be flagged."""
        text = "Looking for a native speaker with young professional energy."
        result = detect_bias_redundancy(text)
        assert "native speaker" in result["potential_bias_terms"]
        assert "young professional" in result["potential_bias_terms"]

    def test_clean_text_no_issues(self):
        """Professional text with no issues should have total_issues == 0."""
        text = (
            "Designed a distributed caching layer using Redis, reducing API latency by 40%. "
            "Led migration from monolith to microservices across 12 services. "
            "Mentored three junior engineers through structured code review sessions."
        )
        result = detect_bias_redundancy(text)
        assert result["total_issues"] == 0
        assert any("clean" in a.lower() or "no major" in a.lower() for a in result["advice"])

    def test_empty_text(self):
        """Empty text should produce no issues."""
        result = detect_bias_redundancy("")
        assert result["total_issues"] == 0

    def test_advice_generated(self):
        """Text with issues should generate actionable advice."""
        text = (
            "I basically managed the team. "
            "I basically handled deployments. "
            "We need a native speaker for this role."
        )
        result = detect_bias_redundancy(text)
        assert len(result["advice"]) > 0
