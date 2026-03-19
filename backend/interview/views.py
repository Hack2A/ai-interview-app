import secrets
import logging
import tempfile
import os

from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import FileResponse

from .apps import get_orchestrator
from .models import InterviewSession, ChatMessage
from .serializers import (
    ResumeUploadSerializer,
    StartSessionSerializer,
    ChatInputSerializer,
    TTSInputSerializer,
    ChatMessageSerializer,
    InterviewSessionSerializer,
)

logger = logging.getLogger('interview')


def _extract_pdf_text(uploaded_file):
    """Save uploaded file to a temp path and extract text using pypdf."""
    try:
        from pypdf import PdfReader

        suffix = os.path.splitext(uploaded_file.name)[1] or '.pdf'
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            for chunk in uploaded_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        reader = PdfReader(tmp_path)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        os.unlink(tmp_path)
        return text.strip()
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        return None


def _save_uploaded_audio(uploaded_file):
    """Save uploaded audio to a temp file and return the path."""
    suffix = os.path.splitext(uploaded_file.name)[1] or '.wav'
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        for chunk in uploaded_file.chunks():
            tmp.write(chunk)
        return tmp.name


def _get_active_session(user):
    """Get the active interview session for a user, or None."""
    return InterviewSession.objects.filter(
        user=user, status='active'
    ).first()


# ── Health Check ─────────────────────────────────────────────────

class HealthCheckView(APIView):
    """ML engine health check — no authentication required."""
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            orch = get_orchestrator()
            health = orch.health_check()
            return Response(health, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e), "detail": "ML orchestrator failed to initialize"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )


# ── ATS Resume Analysis ─────────────────────────────────────────

class ATSAnalyzeView(APIView):
    """Upload resume + JD PDFs, get ATS analysis scores."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ResumeUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        resume_text = _extract_pdf_text(serializer.validated_data['resume'])
        jd_text = _extract_pdf_text(serializer.validated_data['jd'])

        if not resume_text:
            return Response(
                {"error": "Could not extract text from resume PDF"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not jd_text:
            return Response(
                {"error": "Could not extract text from job description PDF"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        orch = get_orchestrator()
        result = orch.analyze_resume(resume_text=resume_text, jd_text=jd_text)

        if "error" in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        return Response(result, status=status.HTTP_200_OK)


# ── Session Management ───────────────────────────────────────────

class StartSessionView(APIView):
    """Create a new interview session."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Check for existing active session
        existing = _get_active_session(request.user)
        if existing:
            return Response(
                {
                    "error": "An active session already exists",
                    "session_id": existing.session_id,
                },
                status=status.HTTP_409_CONFLICT,
            )

        serializer = StartSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        difficulty = serializer.validated_data['difficulty']
        enable_proctoring = serializer.validated_data['enable_proctoring']

        orch = get_orchestrator()

        # Load documents if provided
        resume_text = serializer.validated_data.get('resume_text')
        jd_text = serializer.validated_data.get('jd_text')
        if resume_text:
            orch.load_resume_from_text(resume_text)
        if jd_text:
            orch.load_jd_from_text(jd_text)

        # Create orchestrator session
        orch.new_session(difficulty=difficulty)
        orch.reset_chat()

        # Start proctoring if requested
        if enable_proctoring:
            orch.start_proctoring()

        # Create Django model
        session_id = secrets.token_hex(16)
        session = InterviewSession.objects.create(
            user=request.user,
            session_id=session_id,
            difficulty=difficulty,
            enable_proctoring=enable_proctoring,
        )

        # Generate opening question
        opening = orch.get_opening_question(difficulty=difficulty)

        # Save AI opening message
        ChatMessage.objects.create(
            session=session, role='ai', content=opening
        )

        return Response(
            {
                "session_id": session_id,
                "difficulty": difficulty,
                "enable_proctoring": enable_proctoring,
                "opening_message": opening,
            },
            status=status.HTTP_201_CREATED,
        )


class SessionInfoView(APIView):
    """Get current active session info."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        session = _get_active_session(request.user)
        if not session:
            return Response(
                {"error": "No active session found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = InterviewSessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ── Chat ─────────────────────────────────────────────────────────

class ChatView(APIView):
    """Send a message (text or audio) and get an AI response."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        session = _get_active_session(request.user)
        if not session:
            return Response(
                {"error": "No active session. Start one first."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ChatInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        orch = get_orchestrator()
        user_text = serializer.validated_data.get('message', '')

        # If audio provided, transcribe first
        audio_file = serializer.validated_data.get('audio')
        transcription = None
        if audio_file:
            audio_path = _save_uploaded_audio(audio_file)
            try:
                result = orch.transcribe_audio(audio_path)
                transcription = result.get('text', '')
                user_text = transcription
            finally:
                os.unlink(audio_path)

        if not user_text:
            return Response(
                {"error": "No usable input. Provide text or clear audio."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check toxicity
        toxicity = orch.check_toxicity(user_text)

        # Save user message
        ChatMessage.objects.create(
            session=session, role='user', content=user_text
        )

        # Get AI response
        ai_response = orch.chat(user_text, difficulty=session.difficulty)

        # Save AI message
        ChatMessage.objects.create(
            session=session, role='ai', content=ai_response
        )

        response_data = {
            "user_text": user_text,
            "ai_response": ai_response,
            "toxicity": toxicity,
        }
        if transcription is not None:
            response_data["transcription"] = transcription

        return Response(response_data, status=status.HTTP_200_OK)


class ChatHistoryView(APIView):
    """Get chat history for the active session."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        session = _get_active_session(request.user)
        if not session:
            return Response(
                {"error": "No active session found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        messages = session.messages.all()
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ── End Session ──────────────────────────────────────────────────

class EndSessionView(APIView):
    """End the active session and generate an evaluation report."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        session = _get_active_session(request.user)
        if not session:
            return Response(
                {"error": "No active session to end"},
                status=status.HTTP_404_NOT_FOUND,
            )

        orch = get_orchestrator()

        # Stop proctoring if active
        proctoring_summary = None
        if session.enable_proctoring:
            try:
                proctoring_summary = orch.stop_proctoring()
            except Exception as e:
                logger.warning(f"Proctoring stop failed: {e}")

        # Build chat history for evaluator
        messages = session.messages.all()
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        # Generate evaluation report
        report = None
        try:
            report = orch.generate_report(history=history)
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            report = {"error": str(e)}

        # Update session
        session.status = 'completed'
        session.ended_at = timezone.now()
        session.evaluation_report = report
        session.save()

        # Reset orchestrator state
        orch.reset_chat()

        response_data = {
            "session_id": session.session_id,
            "status": "completed",
            "evaluation_report": report,
        }
        if proctoring_summary:
            response_data["proctoring_summary"] = proctoring_summary

        return Response(response_data, status=status.HTTP_200_OK)


# ── TTS ──────────────────────────────────────────────────────────

class TTSView(APIView):
    """Synthesize text to speech and return the audio file."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TTSInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        text = serializer.validated_data['text']
        orch = get_orchestrator()

        audio_path = orch.synthesize_audio(text)
        if not audio_path or not os.path.exists(audio_path):
            return Response(
                {"error": "TTS synthesis failed. Engine may not be available."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return FileResponse(
            open(audio_path, 'rb'),
            content_type='audio/wav',
            as_attachment=True,
            filename='tts_output.wav',
        )
