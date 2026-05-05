"""WhatsApp action handlers.

Each function receives (wa_user, conv, entities) and returns a reply string.
Keep replies short: max 4 paragraphs, WhatsApp-friendly tone.
"""
import logging
import dateparser
from datetime import timedelta
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings

from interview.models import InterviewSession
from whatsapp.models import ScheduledInterview, WhatsAppConversation

logger = logging.getLogger('whatsapp.actions')

BASE_URL = settings.BEAVER_BASE_URL


# ── Helpers ───────────────────────────────────────────────────────────────────

def _last_sessions(user, n=3):
    return InterviewSession.objects.filter(
        user=user, status='completed'
    ).order_by('-created_at')[:n]


def _score_str(score) -> str:
    return f"{score:.0f}/100" if score is not None else "N/A"


# ── Actions ───────────────────────────────────────────────────────────────────

def handle_greeting(wa_user, conv, entities) -> str:
    name = wa_user.user.first_name if wa_user.user else "there"
    return (
        f"Hey {name}! 👋 Welcome to Beaver AI.\n\n"
        "I can help you with:\n"
        "• Interview history & feedback\n"
        "• Strengths & weaknesses\n"
        "• Scheduling an interview\n"
        "• Your ATS score\n\n"
        "What would you like to do?"
    )


def handle_help(wa_user, conv, entities) -> str:
    return (
        "Here's what I can do for you 🦫\n\n"
        "*Feedback & History*\n"
        "› 'Show my feedback'\n"
        "› 'My strengths / weaknesses'\n"
        "› 'Interview history'\n"
        "› 'My ATS score'\n\n"
        "*Scheduling*\n"
        "› 'Schedule a technical interview tomorrow 6pm'\n"
        "› 'Cancel my interview'\n\n"
        "*Other*\n"
        "› 'Start interview' → opens the app\n"
        "› 'Link account' → connect your account"
    )


def handle_get_feedback(wa_user, conv, entities) -> str:
    if not wa_user.linked or not wa_user.user:
        return _not_linked_msg()

    aspect = entities.get('aspect', 'full')
    cache_key = f"wa_feedback:{wa_user.user_id}:{aspect}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    sessions = _last_sessions(wa_user.user, n=1)
    if not sessions:
        return (
            "You haven't completed any interviews yet. "
            f"Start one here: {BASE_URL}/interview/new"
        )

    session = sessions[0]
    report  = session.evaluation_report or {}
    swot    = report.get('swot_analysis', {})
    score   = _score_str(session.ats_combined_score)
    date    = session.created_at.strftime('%b %d, %Y')

    if aspect == 'weaknesses':
        weaknesses = swot.get('weaknesses', [])
        if not weaknesses:
            reply = f"No specific weaknesses recorded from your {date} session."
        else:
            items = '\n'.join(f"• {w}" for w in weaknesses[:4])
            reply = f"Your areas to improve ({date}):\n{items}\n\nKeep practising! 💪"

    elif aspect == 'strengths':
        strengths = swot.get('strengths', [])
        if not strengths:
            reply = f"No specific strengths recorded from your {date} session."
        else:
            items = '\n'.join(f"• {s}" for s in strengths[:4])
            reply = f"Your strengths ({date}):\n{items}\n\nGreat work! 🌟"

    else:  # full feedback
        strengths  = swot.get('strengths', [])
        weaknesses = swot.get('weaknesses', [])
        mistakes   = report.get('mistakes', [])

        s_text = ', '.join(strengths[:2]) if strengths else 'N/A'
        w_text = ', '.join(weaknesses[:2]) if weaknesses else 'N/A'
        m_text = f"\n⚠️ Watch out: {mistakes[0]}" if mistakes else ''

        reply = (
            f"Last interview ({date}) — Score: *{score}*\n\n"
            f"✅ Strengths: {s_text}\n"
            f"📈 Improve: {w_text}"
            f"{m_text}\n\n"
            f"Full report → {BASE_URL}/reports"
        )

    cache.set(cache_key, reply, timeout=3600)
    return reply


