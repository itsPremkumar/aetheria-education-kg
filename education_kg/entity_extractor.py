"""Entity extraction from educational text."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from education_kg.models import Concept, ConceptDifficulty


@dataclass
class ExtractionResult:
    concepts: list[Concept] = field(default_factory=list)
    confidence: float = 0.0
    source_text: str = ""


class EntityExtractor:
    """Extract educational concepts from text."""

    def __init__(self):
        self._stop_words = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "can", "shall",
            "to", "of", "in", "for", "on", "with", "at", "by", "from",
            "as", "into", "through", "during", "before", "after", "above",
            "below", "between", "out", "off", "over", "under", "again",
            "further", "then", "once", "here", "there", "when", "where",
            "why", "how", "all", "each", "every", "both", "few", "more",
            "most", "other", "some", "such", "no", "nor", "not", "only",
            "own", "same", "so", "than", "too", "very", "just", "because",
            "but", "and", "or", "if", "while", "about", "up", "it", "its",
        }

        self._difficulty_keywords = {
            ConceptDifficulty.BEGINNER: [
                "basic", "introduction", "intro", "fundamental", "simple",
                "beginner", "start", "first", "overview",
            ],
            ConceptDifficulty.INTERMEDIATE: [
                "intermediate", "advanced", "complex", "detailed", "in-depth",
                "practical", "application", "applied",
            ],
            ConceptDifficulty.ADVANCED: [
                "advanced", "expert", "complex", "sophisticated", "research",
                "theoretical", "cutting-edge", "state-of-the-art",
            ],
        }

    def extract(self, text: str, subject: str = "") -> ExtractionResult:
        """Extract concepts from text."""
        concepts = []
        seen_names = set()

        # Extract noun phrases (simplified)
        noun_phrases = self._extract_noun_phrases(text)

        for phrase in noun_phrases:
            name = phrase.strip().title()
            if len(name) < 3 or name.lower() in seen_names:
                continue
            if self._is_stop_word_phrase(name):
                continue

            seen_names.add(name.lower())
            difficulty = self._infer_difficulty(text, name)

            concept = Concept(
                id=f"concept_{len(concepts)}_{hash(name) % 10000}",
                name=name,
                description=f"Extracted from text: {text[:100]}...",
                difficulty=difficulty,
                subject=subject,
                tags=self._extract_tags(text, name),
            )
            concepts.append(concept)

        return ExtractionResult(
            concepts=concepts,
            confidence=0.7 if concepts else 0.0,
            source_text=text,
        )

    def _extract_noun_phrases(self, text: str) -> list[str]:
        """Extract noun phrases from text (simplified)."""
        # Split by common delimiters
        phrases = re.split(r'[;,\n\t]+', text)
        result = []

        for phrase in phrases:
            phrase = phrase.strip()
            if not phrase:
                continue

            # Look for capitalized phrases (potential proper nouns)
            words = phrase.split()
            current_phrase = []

            for word in words:
                clean = re.sub(r'[^a-zA-Z0-9\s-]', '', word)
                if clean and (clean[0].isupper() or clean.isupper()):
                    current_phrase.append(clean)
                else:
                    if current_phrase:
                        result.append(" ".join(current_phrase))
                        current_phrase = []

            if current_phrase:
                result.append(" ".join(current_phrase))

            # Also add the whole phrase if it's short enough
            if 1 <= len(words) <= 4:
                result.append(phrase)

        return result

    def _is_stop_word_phrase(self, phrase: str) -> bool:
        """Check if phrase is mostly stop words."""
        words = phrase.lower().split()
        if not words:
            return True
        stop_count = sum(1 for w in words if w in self._stop_words)
        return stop_count / len(words) > 0.6

    def _infer_difficulty(self, text: str, concept_name: str) -> ConceptDifficulty:
        """Infer difficulty from context."""
        text_lower = text.lower()
        concept_lower = concept_name.lower()

        for difficulty, keywords in self._difficulty_keywords.items():
            for keyword in keywords:
                if keyword in text_lower or keyword in concept_lower:
                    return difficulty

        return ConceptDifficulty.BEGINNER

    def _extract_tags(self, text: str, concept_name: str) -> list[str]:
        """Extract tags from context."""
        tags = []
        text_lower = text.lower()

        tag_keywords = {
            "math": ["math", "mathematics", "algebra", "calculus", "geometry"],
            "science": ["science", "physics", "chemistry", "biology"],
            "programming": ["programming", "code", "software", "algorithm"],
            "language": ["language", "grammar", "vocabulary", "writing"],
            "history": ["history", "historical", "ancient", "modern"],
        }

        for tag, keywords in tag_keywords.items():
            if any(kw in text_lower for kw in keywords):
                tags.append(tag)

        return tags
