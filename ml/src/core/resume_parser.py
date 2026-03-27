import re
from typing import Dict, Any, List

class ResumeParser:
    """Robust regex and heuristic-based parser that guarantees full-text processing."""
    
    def __init__(self):
        # Common section headers
        self.section_headers = {
            "education": [r"(?i)^education", r"(?i)^academic background", r"(?i)^academics"],
            "experience": [r"(?i)^experience", r"(?i)^work experience", r"(?i)^employment", r"(?i)^professional experience", r"(?i)^history"],
            "projects": [r"(?i)^projects", r"(?i)^personal projects", r"(?i)^academic projects"],
            "skills": [r"(?i)^skills", r"(?i)^technical skills", r"(?i)^core competencies", r"(?i)^technologies"],
        }
    
    def parse(self, text: str) -> Dict[str, str]:
        """
        Parses the full text line-by-line into sections. 
        Guarantees no arbitrary text cutoff.
        """
        if not text:
            return {"raw": ""}

        sections = {
            "education": [],
            "experience": [],
            "projects": [],
            "skills": [],
            "other": []
        }
        
        current_section = "other"
        
        lines = [line.strip() for line in text.split("\n")]
        
        for line in lines:
            if not line:
                continue
            
            # Check if this line is a section header (usually short, standalone lines)
            is_header = False
            if len(line) < 60:
                # remove special chars that might surround a header
                clean_line = re.sub(r'[^a-zA-Z\s]', '', line).strip()
                for sec, patterns in self.section_headers.items():
                    if any(re.match(p, clean_line) for p in patterns):
                        current_section = sec
                        is_header = True
                        break
            
            if not is_header:
                sections[current_section].append(line)
                
        # Join lines back together for each section
        return {k: "\n".join(v) for k, v in sections.items()}

parser = ResumeParser()
