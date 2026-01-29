import os
from pathlib import Path
from pypdf import PdfReader
from config import settings

class ResumeLoader:
    def __init__(self):
        self.resume_dir = settings.BASE_DIR / "data" / "resumes"
        self.resume_dir.mkdir(parents=True, exist_ok=True)

    def load_resume(self):
        print(f"Scanning for resumes in: {self.resume_dir}")
        pdfs = list(self.resume_dir.glob("*.pdf"))
        
        if not pdfs:
            print("[ResumeLoader] No resume found. Using Generic Interview Mode.")
            return None
        
        target_file = pdfs[0]
        print(f"[ResumeLoader] Found resume: {target_file.name}")
        
        text = ""
        try:
            reader = PdfReader(target_file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
            text = " ".join(text.split())
            return text[:3000]
        except Exception as e:
            print(f"[ResumeLoader] Error reading PDF: {e}")
            return None