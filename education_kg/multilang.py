"""Multi-language support."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Translation:
    key: str
    language: str
    value: str


class MultiLanguageSupport:
    """Multi-language support for 10+ languages."""

    def __init__(self):
        self._translations: dict[str, dict[str, str]] = {}
        self._load_default_translations()

    def _load_default_translations(self) -> None:
        """Load default translations."""
        self._translations = {
            "en": {
                "welcome": "Welcome to Education Knowledge Graph",
                "concept": "Concept",
                "relation": "Relation",
                "learning_path": "Learning Path",
                "quiz": "Quiz",
                "search": "Search",
                "results": "Results",
                "no_results": "No results found",
                "difficulty": "Difficulty",
                "prerequisites": "Prerequisites",
                "related": "Related Concepts",
            },
            "es": {
                "welcome": "Bienvenido al Grafo de Conocimiento Educativo",
                "concept": "Concepto",
                "relation": "Relación",
                "learning_path": "Ruta de Aprendizaje",
                "quiz": "Cuestionario",
                "search": "Buscar",
                "results": "Resultados",
                "no_results": "No se encontraron resultados",
                "difficulty": "Dificultad",
                "prerequisites": "Prerrequisitos",
                "related": "Conceptos Relacionados",
            },
            "fr": {
                "welcome": "Bienvenue dans le Graphe de Connaissances Éducatif",
                "concept": "Concept",
                "relation": "Relation",
                "learning_path": "Parcours d'Apprentissage",
                "quiz": "Quiz",
                "search": "Rechercher",
                "results": "Résultats",
                "no_results": "Aucun résultat trouvé",
                "difficulty": "Difficulté",
                "prerequisites": "Prérequis",
                "related": "Concepts Connexes",
            },
            "de": {
                "welcome": "Willkommen im Bildungswissensgraph",
                "concept": "Konzept",
                "relation": "Beziehung",
                "learning_path": "Lernpfad",
                "quiz": "Quiz",
                "search": "Suchen",
                "results": "Ergebnisse",
                "no_results": "Keine Ergebnisse gefunden",
                "difficulty": "Schwierigkeit",
                "prerequisites": "Voraussetzungen",
                "related": "Verwandte Konzepte",
            },
            "zh": {
                "welcome": "欢迎使用教育知识图谱",
                "concept": "概念",
                "relation": "关系",
                "learning_path": "学习路径",
                "quiz": "测验",
                "search": "搜索",
                "results": "结果",
                "no_results": "未找到结果",
                "difficulty": "难度",
                "prerequisites": "先修课程",
                "related": "相关概念",
            },
            "ja": {
                "welcome": "教育知識グラフへようこそ",
                "concept": "概念",
                "relation": "関係",
                "learning_path": "学習パス",
                "quiz": "クイズ",
                "search": "検索",
                "results": "結果",
                "no_results": "結果が見つかりません",
                "difficulty": "難易度",
                "prerequisites": "前提条件",
                "related": "関連概念",
            },
            "ko": {
                "welcome": "교육 지식 그래프에 오신 것을 환영합니다",
                "concept": "개념",
                "relation": "관계",
                "learning_path": "학습 경로",
                "quiz": "퀴즈",
                "search": "검색",
                "results": "결과",
                "no_results": "결과를 찾을 수 없습니다",
                "difficulty": "난이도",
                "prerequisites": "선수 과목",
                "related": "관련 개념",
            },
            "ar": {
                "welcome": "مرحبًا بك في الرسم البياني المعرفي التعليمي",
                "concept": "مفهوم",
                "relation": "علاقة",
                "learning_path": "مسار التعلم",
                "quiz": "اختبار",
                "search": "بحث",
                "results": "النتائج",
                "no_results": "لم يتم العثور على نتائج",
                "difficulty": "الصعوبة",
                "prerequisites": "المتطلبات المسبقة",
                "related": "المفاهيم ذات الصلة",
            },
            "hi": {
                "welcome": "शिक्षा ज्ञान ग्राफ में आपका स्वागत है",
                "concept": "अवधारणा",
                "relation": "संबंध",
                "learning_path": "शिक्षण पथ",
                "quiz": "क्विज़",
                "search": "खोज",
                "results": "परिणाम",
                "no_results": "कोई परिणाम नहीं मिला",
                "difficulty": "कठिनाई",
                "prerequisites": "पूर्वापेक्षाएँ",
                "related": "संबंधित अवधारणाएँ",
            },
            "pt": {
                "welcome": "Bem-vindo ao Grafo de Conhecimento Educacional",
                "concept": "Conceito",
                "relation": "Relação",
                "learning_path": "Caminho de Aprendizagem",
                "quiz": "Questionário",
                "search": "Pesquisar",
                "results": "Resultados",
                "no_results": "Nenhum resultado encontrado",
                "difficulty": "Dificuldade",
                "prerequisites": "Pré-requisitos",
                "related": "Conceitos Relacionados",
            },
        }

    def translate(self, key: str, language: str) -> str:
        """Translate a key to the specified language."""
        if language in self._translations:
            return self._translations[language].get(key, key)
        return key

    def get_supported_languages(self) -> list[str]:
        """Get list of supported language codes."""
        return list(self._translations.keys())

    def add_translation(self, language: str, key: str, value: str) -> None:
        """Add a translation."""
        if language not in self._translations:
            self._translations[language] = {}
        self._translations[language][key] = value

    def detect_language(self, text: str) -> str:
        """Detect language from text (simplified)."""
        # Simple heuristic based on character ranges
        if any('\u4e00' <= c <= '\u9fff' for c in text):
            return "zh"
        if any('\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff' for c in text):
            return "ja"
        if any('\uac00' <= c <= '\ud7af' for c in text):
            return "ko"
        if any('\u0600' <= c <= '\u06ff' for c in text):
            return "ar"
        if any('\u0900' <= c <= '\u097f' for c in text):
            return "hi"
        # Default to English for detection, could be extended
        return "en"
