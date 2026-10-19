"""
Unit tests for Processing Components (Cleaning, Deduplication, Language, Brand, Topic).
"""

import pytest
from ingest.base import RawPost
from processing.cleaning import normalize_arabic, clean_text, deduplicate_posts
from processing.language import detect_language
from processing.brand_tagger import BrandTagger
from processing.topic_tagger import TopicTagger


def test_arabic_normalization():
    # Alef variations
    assert normalize_arabic("أحمد وإبراهيم والآن") == "احمد وابراهيم والان"
    # Taa Marbuta
    assert normalize_arabic("خدمة ممتازة للشركة") == "خدمه ممتازه للشركه"
    # Tashkeel and Tatweel
    assert normalize_arabic("مُـمْـتَـازٌ") == "ممتاز"


def test_text_cleaning():
    text = "  تجربة    ممتازة https://example.com/test  مع  النور!   "
    cleaned = clean_text(text, remove_urls=True)
    assert cleaned == "تجربة ممتازة مع النور!"
    assert "https" not in cleaned


def test_deduplicate_posts():
    p1 = RawPost(id="1", source="tiktok", fetch_time="t", query="q", raw_json={}, published_at="p", text="عرض رائع من ديزرت باي", author="a", url="u")
    p2 = RawPost(id="2", source="tiktok", fetch_time="t", query="q", raw_json={}, published_at="p", text="عرض رائع من ديزرت باي  ", author="b", url="u")
    p3 = RawPost(id="3", source="tiktok", fetch_time="t", query="q", raw_json={}, published_at="p", text="عرض رائع من النور للاتصالات", author="c", url="u")

    unique, dupes = deduplicate_posts([p1, p2, p3])
    assert len(unique) == 2
    assert dupes == 1
    assert unique[0].id == "1"
    assert unique[1].id == "3"


def test_language_detection():
    # Pure Arabic
    assert detect_language("تغطية شبكة النور ممتازة في شمال الرياض") == "ar"
    # Pure English
    assert detect_language("Falcon Ride surge pricing in Dubai is completely unreasonable today.") == "en"
    # Mixed Code-Switching
    assert detect_language("شباب الـ 5G حق النور صار so slow اليومين ذي شالسالفة؟") == "mixed"
    assert detect_language("The new update for DesertPay app معلق عندي") == "mixed"


def test_brand_tagger():
    tagger = BrandTagger()

    # Arabic alias
    res1 = tagger.tag_brands("تغطية شركة النور للاتصالات في الرياض")
    assert "Al-Noor Telecom" in res1["brands"]
    assert res1["primary_brand"] == "Al-Noor Telecom"

    # Handle & Hashtag
    res2 = tagger.tag_brands("كاش باك ممتاز من @DesertPay #ديزرت_باي")
    assert "DesertPay" in res2["brands"]

    # English name
    res3 = tagger.tag_brands("Ordered fresh fruit from Oasis Retail in Dubai")
    assert "Oasis Retail" in res3["brands"]

    # Falcon Ride
    res4 = tagger.tag_brands("كابتن صقر رايد ما وصل للآن")
    assert "Falcon Ride" in res4["brands"]

    # GulfCloud
    res5 = tagger.tag_brands("استضافة مواقع على سحابة الخليج GulfCloud")
    assert "GulfCloud" in res5["brands"]


def test_topic_tagger():
    tagger = TopicTagger()

    # Network Outage
    res1 = tagger.tag_topics("انقطاع خدمة الألياف البصرية وضعف شبكة الفايف جي")
    assert res1["primary_theme"] == "Network & Outage"

    # Customer Support
    res2 = tagger.tag_topics("خدمة العملاء والدعم الفني ما يردون على الشكوى")
    assert res2["primary_theme"] == "Customer Support"

    # Pricing & Billing
    res3 = tagger.tag_topics("Falcon Ride surge pricing is 2.8x double fare bill")
    assert res3["primary_theme"] == "Pricing & Billing"

    # Delivery & Logistics
    res4 = tagger.tag_topics("مندوب التوصيل تأخر ساعتين والطلب وصل ذايب")
    assert res4["primary_theme"] == "Delivery & Logistics"

    # Promotions & Offers
    res5 = tagger.tag_topics("كود خصم 30% مع كاش باك إضافي بمناسبة رمضان")
    assert res5["primary_theme"] == "Promotions & Offers"
