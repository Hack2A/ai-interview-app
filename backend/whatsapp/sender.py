"""WhatsApp message sender — wraps Meta Graph API."""
import logging
import httpx
from django.conf import settings

logger = logging.getLogger('whatsapp.sender')

_GRAPH_URL = "https://graph.facebook.com/v19.0/{phone_number_id}/messages"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }


def send_text_message(to: str, text: str) -> bool:
    """Send a plain text message to a WhatsApp number.

    Args:
        to: Phone number in E.164 format (e.g. +919876543210)
        text: Message body (max ~4096 chars; we cap at 1500 for readability)

    Returns:
        True on success, False on failure.
    """
    if not settings.WHATSAPP_ACCESS_TOKEN:
        logger.warning("WHATSAPP_ACCESS_TOKEN not set — skipping send")
        return False

    # Cap at 1500 chars for readable WhatsApp messages
    text = text[:1500]

    url = _GRAPH_URL.format(phone_number_id=settings.WHATSAPP_PHONE_NUMBER_ID)
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }
    try:
        resp = httpx.post(url, headers=_headers(), json=payload, timeout=10)
        resp.raise_for_status()
        return True
    except httpx.HTTPStatusError as e:
        logger.error(f"WhatsApp send failed [{e.response.status_code}]: {e.response.text}")
        return False
    except Exception as e:
        logger.error(f"WhatsApp send error: {e}")
        return False


def download_media(media_id: str) -> bytes | None:
    """Download a media file (PDF, image) from Meta CDN.

    Returns raw bytes on success, None on failure.
    """
    # Step 1: get media URL
    url_endpoint = f"https://graph.facebook.com/v19.0/{media_id}"
    try:
        resp = httpx.get(url_endpoint, headers=_headers(), timeout=10)
        resp.raise_for_status()
        media_url = resp.json().get('url')
        if not media_url:
            return None

        # Step 2: download the file
        file_resp = httpx.get(media_url, headers=_headers(), timeout=30)
        file_resp.raise_for_status()
        return file_resp.content
    except Exception as e:
        logger.error(f"Media download failed for {media_id}: {e}")
        return None
