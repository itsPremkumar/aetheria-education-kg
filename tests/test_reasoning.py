"""Tests for Reasoning Engine."""

import pytest

from education_kg.graph import KnowledgeGraph
from education_kg.models import Concept, ConceptDifficulty, Relation, RelationType
from education_kg.reasoning import ReasoningEngine, ReasoningResult


class TestReasoningEngine:
    def test_create(self):
        kg = KnowledgeGraph()
        engine = ReasoningEngine(kg)
        assert engine is not None

    def test_answer_with_concept_id(self):
        kg = KnowledgeGraph()
        concept = Concept(id="c1", name="Python", description="A programming language")
        kg.add_concept(concept)
        engine = ReasoningEngine(kg)
        result = engine.answer("What is Python?", "c1")
        assert isinstance(result, ReasoningResult)
        assert result.confidence >= 0.9
        assert "Python" in result.answer

    def test_answer_search(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="c1", name="Python", description="Programming language"))
        engine = ReasoningEngine(kg)
        result = engine.answer("Tell me about Python")
        assert result.confidence > 0

    def test_answer_no_results(self):
        kg = KnowledgeGraph()
        engine = ReasoningEngine(kg)
        result = engine.answer("nonexistent topic")
        assert result.confidence == 0.0

    def test_explain(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="c1", name="Basics"))
        kg.add_concept(Concept(id="c2", name="Advanced"))
        kg.add_relation(Relation("c1", "c2", RelationType.PREREQUISITE))
        engine = ReasoningEngine(kg)
        result = engine.explain("c1", "c2")
        assert "Basics" in result.answer
        assert "Advanced" in result.answer

    def test_explain_no_path(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="c1", name="A"))
        kg.add_concept(Concept(id="c2", name="B"))
        engine = ReasoningEngine(kg)
        result = engine.explain("c1", "c2")
        assert result.confidence == 0.0


class TestReasoningResult:
    def test_create(self):
        result = ReasoningResult("answer", 0.8, ["path"], ["evidence"], "query")
        assert result.answer == "answer"
        assert result.confidence == 0.8
