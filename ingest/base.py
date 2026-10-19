"""
Base adapter interface and standardized data structures for social listening ingestion.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import uuid


@dataclass
class RawPost:
    """Standardized representation of an ingested social post or trend record."""
    id: str
    source: str  # youtube, google_trends, tiktok_synthetic, instagram_synthetic, licensed_firehose
    fetch_time: str  # ISO 8601 UTC
    query: str
    raw_json: Dict[str, Any]
    published_at: str  # ISO 8601 UTC
    text: str
    author: str
    url: str
    engagement: Dict[str, int] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RawPost":
        """Reconstruct RawPost from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            source=data.get("source", "unknown"),
            fetch_time=data.get("fetch_time", datetime.now(timezone.utc).isoformat()),
            query=data.get("query", ""),
            raw_json=data.get("raw_json", {}),
            published_at=data.get("published_at", datetime.now(timezone.utc).isoformat()),
            text=data.get("text", ""),
            author=data.get("author", "unknown"),
            url=data.get("url", ""),
            engagement=data.get("engagement", {}),
            metadata=data.get("metadata", {}),
        )


class BaseAdapter(ABC):
    """Abstract base class for all social listening ingestion adapters."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def fetch(self, query: str, limit: int = 50, **kwargs) -> List[RawPost]:
        """
        Fetch posts or signals matching a search query.

        Args:
            query: Brand name, hashtag, or keyword to listen for.
            limit: Maximum number of records to return.
            **kwargs: Adapter-specific parameters (e.g. region, pagination token).

        Returns:
            List of standardized RawPost objects.
        """
        pass

    def now_utc_iso(self) -> str:
        """Utility for current UTC timestamp in ISO 8601."""
        return datetime.now(timezone.utc).isoformat()
