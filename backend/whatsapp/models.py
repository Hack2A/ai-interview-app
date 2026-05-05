from django.db import models
from django.conf import settings
from django.utils import timezone


class WhatsAppUser(models.Model):
    """Links a WhatsApp phone number to a Beaver AI account."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='whatsapp_profile',
    )
    phone  = models.CharField(max_length=20, unique=True, db_index=True)
    wa_id  = models.CharField(max_length=50, unique=True)
    linked = models.BooleanField(default=False)
    opted_in = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.phone} ({'linked' if self.linked else 'unlinked'})"


class WhatsAppConversation(models.Model):
    """Tracks conversation state (short-term memory) per WhatsApp user."""
    STATE_CHOICES = [
        ('idle',                    'Idle'),
        ('awaiting_schedule_time',  'Awaiting Schedule Time'),
        ('awaiting_schedule_type',  'Awaiting Interview Type'),
        ('awaiting_link_otp',       'Awaiting Link OTP'),
    ]

    wa_user        = models.OneToOneField(WhatsAppUser, on_delete=models.CASCADE,
                                          related_name='conversation')
    state          = models.CharField(max_length=50, default='idle')
    pending_intent = models.CharField(max_length=50, blank=True)
    # Stores partial data across turns: e.g. {"scheduled_at": "...", "type": "..."}
    context        = models.JSONField(default=dict)
    last_active    = models.DateTimeField(auto_now=True)

    def reset(self):
        self.state = 'idle'
        self.pending_intent = ''
        self.context = {}
        self.save(update_fields=['state', 'pending_intent', 'context'])

    def __str__(self):
        return f"{self.wa_user.phone} — {self.state}"


class ScheduledInterview(models.Model):
    """Interview scheduled by user via WhatsApp."""
    STATUS_CHOICES = [
        ('pending',       'Pending'),
        ('reminder_sent', 'Reminder Sent'),
        ('completed',     'Completed'),
        ('cancelled',     'Cancelled'),
    ]
    TYPE_CHOICES = [
        ('technical',  'Technical'),
        ('behavioral', 'Behavioral'),
        ('hr',         'HR'),
        ('combined',   'Combined'),
    ]

    user           = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                       related_name='scheduled_interviews')
    scheduled_at   = models.DateTimeField(db_index=True)
    interview_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='technical')
    difficulty     = models.CharField(max_length=10, default='Medium')
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reminder_sent  = models.BooleanField(default=False)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['scheduled_at']

    def __str__(self):
        return f"{self.user} — {self.interview_type} @ {self.scheduled_at}"
