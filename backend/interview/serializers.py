from rest_framework import serializers
from .models import InterviewSession, ChatMessage


# ── Request Serializers ─────────────────────────────────────────

class ResumeUploadSerializer(serializers.Serializer):
    """Accepts resume and job description files for ATS analysis."""
    resume = serializers.FileField(help_text="Resume PDF file")
    jd = serializers.FileField(help_text="Job description PDF file")


class StartSessionSerializer(serializers.Serializer):
    """Accepts parameters to start a new interview session."""
    difficulty = serializers.ChoiceField(
        choices=['Easy', 'Medium', 'Hard', 'Extreme'],
        default='Medium',
    )
    enable_proctoring = serializers.BooleanField(default=False)
    resume_text = serializers.CharField(
        required=False, allow_blank=True,
        help_text="Pre-extracted resume text (skip file upload)"
    )
    jd_text = serializers.CharField(
        required=False, allow_blank=True,
        help_text="Pre-extracted JD text (skip file upload)"
    )


class ChatInputSerializer(serializers.Serializer):
    """Accepts user input for a chat turn — text or audio."""
    message = serializers.CharField(
        required=False, allow_blank=True,
        help_text="User's text message"
    )
    audio = serializers.FileField(
        required=False,
        help_text="Audio file for STT transcription (wav, mp3, flac)"
    )

    def validate(self, attrs):
        if not attrs.get('message') and not attrs.get('audio'):
            raise serializers.ValidationError(
                "Either 'message' (text) or 'audio' (file) is required."
            )
        return attrs


class TTSInputSerializer(serializers.Serializer):
    """Accepts text to synthesize as speech."""
    text = serializers.CharField(help_text="Text to convert to speech")


# ── Response / Model Serializers ────────────────────────────────

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'role', 'content', 'created_at']
        read_only_fields = fields


class InterviewSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = InterviewSession
        fields = [
            'id', 'session_id', 'difficulty', 'status',
            'enable_proctoring',
            'ats_algorithmic_score', 'ats_llm_score', 'ats_combined_score',
            'evaluation_report',
            'created_at', 'ended_at',
            'messages',
        ]
        read_only_fields = fields
