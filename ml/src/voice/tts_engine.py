import os
import sys
import time
import subprocess
import sounddevice as sd
import soundfile as sf
import numpy as np
import threading
import queue
from config import settings

class TTSEngine:
    def __init__(self, vad_module=None):
        self.vad = vad_module
        self.audio_queue = queue.Queue()
        self.stop_signal = False
        self.worker_process = None
        
        
        self._start_worker()

    def _start_worker(self):
        worker_path = settings.BASE_DIR / "src" / "voice" / "tts_worker.py"
        
        if not worker_path.is_file():
            print(f"[TTS Error] Worker file not found: {worker_path}")
            return
        
        worker_resolved = worker_path.resolve()
        expected_dir = (settings.BASE_DIR / "src" / "voice").resolve()
        
        if not str(worker_resolved).startswith(str(expected_dir)):
            print("[TTS Error] Worker path validation failed")
            return
        
        if not worker_path.suffix == '.py':
            print("[TTS Error] Worker must be a Python file")
            return
        
        self.worker_process = subprocess.Popen(
            [sys.executable, str(worker_resolved)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1 
        )

    def speak_stream(self, text_generator):
        """Non-blocking TTS - prints immediately, audio plays in background"""
        collected_text = []
        
        print("\n[BeaverAI]:", end=" ", flush=True)
        
        for sentence in text_generator:
            if not sentence or not sentence.strip():
                continue
            
            print(sentence, end=" ", flush=True)
            collected_text.append(sentence)
        
        print()  
        
        full_text = " ".join(collected_text)
        if full_text.strip():
            threading.Thread(
                target=self._try_tts_background, 
                args=(full_text,),
                daemon=True
            ).start()
        
        return None
    
    def _try_tts_background(self, text):
        """Attempt TTS in background - failures don't affect interview"""
        try:
            if self.vad:
                self.vad.set_mode('speaking')
            
            # Skip TTS if worker process is not running properly
            if not self.worker_process or self.worker_process.poll() is not None:
                print(f"[TTS] Worker process not available, skipping audio")
                if self.vad:
                    self.vad.set_mode('listening')
                return
            
            timestamp = int(time.time() * 1000000)
            filepath = settings.BASE_DIR / "data" / "temp" / f"tts_{timestamp}.wav"
            
            msg = f"{str(filepath)}|{text}\n"
            try:
                self.worker_process.stdin.write(msg)
                self.worker_process.stdin.flush()
            except Exception as e:
                print(f"[TTS] Worker communication failed: {e}, skipping audio")
                if self.vad:
                    self.vad.set_mode('listening')
                return
            
            # Wait longer for file generation (increased from 0.5s to 2s)
            max_wait = 2.0
            wait_interval = 0.1
            elapsed = 0
            
            while elapsed < max_wait:
                if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
                    break
                time.sleep(wait_interval)
                elapsed += wait_interval
            
            if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
                try:
                    data, fs = sf.read(filepath, dtype='float32')
                    sd.play(data, samplerate=fs)
                    sd.wait()
                except Exception as e:
                    print(f"[TTS] Audio playback failed: {e}")
                finally:
                    try:
                        os.remove(filepath)
                    except:
                        pass
            else:
                print(f"[TTS] Audio file not generated, continuing without audio")
        except Exception as e:
            print(f"[TTS] Background TTS error: {e}")
        finally:
            if self.vad:
                self.vad.set_mode('listening')

    def _producer(self, text_generator):
        for sentence in text_generator:
            if sentence is None: continue
            if self.stop_signal: break
            if not sentence.strip(): continue
            
            timestamp = int(time.time() * 1000000)
            filepath = settings.BASE_DIR / "data" / "temp" / f"tts_{timestamp}.wav"
            
            try:
                msg = f"{str(filepath)}|{sentence}\n"
                self.worker_process.stdin.write(msg)
                self.worker_process.stdin.flush()
                
                start_time = time.time()
                while time.time() - start_time < 5.0:
                    if self.worker_process.poll() is not None:
                        print(f"[TTS Error] Worker process died, restarting...")
                        self._start_worker()
                        break
                    
                    try:
                        import select
                        if sys.platform == "win32":
                            resp = self.worker_process.stdout.readline()
                        else:
                            ready = select.select([self.worker_process.stdout], [], [], 0.1)
                            if ready[0]:
                                resp = self.worker_process.stdout.readline()
                            else:
                                time.sleep(0.1)
                                continue
                        
                        if "DONE" in resp or "SKIP" in resp:
                            self.audio_queue.put((sentence, str(filepath)))
                            break
                        elif "FAIL" in resp:
                            print(f"[TTS Warning] Synthesis failed for: {sentence[:30]}...")
                            break
                    except:
                        time.sleep(0.1)
                        continue
                else:
                    print(f"[TTS Warning] Timeout waiting for worker response")
                    
            except Exception as e:
                print(f"[TTS Error] Worker communication failed: {e}")
                try:
                    self.worker_process.kill()
                except:
                    pass
                self._start_worker()

        self.audio_queue.put(None)

    def _consumer(self):
        self.interruption_audio = None
        tts_failed_count = 0
        
        while True:
            if self.stop_signal:
                self._drain_queue()
                break

            try:
                item = self.audio_queue.get_nowait()
            except queue.Empty:
                
                interrupt = self._listen_during_silence(0.1)
                if interrupt is not None:
                    print("\n[!] User Interrupted (Thinking Phase).")
                    self.stop_signal = True
                    self.interruption_audio = interrupt
                    break
                continue
            
            if item is None: break
            
            text, filepath = item
            print(f"\n[BeaverAI]: {text}")
            
            if tts_failed_count > 3:
                print("[TTS] Too many failures, continuing without audio...")
                if os.path.exists(filepath):
                    try: os.remove(filepath)
                    except: pass
                continue
            
            try:
                if self.vad: self.vad.set_mode('speaking')
                
                if os.path.exists(filepath):
                    interrupted_by = self._play_with_bargein(filepath)
                    
                    try: os.remove(filepath)
                    except: pass
                        
                    if interrupted_by is not None:
                        print("\n[!] User Interrupted (Speaking Phase).")
                        self.stop_signal = True
                        self.interruption_audio = interrupted_by
                        self._drain_queue()
                        break
                else:
                    print(f"[TTS Warning] Audio file not found, skipping playback")
                    tts_failed_count += 1
                    time.sleep(0.5)
            finally:
                if self.vad: self.vad.set_mode('listening')

    def _play_with_bargein(self, file_path):
        if not os.path.exists(file_path): return None
        try:
            data, fs = sf.read(file_path, dtype='float32')
        except: return None

        chunk_size = 1024
        current_pos = 0
        
        with sd.OutputStream(samplerate=fs, channels=1) as stream:
            with sd.InputStream(samplerate=16000, channels=1) as mic:
                while current_pos < len(data):
                    if self.stop_signal: return None
                    
                    chunk = data[current_pos : current_pos + chunk_size]
                    if len(chunk) < chunk_size:
                        chunk = np.pad(chunk, (0, chunk_size - len(chunk)))
                    stream.write(chunk)
                    current_pos += chunk_size
                    
                    if self.vad:
                        mic_data, _ = mic.read(512)
                        mic_chunk = mic_data.flatten().astype(np.float32)
                        if self.vad.is_speech_chunk(mic_chunk):
                            mic_data_2, _ = mic.read(512)
                            mic_chunk_2 = mic_data_2.flatten().astype(np.float32)
                            if self.vad.is_speech_chunk(mic_chunk_2):
                                return np.concatenate((mic_chunk, mic_chunk_2))
        return None

    def _listen_during_silence(self, duration=0.1):
        if not self.vad: return None
        try:
            with sd.InputStream(samplerate=16000, channels=1) as mic:
                mic_data, _ = mic.read(int(16000 * duration))
                flat_data = mic_data.flatten().astype(np.float32)
                chunk_size = 512
                for i in range(0, len(flat_data), chunk_size):
                    chunk = flat_data[i:i+chunk_size]
                    if len(chunk) == 512 and self.vad.is_speech_chunk(chunk):
                        return flat_data
        except: pass
        return None

    def _drain_queue(self):
        while not self.audio_queue.empty():
            try:
                item = self.audio_queue.get_nowait()
                if item is None: continue
                _, f = item
                if os.path.exists(f): os.remove(f)
            except: pass