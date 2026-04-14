import json
import sys

from src.core.interview_manager import InterviewManager


# ── Helpers ──────────────────────────────────────────────────────────

def _pause(msg: str = "\nPress Enter to continue (or 'q' to return to menu)...") -> bool:
    """Pause and give the user a chance to return to the menu.

    Returns True if user wants to go back to menu, False otherwise.
    """
    resp = input(msg).strip().lower()
    return resp in ("q", "quit", "back", "exit", "menu")


def _print_result(result):
    """Pretty-print a feature result."""
    if result is None:
        return
    print("\n" + "=" * 50)
    print("  RESULT")
    print("=" * 50)
    if isinstance(result, str):
        print(result)
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    print("=" * 50)


# ── Feature sub-loops ────────────────────────────────────────────────

def _feature_match_report(career, resume_text, jd_text):
    """[1] Smart Match Report — loops until user exits."""
    while True:
        print("\n" + "-" * 40)
        print("  📊  SMART MATCH REPORT")
        print("-" * 40)
        if not jd_text:
            print("[!] This feature requires a JD. Please restart with a JD loaded.")
            return
        print("\n⏳ Generating match report...")
        result = career.match_report(resume_text, jd_text)
        _print_result(result)
        if _pause():
            return


def _feature_cover_letter(career, resume_text, jd_text):
    """[2] AI Cover Letter Generator — loops with tone selection."""
    while True:
        print("\n" + "-" * 40)
        print("  ✉️  AI COVER LETTER GENERATOR")
        print("-" * 40)
        if not jd_text:
            print("[!] This feature requires a JD.")
            return

        print("\nSelect tone:")
        print("  [1] Professional   [2] Enthusiastic  [3] Concise")
        print("  [4] Storytelling   [5] Startup       [6] FAANG")
        print("  [7] Service-Based  [8] Product-Based  [9] Quant")
        print("  [10] Custom (enter your own)")
        tone_map = {
            "1": "professional", "2": "enthusiastic", "3": "concise",
            "4": "storytelling", "5": "startup", "6": "faang",
            "7": "service_based", "8": "product_based", "9": "quant",
            "10": "custom",
        }
        tone_choice = input("Tone (1-10) [Default: 1]: ").strip()
        tone = tone_map.get(tone_choice, "professional")
        custom_inst = ""
        if tone == "custom":
            custom_inst = input("Describe your desired tone: ").strip()
            if not custom_inst:
                tone = "professional"
        print(f"\n⏳ Generating {tone} cover letter...")
        result = career.cover_letter(resume_text, jd_text, tone, custom_inst)
        _print_result(result)
        if _pause("\nGenerate another cover letter? (Enter to try another tone, 'q' to return): "):
            return


def _feature_skill_gap(career, resume_text, jd_text):
    """[3] Skill Gap Analyzer."""
    while True:
        print("\n" + "-" * 40)
        print("  🔍  SKILL GAP ANALYZER")
        print("-" * 40)
        if not jd_text:
            print("[!] This feature requires a JD.")
            return
        print("\n⏳ Analyzing skill gaps...")
        result = career.skill_gap(resume_text, jd_text)
        _print_result(result)
        if _pause():
            return


def _feature_roadmap(career):
    """[4] Learning Roadmap Builder — loops for multiple topics."""
    while True:
        print("\n" + "-" * 40)
        print("  🗺️  LEARNING ROADMAP BUILDER")
        print("-" * 40)
        topic = input("\nEnter topic (e.g., 'Machine Learning', 'Cloud Architecture'): ").strip()
        if not topic:
            print("[!] Topic is required.")
            if _pause():
                return
            continue
        context = input("Any context? (e.g., 'I have 2 years Python experience') [optional]: ").strip()
        print(f"\n⏳ Building roadmap for '{topic}'...")
        result = career.roadmap(topic, context)
        _print_result(result)
        if result and "mermaid_code" in result:
            show_mermaid = input("\nShow Mermaid flowchart code? [Y/n]: ").strip().lower()
            if show_mermaid in ("", "y", "yes"):
                print("\n" + "=" * 50)
                print("  MERMAID FLOWCHART CODE")
                print("=" * 50)
                print(result["mermaid_code"])
                print("=" * 50)
                print("Paste this code into https://mermaid.live to render the flowchart.")
        if _pause("\nBuild another roadmap? (Enter for another topic, 'q' to return): "):
            return


