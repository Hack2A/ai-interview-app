from src.core.ats_checker import ATSChecker

print("="*60)
print("     Testing ATS Resume Checker (Module 5)")
print("="*60)

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

print(f"\n✅ Match Score: {result['match_score']}%")
print(f"\n✅ Matched Skills: {', '.join(result['matched_skills'][:10])}")
print(f"\n❌ Missing Skills: {', '.join(result['missing_skills'][:10])}")
print(f"\n💡 Suggestions:")
for suggestion in result['suggestions']:
    print(f"  - {suggestion}")

print("\n" + "="*60)
print("✅ ATS Module Working!")
print("="*60)
