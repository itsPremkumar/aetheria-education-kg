"""Tests for Multi-Language Support."""

import pytest

from education_kg.multilang import MultiLanguageSupport, Translation


class TestMultiLanguageSupport:
    def test_create(self):
        ml = MultiLanguageSupport()
        assert ml is not None

    def test_get_supported_languages(self):
        ml = MultiLanguageSupport()
        langs = ml.get_supported_languages()
        assert isinstance(langs, list)
        assert len(langs) >= 10
        assert "en" in langs
        assert "es" in langs
        assert "fr" in langs
        assert "de" in langs
        assert "zh" in langs
        assert "ja" in langs
        assert "ko" in langs
        assert "ar" in langs
        assert "hi" in langs
        assert "pt" in langs

    def test_translate_english(self):
        ml = MultiLanguageSupport()
        result = ml.translate("welcome", "en")
        assert result == "Welcome to Education Knowledge Graph"

    def test_translate_spanish(self):
        ml = MultiLanguageSupport()
        result = ml.translate("welcome", "es")
        assert "Bienvenido" in result

    def test_translate_french(self):
        ml = MultiLanguageSupport()
        result = ml.translate("welcome", "fr")
        assert "Bienvenue" in result

    def test_translate_german(self):
        ml = MultiLanguageSupport()
        result = ml.translate("welcome", "de")
        assert "Willkommen" in result

    def test_translate_chinese(self):
        ml = MultiLanguageSupport()
        result = ml.translate("welcome", "zh")
        assert "欢迎" in result

    def test_translate_japanese(self):
        ml = MultiLanguageSupport()
        result = ml.translate("welcome", "ja")
        assert "ようこそ" in result

    def test_translate_korean(self):
        ml = MultiLanguageSupport()
        result = ml.translate("welcome", "ko")
        assert "환영" in result

    def test_translate_arabic(self):
        ml = MultiLanguageSupport()
        result = ml.translate("welcome", "ar")
        assert "مرحبًا" in result or "بك" in result

    def test_translate_hindi(self):
        ml = MultiLanguageSupport()
        result = ml.translate("welcome", "hi")
        assert "स्वागत" in result

    def test_translate_portuguese(self):
        ml = MultiLanguageSupport()
        result = ml.translate("welcome", "pt")
        assert "Bem-vindo" in result

    def test_translate_missing_key(self):
        ml = MultiLanguageSupport()
        result = ml.translate("nonexistent_key", "en")
        assert result == "nonexistent_key"

    def test_translate_missing_language(self):
        ml = MultiLanguageSupport()
        result = ml.translate("welcome", "xx")
        assert result == "welcome"

    def test_add_translation(self):
        ml = MultiLanguageSupport()
        ml.add_translation("it", "welcome", "Benvenuto")
        result = ml.translate("welcome", "it")
        assert result == "Benvenuto"

    def test_add_translation_new_language(self):
        ml = MultiLanguageSupport()
        ml.add_translation("sv", "hello", "Hej")
        assert "sv" in ml.get_supported_languages()
        assert ml.translate("hello", "sv") == "Hej"

    def test_detect_language_chinese(self):
        ml = MultiLanguageSupport()
        result = ml.detect_language("你好世界")
        assert result == "zh"

    def test_detect_language_japanese(self):
        ml = MultiLanguageSupport()
        result = ml.detect_language("こんにちは")
        assert result == "ja"

    def test_detect_language_korean(self):
        ml = MultiLanguageSupport()
        result = ml.detect_language("안녕하세요")
        assert result == "ko"

    def test_detect_language_arabic(self):
        ml = MultiLanguageSupport()
        result = ml.detect_language("مرحبا")
        assert result == "ar"

    def test_detect_language_hindi(self):
        ml = MultiLanguageSupport()
        result = ml.detect_language("नमस्ते")
        assert result == "hi"

    def test_detect_language_english(self):
        ml = MultiLanguageSupport()
        result = ml.detect_language("Hello world")
        assert result == "en"

    def test_all_languages_have_welcome(self):
        ml = MultiLanguageSupport()
        for lang in ml.get_supported_languages():
            result = ml.translate("welcome", lang)
            assert result != "welcome" or lang == "en"

    def test_all_languages_have_concept(self):
        ml = MultiLanguageSupport()
        for lang in ml.get_supported_languages():
            result = ml.translate("concept", lang)
            assert isinstance(result, str)


class TestTranslation:
    def test_create(self):
        t = Translation(key="test", language="en", value="Test")
        assert t.key == "test"
        assert t.language == "en"
        assert t.value == "Test"
