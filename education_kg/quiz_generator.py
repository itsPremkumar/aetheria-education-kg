"""Quiz generation from knowledge graph."""

from __future__ import annotations

import random
import uuid
from dataclasses import dataclass, field
from typing import Any

from education_kg.graph import KnowledgeGraph
from education_kg.models import (
    Concept,
    ConceptDifficulty,
    Quiz,
    QuizQuestion,
    RelationType,
)


class QuizGenerator:
    """Auto-generate quizzes from knowledge graph."""

    def __init__(self, graph: KnowledgeGraph):
        self._graph = graph

    def generate(
        self,
        concept_ids: list[str],
        num_questions: int = 5,
        difficulty: ConceptDifficulty = ConceptDifficulty.BEGINNER,
    ) -> Quiz:
        """Generate a quiz for given concepts."""
        questions = []
        concepts = [
            self._graph.get_concept(cid)
            for cid in concept_ids
            if self._graph.get_concept(cid)
        ]

        if not concepts:
            return Quiz(
                id=str(uuid.uuid4()),
                title="Empty Quiz",
                questions=[],
                difficulty=difficulty,
            )

        for concept in concepts:
            if len(questions) >= num_questions:
                break

            # Generate questions from concept
            concept_questions = self._generate_questions_for_concept(
                concept, difficulty, num_questions - len(questions)
            )
            questions.extend(concept_questions)

        return Quiz(
            id=str(uuid.uuid4()),
            title=f"Quiz: {concepts[0].name if concepts else 'Mixed'}",
            questions=questions[:num_questions],
            difficulty=difficulty,
            subject=concepts[0].subject if concepts else "",
        )

    def generate_from_path(self, learning_path: list[str], num_questions: int = 10) -> Quiz:
        """Generate quiz from a learning path."""
        concepts = [
            self._graph.get_concept(cid)
            for cid in learning_path
            if self._graph.get_concept(cid)
        ]

        questions = []
        for concept in concepts:
            related = self._graph.get_related_concepts(concept.id)
            for related_concept in related[:2]:
                if len(questions) >= num_questions:
                    break

                q = self._create_relation_question(concept, related_concept)
                if q:
                    questions.append(q)

        return Quiz(
            id=str(uuid.uuid4()),
            title=f"Path Quiz ({len(learning_path)} concepts)",
            questions=questions[:num_questions],
        )

    def _generate_questions_for_concept(
        self,
        concept: Concept,
        difficulty: ConceptDifficulty,
        max_questions: int,
    ) -> list[QuizQuestion]:
        """Generate questions for a concept."""
        questions = []
        related = self._graph.get_related_concepts(concept.id)
        prereqs = self._graph.get_prerequisites(concept.id)

        # Question: What is this concept?
        if concept.description:
            wrong_answers = [r.name for r in related[:3]] if related else ["None of the above"]
            options = [concept.description[:50]] + wrong_answers[:3]
            random.shuffle(options)

            questions.append(QuizQuestion(
                question=f"What best describes '{concept.name}'?",
                options=options[:4],
                correct_answer=options.index(concept.description[:50]) if concept.description[:50] in options else 0,
                explanation=f"{concept.name}: {concept.description[:100]}",
                concept_id=concept.id,
            ))

        # Question: What are the prerequisites?
        if prereqs and len(questions) < max_questions:
            prereq_names = [p.name for p in prereqs[:3]]
            wrong = [r.name for r in related[:2]] if related else ["None"]
            options = prereq_names + wrong
            random.shuffle(options)

            questions.append(QuizQuestion(
                question=f"What are the prerequisites for '{concept.name}'?",
                options=options[:4],
                correct_answer=0,
                explanation=f"Prerequisites include: {', '.join(p.name for p in prereqs)}",
                concept_id=concept.id,
            ))

        return questions

    def _create_relation_question(
        self,
        concept1: Concept,
        concept2: Concept,
    ) -> QuizQuestion | None:
        """Create a question about the relationship between concepts."""
        relations = self._graph.get_relations(concept1.id)
        matching_rels = [r for r in relations if r.target_id == concept2.id]

        if not matching_rels:
            return None

        rel = matching_rels[0]
        return QuizQuestion(
            question=f"What is the relationship between '{concept1.name}' and '{concept2.name}'?",
            options=["Prerequisite", "Builds On", "Related To", "Unrelated"],
            correct_answer=["prerequisite", "builds_on", "related_to", "unrelated"].index(
                rel.relation_type.value
            ),
            explanation=f"{concept1.name} → {concept2.name}: {rel.relation_type.value}",
            concept_id=concept1.id,
        )
