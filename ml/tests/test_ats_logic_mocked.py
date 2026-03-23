import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.ats_checker import ATSChecker

class MockATS(ATSChecker):
    def llm_intelligent_score(self, resume_parsed, jd_parsed):
        return {
            "match_score": 88.0,
            "strengths": ["Python", "Docker"],
            "gaps": ["React", "FastAPI"],
            "reasoning": "High relevance to scale AI projects."
        }

ats = MockATS(None)

resume_text = """
John Doe
Software Engineer
Experience: 5 years at Google
Skills: Python, TypeScript, Docker, Kubernetes
Projects: Built an ATS using LLMs.
"""

jd_text = """
Looking for a Backend Engineer with Python, Docker, React, and FastAPI experience.
Should have 3+ years experience.
"""

# Test analysis
res = ats.analyze(resume_text, jd_text)
print("--- ANALYSIS RESULT ---")
for k, v in res.items():
    print(f"{k}: {v}")

assert "algorithmic_score" in res
assert "llm_score" in res
assert "combined_score" in res
assert "llm_gaps" in res
assert "llm_strengths" in res
assert "llm_reasoning" in res
print("✅ Output schema validated!")
