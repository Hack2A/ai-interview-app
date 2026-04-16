"""WebSocket consumer for real-time AI interview sessions.

Full interview pipeline over WebSocket — mirrors the CLI flow exactly:
1. Frontend sends "setup" with resume, JD, difficulty, mode, type → ATS + opening question + audio
2. Frontend sends "answer" with text → streaming AI response + audio
3. Frontend sends binary audio → STT transcription + sentiment → treated as answer
4. Frontend sends "end" → evaluation report + proctoring summary
"""

import asyncio
import base64
import json
import logging
import os
import secrets
import tempfile

import numpy as np

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

from .utils.audio_handler import (
    save_audio_blob,
    save_tts_audio,
    cleanup_session_audio,
)

logger = logging.getLogger('interview')


class InterviewConsumer(AsyncWebsocketConsumer):
    """Async WebSocket consumer for real-time interview sessions.

    Each connection gets its OWN orchestrator instance — no shared state.

    Protocol (JSON messages):

    → Client sends:
        {"type": "setup", "resume": "...", "jd": "...",
         "difficulty": "Medium", "mode": "curated",
         "interview_type": "technical", "proctoring": false}
        {"type": "answer", "text": "My answer..."}
        {"type": "end"}
        (or binary audio data for STT)

    ← Server sends:
        {"type": "connected", "session_id": "..."}
        {"type": "status", "message": "..."}
        {"type": "ats_result", "data": {...}}
        {"type": "question", "text": "...", "audio_url": "..."}
        {"type": "stream_start"}
        {"type": "stream_chunk", "text": "..."}
        {"type": "stream_end", "text": "full response", "audio_url": "..."}
        {"type": "transcript", "text": "...", "sentiment": {...}, "fillers": {...}}
        {"type": "report", "data": {...}}
        {"type": "error", "message": "..."}
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session_id = None
        self.api = None
        self.db_session = None
        self._interview_active = False
        self._difficulty = 'Medium'
        self._proctoring_enabled = False

    # ── Connection Lifecycle ──────────────────────────────────────

    async def connect(self):
        """Accept WebSocket connection and generate session ID."""
        self.session_id = secrets.token_hex(16)
        await self.accept()

        await self.send_json({
            'type': 'connected',
            'session_id': self.session_id,
            'message': 'WebSocket connected. Send {"type": "setup", ...} to begin.',
        })

        logger.info(f"WS connected: session={self.session_id[:8]}")

    async def disconnect(self, close_code):
        """Clean up session on disconnect."""
        logger.info(f"WS disconnected: session="
                     f"{self.session_id[:8] if self.session_id else '?'}, "
                     f"code={close_code}")
        await self._cleanup_session()

    # ── Message Router ────────────────────────────────────────────

    async def receive(self, text_data=None, bytes_data=None):
        """Route incoming messages to appropriate handlers."""
        # Binary data = raw audio from browser MediaRecorder
        if bytes_data:
            await self._handle_audio(bytes_data)
            return

        # JSON text messages
        if text_data:
            try:
                data = json.loads(text_data)
            except json.JSONDecodeError:
                await self.send_json({
                    'type': 'error',
                    'message': 'Invalid JSON.',
                })
                return

            msg_type = data.get('type', '').lower()

            handlers = {
                'setup': self._handle_setup,
                'start': self._handle_setup,
                'answer': self._handle_answer,
                'end': self._handle_end,
            }

            handler = handlers.get(msg_type)
            if handler:
                await handler(data)
            else:
                await self.send_json({
                    'type': 'error',
                    'message': f'Unknown type: "{msg_type}". '
                               f'Use "setup", "answer", or "end".',
                })

    # ── PDF Extraction ────────────────────────────────────────────

    @staticmethod
    def _extract_pdf_text(pdf_bytes: bytes) -> str:
        """Extract text from PDF bytes using pypdf."""
        try:
            from pypdf import PdfReader
            import io
            reader = PdfReader(io.BytesIO(pdf_bytes))
            text = '\n'.join(
                page.extract_text() or '' for page in reader.pages
            )
            return text.strip()
        except Exception as e:
            logger.error(f'PDF extraction failed: {e}')
            return ''

    # ── Setup: Full Interview Pipeline Init ───────────────────────

    async def _handle_setup(self, data: dict):
        """Initialize the full interview pipeline.

        Mirrors CLI flow:
        1. Load resume + JD
        2. Initialize orchestrator engines
        3. Run ATS analysis
        4. Create session (difficulty, mode, type)
        5. Start proctoring (if enabled)
        6. Generate opening question
        7. Synthesize opening question audio (TTS)
        8. Send question with text + audio_url
        """
        if self._interview_active:
            await self.send_json({
                'type': 'error',
                'message': 'Interview already in progress. Send "end" first.',
            })
            return

        # Extract config
        self._difficulty = data.get('difficulty', 'Medium')
        interview_mode = data.get('mode', 'generic')
        interview_type = data.get('interview_type', 'technical')
        self._proctoring_enabled = data.get('proctoring', False)

        # ── Parse resume (text or PDF) ──
        resume_text = data.get('resume', '')
        resume_pdf_b64 = data.get('resume_pdf', '')
        if resume_pdf_b64 and not resume_text:
            try:
                pdf_bytes = base64.b64decode(resume_pdf_b64)
                resume_text = await asyncio.to_thread(
                    self._extract_pdf_text, pdf_bytes
                )
                if not resume_text:
                    await self.send_json({
                        'type': 'error',
                        'message': 'Could not extract text from resume PDF.',
                    })
                    return
            except Exception as e:
                await self.send_json({
                    'type': 'error',
                    'message': f'Invalid resume PDF: {str(e)}',
                })
                return

        # ── Parse JD (text or PDF) ──
        jd_text = data.get('jd', '')
        jd_pdf_b64 = data.get('jd_pdf', '')
        if jd_pdf_b64 and not jd_text:
            try:
                pdf_bytes = base64.b64decode(jd_pdf_b64)
                jd_text = await asyncio.to_thread(
                    self._extract_pdf_text, pdf_bytes
                )
                if not jd_text:
                    await self.send_json({
                        'type': 'error',
                        'message': 'Could not extract text from JD PDF.',
                    })
                    return
            except Exception as e:
                await self.send_json({
                    'type': 'error',
                    'message': f'Invalid JD PDF: {str(e)}',
                })
                return

        try:
            # ── Step 1: Create orchestrator (per-connection) ──
            await self.send_json({
                'type': 'status',
                'message': 'Initializing AI interview engine...',
            })

            self.api = await asyncio.to_thread(self._create_orchestrator)

            # ── Step 2: Load resume and JD ──
            if resume_text:
                await self.send_json({
                    'type': 'status',
                    'message': f'Loading resume ({len(resume_text.split())} words)...',
                })
                await asyncio.to_thread(
                    self.api.load_resume_from_text, resume_text
                )

            if jd_text:
                await self.send_json({
                    'type': 'status',
                    'message': f'Loading job description ({len(jd_text.split())} words)...',
                })
                try:
                    await asyncio.to_thread(
                        self.api.load_jd_from_text, jd_text
                    )
                except AttributeError:
                    # RAG index_jd may not be available
                    self.api._jd_text = jd_text
                    logger.warning("RAG indexing skipped (index_jd not available)")

            # ── Step 3: Run ATS analysis (if both resume + JD) ──
            ats_result = None
            if resume_text and jd_text:
                await self.send_json({
                    'type': 'status',
                    'message': 'Running ATS resume analysis...',
                })
                ats_result = await asyncio.to_thread(self.api.analyze_resume)

                await self.send_json({
                    'type': 'ats_result',
                    'data': ats_result,
                })

            # ── Step 4: Create session ──
            await self.send_json({
                'type': 'status',
                'message': 'Configuring interview session...',
            })
            await asyncio.to_thread(
                self.api.new_session,
                difficulty=self._difficulty,
                interview_mode=interview_mode,
                interview_type=interview_type,
            )
            await asyncio.to_thread(self.api.reset_chat)

            # ── Step 5: Start proctoring (if enabled) ──
            if self._proctoring_enabled:
                await self.send_json({
                    'type': 'status',
                    'message': 'Starting proctoring...',
                })
                await asyncio.to_thread(self.api.start_proctoring)

            # ── Step 6: Create DB record ──
            self.db_session = await self._create_db_session(
                difficulty=self._difficulty,
            )

            self._interview_active = True

            # ── Step 7: Generate opening question ──
            await self.send_json({
                'type': 'status',
                'message': 'Generating opening question...',
            })

            opening = await asyncio.to_thread(
                self.api.get_opening_question, self._difficulty
            )

            # Strip system-prompt leakage from local LLM response
            opening = self._clean_llm_response(opening)

            await self._save_message('ai', opening)

            # ── Step 8: Synthesize opening question audio (TTS) ──
            audio_url = await self._synthesize_and_save(opening)

            await self.send_json({
                'type': 'question',
                'text': opening,
                'audio_url': audio_url,
            })

            logger.info(
                f"Interview started: session={self.session_id[:8]}, "
                f"difficulty={self._difficulty}, mode={interview_mode}, "
                f"type={interview_type}"
            )

        except Exception as e:
            logger.exception(f"Failed to start interview: {e}")
            await self.send_json({
                'type': 'error',
                'message': f'Failed to start interview: {str(e)}',
            })

    # ── Answer: Chat with AI ──────────────────────────────────────

    async def _handle_answer(self, data: dict):
        """Process a user answer and get AI response with audio.

        Flow (mirrors CLI):
        1. Check toxicity
        2. Save user message
        3. Stream AI response token-by-token
        4. Synthesize full response to audio (TTS)
        5. Send stream_end with text + audio_url
        """
        if not self._interview_active or not self.api:
            await self.send_json({
                'type': 'error',
                'message': 'No active interview. Send "setup" first.',
            })
            return

        user_text = data.get('text', '').strip()
        if not user_text:
            await self.send_json({
                'type': 'error',
                'message': 'Empty answer.',
            })
            return

        # Check if user voluntarily wants to end
        end_phrases = ["end interview", "end the interview", "stop interview", "conclude interview"]
        if any(p in user_text.lower() for p in end_phrases) and len(user_text) < 50:
            logger.info(f"User manually ended interview for session {self.session_id}")
            asyncio.create_task(self._handle_end({}))
            return

        # Check toxicity
        toxicity = await asyncio.to_thread(
            self.api.check_toxicity, user_text
        )

        # Save user message
        await self._save_message('user', user_text)

        try:
            # Stream AI response
            await self.send_json({'type': 'stream_start'})

            full_response = await self._stream_response(
                user_text, self._difficulty
            )

            # Save AI message
            await self._save_message('ai', full_response)

            # Synthesize response audio (TTS)
            audio_url = await self._synthesize_and_save(full_response)

            # Send complete response with audio
            await self.send_json({
                'type': 'stream_end',
                'text': full_response,
                'audio_url': audio_url,
                'toxicity': toxicity,
            })

            # Auto-detect if interview has concluded
            is_ending = any(phrase in full_response.lower() for phrase in [
                "concludes the interview",
                "concludes the technical interview",
                "concludes our interview",
                "end of the interview",
                "end of our interview",
                "that concludes"
            ])
            
            if is_ending:
                logger.info(f"Auto-detected end of interview for session {self.session_id}")
                asyncio.create_task(self._handle_end({}))

        except Exception as e:
            logger.exception(f"Chat error: {e}")
            await self.send_json({
                'type': 'error',
                'message': f'AI response failed: {str(e)}',
            })

    # ── Audio: STT + Sentiment → Answer ──────────────────────────

    async def _handle_audio(self, audio_data: bytes):
        """Transcribe binary audio, analyze sentiment, and treat as answer.

        Flow (mirrors CLI):
        1. Save audio file to media/audio/<session>/
        2. Transcribe via STT engine
        3. Analyze sentiment + detect fillers
        4. Send transcript with analysis
        5. Route to _handle_answer for AI response
        """
        if not self._interview_active or not self.api:
            await self.send_json({
                'type': 'error',
                'message': 'No active interview. Send "setup" first.',
            })
            return

        await self.send_json({
            'type': 'status',
            'message': 'Transcribing audio...',
        })

        try:
            # Save audio to session directory (not temp)
            audio_path = await asyncio.to_thread(
                save_audio_blob, audio_data, self.session_id
            )

            # STT transcription
            result = await asyncio.to_thread(
                self.api.transcribe_audio, audio_path
            )

            transcribed_text = result.get('text', '').strip()
            if not transcribed_text:
                await self.send_json({
                    'type': 'error',
                    'message': 'Could not transcribe audio.',
                })
                return

            # Sentiment analysis on the audio file
            sentiment = None
            try:
                sentiment = await asyncio.to_thread(
                    self.api.analyze_sentiment, audio_path
                )
            except Exception as e:
                logger.warning(f"Sentiment analysis failed: {e}")

            # Filler word detection on transcribed text
            fillers = None
            try:
                fillers = await asyncio.to_thread(
                    self.api.detect_fillers, transcribed_text
                )
            except Exception as e:
                logger.warning(f"Filler detection failed: {e}")

            # Send transcript with analysis results
            transcript_msg = {
                'type': 'transcript',
                'text': transcribed_text,
            }
            if sentiment:
                transcript_msg['sentiment'] = sentiment
            if fillers:
                transcript_msg['fillers'] = fillers

            await self.send_json(transcript_msg)

            # Route transcribed text as an answer
            await self._handle_answer({
                'type': 'answer',
                'text': transcribed_text,
            })

        except Exception as e:
            logger.exception(f"Audio error: {e}")
            await self.send_json({
                'type': 'error',
                'message': f'Transcription failed: {str(e)}',
            })

    # ── End: Report + Proctoring + Cleanup ────────────────────────

    async def _handle_end(self, data: dict):
        """End interview, generate evaluation report, stop proctoring.

        Flow (mirrors CLI):
        1. Generate evaluation report from chat history
        2. Stop proctoring and get violation summary
        3. Send report
        4. Clean up
        """
        if not self._interview_active or not self.api:
            await self.send_json({
                'type': 'error',
                'message': 'No active interview to end.',
            })
            return

        report = None

        try:
            # Generate evaluation report (with 120s timeout)
            await self.send_json({
                'type': 'status',
                'message': 'Generating evaluation report... (this may take up to 2 minutes)',
            })

            history = await asyncio.to_thread(self.api.get_chat_history)

            try:
                report = await asyncio.wait_for(
                    asyncio.to_thread(self.api.generate_report, history),
                    timeout=120.0,
                )
            except asyncio.TimeoutError:
                logger.error("Report generation timed out after 120s")
                report = {
                    "error": "Report generation timed out",
                    "chat_history": history,
                }

        except Exception as e:
            logger.exception(f"Report error: {e}")
            report = {"error": str(e)}

        # Stop proctoring (always attempt)
        proctoring_summary = None
        if self._proctoring_enabled:
            try:
                proctoring_summary = await asyncio.to_thread(
                    self.api.stop_proctoring
                )
            except Exception as e:
                logger.warning(f"Proctoring stop failed: {e}")

        # Update DB
        if report:
            await self._end_db_session(report)

        # Send report (even if partial/error)
        response = {
            'type': 'report',
            'data': report or {"error": "No report generated"},
            'session_id': self.session_id,
        }
        if proctoring_summary:
            response['proctoring'] = proctoring_summary

        await self.send_json(response)
        logger.info(f"Interview ended: session={self.session_id[:8]}")

        # Cleanup AFTER sending the report
        await self._cleanup_session()

    # ── Streaming Helper (truly incremental) ──────────────────────

    async def _stream_response(self, user_text: str,
                                difficulty: str) -> str:
        """Stream LLM response token-by-token over WebSocket.

        Uses an asyncio.Queue fed by a background thread so each
        chunk is sent to the client as soon as it's generated —
        no collecting-then-sending.
        """
        queue = asyncio.Queue()
        chunks = []
        loop = asyncio.get_running_loop()

        def _generate():
            """Run the synchronous generator in a thread, pushing to queue."""
            try:
                for chunk in self.api.chat_stream(user_text, difficulty):
                    if chunk.strip():
                        loop.call_soon_threadsafe(
                            queue.put_nowait, chunk
                        )
                # Signal completion
                loop.call_soon_threadsafe(
                    queue.put_nowait, None
                )
            except Exception as e:
                loop.call_soon_threadsafe(
                    queue.put_nowait, e
                )

        # Start generation in background thread
        gen_future = loop.run_in_executor(None, _generate)

        # Read chunks as they arrive and send immediately
        while True:
            item = await queue.get()

            if item is None:
                # Generation complete
                break
            if isinstance(item, Exception):
                raise item

            chunks.append(item)
            await self.send_json({
                'type': 'stream_chunk',
                'text': item,
            })

        # Wait for thread to fully finish
        await gen_future

        return ' '.join(chunks).strip()

    # ── TTS Helper ────────────────────────────────────────────────

    async def _synthesize_and_save(self, text: str) -> str | None:
        """Synthesize text to audio and save to session media directory.

        Returns:
            URL path to the audio file, or None if TTS fails.
        """
        try:
            source_path = await asyncio.to_thread(
                self.api.synthesize_audio, text
            )
            if source_path:
                audio_url = await asyncio.to_thread(
                    save_tts_audio, source_path, self.session_id
                )
                return audio_url
        except Exception as e:
            logger.warning(f"TTS synthesis failed: {e}")
        return None

    # ── Orchestrator Factory (per-connection) ─────────────────────

    @staticmethod
    def _create_orchestrator():
        """Create a FRESH orchestrator instance per WebSocket connection.

        Each connection gets its own orchestrator — no shared state
        between concurrent interview sessions.
        """
        from .apps import _ensure_ml_path
        _ensure_ml_path()
        from orchestrator import BeaverAIOrchestrator
        return BeaverAIOrchestrator(lazy_load=True)

    # ── Database Helpers ──────────────────────────────────────────

    @database_sync_to_async
    def _create_db_session(self, difficulty: str):
        from .models import InterviewSession

        user = self.scope.get('user')
        if not user or isinstance(user, AnonymousUser):
            return None

        return InterviewSession.objects.create(
            user=user,
            session_id=self.session_id,
            difficulty=difficulty,
        )

    @database_sync_to_async
    def _save_message(self, role: str, content: str):
        if not self.db_session:
            return
        from .models import ChatMessage
        ChatMessage.objects.create(
            session=self.db_session, role=role, content=content,
        )

    @database_sync_to_async
    def _end_db_session(self, report: dict):
        if not self.db_session:
            return
        self.db_session.status = 'completed'
        self.db_session.ended_at = timezone.now()
        self.db_session.evaluation_report = report
        self.db_session.save()

    # ── Session Cleanup ───────────────────────────────────────────

    async def _cleanup_session(self):
        if self.api and self._interview_active:
            try:
                await asyncio.to_thread(self.api.reset_chat)
            except Exception:
                pass
        self._interview_active = False
        self._proctoring_enabled = False
        self.api = None
        self.db_session = None

    # ── Utility ───────────────────────────────────────────────────

    @staticmethod
    def _clean_llm_response(text: str) -> str:
        """Strip system-prompt / resume leakage from local LLM output.

        Some local GGUF models echo the persona rules and resume text
        before generating the actual answer.  This is a safety net
        after the LLM engine's own _strip_echo processing.
        """
        import re

        if not text:
            return text

        # Markers that indicate raw system-prompt or resume content
        echo_markers = [
            'You are BeaverAI', 'STRICT RULES:', 'QUESTION FOCUS:',
            "CANDIDATE'S RESUME", 'ABSOLUTE RULE:', 'QUESTION RULES:',
            'TECHNICAL SKILLS', 'EDUCATION', 'EXPERIENCE', 'SUMMARY',
            'DevOps & T ools', 'F rontend:', 'Backend:', 'Languages:',
            'Databases:', 'GPA:', 'Bachelor',
        ]

        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        
        # Check if the raw text has ANY overlap with the markers
        has_leakage = any(marker in text for marker in echo_markers)
        
        # If it doesn't look like a question at all, treat it as failure
        if not has_leakage and '?' in text:
            return text

        # Try to extract a proper question that doesn't have resume markers
        questions = [
            s for s in sentences
            if '?' in s and not any(m in s for m in echo_markers)
        ]

        if questions:
            return questions[-1].strip()

        # Total fallback — the LLM completely failed to ask a question
        return (
            "Hello, let's begin the interview. "
            "Can you tell me about a recent project you worked on "
            "and what technologies you used?"
        )

    async def send_json(self, content: dict):
        await self.send(text_data=json.dumps(content, cls=_NumpyEncoder))


class _NumpyEncoder(json.JSONEncoder):
    """JSON encoder that handles NumPy types from ML pipelines."""

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)
