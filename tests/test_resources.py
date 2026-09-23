"""Tests for Resource model and graph resource registry."""

import pytest

from education_kg.graph import KnowledgeGraph
from education_kg.models import (
    Concept,
    Relation,
    RelationType,
    Resource,
    ResourceType,
)


def _make_resource(rid="r1", concepts=None, rtype=ResourceType.VIDEO, **kwargs):
    return Resource(
        id=rid,
        title=kwargs.get("title", "Intro Video"),
        url=kwargs.get("url", "https://example.com"),
        resource_type=rtype,
        concepts=concepts if concepts is not None else ["c1"],
        estimated_minutes=kwargs.get("estimated_minutes", 30.0),
    )


class TestResourceModel:
    def test_create_defaults(self):
        resource = Resource(id="r1", title="Lecture 1")
        assert resource.resource_type == ResourceType.ARTICLE
        assert resource.concepts == []
        assert resource.estimated_minutes == 0.0
        assert resource.url == ""

    def test_create_full(self):
        resource = _make_resource(
            concepts=["c1", "c2"],
            rtype=ResourceType.EXERCISE,
            estimated_minutes=90.0,
        )
        assert resource.resource_type == ResourceType.EXERCISE
        assert resource.concepts == ["c1", "c2"]
        assert resource.estimated_minutes == 90.0

    def test_to_dict(self):
        resource = _make_resource()
        data = resource.to_dict()
        assert data["id"] == "r1"
        assert data["resource_type"] == "video"
        assert data["concepts"] == ["c1"]
        assert data["estimated_minutes"] == 30.0
        assert data["url"] == "https://example.com"

    def test_all_resource_types_have_values(self):
        expected = {"video", "article", "book", "exercise", "course", "interactive"}
        assert {rt.value for rt in ResourceType} == expected


class TestGraphResourceRegistry:
    def _graph(self):
        graph = KnowledgeGraph()
        graph.add_concept(Concept(id="c1", name="Graphs"))
        graph.add_concept(Concept(id="c2", name="Trees"))
        return graph

    def test_add_and_get_resource(self):
        graph = self._graph()
        resource = _make_resource()
        graph.add_resource(resource)
        assert graph.get_resource("r1") is resource
        assert graph.get_resource("missing") is None

    def test_get_all_resources(self):
        graph = self._graph()
        graph.add_resource(_make_resource("r1"))
        graph.add_resource(_make_resource("r2", concepts=["c2"]))
        assert len(graph.get_all_resources()) == 2

    def test_get_resources_for_concept_filters(self):
        graph = self._graph()
        graph.add_resource(_make_resource("r1", concepts=["c1"]))
        graph.add_resource(_make_resource("r2", concepts=["c2"]))
        graph.add_resource(_make_resource("r3", concepts=["c1", "c2"]))
        for_c1 = graph.get_resources_for_concept("c1")
        ids = {r.id for r in for_c1}
        assert ids == {"r1", "r3"}

    def test_concept_with_no_resources_returns_empty(self):
        graph = self._graph()
        assert graph.get_resources_for_concept("c1") == []

    def test_resource_replaces_same_id(self):
        graph = self._graph()
        graph.add_resource(_make_resource("r1", concepts=["c1"]))
        graph.add_resource(_make_resource("r1", concepts=["c2"],
                                          title="Replacement"))
        assert len(graph.get_all_resources()) == 1
        assert graph.get_resource("r1").title == "Replacement"

    def test_resources_survive_concept_lookup_pattern(self):
        graph = self._graph()
        graph.add_resource(_make_resource())
        # resource referencing a not-yet-added concept is still stored
        assert graph.get_resources_for_concept("c1") != []
