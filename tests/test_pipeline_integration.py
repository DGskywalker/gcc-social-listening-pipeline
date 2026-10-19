"""
End-to-end integration test for the GCC Social Listening Pipeline.
Exercises: Ingestion -> Moto S3 Storage -> Cleaning & Tagging -> S3 Processed Lake -> Dashboard Export.
"""

import pytest
from moto import mock_aws
from storage.s3_client import S3StorageManager
from run_pipeline import run_ingestion_stage, run_processing_stage
from scripts.generate_dashboard_data import generate_dashboard_dataset


@mock_aws
def test_full_pipeline_flow(tmp_path, monkeypatch):
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test_id")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test_secret")
    monkeypatch.setenv("S3_BUCKET_NAME", "integration-test-bucket")
    monkeypatch.setenv("LLM_PROVIDER", "mock")

    s3_manager = S3StorageManager(
        bucket_name="integration-test-bucket",
        region_name="us-east-1",
        mock_mode=False,
    )

    # 1. Ingestion Stage
    test_brands = ["Al-Noor Telecom", "DesertPay"]
    uploaded_uris = run_ingestion_stage(s3_manager, test_brands)
    assert len(uploaded_uris) > 0

    # 2. Processing Stage
    proc_uri = run_processing_stage(s3_manager)
    assert "processed/" in proc_uri

    # 3. Verify S3 processed records
    processed_records = s3_manager.download_all_processed()
    assert len(processed_records) > 0
    for r in processed_records:
        assert "sentiment" in r
        assert "primary_theme" in r
        assert "brand" in r
        assert "language" in r

    # 4. Dashboard Data Export
    bundle = generate_dashboard_dataset()
    assert "metadata" in bundle
    assert "posts" in bundle
    assert "executive_summary" in bundle
    assert len(bundle["posts"]) >= 150
