"""Rule-based tone and bias detectors — NO LLM calls.

Feature 8A: AI Tone Detector
Feature 8B: Bias & Redundancy Detector
"""
import re


# ── Feature 8A: AI Tone Detector ──────────────────────────────────────

AI_PHRASES = [
    "i am excited to", "i am passionate about", "i would be a great fit",
    "looking forward to", "thank you for your consideration", "dynamic team",
    "synergy", "leverage my skills", "results-driven", "go-getter",
    "team player", "hard worker", "self-motivated", "detail-oriented",
    "thinking outside the box", "fast-paced environment", "cutting-edge",
    "proven track record", "strong communication skills", "highly motivated",
    "seeking to leverage", "best of breed", "move the needle", "deep dive",
    "circle back", "bandwidth", "game changer", "delighted to apply",
    "thrilled to apply", "enthusiastic about",
]

VAGUE_PHRASES = [
    "responsible for", "duties included", "worked on", "helped with",
    "assisted in", "various tasks", "and more", "participated in",
    "involved in", "part of a team that",
]

_PASSIVE_RE = re.compile(r"\b(was|were|been|being|is|are)\s+\w+ed\b", re.IGNORECASE)


def detect_ai_tone(text: str) -> dict:
    """Scan text for AI-sounding patterns and return a human-authenticity score.

    Algorithm (from spec):
      1. Lowercase the text
      2. Count matches from AI phrases → ai_count
      3. Count matches from vague phrases → vague_count
      4. Count '!' marks → excl_count
      5. Count passive voice via regex → passive_count
      6. Penalty = min(ai_count*8 + vague_count*8 + excl_count*3 + passive_count*2, 100)
      7. Score = max(0, 100 - penalty)
    """
    lower = text.lower()

    flagged_ai = [p for p in AI_PHRASES if p in lower]
    flagged_vague = [p for p in VAGUE_PHRASES if p in lower]
    excl_count = text.count("!")
    passive_matches = _PASSIVE_RE.findall(text)
    passive_count = len(passive_matches)

    ai_count = len(flagged_ai)
    vague_count = len(flagged_vague)

    penalty = min(ai_count * 8 + vague_count * 8 + excl_count * 3 + passive_count * 2, 100)
    score = max(0, 100 - penalty)

    if score >= 80:
        verdict = "✅ Sounds human and authentic"
    elif score >= 50:
        verdict = "⚠️ Some AI patterns detected — review flagged phrases"
    else:
        verdict = "❌ Heavy AI/robotic tone — significant rewrite recommended"

    # Generate improvement tips
    tips = []
    for phrase in flagged_ai[:3]:
        tips.append(f"Replace '{phrase}' with a specific evidence-backed statement")
    for phrase in flagged_vague[:3]:
        tips.append(f"Strengthen '{phrase}' with an action verb + metric")

    return {
        "tone_score": score,
        "verdict": verdict,
        "flagged_ai_phrases": flagged_ai,
        "flagged_vague_phrases": flagged_vague,
        "exclamation_marks": excl_count,
        "passive_voice_instances": passive_count,
        "improvement_tips": tips,
    }


# ── Feature 8B: Bias & Redundancy Detector ────────────────────────────

FILLER_WORDS = [
    "basically", "literally", "very", "really", "quite", "just",
    "actually", "in terms of", "at the end of the day", "needless to say",
]

BIAS_TERMS = [
    "native speaker", "mother tongue", "young professional",
]


def detect_bias_redundancy(text: str) -> dict:
    """Detect repeated sentence starts, filler words, and bias terms.

    Algorithm (from spec):
      1. Split text into sentences (by '.' and '\\n', keep > 15 chars)
      2. For each sentence, take first 5 words (lowercased) as key → count → flag count > 1
      3. Check for filler words
      4. Check for bias terms
    """
    # Split into sentences
    raw_sentences = re.split(r"[.\n]", text)
    sentences = [s.strip() for s in raw_sentences if len(s.strip()) > 15]

    # Repeated sentence starts (first 5 words)
    start_counts: dict[str, int] = {}
    for sent in sentences:
        words = sent.lower().split()[:5]
        key = " ".join(words)
        start_counts[key] = start_counts.get(key, 0) + 1

    repeated_starts = {k: v for k, v in start_counts.items() if v > 1}

    # Filler language
    lower = text.lower()
    fillers_found = [f for f in FILLER_WORDS if f in lower]

    # Bias terms
    bias_found = [b for b in BIAS_TERMS if b in lower]

    total_issues = len(repeated_starts) + len(fillers_found) + len(bias_found)

    advice = []
    if repeated_starts:
        advice.append("Vary your sentence openings to avoid repetitive structure.")
    if fillers_found:
        advice.append(f"Remove filler words: {', '.join(fillers_found)}")
    if bias_found:
        advice.append(f"Review potentially biased language: {', '.join(bias_found)}")
    if total_issues == 0:
        advice.append("Text looks clean — no major issues detected.")

    return {
        "repeated_sentence_starts": repeated_starts,
        "filler_language_found": fillers_found,
        "potential_bias_terms": bias_found,
        "total_issues": total_issues,
        "advice": advice,
    }
