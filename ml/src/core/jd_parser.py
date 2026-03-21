import re

class JobDescriptionParser:
    """Parses raw job description text into structured sections."""
    def __init__(self):
        self.section_patterns = {
            "requirements": [r"requirements", r"qualifications", r"what we're looking for", r"what you need", r"skills"],
            "responsibilities": [r"responsibilities", r"what you'll do", r"role", r"duties"],
            "benefits": [r"benefits", r"perks", r"what we offer"]
        }

    def parse(self, text: str) -> dict:
        sections = {"requirements": "", "responsibilities": "", "benefits": "", "experience": ""}
        if not text:
            return sections
        
        current_section = None
        lines = text.split('\n')
        
        for line in lines:
            line_lower = line.strip().lower()
            found_section = False
            for sec, keywords in self.section_patterns.items():
                if any(kw == line_lower or line_lower.startswith(kw + ":") for kw in keywords) and len(line_lower) < 60:
                    current_section = sec
                    found_section = True
                    break
            
            if current_section and not found_section:
                sections[current_section] += line + "\n"
                
        if not sections["requirements"].strip() and not sections["responsibilities"].strip():
            sections["requirements"] = text
            
        sections["experience"] = self._extract_experience(text)
        return sections

    def _extract_experience(self, text: str) -> str:
        # Match "X years", "X+ years", "X-Y years", etc.
        pattern = r'(\d+)\+?\s*(?:to|-)\s*(\d+)?\s*years?|(\d+)\+?\s*years?'
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            return match.group(0)
        return ""

jd_parser = JobDescriptionParser()
