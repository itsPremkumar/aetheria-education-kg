"""Tests for the seed curriculum dataset."""

import pytest

from education_kg.graph import KnowledgeGraph
from education_kg.models import (
    Concept,
    ConceptDifficulty,
    Relation,
    RelationType,
)
from education_kg.seed_data import (
    SEED_CONCEPT_COUNT,
    SEED_RELATION_COUNT,
    SEED_RESOURCE_COUNT,
    build_curriculum_graph,
)


class TestSeedDatasetIntegrity:
    def test_build_returns_graph(self):
        graph = build_curriculum_graph()
        assert isinstance(graph, KnowledgeGraph)

    def test_concept_counts_match(self):
        graph = build_curriculum_graph()
        assert len(graph) == SEED_CONCEPT_COUNT
        assert SEED_CONCEPT_COUNT == 20

    def test_relation_counts_match(self):
        graph = build_curriculum_graph()
        stats = graph.get_statistics()
        assert stats["total_relations"] == SEED_RELATION_COUNT
        assert SEED_RELATION_COUNT == 32

    def test_resource_counts_match(self):
        graph = build_curriculum_graph()
        assert len(graph.get_all_resources()) == SEED_RESOURCE_COUNT
        assert SEED_RESOURCE_COUNT == 15

    def test_all_concepts_retrievable(self):
        graph = build_curriculum_graph()
        for concept in graph.get_all_concepts():
            fetched = graph.get_concept(concept.id)
            assert fetched is not None
            assert fetched.name == concept.name

    def test_concepts_have_subjects_and_tags(self):
        graph = build_curriculum_graph()
        for concept in graph.get_all_concepts():
            assert concept.subject, f"{concept.id} missing subject"
            assert concept.tags, f"{concept.id} missing tags"
            assert concept.description, f"{concept.id} missing description"

    def test_covers_expected_subjects(self):
        graph = build_curriculum_graph()
        stats = graph.get_statistics()
        assert "mathematics" in stats["subjects"]
        assert "programming" in stats["subjects"]
        assert "systems" in stats["subjects"]
        assert "artificial-intelligence" in stats["subjects"]

    def test_all_difficulties_represented(self):
        graph = build_curriculum_graph()
        stats = graph.get_statistics()
        assert stats["difficulty_counts"]["beginner"] > 0
        assert stats["difficulty_counts"]["intermediate"] > 0
        assert stats["difficulty_counts"]["advanced"] > 0

    def test_no_duplicate_concept_ids(self):
        graph = build_curriculum_graph()
        ids = [c.id for c in graph.get_all_concepts()]
        assert len(ids) == len(set(ids))

    def test_no_self_loops(self):
        graph = build_curriculum_graph()
        for concept in graph.get_all_concepts():
            for rel in graph.get_relations(concept.id):
                assert rel.source_id != rel.target_id


class TestSeedGraphLearningPaths:
    def test_prerequisite_chain_math_to_ai(self):
        graph = build_curriculum_graph()
        path = graph.find_path("math.logic", "ai.dl")
        assert path is not None
        assert path[0] == "math.logic"
        assert path[-1] == "ai.dl"
        # Prerequisite relations must form a viable study order
        for prev, nxt in zip(path, path[1:]):
            rels = [r for r in graph.get_relations(prev)
                    if r.relation_type == RelationType.PREREQUISITE]
            assert any(r.target_id == nxt for r in rels), \
                f"{prev} -> {nxt} is not a prerequisite edge"

    def test_path_basics_to_dsa(self):
        graph = build_curriculum_graph()
        path = graph.find_path("prog.basics", "prog.dsa")
        assert path is not None
        assert path[0] == "prog.basics"
        assert path[-1] == "prog.dsa"
        # every hop must be a prerequisite edge
        for prev, nxt in zip(path, path[1:]):
            rels = [r for r in graph.get_relations(prev)
                    if r.relation_type == RelationType.PREREQUISITE]
            assert any(r.target_id == nxt for r in rels)

    def test_topological_order_valid(self):
        graph = build_curriculum_graph()
        order = graph.topological_sort()
        assert len(order) == len(graph)
        position = {cid: i for i, cid in enumerate(order)}
        for concept in graph.get_all_concepts():
            for rel in graph.get_relations(concept.id):
                if rel.relation_type == RelationType.PREREQUISITE:
                    assert position[rel.source_id] < position[rel.target_id], \
                        f"topo order violates {rel.source_id} -> {rel.target_id}"

    def test_no_cycles_in_seed(self):
        graph = build_curriculum_graph()
        assert not graph.has_prerequisite_cycle()
        assert graph.find_prerequisite_cycles() == []

    def test_learning_path_generation_end_to_end(self):
        from education_kg.learning_path import LearningPathGenerator
        graph = build_curriculum_graph()
        gen = LearningPathGenerator(graph)
        lp = gen.generate("math.logic", "ai.nlp")
        assert len(lp.concepts) > 0
        assert lp.estimated_hours > 0


class TestSeedResources:
    def test_every_resource_attached_to_existing_concepts(self):
        graph = build_curriculum_graph()
        for resource in graph.get_all_resources():
            assert resource.concepts, f"{resource.id} attached to nothing"
            for cid in resource.concepts:
                assert cid in graph, \
                    f"{resource.id} references missing concept {cid}"

    def test_get_resources_for_concept(self):
        graph = build_curriculum_graph()
        resources = graph.get_resources_for_concept("ai.dl")
        assert len(resources) >= 1
        titles = [r.title for r in resources]
        assert any("Neural networks" in t for t in titles)

    def test_multi_concept_resource(self):
        graph = build_curriculum_graph()
        resources = graph.get_resources_for_concept("math.probability")
        # the probability course covers combinatorics too
        shared = [r for r in resources if "math.combinatorics" in r.concepts]
        assert len(shared) >= 1

    def test_resource_types_diverse(self):
        graph = build_curriculum_graph()
        types = {r.resource_type for r in graph.get_all_resources()}
        assert len(types) >= 5
