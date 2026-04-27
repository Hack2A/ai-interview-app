import logging
import subprocess
import tempfile
from pathlib import Path

from faster_whisper import WhisperModel
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("STTEngine")


def _get_ffmpeg_exe() -> str:
    """Get the ffmpeg executable path, preferring bundled imageio_ffmpeg over system."""
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return "ffmpeg"  # Fall back to system PATH


def _convert_to_wav(input_path: str) -> str | None:
    """Convert any audio file (especially WebM chunks) to WAV using ffmpeg.
    
    Browser MediaRecorder sends incomplete WebM streams that PyAV can't decode
    directly. ffmpeg handles these gracefully with -err_detect ignore_err.
    
    Returns path to the converted WAV file, or None on failure.
    """
    out_path = input_path + "_converted.wav"
    try:
        result = subprocess.run(
            [
                _get_ffmpeg_exe(), "-y",
                "-err_detect", "ignore_err",
                "-i", input_path,
                "-ar", "16000",   # Whisper expects 16kHz
                "-ac", "1",        # Mono
                "-f", "wav",
                out_path,
            ],
            capture_output=True,
            timeout=30,
        )
        if result.returncode == 0 and Path(out_path).stat().st_size > 0:
            return out_path
        logger.warning(f"ffmpeg conversion failed (rc={result.returncode}): {result.stderr.decode()[:200]}")
        return None
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        logger.warning(f"ffmpeg not available or timed out: {e}")
        return None


class STTEngine:
    """Speech-to-Text engine using Faster Whisper."""

    def __init__(self) -> None:
        logger.info(f"Loading Whisper model: {settings.STT_MODEL_SIZE}...")
        try:
            self.model = WhisperModel(
                settings.STT_MODEL_SIZE, 
                device=settings.STT_DEVICE, 
                compute_type="float16" if settings.STT_DEVICE == "cuda" else "int8"
            )
            logger.info("Whisper Loaded Successfully.")
        except Exception as e:
            logger.error(f"Failed to load Whisper: {e}")
            raise e

    def transcribe(self, audio_path: str, language: str | None = None) -> tuple[str, str]:
        """Transcribe audio file and return (text, detected_language)."""
        MAX_AUDIO_SIZE = 25 * 1024 * 1024
        ALLOWED_EXTENSIONS = {'.wav', '.mp3', '.flac', '.m4a', '.ogg', '.webm', '.weba'}
        
        if not audio_path:
            return "", "en"
        
        audio_file = Path(audio_path)
        
        if not audio_file.is_file():
            logger.warning(f"Audio file not found: {audio_path}")
            return "", "en"
        
        if audio_file.suffix.lower() not in ALLOWED_EXTENSIONS:
            logger.warning(f"Invalid audio format: {audio_file.suffix}")
            return "", "en"
        
        file_size = audio_file.stat().st_size
        if file_size > MAX_AUDIO_SIZE:
            logger.warning(f"Audio file too large: {file_size} bytes")
            return "", "en"
        
        if file_size == 0:
            logger.warning("Audio file is empty")
            return "", "en"

        # WebM from browser MediaRecorder is a chunked stream — convert to WAV first
        transcribe_path = str(audio_file)
        converted_path = None
        if audio_file.suffix.lower() in {'.webm', '.weba', '.ogg'}:
            converted_path = _convert_to_wav(str(audio_file))
            if converted_path:
                transcribe_path = converted_path
        
        try:
            segments, info = self.model.transcribe(
                transcribe_path,
                language=language,
                beam_size=5,
                vad_filter=True, 
                vad_parameters=dict(min_silence_duration_ms=500)
            )

            text = " ".join([segment.text for segment in segments]).strip()
            text = text[:5000]
            detected_language = info.language if hasattr(info, 'language') else "en"
            return text, detected_language
        except Exception as e:
            logger.exception(f"Transcription failed for {audio_path}: {e}")
            return "", "en"
        finally:
            # Clean up the temporary WAV conversion
            if converted_path:
                try:
                    Path(converted_path).unlink(missing_ok=True)
                except OSError:
                    pass
