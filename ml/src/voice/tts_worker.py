import sys
import os
import pyttsx3

def main():
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 190)
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
            
            filename, text = data.split("|", 1)
            
            if not text.strip():
                sys.stdout.write("SKIP\n")
                sys.stdout.flush()
                continue
            
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            try:
                engine.save_to_file(text, filename)
                engine.runAndWait()
                
                if os.path.exists(filename) and os.path.getsize(filename) > 0:
                    sys.stdout.write(f"DONE\n")
                else:
                    sys.stdout.write(f"FAIL\n")
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