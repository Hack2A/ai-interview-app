"""Dataset ingestion pipeline — downloads, normalizes, and deduplicates
interview question datasets into a unified question bank.

Kaggle API token is read from the KAGGLE_API_TOKEN environment variable
or from a .env file. It is NEVER hardcoded.

Usage:
    # Set token via environment:
    $env:KAGGLE_API_TOKEN = "KGAT_xxxxx"
    python -m scripts.ingest_datasets

    # Or put it in ml/.env:
    KAGGLE_API_TOKEN=KGAT_xxxxx
"""
from __future__ import annotations

import json
import logging
import os
import re
import sys
from pathlib import Path
from difflib import SequenceMatcher

# ── Path setup (avoid importing config.settings which triggers llama_cpp) ──
_SCRIPT_DIR = Path(__file__).resolve().parent
_ML_ROOT = _SCRIPT_DIR.parent

from dotenv import load_dotenv

# Direct-load question_bank_schema WITHOUT triggering src/brain/__init__.py
# (which imports Evaluator → llama_cpp, not needed for ingestion).
# We register the module in sys.modules so Python 3.11's @dataclass works.
import importlib.util as _ilu
_schema_path = _ML_ROOT / "src" / "brain" / "question_bank_schema.py"
_spec = _ilu.spec_from_file_location("question_bank_schema", _schema_path)
_schema_mod = _ilu.module_from_spec(_spec)
sys.modules["question_bank_schema"] = _schema_mod
_spec.loader.exec_module(_schema_mod)
InterviewQuestion = _schema_mod.InterviewQuestion

# Direct path constants (mirrors config/settings.py without heavy imports)
BASE_DIR = _ML_ROOT
QUESTION_BANK_PATH = BASE_DIR / "data" / "datasets" / "question_bank.json"
DATASETS_RAW_DIR = BASE_DIR / "data" / "datasets" / "raw"

logger = logging.getLogger("DatasetIngestion")
logging.basicConfig(level=logging.INFO, format="%(name)s | %(message)s")

# ── Dataset registry (all 6 from the original spec) ──────────────
KAGGLE_DATASETS = {
    "hr_technical": "mohakpatel2004/interview-questions-hrtechnical",
    "swe_questions": "syedmharis/software-engineering-interview-questions-dataset",
    "ds_questions": "die9origephit/data-science-interview-questions",
    "mock_interview": "aman9das/mock-interview-questions-answers",
}

HUGGINGFACE_DATASETS = {
    "hf_interviews": "awinml/all-interview-questions",
}

# GitHub raw Q&A (ML focused)
GITHUB_DATASETS = {
    "ml_qa": "https://raw.githubusercontent.com/andrewekhalel/MLQuestions/master/README.md",
}


# ── Kaggle token handling ─────────────────────────────────────────

def _setup_kaggle_auth() -> bool:
    """Configure kagglehub authentication from environment variable.

    Reads KAGGLE_API_TOKEN from env or .env file.
    Returns True if a token was found.
    """
    load_dotenv(BASE_DIR / ".env")
    token = os.environ.get("KAGGLE_API_TOKEN")

    if not token:
        logger.warning(
            "KAGGLE_API_TOKEN not set. "
            "Set it via: $env:KAGGLE_API_TOKEN='KGAT_xxx' or add to ml/.env"
        )
        return False

    # kagglehub reads from this env var automatically
    os.environ["KAGGLE_API_TOKEN"] = token
    logger.info("Kaggle API token loaded from environment (not hardcoded)")
    return True


# ── Category inference ────────────────────────────────────────────

