"""Tests for Graph Storage."""

import os
import tempfile
import pytest

from education_kg.models import Concept, ConceptDifficulty
from education_kg.storage import GraphStorage


class TestGraphStorage:
    def test_create(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = os.path.join(tmp, "test.db")
            storage = GraphStorage(db_path)
            assert storage is not None

    def test_connect_close(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = os.path.join(tmp, "test.db")
            storage = GraphStorage(db_path)
            storage.connect()
            storage.close()

    def test_save_and_load_concepts(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = os.path.join(tmp, "test.db")
            storage = GraphStorage(db_path)
            storage.connect()

            concept = Concept(id="c1", name="Python", description="A language")
            storage.save_concept(concept)

            concepts = storage.load_concepts()
            assert len(concepts) == 1
            assert concepts[0].name == "Python"

            storage.close()

    def test_save_duplicate_concept(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = os.path.join(tmp, "test.db")
            storage = GraphStorage(db_path)
            storage.connect()

            concept = Concept(id="c1", name="Python", description="V1")
            storage.save_concept(concept)
            concept2 = Concept(id="c1", name="Python", description="V2")
            storage.save_concept(concept2)

            concepts = storage.load_concepts()
            assert len(concepts) == 1
            assert concepts[0].description == "V2"

            storage.close()

    def test_save_relation(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = os.path.join(tmp, "test.db")
            storage = GraphStorage(db_path)
            storage.connect()

            from education_kg.models import Relation, RelationType
            relation = Relation("c1", "c2", RelationType.PREREQUISITE)
            storage.save_relation(relation)

            storage.close()

    def test_save_learning_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = os.path.join(tmp, "test.db")
            storage = GraphStorage(db_path)
            storage.connect()

            from education_kg.models import LearningPath
            path = LearningPath(id="lp1", title="Python Path", concepts=["c1", "c2"])
            storage.save_learning_path(path)

            storage.close()

    def test_export_import_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = os.path.join(tmp, "test.db")
            json_path = os.path.join(tmp, "export.json")

            storage = GraphStorage(db_path)
            storage.connect()
            storage.save_concept(Concept(id="c1", name="Test", description="Desc"))
            storage.export_json(json_path)

            assert os.path.exists(json_path)

            # Import into new storage
            db_path2 = os.path.join(tmp, "test2.db")
            storage2 = GraphStorage(db_path2)
            storage2.connect()
            storage2.import_json(json_path)

            concepts = storage2.load_concepts()
            assert len(concepts) == 1
            assert concepts[0].name == "Test"

            storage.close()
            storage2.close()
