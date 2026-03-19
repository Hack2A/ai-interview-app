from django.urls import path
from .views import (
    HealthCheckView,
    ATSAnalyzeView,
    StartSessionView,
    SessionInfoView,
    ChatView,
    ChatHistoryView,
    EndSessionView,
    TTSView,
)

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='interview-health'),
    path('ats/analyze/', ATSAnalyzeView.as_view(), name='interview-ats-analyze'),
    path('session/start/', StartSessionView.as_view(), name='interview-session-start'),
    path('session/info/', SessionInfoView.as_view(), name='interview-session-info'),
    path('session/end/', EndSessionView.as_view(), name='interview-session-end'),
    path('chat/', ChatView.as_view(), name='interview-chat'),
    path('chat/history/', ChatHistoryView.as_view(), name='interview-chat-history'),
    path('tts/', TTSView.as_view(), name='interview-tts'),
]
