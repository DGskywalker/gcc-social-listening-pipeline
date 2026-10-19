"""
Unified CLI Entrypoint for the GCC Social Listening Pipeline.
Orchestrates: Ingestion -> AWS S3 Lakehouse -> Cleaning & Tagging -> Validation -> Dashboard.

Usage:
    python run_pipeline.py --all
    python run_pipeline.py --ingest
    python run_pipeline.py --process
    python run_pipeline.py --validate
    python run_pipeline.py --dashboard
"""

import argparse
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List

# Ensure base directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config import settings
from ingest.youtube_adapter import YouTubeAdapter
from ingest.trends_adapter import GoogleTrendsAdapter
from ingest.synthetic_adapter import SyntheticSocialAdapter
from storage.s3_client import S3StorageManager
from processing.cleaning import clean_text, deduplicate_posts
from processing.language import detect_language
from processing.brand_tagger import BrandTagger
from processing.topic_tagger import TopicTagger
from processing.llm_classifier import LLMClassifier
from schedule.alert_manager import alert_manager
from scripts.validate_model import run_validation
from scripts.generate_dashboard_data import generate_dashboard_dataset

# Configure console logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("pipeline")


def run_ingestion_stage(s3_manager: S3StorageManager, brands: List[str]) -> List[str]:
    """Execute all ingestion adapters and upload raw posts to S3 raw zone."""
    logger.info("=" * 60)
    logger.info("STAGE 1: INGESTION & S3 LAKEHOUSE UPLOAD")
    logger.info("=" * 60)

    yt_adapter = YouTubeAdapter()
    trends_adapter = GoogleTrendsAdapter(geo="SA")
    tiktok_adapter = SyntheticSocialAdapter(platform="tiktok")
    insta_adapter = SyntheticSocialAdapter(platform="instagram")

    uploaded_uris = []
    total_posts = 0

    for brand in brands:
        logger.info(f"Ingesting signals for target brand: '{brand}'")
        try:
            # 1. YouTube
            yt_posts = yt_adapter.fetch(brand, limit=4)
            if yt_posts:
                uri = s3_manager.upload_raw_posts("youtube", yt_posts)
                uploaded_uris.append(uri)
                total_posts += len(yt_posts)

            # 2. Google Trends
            trends_posts = trends_adapter.fetch(brand, limit=14)
            if trends_posts:
                uri = s3_manager.upload_raw_posts("google_trends", trends_posts)
                uploaded_uris.append(uri)
                total_posts += len(trends_posts)

            # 3. TikTok (Synthetic compliant)
            tiktok_posts = tiktok_adapter.fetch(brand, limit=10)
            if tiktok_posts:
                uri = s3_manager.upload_raw_posts("tiktok_synthetic", tiktok_posts)
                uploaded_uris.append(uri)
                total_posts += len(tiktok_posts)

            # 4. Instagram (Synthetic compliant)
            insta_posts = insta_adapter.fetch(brand, limit=10)
            if insta_posts:
                uri = s3_manager.upload_raw_posts("instagram_synthetic", insta_posts)
                uploaded_uris.append(uri)
                total_posts += len(insta_posts)

        except Exception as e:
            alert_manager.error("ingestion", f"Failed ingestion for brand '{brand}': {e}")
            logger.error(f"Error during ingestion for {brand}: {e}")

    logger.info(f"Ingestion Stage Complete: {total_posts} raw posts ingested across {len(uploaded_uris)} S3 batches.")
    return uploaded_uris


