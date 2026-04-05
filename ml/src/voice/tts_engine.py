"""TTS Engine — edge-tts (primary) with piper-tts (offline fallback).

Uses Microsoft Edge's neural TTS voices via edge_tts library (free, no API key).
Falls back to Piper TTS for offline use when internet is unavailable.
"""
import asyncio
import io
import logging
import os
import tempfile
import time
import wave
from pathlib import Path
from typing import Generator

import numpy as np
import sounddevice as sd
import soundfile as sf

from config import settings

logger = logging.getLogger("TTSEngine")

# Edge-TTS voice selection
EDGE_VOICE = "en-US-GuyNeural"
EDGE_VOICE_FALLBACKS = ["en-US-ChristopherNeural", "en-US-EricNeural", "en-US-AndrewNeural"]

# Piper model config
PIPER_MODEL_PATH = settings.TTS_MODEL_PATH

# Attempt imports
_edge_tts_available = False
try:
    import edge_tts
    _edge_tts_available = True
except ImportError:
    logger.warning("edge-tts not installed. Install with: pip install edge-tts")

_piper_available = False
try:
    from piper import PiperVoice
    _piper_available = True
except ImportError:
    logger.warning("piper-tts not installed. Install with: pip install piper-tts")


class TTSEngine:
    """Text-to-Speech engine with edge-tts (online) and piper (offline) backends."""

    def __init__(self, vad_module=None) -> None:
        self.vad = vad_module
        self._piper_voice = None
        self._edge_failed_count = 0
        self._max_edge_failures = 5

        # Ensure temp directory exists
        self._temp_dir = settings.BASE_DIR / "data" / "temp"
        self._temp_dir.mkdir(parents=True, exist_ok=True)

        # Create or get event loop for async edge-tts
        try:
            self._loop = asyncio.new_event_loop()
        except Exception:
            self._loop = asyncio.get_event_loop()

        logger.info(f"TTS Engine initialized (edge-tts: {_edge_tts_available}, piper: {_piper_available})")

    def _get_piper_voice(self):
        """Lazy-load Piper voice model."""
        if self._piper_voice is None and _piper_available:
            model_path = PIPER_MODEL_PATH
            if model_path.exists():
                try:
                    self._piper_voice = PiperVoice.load(str(model_path))
                    logger.info(f"Piper voice loaded: {model_path.name}")
                except Exception as e:
                    logger.error(f"Failed to load Piper voice: {e}")
            else:
                logger.warning(f"Piper model not found at: {model_path}")
        return self._piper_voice

    # ── Public API ────────────────────────────────────────────────

    def interrupt(self) -> None:
        """Interrupts playback immediately and clears the synthesis queues."""
        self._interrupted = True
        if hasattr(self, 'interrupt_event'):
            self.interrupt_event.set()
        try:
            sd.stop()
        except Exception as e:
            logger.warning(f"Error stopping sounddevice: {e}")

    def speak_text(self, text: str) -> None:
        """Speak a single text string synchronously."""
        self._interrupted = False
        print(f"\n[intrv.ai]: {text}")
        self._synthesize_and_play(text)

    def speak_stream(self, text_generator: Generator) -> None:
        """Stream sentences to TTS, synthesize concurrently, and play sequentially."""
        import queue
        import threading

        self._interrupted = False
        self.interrupt_event = threading.Event()
        
        text_queue = queue.Queue()
        audio_queue = queue.Queue()
        
        # Thread 1: Synthesizer Worker
        def synthesizer_worker():
            while not self.interrupt_event.is_set():
                try:
                    text = text_queue.get(timeout=0.5)
                    if text is None:  # EOF
                        audio_queue.put(None)
                        break
                    
                    audio_path = None
                    if _edge_tts_available and self._edge_failed_count < self._max_edge_failures:
                        audio_path = self._synthesize_edge(text)
                        if not audio_path:
                            self._edge_failed_count += 1
                            
                    if not audio_path and _piper_available:
                        audio_path = self._synthesize_piper(text)
                        
                    if audio_path:
                        audio_queue.put(audio_path)
                    text_queue.task_done()
                except queue.Empty:
                    continue

        # Thread 2: Player Worker
        def player_worker():
            while not self.interrupt_event.is_set():
                try:
                    audio_path = audio_queue.get(timeout=0.5)
                    if audio_path is None:  # EOF
                        break
                        
                    if not self.interrupt_event.is_set():
                        try:
                            data, samplerate = sf.read(audio_path, dtype='float32')
                            sd.play(data, samplerate=samplerate)
                            # Wait loop that can be interrupted
                            while sd.get_stream() and sd.get_stream().active and not self.interrupt_event.is_set():
                                time.sleep(0.05)
                            
                            if self.interrupt_event.is_set():
                                sd.stop()
                        except Exception as e:
                            logger.warning(f"Audio playback error: {e}")
                            
                        # Cleanup
                        try:
                            if os.path.exists(audio_path):
                                os.remove(audio_path)
                        except OSError:
                            pass
                    audio_queue.task_done()
                except queue.Empty:
                    continue

        # Thread 3: Barge-in Interrupt Listener
        def interrupt_listener():
            if not self.vad:
                return
            try:
                with sd.InputStream(samplerate=self.vad.sample_rate, channels=1) as stream:
                    consecutive_speech = 0
                    local_interrupt_buffer = []

                    while not self.interrupt_event.is_set():
                        data, _ = stream.read(512)
                        audio_chunk = data.flatten().astype(np.float32)
                        
                        if self.vad._check_speech(audio_chunk, threshold=0.85):
                            consecutive_speech += 1
                            local_interrupt_buffer.append(audio_chunk)
                            
                            if consecutive_speech >= 3:  
                                logger.info("Barge-in detected! Interrupting TTS...")
                                self.vad.interrupt_buffer.extend(local_interrupt_buffer)
                                self.interrupt()
                                break
                        else:
                            consecutive_speech = 0
                            local_interrupt_buffer = []

            except Exception as e:
                logger.warning(f"Interrupt listener error: {e}")

        # Start workers
        t1 = threading.Thread(target=synthesizer_worker, daemon=True)
        t2 = threading.Thread(target=player_worker, daemon=True)
        
        try:
            from config import settings
            enable_barge_in = getattr(settings, 'ENABLE_LOCAL_BARGE_IN', False)
        except ImportError:
            enable_barge_in = False
            
        t3 = None
        if enable_barge_in:
            t3 = threading.Thread(target=interrupt_listener, daemon=True)
        
        if self.vad:
            self.vad.set_mode('speaking')
            
        t1.start()
        t2.start()
        if t3:
            t3.start()

        # Producer Loop
        collected = []
        try:
            print("\n[intrv.ai]:", end=" ", flush=True)
            for sentence in text_generator:
                if self.interrupt_event.is_set():
                    break
                if not sentence or not sentence.strip():
                    continue
                print(sentence, end=" ", flush=True)
                collected.append(sentence)
                text_queue.put(sentence)
            print()
        except Exception as e:
            logger.error(f"Stream interrupted: {e}")

        # Signal completion
        text_queue.put(None)
        
        # Wait for threads to complete cleanly if not interrupted
        while t1.is_alive() or t2.is_alive():
            if self.interrupt_event.is_set():
                break
            time.sleep(0.1)
            
        if self.vad:
            self.vad.set_mode('listening')
            
        return None

    # ── Core Synthesis ────────────────────────────────────────────

    def _synthesize_and_play(self, text: str) -> None:
        """Try edge-tts, fall back to piper, play audio."""
        if not text.strip():
            return

        try:
            if self.vad:
                self.vad.set_mode('speaking')

            audio_path = None

            # Primary: edge-tts (online, neural quality)
            if _edge_tts_available and self._edge_failed_count < self._max_edge_failures:
                audio_path = self._synthesize_edge(text)
                if not audio_path:
                    self._edge_failed_count += 1
                    logger.warning(f"edge-tts failed ({self._edge_failed_count}/{self._max_edge_failures})")

            # Fallback: piper (offline, still good quality)
            if not audio_path and _piper_available:
                audio_path = self._synthesize_piper(text)

            # Play audio
            if audio_path and os.path.exists(audio_path):
                self._play_audio(audio_path)
                try:
                    os.remove(audio_path)
                except OSError:
                    pass
            else:
                logger.debug("No TTS audio generated, continuing silently")

        except Exception as e:
            logger.error(f"TTS error: {e}")
        finally:
            if self.vad:
                self.vad.set_mode('listening')

    def _synthesize_edge(self, text: str) -> str | None:
        """Generate audio using edge-tts (Microsoft neural voices)."""
        timestamp = int(time.time() * 1000000)
        output_path = str(self._temp_dir / f"tts_{timestamp}.mp3")

        try:
            async def _generate():
                communicate = edge_tts.Communicate(text, EDGE_VOICE)
                await communicate.save(output_path)

            self._loop.run_until_complete(_generate())

            if os.path.exists(output_path) and os.path.getsize(output_path) > 100:
                logger.debug(f"edge-tts generated {os.path.getsize(output_path)}b")
                return output_path

        except Exception as e:
            logger.warning(f"edge-tts synthesis failed: {e}")
            # Try cleanup
            try:
                if os.path.exists(output_path):
                    os.remove(output_path)
            except OSError:
                pass

        return None

    def _synthesize_piper(self, text: str) -> str | None:
        """Generate audio using Piper TTS (offline neural)."""
        voice = self._get_piper_voice()
        if not voice:
            return None

        timestamp = int(time.time() * 1000000)
        output_path = str(self._temp_dir / f"tts_{timestamp}.wav")

        try:
            # Piper outputs raw PCM, write to WAV
            audio_bytes = io.BytesIO()
            with wave.open(audio_bytes, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(voice.config.sample_rate)

                for audio_chunk in voice.synthesize_stream_raw(text):
                    wav_file.writeframes(audio_chunk)

            with open(output_path, 'wb') as f:
                f.write(audio_bytes.getvalue())

            if os.path.exists(output_path) and os.path.getsize(output_path) > 100:
                logger.debug(f"piper generated {os.path.getsize(output_path)}b")
                return output_path

        except Exception as e:
            logger.warning(f"Piper synthesis failed: {e}")
            try:
                if os.path.exists(output_path):
                    os.remove(output_path)
            except OSError:
                pass

        return None

    def _play_audio(self, file_path: str) -> None:
        """Play an audio file (MP3 or WAV) through speakers."""
        try:
            data, samplerate = sf.read(file_path, dtype='float32')
            sd.play(data, samplerate=samplerate)
            sd.wait()
        except Exception as e:
            logger.warning(f"Audio playback failed: {e}")