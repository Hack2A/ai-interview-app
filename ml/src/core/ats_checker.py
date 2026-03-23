"""ATS Resume Checker — algorithmic + LLM-based resume analysis."""
import json
import logging
import re
from concurrent.futures import ThreadPoolExecutor
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path

import numpy as np
import spacy
import torch
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.core.cache_manager import get_cache_manager

logger = logging.getLogger("ATSChecker")


class ATSChecker:
    """Analyzes resume against job description using both algorithmic and LLM scoring."""

    def __init__(self, llm_model=None) -> None:
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError as e:
            raise RuntimeError(
                "spaCy model 'en_core_web_sm' not found. "
                "Please install it: python -m spacy download en_core_web_sm"
            ) from e

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
            "spark", "hadoop", "kafka", "airflow", "etl", "data engineering",
        }

    # ── Text Processing ───────────────────────────────────────────

    def preprocess_text(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\b(and|or|the|a|an|in|on|at|for|to|of|with|by)\b', ' ', text)
        return ' '.join(text.split())

    @lru_cache(maxsize=128)
    def extract_skills(self, text: str) -> frozenset:
        if not text:
            return frozenset()
        
        try:
            from src.core.skill_ontology import SkillOntology
            ontology = SkillOntology()
            skills_found = ontology.extract_skills(text)
            # Use original skill name rather than standardized to match downstream expectations, or standardized if preferred
            return frozenset([s["skill"] for s in skills_found])
        except Exception as e:
            logger.warning(f"Skill extraction failed, using fallback: {e}")
            text_lower = text.lower()
            return frozenset(skill for skill in self.tech_skills if skill in text_lower)

    @lru_cache(maxsize=128)
    def extract_keywords(self, text: str) -> frozenset:
        if not text:
            return frozenset()
        processed = self.preprocess_text(text)
        doc = self.nlp(processed)
        keywords = set()
        for token in doc:
            if token.pos_ in ['NOUN', 'PROPN', 'ADJ'] and len(token.text) > 2:
                keywords.add(token.text)
        for chunk in doc.noun_chunks:
            if len(chunk.text) > 3:
                keywords.add(chunk.text.strip())
        return frozenset(keywords)

    # ── Similarity Scores ─────────────────────────────────────────

    def get_cached_embedding(self, text: str):
        cached = self.cache.get_embedding_cache(text)
        if cached is not None:
            return cached
        embedding = self.semantic_model.encode(text, convert_to_tensor=False, show_progress_bar=False)
        self.cache.set_embedding_cache(text, embedding)
        return embedding

    def calculate_tfidf_similarity(self, resume_text: str, jd_text: str) -> float:
        if not resume_text or not jd_text:
            return 0.0
        vectorizer = TfidfVectorizer(max_features=500, ngram_range=(1, 2))
        try:
            tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return round(similarity * 100, 2)
        except (ValueError, ZeroDivisionError):
            return 0.0

    def calculate_semantic_similarity(self, resume_parsed: dict, jd_parsed: dict) -> float:
        """Compare specific sections (e.g. experience to responsibilities) rather than whole documents."""
        # Use targeted sections for comparison
        resume_target = resume_parsed.get("experience", "")
        if len(resume_target.strip()) < 50:
            resume_target = resume_parsed.get("summary", "")
            
        jd_target = jd_parsed.get("responsibilities", "") + " " + jd_parsed.get("requirements", "")
        
        if len(resume_target.strip()) < 50:
            # Fall back to raw text comparison if parsing failed
            resume_target = " ".join(resume_parsed.values())
        if len(jd_target.strip()) < 50:
            jd_target = " ".join(jd_parsed.values())

        if not resume_target or not jd_target:
            return 0.0

        resume_sentences = [s.strip() for s in resume_target.split('.') if len(s.strip()) > 20]
        jd_sentences = [s.strip() for s in jd_target.split('.') if len(s.strip()) > 20]
        
        if not resume_sentences or not jd_sentences:
            return 0.0
            
        resume_embeddings = self.semantic_model.encode(
            resume_sentences, batch_size=32, convert_to_tensor=False, show_progress_bar=False
        )
        jd_embeddings = self.semantic_model.encode(
            jd_sentences, batch_size=32, convert_to_tensor=False, show_progress_bar=False
        )
        similarities = cosine_similarity(resume_embeddings, jd_embeddings)
        max_similarities = np.max(similarities, axis=1)
        return round(np.mean(max_similarities) * 100, 2)

    def calculate_experience_score(self, resume_parsed: dict, jd_parsed: dict) -> float:
        """Evaluate if the candidate's years of experience meet the JD requirements."""
        resume_exp_str = resume_parsed.get("years_of_experience", "0")
        jd_exp_str = jd_parsed.get("experience", "0")
        
        try:
            res_match = re.search(r'\d+', str(resume_exp_str))
            res_years = float(res_match.group()) if res_match else 0.0
            
            jd_match = re.search(r'\d+', str(jd_exp_str))
            jd_years = float(jd_match.group()) if jd_match else 0.0
            
            if jd_years == 0:
                return 100.0  # No specific requirement found, assume match
                
            if res_years >= jd_years:
                return 100.0
                
            # Partial score if they have some experience
            return min(100.0, max(0.0, (res_years / jd_years) * 100))
        except Exception as e:
            logger.warning(f"Error extracting experience: {e}")
            return 50.0

    def calculate_skill_match(self, resume_skills: frozenset, jd_skills: frozenset) -> float:
        if not jd_skills:
            return 0.0
        matched = resume_skills.intersection(jd_skills)
        return (len(matched) / len(jd_skills)) * 100

    def calculate_keyword_match(self, resume_keywords: frozenset, jd_keywords: frozenset) -> float:
        if not jd_keywords:
            return 0.0
        matched = resume_keywords.intersection(jd_keywords)
        return (len(matched) / len(jd_keywords)) * 100

    def fuzzy_match_score(self, resume_text: str, jd_text: str) -> float:
        if not resume_text or not jd_text:
            return 0.0
        return SequenceMatcher(None, resume_text[:1000], jd_text[:1000]).ratio() * 100

    # ── NEW: Spelling & Formatting Checks ─────────────────────────

    def check_spelling(self, text: str) -> dict:
        """Check for potential spelling errors using spaCy's vocabulary."""
        if not text:
            return {"error_count": 0, "errors": [], "score_penalty": 0}

        doc = self.nlp(text)
        errors = []
        checked = set()

        for token in doc:
            word = token.text.lower()
            if (
                len(word) > 2
                and word not in checked
                and token.pos_ not in ['PROPN', 'NUM', 'PUNCT', 'SPACE', 'SYM', 'X']
                and not token.is_stop
                and not any(c.isdigit() for c in word)
                and not word.startswith('@')
                and not word.startswith('http')
            ):
                checked.add(word)
                # spaCy's vocab check for potential misspellings
                if not self.nlp.vocab.has_vector(word) and word not in self.tech_skills:
                    if not re.match(r'^[A-Z]{2,}$', token.text):  # Skip acronyms
                        errors.append(word)

        error_count = len(errors)
        # Penalize: -1 point per error, max -15
        score_penalty = min(error_count * 1, 15)

        return {
            "error_count": error_count,
            "errors": errors[:20],  # Show top 20
            "score_penalty": score_penalty,
        }

    def check_formatting(self, text: str) -> dict:
        """Check resume formatting quality heuristics."""
        if not text:
            return {"issues": [], "score_penalty": 0}

        issues = []

        # Check for section headers (common resume sections)
        section_keywords = ["experience", "education", "skills", "projects", "summary", "objective", "certifications"]
        found_sections = [kw for kw in section_keywords if kw in text.lower()]
        if len(found_sections) < 3:
            issues.append(f"Missing standard sections (found {len(found_sections)}/7: {', '.join(found_sections)})")

        # Check for bullet consistency
        bullet_patterns = [r'•', r'[-–—]', r'\*', r'►', r'▪']
        bullet_types_found = sum(1 for p in bullet_patterns if re.search(p, text))
        if bullet_types_found > 2:
            issues.append(f"Inconsistent bullet styles ({bullet_types_found} different types detected)")

        # Check for ALL CAPS abuse
        words = text.split()
        caps_words = [w for w in words if w.isupper() and len(w) > 3]
        caps_ratio = len(caps_words) / max(len(words), 1)
        if caps_ratio > 0.15:
            issues.append(f"Excessive ALL CAPS ({len(caps_words)} words, {caps_ratio:.0%} of text)")

        # Check for extremely long paragraphs (no line breaks)
        lines = text.split('\n')
        long_lines = [l for l in lines if len(l) > 500]
        if long_lines:
            issues.append(f"Wall of text detected ({len(long_lines)} lines over 500 chars — add more line breaks)")

        # Check for contact info presence
        has_email = bool(re.search(r'[\w.+-]+@[\w-]+\.[\w.]+', text))
        has_phone = bool(re.search(r'[\+]?[\d\s\-()]{10,}', text))
        if not has_email:
            issues.append("No email address detected")
        if not has_phone:
            issues.append("No phone number detected")

        # Check word count
        word_count = len(words)
        if word_count < 100:
            issues.append(f"Resume too short ({word_count} words — aim for 300-600)")
        elif word_count > 1200:
            issues.append(f"Resume too long ({word_count} words — keep under 1000 for ATS)")

        score_penalty = min(len(issues) * 2, 15)

        return {
            "issues": issues,
            "issue_count": len(issues),
            "score_penalty": score_penalty,
            "word_count": word_count if words else 0,
            "sections_found": found_sections,
        }

    # ── LLM Intelligent Score ─────────────────────────────────────

    def llm_intelligent_score(self, resume_parsed: dict, jd_parsed: dict) -> dict | None:
        if not self.llm_model or not resume_parsed or not jd_parsed:
            return None

        # We'll use raw text fallback for cache key to ensure consistency
        resume_text = " ".join(str(v) for v in resume_parsed.values())
        jd_text = " ".join(str(v) for v in jd_parsed.values())
        
        cached_result = self.cache.get_llm_cache(resume_text, jd_text)
        if cached_result:
            return cached_result

        try:
            prompt = f"""You are an expert ATS (Applicant Tracking System) and recruitment specialist. Analyze how well this resume matches the job description.

JOB DESCRIPTION:
Requirements: {str(jd_parsed.get('requirements', ''))[:1000]}
Responsibilities: {str(jd_parsed.get('responsibilities', ''))[:1000]}
Experience: {str(jd_parsed.get('experience', ''))[:500]}

RESUME:
Summary: {str(resume_parsed.get('summary', ''))[:500]}
Experience: {str(resume_parsed.get('experience', ''))[:1500]}
Skills: {str(resume_parsed.get('skills', ''))[:1000]}
Education: {str(resume_parsed.get('education', ''))[:500]}

Provide a detailed analysis in JSON format with:
1. match_score: A score from 0-100 indicating overall match quality, strictly evaluating required experience and core skills.
2. strengths: List of 3-5 key strengths where the candidate matches well.
3. gaps: List of 3-5 areas where the candidate could improve or is missing requirements (e.g. skill gaps, lack of years of experience).
4. reasoning: Brief explanation of the score, focusing on role fit and impact.

Respond ONLY with valid JSON, no other text."""

            logger.info("Generating LLM intelligent score...")

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
                        "reasoning": result.get("reasoning", ""),
                    }
                    self.cache.set_llm_cache(resume_text, jd_text, llm_result)
                    return llm_result
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"LLM JSON parse error: {e}")
        except Exception as e:
            logger.error(f"LLM scoring failed: {e}")

        return None

    # ── Gap Analysis ──────────────────────────────────────────────

    def gap_analysis(self, resume_keywords, jd_keywords, resume_skills, jd_skills) -> dict:
        missing_skills = list(jd_skills - resume_skills)
        matched_skills = list(resume_skills.intersection(jd_skills))

        suggestions = []
        if missing_skills:
            suggestions.append(f"Consider adding these skills: {', '.join(missing_skills[:5])}")

        return {
            "missing_skills": missing_skills,
            "matched_skills": matched_skills,
            "suggestions": suggestions,
        }

    # ── Main Analysis ─────────────────────────────────────────────

    def analyze(self, resume_input, jd_input) -> dict:
        """Run full ATS analysis — algorithmic + LLM + spelling + formatting."""

        # 1. Parse Inputs safely
        if hasattr(resume_input, 'raw_text'):
            resume_text = resume_input.raw_text
            resume_parsed = resume_input.parsed_sections
        else:
            resume_text = str(resume_input)
            from src.core.resume_parser import ResumeParser
            resume_parsed = ResumeParser().parse(resume_text)
            
        jd_text = str(jd_input)
        from src.core.jd_parser import jd_parser
        jd_parsed = jd_parser.parse(jd_text)

        # Phase 1: Extract features in parallel
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_kw_resume = executor.submit(self.extract_keywords, resume_text)
            future_kw_jd = executor.submit(self.extract_keywords, jd_text)
            future_sk_resume = executor.submit(self.extract_skills, resume_text)
            future_sk_jd = executor.submit(self.extract_skills, jd_text)

            resume_keywords = future_kw_resume.result()
            jd_keywords = future_kw_jd.result()
            resume_skills = future_sk_resume.result()
            jd_skills = future_sk_jd.result()

        # Phase 2: Calculate scores in parallel
        futures = {}
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures['tfidf'] = executor.submit(self.calculate_tfidf_similarity, resume_text, jd_text)
            futures['semantic'] = executor.submit(self.calculate_semantic_similarity, resume_parsed, jd_parsed)
            futures['experience'] = executor.submit(self.calculate_experience_score, resume_parsed, jd_parsed)
            futures['skill'] = executor.submit(self.calculate_skill_match, resume_skills, jd_skills)
            futures['keyword'] = executor.submit(self.calculate_keyword_match, resume_keywords, jd_keywords)
            futures['fuzzy'] = executor.submit(self.fuzzy_match_score, resume_text, jd_text)
            futures['spelling'] = executor.submit(self.check_spelling, resume_text)
            futures['formatting'] = executor.submit(self.check_formatting, resume_text)

            tfidf_score = futures['tfidf'].result()
            semantic_score = futures['semantic'].result()
            experience_score = futures['experience'].result()
            skill_match_score = futures['skill'].result()
            keyword_match_score = futures['keyword'].result()
            fuzzy_score = futures['fuzzy'].result()
            spelling_result = futures['spelling'].result()
            formatting_result = futures['formatting'].result()

        # Algorithmic score (weighted average, then apply quality penalties)
        raw_algo_score = (
            semantic_score * 0.35
            + skill_match_score * 0.20
            + experience_score * 0.15
            + tfidf_score * 0.20
            + keyword_match_score * 0.05
            + fuzzy_score * 0.05
        )
        algo_score = max(0, raw_algo_score - spelling_result["score_penalty"] - formatting_result["score_penalty"])

        # Gap analysis
        gap_info = self.gap_analysis(resume_keywords, jd_keywords, resume_skills, jd_skills)

        # LLM analysis
        llm_analysis = self.llm_intelligent_score(resume_parsed, jd_parsed)
        llm_score = llm_analysis["llm_score"] if llm_analysis and "llm_score" in llm_analysis else None

        # Combined score (weighted fusion)
        if llm_score is not None:
            # 60% LLM (more reliable for actual fit) / 40% Algorithmic (good for strict keyword matching)
            combined_score = round((algo_score * 0.4) + (float(llm_score) * 0.6), 2)
        else:
            combined_score = round(algo_score, 2)

        result = {
            # Scores
            "algorithmic_score": round(algo_score, 2),
            "llm_score": llm_score,
            "combined_score": combined_score,
            # Sub-scores
            "tfidf_score": tfidf_score,
            "semantic_score": semantic_score,
            "skill_match_score": round(skill_match_score, 2),
            "experience_score": round(experience_score, 2),
            "keyword_match_score": round(keyword_match_score, 2),
            # Quality checks
            "spelling": spelling_result,
            "formatting": formatting_result,
            # Skills
            "missing_skills": gap_info["missing_skills"],
            "matched_skills": gap_info["matched_skills"],
            "suggestions": gap_info["suggestions"],
            # Legacy field
            "match_score": combined_score,
        }

        if llm_analysis:
            result["llm_strengths"] = llm_analysis["strengths"]
            result["llm_gaps"] = llm_analysis["gaps"]
            result["llm_reasoning"] = llm_analysis["reasoning"]

        return result
