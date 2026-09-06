"""Reasoning engine for answering questions using the knowledge graph."""

from typing import List, Dict, Any, Optional
from .knowledge_graph import KnowledgeGraph
from .models import Concept, RelationType


class ReasoningEngine:
    """Answer questions using knowledge graph traversal."""

    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.kg = knowledge_graph

    def answer(self, question: str) -> Dict[str, Any]:
        """Answer a question using the knowledge graph."""
        keywords = question.lower().split()
        relevant_concepts = []
        for keyword in keywords:
            relevant_concepts.extend(self.kg.search(keyword))

        if not relevant_concepts:
            return {
                "answer": "I don't have enough information to answer this question.",
                "confidence": 0.0,
                "concepts_used": [],
            }

        best_concept = max(relevant_concepts, key=lambda c: c.importance)
        related = self.kg.get_related_concepts(best_concept.id)
        prereqs = self.kg.get_prerequisites(best_concept.id)

        answer_parts = [f"Based on the knowledge graph, {best_concept.name}:"]
        if best_concept.description:
            answer_parts.append(best_concept.description)
        if prereqs:
            prereq_names = ", ".join(p.name for p in prereqs[:3])
            answer_parts.append(f"Prerequisites: {prereq_names}")
        if related:
            related_names = ", ".join(r.name for r in related[:3])
            answer_parts.append(f"Related concepts: {related_names}")

        confidence = min(0.9, 0.5 + (len(relevant_concepts) * 0.1))

        return {
            "answer": "\n".join(answer_parts),
            "confidence": confidence,
            "concepts_used": [c.id for c in relevant_concepts[:5]],
        }

    def explain(self, concept_id: str) -> Dict[str, Any]:
        """Explain a concept with its relationships."""
        concept = self.kg.get_concept(concept_id)
        if not concept:
            return {"error": "Concept not found"}

        prereqs = self.kg.get_prerequisites(concept_id)
        related = self.kg.get_related_concepts(concept_id)
        learning_order = self.kg.get_learning_order(concept_id)

        return {
            "concept": concept.model_dump(),
            "prerequisites": [p.model_dump() for p in prereqs],
            "related_concepts": [r.model_dump() for r in related],
            "learning_order": learning_order,
        }

    def find_path(self, source_id: str, target_id: str) -> List[str]:
        """Find a learning path between two concepts."""
        try:
            import networkx as nx
            path = nx.shortest_path(self.kg.graph, source_id, target_id)
            return path
        except (nx.NetworkXError, nx.NodeNotFound):
            return []