def _feature_recruiter_sim(career, resume_text, jd_text):
    """[5] Recruiter Eye Simulator."""
    while True:
        print("\n" + "-" * 40)
        print("  👀  RECRUITER EYE SIMULATOR")
        print("-" * 40)
        if not jd_text:
            print("[!] This feature requires a JD.")
            return
        print("\n⏳ Simulating recruiter review...")
        result = career.recruiter_sim(resume_text, jd_text)
        _print_result(result)
        if _pause():
            return


def _feature_project_extractor(career, resume_text, jd_text):
    """[6] Project Extractor — with optional ranking."""
    while True:
        print("\n" + "-" * 40)
        print("  📦  PROJECT EXTRACTOR")
        print("-" * 40)
        print("\n⏳ Extracting projects from resume...")
        result = career.extract_projects(resume_text)
        _print_result(result)
        if result and jd_text:
            rank_them = input("\nRank projects against JD? [Y/n]: ").strip().lower()
            if rank_them in ("", "y", "yes"):
                print("⏳ Ranking projects...")
                ranked = career.rank_projects(result, jd_text)
                _print_result(ranked)
        if _pause():
            return


def _feature_industry_calibrator(career, resume_text):
    """[7] Industry Calibrator — loops for different industries."""
    while True:
        print("\n" + "-" * 40)
        print("  🏢  INDUSTRY CALIBRATOR")
        print("-" * 40)
        print("\nSelect industry:")
        print("  [1] Startup  [2] Enterprise  [3] FAANG")
        print("  [4] Consulting  [5] Academic  [6] Government")
        mode_map = {"1": "startup", "2": "enterprise", "3": "faang",
                    "4": "consulting", "5": "academic", "6": "government"}
        mode_choice = input("Industry (1-6) [Default: 1]: ").strip()
        mode = mode_map.get(mode_choice, "startup")
        print(f"\n⏳ Calibrating for {mode}...")
        result = career.industry_calibrate(resume_text, mode)
        _print_result(result)
        if _pause("\nCalibrate for another industry? (Enter to try another, 'q' to return): "):
            return


def _feature_tone_detector(career, resume_text):
    """[8] AI Tone Detector."""
    while True:
        print("\n" + "-" * 40)
        print("  🎯  AI TONE DETECTOR")
        print("-" * 40)
        text = input("\nPaste text to analyze (or press Enter to use resume): ").strip()
        if not text:
            text = resume_text
        result = career.tone_detect(text)
        _print_result(result)
        if _pause("\nAnalyze another text? (Enter for another, 'q' to return): "):
            return


def _feature_bias_detector(career, resume_text):
    """[9] Bias & Redundancy Detector."""
    while True:
        print("\n" + "-" * 40)
        print("  ⚖️  BIAS & REDUNDANCY DETECTOR")
        print("-" * 40)
        text = input("\nPaste text to analyze (or press Enter to use resume): ").strip()
        if not text:
            text = resume_text
        result = career.bias_detect(text)
        _print_result(result)
        if _pause("\nAnalyze another text? (Enter for another, 'q' to return): "):
            return


