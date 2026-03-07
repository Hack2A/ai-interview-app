import re
import logging
from typing import Optional

import torch
import numpy as np
import librosa
from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2FeatureExtractor

from config import settings

logger = logging.getLogger("SentimentAnalyzer")

SAMPLE_RATE = 16000
MIN_AUDIO_DURATION = 1.0
MIN_ENERGY_THRESHOLD = 0.001
MIN_PREDICTION_CONFIDENCE = 0.2


class SentimentAnalyzer:
    """Analyzes candidate speech for emotion, fluency, and filler words."""

    def __init__(self) -> None:
        self.feature_extractor: Optional[Wav2Vec2FeatureExtractor] = None
        self.model: Optional[Wav2Vec2ForSequenceClassification] = None
        self.emotion_labels: list[str] = ["angry", "disgust", "fear", "happy", "neutral", "sad"]

        try:
            logger.info("Loading emotion recognition model...")
            self.feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(
                settings.EMOTION_MODEL_NAME
            )
            self.model = Wav2Vec2ForSequenceClassification.from_pretrained(
                settings.EMOTION_MODEL_NAME
            )
            logger.info("Emotion model loaded successfully")
        except (OSError, ValueError, RuntimeError) as e:
            logger.error(f"Failed to load emotion model: {e}")
            self.feature_extractor = None
            self.model = None

    def analyze_emotion(self, audio_path: str) -> dict[str, float]:
        """Detect emotions from audio using Wav2Vec2."""
        if not self.model:
            return {"neutral": 1.0}

        try:
            import soundfile as sf

            waveform, sample_rate = sf.read(audio_path, dtype='float32')

            duration = len(waveform) / sample_rate
            if duration < MIN_AUDIO_DURATION:
                logger.warning(f"Audio too short ({duration:.2f}s), skipping emotion analysis")
                return {"neutral": 1.0}

            if len(waveform.shape) > 1:
                waveform = np.mean(waveform, axis=1)

            if sample_rate != SAMPLE_RATE:
                waveform = librosa.resample(waveform, orig_sr=sample_rate, target_sr=SAMPLE_RATE)

            energy = np.sqrt(np.mean(waveform ** 2))
            if energy < MIN_ENERGY_THRESHOLD:
                logger.warning(f"Audio has very low energy ({energy:.6f}), likely silence")
                return {"neutral": 1.0}

            inputs = self.feature_extractor(
                waveform,
                sampling_rate=SAMPLE_RATE,
                return_tensors="pt",
                padding=True
            )

            with torch.no_grad():
                logits = self.model(**inputs).logits
                probs = torch.nn.functional.softmax(logits, dim=-1)[0]

            if float(probs.max()) < MIN_PREDICTION_CONFIDENCE:
                logger.warning(f"Model predictions seem random (max prob: {float(probs.max()):.3f})")
                return {"neutral": 1.0}

            emotions = {label: float(probs[idx]) for idx, label in enumerate(self.emotion_labels)}
            logger.debug(f"Emotion analysis: {emotions}")
            return emotions
        except (OSError, RuntimeError, ValueError) as e:
            logger.error(f"Emotion analysis failed: {e}")
            return {"neutral": 1.0}

    def calculate_speech_metrics(self, audio_path: str, transcript: str) -> dict[str, float]:
        """Calculate WPM, jitter, and shimmer from audio."""
        try:
            y, sr = librosa.load(audio_path, sr=SAMPLE_RATE)
            duration = librosa.get_duration(y=y, sr=sr)

            word_count = len(transcript.split())
            wpm = (word_count / duration) * 60 if duration > 0 else 0

            pitches, _ = librosa.piptrack(y=y, sr=sr)
            pitch_values = pitches[pitches > 0]
            jitter = float(np.std(pitch_values) / (np.mean(pitch_values) + 1e-6)) if len(pitch_values) > 1 else 0.0

            rms = librosa.feature.rms(y=y)[0]
            shimmer = float(np.std(rms) / (np.mean(rms) + 1e-6)) if len(rms) > 1 else 0.0

            return {
                "wpm": round(wpm, 1),
                "jitter": round(jitter, 4),
                "shimmer": round(shimmer, 4),
            }
        except (OSError, RuntimeError, ValueError) as e:
            logger.error(f"Speech metrics calculation failed: {e}")
            return {"wpm": 0, "jitter": 0, "shimmer": 0}

    def detect_fillers(self, transcript: str) -> dict:
        """Count filler words in transcript."""
        text_lower = transcript.lower()
        filler_count: dict[str, int] = {}
        total_fillers = 0

        for filler in settings.FILLER_WORDS:
            pattern = r'\b' + re.escape(filler) + r'\b'
            count = len(re.findall(pattern, text_lower))
            if count > 0:
                filler_count[filler] = count
                total_fillers += count

        return {"total_fillers": total_fillers, "filler_breakdown": filler_count}

    def analyze_full(self, audio_path: str, transcript: str) -> dict:
        """Run full sentiment pipeline: emotion + speech metrics + fillers."""
        emotions = self.analyze_emotion(audio_path)
        speech_metrics = self.calculate_speech_metrics(audio_path, transcript)
        fillers = self.detect_fillers(transcript)

        dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0]

        confidence_score = 0.5
        if emotions.get("happy", 0) + emotions.get("neutral", 0) > 0.7:
            confidence_score = 0.7
        if speech_metrics.get("jitter", 0) > 0.05 or fillers["total_fillers"] > 5:
            confidence_score -= 0.2

        return {
            "emotions": emotions,
            "dominant_emotion": dominant_emotion,
            "speech_metrics": speech_metrics,
            "fillers": fillers,
            "confidence_score": max(0, min(1, confidence_score)),
        }
