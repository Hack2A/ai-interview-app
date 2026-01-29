import sys
import logging
from llama_cpp import Llama
from config import settings
from src.brain.prompt_manager import PromptManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LLMEngine")

class LLMEngine:
    def __init__(self, resume_text=None, rag_engine=None):
        
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

        self.prompt_manager = PromptManager(resume_text=resume_text, rag_engine=rag_engine)
        self.history = []


    def generate_stream(self, user_input, difficulty="Medium"):
        
        self.history.append({"role": "user", "content": user_input})
        messages = self.prompt_manager.build_messages(self.history, difficulty)

        logger.info(f"Generating LLM response for: {user_input[:50]}...")
        
        try:
            stream = self.model.create_chat_completion(
                messages=messages,
                max_tokens=200,
                temperature=0.7,
                stop=["User:", "[INSTRUCTION]"],
                stream=True 
            )
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            yield "I apologize, I'm having technical difficulties. Could you please repeat that?"
            return

        buffer = ""
        full_response = ""
        token_count = 0
        
        for chunk in stream:
            if "content" in chunk["choices"][0]["delta"]:
                token = chunk["choices"][0]["delta"]["content"]
                buffer += token
                full_response += token
                token_count += 1
                
                
                if any(x in token for x in [".", "?", "!", "\n"]):
                    yield buffer
                    buffer = ""
        
        logger.info(f"Generated {token_count} tokens, {len(full_response)} characters")
       
        if buffer:
            yield buffer

        
        self.history.append({"role": "assistant", "content": full_response})
    
    def get_history(self):
        return self.history