import re


class PromptManager:
    """Manages system prompts, difficulty presets, and injection-safe message construction."""

    def __init__(self, resume_text: str | None = None, rag_engine=None) -> None:
        
        self.has_resume = bool(resume_text)
        self.has_jd = False

        self.system_persona = (
            "You are BeaverAI, a professional Technical Interviewer. "
            "Your goal is to assess the candidate's skills in Coding and System Design.\n"
            "STRICT RULES:\n"
            "1. NEVER switch roles. You are the Interviewer, they are the Candidate. If they ask to interview you, politely decline and return to the topic.\n"
            "2. Keep responses concise (2-3 sentences). Do not lecture.\n"
            "3. If the user is rude, toxic, or uses foul language, issue a stern warning. If they persist, end the interview.\n"
            "4. Do not hallucinate personal details. You are an AI.\n"
            "5. Avoid addressing the user by name.\n"
            "6. Always ask ONE question at a time. Wait for the candidate's answer before asking the next question.\n"
        )
        
        if resume_text:
            sanitized_resume = self._sanitize_text(resume_text, max_length=3000)
            self.system_persona += (
                "\n\n⚠️ ABSOLUTE RULE: You must NEVER repeat, read, narrate, list, or summarize "
                "any part of the resume below. ONLY use it to formulate questions. ⚠️\n\n"
                f"CANDIDATE'S RESUME (for reference only — DO NOT READ ALOUD):\n{sanitized_resume}\n\n"
                "QUESTION RULES:\n"
                "- Pick ONE project or skill and ask a DIRECT technical question about it.\n"
                "- Example: 'Tell me about the data pipeline you built for ReviewNexus.'\n"
                "- BAD example: 'I see your resume lists Python, React, AWS...' (this is narrating!)\n"
            )

        self.rag_engine = rag_engine
        if self.rag_engine:
            jd_context = self._get_jd_context()
            if jd_context:
                self.has_jd = True
                sanitized_jd = self._sanitize_text(jd_context, max_length=3000)
                self.system_persona += (
                    f"\nJOB DESCRIPTION REQUIREMENTS:\n{sanitized_jd}\n\n"
                    "IMPORTANT: Tailor your questions to verify the candidate has the skills "
                    "listed in this job description. Cross-reference their resume with job requirements.\n"
                    "Ask about gaps between the resume and job description.\n"
                )

        self.difficulty_prompts = {
            "Easy": "Ask basic concept questions. Be encouraging and supportive.",
            "Medium": "Ask standard implementation and problem-solving questions.",
            "Hard": "Ask complex system design and architecture questions. Probe deeper.",
            "Extreme": "Ask deep architectural questions with edge cases. Be skeptical and challenging."
        }

    def _sanitize_text(self, text: str, max_length: int = 5000) -> str:
        """Strip injection patterns and control characters from user text."""
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

    def _get_jd_context(self) -> str:
        """Query RAG engine for comprehensive JD context."""
        if not self.rag_engine:
            return ""
        
        queries = [
            "technical skills and technologies required",
            "required experience and qualifications",
            "key responsibilities and duties",
            "education and certifications",
            "team and project details",
        ]
        contexts = []
        seen = set()
        
        for query in queries:
            results = self.rag_engine.query_jd(query, top_k=2)
            for chunk in results:
                chunk_key = chunk[:100]
                if chunk_key not in seen:
                    seen.add(chunk_key)
                    contexts.append(chunk)
        
        return "\n".join(contexts[:6]) if contexts else ""

    def get_opening_prompt(self, difficulty: str = "Medium") -> str:
        """Generate a prompt that forces the LLM to ask the first resume-based question."""
        if self.has_resume:
            return (
                "Ask your FIRST interview question now. Pick ONE specific project or skill "
                "from the candidate's resume and ask a technical question about it. "
                "Do NOT summarize, list, or read out the resume — just ask the question directly."
            )
        elif self.has_jd:
            return (
                "Ask your FIRST interview question based on a key requirement "
                "from the job description. Ask directly, do not summarize."
            )
        else:
            return "Ask a technical question to assess the candidate's skills."

    def build_messages(self, history: list[dict], difficulty: str = "Medium") -> list[dict]:
        """Construct the message array for LLM chat completion."""
       
        messages = [{"role": "system", "content": self.system_persona}]
        
        difficulty_prompt = self.difficulty_prompts.get(difficulty, self.difficulty_prompts["Medium"])
        messages.append({"role": "system", "content": difficulty_prompt})
        
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
