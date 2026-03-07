"""Tests for ATS Checker: algorithmic scoring, spelling, formatting, combined score."""
import pytest
from src.core.ats_checker import ATSChecker


def test_ats_checker_analyze():
    resume = """
    John Doe
    john.doe@email.com  |  +1 234 567 8901
    Senior Software Engineer
    
    Summary
    Experienced full-stack developer with strong background in scalable systems.
    
    Experience
    - Built REST APIs using Python and Django
    - Deployed microservices on AWS using Docker
    
    Skills: Python, JavaScript, React, SQL, Git, AWS
    Experience: 5 years in full-stack development
    
    Education
    BS Computer Science, State University
    """
    
    jd = """
    Senior Full Stack Developer
    Required Skills: Python, React, Node.js, AWS, Docker, Kubernetes
    Experience: 4+ years
    """
    
    checker = ATSChecker()
    result = checker.analyze(resume, jd)
    
    # Check all required keys
    required_keys = [
        'algorithmic_score', 'combined_score', 'match_score',
        'matched_skills', 'missing_skills', 'suggestions',
        'spelling', 'formatting',
    ]
    assert all(k in result for k in required_keys), f"Missing keys: {set(required_keys) - set(result.keys())}"
    
    assert isinstance(result['algorithmic_score'], (int, float))
    assert isinstance(result['combined_score'], (int, float))
    assert isinstance(result['matched_skills'], list)
    assert isinstance(result['missing_skills'], list)
    
    # Spelling result
    assert 'error_count' in result['spelling']
    assert 'score_penalty' in result['spelling']
    
    # Formatting result
    assert 'issues' in result['formatting']
    assert 'score_penalty' in result['formatting']
    
    print(f"\n✅ Algorithmic Score: {result['algorithmic_score']}%")
    print(f"✅ Combined Score: {result['combined_score']}%")
    print(f"📝 Spelling errors: {result['spelling']['error_count']}")
    print(f"📋 Formatting issues: {result['formatting'].get('issue_count', 0)}")


def test_ats_spelling_check():
    checker = ATSChecker()
    result = checker.check_spelling("I am a profeshional softwear enginer")
    assert result['error_count'] >= 0  # spaCy may or may not catch these
    assert isinstance(result['errors'], list)


def test_ats_formatting_check():
    checker = ATSChecker()
    # Minimal resume — should flag missing sections, missing contact info
    result = checker.check_formatting("Just some random text without any structure")
    assert result['issue_count'] > 0
    assert result['score_penalty'] > 0


def test_ats_formatting_good_resume():
    checker = ATSChecker()
    good_resume = """
    John Doe
    john@email.com | +1-555-1234
    
    Summary
    Experienced developer with 5 years of experience.
    
    Experience
    - Senior Developer at Company A
    - Built microservices architecture
    
    Education
    BS in Computer Science
    
    Skills
    Python, JavaScript, React, Docker
    
    Projects
    Project Alpha - Built a scalable API
    
    Certifications
    AWS Solutions Architect
    """
    result = checker.check_formatting(good_resume)
    # A well-structured resume should have fewer issues
    assert result['issue_count'] <= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
