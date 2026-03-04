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

    def speak_text(self, text: str) -> None:
        """Speak a single text string synchronously."""
        print(f"\n[BeaverAI]: {text}")
        self._synthesize_and_play(text)

    def speak_stream(self, text_generator: Generator) -> None:
        """Collect streamed text, print it, then speak the full result."""
        collected = []

        print("\n[BeaverAI]:", end=" ", flush=True)

        for sentence in text_generator:
            if not sentence or not sentence.strip():
                continue
            print(sentence, end=" ", flush=True)
            collected.append(sentence)

        print()

        full_text = " ".join(collected).strip()
        if full_text:
            self._synthesize_and_play(full_text)

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