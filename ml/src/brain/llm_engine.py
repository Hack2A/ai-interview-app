import sys
import logging
from llama_cpp import Llama
from beaverAI.ml.config import settings
from beaverAI.ml.src.brain.prompt_manager import PromptManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LLMEngine")

class LLMEngine:
    def __init__(self, resume_text=None):
        
        try:
            self.model = Llama(
                model_path=str(settings.LLM_MODEL_PATH),
                n_ctx=settings.CONTEXT_SIZE,
                n_threads=settings.N_THREADS,
                verbose=False,
                chat_format="llama-3"
            )
        except Exception as e:
            sys.exit(1)

        self.prompt_manager = PromptManager(resume_text=resume_text)
        self.history = []

    def generate_stream(self, user_input, difficulty="Medium"):
        
        self.history.append({"role": "user", "content": user_input})
        messages = self.prompt_manager.build_messages(self.history, difficulty)

        
        stream = self.model.create_chat_completion(
            messages=messages,
            max_tokens=512,
            temperature=0.7,
            stop=["User:", "[INSTRUCTION]"],
            stream=True 
        )

        buffer = ""
        full_response = ""
        
        for chunk in stream:
            if "content" in chunk["choices"][0]["delta"]:
                token = chunk["choices"][0]["delta"]["content"]
                buffer += token
                full_response += token
                
                
                if any(x in token for x in [".", "?", "!", "\n"]):
                    yield buffer
                    buffer = ""
        
       
        if buffer:
            yield buffer

        
        self.history.append({"role": "assistant", "content": full_response})
    
    def get_history(self):
        return self.history