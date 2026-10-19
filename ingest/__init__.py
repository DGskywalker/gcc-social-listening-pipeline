"""
Ingestion package for GCC Social Listening Pipeline.
"""

from ingest.base import BaseAdapter, RawPost
from ingest.youtube_adapter import YouTubeAdapter
from ingest.trends_adapter import GoogleTrendsAdapter
from ingest.synthetic_adapter import SyntheticSocialAdapter
from ingest.licensed_provider import LicensedSocialProviderAdapter

__all__ = [
    "BaseAdapter",
    "RawPost",
    "YouTubeAdapter",
    "GoogleTrendsAdapter",
    "SyntheticSocialAdapter",
    "LicensedSocialProviderAdapter",
]
