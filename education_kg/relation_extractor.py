"""Relation extraction between educational concepts."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from education_kg.models import Concept, Relation, RelationType


@dataclass
class RelationResult:
    relations: list[Relation] = field(default_factory=list)
    confidence: float = 0.0
    source_concept: str = ""
    target_concept: str = ""


class RelationExtractor:
    """Identify relationships between concepts."""

    def __init__(self):
        self._relation_patterns = {
            RelationType.PREREQUISITE: [
                r"(?:requires?|needs?|depends?\s+on|must\s+know|before)",
                r"(?:prerequisite|prereq)",
            ],
            RelationType.BUILDSON: [
                r"(?:builds?\s+(?:on|upon)|extends?|based\s+on)",
                r"(?:advanced|extension)",
            ],
            RelationType.RELATEDTO: [
                r"(?:related\s+to|connected\s+to|similar\s+to)",
                r"(?:associated|linked)",
            ],
            RelationType.PARTOF: [
                r"(?:part\s+of|component\s+of|element\s+of)",
                r"(?:contains?|includes?)",
            ],
            RelationType.LEADSTO: [
                r"(?:leads?\s+to|results?\s+in|enables?)",
                r"(?:outcome|consequence)",
            ],
        }

        self._implicit_rules = {
            "difficulty_order": self._infer_difficulty_order,
            "tag_overlap": self._infer_tag_overlap,
            "name_pattern": self._infer_name_pattern,
        }

    def extract_relations(
        self,
        concept1: Concept,
        concept2: str,
        context: str = "",
    ) -> RelationResult:
        """Extract relations between two concepts."""
        relations = []
        context_lower = context.lower()

        for relation_type, patterns in self._relation_patterns.items():
            for pattern in patterns:
                if re.search(pattern, context_lower):
                    relations.append(
                        Relation(
                            source_id=concept1.id,
                            target_id=concept2,
                            relation_type=relation_type,
                            weight=0.8,
                            metadata={"pattern": pattern, "context": context[:100]},
                        )
                    )
                    break

        # Apply implicit rules
        if not relations:
            for rule_name, rule_fn in self._implicit_rules.items():
                result = rule_fn(concept1, concept2, context)
                if result:
                    relations.append(result)

        confidence = 0.8 if relations else 0.0

        return RelationResult(
            relations=relations,
            confidence=confidence,
            source_concept=concept1.name,
            target_concept=concept2,
        )

    def extract_all_relations(
        self,
        concepts: list[Concept],
        context_text: str = "",
    ) -> list[Relation]:
        """Extract all relations among a set of concepts."""
        relations = []

        for i, concept1 in enumerate(concepts):
            for concept2 in concepts[i + 1:]:
                # Check both directions
                result1 = self.extract_relations(concept1, concept2.id, context_text)
                relations.extend(result1.relations)

                result2 = self.extract_relations(concept2, concept1.id, context_text)
                relations.extend(result2.relations)

        return relations

    def _infer_difficulty_order(
        self,
        concept1: Concept,
        concept2: str,
        context: str,
    ) -> Relation | None:
        """Infer relations based on difficulty ordering."""
        difficulty_order = {"beginner": 0, "intermediate": 1, "advanced": 2}

        c1_level = difficulty_order.get(concept1.difficulty.value, 0)

        # If concept1 is beginner and concept2 name suggests advanced
        if c1_level == 0:
            advanced_keywords = ["advanced", "expert", "complex"]
            if any(kw in context.lower() for kw in advanced_keywords):
                return Relation(
                    source_id=concept1.id,
                    target_id=concept2,
                    relation_type=RelationType.LEADSTO,
                    weight=0.5,
                    metadata={"rule": "difficulty_order"},
                )

        return None

    def _infer_tag_overlap(
        self,
        concept1: Concept,
        concept2: str,
        context: str,
    ) -> Relation | None:
        """Infer relations based on tag overlap."""
        if concept1.tags:
            context_lower = context.lower()
            for tag in concept1.tags:
                if tag in context_lower:
                    return Relation(
                        source_id=concept1.id,
                        target_id=concept2,
                        relation_type=RelationType.RELATEDTO,
                        weight=0.6,
                        metadata={"rule": "tag_overlap", "tag": tag},
                    )

        return None

    def _infer_name_pattern(
        self,
        concept1: Concept,
        concept2: str,
        context: str,
    ) -> Relation | None:
        """Infer relations based on naming patterns."""
        name_words = set(concept1.name.lower().split())
        context_words = set(context.lower().split())

        if name_words & context_words:
            return Relation(
                source_id=concept1.id,
                target_id=concept2,
                relation_type=RelationType.RELATEDTO,
                weight=0.4,
                metadata={"rule": "name_pattern"},
            )

        return None
