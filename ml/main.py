import json
import sys

from src.core.interview_manager import InterviewManager


def run_career_cli():
    """Interactive CLI for the Career Management System."""
    from src.career.career_orchestrator import CareerOrchestrator
    from src.core.resume_loader import ResumeLoader

    print("\n" + "=" * 50)
    print("    BEAVER AI — CAREER MANAGEMENT SYSTEM")
    print("=" * 50)

    # Load resume
    loader = ResumeLoader()
    resume_data = loader.load_resume()
    resume_text = resume_data.raw_text if hasattr(resume_data, 'raw_text') else str(resume_data)
    print(f"[✓] Resume loaded ({len(resume_text.split())} words)")

    # Optionally load JD
    jd_text = ""
    load_jd = input("\nLoad a job description? [Y/n]: ").strip().lower()
    if load_jd in ("", "y", "yes"):
        try:
            from src.core.jd_loader import JDLoader
            jd_loader = JDLoader()
            jd_text = jd_loader.load_jd() or ""
            if jd_text:
                print(f"[✓] JD loaded ({len(jd_text.split())} words)")
            else:
                print("[!] No JD found — some features will be limited")
        except Exception as e:
            print(f"[!] JD loading failed: {e}")

    career = CareerOrchestrator()

    while True:
        print("\n" + "-" * 50)
        print("  CAREER FEATURES")
        print("-" * 50)
        print("  [1]  Smart Match Report          (resume + JD)")
        print("  [2]  AI Cover Letter Generator    (resume + JD)")
        print("  [3]  Skill Gap Analyzer           (resume + JD)")
        print("  [4]  Learning Roadmap Builder     (topic)")
        print("  [5]  Recruiter Eye Simulator      (resume + JD)")
        print("  [6]  Project Extractor            (resume)")
        print("  [7]  Industry Calibrator          (resume)")
        print("  [8]  AI Tone Detector             (text)")
        print("  [9]  Bias & Redundancy Detector   (text)")
        print("  [0]  Exit")
        print("-" * 50)

        choice = input("\nSelect feature (0-9): ").strip()

        if choice == "0":
            print("Goodbye!")
            break

        result = None

        if choice == "1":
            if not jd_text:
                print("[!] This feature requires a JD. Please restart with a JD loaded.")
                continue
            print("\n⏳ Generating match report...")
            result = career.match_report(resume_text, jd_text)

        elif choice == "2":
            if not jd_text:
                print("[!] This feature requires a JD.")
                continue
            print("\nSelect tone: [1] Professional  [2] Enthusiastic  [3] Concise  [4] Storytelling")
            tone_map = {"1": "professional", "2": "enthusiastic", "3": "concise", "4": "storytelling"}
            tone_choice = input("Tone (1-4) [Default: 1]: ").strip()
            tone = tone_map.get(tone_choice, "professional")
            print(f"\n⏳ Generating {tone} cover letter...")
            result = career.cover_letter(resume_text, jd_text, tone)

        elif choice == "3":
            if not jd_text:
                print("[!] This feature requires a JD.")
                continue
            print("\n⏳ Analyzing skill gaps...")
            result = career.skill_gap(resume_text, jd_text)

        elif choice == "4":
            topic = input("\nEnter topic (e.g., 'Machine Learning', 'Cloud Architecture'): ").strip()
            if not topic:
                print("[!] Topic is required.")
                continue
            context = input("Any context? (e.g., 'I have 2 years Python experience') [optional]: ").strip()
            print(f"\n⏳ Building roadmap for '{topic}'...")
            result = career.roadmap(topic, context)

        elif choice == "5":
            if not jd_text:
                print("[!] This feature requires a JD.")
                continue
            print("\n⏳ Simulating recruiter review...")
            result = career.recruiter_sim(resume_text, jd_text)

        elif choice == "6":
            print("\n⏳ Extracting projects from resume...")
            result = career.extract_projects(resume_text)
            if result and jd_text:
                rank_them = input("\nRank projects against JD? [Y/n]: ").strip().lower()
                if rank_them in ("", "y", "yes"):
                    print("⏳ Ranking projects...")
                    result = career.rank_projects(result, jd_text)

        elif choice == "7":
            print("\nSelect industry: [1] Startup  [2] Enterprise  [3] FAANG  [4] Consulting  [5] Academic  [6] Government")
            mode_map = {"1": "startup", "2": "enterprise", "3": "faang", "4": "consulting", "5": "academic", "6": "government"}
            mode_choice = input("Industry (1-6) [Default: 1]: ").strip()
            mode = mode_map.get(mode_choice, "startup")
            print(f"\n⏳ Calibrating for {mode}...")
            result = career.industry_calibrate(resume_text, mode)

        elif choice == "8":
            text = input("\nPaste text to analyze (or press Enter to use resume): ").strip()
            if not text:
                text = resume_text
            result = career.tone_detect(text)

        elif choice == "9":
            text = input("\nPaste text to analyze (or press Enter to use resume): ").strip()
            if not text:
                text = resume_text
            result = career.bias_detect(text)

        else:
            print("[!] Invalid choice. Try again.")
            continue

        if result:
            print("\n" + "=" * 50)
            print("  RESULT")
            print("=" * 50)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print("=" * 50)


def main():
    print("\n" + "=" * 50)
    print("         🦫  BEAVER AI  🦫")
    print("=" * 50)
    print("\n  Select mode:")
    print("  [1] AI Interview")
    print("  [2] Career Management System")

    mode = input("\n  Enter choice (1-2) [Default: 1]: ").strip()

    if mode == "2":
        run_career_cli()
    else:
        print("\n Booting up BeaverAI Interview Core...")
        app = InterviewManager()
        app.start_session()


if __name__ == "__main__":
    main()