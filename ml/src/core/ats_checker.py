import spacy
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
from difflib import SequenceMatcher
from sentence_transformers import SentenceTransformer
import numpy as np

class ATSChecker:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            import os
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
        
        self.semantic_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        self.tech_skills = {
            "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go", "rust", "swift",
            "react", "angular", "vue", "node", "express", "django", "flask", "fastapi", "spring",
            "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "terraform", "ansible",
            "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "cassandra",
            "git", "github", "gitlab", "bitbucket", "jira", "confluence",
            "api", "rest", "graphql", "grpc", "microservices", "serverless",
            "machine learning", "deep learning", "nlp", "computer vision", "tensorflow", 
            "pytorch", "keras", "scikit-learn", "pandas", "numpy", "opencv",
            "agile", "scrum", "cicd", "devops", "testing", "tdd", "junit", "pytest",
            "html", "css", "sass", "webpack", "babel", "npm", "yarn",
            "linux", "unix", "bash", "powershell", "windows", "macos",
            "networking", "security", "encryption", "authentication", "oauth",
            "data structures", "algorithms", "system design", "database design",
            "ai", "artificial intelligence", "neural networks", "transformers",
            "spark", "hadoop", "kafka", "airflow", "etl", "data engineering"
        }
    
    def preprocess_text(self, text):
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = ' '.join(text.split())
        return text
    
    def extract_skills(self, text):
        if not text:
            return set()
        
        text_lower = text.lower()
        found_skills = set()
        
        for skill in self.tech_skills:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.add(skill)
        
        return found_skills
    
    def extract_keywords(self, text):
        if not text:
            return set()
        
        doc = self.nlp(text.lower())
        keywords = set()
        
        for ent in doc.ents:
            if ent.label_ in ["ORG", "PRODUCT", "GPE", "WORK_OF_ART", "LANGUAGE", "SKILL"]:
                keywords.add(ent.text.strip())
        
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.strip()
            if 2 <= len(chunk_text.split()) <= 4:
                keywords.add(chunk_text)
        
        for token in doc:
            if token.pos_ in ["NOUN", "PROPN"] and len(token.text) > 2:
                keywords.add(token.text)
        
        return keywords
    
    def fuzzy_match_score(self, resume_text, jd_text):
        resume_words = set(self.preprocess_text(resume_text).split())
        jd_words = set(self.preprocess_text(jd_text).split())
        
        if not jd_words:
            return 0.0
        
        matched_count = 0
        for jd_word in jd_words:
            if len(jd_word) < 3:
                continue
            for resume_word in resume_words:
                if SequenceMatcher(None, jd_word, resume_word).ratio() > 0.85:
                    matched_count += 1
                    break
        
        return (matched_count / len(jd_words)) * 100 if jd_words else 0.0
    
    def calculate_tfidf_similarity(self, resume_text, jd_text):
        if not resume_text or not jd_text:
            return 0.0
        
        vectorizer = TfidfVectorizer(
            stop_words='english', 
            ngram_range=(1, 3),
            max_features=1000,
            min_df=1
        )
        
        try:
            vectors = vectorizer.fit_transform([resume_text, jd_text])
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            return round(similarity * 100, 2)
        except:
            return 0.0
    
    def calculate_semantic_similarity(self, resume_text, jd_text):
        if not resume_text or not jd_text:
            return 0.0
        
        try:
            resume_sentences = [s.strip() for s in resume_text.split('.') if s.strip()]
            jd_sentences = [s.strip() for s in jd_text.split('.') if s.strip()]
            
            if not resume_sentences or not jd_sentences:
                return 0.0
            
            resume_embeddings = self.semantic_model.encode(resume_sentences[:50])
            jd_embeddings = self.semantic_model.encode(jd_sentences[:50])
            
            similarities = cosine_similarity(resume_embeddings, jd_embeddings)
            max_similarities = similarities.max(axis=0)
            avg_similarity = max_similarities.mean()
            
            return round(avg_similarity * 100, 2)
        except:
            return 0.0
    
    def calculate_skill_match(self, resume_skills, jd_skills):
        if not jd_skills:
            return 100.0
        
        matched = resume_skills & jd_skills
        return (len(matched) / len(jd_skills)) * 100
    
    def calculate_keyword_match(self, resume_keywords, jd_keywords):
        if not jd_keywords:
            return 100.0
        
        matched = resume_keywords & jd_keywords
        fuzzy_matched = 0
        
        for jd_kw in jd_keywords - matched:
            for resume_kw in resume_keywords:
                if SequenceMatcher(None, jd_kw, resume_kw).ratio() > 0.8:
                    fuzzy_matched += 1
                    break
        
        total_matched = len(matched) + fuzzy_matched
        return (total_matched / len(jd_keywords)) * 100
    
    def gap_analysis(self, resume_keywords, jd_keywords, resume_skills, jd_skills):
        missing_keywords = jd_keywords - resume_keywords
        missing_skills = jd_skills - resume_skills
        matched_keywords = resume_keywords & jd_keywords
        matched_skills = resume_skills & jd_skills
        
        suggestions = []
        
        if missing_skills:
            top_missing_skills = sorted(list(missing_skills))[:5]
            suggestions.append(f"Consider adding these skills: {', '.join(top_missing_skills)}")
        
        if len(matched_skills) < len(jd_skills) * 0.7:
            suggestions.append("Resume match is low. Highlight relevant experience more prominently.")
        
        if len(matched_keywords) < len(jd_keywords) * 0.3:
            suggestions.append("Add more keywords from the job description to your resume.")
        
        return {
            "missing_keywords": sorted(list(missing_keywords))[:10],
            "missing_skills": sorted(list(missing_skills)),
            "matched_keywords": sorted(list(matched_keywords)),
            "matched_skills": sorted(list(matched_skills)),
            "suggestions": suggestions
        }
    
    def analyze(self, resume_text, jd_text):
        resume_keywords = self.extract_keywords(resume_text)
        jd_keywords = self.extract_keywords(jd_text)
        resume_skills = self.extract_skills(resume_text)
        jd_skills = self.extract_skills(jd_text)
        
        tfidf_score = self.calculate_tfidf_similarity(resume_text, jd_text)
        semantic_score = self.calculate_semantic_similarity(resume_text, jd_text)
        skill_match_score = self.calculate_skill_match(resume_skills, jd_skills)
        keyword_match_score = self.calculate_keyword_match(resume_keywords, jd_keywords)
        fuzzy_score = self.fuzzy_match_score(resume_text, jd_text)
        
        final_score = (
            tfidf_score * 0.25 +
            semantic_score * 0.35 +
            skill_match_score * 0.20 +
            keyword_match_score * 0.15 +
            fuzzy_score * 0.05
        )
        
        gap_info = self.gap_analysis(resume_keywords, jd_keywords, resume_skills, jd_skills)
        
        return {
            "match_score": round(final_score, 2),
            "tfidf_score": tfidf_score,
            "semantic_score": semantic_score,
            "skill_match_score": round(skill_match_score, 2),
            "keyword_match_score": round(keyword_match_score, 2),
            "missing_skills": gap_info["missing_skills"],
            "matched_skills": gap_info["matched_skills"],
            "suggestions": gap_info["suggestions"]
        }
