"""Tests for prerequisite-cycle detection and robust topological sort."""

import pytest

from education_kg.graph import KnowledgeGraph
from education_kg.models import (
    Concept,
    ConceptDifficulty,
    Relation,
    RelationType,
)


def _graph_with(relation_specs: list[tuple[str, str, RelationType]]) -> KnowledgeGraph:
    """Build a graph with concepts a..e and the given relations."""
    graph = KnowledgeGraph()
    for cid in ["a", "b", "c", "d", "e"]:
        graph.add_concept(Concept(id=cid, name=cid.upper()))
    for source, target, rel_type in relation_specs:
        graph.add_relation(Relation(source, target, rel_type))
    return graph


class TestCycleDetection:
    def test_acyclic_graph_has_no_cycle(self):
        graph = _graph_with([("a", "b", RelationType.PREREQUISITE),
                             ("b", "c", RelationType.PREREQUISITE)])
        assert graph.has_prerequisite_cycle() is False

    def test_simple_two_node_cycle_detected(self):
        graph = _graph_with([("a", "b", RelationType.PREREQUISITE),
                             ("b", "a", RelationType.PREREQUISITE)])
        assert graph.has_prerequisite_cycle() is True

    def test_three_node_cycle_detected(self):
        graph = _graph_with([("a", "b", RelationType.PREREQUISITE),
                             ("b", "c", RelationType.PREREQUISITE),
                             ("c", "a", RelationType.PREREQUISITE)])
        assert graph.has_prerequisite_cycle() is True

    def test_self_loop_detected(self):
        graph = _graph_with([("a", "a", RelationType.PREREQUISITE)])
        assert graph.has_prerequisite_cycle() is True

    def test_cycles_in_other_relation_types_ignored(self):
        # A related_to cycle is not a prerequisite cycle
        graph = _graph_with([("a", "b", RelationType.RELATEDTO),
                             ("b", "a", RelationType.RELATEDTO)])
        assert graph.has_prerequisite_cycle() is False

    def test_empty_graph_has_no_cycle(self):
        assert KnowledgeGraph().has_prerequisite_cycle() is False

    def test_find_cycles_returns_empty_for_dag(self):
        graph = _graph_with([("a", "b", RelationType.PREREQUISITE),
                             ("b", "c", RelationType.PREREQUISITE),
                             ("a", "c", RelationType.PREREQUISITE)])
        assert graph.find_prerequisite_cycles() == []

    def test_find_cycles_returns_cycle_members(self):
        graph = _graph_with([("a", "b", RelationType.PREREQUISITE),
                             ("b", "c", RelationType.PREREQUISITE),
                             ("c", "a", RelationType.PREREQUISITE)])
        cycles = graph.find_prerequisite_cycles()
        assert len(cycles) == 1
        assert sorted(cycles[0]) == ["a", "b", "c"]

    def test_find_cycles_two_disjoint_cycles(self):
        graph = _graph_with([
            ("a", "b", RelationType.PREREQUISITE),
            ("b", "a", RelationType.PREREQUISITE),
            ("c", "d", RelationType.PREREQUISITE),
            ("d", "c", RelationType.PREREQUISITE),
        ])
        cycles = graph.find_prerequisite_cycles()
        assert len(cycles) == 2
        all_members = sorted(m for cyc in cycles for m in cyc)
        assert all_members == ["a", "b", "c", "d"]

    def test_find_cycles_ignores_non_concept_targets(self):
        # relation pointing at a concept id that was never added
        graph = KnowledgeGraph()
        graph.add_concept(Concept(id="a", name="A"))
        graph.add_relation(Relation("a", "ghost", RelationType.PREREQUISITE))
        assert graph.find_prerequisite_cycles() == []


class TestTopologicalSortRobustness:
    def test_dag_sorts_all_nodes(self):
        graph = _graph_with([("a", "b", RelationType.PREREQUISITE),
                             ("b", "c", RelationType.PREREQUISITE)])
        order = graph.topological_sort()
        assert len(order) == 5
        assert order.index("a") < order.index("b") < order.index("c")

    def test_cyclic_nodes_omitted_not_hanging(self):
        graph = _graph_with([("a", "b", RelationType.PREREQUISITE),
                             ("b", "a", RelationType.PREREQUISITE),
                             ("c", "d", RelationType.PREREQUISITE)])
        order = graph.topological_sort()
        # acyclic portion (c->d, plus isolated e) still sorts
        assert "c" in order and "d" in order and "e" in order
        assert order.index("c") < order.index("d")
        # cyclic nodes are dropped, not deadlocked
        assert "a" not in order and "b" not in order

    def test_only_prerequisites_affect_order(self):
        graph = _graph_with([("a", "b", RelationType.RELATEDTO)])
        # related_to must NOT constrain ordering
        order = graph.topological_sort()
        assert len(order) == 5

    def test_empty_graph_sorts_empty(self):
        assert KnowledgeGraph().topological_sort() == []


class TestNewRelationTypes:
    def test_same_as_value(self):
        assert RelationType.SAMEAS.value == "same_as"

    def test_example_of_value(self):
        assert RelationType.EXAMPLEOF.value == "example_of"

    def test_assessed_by_value(self):
        assert RelationType.ASSESSEDBY.value == "assessed_by"

    def test_new_types_usable_in_graph(self):
        graph = KnowledgeGraph()
        graph.add_concept(Concept(id="c1", name="Quadratic Equations"))
        graph.add_concept(Concept(id="c2", name="Completing The Square"))
        graph.add_relation(Relation("c2", "c1", RelationType.EXAMPLEOF))
        graph.add_relation(Relation("quiz1", "c1", RelationType.ASSESSEDBY))
        assert graph.get_related_concepts("c1") != []

    def test_new_types_do_not_affect_prerequisites(self):
        graph = KnowledgeGraph()
        graph.add_concept(Concept(id="c1", name="A"))
        graph.add_concept(Concept(id="c2", name="B"))
        graph.add_relation(Relation("c1", "c2", RelationType.SAMEAS))
        assert graph.get_prerequisites("c2") == []
        assert graph.get_dependents("c1") == []
