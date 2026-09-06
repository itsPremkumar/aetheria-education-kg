"""Tests for Learning Path Generator."""

import pytest

from education_kg.graph import KnowledgeGraph
from education_kg.learning_path import LearningPathGenerator
from education_kg.models import Concept, ConceptDifficulty, Relation, RelationType


class TestLearningPathGenerator:
    def test_create(self):
        kg = KnowledgeGraph()
        generator = LearningPathGenerator(kg)
        assert generator is not None

    def test_generate_direct_path(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="c1", name="Basics"))
        kg.add_concept(Concept(id="c2", name="Advanced"))
        kg.add_relation(Relation("c1", "c2", RelationType.PREREQUISITE))
        generator = LearningPathGenerator(kg)
        path = generator.generate("c1", "c2")
        assert path is not None
        assert "c1" in path.concepts
        assert "c2" in path.concepts

    def test_generate_no_path(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="c1", name="A"))
        kg.add_concept(Concept(id="c2", name="B"))
        generator = LearningPathGenerator(kg)
        path = generator.generate("c1", "c2")
        assert path is not None  # Returns empty path
        assert len(path.concepts) == 0

    def test_generate_multi_step_path(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="c1", name="A"))
        kg.add_concept(Concept(id="c2", name="B"))
        kg.add_concept(Concept(id="c3", name="C"))
        kg.add_relation(Relation("c1", "c2", RelationType.PREREQUISITE))
        kg.add_relation(Relation("c2", "c3", RelationType.PREREQUISITE))
        generator = LearningPathGenerator(kg)
        path = generator.generate("c1", "c3")
        assert len(path.concepts) == 3

    def test_generate_from_prerequisites(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="c1", name="Basics"))
        kg.add_concept(Concept(id="c2", name="Advanced"))
        kg.add_relation(Relation("c1", "c2", RelationType.PREREQUISITE))
        generator = LearningPathGenerator(kg)
        path = generator.generate_from_prerequisites("c2")
        assert "c1" in path.concepts
        assert "c2" in path.concepts

    def test_estimated_hours(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="c1", name="A"))
        kg.add_concept(Concept(id="c2", name="B"))
        kg.add_relation(Relation("c1", "c2", RelationType.PREREQUISITE))
        generator = LearningPathGenerator(kg)
        path = generator.generate("c1", "c2")
        assert path.estimated_hours > 0