def handle_get_history(wa_user, conv, entities) -> str:
    if not wa_user.linked or not wa_user.user:
        return _not_linked_msg()

    sessions = _last_sessions(wa_user.user, n=5)
    if not sessions:
        return (
            "No completed interviews yet.\n"
            f"Start your first one: {BASE_URL}/interview/new"
        )

    lines = []
    for i, s in enumerate(sessions, 1):
        score = _score_str(s.ats_combined_score)
        date  = s.created_at.strftime('%b %d')
        lines.append(f"{i}. {date} — {s.difficulty} — {score}")

    history = '\n'.join(lines)
    return (
        f"Your last {len(sessions)} interview(s):\n\n"
        f"{history}\n\n"
        f"Full history → {BASE_URL}/reports"
    )


def handle_get_score(wa_user, conv, entities) -> str:
    if not wa_user.linked or not wa_user.user:
        return _not_linked_msg()

    session = _last_sessions(wa_user.user, n=1).first()
    if not session:
        return f"No sessions yet. Start here: {BASE_URL}/interview/new"

    score = _score_str(session.ats_combined_score)
    algo  = _score_str(session.ats_algorithmic_score)
    llm   = _score_str(session.ats_llm_score)
    date  = session.created_at.strftime('%b %d, %Y')

    return (
        f"Your latest ATS score ({date}):\n\n"
        f"📊 Overall: *{score}*\n"
        f"⚙️ Algorithmic: {algo}\n"
        f"🧠 LLM Analysis: {llm}\n\n"
        f"Improve your resume → {BASE_URL}/career"
    )


def handle_schedule_interview(wa_user, conv, entities) -> str:
    if not wa_user.linked or not wa_user.user:
        return _not_linked_msg()

    raw_time       = entities.get('raw_time', '')
    interview_type = entities.get('interview_type')
    difficulty     = entities.get('difficulty', 'Medium')

    # Parse datetime
    parsed_dt = dateparser.parse(
        raw_time,
        settings={'PREFER_DATES_FROM': 'future', 'RETURN_AS_TIMEZONE_AWARE': True}
    )

    if not parsed_dt:
        # Ask for time
        conv.pending_intent = 'schedule_interview'
        conv.context.update({'interview_type': interview_type, 'difficulty': difficulty})
        if not interview_type:
            conv.state = 'awaiting_schedule_type'
            conv.save()
            return "What type of interview? Reply: technical / behavioral / hr / combined"
        conv.state = 'awaiting_schedule_time'
        conv.save()
        return "When should I schedule it? (e.g. 'tomorrow 6pm', 'Friday 3pm')"

    if not interview_type:
        conv.state = 'awaiting_schedule_type'
        conv.context.update({'scheduled_at': parsed_dt.isoformat(), 'difficulty': difficulty})
        conv.save()
        return "What type? Reply: technical / behavioral / hr / combined"

    # All info collected — create the schedule
    return _create_schedule(wa_user.user, parsed_dt, interview_type, difficulty, conv)


def handle_schedule_provide_time(wa_user, conv, entities) -> str:
    """Handle the time answer in multi-turn scheduling."""
    raw_time = entities.get('raw_time', '')
    parsed_dt = dateparser.parse(
        raw_time,
        settings={'PREFER_DATES_FROM': 'future', 'RETURN_AS_TIMEZONE_AWARE': True}
    )
    if not parsed_dt:
        return "Couldn't parse that time. Try: 'tomorrow 6pm' or 'Friday 3pm'"

    ctx = conv.context
    interview_type = ctx.get('interview_type')
    difficulty     = ctx.get('difficulty', 'Medium')

    if not interview_type:
        conv.state = 'awaiting_schedule_type'
        conv.context['scheduled_at'] = parsed_dt.isoformat()
        conv.save()
        return "What type? Reply: technical / behavioral / hr / combined"

    return _create_schedule(wa_user.user, parsed_dt, interview_type, difficulty, conv)


