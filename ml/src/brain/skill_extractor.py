"""Skill Extractor — extracts structured skills, technologies, and domains
from resume text for resume-aware question retrieval.
"""
from __future__ import annotations

import logging
import re

logger = logging.getLogger("SkillExtractor")


# ── Comprehensive skill taxonomy ──────────────────────────────────

SKILL_TAXONOMY = {
    "languages": [
        "python", "java", "javascript", "typescript", "c++", "c#", "go",
        "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "matlab",
        "dart", "lua", "perl", "shell", "bash", "sql", "haskell", "elixir",
    ],
    "frontend": [
        "react", "angular", "vue", "svelte", "next.js", "nuxt", "gatsby",
        "html", "css", "sass", "tailwind", "bootstrap", "material ui",
        "webpack", "vite", "redux", "zustand", "jquery", "d3.js",
    ],
    "backend": [
        "node.js", "express", "django", "flask", "fastapi", "spring",
        "rails", "laravel", ".net", "asp.net", "gin", "fiber",
        "graphql", "rest api", "grpc", "websocket", "microservices",
    ],
    "databases": [
        "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
        "cassandra", "dynamodb", "sqlite", "oracle", "sql server",
        "neo4j", "firebase", "supabase", "prisma", "sqlalchemy",
    ],
    "cloud": [
        "aws", "gcp", "azure", "heroku", "vercel", "netlify", "render",
        "ec2", "s3", "lambda", "ecs", "eks", "fargate", "cloudfront",
        "cloud run", "app engine", "cloud functions",
    ],
    "devops": [
        "docker", "kubernetes", "terraform", "ansible", "jenkins",
        "github actions", "gitlab ci", "circleci", "nginx", "apache",
        "prometheus", "grafana", "datadog", "elk stack",
    ],
    "ml_ai": [
        "tensorflow", "pytorch", "scikit-learn", "keras", "xgboost",
        "lightgbm", "hugging face", "transformers", "langchain",
        "opencv", "spacy", "nltk", "pandas", "numpy", "scipy",
        "mlflow", "wandb", "ray", "dask", "spark",
        "machine learning", "deep learning", "nlp", "computer vision",
        "reinforcement learning", "neural network", "llm", "rag",
        "generative ai", "fine-tuning", "embeddings",
    ],
    "data_engineering": [
        "apache spark", "airflow", "kafka", "flink", "hadoop",
        "etl", "data pipeline", "data warehouse", "snowflake",
        "bigquery", "redshift", "dbt", "databricks",
    ],
    "mobile": [
        "react native", "flutter", "ios", "android", "swiftui",
        "jetpack compose", "expo", "xamarin",
    ],
    "testing": [
        "jest", "pytest", "junit", "selenium", "playwright",
        "cypress", "mocha", "chai", "unittest", "tdd", "bdd",
    ],
    "concepts": [
        "system design", "distributed systems", "data structures",
        "algorithms", "oop", "functional programming", "design patterns",
        "solid principles", "clean architecture", "domain driven design",
        "event driven", "cqrs", "event sourcing", "api design",
        "concurrency", "multithreading", "caching", "load balancing",
    ],
}

# Flatten for quick lookup
_ALL_SKILLS = {}
for domain, skills in SKILL_TAXONOMY.items():
    for skill in skills:
        _ALL_SKILLS[skill.lower()] = domain


# ── Domain mapping ────────────────────────────────────────────────

SKILL_TO_INTERVIEW_DOMAIN = {
    "languages": ["general_technical", "dsa"],
    "frontend": ["frontend"],
    "backend": ["backend", "system_design"],
    "databases": ["database", "backend"],
    "cloud": ["cloud", "devops", "system_design"],
    "devops": ["devops", "cloud"],
    "ml_ai": ["ml", "data_science"],
    "data_engineering": ["data_science", "backend"],
    "mobile": ["frontend", "general_technical"],
    "testing": ["general_technical"],
    "concepts": ["system_design", "dsa", "general_technical"],
}


class SkillExtractor:
    """Extracts structured skills from resume text for retrieval filtering."""

    def extract(self, resume_text: str) -> dict:
        """Extract skills, domains, and experience level from resume text.

        Returns:
            {
                "skills": ["python", "react", "aws", ...],
                "skill_domains": {"languages": [...], "frontend": [...]},
                "interview_domains": ["backend", "ml", ...],
                "experience_keywords": ["senior", "lead", ...],
            }
        """
        if not resume_text:
            return {
                "skills": [],
                "skill_domains": {},
                "interview_domains": [],
                "experience_keywords": [],
            }

        text_lower = resume_text.lower()
        found_skills: dict[str, list[str]] = {}
        all_skills: list[str] = []

        # Match skills against taxonomy
        for skill, domain in _ALL_SKILLS.items():
            # Use word boundary matching for short skills
            if len(skill) <= 3:
                pattern = rf'\b{re.escape(skill)}\b'
                if re.search(pattern, text_lower):
                    found_skills.setdefault(domain, []).append(skill)
                    all_skills.append(skill)
            else:
                if skill in text_lower:
                    found_skills.setdefault(domain, []).append(skill)
                    all_skills.append(skill)

        # Deduplicate
        all_skills = list(dict.fromkeys(all_skills))

        # Infer interview domains
        interview_domains = set()
        for domain in found_skills:
            mapped = SKILL_TO_INTERVIEW_DOMAIN.get(domain, ["general_technical"])
            interview_domains.update(mapped)

        # Detect experience level keywords
        experience_keywords = []
        exp_patterns = {
            "senior": r'\b(senior|sr\.?|lead|principal|staff)\b',
            "mid": r'\b(mid[- ]?level|intermediate)\b',
            "junior": r'\b(junior|jr\.?|entry[- ]?level|intern|fresh)\b',
        }
        for level, pattern in exp_patterns.items():
            if re.search(pattern, text_lower):
                experience_keywords.append(level)

        result = {
            "skills": all_skills,
            "skill_domains": {k: list(dict.fromkeys(v)) for k, v in found_skills.items()},
            "interview_domains": sorted(interview_domains),
            "experience_keywords": experience_keywords,
        }

        logger.info(
            f"Extracted {len(all_skills)} skills across "
            f"{len(found_skills)} domains → {len(interview_domains)} interview domains"
        )

        return result

    def get_retrieval_query(self, skills_data: dict) -> str:
        """Build a semantic query string from extracted skills for RAG retrieval."""
        parts = []

        top_skills = skills_data.get("skills", [])[:15]
        if top_skills:
            parts.append("Skills: " + ", ".join(top_skills))

        domains = skills_data.get("interview_domains", [])
        if domains:
            parts.append("Domains: " + ", ".join(domains))

        return " | ".join(parts) if parts else "general software engineering interview questions"
