import spacy
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
from difflib import SequenceMatcher
from sentence_transformers import SentenceTransformer
import numpy as np
import json
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor, as_completed
import torch
from src.core.cache_manager import get_cache_manager

class ATSChecker:
    def __init__(self, llm_model=None):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], check=True)
            self.nlp = spacy.load("en_core_web_sm")
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.semantic_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', device=device)
        self.llm_model = llm_model
        self.cache = get_cache_manager()
        
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
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\b(and|or|the|a|an|in|on|at|for|to|of|with|by)\b', ' ', text)
        text = ' '.join(text.split())
        return text
    
    @lru_cache(maxsize=128)
    def extract_skills(self, text):
        if not text:
            return set()
        
        text_lower = text.lower()
        found_skills = set()
        
        for skill in self.tech_skills:
            if skill in text_lower:
                found_skills.add(skill)
        
        return found_skills
    
    @lru_cache(maxsize=128)
    def extract_keywords(self, text):
        if not text:
            return set()
        
        processed = self.preprocess_text(text)
        doc = self.nlp(processed)
        
        keywords = set()
        for token in doc:
            if token.pos_ in ['NOUN', 'PROPN', 'ADJ'] and len(token.text) > 2:
                keywords.add(token.text)
        
        for chunk in doc.noun_chunks:
            if len(chunk.text) > 3:
                keywords.add(chunk.text.strip())
        
        return keywords
    
    def get_cached_embedding(self, text):
        cached = self.cache.get_embedding_cache(text)
        if cached is not None:
            return cached
        
        embedding = self.semantic_model.encode(text, convert_to_tensor=False, show_progress_bar=False)
        self.cache.set_embedding_cache(text, embedding)
        return embedding
    
    def calculate_tfidf_similarity(self, resume_text, jd_text):
        if not resume_text or not jd_text:
            return 0.0
        
        vectorizer = TfidfVectorizer(max_features=500, ngram_range=(1, 2))
        try:
            tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return round(similarity * 100, 2)
        except:
            return 0.0
    
    def calculate_semantic_similarity(self, resume_text, jd_text):
        if not resume_text or not jd_text:
            return 0.0
        
        resume_sentences = [s.strip() for s in resume_text.split('.') if len(s.strip()) > 20]
        jd_sentences = [s.strip() for s in jd_text.split('.') if len(s.strip()) > 20]
        
        if not resume_sentences or not jd_sentences:
            return 0.0
        
        resume_embeddings = self.semantic_model.encode(resume_sentences, 
                                                       batch_size=32,
                                                       convert_to_tensor=False, 
                                                       show_progress_bar=False)
        jd_embeddings = self.semantic_model.encode(jd_sentences,
                                                   batch_size=32, 
                                                   convert_to_tensor=False, 
                                                   show_progress_bar=False)
        
        similarities = cosine_similarity(resume_embeddings, jd_embeddings)
        max_similarities = np.max(similarities, axis=1)
        avg_similarity = np.mean(max_similarities)
        
        return round(avg_similarity * 100, 2)
    
    def calculate_skill_match(self, resume_skills, jd_skills):
        if not jd_skills:
            return 0.0
        
        matched = resume_skills.intersection(jd_skills)
        return (len(matched) / len(jd_skills)) * 100
    
    def calculate_keyword_match(self, resume_keywords, jd_keywords):
        if not jd_keywords:
            return 0.0
        
        matched = resume_keywords.intersection(jd_keywords)
        return (len(matched) / len(jd_keywords)) * 100
    
    def fuzzy_match_score(self, resume_text, jd_text):
        if not resume_text or not jd_text:
            return 0.0
        
        return SequenceMatcher(None, resume_text[:1000], jd_text[:1000]).ratio() * 100
    
    def gap_analysis(self, resume_keywords, jd_keywords, resume_skills, jd_skills):
        missing_skills = list(jd_skills - resume_skills)
        matched_skills = list(resume_skills.intersection(jd_skills))
        
        suggestions = []
        if missing_skills:
            suggestions.append(f"Consider adding these skills: {', '.join(missing_skills[:5])}")
        
        return {
            "missing_skills": missing_skills,
            "matched_skills": matched_skills,
            "suggestions": suggestions
        }
    
    def llm_intelligent_score(self, resume_text, jd_text):
        if not self.llm_model or not resume_text or not jd_text:
            return None
        
        cached_result = self.cache.get_llm_cache(resume_text, jd_text)
        if cached_result:
            return cached_result
        
        try:
            prompt = f"""You are an expert ATS (Applicant Tracking System) and recruitment specialist. Analyze how well this resume matches the job description.

JOB DESCRIPTION:
{jd_text[:2000]}

RESUME:
{resume_text[:2000]}

Provide a detailed analysis in JSON format with:
1. match_score: A score from 0-100 indicating overall match quality
2. strengths: List of 3-5 key strengths where the candidate matches well
3. gaps: List of 3-5 areas where the candidate could improve or is missing requirements
4. reasoning: Brief explanation of the score

Respond ONLY with valid JSON, no other text."""

            print("\n[LLM Analysis] Generating intelligent score...")
            
            response = self.llm_model.create_completion(
                prompt=prompt,
                max_tokens=800,
                temperature=0.3,
                stop=["</s>", "USER:", "ASSISTANT:"]
            )
            
            response_text = response['choices'][0]['text'].strip()
            
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                try:
                    result = json.loads(json_str)
                    llm_result = {
                        "llm_score": float(result.get("match_score", 0)),
                        "strengths": result.get("strengths", []),
                        "gaps": result.get("gaps", []),
                        "reasoning": result.get("reasoning", "")
                    }
                    self.cache.set_llm_cache(resume_text, jd_text, llm_result)
                    return llm_result
                except json.JSONDecodeError as je:
                    print(f"[LLM Score] JSON decode error: {je}")
                    decoder = json.JSONDecoder()
                    try:
                        result, _ = decoder.raw_decode(json_str)
                        llm_result = {
                            "llm_score": float(result.get("match_score", 0)),
                            "strengths": result.get("strengths", []),
                            "gaps": result.get("gaps", []),
                            "reasoning": result.get("reasoning", "")
                        }
                        self.cache.set_llm_cache(resume_text, jd_text, llm_result)
                        return llm_result
                    except:
                        pass
        except Exception as e:
            print(f"[LLM Score] Error: {e}")
            import traceback
            traceback.print_exc()
            return None
        
        return None
    
    def analyze(self, resume_text, jd_text):
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_keywords_resume = executor.submit(self.extract_keywords, resume_text)
            future_keywords_jd = executor.submit(self.extract_keywords, jd_text)
            future_skills_resume = executor.submit(self.extract_skills, resume_text)
            future_skills_jd = executor.submit(self.extract_skills, jd_text)
            
            resume_keywords = future_keywords_resume.result()
            jd_keywords = future_keywords_jd.result()
            resume_skills = future_skills_resume.result()
            jd_skills = future_skills_jd.result()
        
        futures = {}
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures['tfidf'] = executor.submit(self.calculate_tfidf_similarity, resume_text, jd_text)
            futures['semantic'] = executor.submit(self.calculate_semantic_similarity, resume_text, jd_text)
            futures['skill'] = executor.submit(self.calculate_skill_match, resume_skills, jd_skills)
            futures['keyword'] = executor.submit(self.calculate_keyword_match, resume_keywords, jd_keywords)
            futures['fuzzy'] = executor.submit(self.fuzzy_match_score, resume_text, jd_text)
            
            tfidf_score = futures['tfidf'].result()
            semantic_score = futures['semantic'].result()
            skill_match_score = futures['skill'].result()
            keyword_match_score = futures['keyword'].result()
            fuzzy_score = futures['fuzzy'].result()
        
        final_score = (
            tfidf_score * 0.20 +
            semantic_score * 0.45 +
            skill_match_score * 0.20 +
            keyword_match_score * 0.10 +
            fuzzy_score * 0.05
        )
        
        gap_info = self.gap_analysis(resume_keywords, jd_keywords, resume_skills, jd_skills)
        
        llm_analysis = self.llm_intelligent_score(resume_text, jd_text)
        
        result = {
            "match_score": round(final_score, 2),
            "tfidf_score": tfidf_score,
            "semantic_score": semantic_score,
            "skill_match_score": round(skill_match_score, 2),
            "keyword_match_score": round(keyword_match_score, 2),
            "missing_skills": gap_info["missing_skills"],
            "matched_skills": gap_info["matched_skills"],
            "suggestions": gap_info["suggestions"]
        }
        
        if llm_analysis:
            result["llm_score"] = llm_analysis["llm_score"]
            result["llm_strengths"] = llm_analysis["strengths"]
            result["llm_gaps"] = llm_analysis["gaps"]
            result["llm_reasoning"] = llm_analysis["reasoning"]
        
        return result
