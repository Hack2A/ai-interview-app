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
       
        if not audio_path:
            return "", "en"
            
        segments, info = self.model.transcribe(
            audio_path, 
            language=language,
            beam_size=5,
            vad_filter=True, 
            vad_parameters=dict(min_silence_duration_ms=500)
        )

        text = " ".join([segment.text for segment in segments]).strip()
        detected_language = info.language if hasattr(info, 'language') else "en"
        return text, detected_language
