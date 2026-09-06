"""Tests for Quiz Generator."""

import pytest

from education_kg.graph import KnowledgeGraph
from education_kg.models import Concept, ConceptDifficulty, Relation, RelationType
from education_kg.quiz_generator import QuizGenerator


class TestQuizGenerator:
    def test_create(self):
        kg = KnowledgeGraph()
        generator = QuizGenerator(kg)
        assert generator is not None

    def test_generate_basic(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="c1", name="Python", description="A programming language"))
        generator = QuizGenerator(kg)
        quiz = generator.generate(["c1"], num_questions=2)
        assert quiz is not None
        assert quiz.title != ""

    def test_generate_multiple_concepts(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="c1", name="Python", description="A language"))
        kg.add_concept(Concept(id="c2", name="Java", description="Another language"))
        kg.add_relation(Relation("c1", "c2", RelationType.RELATEDTO))
        generator = QuizGenerator(kg)
        quiz = generator.generate(["c1", "c2"], num_questions=5)
        assert len(quiz.questions) <= 5

    def test_generate_no_concepts(self):
        kg = KnowledgeGraph()
        generator = QuizGenerator(kg)
        quiz = generator.generate([], num_questions=5)
        assert quiz.questions == []

    def test_generate_from_path(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="c1", name="A"))
        kg.add_concept(Concept(id="c2", name="B"))
        kg.add_concept(Concept(id="c3", name="C"))
        kg.add_relation(Relation("c1", "c2", RelationType.PREREQUISITE))
        kg.add_relation(Relation("c2", "c3", RelationType.PREREQUISITE))
        generator = QuizGenerator(kg)
        quiz = generator.generate_from_path(["c1", "c2", "c3"], num_questions=10)
        assert quiz is not None

    def test_generate_with_difficulty(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="c1", name="Advanced Topic", description="Complex topic", difficulty=ConceptDifficulty.ADVANCED))
        generator = QuizGenerator(kg)
        quiz = generator.generate(["c1"], num_questions=3, difficulty=ConceptDifficulty.ADVANCED)
        assert quiz.difficulty == ConceptDifficulty.ADVANCED
