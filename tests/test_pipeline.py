"""Tests for Pipeline orchestration."""

import pytest

from education_kg.models import Concept, ConceptDifficulty, Relation, RelationType
from education_kg.pipeline import Pipeline, PipelineResult


class TestPipeline:
    def test_create(self):
        pipeline = Pipeline(":memory:")
        assert pipeline is not None

    def test_initialize_shutdown(self):
        pipeline = Pipeline(":memory:")
        pipeline.initialize()
        pipeline.shutdown()

    def test_process_text(self):
        pipeline = Pipeline(":memory:")
        pipeline.initialize()
        result = pipeline.process_text("Python is a programming language", "programming")
        assert isinstance(result, PipelineResult)
        assert result.concepts_extracted >= 0
        assert result.relations_found >= 0
        pipeline.shutdown()

    def test_process_text_empty(self):
        pipeline = Pipeline(":memory:")
        pipeline.initialize()
        result = pipeline.process_text("", "")
        assert result.concepts_extracted == 0
        pipeline.shutdown()

    def test_generate_learning_path(self):
        pipeline = Pipeline(":memory:")
        pipeline.initialize()
        graph = pipeline.get_graph()
        graph.add_concept(Concept(id="c1", name="Basics"))
        graph.add_concept(Concept(id="c2", name="Advanced"))
        graph.add_relation(Relation("c1", "c2", RelationType.PREREQUISITE))
        path = pipeline.generate_learning_path("c1", "c2")
        assert path is not None
        pipeline.shutdown()

    def test_generate_quiz(self):
        pipeline = Pipeline(":memory:")
        pipeline.initialize()
        graph = pipeline.get_graph()
        graph.add_concept(Concept(id="c1", name="Python", description="A language"))
        quiz = pipeline.generate_quiz(["c1"], num_questions=3)
        assert quiz is not None
        pipeline.shutdown()

    def test_answer_question(self):
        pipeline = Pipeline(":memory:")
        pipeline.initialize()
        graph = pipeline.get_graph()
        graph.add_concept(Concept(id="c1", name="Python", description="A programming language"))
        result = pipeline.answer_question("What is Python?", "c1")
        assert result is not None
        assert result.confidence > 0
        pipeline.shutdown()

    def test_get_graph(self):
        pipeline = Pipeline(":memory:")
        graph = pipeline.get_graph()
        assert graph is not None

    def test_get_storage(self):
        pipeline = Pipeline(":memory:")
        storage = pipeline.get_storage()
        assert storage is not None

    def test_get_multilang(self):
        pipeline = Pipeline(":memory:")
        multilang = pipeline.get_multilang()
        assert multilang is not None


class TestPipelineResult:
    def test_create(self):
        result = PipelineResult()
        assert result.concepts_extracted == 0
        assert result.relations_found == 0
        assert result.learning_paths_generated == 0
        assert result.quizzes_generated == 0
        assert result.errors == []
        assert result.warnings == []

    def test_create_with_values(self):
        result = PipelineResult(
            concepts_extracted=5,
            relations_found=3,
            errors=["error1"],
            warnings=["warning1"],
        )
        assert result.concepts_extracted == 5
        assert result.relations_found == 3
        assert "error1" in result.errors
        assert "warning1" in result.warnings
