import time
import json
import numpy as np
import soundfile as sf
from beaverAI.ml.src.brain.llm_engine import LLMEngine
from beaverAI.ml.src.ears.stt_engine import STTEngine
from beaverAI.ml.src.ears.vad import VoiceRecorder
from beaverAI.ml.src.voice.tts_engine import TTSEngine
from beaverAI.ml.src.brain.evaluator import Evaluator
from beaverAI.ml.src.core.session_state import SessionState
from beaverAI.ml.config import settings
from beaverAI.ml.src.core.resume_loader import ResumeLoader

class InterviewManager:
    def __init__(self):
        print("Initializing BeaverAI Engines...")
        self.state = SessionState()
        self.resume_loader = ResumeLoader()
        resume_text = self.resume_loader.load_resume()
        self.brain = LLMEngine(resume_text=resume_text)
        self.ears = STTEngine()
        self.recorder = VoiceRecorder()
        self.voice = TTSEngine(vad_module=self.recorder) 
        self.evaluator = Evaluator(settings.LLM_MODEL_PATH)
        self.next_turn_audio = None

    def _configure_session(self):
        print("\n" + "="*40 + "\n      BEAVER AI - SESSION SETUP\n" + "="*40)
        print("Please select the interview difficulty:\n [1] Easy\n [2] Medium\n [3] Hard\n [4] Extreme")
        choice = input("\nEnter choice (1-4) [Default: 2]: ").strip()
        mapping = {"1": "Easy", "2": "Medium", "3": "Hard", "4": "Extreme"}
        self.state.difficulty = mapping.get(choice, "Medium")
        print(f"\n>> Configuration Locked: {self.state.difficulty} Mode\n")
        time.sleep(1)

    def start_session(self):
        self._configure_session()
        print(f"--- Interview Session Started (ID: {self.state.session_id}) ---")
        self.voice.speak_stream([f"Hello! I am ready for the {self.state.difficulty} interview. Let's begin."])

        while self.state.is_active:
            try:
                
                print(f"\n[Status] Listening...")
                audio_data = self.recorder.listen_and_record(prepend_audio=self.next_turn_audio)
                self.next_turn_audio = None 
                
                if audio_data is None or len(audio_data) == 0: continue

                
                temp_wav = settings.BASE_DIR / "data" / "temp" / "input_buffer.wav"
                sf.write(str(temp_wav), audio_data, 16000)
                user_text = self.ears.transcribe(str(temp_wav))
                print(f"[User]: {user_text}")

                if not user_text.strip(): continue

                
                txt = user_text.lower().strip()
                is_exit_command = False
                
                
                exit_phrases = ["end interview", "stop the interview", "exit interview", "terminate session", "i want to quit"]
                if any(p in txt for p in exit_phrases): is_exit_command = True
                
                
                if len(txt.split()) <= 3 and any(w in txt for w in ["exit", "quit", "stop", "bye"]):
                    is_exit_command = True

                if is_exit_command:
                    self.voice.speak_stream(["Are you sure you want to end the interview?"])
                    print(">> Waiting for confirmation...")
                    
                    confirm_audio = self.recorder.listen_and_record()
                    sf.write(str(temp_wav), confirm_audio, 16000)
                    confirm_text = self.ears.transcribe(str(temp_wav)).lower()
                    print(f"[Confirmation]: {confirm_text}")
                    
                    if any(x in confirm_text for x in ["yes", "yeah", "sure", "correct", "end", "right", "bye"]):
                         self.voice.speak_stream(["Ending session."])
                         break
                    else:
                         self.voice.speak_stream(["Resuming."])
                         continue 

                
                print("[Status] Thinking...")
                response_generator = self.brain.generate_stream(user_text, self.state.difficulty)
                
                
                self.next_turn_audio = self.voice.speak_stream(response_generator)
                
                self.state.question_count += 1

            except KeyboardInterrupt:
                break
        
        self.end_session()

    def end_session(self):
        print("\n--- Session Ended ---")
        history = self.brain.get_history()
        if len(history) > 4:
            report = self.evaluator.generate_report(history)
            report["transcript"] = history
            settings.TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
            filename = settings.TRANSCRIPTS_DIR / f"{self.state.session_id}_report.json"
            with open(filename, "w") as f: json.dump(report, f, indent=2)
            print(f"Report saved to: {filename}")