"""Tests for Knowledge Graph models."""

import pytest

from education_kg.models import (
    Concept,
    ConceptDifficulty,
    LearningPath,
    Quiz,
    QuizQuestion,
    Relation,
    RelationType,
)


class TestConceptDifficulty:
    def test_values(self):
        assert ConceptDifficulty.BEGINNER.value == "beginner"
        assert ConceptDifficulty.INTERMEDIATE.value == "intermediate"
        assert ConceptDifficulty.ADVANCED.value == "advanced"


class TestRelationType:
    def test_values(self):
        assert RelationType.PREREQUISITE.value == "prerequisite"
        assert RelationType.BUILDSON.value == "builds_on"
        assert RelationType.RELATEDTO.value == "related_to"


class TestConcept:
    def test_create(self):
        concept = Concept(id="c1", name="Python Basics")
        assert concept.id == "c1"
        assert concept.name == "Python Basics"
        assert concept.difficulty == ConceptDifficulty.BEGINNER

    def test_to_dict(self):
        concept = Concept(id="c1", name="Test", description="Desc")
        data = concept.to_dict()
        assert data["id"] == "c1"
        assert data["name"] == "Test"
        assert "difficulty" in data


class TestRelation:
    def test_create(self):
        rel = Relation("c1", "c2", RelationType.PREREQUISITE)
        assert rel.source_id == "c1"
        assert rel.target_id == "c2"
        assert rel.relation_type == RelationType.PREREQUISITE

    def test_to_dict(self):
        rel = Relation("c1", "c2", RelationType.BUILDSON)
        data = rel.to_dict()
        assert data["source_id"] == "c1"
        assert data["relation_type"] == "builds_on"


class TestLearningPath:
    def test_create(self):
        path = LearningPath(id="lp1", title="Python Path", concepts=["c1", "c2"])
        assert path.id == "lp1"
        assert len(path.concepts) == 2

    def test_to_dict(self):
        path = LearningPath(id="lp1", title="Test", concepts=["c1"])
        data = path.to_dict()
        assert data["id"] == "lp1"
        assert data["concepts"] == ["c1"]


class TestQuizQuestion:
    def test_create(self):
        q = QuizQuestion("What is Python?", ["Language", "Snake", "Both"], 2)
        assert q.question == "What is Python?"
        assert q.correct_answer == 2


class TestQuiz:
    def test_create(self):
        q = Quiz(id="q1", title="Python Quiz", questions=[])
        assert q.id == "q1"
        assert q.questions == []

    def test_to_dict(self):
        q = Quiz(id="q1", title="Quiz", questions=[])
        data = q.to_dict()
        assert data["id"] == "q1"
        assert data["questions"] == []
