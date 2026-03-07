"""Interview Manager — orchestrates audio, LLM, TTS, proctoring, and evaluation."""
import json
import logging
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import soundfile as sf

from config import settings
from src.brain.evaluator import Evaluator
from src.brain.llm_engine import LLMEngine
from src.brain.rag_engine import RAGEngine
from src.core.ats_checker import ATSChecker
from src.core.jd_loader import JDLoader
from src.core.resume_loader import ResumeLoader
from src.core.session_state import SessionState
from src.ears.stt_engine import STTEngine
from src.ears.vad import VoiceRecorder
from src.voice.tts_engine import TTSEngine

logger = logging.getLogger("InterviewManager")

_proctoring_available = False
if settings.ENABLE_PROCTORING:
    try:
        from src.eyes.proctoring_monitor import ProctoringMonitor
        _proctoring_available = True
    except ImportError:
        pass

_coqui_available = False
if settings.USE_ADVANCED_TTS:
    try:
        from src.voice.tts_coqui import CoquiTTSEngine
        _coqui_available = True
    except ImportError:
        pass


class InterviewManager:
    """Orchestrates the full interview pipeline: audio capture, LLM, TTS, proctoring, and evaluation."""

    def __init__(self) -> None:
        logger.info("Initializing BeaverAI Engines...")
        self.state = SessionState()

        self.resume_loader = ResumeLoader()
        resume_text = self.resume_loader.load_resume()

        self.jd_loader = JDLoader() if settings.ENABLE_RAG else None
        jd_text = self.jd_loader.load_jd() if self.jd_loader else None

        self._sentiment_analyzer = None
        self._proctoring = None
        self._ats_checker = None

        with ThreadPoolExecutor(max_workers=3) as executor:
            future_rag = None
            if settings.ENABLE_RAG and jd_text:
                future_rag = executor.submit(RAGEngine, jd_text=jd_text)

            future_brain = executor.submit(LLMEngine, resume_text=resume_text, rag_engine=None)
            future_ears = executor.submit(STTEngine)
            future_recorder = executor.submit(VoiceRecorder)

            self.rag_engine = future_rag.result() if future_rag else None
            self.brain = future_brain.result()
            self.brain.prompt_manager.rag_engine = self.rag_engine
            self.ears = future_ears.result()
            self.recorder = future_recorder.result()

        if settings.USE_ADVANCED_TTS and _coqui_available:
            try:
                self.voice_engine = CoquiTTSEngine()
                logger.info("Using Coqui XTTS v2")
            except (ImportError, RuntimeError, OSError) as e:
                logger.warning(f"Coqui TTS failed ({e}), falling back to pyttsx3")
                self.voice_engine = TTSEngine(vad_module=self.recorder)
        else:
            self.voice_engine = TTSEngine(vad_module=self.recorder)

        self.evaluator = Evaluator(settings.LLM_MODEL_PATH)

        self.next_turn_audio = None
        self.audio_responses = []
        self.detected_language = settings.DEFAULT_INTERVIEW_LANGUAGE
        self._toxicity_warnings = 0
        self._max_toxicity_warnings = 2

    # ── Toxicity Detection ────────────────────────────────────────

    _PROFANITY_WORDS = frozenset([
        "fuck", "shit", "bitch", "ass", "damn", "bastard", "dick",
        "asshole", "crap", "piss", "slut", "whore", "cunt", "stfu",
        "motherfucker", "bullshit", "dumbass", "idiot", "stupid",
    ])

    def _is_toxic(self, text: str) -> bool:
        """Check if user input contains profanity or hostile language."""
        words = set(text.lower().split())
        return bool(words & self._PROFANITY_WORDS)

    # ── Lazy Properties ───────────────────────────────────────────

    @property
    def sentiment_analyzer(self):
        if self._sentiment_analyzer is None and settings.ENABLE_SENTIMENT:
            from src.ears.sentiment_analyzer import SentimentAnalyzer
            self._sentiment_analyzer = SentimentAnalyzer()
        return self._sentiment_analyzer

    @property
    def proctoring(self):
        if self._proctoring is None and settings.ENABLE_PROCTORING and _proctoring_available:
            self._proctoring = ProctoringMonitor()
        return self._proctoring

    @proctoring.setter
    def proctoring(self, value):
        self._proctoring = value

    @property
    def ats_checker(self):
        if self._ats_checker is None and settings.ENABLE_ATS:
            self._ats_checker = ATSChecker(llm_model=self.brain.llm)
        return self._ats_checker

    # ── ATS Check ─────────────────────────────────────────────────

    def _run_ats_check(self, resume_text: str, jd_text: str):
        if not self.ats_checker or not resume_text or not jd_text:
            return True

        print("\n" + "=" * 60)
        print("            ATS RESUME ANALYSIS")
        print("=" * 60)
        print("Analyzing resume against job description...\n")

        ats_report = self.ats_checker.analyze(resume_text, jd_text)

        # ── Algorithmic Score ──
        print("┌─────────────────────────────────────────┐")
        print(f"│  📊 Algorithmic ATS Score:  {ats_report['algorithmic_score']:>5.1f}%      │")
        print("├─────────────────────────────────────────┤")
        print(f"│  TF-IDF Similarity:     {ats_report['tfidf_score']:>6.1f}%         │")
        print(f"│  Semantic Similarity:   {ats_report['semantic_score']:>6.1f}%         │")
        print(f"│  Skill Match:           {ats_report['skill_match_score']:>6.1f}%         │")
        print(f"│  Keyword Match:         {ats_report['keyword_match_score']:>6.1f}%         │")
        print("└─────────────────────────────────────────┘")

        # ── Spelling & Formatting ──
        spelling = ats_report.get("spelling", {})
        formatting = ats_report.get("formatting", {})

        if spelling.get("error_count", 0) > 0:
            print(f"\n⚠️  Spelling Issues ({spelling['error_count']} found):")
            for err in spelling["errors"][:10]:
                print(f"   • \"{err}\"")
            print(f"   Penalty: -{spelling['score_penalty']} points")

        if formatting.get("issues"):
            print(f"\n⚠️  Formatting Issues ({formatting['issue_count']} found):")
            for issue in formatting["issues"]:
                print(f"   • {issue}")
            print(f"   Penalty: -{formatting['score_penalty']} points")

        # ── LLM Score ──
        if ats_report.get("llm_score") is not None:
            print("\n┌─────────────────────────────────────────┐")
            print(f"│  🤖 AI Intelligent Score:   {ats_report['llm_score']:>5.1f}%      │")
            print("└─────────────────────────────────────────┘")
            print(f"\n  Reasoning: {ats_report.get('llm_reasoning', 'N/A')}")

            if ats_report.get('llm_strengths'):
                print("\n  ✅ Key Strengths (AI Analysis):")
                for s in ats_report['llm_strengths'][:5]:
                    print(f"     + {s}")

            if ats_report.get('llm_gaps'):
                print("\n  ❌ Areas for Improvement (AI Analysis):")
                for g in ats_report['llm_gaps'][:5]:
                    print(f"     - {g}")

        # ── Combined Score ──
        print("\n" + "=" * 60)
        print(f"  ⭐ COMBINED SCORE: {ats_report['combined_score']:.1f}%")
        if ats_report.get("llm_score") is not None:
            print(f"     (Algorithmic: {ats_report['algorithmic_score']:.1f}% + AI: {ats_report['llm_score']:.1f}%) / 2")
        print("=" * 60)

        # Skills summary
        matched = ats_report.get("matched_skills", [])
        missing = ats_report.get("missing_skills", [])
        if matched:
            print(f"\n  Matched Skills ({len(matched)}): {', '.join(matched[:10])}")
        if missing:
            print(f"  Missing Skills ({len(missing)}): {', '.join(missing[:10])}")

        if ats_report["suggestions"]:
            print("\n  💡 Suggestions:")
            for s in ats_report["suggestions"]:
                print(f"     {s}")

        print("=" * 60)
        proceed = input("\nProceed with interview? [Y/n]: ").strip().lower()
        if proceed and proceed not in ['y', 'yes', '']:
            print("Interview cancelled by user.")
            return False
        return True

    # ── Session Config ────────────────────────────────────────────

    def _configure_session(self):
        print("\n" + "=" * 40 + "\n      BEAVER AI - SESSION SETUP\n" + "=" * 40)

        if self.ats_checker and self.jd_loader:
            resume_text = self.resume_loader.load_resume()
            jd_text = self.jd_loader.load_jd()
            if resume_text and jd_text:
                if not self._run_ats_check(resume_text, jd_text):
                    return False

        print("\nPlease select the interview difficulty:\n [1] Easy\n [2] Medium\n [3] Hard\n [4] Extreme")
        choice = input("\nEnter choice (1-4) [Default: 2]: ").strip()
        mapping = {"1": "Easy", "2": "Medium", "3": "Hard", "4": "Extreme"}
        self.state.difficulty = mapping.get(choice, "Medium")

        if self.proctoring:
            enable_proc = input("\nEnable AI Proctoring? [Y/n]: ").strip().lower()
            if enable_proc and enable_proc not in ['y', 'yes', '']:
                self.proctoring = None

        print(f"\n>> Configuration Locked: {self.state.difficulty} Mode")
        if self.proctoring:
            print(">> Proctoring: ENABLED")
        time.sleep(1)

    # ── Main Session ──────────────────────────────────────────────

    def _speak(self, text: str) -> None:
        """Speak text using the appropriate engine."""
        if hasattr(self.voice_engine, 'speak_text'):
            self.voice_engine.speak_text(text)
        elif hasattr(self.voice_engine, 'speak'):
            self.voice_engine.speak(text, self.detected_language)
        else:
            print(f"\n[BeaverAI]: {text}")

    def start_session(self):
        self._configure_session()

        if self.proctoring:
            self.proctoring.start()
            time.sleep(1)

        print(f"--- Interview Session Started (ID: {self.state.session_id}) ---")

        # Greeting
        self._speak(f"Hello! I am ready for the {self.state.difficulty} interview. Let's begin.")

        (settings.BASE_DIR / "data" / "temp").mkdir(parents=True, exist_ok=True)

        # Generate opening question based on resume/JD
        self._generate_opening_question()

        while self.state.is_active:
            try:
                print(f"\n[Status] Listening...")
                audio_data = self.recorder.listen_and_record(prepend_audio=self.next_turn_audio)
                self.next_turn_audio = None

                if audio_data is None or len(audio_data) == 0:
                    continue

                temp_wav = settings.BASE_DIR / "data" / "temp" / f"input_{self.state.question_count}.wav"
                sf.write(str(temp_wav), audio_data, 16000)

                user_text, detected_lang = self.ears.transcribe(str(temp_wav), language=None)
                self.detected_language = detected_lang

                print(f"[User]: {user_text}")

                if not user_text.strip():
                    continue

                txt = user_text.lower().strip()
                is_exit_command = False

                exit_phrases = ["end interview", "stop the interview", "exit interview",
                                "terminate session", "i want to quit"]
                if any(p in txt for p in exit_phrases):
                    is_exit_command = True

                if len(txt.split()) <= 3 and any(w in txt for w in ["exit", "quit", "stop", "bye"]):
                    is_exit_command = True

                if is_exit_command:
                    self._speak("Are you sure you want to end the interview?")

                    print(">> Waiting for confirmation...")

                    confirm_audio = self.recorder.listen_and_record()
                    if confirm_audio is not None and len(confirm_audio) > 0:
                        sf.write(str(temp_wav), confirm_audio, 16000)
                    else:
                        print("No audio recorded, assuming exit.")
                        break

                    confirm_text, _ = self.ears.transcribe(str(temp_wav))
                    confirm_text = confirm_text.lower()
                    print(f"[Confirmation]: {confirm_text}")

                    if any(x in confirm_text for x in ["yes", "yeah", "sure", "correct", "end", "right", "bye"]):
                        self._speak("Ending session.")
                        break
                    else:
                        self._speak("Resuming the interview.")
                        continue

                # ── Toxicity check BEFORE sending to LLM ──
                if self._is_toxic(user_text):
                    self._toxicity_warnings += 1
                    if self._toxicity_warnings >= self._max_toxicity_warnings:
                        self._speak(
                            "This interview is being terminated due to repeated inappropriate language. "
                            "Please maintain professionalism in future interviews."
                        )
                        print(f"[!] Session auto-ended: {self._toxicity_warnings} toxicity warnings")
                        break
                    else:
                        self._speak(
                            f"Warning {self._toxicity_warnings}/{self._max_toxicity_warnings}: "
                            "Please maintain a professional tone. "
                            "One more violation will end this interview."
                        )
                        continue

                print("[Status] Thinking...")
                response_generator = self.brain.generate_stream(user_text, self.state.difficulty)

                print("[Status] Generating response...")
                if hasattr(self.voice_engine, 'speak_stream'):
                    self.next_turn_audio = self.voice_engine.speak_stream(response_generator)
                else:
                    response_text = "".join(list(response_generator))
                    self._speak(response_text)

                self.audio_responses.append(str(temp_wav))
                self.state.question_count += 1

            except KeyboardInterrupt:
                print("\n[!] Interview interrupted by user")
                break
            except Exception as e:
                print(f"\n[Error] {e}")
                import traceback
                traceback.print_exc()
                break

        self.end_session()

    def _generate_opening_question(self) -> None:
        """Generate the first interview question based on resume/JD context."""
        opening_prompt = self.brain.prompt_manager.get_opening_prompt(self.state.difficulty)

        print("[Status] Preparing first question...")
        response_generator = self.brain.generate_stream(opening_prompt, self.state.difficulty)

        if hasattr(self.voice_engine, 'speak_stream'):
            self.voice_engine.speak_stream(response_generator)
        else:
            response_text = "".join(list(response_generator))
            self._speak(response_text)

    # ── End Session ───────────────────────────────────────────────

    def end_session(self):
        print("\n--- Session Ended ---")

        try:
            if self.proctoring:
                self.proctoring.stop()
        except Exception as e:
            logger.warning(f"Proctoring stop failed: {e}")

        try:
            history = self.brain.get_history()

            print(f"\n[Report] Generating evaluation report...")
            report = self.evaluator.generate_report(history)
            report["transcript"] = history

            if self.sentiment_analyzer and self.audio_responses:
                try:
                    print("[Report] Analyzing sentiment and speech quality...")
                    sentiment_results = []
                    for i, audio_path in enumerate(self.audio_responses):
                        hist_idx = i - 1
                        if Path(audio_path).exists() and hist_idx < len(history) and history[hist_idx]['role'] == 'user':
                            result = self.sentiment_analyzer.analyze_full(audio_path, history[hist_idx]['content'])
                            sentiment_results.append(result)

                    if sentiment_results:
                        avg_confidence = np.mean([r['confidence_score'] for r in sentiment_results])
                        all_emotions = {}
                        for r in sentiment_results:
                            for emotion, score in r['emotions'].items():
                                all_emotions[emotion] = all_emotions.get(emotion, 0) + score

                        dominant_emotion = max(all_emotions.items(), key=lambda x: x[1])[0] if all_emotions else "neutral"
                        total_fillers = sum(r['fillers']['total_fillers'] for r in sentiment_results)
                        avg_wpm = np.mean([r['speech_metrics'].get('wpm', 0) for r in sentiment_results])

                        report["sentiment_analysis"] = {
                            "average_confidence": round(avg_confidence, 2),
                            "dominant_emotion": dominant_emotion,
                            "speaking_pace_wpm": round(avg_wpm, 1),
                            "total_filler_words": total_fillers,
                            "detailed_results": sentiment_results,
                        }
                except Exception as e:
                    logger.warning(f"Sentiment analysis failed: {e}")

            if self.proctoring:
                try:
                    violations_summary = self.proctoring.get_violations_summary()
                    report["proctoring"] = violations_summary
                except Exception as e:
                    logger.warning(f"Proctoring summary failed: {e}")

            settings.TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
            filename = settings.TRANSCRIPTS_DIR / f"{self.state.session_id}_report.json"

            with open(filename, "w") as f:
                json.dump(report, f, indent=2)

            print(f"✅ Report saved to: {filename}")

        except Exception as e:
            print(f"\n[Error] Report generation failed: {e}")
            import traceback
            traceback.print_exc()
