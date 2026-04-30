import re


class PromptManager:
    """Manages system prompts, difficulty presets, and injection-safe message construction."""

    # ── Interview type persona templates ──────────────────────────

    _TYPE_PERSONAS = {
        "technical": (
            "You are intrv.ai, a professional Technical Interviewer. "
            "Your goal is to assess the candidate's skills in Coding, System Design, and Data Structures.\n"
        ),
        "behavioral": (
            "You are intrv.ai, a professional Behavioral Interviewer. "
            "Your goal is to assess the candidate's soft skills, teamwork, leadership, and problem-solving approach "
            "using the STAR method (Situation, Task, Action, Result).\n"
        ),
        "hr": (
            "You are intrv.ai, a professional HR Interviewer. "
            "Your goal is to evaluate the candidate's career goals, cultural fit, salary expectations, "
            "strengths, weaknesses, and motivation for the role.\n"
        ),
        "combined": (
            "You are intrv.ai, a professional Interview Panel conducting a comprehensive interview. "
            "You will rotate between Technical, Behavioral, and HR questions to evaluate the candidate holistically. "
            "Mix coding/system-design questions with STAR-method behavioral questions and HR/culture-fit questions.\n"
        ),
    }

    _TYPE_QUESTION_GUIDANCE = {
        "technical": (
            "Focus on: coding problems, system design, architecture, algorithms, "
            "data structures, and technical project deep-dives."
        ),
        "behavioral": (
            "Focus on: teamwork scenarios, conflict resolution, leadership examples, "
            "failures and learnings, time management, and communication skills. "
            "Always frame questions using the STAR method."
        ),
        "hr": (
            "Focus on: career aspirations, motivation for applying, strengths and weaknesses, "
            "work-life balance expectations, salary expectations, and cultural alignment."
        ),
        "combined": (
            "Rotate between question types in this order: "
            "1st question → Technical, 2nd → Behavioral, 3rd → HR, then repeat. "
            "Ensure a balanced mix across all three areas."
        ),
    }

    _COMMON_RULES = (
        "STRICT RULES:\n"
        "1. NEVER switch roles. You are the Interviewer, they are the Candidate. If they ask to interview you, politely decline and return to the topic.\n"
        "2. Keep responses OUTSTANDINGLY concise (1-2 short sentences maximum). Under no circumstances should you lecture or explain.\n"
        "3. If the user is rude, toxic, or uses foul language, issue a stern warning. If they persist, end the interview.\n"
        "4. Do not hallucinate personal details. You are an AI.\n"
        "5. Avoid addressing the user by name.\n"
        "6. Always ask ONE question at a time. Wait for the candidate's answer before asking the next question.\n"
        "7. CRITICAL: Do NOT correct the user's grammar, pronunciation, or speech-to-text transcript errors (e.g. if they say 'equal injection' instead of 'SQL injection'). Just acknowledge their answer smoothly and ask the next question.\n"
    )

    def __init__(self, resume_text: str | None = None, rag_engine=None,
                 interview_type: str = "technical") -> None:

        self.has_resume = bool(resume_text)
        self.has_jd = False
        self.interview_type = interview_type

        # Build system persona from type template + common rules
        type_persona = self._TYPE_PERSONAS.get(interview_type, self._TYPE_PERSONAS["technical"])
        type_guidance = self._TYPE_QUESTION_GUIDANCE.get(interview_type, self._TYPE_QUESTION_GUIDANCE["technical"])

        self.system_persona = type_persona + self._COMMON_RULES + f"\nQUESTION FOCUS:\n{type_guidance}\n"
        self.resume_context = ""
        self.jd_context = ""

        if resume_text:
            sanitized_resume = self._sanitize_text(resume_text, max_length=1500)
            self.system_persona += (
                "\n\n ABSOLUTE RULE: You must NEVER repeat, read, narrate, list, or summarize "
                "any part of the resume below. ONLY use it to formulate questions. \n\n"
                f"CANDIDATE'S RESUME (for reference only — DO NOT READ ALOUD):\n{sanitized_resume}\n\n"
                "QUESTION RULES:\n"
                "- Pick ONE project or skill and ask a DIRECT question about it.\n"
                "- Example: 'Tell me about the data pipeline you built for ReviewNexus.'\n"
                "- BAD example: 'I see your resume lists Python, React, AWS...' (this is narrating!)\n"
            )

        self.rag_engine = rag_engine
        if self.rag_engine:
            jd_context = self._get_jd_context()
            if jd_context:
                self.has_jd = True
                sanitized_jd = self._sanitize_text(jd_context, max_length=1000)
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
        """Generate a prompt that forces the LLM to ask the first type-appropriate question."""
        itype = self.interview_type

        if itype == "behavioral":
            if self.has_resume:
                return (
                    "Ask your FIRST behavioral interview question now. Pick ONE specific experience "
                    "from the candidate's resume and ask a STAR-method question about it. "
                    "For example: 'Tell me about a time you faced a challenge while working on [project].' "
                    "Do NOT summarize the resume."
                )
            return "Ask a behavioral question about teamwork or a challenging work situation using the STAR method."

        if itype == "hr":
            return (
                "Ask your FIRST HR question now. Start with something about the candidate's "
                "career motivation or what drew them to this opportunity. Keep it warm and conversational."
            )

        if itype == "combined":
            if self.has_resume:
                return (
                    "Ask your FIRST interview question now. Start with a TECHNICAL question. "
                    "Pick ONE specific project or skill from the candidate's resume and ask a "
                    "technical deep-dive question about it. Do NOT summarize the resume."
                )
            return "Ask a technical question to assess the candidate's core skills to start the interview."

        # Default: technical
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

    def build_messages(self, history: list[dict], difficulty: str = "Medium",
                       question_context: dict | None = None) -> list[dict]:
        """Construct the message array for LLM chat completion.

        Args:
            history: Conversation history.
            difficulty: Current difficulty level.
            question_context: Optional RAG-retrieved question with ideal answer.
        """
        # Merge difficulty into the system persona — Gemma4 only allows ONE system message.
        difficulty_prompt = self.difficulty_prompts.get(difficulty, self.difficulty_prompts["Medium"])
        merged_system = self.system_persona + f"\n\nCURRENT DIFFICULTY: {difficulty_prompt}"
        messages = [{"role": "system", "content": merged_system}]

        if history:
            sanitized_history = []
            for msg in history[-10:]:
                sanitized_msg = {
                    "role": role,
                    "content": content
                }
                sanitized_history.append(sanitized_msg)
            
            # Inject RAG question context into the LAST user message if provided
            if question_context and sanitized_history:
                q_injection = self._build_question_injection(question_context)
                if sanitized_history[-1]["role"] == "user":
                    sanitized_history[-1]["content"] += f"\n\n[SYSTEM INSTRUCTION: {q_injection}]"
                    
            messages.extend(sanitized_history)
        elif question_context:
            # If no history exists, append a user message with the injection
            q_injection = self._build_question_injection(question_context)
            messages.append({"role": "user", "content": q_injection})

        return messages

    def _build_question_injection(self, question_context: dict) -> str:
        """Build a system message that guides the LLM to ask a specific question."""
        q = question_context.get("question", "")
        category = question_context.get("category", "general")
        difficulty = question_context.get("difficulty", "medium")

        injection = (
            f"QUESTION BANK GUIDANCE (Category: {category}, Difficulty: {difficulty}):\n"
            f"Consider asking a question along these lines: \"{q}\"\n"
            "You may rephrase it naturally to fit the conversation flow, "
            "but keep the core topic and difficulty intact.\n"
            "Do NOT mention that this question came from a question bank.\n"
        )

        return injection

    def build_evaluation_context(self, question: str, ideal_answer: str,
                                  candidate_answer: str) -> str:
        """Build context for per-question evaluation."""
        return (
            f"QUESTION ASKED: {question}\n\n"
            f"IDEAL ANSWER (reference): {ideal_answer}\n\n"
            f"CANDIDATE'S ANSWER: {candidate_answer}\n\n"
            "Evaluate the candidate's answer against the ideal. "
            "Score technical accuracy, clarity, and communication separately."
        )

