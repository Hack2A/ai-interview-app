import os
import sys
from pathlib import Path

print("="*60)
print("     BEAVERAI - MODEL DOWNLOADER")
print("="*60)

print("\n[1/4] Downloading spaCy English model...")
os.system("python -m spacy download en_core_web_sm")

print("\n[2/4] Downloading sentence-transformers model...")
try:
    from sentence_transformers import SentenceTransformer
    print("Loading sentence-transformers/all-MiniLM-L6-v2...")
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    print("✓ Sentence transformer model downloaded")
except Exception as e:
    print(f"✗ Failed to download sentence-transformers: {e}")

print("\n[3/4] Downloading emotion recognition model...")
try:
    from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2FeatureExtractor
    model_name = "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"
    print(f"Loading {model_name}...")
    feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(model_name)
    model = Wav2Vec2ForSequenceClassification.from_pretrained(model_name)
    print("✓ Emotion model downloaded")
except Exception as e:
    print(f"✗ Failed to download emotion model: {e}")

print("\n[4/4] Downloading Coqui TTS model...")
try:
    from TTS.api import TTS
    print("Loading tts_models/multilingual/multi-dataset/xtts_v2...")
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    print("✓ Coqui XTTS v2 downloaded")
except Exception as e:
    print(f"✗ Failed to download Coqui TTS: {e}")
    print("  (Will fallback to pyttsx3)")

print("\n" + "="*60)
print("Model download complete!")
print("="*60)
print("\nNote: ChromaDB and MediaPipe models will be downloaded")
print("automatically on first use.")