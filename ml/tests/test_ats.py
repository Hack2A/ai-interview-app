import pytest
from src.core.ats_checker import ATSChecker

def test_ats_checker_analyze():
    resume = """
    John Doe
    Senior Software Engineer
    
    Skills: Python, JavaScript, React, SQL, Git, AWS
    Experience: 5 years in full-stack development
    """
    
    jd = """
    Senior Full Stack Developer
    Required Skills: Python, React, Node.js, AWS, Docker, Kubernetes
    Experience: 4+ years
    """
    
    checker = ATSChecker()
    result = checker.analyze(resume, jd)
    
    required_keys = ['match_score', 'matched_skills', 'missing_skills', 'suggestions']
    assert all(k in result for k in required_keys), f"Missing keys in result: {result.keys()}"
    
    assert isinstance(result.get('match_score'), (int, float)), "match_score should be numeric"
    assert isinstance(result.get('matched_skills', []), list), "matched_skills should be a list"
    assert isinstance(result.get('missing_skills', []), list), "missing_skills should be a list"
    assert isinstance(result.get('suggestions', []), list), "suggestions should be a list"
    
    matched_skills = result.get('matched_skills', [])
    missing_skills = result.get('missing_skills', [])
    suggestions = result.get('suggestions', [])
    
    print(f"\n✅ Match Score: {result['match_score']}%")
    print(f"✅ Matched Skills: {', '.join(matched_skills[:10]) if matched_skills else 'None'}")
    print(f"❌ Missing Skills: {', '.join(missing_skills[:10]) if missing_skills else 'None'}")
    print(f"💡 Suggestions:")
    for suggestion in suggestions:
        print(f"  - {suggestion}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
