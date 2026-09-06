"""Pipeline orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from education_kg.entity_extractor import EntityExtractor, ExtractionResult
from education_kg.graph import KnowledgeGraph
from education_kg.learning_path import LearningPathGenerator
from education_kg.models import Concept, LearningPath, Quiz, Relation
from education_kg.multilang import MultiLanguageSupport
from education_kg.quiz_generator import QuizGenerator
from education_kg.reasoning import ReasoningEngine, ReasoningResult
from education_kg.relation_extractor import RelationExtractor
from education_kg.storage import GraphStorage


@dataclass
class PipelineResult:
    concepts_extracted: int = 0
    relations_found: int = 0
    learning_paths_generated: int = 0
    quizzes_generated: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class Pipeline:
    """Orchestrate the full education KG pipeline."""

    def __init__(self, db_path: str = "education_kg.db"):
        self._storage = GraphStorage(db_path)
        self._graph = KnowledgeGraph()
        self._entity_extractor = EntityExtractor()
        self._relation_extractor = RelationExtractor()
        self._reasoning = ReasoningEngine(self._graph)
        self._path_generator = LearningPathGenerator(self._graph)
        self._quiz_generator = QuizGenerator(self._graph)
        self._multilang = MultiLanguageSupport()

    def initialize(self) -> None:
        """Initialize the pipeline."""
        self._storage.connect()
        concepts = self._storage.load_concepts()
        for concept in concepts:
            self._graph.add_concept(concept)

    def shutdown(self) -> None:
        """Shutdown the pipeline."""
        self._storage.close()

    def process_text(self, text: str, subject: str = "") -> PipelineResult:
        """Process text and extract knowledge."""
        result = PipelineResult()

        # Extract entities
        extraction = self._entity_extractor.extract(text, subject)
        result.concepts_extracted = len(extraction.concepts)

        # Add concepts to graph
        for concept in extraction.concepts:
            self._graph.add_concept(concept)
            self._storage.save_concept(concept)

        # Extract relations
        relations = self._relation_extractor.extract_all_relations(
            extraction.concepts, text
        )
        result.relations_found = len(relations)

        for relation in relations:
            self._graph.add_relation(relation)
            self._storage.save_relation(relation)

        return result

    def generate_learning_path(
        self,
        start: str,
        goal: str,
    ) -> LearningPath | None:
        """Generate a learning path."""
        return self._path_generator.generate(start, goal)

    def generate_quiz(self, concept_ids: list[str], num_questions: int = 5) -> Quiz:
        """Generate a quiz."""
        return self._quiz_generator.generate(concept_ids, num_questions)

    def answer_question(self, query: str, concept_id: str = "") -> ReasoningResult:
        """Answer a question."""
        return self._reasoning.answer(query, concept_id)

    def get_graph(self) -> KnowledgeGraph:
        """Get the knowledge graph."""
        return self._graph

    def get_storage(self) -> GraphStorage:
        """Get the storage."""
        return self._storage

    def get_multilang(self) -> MultiLanguageSupport:
        """Get the multi-language support."""
        return self._multilang
