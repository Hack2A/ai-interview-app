import os
import sys
import time
import subprocess
import sounddevice as sd
import soundfile as sf
import numpy as np
import threading
import queue
from beaverAI.ml.config import settings

class TTSEngine:
    def __init__(self, vad_module=None):
        self.vad = vad_module
        self.audio_queue = queue.Queue()
        self.stop_signal = False
        self.worker_process = None
        
        
        self._start_worker()

    def _start_worker(self):
        worker_path = settings.BASE_DIR / "src" / "voice" / "tts_worker.py"
        self.worker_process = subprocess.Popen(
            [sys.executable, str(worker_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1 
        )

    def speak_stream(self, text_generator):
        self.stop_signal = False
        self.audio_queue = queue.Queue()
        
        gen_thread = threading.Thread(target=self._producer, args=(text_generator,))
        gen_thread.start()
        
        self._consumer()
        gen_thread.join()
        
        return self.interruption_audio

    def _producer(self, text_generator):
        for sentence in text_generator:
            if self.stop_signal: break
            if not sentence.strip(): continue
            
            timestamp = int(time.time() * 1000000)
            filepath = settings.BASE_DIR / "data" / "temp" / f"tts_{timestamp}.wav"
            
            
            try:
                msg = f"{str(filepath)}|{sentence}\n"
                self.worker_process.stdin.write(msg)
                self.worker_process.stdin.flush()
                
                
                resp = self.worker_process.stdout.readline()
                
                if "DONE" in resp:
                    self.audio_queue.put((sentence, str(filepath)))
            except Exception as e:
                print(f"[TTS Error] Worker failed: {e}")
                self._start_worker() 

        self.audio_queue.put(None)

    def _consumer(self):
        self.interruption_audio = None
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
            
            if self.vad: self.vad.set_mode('speaking')
            interrupted_by = self._play_with_bargein(filepath)
            if self.vad: self.vad.set_mode('listening')
            
            if os.path.exists(filepath):
                try: os.remove(filepath)
                except: pass
                
            if interrupted_by is not None:
                print("\n[!] User Interrupted (Speaking Phase).")
                self.stop_signal = True
                self.interruption_audio = interrupted_by
                self._drain_queue()
                break

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
                _, f = self.audio_queue.get_nowait()
                if os.path.exists(f): os.remove(f)
            except: pass