from django.db import models
from django.conf import settings


class InterviewSession(models.Model):
    """Tracks an interview session tied to a user."""

    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
        ('Extreme', 'Extreme'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='interview_sessions',
    )
    session_id = models.CharField(max_length=64, unique=True)
    difficulty = models.CharField(
        max_length=10, choices=DIFFICULTY_CHOICES, default='Medium'
    )
    status = models.CharField(
        max_length=12, choices=STATUS_CHOICES, default='active'
    )
    enable_proctoring = models.BooleanField(default=False)

    # ATS scores (populated after resume analysis)
    ats_algorithmic_score = models.FloatField(null=True, blank=True)
    ats_llm_score = models.FloatField(null=True, blank=True)
    ats_combined_score = models.FloatField(null=True, blank=True)

    # Evaluation report (populated after session ends)
    evaluation_report = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Session {self.session_id[:8]} — {self.user} ({self.difficulty})"


class ChatMessage(models.Model):
    """Stores individual messages in an interview session."""

    ROLE_CHOICES = [
        ('user', 'User'),
        ('ai', 'AI'),
        ('system', 'System'),
    ]

    session = models.ForeignKey(
        InterviewSession,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"[{self.role}] {self.content[:60]}"
