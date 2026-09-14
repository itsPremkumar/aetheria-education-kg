"""Tests for Learning Commons KG — concept mapping and discovery."""

import pytest

from education_kg.graph import KnowledgeGraph
from education_kg.models import Concept, ConceptDifficulty, Relation, RelationType
from education_kg.entity_extractor import EntityExtractor
from education_kg.relation_extractor import RelationExtractor


class TestLearningCommonsKG:
    """Test Learning Commons KG concept mapping and discovery."""

    def test_create_learning_commons_graph(self):
        kg = KnowledgeGraph()
        assert kg is not None
        assert len(kg) == 0

    def test_add_learning_commons_concepts(self):
        kg = KnowledgeGraph()
        concepts = [
            Concept(id="lc1", name="Information Literacy", description="Ability to find and evaluate information",
                    difficulty=ConceptDifficulty.BEGINNER, subject="library"),
            Concept(id="lc2", name="Research Skills", description="Conducting academic research",
                    difficulty=ConceptDifficulty.INTERMEDIATE, subject="library"),
            Concept(id="lc3", name="Digital Citizenship", description="Responsible use of technology",
                    difficulty=ConceptDifficulty.BEGINNER, subject="technology"),
        ]
        for c in concepts:
            kg.add_concept(c)
        assert len(kg) == 3

    def test_learning_commons_prerequisites(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="lc1", name="Basic Research", difficulty=ConceptDifficulty.BEGINNER))
        kg.add_concept(Concept(id="lc2", name="Advanced Research", difficulty=ConceptDifficulty.ADVANCED))
        kg.add_relation(Relation("lc1", "lc2", RelationType.PREREQUISITE))
        prereqs = kg.get_prerequisites("lc2")
        assert len(prereqs) == 1
        assert prereqs[0].name == "Basic Research"

    def test_learning_commons_search(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="lc1", name="Information Literacy", description="Finding information",
                               difficulty=ConceptDifficulty.BEGINNER, subject="library"))
        kg.add_concept(Concept(id="lc2", name="Data Science", description="Analyzing data",
                               difficulty=ConceptDifficulty.ADVANCED, subject="technology"))
        results = kg.search("information")
        assert len(results) >= 1

    def test_learning_commons_statistics(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="lc1", name="Concept A", difficulty=ConceptDifficulty.BEGINNER))
        kg.add_concept(Concept(id="lc2", name="Concept B", difficulty=ConceptDifficulty.INTERMEDIATE))
        kg.add_concept(Concept(id="lc3", name="Concept C", difficulty=ConceptDifficulty.ADVANCED))
        stats = kg.get_statistics()
        assert stats["total_concepts"] == 3
        assert stats["difficulty_counts"]["beginner"] == 1
        assert stats["difficulty_counts"]["intermediate"] == 1
        assert stats["difficulty_counts"]["advanced"] == 1

    def test_learning_commons_topological_sort(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="lc1", name="Foundations", difficulty=ConceptDifficulty.BEGINNER))
        kg.add_concept(Concept(id="lc2", name="Intermediate", difficulty=ConceptDifficulty.INTERMEDIATE))
        kg.add_concept(Concept(id="lc3", name="Advanced", difficulty=ConceptDifficulty.ADVANCED))
        kg.add_relation(Relation("lc1", "lc2", RelationType.PREREQUISITE))
        kg.add_relation(Relation("lc2", "lc3", RelationType.PREREQUISITE))
        sorted_ids = kg.topological_sort()
        assert sorted_ids.index("lc1") < sorted_ids.index("lc2")
        assert sorted_ids.index("lc2") < sorted_ids.index("lc3")

    def test_learning_commons_entity_extraction(self):
        extractor = EntityExtractor()
        text = "Information Literacy and Digital Citizenship are core competencies"
        result = extractor.extract(text, "library")
        assert len(result.concepts) >= 1
        assert result.confidence > 0

    def test_learning_commons_relation_extraction(self):
        extractor = RelationExtractor()
        c1 = Concept(id="lc1", name="Basic Research", tags=["library"])
        result = extractor.extract_relations(c1, "lc2", "Basic Research is a prerequisite for Advanced Research")
        assert len(result.relations) >= 1

    def test_learning_commons_path_finding(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="lc1", name="Start"))
        kg.add_concept(Concept(id="lc2", name="Middle"))
        kg.add_concept(Concept(id="lc3", name="End"))
        kg.add_relation(Relation("lc1", "lc2", RelationType.PREREQUISITE))
        kg.add_relation(Relation("lc2", "lc3", RelationType.PREREQUISITE))
        path = kg.find_path("lc1", "lc3")
        assert path is not None
        assert path == ["lc1", "lc2", "lc3"]

    def test_learning_commons_related_concepts(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="lc1", name="Research"))
        kg.add_concept(Concept(id="lc2", name="Writing"))
        kg.add_concept(Concept(id="lc3", name="Math"))
        kg.add_relation(Relation("lc1", "lc2", RelationType.RELATEDTO))
        related = kg.get_related_concepts("lc1")
        assert len(related) == 1
        assert related[0].name == "Writing"
