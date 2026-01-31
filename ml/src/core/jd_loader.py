from pathlib import Path
from pypdf import PdfReader
from config import settings

class JDLoader:
    def __init__(self):
        self.jd_dir = settings.JD_DIR
        self.jd_dir.mkdir(parents=True, exist_ok=True)
    
    def load_jd(self):
        print(f"Scanning for Job Descriptions in: {self.jd_dir}")
        
        pdfs = list(self.jd_dir.glob("*.pdf"))
        txt_files = list(self.jd_dir.glob("*.txt"))
        
        all_files = pdfs + txt_files
        
        if not all_files:
            print("[JDLoader] No JD found. Using generic interview mode.")
            return None
        
        target_file = all_files[0]
        print(f"[JDLoader] Found JD: {target_file.name}")
        
        try:
            if target_file.suffix == ".pdf":
                return self._load_pdf(target_file)
            else:
                return self._load_txt(target_file)
        except Exception as e:
            print(f"[JDLoader] Error reading file: {e}")
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
            if not str(file_path_resolved).startswith(str(self.jd_dir.resolve())):
                raise ValueError("Path traversal detected")
        except:
            raise ValueError("Invalid file path")
        
        text = ""
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return " ".join(text.split())
    
    def _load_txt(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        return " ".join(text.split())
    
    def chunk_text(self, text, chunk_size=200):
        if not text:
            return []
        
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
        
        return chunks