def _feature_add_project(career):
    """[10] Add Project (manual/GitHub) — loops for multiple projects."""
    while True:
        print("\n" + "-" * 40)
        print("  ➕  ADD PROJECT")
        print("-" * 40)
        print("\n  [A] Add project manually")
        print("  [B] Import from GitHub URL")
        print("  [L] List stored projects")
        print("  [Q] Return to menu")

        sub = input("\nChoice (A/B/L/Q): ").strip().upper()

        if sub == "Q":
            return

        if sub == "A":
            title = input("  Project title: ").strip()
            desc = input("  Description: ").strip()
            skills = input("  Skills used (comma separated): ").strip()
            tools = input("  Tools used (comma separated): ").strip()
            github = input("  GitHub link (optional): ").strip()
            dates = input("  Dates (optional): ").strip()
            impact = input("  Impact / result (optional): ").strip()
            role = input("  Your role (optional): ").strip()
            team_size = input("  Team size (optional): ").strip()

            fields = {
                "title": title,
                "description": desc,
                "skills_used": [s.strip() for s in skills.split(",") if s.strip()] if skills else [],
                "tools_used": [t.strip() for t in tools.split(",") if t.strip()] if tools else [],
                "github_link": github,
                "dates": dates or "not specified",
                "impact": impact or "not specified",
                "role": role,
                "team_size": team_size,
            }
            result = career.add_project_manual(fields)
            _print_result(result)

        elif sub == "B":
            url = input("  GitHub repo URL: ").strip()
            if url:
                print("⏳ Extracting from GitHub...")
                result = career.extract_project_github(url)
                _print_result(result)
            else:
                print("[!] URL is required.")

        elif sub == "L":
            all_projects = career.get_all_projects()
            if all_projects:
                print(f"\n  📦 Total projects in store: {len(all_projects)}")
                for i, p in enumerate(all_projects):
                    name = p.get("name", "Untitled")
                    source = p.get("source", "?")
                    tech = ", ".join(p.get("tech_stack", [])[:5])
                    print(f"    [{i+1}] {name} ({source}) — {tech}")
            else:
                print("  No projects stored yet.")

        print(f"\n  📦 Total projects: {len(career.get_all_projects())}")


def _feature_jd_manager(career):
    """[11] JD Manager — add text/URL, list stored JDs."""
    while True:
        print("\n" + "-" * 40)
        print("  📋  JD MANAGER")
        print("-" * 40)
        print("\n  [A] Add JD from text")
        print("  [B] Add JD from URL")
        print("  [L] List stored JDs")
        print("  [Q] Return to menu")

        sub = input("\nChoice (A/B/L/Q): ").strip().upper()

        if sub == "Q":
            return

        if sub == "A":
            label = input("  Label (e.g. 'Google SWE Intern'): ").strip()
            print("  Paste JD text (press Enter twice to finish):")
            lines = []
            while True:
                line = input()
                if line == "":
                    if lines and lines[-1] == "":
                        break
                    lines.append("")
                else:
                    lines.append(line)
            jd_input = "\n".join(lines).strip()
            if jd_input:
                result = career.add_jd_text(jd_input, label)
                _print_result(result)
            else:
                print("[!] No text entered.")

        elif sub == "B":
            url = input("  Job posting URL: ").strip()
            if url:
                print("⏳ Scraping JD from URL...")
                result = career.add_jd_url(url)
                _print_result(result)
            else:
                print("[!] URL is required.")

        elif sub == "L":
            stored = career.list_jds()
            if stored:
                print("\n  Stored JDs:")
                for i, jd in enumerate(stored):
                    print(f"    [{i+1}] {jd.get('label', 'N/A')} ({jd.get('word_count', '?')} words, {jd.get('source', '?')})")
            else:
                print("  No JDs stored yet.")


