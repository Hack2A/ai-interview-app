import json
import logging
import time
import threading
from typing import Generator

import requests

from config import settings
from src.brain.prompt_manager import PromptManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LLMEngine")

MAX_RESPONSE_TOKENS = 150
LLM_TEMPERATURE = 0.7
STREAM_TIMEOUT_SECONDS = 120  # Gemma4 thinks before responding — give it time

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_CHAT_URL = f"{OLLAMA_BASE_URL}/api/chat"
OLLAMA_MODEL = "gemma4"
OLLAMA_CAREER_MODEL = "career-llama3:latest"  # Meta-Llama-3-8B for career features


class OllamaClient:
    """Thin wrapper around Ollama's REST API, compatible with the llama.cpp interface."""

    def __init__(self, model_name: str = OLLAMA_MODEL) -> None:
        self.model_name = model_name

        # Verify connectivity
        try:
            r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            r.raise_for_status()
            models = [m["name"] for m in r.json().get("models", [])]
            logger.info(f"Connected to Ollama. Available models: {models}")
            if not any(model_name in m for m in models):
                logger.warning(f"Model '{model_name}' not found in Ollama. Available: {models}")
        except Exception as e:
            logger.error(f"Cannot connect to Ollama at {OLLAMA_BASE_URL}: {e}")
            raise

    def create_chat_completion(self, messages, max_tokens=MAX_RESPONSE_TOKENS,
                               temperature=LLM_TEMPERATURE, stop=None, stream=False,
                               response_format=None, keep_alive=None, **kwargs):
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": stream,
            "think": False,  # Disable Gemma4 thinking — interview needs fast direct answers
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
                "num_ctx": kwargs.get("num_ctx", 2048),
            }
        }

        if stop:
            payload["options"]["stop"] = stop
        if response_format:
            payload["format"] = "json"
        if keep_alive is not None:
            payload["keep_alive"] = keep_alive

        if stream:
            return self._stream_generator(payload)
        else:
            return self._sync_request(payload)

    def _stream_generator(self, payload):
        """Yield streaming chunks with retry logic for VRAM contention 500s."""
        for attempt in range(3):
            try:
                with requests.post(OLLAMA_CHAT_URL, json=payload, stream=True, timeout=600) as response:
                    if response.status_code == 500 and attempt < 2:
                        logger.warning(f"Ollama stream 500 on attempt {attempt+1}, retrying in 2s...")
                        try:
                            import torch; torch.cuda.empty_cache()
                        except Exception:
                            pass
                        time.sleep(2.0)
                        continue
                    response.raise_for_status()
                    for line in response.iter_lines():
                        if line:
                            try:
                                chunk = json.loads(line)
                                yield chunk
                                if chunk.get("done"):
                                    break
                            except json.JSONDecodeError:
                                logger.warning(f"Failed to decode streaming chunk: {line}")
                                continue
                    return  # success — stop retry loop
            except requests.exceptions.HTTPError as e:
                if e.response is not None and e.response.status_code == 500 and attempt < 2:
                    logger.warning(f"Ollama stream HTTPError 500 on attempt {attempt+1}, retrying in 2s...")
                    try:
                        import torch; torch.cuda.empty_cache()
                    except Exception:
                        pass
                    time.sleep(2.0)
                    continue
                logger.error(f"Ollama streaming request failed: {e}")
                raise
            except requests.exceptions.RequestException as e:
                logger.error(f"Ollama streaming request connection error: {e}")
                if attempt < 2:
                    try:
                        import torch; torch.cuda.empty_cache()
                    except Exception:
                        pass
                    time.sleep(2.0)
                    continue
                raise

    def _sync_request(self, payload):
        """Non-streaming request with retry logic for VRAM contention 500s."""
        for attempt in range(3):
            try:
                r = requests.post(OLLAMA_CHAT_URL, json=payload, timeout=600)
                if r.status_code == 500 and attempt < 2:
                    logger.warning(f"Ollama sync 500 on attempt {attempt+1}, retrying in 2s...")
                    try:
                        import torch; torch.cuda.empty_cache()
                    except Exception:
                        pass
                    time.sleep(2.0)
                    continue
                r.raise_for_status()
                data = r.json()
                # Convert Ollama response to llama.cpp-compatible format
                return {
                    "choices": [{
                        "message": {
                            "role": data.get("message", {}).get("role", "assistant"),
                            "content": data.get("message", {}).get("content", ""),
                        }
                    }]
                }
            except requests.exceptions.HTTPError as e:
                if e.response is not None and e.response.status_code == 500 and attempt < 2:
                    logger.warning(f"Ollama sync HTTPError 500 on attempt {attempt+1}, retrying in 2s...")
                    try:
                        import torch; torch.cuda.empty_cache()
                    except Exception:
                        pass
                    time.sleep(2.0)
                    continue
                logger.error(f"Ollama sync request failed: {e}")
                raise
            except requests.exceptions.RequestException as e:
                logger.error(f"Ollama sync connection error: {e}")
                if attempt < 2:
                    try:
                        import torch; torch.cuda.empty_cache()
                    except Exception:
                        pass
                    time.sleep(2.0)
                    continue
                raise

    def unload_model(self):
        """Unload model from VRAM."""
        try:
            requests.post(OLLAMA_CHAT_URL, json={
                "model": self.model_name,
                "messages": [],
                "keep_alive": 0
            }, timeout=10)
            logger.info(f"Unloaded {self.model_name} from Ollama VRAM")
        except Exception as e:
            logger.warning(f"Failed to unload model: {e}")


