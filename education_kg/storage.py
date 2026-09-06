"""Graph persistence and storage."""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime
from typing import Any

from education_kg.models import (
    Concept,
    ConceptDifficulty,
    LearningPath,
    Relation,
    RelationType,
)


class GraphStorage:
    """Store and load knowledge graphs."""

    def __init__(self, db_path: str = "education_kg.db"):
        self._db_path = db_path
        self._conn: sqlite3.Connection | None = None

    def connect(self) -> None:
        """Connect to database."""
        self._conn = sqlite3.connect(self._db_path)
        self._create_tables()

    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def _create_tables(self) -> None:
        """Create database tables."""
        if not self._conn:
            return

        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS concepts (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                difficulty TEXT DEFAULT 'beginner',
                subject TEXT DEFAULT '',
                tags TEXT DEFAULT '[]',
                metadata TEXT DEFAULT '{}',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS relations (
                source_id TEXT,
                target_id TEXT,
                relation_type TEXT DEFAULT 'related_to',
                weight REAL DEFAULT 1.0,
                metadata TEXT DEFAULT '{}',
                PRIMARY KEY (source_id, target_id, relation_type)
            );

            CREATE TABLE IF NOT EXISTS learning_paths (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                concepts TEXT DEFAULT '[]',
                estimated_hours REAL DEFAULT 0.0,
                difficulty TEXT DEFAULT 'beginner',
                description TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
        """)
        self._conn.commit()

    def save_concept(self, concept: Concept) -> None:
        """Save a concept to storage."""
        if not self._conn:
            return
        self._conn.execute(
            """INSERT OR REPLACE INTO concepts
               (id, name, description, difficulty, subject, tags, metadata, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                concept.id,
                concept.name,
                concept.description,
                concept.difficulty.value,
                concept.subject,
                json.dumps(concept.tags),
                json.dumps(concept.metadata),
                concept.created_at.isoformat(),
            ),
        )
        self._conn.commit()

    def load_concepts(self) -> list[Concept]:
        """Load all concepts from storage."""
        if not self._conn:
            return []
        cursor = self._conn.execute("SELECT * FROM concepts")
        concepts = []
        for row in cursor.fetchall():
            try:
                concept = Concept(
                    id=row[0],
                    name=row[1],
                    description=row[2],
                    difficulty=ConceptDifficulty(row[3]),
                    subject=row[4],
                    tags=json.loads(row[5]) if row[5] else [],
                    metadata=json.loads(row[6]) if row[6] else {},
                    created_at=datetime.fromisoformat(row[7]) if row[7] else datetime.utcnow(),
                )
                concepts.append(concept)
            except (ValueError, IndexError):
                continue
        return concepts

    def save_relation(self, relation: Relation) -> None:
        """Save a relation to storage."""
        if not self._conn:
            return
        self._conn.execute(
            """INSERT OR REPLACE INTO relations
               (source_id, target_id, relation_type, weight, metadata)
               VALUES (?, ?, ?, ?, ?)""",
            (
                relation.source_id,
                relation.target_id,
                relation.relation_type.value,
                relation.weight,
                json.dumps(relation.metadata),
            ),
        )
        self._conn.commit()

    def save_learning_path(self, path: LearningPath) -> None:
        """Save a learning path."""
        if not self._conn:
            return
        self._conn.execute(
            """INSERT OR REPLACE INTO learning_paths
               (id, title, concepts, estimated_hours, difficulty, description, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                path.id,
                path.title,
                json.dumps(path.concepts),
                path.estimated_hours,
                path.difficulty.value,
                path.description,
                path.created_at.isoformat(),
            ),
        )
        self._conn.commit()

    def export_json(self, filepath: str) -> None:
        """Export all data to JSON."""
        if not self._conn:
            return
        data = {
            "concepts": [c.to_dict() for c in self.load_concepts()],
            "relations": [],
            "learning_paths": [],
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def import_json(self, filepath: str) -> None:
        """Import data from JSON."""
        if not self._conn:
            return
        with open(filepath, "r") as f:
            data = json.load(f)
        for concept_data in data.get("concepts", []):
            try:
                concept = Concept(
                    id=concept_data["id"],
                    name=concept_data["name"],
                    description=concept_data.get("description", ""),
                    difficulty=ConceptDifficulty(concept_data.get("difficulty", "beginner")),
                    subject=concept_data.get("subject", ""),
                    tags=concept_data.get("tags", []),
                    metadata=concept_data.get("metadata", {}),
                )
                self.save_concept(concept)
            except (ValueError, KeyError):
                continue
