"""WebSocket consumer for real-time AI interview sessions.

Full interview pipeline over WebSocket:
1. Frontend sends "setup" with resume, JD, difficulty, mode, type → ATS + opening question
2. Frontend sends "answer" with text → AI response (streaming)
3. Frontend sends binary audio → transcribed via STT → treated as answer
4. Frontend sends "end" → evaluation report + proctoring summary
"""

import asyncio
import base64
import json
import logging
import os
import secrets
import tempfile

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

logger = logging.getLogger('interview')


class InterviewConsumer(AsyncWebsocketConsumer):
    """Async WebSocket consumer for real-time interview sessions.

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
        {"type": "question", "text": "..."}
        {"type": "stream_start"}
        {"type": "stream_chunk", "text": "..."}
        {"type": "stream_end", "text": "full response"}
        {"type": "response", "text": "..."}
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

    

    async def receive(self, text_data=None, bytes_data=None):
        """Route incoming messages to appropriate handlers."""
         
        if bytes_data:
            await self._handle_audio(bytes_data)
            return

        
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


    async def _handle_setup(self, data: dict):
        """Initialize the full interview pipeline.

        Accepts resume/JD as either:
          - Plain text: {"resume": "text...", "jd": "text..."}
          - Base64 PDF: {"resume_pdf": "base64...", "jd_pdf": "base64..."}

        Other fields:
            difficulty: str (Easy/Medium/Hard/Extreme)
            mode: str (generic/curated)
            interview_type: str (technical/behavioral/hr/combined)
            proctoring: bool
        """
        if self._interview_active:
            await self.send_json({
                'type': 'error',
                'message': 'Interview already in progress. Send "end" first.',
            })
            return

        
        self._difficulty = data.get('difficulty', 'Medium')
        interview_mode = data.get('mode', 'generic')
        interview_type = data.get('interview_type', 'technical')
        self._proctoring_enabled = data.get('proctoring', False)

        
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
                    # RAGEngine may not have index_jd — set JD directly
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
                'message': 'Interview starting...',
            })

            opening = await asyncio.to_thread(
                self.api.get_opening_question, self._difficulty
            )

            await self._save_message('ai', opening)

            await self.send_json({
                'type': 'question',
                'text': opening,
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
        """Process a user answer and get AI response."""
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

            # Send complete response
            await self.send_json({
                'type': 'stream_end',
                'text': full_response,
                'toxicity': toxicity,
            })

            # Also send as a simple "response" for easy consumption
            await self.send_json({
                'type': 'response',
                'text': full_response,
            })

        except Exception as e:
            logger.exception(f"Chat error: {e}")
            await self.send_json({
                'type': 'error',
                'message': f'AI response failed: {str(e)}',
            })

    # ── Audio: STT → Answer ───────────────────────────────────────

    async def _handle_audio(self, audio_data: bytes):
        """Transcribe binary audio and treat as answer."""
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
            with tempfile.NamedTemporaryFile(
                delete=False, suffix='.webm'
            ) as tmp:
                tmp.write(audio_data)
                audio_path = tmp.name

            result = await asyncio.to_thread(
                self.api.transcribe_audio, audio_path
            )

            try:
                os.unlink(audio_path)
            except OSError:
                pass

            transcribed_text = result.get('text', '').strip()
            if not transcribed_text:
                await self.send_json({
                    'type': 'error',
                    'message': 'Could not transcribe audio.',
                })
                return

            await self.send_json({
                'type': 'transcription',
                'text': transcribed_text,
            })

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

    # ── End: Report + Cleanup ─────────────────────────────────────

    async def _handle_end(self, data: dict):
        """End interview, generate report, stop proctoring."""
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
                report = {"error": "Report generation timed out", "chat_history": history}

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

    # ── Streaming Helper ──────────────────────────────────────────

    async def _stream_response(self, user_text: str,
                                difficulty: str) -> str:
        """Stream LLM response token-by-token over WebSocket."""
        chunks = []

        def _generate():
            return list(self.api.chat_stream(user_text, difficulty))

        all_chunks = await asyncio.to_thread(_generate)

        for chunk in all_chunks:
            if chunk.strip():
                chunks.append(chunk)
                await self.send_json({
                    'type': 'stream_chunk',
                    'text': chunk,
                })

        return ' '.join(chunks).strip()

    # ── Orchestrator Factory ──────────────────────────────────────

    @staticmethod
    def _create_orchestrator():
        """Create orchestrator instance."""
        from .apps import get_orchestrator
        return get_orchestrator()

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

    async def send_json(self, content: dict):
        await self.send(text_data=json.dumps(content))
