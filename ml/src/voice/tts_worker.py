"""TTS Worker subprocess — receives text via stdin, generates WAV files via pyttsx3."""
import sys
import os
import pyttsx3
from pathlib import Path

# Project root for path validation
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ALLOWED_TEMP_DIR = PROJECT_ROOT / "data" / "temp"


def _is_safe_path(filepath: str) -> bool:
    """Validate that the filepath is within the project's temp directory."""
    try:
        resolved = Path(filepath).resolve()
        return str(resolved).startswith(str(ALLOWED_TEMP_DIR.resolve()))
    except (ValueError, OSError):
        return False


def main():
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 190)
        # Try to set a natural-sounding voice
        voices = engine.getProperty('voices')
        for voice in voices:
            if 'david' in voice.name.lower() or 'mark' in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
    except Exception as e:
        sys.stderr.write(f"ERROR: Failed to init TTS: {e}\n")
        sys.stderr.flush()
        return

    sys.stderr.write("READY\n")
    sys.stderr.flush()

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break

            data = line.strip()
            if "|" not in data:
                sys.stdout.write("SKIP\n")
                sys.stdout.flush()
                continue

            filepath, text = data.split("|", 1)

            if not text.strip():
                sys.stdout.write("SKIP\n")
                sys.stdout.flush()
                continue

            # Validate path is within project temp directory
            if not filepath or '..' in filepath or not _is_safe_path(filepath):
                sys.stderr.write(f"WARN: Rejected path: {filepath}\n")
                sys.stderr.flush()
                sys.stdout.write("SKIP\n")
                sys.stdout.flush()
                continue

            safe_path = Path(filepath).resolve()
            safe_path.parent.mkdir(parents=True, exist_ok=True)

            try:
                engine.save_to_file(text, str(safe_path))
                engine.runAndWait()

                if safe_path.exists() and safe_path.stat().st_size > 0:
                    sys.stderr.write(f"OK: Generated {safe_path.stat().st_size}b -> {safe_path.name}\n")
                    sys.stderr.flush()
                    sys.stdout.write("DONE\n")
                else:
                    sys.stderr.write(f"WARN: File not created at {safe_path}\n")
                    sys.stderr.flush()
                    sys.stdout.write("FAIL\n")
            except Exception as e:
                sys.stderr.write(f"ERROR: Synthesis failed: {e}\n")
                sys.stderr.flush()
                sys.stdout.write("FAIL\n")

            sys.stdout.flush()

        except Exception as e:
            sys.stderr.write(f"ERROR: {e}\n")
            sys.stderr.flush()
            sys.stdout.write("ERROR\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()