def _feature_resume_parser(career, resume_text):
    """[12] Resume Parser — parse and optionally view parsed resumes."""
    while True:
        print("\n" + "-" * 40)
        print("  📄  RESUME PARSER")
        print("-" * 40)
        print("\n  [P] Parse current resume")
        print("  [L] List parsed resumes")
        print("  [V] View a parsed resume")
        print("  [Q] Return to menu")

        sub = input("\nChoice (P/L/V/Q): ").strip().upper()

        if sub == "Q":
            return

        if sub == "P":
            label = input("  Label for this resume (or press Enter for auto): ").strip()
            print("\n⏳ Parsing resume into structured format...")
            result = career.parse_resume(resume_text, label)
            _print_result(result)

        elif sub == "L":
            resumes = career.list_parsed_resumes()
            if resumes:
                print("\n  Parsed resumes:")
                for r in resumes:
                    print(f"    [{r['id']}] {r['label']} (parsed {r['parsed_at'][:10]})")
            else:
                print("  No parsed resumes yet. Use [P] to parse one.")

        elif sub == "V":
            resumes = career.list_parsed_resumes()
            if not resumes:
                print("  No parsed resumes yet.")
                continue
            for r in resumes:
                print(f"    [{r['id']}] {r['label']}")
            rid = input("  Enter resume ID to view: ").strip()
            try:
                parsed = career.get_parsed_resume(int(rid))
                if parsed:
                    _print_result(parsed.get("parsed"))
                else:
                    print("[!] Resume not found.")
            except (ValueError, TypeError):
                print("[!] Invalid ID.")


def _feature_smart_selector(career, jd_text):
    """[13] Smart Project Selector — select resume + JD + projects → ranked LaTeX."""
    while True:
        print("\n" + "-" * 40)
        print("  🎯  SMART PROJECT SELECTOR")
        print("-" * 40)

        # Check for parsed resumes
        resumes = career.list_parsed_resumes()
        if not resumes:
            print("[!] No parsed resumes. Run option [12] first to parse your resume.")
            if _pause():
                return
            continue

        print("\n  Parsed resumes:")
        for r in resumes:
            print(f"    [{r['id']}] {r['label']} (parsed {r['parsed_at'][:10]})")

        rid = input("  Select resume ID: ").strip()
        try:
            resume_parsed = career.get_parsed_resume(int(rid))
        except (ValueError, TypeError):
            print("[!] Invalid ID.")
            continue

        if not resume_parsed:
            print("[!] Resume not found.")
            continue

        # Select JD
        stored_jds = career.list_jds()
        active_jd = jd_text
        if stored_jds:
            print("\n  Available JDs:")
            print("    [0] Use currently loaded JD")
            for i, jd in enumerate(stored_jds):
                print(f"    [{i+1}] {jd.get('label', 'N/A')}")
            jd_choice = input("  Select JD (0 for loaded): ").strip()
            if jd_choice != "0":
                try:
                    selected_jd = career.get_jd_by_index(int(jd_choice) - 1)
                    if selected_jd:
                        active_jd = selected_jd["text"]
                except (ValueError, TypeError):
                    pass

        if not active_jd:
            print("[!] No JD available. Load a JD on startup or add one via option [11].")
            if _pause():
                return
            continue

        extra = career.get_all_projects()
        resume_projects = resume_parsed["parsed"].get("projects", [])
        print(f"\n⏳ Ranking {len(resume_projects)} resume + {len(extra)} extra projects...")
        result = career.select_and_generate_latex(
            resume_parsed["parsed"], active_jd, extra
        )
        if result and result.get("ranked_projects"):
            _print_result(result)
            if "latex_code" in result:
                show_latex = input("\nShow LaTeX code? [Y/n]: ").strip().lower()
                if show_latex in ("", "y", "yes"):
                    print("\n" + "=" * 50)
                    print("  LATEX PROJECT CODE")
                    print("=" * 50)
                    print(result["latex_code"])
                    print("=" * 50)
        elif result and "error" in result:
            print(f"\n[!] {result['error']}")
        else:
            print("\n[!] No ranked projects returned. This can happen if:")
            print("    - The LLM could not parse projects from the resume")
            print("    - Try running [12] Resume Parser first, then [6] Project Extractor")
            _print_result(result)

        if _pause("\nRun selector again? (Enter to retry, 'q' to return): "):
            return


