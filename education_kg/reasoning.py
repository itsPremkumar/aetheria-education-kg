"""Reasoning engine using graph traversal."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from education_kg.graph import KnowledgeGraph
from education_kg.models import Concept, RelationType


@dataclass
class ReasoningResult:
    answer: str
    confidence: float
    reasoning_path: list[str]
    supporting_evidence: list[str]
    query: str


class ReasoningEngine:
    """Answer questions using knowledge graph traversal."""

    def __init__(self, graph: KnowledgeGraph):
        self._graph = graph

    def answer(self, query: str, concept_id: str = "") -> ReasoningResult:
        """Answer a query using graph traversal."""
        query_lower = query.lower()

        # Direct concept lookup
        if concept_id:
            concept = self._graph.get_concept(concept_id)
            if concept:
                return ReasoningResult(
                    answer=f"Concept '{concept.name}': {concept.description}",
                    confidence=0.9,
                    reasoning_path=[concept.name],
                    supporting_evidence=[concept.description],
                    query=query,
                )

        # Search for relevant concepts
        concepts = self._graph.search(query, limit=5)
        if not concepts:
            return ReasoningResult(
                answer="No relevant concepts found",
                confidence=0.0,
                reasoning_path=[],
                supporting_evidence=[],
                query=query,
            )

        # Build answer from top concept
        top_concept = concepts[0]
        related = self._graph.get_related_concepts(top_concept.id)
        prerequisites = self._graph.get_prerequisites(top_concept.id)

        evidence = [top_concept.description]
        path = [top_concept.name]

        if prerequisites:
            evidence.append(f"Prerequisites: {', '.join(p.name for p in prerequisites)}")
            path.extend(p.name for p in prerequisites)

        if related:
            evidence.append(f"Related: {', '.join(r.name for r in related)}")
            path.extend(r.name for r in related[:3])

        return ReasoningResult(
            answer=f"Found concept: {top_concept.name}. {top_concept.description}",
            confidence=0.7 if top_concept.description else 0.4,
            reasoning_path=path,
            supporting_evidence=evidence,
            query=query,
        )

    def explain(self, source_id: str, target_id: str) -> ReasoningResult:
        """Explain the relationship between two concepts."""
        path = self._graph.find_path(source_id, target_id)
        if not path:
            return ReasoningResult(
                answer="No path found between concepts",
                confidence=0.0,
                reasoning_path=[],
                supporting_evidence=[],
                query=f"Explain {source_id} to {target_id}",
            )

        concepts = [self._graph.get_concept(cid) for cid in path]
        names = [c.name for c in concepts if c]

        return ReasoningResult(
            answer=f"Path from {names[0]} to {names[-1]}: {' → '.join(names)}",
            confidence=0.8,
            reasoning_path=names,
            supporting_evidence=[
                f"{names[i]} → {names[i+1]}" for i in range(len(names) - 1)
            ],
            query=f"Explain {source_id} to {target_id}",
        )
