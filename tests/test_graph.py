"""Tests for Knowledge Graph."""

import pytest

from education_kg.graph import KnowledgeGraph
from education_kg.models import (
    Concept,
    ConceptDifficulty,
    Relation,
    RelationType,
)


class TestKnowledgeGraph:
    def test_create(self):
        kg = KnowledgeGraph()
        assert kg is not None
        assert len(kg) == 0

    def test_add_concept(self):
        kg = KnowledgeGraph()
        concept = Concept(id="c1", name="Python")
        kg.add_concept(concept)
        assert len(kg) == 1
        assert "c1" in kg

    def test_get_concept(self):
        kg = KnowledgeGraph()
        concept = Concept(id="c1", name="Python")
        kg.add_concept(concept)
        result = kg.get_concept("c1")
        assert result is not None
        assert result.name == "Python"

    def test_get_all_concepts(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="c1", name="Python"))
        kg.add_concept(Concept(id="c2", name="Java"))
        assert len(kg.get_all_concepts()) == 2

    def test_add_relation(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="c1", name="Python"))
        kg.add_concept(Concept(id="c2", name="Advanced Python"))
        kg.add_relation(Relation("c1", "c2", RelationType.PREREQUISITE))
        relations = kg.get_relations("c1")
        assert len(relations) == 1
        assert relations[0].target_id == "c2"

    def test_get_prerequisites(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="c1", name="Basics"))
        kg.add_concept(Concept(id="c2", name="Advanced"))
        kg.add_relation(Relation("c1", "c2", RelationType.PREREQUISITE))
        prereqs = kg.get_prerequisites("c2")
        assert len(prereqs) == 1
        assert prereqs[0].name == "Basics"

    def test_get_dependents(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="c1", name="Basics"))
        kg.add_concept(Concept(id="c2", name="Advanced"))
        kg.add_relation(Relation("c1", "c2", RelationType.PREREQUISITE))
        dependents = kg.get_dependents("c1")
        assert len(dependents) == 1
        assert dependents[0].name == "Advanced"

    def test_find_path(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="c1", name="A"))
        kg.add_concept(Concept(id="c2", name="B"))
        kg.add_concept(Concept(id="c3", name="C"))
        kg.add_relation(Relation("c1", "c2", RelationType.PREREQUISITE))
        kg.add_relation(Relation("c2", "c3", RelationType.PREREQUISITE))
        path = kg.find_path("c1", "c3")
        assert path is not None
        assert path == ["c1", "c2", "c3"]

    def test_find_path_no_path(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="c1", name="A"))
        kg.add_concept(Concept(id="c2", name="B"))
        path = kg.find_path("c1", "c2")
        assert path is None

    def test_topological_sort(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="c1", name="A"))
        kg.add_concept(Concept(id="c2", name="B"))
        kg.add_concept(Concept(id="c3", name="C"))
        kg.add_relation(Relation("c1", "c2", RelationType.PREREQUISITE))
        kg.add_relation(Relation("c2", "c3", RelationType.PREREQUISITE))
        sorted_ids = kg.topological_sort()
        assert sorted_ids.index("c1") < sorted_ids.index("c2")
        assert sorted_ids.index("c2") < sorted_ids.index("c3")

    def test_search(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="c1", name="Python Basics", difficulty=ConceptDifficulty.BEGINNER))
        kg.add_concept(Concept(id="c2", name="Java Advanced", difficulty=ConceptDifficulty.ADVANCED))
        results = kg.search("python")
        assert len(results) == 1
        assert results[0].name == "Python Basics"

    def test_search_by_difficulty(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="c1", name="Basics", difficulty=ConceptDifficulty.BEGINNER))
        kg.add_concept(Concept(id="c2", name="Advanced", difficulty=ConceptDifficulty.ADVANCED))
        results = kg.search("", difficulty=ConceptDifficulty.ADVANCED)
        assert len(results) == 1

    def test_get_related_concepts(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="c1", name="A"))
        kg.add_concept(Concept(id="c2", name="B"))
        kg.add_relation(Relation("c1", "c2", RelationType.RELATEDTO))
        related = kg.get_related_concepts("c1")
        assert len(related) == 1

    def test_get_statistics(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="c1", name="A", difficulty=ConceptDifficulty.BEGINNER))
        kg.add_concept(Concept(id="c2", name="B", difficulty=ConceptDifficulty.ADVANCED))
        kg.add_relation(Relation("c1", "c2", RelationType.PREREQUISITE))
        stats = kg.get_statistics()
        assert stats["total_concepts"] == 2
        assert stats["total_relations"] == 1
