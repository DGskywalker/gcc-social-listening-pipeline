"""
Unit tests for LLM Classifier (Versioned Prompts, Schema, Caching, Sarcasm).
"""

import pytest
from processing.llm_classifier import LLMClassifier


def test_classifier_prompt_loading():
    classifier = LLMClassifier()
    assert classifier.prompt_version == "1.0.0"
    assert "system_instruction" in classifier.prompt_config
    assert "output_schema" in classifier.prompt_config


def test_classifier_schema_compliance():
    classifier = LLMClassifier(cache_enabled=False)
    res = classifier.classify(
        text="تغطية 5G ممتازة وسريعة جداً من النور للاتصالات في بوليفارد الرياض",
        brand="Al-Noor Telecom",
        platform="tiktok",
        language="ar"
    )

    # Verify structured JSON output fields
    assert res["sentiment"] in ("positive", "negative", "neutral")
    assert isinstance(res["sentiment_score"], float)
    assert -1.0 <= res["sentiment_score"] <= 1.0
    assert "primary_theme" in res
    assert isinstance(res["confidence"], float)
    assert isinstance(res["is_sarcasm"], bool)
    assert res["dialect"] in ("Saudi", "Emirati", "Gulf", "MSA", "English", "Mixed")
    assert isinstance(res["reasoning"], str)
    assert res["sentiment"] == "positive"


def test_classifier_sarcasm_detection():
    classifier = LLMClassifier(cache_enabled=False)
    # Authentic GCC sarcastic post
    res = classifier.classify(
        text="ما قصرتوا يا النور قطعتوا النت وقت اجتماع زووم مصيري للشركة! فعلاً تثبتون كل يوم أنكم الأفضل 👏",
        brand="Al-Noor Telecom",
        platform="tiktok",
        language="ar"
    )

    assert res["sentiment"] == "negative"
    assert res["is_sarcasm"] is True


def test_classifier_caching(tmp_path, monkeypatch):
    test_cache = tmp_path / "test_cache.json"
    classifier = LLMClassifier(cache_enabled=True)
    classifier.cache_file = test_cache
    classifier._cache = {}

    text = "تجربة ممتازة مع ديزرت باي كاش باك فوري شكرا لكم"
    res1 = classifier.classify(text, brand="DesertPay")
    assert res1.get("_from_cache") is False

    # Second call should hit cache
    res2 = classifier.classify(text, brand="DesertPay")
    assert res2.get("_from_cache") is True
    assert res2["sentiment"] == res1["sentiment"]
