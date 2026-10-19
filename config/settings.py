"""
Configuration and settings for GCC Social Listening Pipeline.
Supports local mock S3 (via moto or local filesystem), LocalStack, or real AWS S3.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# --- Environment & Storage Settings ---
APP_ENV = os.getenv("APP_ENV", "development")  # development, test, production
MOCK_S3 = os.getenv("MOCK_S3", "true").lower() in ("true", "1", "yes")
USE_LOCALSTACK = os.getenv("USE_LOCALSTACK", "false").lower() in ("true", "1", "yes")

# AWS Credentials (do not commit real values)
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "mock_key_id")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "mock_secret_key")
AWS_REGION = os.getenv("AWS_REGION", "me-central-1")  # Default to GCC region (UAE)
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "gcc-social-listening-bucket")
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL", None)

# If USE_LOCALSTACK is true and no endpoint set, point to default LocalStack URL
if USE_LOCALSTACK and not S3_ENDPOINT_URL:
    S3_ENDPOINT_URL = "http://localhost:4566"

# Local storage path fallback for zero-cloud runs
LOCAL_STORAGE_DIR = BASE_DIR / "local_storage"

# --- API Keys ---
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock")  # "gemini", "openai", "mock"
LLM_CACHE_ENABLED = os.getenv("LLM_CACHE_ENABLED", "true").lower() in ("true", "1", "yes")
LLM_CACHE_FILE = BASE_DIR / ".cache" / "llm_cache.json"

# Logging & Alerts
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = BASE_DIR / "logs"
ALERT_LOG_FILE = LOG_DIR / "alerts.log"
PIPELINE_LOG_FILE = LOG_DIR / "pipeline.log"

# Default brands tracked
DEFAULT_BRANDS = [
    "Al-Noor Telecom",
    "DesertPay",
    "Oasis Retail",
    "Falcon Ride",
    "GulfCloud"
]

# Ensure required local directories exist
LOG_DIR.mkdir(parents=True, exist_ok=True)
(BASE_DIR / ".cache").mkdir(parents=True, exist_ok=True)
LOCAL_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