_CATEGORY_KEYWORDS = {
    "dsa": ["array", "linked list", "tree", "graph", "sorting", "searching",
             "stack", "queue", "hash", "dynamic programming", "recursion",
             "algorithm", "big o", "complexity", "binary search"],
    "system_design": ["design", "scalab", "load balancer", "microservice",
                       "caching", "database design", "api design", "distributed"],
    "ml": ["machine learning", "neural network", "deep learning", "gradient",
            "backpropagation", "overfitting", "regularization", "ensemble",
            "random forest", "svm", "clustering", "classification", "regression model"],
    "data_science": ["data analysis", "pandas", "numpy", "statistics",
                      "probability", "hypothesis", "visualization", "eda",
                      "feature engineering", "data cleaning"],
    "frontend": ["react", "javascript", "css", "html", "dom", "vue",
                  "angular", "typescript", "responsive", "webpack"],
    "backend": ["api", "rest", "server", "node", "express", "django",
                 "flask", "authentication", "middleware", "database"],
    "behavioral": ["tell me about", "describe a time", "how do you handle",
                    "leadership", "teamwork", "conflict", "challenge",
                    "strength", "weakness", "motivation"],
    "hr": ["salary", "career goal", "why this company", "where do you see",
            "work-life", "culture fit", "notice period", "relocation"],
    "database": ["sql", "nosql", "join", "index", "normalization",
                  "transaction", "acid", "mongodb", "postgresql"],
    "devops": ["docker", "kubernetes", "ci/cd", "jenkins", "terraform",
                "aws", "cloud", "deployment", "monitoring"],
    "os": ["process", "thread", "memory management", "deadlock",
            "scheduling", "virtual memory", "file system"],
    "networking": ["tcp", "udp", "http", "dns", "ip address", "osi model",
                    "socket", "load balancing", "cdn"],
}


def infer_category(question: str, existing_category: str = "") -> str:
    """Infer the best category from question text."""
    if existing_category and existing_category.lower() in {
        "dsa", "system_design", "ml", "data_science", "frontend",
        "backend", "behavioral", "hr", "database", "devops", "os", "networking"
    }:
        return existing_category.lower()

    q_lower = question.lower()
    scores = {}
    for cat, keywords in _CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in q_lower)
        if score > 0:
            scores[cat] = score

    return max(scores, key=scores.get) if scores else "general_technical"


def infer_difficulty(text: str, existing: str = "") -> str:
    """Infer difficulty from text or metadata."""
    if existing and existing.lower() in ("easy", "medium", "hard"):
        return existing.lower()

    t = text.lower()
    if any(w in t for w in ["basic", "simple", "define", "what is", "list"]):
        return "easy"
    if any(w in t for w in ["design", "architect", "optimize", "complex", "advanced"]):
        return "hard"
    return "medium"


def extract_tags(question: str) -> list[str]:
    """Extract technology/concept tags from question text."""
    tech_keywords = [
        "python", "java", "javascript", "c++", "sql", "react", "node",
        "docker", "kubernetes", "aws", "gcp", "azure", "git", "linux",
        "tensorflow", "pytorch", "pandas", "numpy", "mongodb", "redis",
        "postgresql", "mysql", "html", "css", "rest", "graphql", "api",
        "microservice", "agile", "scrum", "ci/cd", "machine learning",
        "deep learning", "nlp", "computer vision", "data structure",
    ]
    q_lower = question.lower()
    return [t for t in tech_keywords if t in q_lower]


# ── Dataset adapters ──────────────────────────────────────────────

def _adapt_hr_technical(raw_dir: Path) -> list[InterviewQuestion]:
    """Adapter for mohakpatel2004/interview-questions-hrtechnical."""
    import pandas as pd
    questions = []
    for csv_file in raw_dir.glob("*.csv"):
        try:
            df = pd.read_csv(csv_file)
            for _, row in df.iterrows():
                q_text = str(row.get("Question", row.get("question", ""))).strip()
                if not q_text or len(q_text) < 10:
                    continue

                cat_raw = str(row.get("Category", row.get("category", ""))).strip()
                diff_raw = str(row.get("Difficulty", row.get("difficulty", ""))).strip()
                answer = str(row.get("Answer", row.get("answer", ""))).strip()
                if answer == "nan":
                    answer = ""

                questions.append(InterviewQuestion(
                    question=q_text,
                    answer=answer,
                    category=infer_category(q_text, cat_raw),
                    difficulty=infer_difficulty(q_text, diff_raw),
                    tags=extract_tags(q_text),
                    source="kaggle/hr_technical",
                ))
        except Exception as e:
            logger.warning(f"Failed to parse {csv_file.name}: {e}")
    return questions


