import torch
import sounddevice as sd
import numpy as np
import time
import logging

logger = logging.getLogger("VoiceRecorder")

class VoiceRecorder:
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        print("[VAD] Loading Silero VAD Model...")
        self.model, utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False,
            onnx=False
        )
        print("[VAD] Silero Model Loaded.")
        self.base_threshold = 0.5
        self.speaking_threshold = 0.85
        self.current_threshold = self.base_threshold
    
    def set_mode(self, mode):
        if mode == 'listening': self.current_threshold = self.base_threshold
        elif mode == 'speaking': self.current_threshold = self.speaking_threshold

    def listen_and_record(self, prepend_audio=None, max_duration=120):
        
        self.set_mode('listening') 
        
        buffer = []
        speech_started = False
        silence_start = None
        chunk_size = 512 
        start_time = time.time()

        
        if prepend_audio is not None and len(prepend_audio) > 0:
            print("\r[Recorder] Resuming from interruption...", end="", flush=True)
            buffer.append(prepend_audio)
            speech_started = True 
            silence_start = None
        else:
            print("\r[Recorder] Listening...", end="", flush=True)

        with sd.InputStream(samplerate=self.sample_rate, channels=1, callback=None) as stream:
            while True:
                if time.time() - start_time > max_duration:
                    print("\n[Recorder] Timeout - max recording duration reached")
                    break
                
                data, _ = stream.read(chunk_size)
                audio_chunk = data.flatten().astype(np.float32)
                buffer.append(audio_chunk)
                
                if self._check_speech(audio_chunk, self.current_threshold):
                    if not speech_started:
                        print("\r[Recorder] Speech Detected!   ", end="", flush=True)
                        speech_started = True
                    silence_start = None
                
                elif speech_started:
                    if silence_start is None:
                        silence_start = time.time()
                    elif time.time() - silence_start > 1.2: 
                        print("\n[Recorder] Processing...")
                        break
        
        if buffer:
            return np.concatenate(buffer)
        else:
            return np.array([], dtype=np.float32)
    
    def is_speech_chunk(self, audio_chunk):
        return self._check_speech(audio_chunk, threshold=0.6)

    def _check_speech(self, audio_chunk, threshold):
        if len(audio_chunk) != 512: 
            return False
        try:
            tensor = torch.from_numpy(audio_chunk)
            prob = self.model(tensor, self.sample_rate).item()
            return prob > threshold
        except Exception as e:
            logger.error(f"VAD speech check error: {e}")
            return False