import sys
from pathlib import Path
from pypdf import PdfReader
from src.core.resume_parser import parser

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

from config import settings

class ResumeData:
    def __init__(self, raw_text: str, parsed_sections: dict):
        self.raw_text = raw_text
        self.parsed_sections = parsed_sections
        # Fallback dictionary access for older code
        self.text = raw_text
    
    def __str__(self):
        return self.raw_text
    
    def __len__(self):
        return len(self.raw_text)

class ResumeLoader:
    def __init__(self):
        self.resume_dir = settings.BASE_DIR / "data" / "resumes"
        self.resume_dir.mkdir(parents=True, exist_ok=True)
    
    def load_resume(self):
        print(f"Scanning for resumes in: {self.resume_dir}")
        pdfs = list(self.resume_dir.glob("*.pdf"))
        docxs = list(self.resume_dir.glob("*.docx")) if DOCX_AVAILABLE else []
        
        resumes = pdfs + docxs
        if not resumes:
            print("[ResumeLoader] No resume found. Proceeding without resume context.")
            return None
        
        target_resume = resumes[0]
        print(f"[ResumeLoader] Found resume: {target_resume.name}")
        
        try:
            return self.load_from_path(target_resume)
        except Exception as e:
            print(f"[ResumeLoader] Error reading document: {e}")
            return None

    def load_from_path(self, file_path: Path):
        MAX_FILE_SIZE = 10 * 1024 * 1024
        
        if not file_path.is_file():
            raise ValueError("Invalid file path")
        
        ext = file_path.suffix.lower()
        if ext not in ['.pdf', '.docx']:
            raise ValueError("File must be PDF or DOCX")
            
        if ext == '.docx' and not DOCX_AVAILABLE:
            raise ValueError("python-docx is not installed. Please pip install python-docx")
        
        file_size = file_path.stat().st_size
        if file_size > MAX_FILE_SIZE:
            raise ValueError(f"File too large: {file_size} bytes (max 10MB)")
        
        if file_size == 0:
            raise ValueError("File is empty")
        
        try:
            file_path_resolved = file_path.resolve()
        except (FileNotFoundError, OSError) as e:
            raise ValueError("Invalid file path") from e
        
        text = ""
        if ext == '.pdf':
            reader = PdfReader(file_path)
            # Parse all pages unconditionally to guarantee no cutoff
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        elif ext == '.docx':
            doc = Document(file_path)
            for para in doc.paragraphs:
                if para.text:
                    text += para.text + "\n"
                    
        # Clean whitespace but DO NOT truncate the text length
        # Using a single space join can mess up line-based parsing slightly but we do it per \n to preserve lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        clean_text = "\n".join(lines)
        
        # Parse into sections
        parsed_sections = parser.parse(clean_text)
        return ResumeData(raw_text=clean_text, parsed_sections=parsed_sections)