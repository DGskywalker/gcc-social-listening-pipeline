# Integrating Licensed Social Data Sources

## Overview

In enterprise social listening (especially within the GCC region), scraping platforms such as Instagram, TikTok, LinkedIn, or X violates platform Terms of Service (ToS) and risks IP blocks, legal action, and brittle data collection.

This pipeline is architected to ingest data legally through two official patterns:
1. **Official Developer APIs** (e.g., YouTube Data API v3, Meta Content Publishing / Graph API).
2. **Licensed Commercial Data Feeds & Firehoses** (e.g., Brandwatch, Sprinklr, Meltwater, X Enterprise Decahose, DataSift/Talkwalker).

For local execution, testing, and continuous integration, high-fidelity **Synthetic Generators** (`ingest/synthetic_adapter.py`) produce compliant GCC social posts without unauthorized scraping.

---

## Architectural Flow for Licensed Providers

```
[ Licensed Provider (Brandwatch / Sprinklr / Decahose) ]
                          │
                          │ (HTTPS Webhook or SQS / Kafka Stream)
                          ▼
            [ Ingestion Microservice / AWS Lambda ]
                          │
                          │ Validates HMAC Signature & Normalizes to RawPost
                          ▼
             [ ingest/licensed_provider.py ]
                          │
                          │ Partitions and Writes to S3 Raw Zone
                          ▼
            [ s3://bucket/raw/<source>/<YYYY-MM-DD>/... ]
```

---

## Implementation Guide

To plug a licensed provider into this pipeline:

### 1. Extend `BaseAdapter`
Implement `BaseAdapter` from `ingest/base.py` as demonstrated in `ingest/licensed_provider.py`:

```python
from ingest.base import BaseAdapter, RawPost

class BrandwatchAdapter(BaseAdapter):
    def __init__(self, api_token: str, project_id: str):
        super().__init__(name="brandwatch")
        self.api_token = api_token
        self.project_id = project_id

    def fetch(self, query: str, limit: int = 50, **kwargs) -> List[RawPost]:
        # Call Brandwatch Query API v2
        headers = {"Authorization": f"Bearer {self.api_token}"}
        response = requests.get(
            f"https://api.brandwatch.com/projects/{self.project_id}/data/mentions",
            params={"query": query, "pageSize": limit},
            headers=headers
        )
        response.raise_for_status()
        mentions = response.json().get("results", [])
        return [self._map_mention(m, query) for m in mentions]
```

### 2. Map Payload to `RawPost`
Standardize the provider's fields:
- `id`: Provider's immutable mention ID.
- `source`: Platform identity (e.g., `brandwatch`, `decahose`).
- `fetch_time`: Current UTC timestamp (`now_utc_iso()`).
- `query`: Target search keyword, hashtag, or boolean topic query.
- `raw_json`: **The complete, unadulterated provider response payload** for archival and replay.
- `published_at`: Original author publication timestamp.
- `text`: Post caption, tweet, or message body.
- `author`: Author handle or anonymized ID.
- `url`: Direct canonical URL.
- `engagement`: Dictionary of likes, shares, impressions, retweets, views.
- `metadata`: Licensed metadata, language tags, sentiment flags.

### 3. Webhook Ingestion Mode (Push vs Poll)
For real-time feeds (e.g. Meta Webhooks or Sprinklr Webhooks):
1. Configure an API Gateway + AWS Lambda endpoint.
2. Verify the provider's webhook signature (HMAC-SHA256).
3. Call `LicensedSocialProviderAdapter.parse_webhook_payload(payload)`.
4. Upload directly to S3 under `raw/licensed/<YYYY-MM-DD>/<id>.json`.

---

## Compliance & Governance Best Practices
1. **Right to be Forgotten (GDPR / Saudi PDPL)**: Store provider mention IDs. If a user deletes their tweet or post, commercial providers emit deletion events. The S3 cleaner removes or anonymizes the corresponding record from both raw and processed zones.
2. **Access Control**: S3 raw data contains user handles; ensure the S3 bucket has SSE-KMS encryption and IAM policies restricting access to authorized data engineering roles.
