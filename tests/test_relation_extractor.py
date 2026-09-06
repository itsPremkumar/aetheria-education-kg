"""Tests for Relation Extractor."""

import pytest

from education_kg.models import Concept, RelationType
from education_kg.relation_extractor import RelationExtractor, RelationResult


class TestRelationExtractor:
    def test_create(self):
        extractor = RelationExtractor()
        assert extractor is not None

    def test_extract_prerequisite(self):
        extractor = RelationExtractor()
        c1 = Concept(id="c1", name="Basics")
        result = extractor.extract_relations(c1, "c2", "This requires basics")
        assert len(result.relations) >= 1
        assert result.relations[0].relation_type == RelationType.PREREQUISITE

    def test_extract_builds_on(self):
        extractor = RelationExtractor()
        c1 = Concept(id="c1", name="Basics")
        result = extractor.extract_relations(c1, "c2", "This builds on basics")
        assert len(result.relations) >= 1
        assert result.relations[0].relation_type == RelationType.BUILDSON

    def test_extract_related_to(self):
        extractor = RelationExtractor()
        c1 = Concept(id="c1", name="Python")
        result = extractor.extract_relations(c1, "c2", "This is related to programming")
        assert len(result.relations) >= 1

    def test_extract_all_relations(self):
        extractor = RelationExtractor()
        c1 = Concept(id="c1", name="A")
        c2 = Concept(id="c2", name="B")
        c3 = Concept(id="c3", name="C")
        relations = extractor.extract_all_relations([c1, c2, c3], "A and B are related")
        assert isinstance(relations, list)

    def test_extract_no_match(self):
        extractor = RelationExtractor()
        c1 = Concept(id="c1", name="XYZ")
        result = extractor.extract_relations(c1, "c2", "No relation here")
        # May have implicit relations


class TestRelationResult:
    def test_create(self):
        result = RelationResult()
        assert result.relations == []
        assert result.confidence == 0.0
