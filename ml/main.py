from beaverAI.ml.src.core.interview_manager import InterviewManager

def main():
    print(" Booting up BeaverAI Core...")
    app = InterviewManager()
    app.start_session()

if __name__ == "__main__":
    main()