def handle_schedule_provide_type(wa_user, conv, entities) -> str:
    """Handle the type answer in multi-turn scheduling."""
    import dateparser as dp
    from datetime import datetime

    interview_type = entities.get('interview_type', 'technical')
    ctx = conv.context
    difficulty = ctx.get('difficulty', 'Medium')

    raw_at = ctx.get('scheduled_at')
    if raw_at:
        parsed_dt = dp.parse(raw_at, settings={'RETURN_AS_TIMEZONE_AWARE': True})
    else:
        parsed_dt = None

    if not parsed_dt:
        conv.state = 'awaiting_schedule_time'
        conv.context['interview_type'] = interview_type
        conv.save()
        return "When should I schedule it? (e.g. 'tomorrow 6pm')"

    return _create_schedule(wa_user.user, parsed_dt, interview_type, difficulty, conv)


def _create_schedule(user, dt, interview_type, difficulty, conv) -> str:
    ScheduledInterview.objects.create(
        user=user,
        scheduled_at=dt,
        interview_type=interview_type,
        difficulty=difficulty,
    )
    conv.reset()

    date_str = dt.strftime('%A, %b %d at %-I:%M %p')
    return (
        f"✅ Scheduled!\n\n"
        f"📅 {date_str}\n"
        f"🎯 Type: {interview_type.title()}\n"
        f"⚡ Difficulty: {difficulty}\n\n"
        f"I'll remind you 30 min before.\n"
        f"Ready to start early? → {BASE_URL}/interview/new"
    )


def handle_cancel_schedule(wa_user, conv, entities) -> str:
    if not wa_user.linked or not wa_user.user:
        return _not_linked_msg()

    upcoming = ScheduledInterview.objects.filter(
        user=wa_user.user, status='pending'
    ).order_by('scheduled_at').first()

    if not upcoming:
        return "You don't have any upcoming scheduled interviews."

    dt_str = upcoming.scheduled_at.strftime('%A, %b %d at %-I:%M %p')
    upcoming.status = 'cancelled'
    upcoming.save()
    return f"❌ Cancelled your interview scheduled for {dt_str}."


def handle_start_interview(wa_user, conv, entities) -> str:
    """WhatsApp doesn't do live interviews — redirect to app."""
    link = f"{BASE_URL}/interview/new"
    return (
        "Live interviews run in the Beaver AI app, not on WhatsApp.\n\n"
        f"👉 Start your interview here: {link}\n\n"
        "After it's done, come back here to check your feedback! 📊"
    )


def handle_link_account(wa_user, conv, entities) -> str:
    conv.state = 'awaiting_link_otp'
    conv.save()
    return (
        "To link your account:\n\n"
        f"1. Open {BASE_URL}/settings/whatsapp\n"
        "2. Click 'Generate Code'\n"
        "3. Send me the BV-XXXX code\n\n"
        "The code expires in 10 minutes."
    )


def handle_link_verify_otp(wa_user, conv, entities) -> str:
    from django.core.cache import cache
    otp = entities.get('otp', '').replace('-', '').replace(' ', '')
    cache_key = f"wa_link:{otp}"
    user_id = cache.get(cache_key)

    if not user_id:
        return "That code is invalid or expired. Generate a new one at the app."

    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
        wa_user.user = user
        wa_user.linked = True
        wa_user.save()
        cache.delete(cache_key)
        conv.reset()
        return (
            f"✅ Account linked! Welcome, {user.first_name}!\n\n"
            "You can now ask me about your interviews, feedback, and more."
        )
    except User.DoesNotExist:
        return "Something went wrong. Please try again."


def handle_unknown(wa_user, conv, entities, ask: str | None = None) -> str:
    conv.reset()
    if ask:
        return ask
    return (
        "I didn't quite get that.\n\n"
        "Try: 'show my feedback', 'my weaknesses', "
        "'schedule interview', or 'help' 😊"
    )


def _not_linked_msg() -> str:
    return (
        "Your WhatsApp isn't linked to a Beaver AI account yet.\n\n"
        "Send 'link account' to connect, or visit beaver.ai/settings/whatsapp"
    )