def _adapt_swe_questions(raw_dir: Path) -> list[InterviewQuestion]:
    """Adapter for syedmharis/software-engineering-interview-questions-dataset."""
    import pandas as pd
    questions = []
    for csv_file in raw_dir.glob("*.csv"):
        try:
            df = pd.read_csv(csv_file)
            for _, row in df.iterrows():
                q_text = str(row.get("Question", row.get("question", ""))).strip()
                if not q_text or len(q_text) < 10:
                    continue

                answer = str(row.get("Brief Answer", row.get("Answer", row.get("answer", "")))).strip()
                if answer == "nan":
                    answer = ""
                cat_raw = str(row.get("Category", row.get("category", ""))).strip()
                diff_raw = str(row.get("Difficulty", row.get("difficulty", ""))).strip()

                questions.append(InterviewQuestion(
                    question=q_text,
                    answer=answer,
                    category=infer_category(q_text, cat_raw),
                    difficulty=infer_difficulty(q_text, diff_raw),
                    tags=extract_tags(q_text),
                    source="kaggle/swe_questions",
                ))
        except Exception as e:
            logger.warning(f"Failed to parse {csv_file.name}: {e}")
    return questions


def _adapt_ds_questions(raw_dir: Path) -> list[InterviewQuestion]:
    """Adapter for die9origephit/data-science-interview-questions."""
    import pandas as pd
    questions = []
    for f in raw_dir.glob("*"):
        if f.suffix.lower() in (".csv", ".tsv"):
            try:
                sep = "\t" if f.suffix == ".tsv" else ","
                df = pd.read_csv(f, sep=sep)
                for _, row in df.iterrows():
                    # Try multiple possible column names
                    q_text = ""
                    for col in ["Question", "question", "Questions"]:
                        if col in df.columns:
                            q_text = str(row[col]).strip()
                            break
                    if not q_text or q_text == "nan" or len(q_text) < 10:
                        continue

                    answer = ""
                    for col in ["Answer", "answer", "Answers"]:
                        if col in df.columns:
                            answer = str(row[col]).strip()
                            if answer == "nan":
                                answer = ""
                            break

                    questions.append(InterviewQuestion(
                        question=q_text,
                        answer=answer,
                        category="data_science",
                        difficulty=infer_difficulty(q_text),
                        tags=extract_tags(q_text) + ["data science"],
                        source="kaggle/ds_questions",
                    ))
            except Exception as e:
                logger.warning(f"Failed to parse {f.name}: {e}")
    return questions


def _adapt_mock_interview(raw_dir: Path) -> list[InterviewQuestion]:
    """Adapter for aman9das/mock-interview-questions-answers."""
    import pandas as pd
    questions = []
    for csv_file in raw_dir.glob("*.csv"):
        try:
            df = pd.read_csv(csv_file)
            for _, row in df.iterrows():
                q_text = str(row.get("Question", row.get("question", ""))).strip()
                if not q_text or q_text == "nan" or len(q_text) < 10:
                    continue

                answer = str(row.get("Answer", row.get("answer", ""))).strip()
                if answer == "nan":
                    answer = ""
                field_val = str(row.get("Field", row.get("Subfield", ""))).strip()
                tier = str(row.get("Tier", "")).strip().lower()

                diff = "easy"
                if tier in ("tier 2", "mid"):
                    diff = "medium"
                elif tier in ("tier 3", "senior", "advanced"):
                    diff = "hard"

                questions.append(InterviewQuestion(
                    question=q_text,
                    answer=answer,
                    category=infer_category(q_text, field_val),
                    difficulty=diff,
                    tags=extract_tags(q_text),
                    company="generic",
                    source="kaggle/mock_interview",
                ))
        except Exception as e:
            logger.warning(f"Failed to parse {csv_file.name}: {e}")
    return questions