class LLMEngine:
    """LLM inference engine using Ollama backend."""

    def __init__(self, resume_text: str | None = None, rag_engine=None,
                 interview_type: str = "technical") -> None:

        try:
            logger.info(f"Connecting to Ollama model: {OLLAMA_MODEL}")
            self.model = OllamaClient(model_name=OLLAMA_MODEL)
            logger.info("Ollama LLM connected successfully")
        except Exception as e:
            logger.error(f"CRITICAL ERROR: Failed to connect to LLM backend: {e}")
            raise Exception(f"LLM initialization failed: {e}")

        self.prompt_manager = PromptManager(
            resume_text=resume_text, rag_engine=rag_engine,
            interview_type=interview_type
        )
        self.history = []
        self._is_first_call = True
        self.lock = threading.Lock()


    def generate_stream(self, user_input: str, difficulty: str = "Medium", question_context: dict | None = None) -> Generator[str, None, None]:
        """Stream LLM response token-by-token, yielding sentence fragments."""
        
        self.history.append({"role": "user", "content": user_input})
        messages = self.prompt_manager.build_messages(self.history, difficulty, question_context=question_context)

        logger.info(f"Generating LLM response for: {user_input[:50]}...")
        
        with self.lock:
            try:
                stream = self.model.create_chat_completion(
                    messages=messages,
                    max_tokens=MAX_RESPONSE_TOKENS,
                    temperature=LLM_TEMPERATURE,
                    stop=["User:", "[INSTRUCTION]", "STRICT RULES:", "CANDIDATE'S RESUME", "QUESTION FOCUS:", "ABSOLUTE RULE:"],
                    stream=True,
                )
            except Exception as e:
                logger.error(f"LLM generation error: {e}")
                yield "I apologize, I'm having technical difficulties. Could you please repeat that?"
                return

            buffer = ""
            full_response = ""
            token_count = 0
            
            stream_start = time.time()
            # First call is always slow (processing full system prompt), skip timeout
            apply_timeout = not self._is_first_call
            self._is_first_call = False

            try:
                for chunk in stream:
                    # Timeout guard (skip on first call)
                    if apply_timeout and time.time() - stream_start > STREAM_TIMEOUT_SECONDS:
                        logger.warning(f"LLM stream timed out after {STREAM_TIMEOUT_SECONDS}s")
                        break

                    if "message" in chunk and "content" in chunk["message"]:
                        token = chunk["message"]["content"]
                        # Gemma4 is a thinking model — during the reasoning phase it sends
                        # empty content tokens. Skip them; only stream the actual response.
                        if not token:
                            continue
                        buffer += token
                        full_response += token
                        token_count += 1
                        
                        if any(x in token for x in [".", "?", "!", "\n"]):
                            yield buffer
                            buffer = ""
            except Exception as e:
                logger.error(f"Stream error: {e}", exc_info=True)
                if buffer:
                    yield buffer
                    buffer = ""
            
            logger.info(f"Generated {token_count} tokens, {len(full_response)} characters")
            
            if buffer:
                yield buffer

        self.history.append({"role": "assistant", "content": full_response})

    def shutdown(self):
        """Unload memory before exiting."""
        self.model.unload_model()

    @property
    def llm(self) -> OllamaClient:
        """Access the underlying Ollama client."""
        return self.model

    def get_history(self) -> list[dict]:
        """Return conversation history."""
        return self.history