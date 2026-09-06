"""Education Knowledge Graph — offline-first learning assistant."""

__version__ = "1.0.0"

from education_kg.models import Concept, Relation, LearningPath, Quiz, QuizQuestion
from education_kg.graph import KnowledgeGraph
from education_kg.entity_extractor import EntityExtractor
from education_kg.relation_extractor import RelationExtractor
from education_kg.reasoning import ReasoningEngine
from education_kg.learning_path import LearningPathGenerator
from education_kg.quiz_generator import QuizGenerator
from education_kg.multilang import MultiLanguageSupport
from education_kg.storage import GraphStorage
from education_kg.pipeline import Pipeline

__all__ = [
    "KnowledgeGraph",
    "Concept",
    "Relation",
    "LearningPath",
    "Quiz",
    "QuizQuestion",
    "EntityExtractor",
    "RelationExtractor",
    "ReasoningEngine",
    "LearningPathGenerator",
    "QuizGenerator",
    "MultiLanguageSupport",
    "GraphStorage",
    "Pipeline",
]
