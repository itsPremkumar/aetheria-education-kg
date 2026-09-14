"""Tests for IEEE LOM — Learning Object Metadata standard."""

import pytest

from education_kg.graph import KnowledgeGraph
from education_kg.models import Concept, ConceptDifficulty, LearningPath, Relation, RelationType
from education_kg.entity_extractor import EntityExtractor
from education_kg.quiz_generator import QuizGenerator
from education_kg.reasoning import ReasoningEngine
from education_kg.learning_path import LearningPathGenerator


class TestIEEELOM:
    """Test IEEE LOM (Learning Object Metadata) standard compliance."""

    def test_create_ieee_lom_graph(self):
        kg = KnowledgeGraph()
        assert kg is not None
        assert len(kg) == 0

    def test_ieee_lom_learning_objects(self):
        kg = KnowledgeGraph()
        learning_objects = [
            Concept(id="lom1", name="Introduction to Python",
                    description="Basic Python programming concepts",
                    difficulty=ConceptDifficulty.BEGINNER,
                    subject="computer_science",
                    metadata={"lom_type": "learning_object", "interactivity_type": "expositive"}),
            Concept(id="lom2", name="Data Structures",
                    description="Arrays, lists, and trees",
                    difficulty=ConceptDifficulty.INTERMEDIATE,
                    subject="computer_science",
                    metadata={"lom_type": "learning_object", "interactivity_type": "active"}),
            Concept(id="lom3", name="Algorithms",
                    description="Sorting and searching algorithms",
                    difficulty=ConceptDifficulty.ADVANCED,
                    subject="computer_science",
                    metadata={"lom_type": "learning_object", "interactivity_type": "active"}),
        ]
        for lo in learning_objects:
            kg.add_concept(lo)
        assert len(kg) == 3

    def test_ieee_lom_metadata_fields(self):
        kg = KnowledgeGraph()
        concept = Concept(
            id="lom1",
            name="Learning Object",
            description="A learning object",
            difficulty=ConceptDifficulty.BEGINNER,
            subject="education",
            metadata={
                "lom_type": "learning_object",
                "title": "Learning Object",
                "description": "A learning object",
                "language": "en",
                "interactivity_type": "expositive",
                "learning_resource_type": "exercise",
                "interactivity_level": "low",
                "semantic_density": "medium",
                "intended_end_user": "learner",
                "context": "school",
                "difficulty": "easy",
                "typical_learning_time": "PT30M",
            },
        )
        kg.add_concept(concept)
        result = kg.get_concept("lom1")
        assert result is not None
        assert "lom_type" in result.metadata
        assert result.metadata["lom_type"] == "learning_object"

    def test_ieee_lom_difficulty_mapping(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="lom1", name="Easy", difficulty=ConceptDifficulty.BEGINNER,
                               metadata={"lom_difficulty": "easy"}))
        kg.add_concept(Concept(id="lom2", name="Medium", difficulty=ConceptDifficulty.INTERMEDIATE,
                               metadata={"lom_difficulty": "medium"}))
        kg.add_concept(Concept(id="lom3", name="Hard", difficulty=ConceptDifficulty.ADVANCED,
                               metadata={"lom_difficulty": "hard"}))
        results = kg.search("", difficulty=ConceptDifficulty.BEGINNER)
        assert len(results) == 1
        assert results[0].metadata["lom_difficulty"] == "easy"

    def test_ieee_lom_interactivity_types(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="lom1", name="Expositive", metadata={"interactivity_type": "expositive"}))
        kg.add_concept(Concept(id="lom2", name="Active", metadata={"interactivity_type": "active"}))
        kg.add_concept(Concept(id="lom3", name="Mixed", metadata={"interactivity_type": "mixed"}))
        stats = kg.get_statistics()
        assert stats["total_concepts"] == 3

    def test_ieee_lom_learning_path(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="lom1", name="LO1", difficulty=ConceptDifficulty.BEGINNER,
                               metadata={"lom_type": "learning_object"}))
        kg.add_concept(Concept(id="lom2", name="LO2", difficulty=ConceptDifficulty.INTERMEDIATE,
                               metadata={"lom_type": "learning_object"}))
        kg.add_concept(Concept(id="lom3", name="LO3", difficulty=ConceptDifficulty.ADVANCED,
                               metadata={"lom_type": "learning_object"}))
        kg.add_relation(Relation("lom1", "lom2", RelationType.PREREQUISITE))
        kg.add_relation(Relation("lom2", "lom3", RelationType.PREREQUISITE))
        generator = LearningPathGenerator(kg)
        path = generator.generate("lom1", "lom3")
        assert len(path.concepts) == 3
        assert path.estimated_hours > 0

    def test_ieee_lom_quiz_generation(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="lom1", name="LO1", description="First learning object",
                               difficulty=ConceptDifficulty.BEGINNER,
                               metadata={"lom_type": "learning_object"}))
        kg.add_concept(Concept(id="lom2", name="LO2", description="Second learning object",
                               difficulty=ConceptDifficulty.INTERMEDIATE,
                               metadata={"lom_type": "learning_object"}))
        generator = QuizGenerator(kg)
        quiz = generator.generate(["lom1", "lom2"], num_questions=5)
        assert quiz is not None
        assert len(quiz.questions) <= 5

    def test_ieee_lom_reasoning(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="lom1", name="Learning Object",
                               description="A reusable unit of learning",
                               difficulty=ConceptDifficulty.BEGINNER,
                               metadata={"lom_type": "learning_object"}))
        engine = ReasoningEngine(kg)
        result = engine.answer("What is a learning object?", "lom1")
        assert result.confidence > 0
        assert "Learning Object" in result.answer

    def test_ieee_lom_entity_extraction(self):
        extractor = EntityExtractor()
        text = "IEEE LOM defines learning object metadata for educational resources"
        result = extractor.extract(text, "education")
        assert len(result.concepts) >= 1
        assert result.confidence > 0

    def test_ieee_lom_statistics(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="lom1", name="LO1", difficulty=ConceptDifficulty.BEGINNER,
                               subject="cs", metadata={"lom_type": "learning_object"}))
        kg.add_concept(Concept(id="lom2", name="LO2", difficulty=ConceptDifficulty.INTERMEDIATE,
                               subject="cs", metadata={"lom_type": "learning_object"}))
        kg.add_concept(Concept(id="lom3", name="LO3", difficulty=ConceptDifficulty.ADVANCED,
                               subject="math", metadata={"lom_type": "learning_object"}))
        kg.add_relation(Relation("lom1", "lom2", RelationType.PREREQUISITE))
        kg.add_relation(Relation("lom2", "lom3", RelationType.PREREQUISITE))
        stats = kg.get_statistics()
        assert stats["total_concepts"] == 3
        assert stats["total_relations"] == 2
        assert "cs" in stats["subjects"]
        assert "math" in stats["subjects"]

    def test_ieee_lom_topological_order(self):
        kg = KnowledgeGraph()
        kg.add_concept(Concept(id="lom1", name="Foundation", difficulty=ConceptDifficulty.BEGINNER))
        kg.add_concept(Concept(id="lom2", name="Intermediate", difficulty=ConceptDifficulty.INTERMEDIATE))
        kg.add_concept(Concept(id="lom3", name="Advanced", difficulty=ConceptDifficulty.ADVANCED))
        kg.add_relation(Relation("lom1", "lom2", RelationType.PREREQUISITE))
        kg.add_relation(Relation("lom2", "lom3", RelationType.PREREQUISITE))
        sorted_ids = kg.topological_sort()
        assert sorted_ids.index("lom1") < sorted_ids.index("lom2")
        assert sorted_ids.index("lom2") < sorted_ids.index("lom3")
