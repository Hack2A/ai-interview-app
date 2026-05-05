"""WhatsApp webhook view — receives and verifies Meta messages."""
import json
import hmac
import hashlib
import logging

from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from django.core.cache import cache

from whatsapp.tasks import process_whatsapp_message

logger = logging.getLogger('whatsapp.webhook')


def check_rate_limit(phone: str, limit: int = 15, window: int = 60) -> bool:
    """Allow up to `limit` messages per `window` seconds per phone number."""
    key = f"wa_rate:{phone}"
    count = cache.get(key, 0)
    if count >= limit:
        return False
    cache.set(key, count + 1, timeout=window)
    return True


@method_decorator(csrf_exempt, name='dispatch')
class WhatsAppWebhookView(View):
    """Handles GET (verification) and POST (messages) from Meta."""

    def get(self, request):
        """Webhook verification challenge from Meta."""
        mode         = request.GET.get('hub.mode')
        token        = request.GET.get('hub.verify_token')
        challenge    = request.GET.get('hub.challenge')

        if mode == 'subscribe' and token == settings.WHATSAPP_VERIFY_TOKEN:
            logger.info("WhatsApp webhook verified successfully.")
            return HttpResponse(challenge, content_type='text/plain')

        logger.warning("Webhook verification failed — token mismatch.")
        return HttpResponse(status=403)

    def post(self, request):
        """Receive inbound messages — always return 200 immediately."""
        # Verify Meta signature FIRST (security gate)
        if not self._verify_signature(request):
            logger.warning("Invalid WhatsApp signature — rejecting request.")
            return HttpResponse(status=403)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponse(status=400)

        # Extract and queue messages (never block here)
        for entry in data.get('entry', []):
            for change in entry.get('changes', []):
                value    = change.get('value', {})
                messages = value.get('messages', [])

                for msg in messages:
                    phone    = msg.get('from', '')
                    wa_id    = msg.get('id', '')
                    msg_type = msg.get('type', 'text')
                    text     = msg.get('text', {}).get('body', '')

                    if not phone:
                        continue

                    if not check_rate_limit(phone):
                        logger.info(f"Rate limited: {phone}")
                        continue

                    # Dispatch to Celery — non-blocking
                    process_whatsapp_message.delay(
                        phone=phone,
                        wa_id=wa_id,
                        message=text,
                        msg_type=msg_type,
                    )

        # Meta requires 200 within 15s — always return fast
        return HttpResponse(status=200)

    def _verify_signature(self, request) -> bool:
        """Verify X-Hub-Signature-256 from Meta."""
        if not settings.WHATSAPP_APP_SECRET:
            # Skip in dev if secret not set
            return True

        signature = request.headers.get('X-Hub-Signature-256', '')
        if not signature:
            return False

        expected = 'sha256=' + hmac.new(
            settings.WHATSAPP_APP_SECRET.encode(),
            request.body,
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(signature, expected)
