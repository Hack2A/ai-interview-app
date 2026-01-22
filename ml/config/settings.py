import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
TRANSCRIPTS_DIR = BASE_DIR / "data" / "transcripts"


LLM_MODEL_NAME = "Meta-Llama-3-8B-Instruct-Q4_K_M.gguf" 
LLM_MODEL_PATH = MODELS_DIR / "llm" / LLM_MODEL_NAME

CONTEXT_SIZE = 4096
N_THREADS = 4
N_GPU_LAYERS = -1


STT_MODEL_SIZE = "base.en"
STT_DEVICE = "cpu"


TTS_MODEL_NAME = "en_US-ryan-medium.onnx"
TTS_MODEL_PATH = MODELS_DIR / "tts" / "en" / "en_US" / "ryan" / "medium" / TTS_MODEL_NAME