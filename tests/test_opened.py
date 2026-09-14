"""Tests for OpenEd — open education resource mapping."""

import pytest

from education_kg.graph import KnowledgeGraph
from education_kg.models import Concept, ConceptDifficulty, LearningPath, Relation, RelationType
from education_kg.learning_path import LearningPathGenerator
from education_kg.quiz_generator import QuizGenerator


class TestOpenEd:
    """Test OpenEd open education resource mapping."""

    def test_create_opened_graph(self):
        kg = KnowledgeGraph()
        assert kg is not None
        assert len(kg) == 0

    def test_add_opened_concepts(self):
        kg = KnowledgeGraph()
        concepts = [
            Concept(id="oe1", name="Open Educational Resources", description="Freely accessible teaching materials",
                    difficulty=ConceptDifficulty.BEGINNER, subject="education"),
            Concept(id="oe2", name="Creative Commons Licensing", description="Open licensing for educational content",
                    difficulty=ConceptDifficulty.INTERMEDIATE, subject="licensing"),
            Concept(id="oe3", name="MOOCs", description="Massive Open Online Courses",
                    difficulty=ConceptDifficulty.BEGINNER, subject="online_learning"),
        ]
        for c in concepts:
            kg.add_concept(c)
        assert len(kg) == 3

    def test_opened_learning_path(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="oe1", name="OER Basics", difficulty=ConceptDifficulty.BEGINNER))
        kg.add_concept(Concept(id="oe2", name="OER Advanced", difficulty=ConceptDifficulty.ADVANCED))
        kg.add_relation(Relation("oe1", "oe2", RelationType.PREREQUISITE))
        generator = LearningPathGenerator(kg)
        path = generator.generate("oe1", "oe2")
        assert path is not None
        assert "oe1" in path.concepts
        assert "oe2" in path.concepts

    def test_opened_quiz_generation(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="oe1", name="OER", description="Open Educational Resources",
                               difficulty=ConceptDifficulty.BEGINNER, subject="education"))
        generator = QuizGenerator(kg)
        quiz = generator.generate(["oe1"], num_questions=3)
        assert quiz is not None
        assert quiz.title != ""

    def test_opened_quiz_from_path(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="oe1", name="OER Basics"))
        kg.add_concept(Concept(id="oe2", name="OER Licensing"))
        kg.add_concept(Concept(id="oe3", name="OER Implementation"))
        kg.add_relation(Relation("oe1", "oe2", RelationType.PREREQUISITE))
        kg.add_relation(Relation("oe2", "oe3", RelationType.PREREQUISITE))
        generator = QuizGenerator(kg)
        quiz = generator.generate_from_path(["oe1", "oe2", "oe3"], num_questions=5)
        assert quiz is not None

    def test_opened_relation_types(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="oe1", name="OER"))
        kg.add_concept(Concept(id="oe2", name="Open Access"))
        kg.add_concept(Concept(id="oe3", name="Open Source"))
        kg.add_relation(Relation("oe1", "oe2", RelationType.RELATEDTO))
        kg.add_relation(Relation("oe1", "oe3", RelationType.BUILDSON))
        related = kg.get_related_concepts("oe1")
        assert len(related) == 2

    def test_opened_search_by_subject(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="oe1", name="OER", subject="education"))
        kg.add_concept(Concept(id="oe2", name="Physics", subject="science"))
        results = kg.search("", subject="education")
        assert len(results) == 1
        assert results[0].name == "OER"

    def test_opened_search_by_difficulty(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="oe1", name="Basic OER", difficulty=ConceptDifficulty.BEGINNER))
        kg.add_concept(Concept(id="oe2", name="Advanced OER", difficulty=ConceptDifficulty.ADVANCED))
        results = kg.search("", difficulty=ConceptDifficulty.BEGINNER)
        assert len(results) == 1

    def test_opened_statistics(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="oe1", name="OER", difficulty=ConceptDifficulty.BEGINNER, subject="education"))
        kg.add_concept(Concept(id="oe2", name="MOOCs", difficulty=ConceptDifficulty.BEGINNER, subject="online_learning"))
        kg.add_relation(Relation("oe1", "oe2", RelationType.RELATEDTO))
        stats = kg.get_statistics()
        assert stats["total_concepts"] == 2
        assert stats["total_relations"] == 1
        assert "education" in stats["subjects"]

    def test_opened_learning_path_from_prerequisites(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="oe1", name="OER Basics", difficulty=ConceptDifficulty.BEGINNER))
        kg.add_concept(Concept(id="oe2", name="OER Licensing", difficulty=ConceptDifficulty.INTERMEDIATE))
        kg.add_concept(Concept(id="oe3", name="OER Implementation", difficulty=ConceptDifficulty.ADVANCED))
        kg.add_relation(Relation("oe1", "oe2", RelationType.PREREQUISITE))
        kg.add_relation(Relation("oe2", "oe3", RelationType.PREREQUISITE))
        generator = LearningPathGenerator(kg)
        path = generator.generate_from_prerequisites("oe3")
        assert "oe1" in path.concepts
        assert "oe2" in path.concepts
        assert "oe3" in path.concepts

    def test_opened_estimated_hours(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="oe1", name="OER Basics"))
        kg.add_concept(Concept(id="oe2", name="OER Advanced"))
        kg.add_relation(Relation("oe1", "oe2", RelationType.PREREQUISITE))
        generator = LearningPathGenerator(kg)
        path = generator.generate("oe1", "oe2")
        assert path.estimated_hours > 0
