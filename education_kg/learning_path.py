"""Learning path generation."""

from __future__ import annotations

import uuid
from typing import Any

from education_kg.graph import KnowledgeGraph
from education_kg.models import (
    Concept,
    ConceptDifficulty,
    LearningPath,
    RelationType,
)


class LearningPathGenerator:
    """Create personalized learning paths."""

    def __init__(self, graph: KnowledgeGraph):
        self._graph = graph

    def generate(
        self,
        start_concept: str,
        goal_concept: str,
        max_concepts: int = 10,
    ) -> LearningPath:
        """Generate a learning path from start to goal."""
        path = self._graph.find_path(start_concept, goal_concept, max_depth=max_concepts)

        if not path:
            # Try to find a path via intermediate concepts
            path = self._find_indirect_path(start_concept, goal_concept, max_concepts)

        if not path:
            return LearningPath(
                id=str(uuid.uuid4()),
                title=f"Path from {start_concept} to {goal_concept}",
                concepts=[],
                estimated_hours=0.0,
                difficulty=ConceptDifficulty.BEGINNER,
                description="No path found",
            )

        concepts = [self._graph.get_concept(cid) for cid in path]
        valid_concepts = [c for c in concepts if c]

        # Calculate estimated hours
        hours_per_concept = 2.0
        estimated_hours = len(valid_concepts) * hours_per_concept

        # Determine overall difficulty
        difficulty = max(
            (c.difficulty for c in valid_concepts),
            key=lambda d: {"beginner": 0, "intermediate": 1, "advanced": 2}.get(d.value, 0),
            default=ConceptDifficulty.BEGINNER,
        )

        return LearningPath(
            id=str(uuid.uuid4()),
            title=f"Learning Path: {start_concept} → {goal_concept}",
            concepts=path,
            estimated_hours=estimated_hours,
            difficulty=difficulty,
            description=f"{len(valid_concepts)} concepts to master",
        )

    def generate_from_prerequisites(self, concept_id: str) -> LearningPath:
        """Generate path from all prerequisites to target concept."""
        prereqs = self._graph.get_prerequisites(concept_id)
        all_concepts = [concept_id]

        for prereq in prereqs:
            all_concepts.append(prereq.id)
            # Recursively add prerequisites
            sub_path = self.generate_from_prerequisites(prereq.id)
            for cid in sub_path.concepts:
                if cid not in all_concepts:
                    all_concepts.append(cid)

        return LearningPath(
            id=str(uuid.uuid4()),
            title=f"Prerequisite Path for {concept_id}",
            concepts=all_concepts[:10],
            estimated_hours=len(all_concepts[:10]) * 2.0,
            difficulty=ConceptDifficulty.INTERMEDIATE,
            description=f"Prerequisites for {concept_id}",
        )

    def _find_indirect_path(
        self,
        source: str,
        target: str,
        max_depth: int,
    ) -> list[str] | None:
        """Find path through intermediate concepts."""
        source_concept = self._graph.get_concept(source)
        target_concept = self._graph.get_concept(target)
        if not source_concept or not target_concept:
            return None

        # Try to find a common intermediate
        source_related = set(r.target_id for r in self._graph.get_relations(source))
        target_related = set(r.target_id for r in self._graph.get_reverse_relations(target))

        common = source_related & target_related
        if common:
            intermediate = next(iter(common))
            path1 = self._graph.find_path(source, intermediate, max_depth // 2)
            path2 = self._graph.find_path(intermediate, target, max_depth // 2)
            if path1 and path2:
                return path1 + path2[1:]

        return None
