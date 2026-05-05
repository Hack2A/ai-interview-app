"""Intent classification — rule-based with keyword shortcuts.

Strategy for MVP:
  1. Hard-coded keyword shortcuts (zero LLM cost)
  2. Pattern matching for scheduling, feedback, history
  3. Fallback to 'unknown' for unrecognised messages

No external LLM call for intent — fast, deterministic, free.
The LLM is only used inside action handlers (e.g. summarising feedback).
"""
import re
from dataclasses import dataclass, field


@dataclass
class IntentResult:
    intent: str
    entities: dict = field(default_factory=dict)
    # If set, send this question back before executing intent
    ask: str | None = None


# ── Keyword maps ──────────────────────────────────────────────────────────────

_SCHEDULE_KEYWORDS = [
    'schedule', 'book', 'set up', 'arrange', 'fix', 'plan', 'appointment',
    'tomorrow', 'today', 'monday', 'tuesday', 'wednesday', 'thursday',
    'friday', 'saturday', 'sunday', 'next week', 'at ', 'am', 'pm',
]

_FEEDBACK_KEYWORDS = [
    'feedback', 'how did i do', 'my result', 'my performance', 'result',
    'evaluation', 'assessment', 'how was i', 'review',
]

_WEAKNESS_KEYWORDS = [
    'weakness', 'weaknesses', 'weak', 'improve', 'lacking', 'bad at',
    'struggle', 'needs work', 'areas to improve',
]

_STRENGTH_KEYWORDS = [
    'strength', 'strengths', 'strong', 'good at', 'excel', 'best at',
    'doing well', 'positive',
]

_HISTORY_KEYWORDS = [
    'history', 'past interview', 'previous interview', 'last interview',
    'all sessions', 'my sessions', 'interviews i', 'how many interview',
]

_SCORE_KEYWORDS = [
    'score', 'ats score', 'rating', 'grade', 'points', 'mark', 'percentage',
]

_CANCEL_KEYWORDS = [
    'cancel', 'remove', 'delete', 'unbook', 'reschedule',
]

_HELP_KEYWORDS = ['help', 'what can you', 'commands', 'options', 'menu']
_GREETING_KEYWORDS = ['hi', 'hello', 'hey', 'hii', 'helo', 'good morning',
                      'good afternoon', 'good evening', 'sup', 'yo']
_LINK_KEYWORDS = ['link account', 'connect account', 'link my account', 'otp']
_START_INTERVIEW_KEYWORDS = ['start interview', 'begin interview', 'take interview',
                              'conduct interview', 'open interview', 'do an interview',
                              'want interview', 'practice interview']

_TYPE_MAP = {
    'technical': 'technical', 'tech': 'technical',
    'behavioral': 'behavioral', 'behaviour': 'behavioral', 'behavior': 'behavioral',
    'hr': 'hr', 'human resource': 'hr',
    'combined': 'combined', 'mix': 'combined', 'mixed': 'combined',
}
_DIFFICULTY_MAP = {
    'easy': 'Easy', 'medium': 'Medium', 'hard': 'Hard',
    'extreme': 'Extreme', 'difficult': 'Hard',
}


def classify_intent(text: str, state: str = 'idle') -> IntentResult:
    """Classify a WhatsApp message into an intent.

    Args:
        text: Raw message from user.
        state: Current conversation state (affects interpretation).

    Returns:
        IntentResult with intent name and extracted entities.
    """
    lower = text.lower().strip()

    # State-aware classification — mid-conversation answers
    if state == 'awaiting_schedule_type':
        interview_type = _extract_type(lower)
        if interview_type:
            return IntentResult('schedule_provide_type', {'interview_type': interview_type})
        return IntentResult('unknown', ask="Please specify: technical, behavioral, hr, or combined.")

    if state == 'awaiting_schedule_time':
        return IntentResult('schedule_provide_time', {'raw_time': text})

    if state == 'awaiting_link_otp':
        otp_match = re.search(r'BV-?\d{4}', text.upper())
        if otp_match:
            return IntentResult('link_verify_otp', {'otp': otp_match.group()})
        return IntentResult('unknown', ask="Please send the BV-XXXX code from the app.")

    # ── Hard-coded shortcuts (no ambiguity) ─────────────────────────────────
    if any(lower == kw for kw in _GREETING_KEYWORDS):
        return IntentResult('greeting')

    if any(kw in lower for kw in _HELP_KEYWORDS):
        return IntentResult('help')

    if any(kw in lower for kw in _LINK_KEYWORDS):
        return IntentResult('link_account')

    if any(kw in lower for kw in _START_INTERVIEW_KEYWORDS):
        return IntentResult('start_interview')

    # ── Cancel ──────────────────────────────────────────────────────────────
    if any(kw in lower for kw in _CANCEL_KEYWORDS):
        return IntentResult('cancel_schedule')

    # ── Score ───────────────────────────────────────────────────────────────
    if any(kw in lower for kw in _SCORE_KEYWORDS):
        return IntentResult('get_score')

    # ── History ─────────────────────────────────────────────────────────────
    if any(kw in lower for kw in _HISTORY_KEYWORDS):
        return IntentResult('get_history')

    # ── Strength / Weakness (specific aspects) ───────────────────────────────
    if any(kw in lower for kw in _WEAKNESS_KEYWORDS):
        return IntentResult('get_feedback', {'aspect': 'weaknesses'})

    if any(kw in lower for kw in _STRENGTH_KEYWORDS):
        return IntentResult('get_feedback', {'aspect': 'strengths'})

    # ── General feedback ────────────────────────────────────────────────────
    if any(kw in lower for kw in _FEEDBACK_KEYWORDS):
        return IntentResult('get_feedback', {'aspect': 'full'})

    # ── Schedule ────────────────────────────────────────────────────────────
    if any(kw in lower for kw in _SCHEDULE_KEYWORDS):
        entities: dict = {}
        entities['interview_type'] = _extract_type(lower) or None
        entities['difficulty']     = _extract_difficulty(lower) or None
        # Pass raw text so action handler can parse datetime with dateparser
        entities['raw_time']       = text
        return IntentResult('schedule_interview', entities)

    return IntentResult('unknown')


def _extract_type(text: str) -> str | None:
    for keyword, mapped in _TYPE_MAP.items():
        if keyword in text:
            return mapped
    return None


def _extract_difficulty(text: str) -> str | None:
    for keyword, mapped in _DIFFICULTY_MAP.items():
        if keyword in text:
            return mapped
    return None
