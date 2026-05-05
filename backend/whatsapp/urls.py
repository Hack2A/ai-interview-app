"""WhatsApp URL configuration."""
from django.urls import path
from whatsapp.views import WhatsAppWebhookView
from whatsapp import link_views

urlpatterns = [
    path('webhook/', WhatsAppWebhookView.as_view(), name='whatsapp-webhook'),
    path('link/generate/', link_views.GenerateLinkOTPView.as_view(), name='wa-link-generate'),
    path('link/status/', link_views.LinkStatusView.as_view(), name='wa-link-status'),
]
