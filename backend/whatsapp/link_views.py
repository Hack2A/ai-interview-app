"""Account linking via OTP — called from the web app settings page."""
import secrets
import logging

from django.core.cache import cache
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from whatsapp.models import WhatsAppUser

logger = logging.getLogger('whatsapp.link')


class GenerateLinkOTPView(APIView):
    """Generate a one-time OTP for linking WhatsApp to the logged-in account.

    POST /api/whatsapp/link/generate/
    Auth: JWT required
    Response: {"otp": "BV-4827", "expires_in": 600}
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Check if already linked
        if hasattr(user, 'whatsapp_profile') and user.whatsapp_profile.linked:
            phone = user.whatsapp_profile.phone
            return Response({
                'already_linked': True,
                'phone': phone,
            })

        # Generate OTP
        otp   = f"BV-{secrets.randbelow(9000) + 1000}"
        key   = f"wa_link:{otp}"
        cache.set(key, user.id, timeout=600)  # 10 minutes

        logger.info(f"Generated WhatsApp link OTP for user {user.id}")
        return Response({
            'otp': otp,
            'expires_in': 600,
            'instructions': 'Send this code to Beaver AI on WhatsApp',
        })


class LinkStatusView(APIView):
    """Check if the current user's WhatsApp is linked.

    GET /api/whatsapp/link/status/
    Auth: JWT required
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            profile = user.whatsapp_profile
            return Response({
                'linked': profile.linked,
                'phone':  profile.phone if profile.linked else None,
            })
        except WhatsAppUser.DoesNotExist:
            return Response({'linked': False, 'phone': None})
