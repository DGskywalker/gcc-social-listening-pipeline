"""
Unit tests for Ingestion Adapters (YouTube, Trends, Synthetic).
"""

import pytest
from ingest.base import RawPost
from ingest.youtube_adapter import YouTubeAdapter, YouTubeQuotaExceededException
from ingest.trends_adapter import GoogleTrendsAdapter
from ingest.synthetic_adapter import SyntheticSocialAdapter


def test_youtube_adapter_offline_sample():
    adapter = YouTubeAdapter(api_key="")
    posts = adapter.fetch(query="Al-Noor Telecom", limit=3)
    assert len(posts) == 3
    for p in posts:
        assert isinstance(p, RawPost)
        assert p.source == "youtube"
        assert "Al-Noor" in p.text or "النور" in p.text or len(p.text) > 0
        assert "views" in p.engagement
        assert p.metadata.get("is_synthetic") is True


def test_google_trends_adapter():
    adapter = GoogleTrendsAdapter(geo="SA")
    posts = adapter.fetch(query="DesertPay", limit=7)
    assert len(posts) == 7
    for p in posts:
        assert isinstance(p, RawPost)
        assert p.source == "google_trends"
        assert "search_index" in p.engagement
        assert 0 <= p.engagement["search_index"] <= 100
        assert "unofficial_api_notice" in p.metadata


def test_synthetic_tiktok_adapter():
    adapter = SyntheticSocialAdapter(platform="tiktok")
    posts = adapter.fetch(query="Falcon Ride", limit=5)
    assert len(posts) == 5
    for p in posts:
        assert isinstance(p, RawPost)
        assert p.source == "tiktok_synthetic"
        assert p.metadata.get("is_synthetic") is True
        assert "views" in p.engagement
        assert "likes" in p.engagement
        assert "comments" in p.engagement


def test_synthetic_instagram_adapter():
    adapter = SyntheticSocialAdapter(platform="instagram")
    posts = adapter.fetch(query="Oasis Retail", limit=4)
    assert len(posts) == 4
    for p in posts:
        assert isinstance(p, RawPost)
        assert p.source == "instagram_synthetic"
        assert p.metadata.get("is_synthetic") is True
        assert "likes" in p.engagement
        assert "saves" in p.engagement


def test_raw_post_serialization():
    post = RawPost(
        id="test_01",
        source="test_source",
        fetch_time="2026-10-19T10:00:00Z",
        query="Al-Noor",
        raw_json={"foo": "bar"},
        published_at="2026-10-18T10:00:00Z",
        text="Sample post text",
        author="@test_user",
        url="https://example.com/test",
        engagement={"likes": 10},
        metadata={"region": "SA"},
    )
    d = post.to_dict()
    assert d["id"] == "test_01"
    assert d["source"] == "test_source"
    assert d["engagement"]["likes"] == 10

    reconstructed = RawPost.from_dict(d)
    assert reconstructed.id == post.id
    assert reconstructed.text == post.text
    assert reconstructed.engagement == post.engagement
