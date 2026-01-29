import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path

class ATSChecker:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            import os
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
    
    def extract_keywords(self, text):
        if not text:
            return set()
        
        doc = self.nlp(text.lower())
        keywords = set()
        
        for ent in doc.ents:
            if ent.label_ in ["ORG", "PRODUCT", "GPE", "WORK_OF_ART", "LANGUAGE"]:
                keywords.add(ent.text.strip())
        
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) <= 3:
                keywords.add(chunk.text.strip())
        
        tech_patterns = ["python", "java", "javascript", "react", "node", "aws", "docker", 
                        "kubernetes", "sql", "mongodb", "git", "api", "rest", "graphql",
                        "machine learning", "deep learning", "nlp", "computer vision"]
        
        text_lower = text.lower()
        for pattern in tech_patterns:
            if pattern in text_lower:
                keywords.add(pattern)
        
        return keywords
    
    def calculate_similarity(self, resume_text, jd_text):
        if not resume_text or not jd_text:
            return 0.0
        
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        
        try:
            vectors = vectorizer.fit_transform([resume_text, jd_text])
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            return round(similarity * 100, 2)
        except:
            return 0.0
    
    def gap_analysis(self, resume_keywords, jd_keywords):
        missing = jd_keywords - resume_keywords
        extra = resume_keywords - jd_keywords
        matched = resume_keywords & jd_keywords
        
        suggestions = []
        if missing:
            top_missing = sorted(list(missing))[:5]
            suggestions.append(f"Consider adding these skills: {', '.join(top_missing)}")
        
        if len(matched) < len(jd_keywords) * 0.5:
            suggestions.append("Resume match is low. Highlight relevant experience more prominently.")
        
        return {
            "missing_keywords": sorted(list(missing)),
            "matched_keywords": sorted(list(matched)),
            "extra_keywords": sorted(list(extra)),
            "suggestions": suggestions
        }
    
    def analyze(self, resume_text, jd_text):
        resume_keywords = self.extract_keywords(resume_text)
        jd_keywords = self.extract_keywords(jd_text)
        
        similarity_score = self.calculate_similarity(resume_text, jd_text)
        gap_info = self.gap_analysis(resume_keywords, jd_keywords)
        
        return {
            "match_score": similarity_score,
            "missing_skills": gap_info["missing_keywords"][:10],
            "matched_skills": gap_info["matched_keywords"][:15],
            "suggestions": gap_info["suggestions"]
        }
