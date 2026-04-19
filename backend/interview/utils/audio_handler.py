"""Audio file management utilities for the interview WebSocket pipeline.

Handles saving user audio blobs, copying TTS output to media storage,
generating servable URLs, and session cleanup.
"""

import logging
import os
import shutil
import uuid
from pathlib import Path

from django.conf import settings

logger = logging.getLogger('interview')

# Base directory for all interview audio files
AUDIO_ROOT = Path(settings.MEDIA_ROOT) / 'audio'


def _ensure_session_dir(session_id: str) -> Path:
    """Create and return the audio directory for a session."""
    session_dir = AUDIO_ROOT / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir


def save_audio_blob(audio_bytes: bytes, session_id: str,
                    suffix: str = '.webm') -> str:
    """Save raw audio bytes (from browser MediaRecorder) to disk.

    Args:
        audio_bytes: Raw audio data.
        session_id: Interview session identifier.
        suffix: File extension (default .webm for browser recordings).

    Returns:
        Absolute file path of the saved audio.
    """
    session_dir = _ensure_session_dir(session_id)
    filename = f"user_{uuid.uuid4().hex[:12]}{suffix}"
    file_path = session_dir / filename
    file_path.write_bytes(audio_bytes)
    logger.debug(f"Saved user audio: {file_path} ({len(audio_bytes)} bytes)")
    return str(file_path)


def save_tts_audio(source_path: str, session_id: str) -> str | None:
    """Copy a TTS-generated audio file into the session's media directory.

    Args:
        source_path: Absolute path to the TTS output file.
        session_id: Interview session identifier.

    Returns:
        Relative URL path (e.g. /media/audio/<session>/<file>.wav),
        or None if source doesn't exist.
    """
    if not source_path or not os.path.exists(source_path):
        logger.warning(f"TTS source not found: {source_path}")
        return None

    session_dir = _ensure_session_dir(session_id)
    ext = Path(source_path).suffix or '.wav'
    filename = f"ai_{uuid.uuid4().hex[:12]}{ext}"
    dest_path = session_dir / filename

    shutil.copy2(source_path, dest_path)
    logger.debug(f"Saved TTS audio: {dest_path}")

    # Return URL-safe relative path
    return get_audio_url(str(dest_path))


def get_audio_url(file_path: str) -> str:
    """Convert an absolute file path to a servable media URL.

    Args:
        file_path: Absolute path inside MEDIA_ROOT.

    Returns:
        URL path like /media/audio/<session>/<file>.wav
    """
    try:
        rel = Path(file_path).relative_to(settings.MEDIA_ROOT)
        return f"{settings.MEDIA_URL}{rel}"
    except ValueError:
        # File is outside MEDIA_ROOT — return as-is
        return file_path


def cleanup_session_audio(session_id: str) -> None:
    """Delete all audio files for a given session.

    Args:
        session_id: Interview session identifier.
    """
    session_dir = AUDIO_ROOT / session_id
    if session_dir.exists():
        shutil.rmtree(session_dir, ignore_errors=True)
        logger.info(f"Cleaned up audio for session {session_id[:8]}")
