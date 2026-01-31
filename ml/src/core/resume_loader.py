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
            print("[ResumeLoader] No resume found. Proceeding without resume context.")
            return None
        
        target_pdf = pdfs[0]
        print(f"[ResumeLoader] Found resume: {target_pdf.name}")
        
        try:
            return self._load_pdf(target_pdf)
        except Exception as e:
            print(f"[ResumeLoader] Error reading PDF: {e}")
            return None
    
    def _load_pdf(self, file_path):
        MAX_FILE_SIZE = 10 * 1024 * 1024
        
        if not file_path.is_file():
            raise ValueError("Invalid file path")
        
        if not file_path.suffix.lower() == '.pdf':
            raise ValueError("File must be PDF")
        
        file_size = file_path.stat().st_size
        if file_size > MAX_FILE_SIZE:
            raise ValueError(f"File too large: {file_size} bytes (max 10MB)")
        
        if file_size == 0:
            raise ValueError("File is empty")
        
        try:
            file_path_resolved = file_path.resolve()
            if not str(file_path_resolved).startswith(str(self.resume_dir.resolve())):
                raise ValueError("Path traversal detected")
        except:
            raise ValueError("Invalid file path")
        
        text = ""
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text() + "\n"
            if len(text) > 50000:
                break
        return " ".join(text.split())[:10000]