def _adapt_github_ml(raw_dir: Path) -> list[InterviewQuestion]:
    """Adapter for GitHub ML Q&A from andrewekhalel/MLQuestions."""
    import requests

    questions = []
    url = GITHUB_DATASETS["ml_qa"]

    # Try cached file first
    cached = raw_dir / "ml_qa_github.md"
    if cached.exists():
        content = cached.read_text(encoding="utf-8")
    else:
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            content = resp.text
            cached.write_text(content, encoding="utf-8")
        except Exception as e:
            logger.warning(f"Failed to fetch GitHub ML Q&A: {e}")
            return questions

    # Parse markdown Q&A pairs (## Question / Answer pattern)
    blocks = re.split(r'\n##\s+', content)
    for block in blocks:
        lines = block.strip().split("\n")
        if not lines:
            continue

        q_line = lines[0].strip().lstrip("#").strip()
        if len(q_line) < 15:
            continue

        answer_lines = [l for l in lines[1:] if l.strip() and not l.startswith("#")]
        answer = "\n".join(answer_lines).strip()

        questions.append(InterviewQuestion(
            question=q_line,
            answer=answer[:2000],
            category="ml",
            difficulty=infer_difficulty(q_line),
            tags=extract_tags(q_line) + ["machine learning"],
            source="github/ml_questions",
        ))

    return questions


def _adapt_huggingface(raw_dir: Path) -> list[InterviewQuestion]:
    """Adapter for HuggingFace awinml/all-interview-questions dataset."""
    questions = []
    try:
        from datasets import load_dataset
        ds = load_dataset("awinml/all-interview-questions", split="train")

        for row in ds:
            q_text = str(row.get("question", row.get("Question", ""))).strip()
            if not q_text or len(q_text) < 10:
                continue

            answer = str(row.get("answer", row.get("Answer", ""))).strip()
            if answer == "None" or answer == "nan":
                answer = ""

            questions.append(InterviewQuestion(
                question=q_text,
                answer=answer[:2000],
                category=infer_category(q_text),
                difficulty=infer_difficulty(q_text),
                tags=extract_tags(q_text),
                source="huggingface/all_interview_questions",
            ))

    except Exception as e:
        logger.warning(f"HuggingFace dataset load failed: {e}")
        logger.info("Skipping HuggingFace dataset — install 'datasets' or check network.")

    return questions


# ── Kaggle download ───────────────────────────────────────────────

def download_kaggle_datasets() -> dict[str, Path]:
    """Download Kaggle datasets using kagglehub. Returns {name: local_path}."""
    paths = {}

    try:
        import kagglehub
    except ImportError:
        logger.error("kagglehub not installed. Run: pip install kagglehub")
        return paths

    if not _setup_kaggle_auth():
        logger.warning("Kaggle auth not configured — will only use local/cached files")
        return paths

    for name, dataset_id in KAGGLE_DATASETS.items():
        try:
            logger.info(f"Downloading {name} ({dataset_id})...")
            path = kagglehub.dataset_download(dataset_id)
            paths[name] = Path(path)
            logger.info(f"  → {path}")
        except Exception as e:
            logger.warning(f"Failed to download {name}: {e}")

    return paths


# ── Deduplication ─────────────────────────────────────────────────

def deduplicate(questions: list[InterviewQuestion],
                threshold: float = 0.85) -> list[InterviewQuestion]:
    """Remove near-duplicate questions using fuzzy matching."""
    unique = []
    seen_normalized = set()

    for q in questions:
        # Fast exact-match dedup first
        normalized = re.sub(r'\s+', ' ', q.question.lower().strip())
        if normalized in seen_normalized:
            continue
        seen_normalized.add(normalized)

        # Fuzzy dedup against recent entries (sliding window for performance)
        is_dup = False
        for existing in unique[-200:]:
            ratio = SequenceMatcher(
                None, normalized,
                re.sub(r'\s+', ' ', existing.question.lower().strip())
            ).ratio()
            if ratio >= threshold:
                is_dup = True
                # Keep the one with more complete data
                if len(q.answer) > len(existing.answer):
                    unique.remove(existing)
                    unique.append(q)
                break

        if not is_dup:
            unique.append(q)

    return unique


