"""JWT authentication middleware for Django Channels WebSocket connections.

Extracts JWT token from the query string (?token=xxx) and authenticates the user.
Falls back to AnonymousUser if no token is provided or token is invalid.
"""

import logging
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger('interview')


@database_sync_to_async
def get_user_from_token(token: str):
    """Validate a JWT access token and return the associated user."""
    try:
        from rest_framework_simplejwt.tokens import AccessToken
        from django.contrib.auth import get_user_model

        User = get_user_model()
        validated = AccessToken(token)
        user_id = validated['user_id']
        return User.objects.get(id=user_id)
    except Exception as e:
        logger.debug(f"JWT auth failed: {e}")
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    """Middleware that authenticates WebSocket connections via JWT query param.

    Usage in ASGI routing:
        JWTAuthMiddleware(URLRouter(websocket_urlpatterns))

    Frontend connects with:
        new WebSocket("ws://localhost:8000/ws/interview/?token=<jwt_access_token>")
    """

    async def __call__(self, scope, receive, send):
        # Extract token from query string
        query_string = scope.get('query_string', b'').decode('utf-8')
        params = parse_qs(query_string)
        token = params.get('token', [None])[0]

        if token:
            scope['user'] = await get_user_from_token(token)
        else:
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)
