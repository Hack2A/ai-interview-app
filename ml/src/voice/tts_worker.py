import sys
import pyttsx3


def main():
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 190)
    except:
        return

   
    sys.stderr.write("READY\n")
    sys.stderr.flush()

    while True:
        try:
            
            line = sys.stdin.readline()
            if not line: break
            
            data = line.strip()
            if "|" not in data: continue
            
            filename, text = data.split("|", 1)
            
            
            engine.save_to_file(text, filename)
            engine.runAndWait()
            
            
            sys.stdout.write(f"DONE\n")
            sys.stdout.flush()
            
        except Exception:
            sys.stdout.write("ERROR\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()