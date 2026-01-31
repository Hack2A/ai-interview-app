import re

class PromptManager:
    def __init__(self, resume_text=None, rag_engine=None):
        
        self.system_persona = (
            "You are BeaverAI, a professional Technical Interviewer. "
            "Your goal is to assess the candidate's skills in Coding and System Design.\n"
            "STRICT RULES:\n"
            "1. NEVER switch roles. You are the Interviewer, they are the Candidate. If they ask to interview you, politely decline and return to the topic.\n"
            "2. Keep responses concise (under 2 sentences). Do not lecture.\n"
            "3. If the user is rude, toxic, or uses foul language, issue a stern warning. If they persist, end the interview.\n"
            "4. Do not hallucinate personal details. You are an AI."
            "5. Avoid addressing the user by name.\n"
        )
        
        if resume_text:
            sanitized_resume = self._sanitize_text(resume_text, max_length=8000)
            self.system_persona += (
                f"\n\nCONTEXT: Use the candidate's resume below to ask specific questions.\n"
                f"RESUME DATA:\n{sanitized_resume}"
            )

        self.rag_engine = rag_engine
        if self.rag_engine:
            jd_context = self._get_jd_context()
            if jd_context:
                sanitized_jd = self._sanitize_text(jd_context, max_length=2000)
                self.system_persona += (
                    f"\n\nJOB REQUIREMENTS:\n{sanitized_jd}\n"
                    "Ask questions to verify the candidate has these specific skills and experiences."
                )

        self.difficulty_prompts = {
            "Easy": "Ask basic concept questions. Be encouraging.",
            "Medium": "Ask standard implementation questions.",
            "Hard": "Ask complex system design questions.",
            "Extreme": "Ask deep architectural questions. Be skeptical."
        }
    
    def _sanitize_text(self, text: str, max_length: int = 5000) -> str:
        if not text:
            return ""
        
        text = text[:max_length]
        
        injection_patterns = [
            r'(?i)(ignore|disregard|forget)\s+(all\s+)?(previous|prior|above)\s+(instructions?|prompts?|commands?)',
            r'(?i)system\s*:',
            r'(?i)assistant\s*:',
            r'(?i)user\s*:',
            r'(?i)you\s+are\s+now',
            r'(?i)new\s+instructions?',
            r'(?i)act\s+as',
            r'(?i)pretend\s+to\s+be',
            r'(?i)roleplay',
        ]
        
        for pattern in injection_patterns:
            text = re.sub(pattern, '[REDACTED]', text)
        
        control_chars = ''.join(chr(i) for i in range(32) if i not in [9, 10, 13])
        text = text.translate(str.maketrans('', '', control_chars))
        
        return text.strip()

    def _get_jd_context(self):
        if not self.rag_engine:
            return ""
        
        queries = ["technical skills", "required experience", "key responsibilities", "qualifications"]
        contexts = []
        
        for query in queries:
            results = self.rag_engine.query_jd(query, top_k=1)
            if results:
                contexts.append(results[0])
        
        return "\n".join(contexts[:3]) if contexts else ""

    def build_messages(self, history, difficulty="Medium"):
       
        messages = [{"role": "system", "content": self.system_persona}]
        if history:
            sanitized_history = []
            for msg in history[-20:]:
                sanitized_msg = {
                    "role": msg.get("role", "user"),
                    "content": self._sanitize_text(msg.get("content", ""), max_length=5000)
                }
                sanitized_history.append(sanitized_msg)
            messages.extend(sanitized_history)
            
        
        return messages