def _feature_project_latex(career):
    """[14] Generate Project LaTeX for stored projects."""
    while True:
        print("\n" + "-" * 40)
        print("  📝  GENERATE PROJECT LATEX")
        print("-" * 40)

        all_projects = career.get_all_projects()
        if not all_projects:
            print("[!] No projects stored. Use option [6] or [10] first.")
            if _pause():
                return
            continue

        print(f"\n  Projects available ({len(all_projects)}):")
        for i, p in enumerate(all_projects):
            print(f"    [{i+1}] {p.get('name', 'Untitled')}")

        print(f"\n⏳ Generating LaTeX for {len(all_projects)} projects...")
        latex = career.generate_project_latex(all_projects)
        print("\n" + "=" * 50)
        print("  LATEX PROJECT CODE")
        print("=" * 50)
        print(latex)
        print("=" * 50)

        if _pause():
            return


# ── Career CLI ───────────────────────────────────────────────────────

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
        print("\n" + "-" * 60)
        print("  CAREER FEATURES")
        print("-" * 60)
        print("  [1]  Smart Match Report          (resume + JD)")
        print("  [2]  AI Cover Letter Generator    (resume + JD)")
        print("  [3]  Skill Gap Analyzer           (resume + JD)")
        print("  [4]  Learning Roadmap Builder     (topic)")
        print("  [5]  Recruiter Eye Simulator      (resume + JD)")
        print("  [6]  Project Extractor            (resume)")
        print("  [7]  Industry Calibrator          (resume)")
        print("  [8]  AI Tone Detector             (text)")
        print("  [9]  Bias & Redundancy Detector   (text)")
        print("  ─── NEW ───────────────────────────────────")
        print("  [10] Add Project (manual/GitHub)  (interactive)")
        print("  [11] JD Manager (add/list)        (text/URL)")
        print("  [12] Resume Parser                (resume)")
        print("  [13] Smart Project Selector       (resume + JD)")
        print("  [14] Generate Project LaTeX       (projects)")
        print("  [0]  Exit")
        print("-" * 60)

        choice = input("\nSelect feature (0-14): ").strip()

        if choice == "0":
            print("Goodbye!")
            try:
                if hasattr(career, "llm") and career._llm is not None:
                    career.llm.unload_model()
                    print("[System] VRAM cleared for Ollama LLM.")
            except Exception:
                pass
            break
        elif choice == "1":
            _feature_match_report(career, resume_text, jd_text)
        elif choice == "2":
            _feature_cover_letter(career, resume_text, jd_text)
        elif choice == "3":
            _feature_skill_gap(career, resume_text, jd_text)
        elif choice == "4":
            _feature_roadmap(career)
        elif choice == "5":
            _feature_recruiter_sim(career, resume_text, jd_text)
        elif choice == "6":
            _feature_project_extractor(career, resume_text, jd_text)
        elif choice == "7":
            _feature_industry_calibrator(career, resume_text)
        elif choice == "8":
            _feature_tone_detector(career, resume_text)
        elif choice == "9":
            _feature_bias_detector(career, resume_text)
        elif choice == "10":
            _feature_add_project(career)
        elif choice == "11":
            _feature_jd_manager(career)
        elif choice == "12":
            _feature_resume_parser(career, resume_text)
        elif choice == "13":
            _feature_smart_selector(career, jd_text)
        elif choice == "14":
            _feature_project_latex(career)
        else:
            print("[!] Invalid choice. Try again.")


def main():
    print("\n" + "=" * 50)
    print("           BEAVER AI   ")
    print("=" * 50)
    print("\n  Select mode:")
    print("  [1] AI Interview")
    print("  [2] Career Management System")

    mode = input("\n  Enter choice (1-2) [Default: 1]: ").strip()

    if mode == "2":
        run_career_cli()
    else:
        print("\n Booting up intrv.ai Interview Core...")
        app = InterviewManager()
        app.start_session()


if __name__ == "__main__":
    main()