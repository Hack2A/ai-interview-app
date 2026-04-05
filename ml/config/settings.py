import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
TRANSCRIPTS_DIR = BASE_DIR / "data" / "transcripts"


LLM_MODEL_NAME = "Meta-Llama-3-8B-Instruct-Q4_K_M.gguf" 
LLM_MODEL_PATH = MODELS_DIR / "llm" / LLM_MODEL_NAME

CONTEXT_SIZE = 4096
N_THREADS = 8
N_GPU_LAYERS = -1


STT_MODEL_SIZE = "small.en"
STT_DEVICE = "cuda"


TTS_MODEL_NAME = "en_US-ryan-medium.onnx"
TTS_MODEL_PATH = MODELS_DIR / "tts" / "en" / "en_US" / "ryan" / "medium" / TTS_MODEL_NAME

ENABLE_RAG = True
ENABLE_PROCTORING = True
ENABLE_SENTIMENT = True
ENABLE_ATS = True

JD_DIR = BASE_DIR / "data" / "job_descriptions"
CHROMADB_DIR = MODELS_DIR / "chromadb"
EMOTION_MODEL_NAME = "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"

PROCTORING_FPS = 5
PROCTORING_DISPLAY_FPS = 30
VIOLATION_THRESHOLD_SECONDS = 2  

# --- Proctoring Enhancements ---
ENABLE_OBJECT_DETECTION = True
ENABLE_MOUTH_ANALYSIS = True
ENABLE_EARPIECE_DETECTION = True
YOLO_MODEL_NAME = "yolov8n.pt"
YOLO_MODEL_PATH = MODELS_DIR / "yolo" / YOLO_MODEL_NAME
YOLO_CONFIDENCE_THRESHOLD = 0.45
MOUTH_OPEN_THRESHOLD = 0.35
RISK_WINDOW_SECONDS = 30
RISK_ALERT_THRESHOLDS = {"info": 0.3, "warning": 0.6, "critical": 0.85}

FILLER_WORDS = ["umm", "uh", "like", "you know", "so", "basically", "actually"]

USE_ADVANCED_TTS = False
DEFAULT_INTERVIEW_LANGUAGE = "en"
VOICE_CLONE_SAMPLE = MODELS_DIR / "voice_samples" / "interviewer.wav"

# --- Question Bank & RAG ---
QUESTION_BANK_PATH = BASE_DIR / "data" / "datasets" / "question_bank.json"
DATASETS_RAW_DIR = BASE_DIR / "data" / "datasets" / "raw"
ENABLE_QUESTION_BANK = True
ENABLE_PER_QUESTION_EVAL = True

# --- Voice AI Pipeline Enhancements ---
ENABLE_LOCAL_BARGE_IN = False  # Set to True if wearing headphones, False otherwise to prevent acoustic echo

# --- Scoring Weights ---
SCORING_WEIGHT_TECHNICAL = 0.50
SCORING_WEIGHT_CLARITY = 0.30
SCORING_WEIGHT_COMMUNICATION = 0.20
