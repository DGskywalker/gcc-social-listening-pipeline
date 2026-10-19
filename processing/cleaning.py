"""
Text cleaning, Arabic normalization, and deduplication module.
"""

import hashlib
import re
from typing import List, Tuple, Set
from ingest.base import RawPost


# Arabic character normalization maps
ARABIC_ALEFS = re.compile(r"[إأآا]", re.UNICODE)
ARABIC_TAA_MARBUTA = re.compile(r"ة", re.UNICODE)
ARABIC_YAA = re.compile(r"[ىي]", re.UNICODE)
ARABIC_TASHKEEL = re.compile(r"[\u064B-\u065F\u0670]", re.UNICODE)
ARABIC_TATWEEL = re.compile(r"\u0640", re.UNICODE)
EXCESS_WHITESPACE = re.compile(r"\s+")
URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")


def normalize_arabic(text: str) -> str:
    """
    Normalize Arabic text to standardized baseline for matching and search:
      - Alefs (إ / أ / آ) -> ا
      - Taa Marbuta (ة) -> ه
      - Yaa / Alef Maksura (ى / ي) -> ي
      - Strips Tashkeel (diacritics) and Tatweel (elongation)
    """
    if not text:
        return ""
    # Strip diacritics and elongation
    text = ARABIC_TASHKEEL.sub("", text)
    text = ARABIC_TATWEEL.sub("", text)
    # Normalize orthographic variations
    text = ARABIC_ALEFS.sub("ا", text)
    text = ARABIC_TAA_MARBUTA.sub("ه", text)
    text = ARABIC_YAA.sub("ي", text)
    return text


def clean_text(text: str, remove_urls: bool = False) -> str:
    """
    Clean post text:
      - Preserves emojis (critical for GCC sentiment signal)
      - Trims and collapses multiple spaces/newlines
      - Optionally removes URLs
    """
    if not text:
        return ""
    if remove_urls:
        text = URL_PATTERN.sub("", text)
    # Collapse multiple whitespace characters into single space
    cleaned = EXCESS_WHITESPACE.sub(" ", text).strip()
    return cleaned


def deduplicate_posts(posts: List[RawPost]) -> Tuple[List[RawPost], int]:
    """
    Deduplicate posts based on normalized text content hash.
    Preserves first-seen record and returns (unique_posts, duplicate_count).
    """
    seen_hashes: Set[str] = set()
    unique_posts: List[RawPost] = []
    duplicates_count = 0

    for post in posts:
        # Create deterministic fingerprint using normalized text
        norm_text = normalize_arabic(clean_text(post.text, remove_urls=True)).lower()
        content_hash = hashlib.md5(norm_text.encode("utf-8")).hexdigest()

        if content_hash in seen_hashes:
            duplicates_count += 1
            continue

        seen_hashes.add(content_hash)
        unique_posts.append(post)

    return unique_posts, duplicates_count
