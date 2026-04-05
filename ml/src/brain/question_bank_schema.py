"""Unified schema for the interview question bank.

All ingested datasets are normalized to this format for consistent
retrieval, filtering, and evaluation.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional


VALID_CATEGORIES = frozenset([
    "dsa", "system_design", "ml", "data_science", "frontend",
    "backend", "devops", "behavioral", "hr", "general_technical",
    "database", "networking", "os", "security", "cloud",
])

VALID_DIFFICULTIES = frozenset(["easy", "medium", "hard"])


@dataclass
class InterviewQuestion:
    """A single interview question with its ideal answer and metadata."""

    question: str
    answer: str = ""
    category: str = "general_technical"
    difficulty: str = "medium"
    tags: list[str] = field(default_factory=list)
    company: str = "generic"
    evaluation_points: list[str] = field(default_factory=list)
    source: str = "unknown"

    def __post_init__(self) -> None:
        self.category = self.category.lower().strip()
        self.difficulty = self.difficulty.lower().strip()
        self.tags = [t.lower().strip() for t in self.tags if t.strip()]

        if self.category not in VALID_CATEGORIES:
            self.category = "general_technical"
        if self.difficulty not in VALID_DIFFICULTIES:
            self.difficulty = "medium"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> InterviewQuestion:
        return cls(
            question=data.get("question", ""),
            answer=data.get("answer", ""),
            category=data.get("category", "general_technical"),
            difficulty=data.get("difficulty", "medium"),
            tags=data.get("tags", []),
            company=data.get("company", "generic"),
            evaluation_points=data.get("evaluation_points", []),
            source=data.get("source", "unknown"),
        )

    def is_valid(self) -> bool:
        return bool(self.question and len(self.question.strip()) >= 10)
