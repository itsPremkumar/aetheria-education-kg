"""Tests for EduGraph — educational graph analytics."""

import pytest

from education_kg.graph import KnowledgeGraph
from education_kg.models import Concept, ConceptDifficulty, Relation, RelationType
from education_kg.reasoning import ReasoningEngine
from education_kg.learning_path import LearningPathGenerator


class TestEduGraph:
    """Test EduGraph educational graph analytics."""

    def test_create_edugraph(self):
        kg = KnowledgeGraph()
        assert kg is not None
        assert len(kg) == 0

    def test_edugraph_concept_density(self):
        kg = KnowledgeGraph()
        for i in range(10):
            kg.add_concept(Concept(id=f"eg{i}", name=f"Concept {i}", difficulty=ConceptDifficulty.BEGINNER))
        for i in range(9):
            kg.add_relation(Relation(f"eg{i}", f"eg{i+1}", RelationType.PREREQUISITE))
        stats = kg.get_statistics()
        assert stats["total_concepts"] == 10
        assert stats["total_relations"] == 9

    def test_edugraph_centrality(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="eg1", name="Central Concept"))
        kg.add_concept(Concept(id="eg2", name="Related 1"))
        kg.add_concept(Concept(id="eg3", name="Related 2"))
        kg.add_concept(Concept(id="eg4", name="Related 3"))
        kg.add_relation(Relation("eg1", "eg2", RelationType.RELATEDTO))
        kg.add_relation(Relation("eg1", "eg3", RelationType.RELATEDTO))
        kg.add_relation(Relation("eg1", "eg4", RelationType.RELATEDTO))
        related = kg.get_related_concepts("eg1")
        assert len(related) == 3

    def test_edugraph_reasoning(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="eg1", name="Mathematics", description="Study of numbers and patterns",
                               difficulty=ConceptDifficulty.BEGINNER))
        kg.add_concept(Concept(id="eg2", name="Algebra", description="Branch of mathematics",
                               difficulty=ConceptDifficulty.INTERMEDIATE))
        kg.add_relation(Relation("eg1", "eg2", RelationType.PREREQUISITE))
        engine = ReasoningEngine(kg)
        result = engine.answer("Tell me about Mathematics", "eg1")
        assert result.confidence > 0
        assert "Mathematics" in result.answer

    def test_edugraph_explain_relationship(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="eg1", name="Arithmetic"))
        kg.add_concept(Concept(id="eg2", name="Algebra"))
        kg.add_relation(Relation("eg1", "eg2", RelationType.PREREQUISITE))
        engine = ReasoningEngine(kg)
        result = engine.explain("eg1", "eg2")
        assert "Arithmetic" in result.answer
        assert "Algebra" in result.answer

    def test_edugraph_learning_path_optimization(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="eg1", name="Basic Math", difficulty=ConceptDifficulty.BEGINNER))
        kg.add_concept(Concept(id="eg2", name="Algebra", difficulty=ConceptDifficulty.INTERMEDIATE))
        kg.add_concept(Concept(id="eg3", name="Calculus", difficulty=ConceptDifficulty.ADVANCED))
        kg.add_relation(Relation("eg1", "eg2", RelationType.PREREQUISITE))
        kg.add_relation(Relation("eg2", "eg3", RelationType.PREREQUISITE))
        generator = LearningPathGenerator(kg)
        path = generator.generate("eg1", "eg3")
        assert len(path.concepts) == 3
        assert path.estimated_hours > 0

    def test_edugraph_difficulty_progression(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="eg1", name="Beginner", difficulty=ConceptDifficulty.BEGINNER))
        kg.add_concept(Concept(id="eg2", name="Intermediate", difficulty=ConceptDifficulty.INTERMEDIATE))
        kg.add_concept(Concept(id="eg3", name="Advanced", difficulty=ConceptDifficulty.ADVANCED))
        kg.add_relation(Relation("eg1", "eg2", RelationType.PREREQUISITE))
        kg.add_relation(Relation("eg2", "eg3", RelationType.PREREQUISITE))
        generator = LearningPathGenerator(kg)
        path = generator.generate("eg1", "eg3")
        assert path.difficulty == ConceptDifficulty.ADVANCED

    def test_edugraph_search_relevance(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="eg1", name="Python Programming", description="Learn Python",
                               difficulty=ConceptDifficulty.BEGINNER, tags=["programming"]))
        kg.add_concept(Concept(id="eg2", name="Java Programming", description="Learn Java",
                               difficulty=ConceptDifficulty.BEGINNER, tags=["programming"]))
        kg.add_concept(Concept(id="eg3", name="History", description="World history",
                               difficulty=ConceptDifficulty.BEGINNER, tags=["humanities"]))
        results = kg.search("programming")
        assert len(results) == 2

    def test_edugraph_tag_filtering(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="eg1", name="Python", tags=["programming", "language"]))
        kg.add_concept(Concept(id="eg2", name="Java", tags=["programming", "language"]))
        kg.add_concept(Concept(id="eg3", name="History", tags=["humanities"]))
        results = kg.search("programming")
        assert len(results) == 2

    def test_edugraph_graph_traversal(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="eg1", name="A"))
        kg.add_concept(Concept(id="eg2", name="B"))
        kg.add_concept(Concept(id="eg3", name="C"))
        kg.add_concept(Concept(id="eg4", name="D"))
        kg.add_relation(Relation("eg1", "eg2", RelationType.PREREQUISITE))
        kg.add_relation(Relation("eg2", "eg3", RelationType.PREREQUISITE))
        kg.add_relation(Relation("eg3", "eg4", RelationType.PREREQUISITE))
        path = kg.find_path("eg1", "eg4")
        assert path is not None
        assert len(path) == 4

    def test_edugraph_cycle_handling(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="eg1", name="A"))
        kg.add_concept(Concept(id="eg2", name="B"))
        kg.add_concept(Concept(id="eg3", name="C"))
        kg.add_relation(Relation("eg1", "eg2", RelationType.PREREQUISITE))
        kg.add_relation(Relation("eg2", "eg3", RelationType.PREREQUISITE))
        sorted_ids = kg.topological_sort()
        assert len(sorted_ids) == 3
        assert sorted_ids.index("eg1") < sorted_ids.index("eg2")
