from TTS.api import TTS
import numpy as np
import sounddevice as sd
import logging
from pathlib import Path
from config import settings

logger = logging.getLogger("CoquiTTS")

class CoquiTTSEngine:
    def __init__(self):
        try:
            logger.info("Loading Coqui XTTS v2 model...")
            self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
            
            if settings.VOICE_CLONE_SAMPLE and hasattr(settings.VOICE_CLONE_SAMPLE, 'exists'):
                voice_sample = Path(settings.VOICE_CLONE_SAMPLE)
                if voice_sample.exists():
                    self.speaker_wav = str(voice_sample)
                    logger.info(f"Using voice clone sample: {self.speaker_wav}")
                else:
                    self.speaker_wav = None
                    logger.warning("Voice clone sample not found, using default voice")
            else:
                self.speaker_wav = None
                logger.warning("Voice clone sample not configured")
            
            self.sample_rate = 24000
            logger.info("Coqui TTS loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Coqui TTS: {e}")
            raise
    
    def speak(self, text, language="en"):
        try:
            if self.speaker_wav:
                wav = self.tts.tts(
                    text=text,
                    speaker_wav=self.speaker_wav,
                    language=language
                )
            else:
                wav = self.tts.tts(text=text, language=language)
            
            wav_array = np.array(wav, dtype=np.float32)
            
            sd.play(wav_array, self.sample_rate)
            sd.wait()
            
            return wav_array
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            return None
    
    def speak_stream(self, text_chunks, language="en"):
        for chunk in text_chunks:
            if isinstance(chunk, str):
                self.speak(chunk, language)
            else:
                for subchunk in chunk:
                    self.speak(subchunk, language)
