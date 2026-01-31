import logging
from faster_whisper import WhisperModel
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("STTEngine")

class STTEngine:
    def __init__(self):
        logger.info(f"Loading Whisper model: {settings.STT_MODEL_SIZE}...")
        try:
            
            self.model = WhisperModel(
                settings.STT_MODEL_SIZE, 
                device=settings.STT_DEVICE, 
                compute_type="int8"
            )
            logger.info("Whisper Loaded Successfully.")
        except Exception as e:
            logger.error(f"Failed to load Whisper: {e}")
            raise e

    def transcribe(self, audio_path, language=None):
        MAX_AUDIO_SIZE = 25 * 1024 * 1024
        ALLOWED_EXTENSIONS = {'.wav', '.mp3', '.flac', '.m4a', '.ogg'}
        
        if not audio_path:
            return "", "en"
        
        from pathlib import Path
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
            
        segments, info = self.model.transcribe(
            str(audio_file), 
            language=language,
            beam_size=5,
            vad_filter=True, 
            vad_parameters=dict(min_silence_duration_ms=500)
        )

        text = " ".join([segment.text for segment in segments]).strip()
        text = text[:5000]
        detected_language = info.language if hasattr(info, 'language') else "en"
        return text, detected_language