# ── Main pipeline ─────────────────────────────────────────────────

def run_ingestion() -> Path:
    """Run the full ingestion pipeline and produce question_bank.json."""
    all_questions: list[InterviewQuestion] = []

    # Ensure output dirs exist
    DATASETS_RAW_DIR.mkdir(parents=True, exist_ok=True)
    QUESTION_BANK_PATH.parent.mkdir(parents=True, exist_ok=True)

    # ── Phase 1: Download Kaggle datasets ──
    logger.info("=" * 50)
    logger.info("PHASE 1: Downloading Kaggle datasets...")
    kaggle_paths = download_kaggle_datasets()

    # ── Phase 2: Adapt each dataset ──
    logger.info("=" * 50)
    logger.info("PHASE 2: Adapting datasets...")

    adapters = {
        "hr_technical": _adapt_hr_technical,
        "swe_questions": _adapt_swe_questions,
        "ds_questions": _adapt_ds_questions,
        "mock_interview": _adapt_mock_interview,
    }

    for name, adapter_fn in adapters.items():
        source_dir = kaggle_paths.get(name, DATASETS_RAW_DIR / name)
        if source_dir.exists():
            questions = adapter_fn(source_dir)
            logger.info(f"  {name}: {len(questions)} questions")
            all_questions.extend(questions)
        else:
            logger.warning(f"  {name}: directory not found at {source_dir}")

    # ── Phase 3: GitHub ML Q&A ──
    logger.info("Fetching GitHub ML Q&A...")
    ml_questions = _adapt_github_ml(DATASETS_RAW_DIR)
    logger.info(f"  github/ml_qa: {len(ml_questions)} questions")
    all_questions.extend(ml_questions)

    # ── Phase 4: HuggingFace dataset ──
    logger.info("Loading HuggingFace dataset...")
    hf_questions = _adapt_huggingface(DATASETS_RAW_DIR)
    logger.info(f"  huggingface: {len(hf_questions)} questions")
    all_questions.extend(hf_questions)

    # ── Phase 5: Filter invalid entries ──
    valid = [q for q in all_questions if q.is_valid()]
    logger.info(f"\nTotal raw: {len(all_questions)} → Valid: {len(valid)}")

    # ── Phase 6: Deduplicate ──
    logger.info("Deduplicating...")
    unique = deduplicate(valid)
    logger.info(f"After dedup: {len(unique)} questions")

    # ── Phase 7: Auto-generate evaluation points for entries missing them ──
    for q in unique:
        if not q.evaluation_points:
            q.evaluation_points = _generate_eval_points(q)

    # ── Phase 8: Save ──
    output = [q.to_dict() for q in unique]
    with open(QUESTION_BANK_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    logger.info(f"\n✅ Question bank saved: {QUESTION_BANK_PATH}")
    logger.info(f"   Total questions: {len(output)}")

    # Category breakdown
    from collections import Counter
    cats = Counter(q.category for q in unique)
    diffs = Counter(q.difficulty for q in unique)
    logger.info(f"   Categories: {dict(cats)}")
    logger.info(f"   Difficulties: {dict(diffs)}")

    return QUESTION_BANK_PATH


def _generate_eval_points(q: InterviewQuestion) -> list[str]:
    """Auto-generate evaluation criteria from question content."""
    points = ["relevance_to_question", "technical_accuracy"]

    cat = q.category
    if cat in ("dsa", "general_technical", "backend"):
        points.extend(["time_complexity_awareness", "code_quality"])
    elif cat == "system_design":
        points.extend(["scalability_thinking", "trade_off_analysis"])
    elif cat in ("ml", "data_science"):
        points.extend(["mathematical_understanding", "practical_application"])
    elif cat == "behavioral":
        points.extend(["star_method_usage", "self_awareness"])
    elif cat == "hr":
        points.extend(["authenticity", "cultural_alignment"])

    points.append("communication_clarity")
    return points


if __name__ == "__main__":
    run_ingestion()
