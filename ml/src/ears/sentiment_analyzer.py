import torch
import numpy as np
from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2FeatureExtractor
import librosa
import numpy as np
from config import settings
import logging

logger = logging.getLogger("SentimentAnalyzer")

class SentimentAnalyzer:
    def __init__(self):
        try:
            logger.info("Loading emotion recognition model...")
            self.feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(
                settings.EMOTION_MODEL_NAME
            )
            self.model = Wav2Vec2ForSequenceClassification.from_pretrained(
                settings.EMOTION_MODEL_NAME
            )
            self.emotion_labels = ["angry", "disgust", "fear", "happy", "neutral", "sad"]
            logger.info("Emotion model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load emotion model: {e}")
            self.model = None
    
    def analyze_emotion(self, audio_path):
        if not self.model:
            return {"neutral": 1.0}
        
        try:
            import soundfile as sf
            
            waveform, sample_rate = sf.read(audio_path, dtype='float32')
            
            
            duration = len(waveform) / sample_rate
            if duration < 1.0:
                logger.warning(f"Audio too short ({duration:.2f}s), skipping emotion analysis")
                return {"neutral": 1.0}
            
            if len(waveform.shape) > 1:
                waveform = np.mean(waveform, axis=1)
            
            if sample_rate != 16000:
                import librosa
                waveform = librosa.resample(waveform, orig_sr=sample_rate, target_sr=16000)
            
            # Ensure audio has sufficient energy
            energy = np.sqrt(np.mean(waveform ** 2))
            if energy < 0.001:
                logger.warning(f"Audio has very low energy ({energy:.6f}), likely silence")
                return {"neutral": 1.0}
            
            inputs = self.feature_extractor(
                waveform,
                sampling_rate=16000,
                return_tensors="pt",
                padding=True
            )
            
            with torch.no_grad():
                logits = self.model(**inputs).logits
                probs = torch.nn.functional.softmax(logits, dim=-1)[0]
            
            # Validate that model is producing meaningful predictions
            max_prob = float(probs.max())
            if max_prob < 0.2:  # All probabilities roughly equal means model isn't working
                logger.warning(f"Model predictions seem random (max prob: {max_prob:.3f})")
                return {"neutral": 1.0}
            
            emotions = {}
            for idx, label in enumerate(self.emotion_labels):
                emotions[label] = float(probs[idx])
            
            logger.debug(f"Emotion analysis: {emotions}")
            return emotions
        except Exception as e:
            logger.error(f"Emotion analysis failed: {e}")
            return {"neutral": 1.0}
    
    def calculate_speech_metrics(self, audio_path, transcript):
        metrics = {}
        
        try:
            y, sr = librosa.load(audio_path, sr=16000)
            
            duration = librosa.get_duration(y=y, sr=sr)
            
            word_count = len(transcript.split())
            wpm = (word_count / duration) * 60 if duration > 0 else 0
            metrics["wpm"] = round(wpm, 1)
            
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            pitch_values = pitches[pitches > 0]
            
            if len(pitch_values) > 1:
                jitter = np.std(pitch_values) / (np.mean(pitch_values) + 1e-6)
                metrics["jitter"] = float(round(jitter, 4))
            else:
                metrics["jitter"] = 0.0
            
            rms = librosa.feature.rms(y=y)[0]
            if len(rms) > 1:
                shimmer = np.std(rms) / (np.mean(rms) + 1e-6)
                metrics["shimmer"] = float(round(shimmer, 4))
            else:
                metrics["shimmer"] = 0.0
            
        except Exception as e:
            logger.error(f"Speech metrics calculation failed: {e}")
            metrics = {"wpm": 0, "jitter": 0, "shimmer": 0}
        
        return metrics
    
    def detect_fillers(self, transcript):
        text_lower = transcript.lower()
        filler_count = {}
        total_fillers = 0
        
        for filler in settings.FILLER_WORDS:
            count = text_lower.count(filler)
            if count > 0:
                filler_count[filler] = count
                total_fillers += count
        
        return {
            "total_fillers": total_fillers,
            "filler_breakdown": filler_count
        }
    
    def analyze_full(self, audio_path, transcript):
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
            "confidence_score": max(0, min(1, confidence_score))
        }
