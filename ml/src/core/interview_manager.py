import time
import json
import numpy as np
import soundfile as sf
from pathlib import Path
from src.brain.llm_engine import LLMEngine
from src.ears.stt_engine import STTEngine
from src.ears.vad import VoiceRecorder
from src.voice.tts_engine import TTSEngine
from src.brain.evaluator import Evaluator
from src.core.session_state import SessionState
from config import settings
from src.core.resume_loader import ResumeLoader
from src.core.jd_loader import JDLoader
from src.brain.rag_engine import RAGEngine
from src.core.ats_checker import ATSChecker
from src.ears.sentiment_analyzer import SentimentAnalyzer

if settings.ENABLE_PROCTORING:
    from src.eyes.proctoring_monitor import ProctoringMonitor

if settings.USE_ADVANCED_TTS:
    try:
        from src.voice.tts_coqui import CoquiTTSEngine
    except:
        settings.USE_ADVANCED_TTS = False

class InterviewManager:
    def __init__(self):
        print("Initializing BeaverAI Engines...")
        self.state = SessionState()
        
        self.resume_loader = ResumeLoader()
        resume_text = self.resume_loader.load_resume()
        
        self.jd_loader = JDLoader() if settings.ENABLE_RAG else None
        jd_text = self.jd_loader.load_jd() if self.jd_loader else None
        
        self.rag_engine = None
        if settings.ENABLE_RAG and jd_text:
            self.rag_engine = RAGEngine(jd_text=jd_text)
        
        self.brain = LLMEngine(resume_text=resume_text, rag_engine=self.rag_engine)
        self.ats_checker = ATSChecker(llm_model=self.brain.llm) if settings.ENABLE_ATS else None
        self.ears = STTEngine()
        self.recorder = VoiceRecorder()
        
        if settings.USE_ADVANCED_TTS:
            try:
                self.voice_engine = CoquiTTSEngine()
                print("[TTS] Using Coqui XTTS v2")
            except:
                self.voice_engine = TTSEngine(vad_module=self.recorder)
                print("[TTS] Using pyttsx3 (fallback)")
        else:
            self.voice_engine = TTSEngine(vad_module=self.recorder)
        
        self.evaluator = Evaluator(settings.LLM_MODEL_PATH)
        self.sentiment_analyzer = SentimentAnalyzer() if settings.ENABLE_SENTIMENT else None
        self.proctoring = ProctoringMonitor() if settings.ENABLE_PROCTORING else None
        
        self.next_turn_audio = None
        self.audio_responses = []
        self.detected_language = settings.DEFAULT_INTERVIEW_LANGUAGE

    def _run_ats_check(self, resume_text, jd_text):
        if not self.ats_checker or not resume_text or not jd_text:
            return
        
        print("\n" + "="*50)
        print("        ATS RESUME CHECKER")
        print("="*50)
        print("Analyzing resume against job description...")
        
        ats_report = self.ats_checker.analyze(resume_text, jd_text)
        
        print(f"\nTraditional ATS Score: {ats_report['match_score']}%")
        
        if 'llm_score' in ats_report:
            print(f"AI Intelligent Score: {ats_report['llm_score']}%")
            print(f"\nAI Analysis: {ats_report.get('llm_reasoning', 'N/A')}")
            
            if ats_report.get('llm_strengths'):
                print("\nKey Strengths (AI Analysis):")
                for strength in ats_report['llm_strengths'][:5]:
                    print(f"  + {strength}")
            
            if ats_report.get('llm_gaps'):
                print("\nAreas for Improvement (AI Analysis):")
                for gap in ats_report['llm_gaps'][:5]:
                    print(f"  - {gap}")
        
        print(f"\nMatched Skills ({len(ats_report['matched_skills'])}): {', '.join(ats_report['matched_skills'][:10])}")
        if ats_report['missing_skills']:
            print(f"\nMissing Skills ({len(ats_report['missing_skills'])}): {', '.join(ats_report['missing_skills'][:10])}")
        
        if ats_report['suggestions']:
            print("\nSuggestions:")
            for suggestion in ats_report['suggestions']:
                print(f"  - {suggestion}")
        
        print("="*50)
        proceed = input("\nProceed with interview? [Y/n]: ").strip().lower()
        if proceed and proceed not in ['y', 'yes', '']:
            print("Exiting...")
            exit(0)

    def _configure_session(self):
        print("\n" + "="*40 + "\n      BEAVER AI - SESSION SETUP\n" + "="*40)
        
        if self.ats_checker and self.jd_loader:
            resume_text = self.resume_loader.load_resume()
            jd_text = self.jd_loader.load_jd()
            if resume_text and jd_text:
                self._run_ats_check(resume_text, jd_text)
        
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

    def start_session(self):
        self._configure_session()
        
        if self.proctoring:
            self.proctoring.start()
            time.sleep(1)
        
        print(f"--- Interview Session Started (ID: {self.state.session_id}) ---")
        
        if hasattr(self.voice_engine, 'speak'):
            self.voice_engine.speak(f"Hello! I am ready for the {self.state.difficulty} interview. Let's begin.", self.detected_language)
        else:
            self.voice_engine.speak_stream([f"Hello! I am ready for the {self.state.difficulty} interview. Let's begin."])

        (settings.BASE_DIR / "data" / "temp").mkdir(parents=True, exist_ok=True)
        
        while self.state.is_active:
            try:
                print(f"\n[Status] Listening...")
                audio_data = self.recorder.listen_and_record(prepend_audio=self.next_turn_audio)
                self.next_turn_audio = None
                
                if audio_data is None or len(audio_data) == 0: continue

                temp_wav = settings.BASE_DIR / "data" / "temp" / f"input_{self.state.question_count}.wav"
                sf.write(str(temp_wav), audio_data, 16000)
                
                user_text, detected_lang = self.ears.transcribe(str(temp_wav), language=None)
                self.detected_language = detected_lang
                
                print(f"[User]: {user_text}")

                if not user_text.strip(): continue

                txt = user_text.lower().strip()
                is_exit_command = False
                
                exit_phrases = ["end interview", "stop the interview", "exit interview", "terminate session", "i want to quit"]
                if any(p in txt for p in exit_phrases): is_exit_command = True
                
                if len(txt.split()) <= 3 and any(w in txt for w in ["exit", "quit", "stop", "bye"]):
                    is_exit_command = True

                if is_exit_command:
                    if hasattr(self.voice_engine, 'speak'):
                        self.voice_engine.speak("Are you sure you want to end the interview?", self.detected_language)
                    else:
                        self.voice_engine.speak_stream(["Are you sure you want to end the interview?"])
                    
                    print(">> Waiting for confirmation...")
                    
                    confirm_audio = self.recorder.listen_and_record()
                    sf.write(str(temp_wav), confirm_audio, 16000)
                    confirm_text, _ = self.ears.transcribe(str(temp_wav))
                    confirm_text = confirm_text.lower()
                    print(f"[Confirmation]: {confirm_text}")
                    
                    if any(x in confirm_text for x in ["yes", "yeah", "sure", "correct", "end", "right", "bye"]):
                        if hasattr(self.voice_engine, 'speak'):
                            self.voice_engine.speak("Ending session.", self.detected_language)
                        else:
                            self.voice_engine.speak_stream(["Ending session."])
                        break
                    else:
                        if hasattr(self.voice_engine, 'speak'):
                            self.voice_engine.speak("Resuming.", self.detected_language)
                        else:
                            self.voice_engine.speak_stream(["Resuming."])
                        continue

                print("[Status] Thinking...")
                response_generator = self.brain.generate_stream(user_text, self.state.difficulty)
                
                print("[Status] Generating response...")
                if hasattr(self.voice_engine, 'speak_stream'):
                    self.next_turn_audio = self.voice_engine.speak_stream(response_generator)
                else:
                    response_text = "".join(list(response_generator))
                    print(f"[Debug] Generated response length: {len(response_text)}")
                    self.voice_engine.speak(response_text, self.detected_language)
                
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

    def end_session(self):
        print("\n--- Session Ended ---")
        
        try:
            if self.proctoring:
                self.proctoring.stop()
        except Exception as e:
            print(f"[Warning] Proctoring stop failed: {e}")
        
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
                        if Path(audio_path).exists() and i < len(history) and history[i]['role'] == 'user':
                            result = self.sentiment_analyzer.analyze_full(audio_path, history[i]['content'])
                            sentiment_results.append(result)
                    
                    if sentiment_results:
                        avg_confidence = np.mean([r['confidence_score'] for r in sentiment_results])
                        all_emotions = {}
                        for r in sentiment_results:
                            for emotion, score in r['emotions'].items():
                                all_emotions[emotion] = all_emotions.get(emotion, 0) + score
                        
                        dominant_emotion = max(all_emotions.items(), key=lambda x: x[1])[0]
                        total_fillers = sum([r['fillers']['total_fillers'] for r in sentiment_results])
                        avg_wpm = np.mean([r['speech_metrics'].get('wpm', 0) for r in sentiment_results])
                        
                        report["sentiment_analysis"] = {
                            "average_confidence": round(avg_confidence, 2),
                            "dominant_emotion": dominant_emotion,
                            "speaking_pace_wpm": round(avg_wpm, 1),
                            "total_filler_words": total_fillers,
                            "detailed_results": sentiment_results
                        }
                except Exception as e:
                    print(f"[Warning] Sentiment analysis failed: {e}")
            
            if self.proctoring:
                try:
                    violations_summary = self.proctoring.get_violations_summary()
                    report["proctoring"] = violations_summary
                except Exception as e:
                    print(f"[Warning] Proctoring summary failed: {e}")
            
            settings.TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
            filename = settings.TRANSCRIPTS_DIR / f"{self.state.session_id}_report.json"
            
            with open(filename, "w") as f:
                json.dump(report, f, indent=2)
            
            print(f"✅ Report saved to: {filename}")
            
        except Exception as e:
            print(f"\n[Error] Report generation failed: {e}")
            import traceback
            traceback.print_exc()
