"""
Unit tests for S3 Storage Client using moto (mock AWS S3).
"""

import json
import pytest
from moto import mock_aws
import boto3

from storage.s3_client import S3StorageManager
from ingest.base import RawPost


@pytest.fixture
def mock_s3_environment(monkeypatch):
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test_mock_key")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test_mock_secret")
    monkeypatch.setenv("S3_BUCKET_NAME", "test-gcc-listening-bucket")


@mock_aws
def test_s3_storage_with_moto(mock_s3_environment):
    # Initialize S3 storage inside moto context
    s3_manager = S3StorageManager(
        bucket_name="test-gcc-listening-bucket",
        region_name="us-east-1",
        mock_mode=False,  # Under mock_aws, mock_mode=False exercises real boto3 against moto!
    )

    # Test key building
    raw_key = s3_manager.build_raw_key("tiktok", "2026-10-19", "batch_001.json")
    assert raw_key == "raw/tiktok/2026-10-19/batch_001.json"

    proc_key = s3_manager.build_processed_key("2026-10-19", "summary.json")
    assert proc_key == "processed/2026-10-19/summary.json"

    # Test putting and getting an object
    uri = s3_manager.put_object("raw/test/sample.json", '{"status": "ok"}')
    assert uri == "s3://test-gcc-listening-bucket/raw/test/sample.json"

    content = s3_manager.get_object("raw/test/sample.json")
    assert json.loads(content)["status"] == "ok"

    # Test uploading raw posts
    posts = [
        RawPost(
            id="p1",
            source="tiktok",
            fetch_time="2026-10-19T10:00:00Z",
            query="DesertPay",
            raw_json={"test": 1},
            published_at="2026-10-19T09:00:00Z",
            text="DesertPay cashback is great!",
            author="@user1",
            url="https://tiktok.com/p1",
            engagement={"likes": 50},
        )
    ]

    s3_uri = s3_manager.upload_raw_posts("tiktok", posts, date_str="2026-10-19")
    assert "raw/tiktok/2026-10-19/" in s3_uri

    # Test listing keys
    keys = s3_manager.list_keys(prefix="raw/")
    assert len(keys) >= 2

    # Test downloading all raw posts
    downloaded = s3_manager.download_all_raw(date_str="2026-10-19")
    assert len(downloaded) >= 1
    assert downloaded[0].query == "DesertPay"

    # Test processed upload and download
    records = [{"id": "r1", "brand": "DesertPay", "sentiment": "positive"}]
    p_uri = s3_manager.upload_processed_records(records, date_str="2026-10-19")
    assert "processed/2026-10-19/" in p_uri

    downloaded_proc = s3_manager.download_all_processed(date_str="2026-10-19")
    assert len(downloaded_proc) == 1
    assert downloaded_proc[0]["brand"] == "DesertPay"


def test_s3_guard_against_real_aws_placeholders(monkeypatch):
    """Ensure pipeline refuses to call real AWS if credentials are placeholder defaults."""
    monkeypatch.setenv("MOCK_S3", "false")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "your_aws_access_key_id")
    
    from config import settings
    monkeypatch.setattr(settings, "AWS_ACCESS_KEY_ID", "your_aws_access_key_id")

    with pytest.raises(ValueError, match="valid AWS credentials were not provided"):
        S3StorageManager(mock_mode=False)
