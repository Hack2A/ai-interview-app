import logging
import sys
import time
from typing import Generator

from llama_cpp import Llama

from config import settings
from src.brain.prompt_manager import PromptManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LLMEngine")

MAX_RESPONSE_TOKENS = 500
LLM_TEMPERATURE = 0.7
STREAM_TIMEOUT_SECONDS = 30


class LLMEngine:
    """Local LLM inference engine using llama.cpp."""

    def __init__(self, resume_text: str | None = None, rag_engine=None,
                 interview_type: str = "technical") -> None:
        
        try:
            logger.info(f"Loading LLM from: {settings.LLM_MODEL_PATH}")
            self.model = Llama(
                model_path=str(settings.LLM_MODEL_PATH),
                n_ctx=settings.CONTEXT_SIZE,
                n_threads=settings.N_THREADS,
                verbose=False,
                chat_format="llama-3"
            )
            logger.info("LLM loaded successfully")
        except Exception as e:
            logger.error(f"CRITICAL ERROR: Failed to load LLM model: {e}")
            logger.error(f"Model path: {settings.LLM_MODEL_PATH}")
            logger.error("Please ensure the model file exists in the models/llm directory")
            raise Exception(f"LLM initialization failed: {e}")

        self.prompt_manager = PromptManager(
            resume_text=resume_text, rag_engine=rag_engine,
            interview_type=interview_type
        )
        self.history = []
        self._is_first_call = True


    def generate_stream(self, user_input: str, difficulty: str = "Medium", question_context: dict | None = None) -> Generator[str, None, None]:
        """Stream LLM response token-by-token, yielding sentence fragments."""
        
        self.history.append({"role": "user", "content": user_input})
        messages = self.prompt_manager.build_messages(self.history, difficulty, question_context=question_context)

        logger.info(f"Generating LLM response for: {user_input[:50]}...")
        
        try:
            stream = self.model.create_chat_completion(
                messages=messages,
                max_tokens=MAX_RESPONSE_TOKENS,
                temperature=LLM_TEMPERATURE,
                stop=["User:", "[INSTRUCTION]"],
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

                if "content" in chunk["choices"][0]["delta"]:
                    token = chunk["choices"][0]["delta"]["content"]
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

    @property
    def llm(self) -> Llama:
        """Access the underlying Llama model."""
        return self.model

    def get_history(self) -> list[dict]:
        """Return conversation history."""
        return self.history