"""Tests for Entity Extractor."""

import pytest

from education_kg.entity_extractor import EntityExtractor, ExtractionResult
from education_kg.models import ConceptDifficulty


class TestEntityExtractor:
    def test_create(self):
        extractor = EntityExtractor()
        assert extractor is not None

    def test_extract_simple(self):
        extractor = EntityExtractor()
        result = extractor.extract("Python is a programming language", "programming")
        assert isinstance(result, ExtractionResult)
        assert result.confidence >= 0

    def test_extract_with_capitalized_phrases(self):
        extractor = EntityExtractor()
        result = extractor.extract("Machine Learning and Artificial Intelligence")
        assert len(result.concepts) >= 2

    def test_extract_difficulty_beginner(self):
        extractor = EntityExtractor()
        result = extractor.extract("Basic introduction to Python programming")
        for concept in result.concepts:
            assert concept.difficulty == ConceptDifficulty.BEGINNER

    def test_extract_empty_text(self):
        extractor = EntityExtractor()
        result = extractor.extract("")
        assert len(result.concepts) == 0
        assert result.confidence == 0.0

    def test_extract_with_tags(self):
        extractor = EntityExtractor()
        result = extractor.extract("Python programming with algorithms and code")
        for concept in result.concepts:
            assert "programming" in concept.tags


class TestExtractionResult:
    def test_create(self):
        result = ExtractionResult()
        assert result.concepts == []
        assert result.confidence == 0.0
