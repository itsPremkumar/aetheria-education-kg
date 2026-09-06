"""Data models for Education Knowledge Graph."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class ConceptDifficulty(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class RelationType(Enum):
    PREREQUISITE = "prerequisite"
    BUILDSON = "builds_on"
    RELATEDTO = "related_to"
    PARTOF = "part_of"
    LEADSTO = "leads_to"


@dataclass
class Concept:
    id: str
    name: str
    description: str = ""
    difficulty: ConceptDifficulty = ConceptDifficulty.BEGINNER
    subject: str = ""
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "difficulty": self.difficulty.value,
            "subject": self.subject,
            "tags": self.tags,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class Relation:
    source_id: str
    target_id: str
    relation_type: RelationType
    weight: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type.value,
            "weight": self.weight,
            "metadata": self.metadata,
        }


@dataclass
class LearningPath:
    id: str
    title: str
    concepts: list[str]
    estimated_hours: float = 0.0
    difficulty: ConceptDifficulty = ConceptDifficulty.BEGINNER
    description: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "concepts": self.concepts,
            "estimated_hours": self.estimated_hours,
            "difficulty": self.difficulty.value,
            "description": self.description,
        }


@dataclass
class QuizQuestion:
    question: str
    options: list[str]
    correct_answer: int
    explanation: str = ""
    concept_id: str = ""


@dataclass
class Quiz:
    id: str
    title: str
    questions: list[QuizQuestion]
    difficulty: ConceptDifficulty = ConceptDifficulty.BEGINNER
    subject: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "questions": [
                {
                    "question": q.question,
                    "options": q.options,
                    "correct_answer": q.correct_answer,
                    "explanation": q.explanation,
                    "concept_id": q.concept_id,
                }
                for q in self.questions
            ],
            "difficulty": self.difficulty.value,
            "subject": self.subject,
        }
