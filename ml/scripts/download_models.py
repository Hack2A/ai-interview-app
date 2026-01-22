import os
import sys
from pathlib import Path
from huggingface_hub import hf_hub_download

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"

LLM_REPO = "bartowski/Meta-Llama-3-8B-Instruct-GGUF"
LLM_FILENAME = "Meta-Llama-3-8B-Instruct-Q4_K_M.gguf"

TTS_REPO = "rhasspy/piper-voices"
TTS_FILE_ONNX = "en/en_US/ryan/medium/en_US-ryan-medium.onnx"
TTS_FILE_JSON = "en/en_US/ryan/medium/en_US-ryan-medium.onnx.json"

def download_file(repo_id, filename, local_dir, subfolder=None):
    print(f"Checking {filename}...")
    try:
        file_path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            subfolder=subfolder,
            local_dir=local_dir,
            local_dir_use_symlinks=False
        )
        print(f"Success: {file_path}")
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
        sys.exit(1)

def main():
    print("--- BeaverAI Model Downloader ---")

    llm_dir = MODELS_DIR / "llm"
    llm_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n[1/3] Downloading LLM (Brain)...")
    download_file(LLM_REPO, LLM_FILENAME, llm_dir)
    
    tts_dir = MODELS_DIR / "tts"
    tts_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[2/3] Downloading TTS Model (Voice)...")
    download_file(TTS_REPO, TTS_FILE_ONNX, tts_dir)
    
    print(f"\n[3/3] Downloading TTS Config...")
    download_file(TTS_REPO, TTS_FILE_JSON, tts_dir)

    print("\nAll models downloaded successfully.")
    print(f"Location: {MODELS_DIR}")

if __name__ == "__main__":
    main()