def run_processing_stage(s3_manager: S3StorageManager) -> str:
    """Download raw data from S3, clean, deduplicate, tag, and upload to S3 processed zone."""
    logger.info("=" * 60)
    logger.info("STAGE 2: CLEANING, DEDUPLICATION & AI/LLM TAGGING")
    logger.info("=" * 60)

    raw_posts = s3_manager.download_all_raw()
    logger.info(f"Retrieved {len(raw_posts)} raw posts from S3 raw zone.")

    if not raw_posts:
        logger.warning("No raw posts found in S3. Please run ingestion first.")
        return ""

    # Deduplicate
    unique_posts, dupe_count = deduplicate_posts(raw_posts)
    logger.info(f"Deduplication complete: {len(unique_posts)} unique posts ({dupe_count} duplicates removed).")

    # Initialize NLP & LLM taggers
    brand_tagger = BrandTagger()
    topic_tagger = TopicTagger()
    classifier = LLMClassifier()

    processed_records = []

    for post in unique_posts:
        cleaned = clean_text(post.text)
        lang = detect_language(cleaned)
        b_info = brand_tagger.tag_brands(cleaned)
        primary_brand = b_info["primary_brand"] or post.metadata.get("target_brand") or "Al-Noor Telecom"

        # LLM classification with caching and retry
        llm_res = classifier.classify(
            text=cleaned,
            brand=primary_brand,
            platform=post.source,
            language=lang,
        )

        record = {
            "id": post.id,
            "source": post.source,
            "published_at": post.published_at,
            "date": post.published_at[:10],
            "text": cleaned,
            "author": post.author,
            "url": post.url,
            "language": lang,
            "brand": primary_brand,
            "sentiment": llm_res["sentiment"],
            "sentiment_score": llm_res["sentiment_score"],
            "primary_theme": llm_res["primary_theme"],
            "secondary_theme": llm_res["secondary_theme"],
            "confidence": llm_res["confidence"],
            "is_sarcasm": llm_res["is_sarcasm"],
            "dialect": llm_res["dialect"],
            "engagement": post.engagement,
            "is_synthetic": post.metadata.get("is_synthetic", True),
        }
        processed_records.append(record)

    # Upload to S3 processed zone
    processed_uri = s3_manager.upload_processed_records(processed_records)
    logger.info(f"Processing Stage Complete: {len(processed_records)} records saved to {processed_uri}")
    return processed_uri


def main():
    parser = argparse.ArgumentParser(description="GCC Social Listening Pipeline CLI")
    parser.add_argument("--all", action="store_true", help="Execute complete end-to-end pipeline")
    parser.add_argument("--ingest", action="store_true", help="Run ingestion adapters and S3 upload")
    parser.add_argument("--process", action="store_true", help="Run cleaning, deduplication, and AI tagging")
    parser.add_argument("--validate", action="store_true", help="Run validation against 150 gold items")
    parser.add_argument("--dashboard", action="store_true", help="Export processed data for dashboard")
    parser.add_argument("--mock", action="store_true", default=None, help="Force mock S3 mode")

    args = parser.parse_args()

    # Default to --all if no specific stage requested
    if not any([args.all, args.ingest, args.process, args.validate, args.dashboard]):
        args.all = True

    start_time = time.time()
    logger.info("Starting GCC Social Listening Pipeline...")
    logger.info(f"Target GCC Brands: {', '.join(settings.DEFAULT_BRANDS)}")

    # Initialize S3 Lakehouse Manager (Mock or AWS)
    mock_override = True if args.mock else None
    s3_manager = S3StorageManager(mock_mode=mock_override)

    try:
        if args.all or args.ingest:
            run_ingestion_stage(s3_manager, settings.DEFAULT_BRANDS)

        if args.all or args.process:
            run_processing_stage(s3_manager)

        if args.all or args.validate:
            logger.info("=" * 60)
            logger.info("STAGE 3: MODEL VALIDATION AGAINST 150 GOLD BENCHMARK")
            logger.info("=" * 60)
            run_validation()

        if args.all or args.dashboard:
            logger.info("=" * 60)
            logger.info("STAGE 4: DASHBOARD DATA EXPORT")
            logger.info("=" * 60)
            generate_dashboard_dataset()

        elapsed = time.time() - start_time
        logger.info("=" * 60)
        logger.info(f"🎉 PIPELINE EXECUTION SUCCESSFUL (Total Time: {elapsed:.2f}s)")
        logger.info(f"Dashboard available at: file://{BASE_DIR / 'dashboard' / 'index.html'}")
        logger.info(f"Validation report at: file://{BASE_DIR / 'docs' / 'VALIDATION.md'}")
        logger.info("=" * 60)

    except Exception as e:
        alert_manager.critical("pipeline_main", f"Fatal pipeline failure: {e}")
        logger.exception("Pipeline run aborted due to error.")
        sys.exit(1)


if __name__ == "__main__":
    main()
