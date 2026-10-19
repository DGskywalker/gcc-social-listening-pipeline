"""
YouTube Data API v3 Ingestion Adapter.
Official Google API client with pagination, quota handling, and robust fallback.
"""

import logging
from typing import List, Dict, Any, Optional
import requests
from config import settings
from ingest.base import BaseAdapter, RawPost

logger = logging.getLogger(__name__)


class YouTubeQuotaExceededException(Exception):
    """Raised when YouTube Data API quota has been reached."""
    pass


class YouTubeAdapter(BaseAdapter):
    """
    Adapter for official YouTube Data API v3.
    Searches videos/shorts matching queries within GCC target regions (SA, AE, KW).
    Handles pagination, rate limits, quota errors, and stores complete raw JSON.
    """

    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(name="youtube")
        self.api_key = api_key or settings.YOUTUBE_API_KEY

    def fetch(
        self,
        query: str,
        limit: int = 25,
        region_code: str = "SA",
        relevance_language: str = "ar",
        **kwargs
    ) -> List[RawPost]:
        """
        Fetch YouTube videos matching the query.
        If no API key is provided, returns high-fidelity fallback items for offline testing.
        """
        fetch_time = self.now_utc_iso()

        if not self.api_key:
            logger.warning(
                "No YOUTUBE_API_KEY provided in environment. "
                "Returning mock YouTube data for offline demonstration."
            )
            return self._generate_offline_sample(query, limit, fetch_time, region_code)

        results: List[RawPost] = []
        next_page_token = kwargs.get("page_token", None)
        remaining = limit

        while remaining > 0:
            batch_size = min(remaining, 50)  # Max allowed per YouTube search page
            params = {
                "part": "snippet",
                "q": query,
                "type": "video",
                "maxResults": batch_size,
                "regionCode": region_code,
                "relevanceLanguage": relevance_language,
                "key": self.api_key,
            }
            if next_page_token:
                params["pageToken"] = next_page_token

            try:
                resp = requests.get(f"{self.BASE_URL}/search", params=params, timeout=10)
                
                # Check for quota errors
                if resp.status_code == 403:
                    err_json = resp.json().get("error", {})
                    errors = err_json.get("errors", [{}])
                    reason = errors[0].get("reason", "") if errors else ""
                    if reason in ("quotaExceeded", "dailyLimitExceeded", "rateLimitExceeded"):
                        logger.error(f"YouTube API quota exceeded: {reason}")
                        raise YouTubeQuotaExceededException(f"YouTube API quota reached: {reason}")
                    resp.raise_for_status()

                resp.raise_for_status()
                data = resp.json()
            except requests.RequestException as e:
                logger.error(f"Error fetching from YouTube API: {e}")
                # Fallback gracefully if network or quota issue in demo mode
                if not results:
                    return self._generate_offline_sample(query, limit, fetch_time, region_code)
                break

            items = data.get("items", [])
            if not items:
                break

            video_ids = [
                item["id"]["videoId"]
                for item in items
                if "videoId" in item.get("id", {})
            ]

            # Fetch video statistics (views, likes, comments)
            stats_map = self._fetch_video_stats(video_ids)

            for item in items:
                video_id = item.get("id", {}).get("videoId")
                if not video_id:
                    continue
                snippet = item.get("snippet", {})
                title = snippet.get("title", "")
                desc = snippet.get("description", "")
                stats = stats_map.get(video_id, {})

                raw_post = RawPost(
                    id=f"yt_{video_id}",
                    source=self.name,
                    fetch_time=fetch_time,
                    query=query,
                    raw_json=item,
                    published_at=snippet.get("publishedAt", fetch_time),
                    text=f"{title}\n{desc}".strip(),
                    author=snippet.get("channelTitle", "Unknown Channel"),
                    url=f"https://www.youtube.com/watch?v={video_id}",
                    engagement={
                        "views": int(stats.get("viewCount", 0)),
                        "likes": int(stats.get("likeCount", 0)),
                        "comments": int(stats.get("commentCount", 0)),
                    },
                    metadata={
                        "region_code": region_code,
                        "channel_id": snippet.get("channelId", ""),
                        "is_synthetic": False,
                    },
                )
                results.append(raw_post)

            remaining -= len(items)
            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break

        return results

    def _fetch_video_stats(self, video_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Fetch statistics (viewCount, likeCount, commentCount) for video IDs."""
        if not video_ids or not self.api_key:
            return {}
        try:
            params = {
                "part": "statistics",
                "id": ",".join(video_ids[:50]),
                "key": self.api_key,
            }
            resp = requests.get(f"{self.BASE_URL}/videos", params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    item["id"]: item.get("statistics", {})
                    for item in data.get("items", [])
                }
        except Exception as e:
            logger.warning(f"Failed to fetch video statistics: {e}")
        return {}

    def _generate_offline_sample(
        self, query: str, limit: int, fetch_time: str, region_code: str
    ) -> List[RawPost]:
        """Offline high-fidelity sample for YouTube when API key is unavailable."""
        samples = [
            (
                "yt_mock_001",
                "مراجعة تغطية وسرعة 5G من النور للاتصالات في الرياض | تجربة واقعية",
                "تجربة سرعة 5G مع Al-Noor Telecom في شمال الرياض، القياس وصل إلى 850 ميجابت ولكن في بعض الأحياء التغطية تقطع.",
                "تقنية الخليج | Gulf Tech",
                {"views": 45200, "likes": 2340, "comments": 412},
            ),
            (
                "yt_mock_002",
                "مقارنة المحافظ الرقمية في السعودية 2026: ديزرت باي DesertPay مقابل المنافسين",
                "فيديو تفصيلي عن رسوم التحويل الدولي ومميزات الكاش باك في تطبيق DesertPay وعروض اليوم الوطني.",
                "سعودي بودكاست مالي",
                {"views": 32100, "likes": 1820, "comments": 298},
            ),
            (
                "yt_mock_003",
                "تجربة تسوق وتوصيل من واحة التجزئة Oasis Retail في دبي",
                "طلبنا مقاضي البيت عبر تطبيق Oasis Retail، التوصيل استغرق أقل من ساعتين والأسعار مناسبة جداً.",
                "دبي لايف ستايل",
                {"views": 18900, "likes": 980, "comments": 85},
            ),
            (
                "yt_mock_004",
                "Falcon Ride App Review: Ride Hailing Price Surge Analysis in Riyadh",
                "Testing Falcon Ride vs competitors during peak hours in Boulevard Riyadh City. Surge multiplier was 1.8x.",
                "Riyadh Urban Mobility",
                {"views": 27400, "likes": 1410, "comments": 194},
            ),
            (
                "yt_mock_005",
                "شرح خدمات سحابة الخليج GulfCloud لرواد الأعمال والشركات الناشئة",
                "كيف تستفيد من مراكز البيانات المحلية لـ GulfCloud في المملكة لضمان الامتثال لضوابط الأمن السيبراني.",
                "عالم السحابة العربية",
                {"views": 12800, "likes": 760, "comments": 63},
            ),
        ]

        posts = []
        for i in range(min(limit, len(samples))):
            sid, title, desc, channel, stats = samples[i]
            posts.append(
                RawPost(
                    id=sid,
                    source=self.name,
                    fetch_time=fetch_time,
                    query=query,
                    raw_json={
                        "kind": "youtube#searchResult",
                        "id": {"videoId": sid},
                        "snippet": {"title": title, "description": desc, "channelTitle": channel},
                        "statistics": stats,
                        "_mock_note": "Sample response generated because YOUTUBE_API_KEY was not configured",
                    },
                    published_at="2026-10-18T14:30:00Z",
                    text=f"{title}\n{desc}",
                    author=channel,
                    url=f"https://www.youtube.com/watch?v={sid}",
                    engagement=stats,
                    metadata={"region_code": region_code, "is_synthetic": True},
                )
            )
        return posts
