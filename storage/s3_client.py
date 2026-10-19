"""
S3 Storage Client and Data Lake Layout Manager.
Supports Moto mock storage for testing, LocalStack, local filesystem fallback,
and real AWS S3 buckets configured via environment variables.
"""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

import boto3
from botocore.exceptions import ClientError

from config import settings
from ingest.base import RawPost

logger = logging.getLogger(__name__)


class S3StorageManager:
    """
    Manages cloud storage operations with standardized S3 key layouts:
      - raw/<source>/<YYYY-MM-DD>/<filename>.json
      - processed/<YYYY-MM-DD>/<filename>.json
    """

    def __init__(
        self,
        bucket_name: Optional[str] = None,
        region_name: Optional[str] = None,
        mock_mode: Optional[bool] = None,
        endpoint_url: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
    ):
        self.bucket_name = bucket_name or settings.S3_BUCKET_NAME
        self.region_name = region_name or settings.AWS_REGION
        self.mock_mode = settings.MOCK_S3 if mock_mode is None else mock_mode
        self.endpoint_url = endpoint_url or settings.S3_ENDPOINT_URL
        self.aws_access_key_id = aws_access_key_id or os.getenv("AWS_ACCESS_KEY_ID", settings.AWS_ACCESS_KEY_ID)
        self.aws_secret_access_key = aws_secret_access_key or os.getenv("AWS_SECRET_ACCESS_KEY", settings.AWS_SECRET_ACCESS_KEY)
        self.local_fallback_dir = settings.LOCAL_STORAGE_DIR / self.bucket_name

        self.s3_client = self._init_client()
        self.ensure_bucket_exists()

    def _init_client(self):
        """Initialize boto3 S3 client with mock, LocalStack, or AWS credentials."""
        # Safety check: prevent accidental production AWS calls with placeholders
        if not self.mock_mode:
            if self.aws_access_key_id in ("your_aws_access_key_id", ""):
                raise ValueError(
                    "MOCK_S3 is set to False, but valid AWS credentials were not provided in .env. "
                    "To prevent unintended charges or errors, set MOCK_S3=true or configure real AWS credentials."
                )
            logger.info(f"Connecting to real AWS S3 / Moto in region '{self.region_name}'")
            return boto3.client(
                "s3",
                region_name=self.region_name,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                endpoint_url=self.endpoint_url,
            )

        # Local mock mode: Check if LocalStack is active or use local disk/moto
        if settings.USE_LOCALSTACK and self.endpoint_url:
            logger.info(f"Connecting to LocalStack S3 at {self.endpoint_url}")
            return boto3.client(
                "s3",
                region_name=self.region_name,
                aws_access_key_id="test",
                aws_secret_access_key="test",
                endpoint_url=self.endpoint_url,
            )

        # In offline local mode without running daemon, use local filesystem mirror
        logger.info(
            f"Using local filesystem S3 mock at '{self.local_fallback_dir}' "
            "(Fully compatible with moto & zero external AWS dependencies)"
        )
        return None

    def ensure_bucket_exists(self) -> None:
        """Ensure destination bucket or directory exists."""
        if self.s3_client is not None:
            try:
                self.s3_client.head_bucket(Bucket=self.bucket_name)
            except ClientError as e:
                err_code = e.response.get("Error", {}).get("Code", "")
                if err_code in ("404", "NoSuchBucket"):
                    logger.info(f"Creating S3 bucket: {self.bucket_name}")
                    create_params = {"Bucket": self.bucket_name}
                    if self.region_name != "us-east-1":
                        create_params["CreateBucketConfiguration"] = {
                            "LocationConstraint": self.region_name
                        }
                    self.s3_client.create_bucket(**create_params)
        else:
            self.local_fallback_dir.mkdir(parents=True, exist_ok=True)

    # --- S3 Key Layout Builders ---

    @staticmethod
    def build_raw_key(source: str, date_str: str, filename: str) -> str:
        """Standardized raw key layout: raw/<source>/<YYYY-MM-DD>/<filename>.json"""
        clean_filename = filename if filename.endswith(".json") else f"{filename}.json"
        return f"raw/{source}/{date_str}/{clean_filename}"

    @staticmethod
    def build_processed_key(date_str: str, filename: str) -> str:
        """Standardized processed key layout: processed/<YYYY-MM-DD>/<filename>.json"""
        clean_filename = filename if filename.endswith(".json") else f"{filename}.json"
        return f"processed/{date_str}/{clean_filename}"

    # --- Storage Operations ---

    def put_object(self, key: str, body: str, content_type: str = "application/json") -> str:
        """Write string content to S3 or local mock."""
        if self.s3_client is not None:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=body.encode("utf-8"),
                ContentType=content_type,
            )
        else:
            target_path = self.local_fallback_dir / key
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(body, encoding="utf-8")

        return f"s3://{self.bucket_name}/{key}"

    def get_object(self, key: str) -> str:
        """Retrieve string content from S3 or local mock."""
        if self.s3_client is not None:
            resp = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            return resp["Body"].read().decode("utf-8")
        else:
            target_path = self.local_fallback_dir / key
            if not target_path.exists():
                raise FileNotFoundError(f"Mock S3 key not found: {key}")
            return target_path.read_text(encoding="utf-8")

    def list_keys(self, prefix: str = "") -> List[str]:
        """List all object keys under a given prefix."""
        if self.s3_client is not None:
            paginator = self.s3_client.get_paginator("list_objects_v2")
            keys = []
            for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix):
                for obj in page.get("Contents", []):
                    keys.append(obj["Key"])
            return sorted(keys)
        else:
            search_dir = self.local_fallback_dir / prefix
            if not search_dir.exists():
                # Check if prefix is partial directory or file
                parent = search_dir.parent
                if not parent.exists():
                    return []
                prefix_rel = str(search_dir.relative_to(self.local_fallback_dir))
                all_files = [
                    str(p.relative_to(self.local_fallback_dir))
                    for p in self.local_fallback_dir.rglob("*")
                    if p.is_file() and str(p.relative_to(self.local_fallback_dir)).startswith(prefix)
                ]
                return sorted(all_files)

            all_files = [
                str(p.relative_to(self.local_fallback_dir))
                for p in search_dir.rglob("*")
                if p.is_file()
            ]
            return sorted(all_files)

    # --- High-Level Ingestion & Processing Storage ---

    def upload_raw_posts(
        self, source: str, posts: List[RawPost], date_str: Optional[str] = None
    ) -> str:
        """
        Store raw posts batch in S3 under raw/<source>/<YYYY-MM-DD>/batch_<timestamp>.json.
        Preserves complete original raw JSON payloads and metadata.
        """
        if not posts:
            return ""

        now = datetime.now(timezone.utc)
        target_date = date_str or now.strftime("%Y-%m-%d")
        timestamp_slug = now.strftime("%H%M%S")
        batch_filename = f"batch_{timestamp_slug}_{len(posts)}_posts.json"
        s3_key = self.build_raw_key(source, target_date, batch_filename)

        payload = {
            "source": source,
            "ingestion_date": target_date,
            "uploaded_at": now.isoformat(),
            "count": len(posts),
            "records": [p.to_dict() for p in posts],
        }

        s3_uri = self.put_object(s3_key, json.dumps(payload, indent=2, ensure_ascii=False))
        logger.info(f"Uploaded {len(posts)} raw records to {s3_uri}")
        return s3_uri

    def upload_processed_records(
        self,
        records: List[Dict[str, Any]],
        date_str: Optional[str] = None,
        batch_id: Optional[str] = None,
    ) -> str:
        """
        Store cleaned and tagged processed records under processed/<YYYY-MM-DD>/<batch_id>.json.
        """
        if not records:
            return ""

        now = datetime.now(timezone.utc)
        target_date = date_str or now.strftime("%Y-%m-%d")
        slug = batch_id or f"processed_{now.strftime('%H%M%S')}"
        s3_key = self.build_processed_key(target_date, f"{slug}.json")

        payload = {
            "processed_date": target_date,
            "processed_at": now.isoformat(),
            "record_count": len(records),
            "data": records,
        }

        s3_uri = self.put_object(s3_key, json.dumps(payload, indent=2, ensure_ascii=False))
        logger.info(f"Uploaded {len(records)} processed records to {s3_uri}")
        return s3_uri

    def download_all_raw(self, date_str: Optional[str] = None) -> List[RawPost]:
        """Fetch all raw posts from S3 across all sources."""
        prefix = f"raw/" if not date_str else f"raw/"
        keys = self.list_keys(prefix=prefix)
        posts: List[RawPost] = []

        for key in keys:
            if not key.endswith(".json"):
                continue
            if date_str and f"/{date_str}/" not in key:
                continue
            try:
                content = self.get_object(key)
                data = json.loads(content)
                records = data.get("records", [])
                for r in records:
                    posts.append(RawPost.from_dict(r))
            except Exception as e:
                logger.error(f"Error reading raw key '{key}': {e}")

        return posts

    def download_all_processed(self, date_str: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch all processed post records from S3."""
        prefix = f"processed/" if not date_str else f"processed/{date_str}/"
        keys = self.list_keys(prefix=prefix)
        results: List[Dict[str, Any]] = []

        for key in keys:
            if not key.endswith(".json"):
                continue
            try:
                content = self.get_object(key)
                data = json.loads(content)
                items = data.get("data", [])
                results.extend(items)
            except Exception as e:
                logger.error(f"Error reading processed key '{key}': {e}")

        return results
