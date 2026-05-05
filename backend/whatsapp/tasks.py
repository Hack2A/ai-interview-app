"""Celery tasks for WhatsApp message processing and reminders."""
import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger('whatsapp.tasks')


@shared_task(
    bind=True,
    queue='whatsapp',
    max_retries=3,
    default_retry_delay=5,
    acks_late=True,
)
def process_whatsapp_message(self, phone: str, wa_id: str, message: str, msg_type: str):
    """Process an inbound WhatsApp message asynchronously.

    Flow:
        1. Get or create WhatsAppUser
        2. Get or create conversation state
        3. Classify intent (rule-based, no LLM)
        4. Dispatch to action handler
        5. Send reply via Meta Graph API
    """
    from whatsapp.models import WhatsAppUser, WhatsAppConversation
    from whatsapp.intent import classify_intent
    from whatsapp.dispatcher import dispatch
    from whatsapp.sender import send_text_message

    try:
        # Lookup or bootstrap user
        wa_user, _ = WhatsAppUser.objects.get_or_create(
            phone=phone,
            defaults={'wa_id': wa_id},
        )
        conv, _ = WhatsAppConversation.objects.get_or_create(wa_user=wa_user)

        # Only text messages for MVP; handle unsupported types
        if msg_type != 'text':
            reply = _handle_unsupported_type(msg_type)
            send_text_message(phone, reply)
            return

        # Classify + dispatch
        intent_result = classify_intent(message, state=conv.state)
        logger.info(f"[{phone}] intent={intent_result.intent} state={conv.state}")

        reply = dispatch(intent_result, wa_user, conv)
        send_text_message(phone, reply)

    except Exception as exc:
        logger.exception(f"process_whatsapp_message failed for {phone}: {exc}")
        raise self.retry(exc=exc)


@shared_task(queue='default')
def send_interview_reminders():
    """Send 30-minute reminders for upcoming scheduled interviews.

    Called by Celery Beat every 5 minutes.
    """
    from whatsapp.models import ScheduledInterview
    from whatsapp.sender import send_text_message
    from django.conf import settings

    window_start = timezone.now()
    window_end   = window_start + timedelta(minutes=35)

    upcoming = ScheduledInterview.objects.filter(
        scheduled_at__gte=window_start,
        scheduled_at__lte=window_end,
        status='pending',
        reminder_sent=False,
        user__whatsapp_profile__linked=True,
    ).select_related('user__whatsapp_profile')

    for interview in upcoming:
        try:
            phone = interview.user.whatsapp_profile.phone
            dt_str = interview.scheduled_at.strftime('%I:%M %p')
            msg = (
                f"⏰ Reminder! Your {interview.interview_type} interview "
                f"starts in ~30 minutes ({dt_str}).\n\n"
                f"👉 Start here: {settings.BEAVER_BASE_URL}/interview/new"
            )
            send_text_message(phone, msg)
            interview.reminder_sent = True
            interview.save(update_fields=['reminder_sent'])
        except Exception as e:
            logger.error(f"Reminder failed for interview {interview.id}: {e}")


def _handle_unsupported_type(msg_type: str) -> str:
    if msg_type == 'audio':
        from django.conf import settings
        return (
            "I can only process text messages here. 🎤\n\n"
            "For voice-based interviews, use the app:\n"
            f"{settings.BEAVER_BASE_URL}/interview/new"
        )
    if msg_type == 'image':
        return "I can't process images yet. Send your resume as a PDF via the app."
    return "I can only handle text messages for now. Type 'help' to see what I can do."
