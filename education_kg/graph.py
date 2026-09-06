"""Knowledge Graph implementation."""

from __future__ import annotations

import heapq
import uuid
from collections import defaultdict, deque
from typing import Any, Iterator

from education_kg.models import (
    Concept,
    ConceptDifficulty,
    LearningPath,
    Relation,
    RelationType,
)


class KnowledgeGraph:
    """Knowledge Graph with concept relationships."""

    def __init__(self):
        self._concepts: dict[str, Concept] = {}
        self._relations: dict[str, list[Relation]] = defaultdict(list)
        self._reverse_relations: dict[str, list[Relation]] = defaultdict(list)

    def add_concept(self, concept: Concept) -> None:
        """Add a concept to the graph."""
        self._concepts[concept.id] = concept

    def get_concept(self, concept_id: str) -> Concept | None:
        """Get a concept by ID."""
        return self._concepts.get(concept_id)

    def get_all_concepts(self) -> list[Concept]:
        """Get all concepts."""
        return list(self._concepts.values())

    def add_relation(self, relation: Relation) -> None:
        """Add a relation between concepts."""
        self._relations[relation.source_id].append(relation)
        self._reverse_relations[relation.target_id].append(relation)

    def get_relations(self, concept_id: str) -> list[Relation]:
        """Get all relations from a concept."""
        return self._relations.get(concept_id, [])

    def get_reverse_relations(self, concept_id: str) -> list[Relation]:
        """Get all relations pointing to a concept."""
        return self._reverse_relations.get(concept_id, [])

    def get_prerequisites(self, concept_id: str) -> list[Concept]:
        """Get prerequisite concepts."""
        prereqs = []
        for rel in self._reverse_relations.get(concept_id, []):
            if rel.relation_type == RelationType.PREREQUISITE:
                concept = self._concepts.get(rel.source_id)
                if concept:
                    prereqs.append(concept)
        return prereqs

    def get_dependents(self, concept_id: str) -> list[Concept]:
        """Get concepts that depend on this one."""
        dependents = []
        for rel in self._relations.get(concept_id, []):
            if rel.relation_type == RelationType.PREREQUISITE:
                concept = self._concepts.get(rel.target_id)
                if concept:
                    dependents.append(concept)
        return dependents

    def find_path(
        self,
        source_id: str,
        target_id: str,
        max_depth: int = 10,
    ) -> list[str] | None:
        """Find path between concepts using BFS."""
        if source_id not in self._concepts or target_id not in self._concepts:
            return None

        queue = deque([(source_id, [source_id])])
        visited = {source_id}

        while queue:
            current, path = queue.popleft()
            if len(path) > max_depth:
                continue

            for rel in self._relations.get(current, []):
                if rel.target_id == target_id:
                    return path + [target_id]
                if rel.target_id not in visited:
                    visited.add(rel.target_id)
                    queue.append((rel.target_id, path + [rel.target_id]))

        return None

    def topological_sort(self) -> list[str]:
        """Topological sort based on prerequisite relations."""
        in_degree = defaultdict(int)
        for concept_id in self._concepts:
            if concept_id not in in_degree:
                in_degree[concept_id] = 0

        for rels in self._relations.values():
            for rel in rels:
                if rel.relation_type == RelationType.PREREQUISITE:
                    in_degree[rel.target_id] += 1

        queue = deque([cid for cid, deg in in_degree.items() if deg == 0])
        result = []

        while queue:
            current = queue.popleft()
            result.append(current)
            for rel in self._relations.get(current, []):
                if rel.relation_type == RelationType.PREREQUISITE:
                    in_degree[rel.target_id] -= 1
                    if in_degree[rel.target_id] == 0:
                        queue.append(rel.target_id)

        return result

    def search(
        self,
        query: str,
        subject: str = "",
        difficulty: ConceptDifficulty | None = None,
        limit: int = 20,
    ) -> list[Concept]:
        """Search concepts by name/description."""
        query_lower = query.lower()
        query_words = query_lower.split()
        results = []

        for concept in self._concepts.values():
            score = 0
            name_lower = concept.name.lower()
            desc_lower = concept.description.lower()

            # Full phrase match
            if query_lower in name_lower:
                score += 10
            if query_lower in desc_lower:
                score += 5

            # Word-level match (any query word in name/desc)
            for word in query_words:
                if word in name_lower:
                    score += 3
                if word in desc_lower:
                    score += 1

            if concept.tags:
                tag_text = " ".join(concept.tags).lower()
                if query_lower in tag_text:
                    score += 3
                for word in query_words:
                    if word in tag_text:
                        score += 1

            if score > 0:
                if subject and concept.subject != subject:
                    continue
                if difficulty and concept.difficulty != difficulty:
                    continue
                results.append((score, concept))

        results.sort(key=lambda x: (-x[0], x[1].name))
        return [c for _, c in results[:limit]]

    def get_related_concepts(self, concept_id: str) -> list[Concept]:
        """Get related concepts."""
        related = set()
        for rel in self._relations.get(concept_id, []):
            related.add(rel.target_id)
        for rel in self._reverse_relations.get(concept_id, []):
            related.add(rel.source_id)

        return [self._concepts[cid] for cid in related if cid in self._concepts]

    def get_statistics(self) -> dict[str, Any]:
        """Get graph statistics."""
        return {
            "total_concepts": len(self._concepts),
            "total_relations": sum(len(rels) for rels in self._relations.values()),
            "subjects": list(set(c.subject for c in self._concepts.values())),
            "difficulty_counts": {
                "beginner": sum(
                    1 for c in self._concepts.values()
                    if c.difficulty == ConceptDifficulty.BEGINNER
                ),
                "intermediate": sum(
                    1 for c in self._concepts.values()
                    if c.difficulty == ConceptDifficulty.INTERMEDIATE
                ),
                "advanced": sum(
                    1 for c in self._concepts.values()
                    if c.difficulty == ConceptDifficulty.ADVANCED
                ),
            },
        }

    def __len__(self) -> int:
        return len(self._concepts)

    def __contains__(self, concept_id: str) -> bool:
        return concept_id in self._concepts
