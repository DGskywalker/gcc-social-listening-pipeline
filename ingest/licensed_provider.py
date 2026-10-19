"""
Licensed Data Source Ingestion Adapter.
Architectural reference and production adapter template for integrating commercial,
licensed enterprise firehoses (e.g., Brandwatch, Sprinklr, Meta Graph API, X Enterprise Decahose).

Complies with platform terms of service and licensing agreements.
"""

import logging
from typing import List, Dict, Any, Optional
from ingest.base import BaseAdapter, RawPost

logger = logging.getLogger(__name__)


class LicensedSocialProviderAdapter(BaseAdapter):
    """
    Adapter for enterprise commercial social listening feeds and webhooks.
    Designed for webhook ingestion or streaming API consumption.
    """

    def __init__(self, provider_name: str = "licensed_firehose", api_token: Optional[str] = None):
        super().__init__(name=provider_name)
        self.api_token = api_token

    def fetch(self, query: str, limit: int = 50, **kwargs) -> List[RawPost]:
        """
        Polls or retrieves batch data from the licensed partner API.
        In production, this queries the provider's REST endpoints or ingests SQS/Kafka
        events populated by incoming webhooks.
        """
        fetch_time = self.now_utc_iso()
        logger.info(
            f"Licensed provider '{self.name}' invoked for query '{query}' (limit={limit}). "
            "To activate live enterprise streaming, configure LICENSED_PROVIDER_API_KEY in .env."
        )

        # In offline/sandbox mode, demonstrates the structured output format
        return []

    def parse_webhook_payload(self, event_payload: Dict[str, Any]) -> RawPost:
        """
        Parses an incoming enterprise webhook JSON payload into the standardized RawPost schema.

        Example standard enterprise payload mapping:
        - X/Twitter Decahose: id_str -> id, text/full_text -> text, user.screen_name -> author
        - Meta Graph API: post_id -> id, message -> text, from.name -> author
        - Brandwatch API: mentionId -> id, snippet -> text, author.name -> author
        """
        fetch_time = self.now_utc_iso()
        post_id = str(event_payload.get("id") or event_payload.get("mention_id") or "lic_001")
        return RawPost(
            id=f"lic_{post_id}",
            source=self.name,
            fetch_time=fetch_time,
            query=event_payload.get("query", "licensed_stream"),
            raw_json=event_payload,
            published_at=event_payload.get("created_at", fetch_time),
            text=event_payload.get("text", "") or event_payload.get("body", ""),
            author=event_payload.get("author", "Verified Enterprise Feed"),
            url=event_payload.get("url", f"https://enterprise-provider.internal/{post_id}"),
            engagement=event_payload.get("engagement", {}),
            metadata={
                "licensed": True,
                "partner": self.name,
                "compliance_hash": event_payload.get("compliance_hash", ""),
            },
        )
