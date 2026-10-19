"""
Synthetic Ingestion Adapters for TikTok- and Instagram-style posts.
Generates realistic GCC social media conversations in Arabic (dialects + MSA) and English,
complete with engagement metrics, timestamps, hashtags, and brand mentions.

Allows the pipeline to run end-to-end without scraping platforms that prohibit automated access,
fulfilling compliance and ethical data ingestion best practices.
"""

import hashlib
import random
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from ingest.base import BaseAdapter, RawPost


# --- Realistic GCC Social Media Templates ---

POST_TEMPLATES = [
    # --- Al-Noor Telecom (Telecom, 5G, Fiber, Customer Service) ---
    {
        "brand": "Al-Noor Telecom",
        "platform": "tiktok",
        "lang": "ar",
        "sentiment": "negative",
        "theme": "Network & Outage",
        "text": "يا جماعة شبكة النور للاتصالات في حي الياسمين شمال الرياض فاصلة تماماً من الصباح! كل ما نكلم الدعم يقولون تحديث برج. أحد عنده نفس المشكلة؟ 😡📡 #النور_للاتصالات #الرياض #انقطاع_النت",
        "author": "@riyadh_tech_guy",
    },
    {
        "brand": "Al-Noor Telecom",
        "platform": "instagram",
        "lang": "ar",
        "sentiment": "positive",
        "theme": "Network & Outage",
        "text": "تجربة قياس سرعة الفايف جي 5G مع @alnoor_telecom في بوليفارد سيتي وصلت 920 Mbps! صراحة تطور جبار في التغطية مقارنة بالعام الماضي. ⚡🏎️ #تقنية #السعودية #5G #النور",
        "author": "@saudi_speedtest",
    },
    {
        "brand": "Al-Noor Telecom",
        "platform": "tiktok",
        "lang": "en",
        "sentiment": "negative",
        "theme": "Pricing & Billing",
        "text": "Al-Noor Telecom just increased their postpaid fiber subscription fee by 15% without prior notice. Customer care response time is over 45 minutes on WhatsApp. Disappointing service! #AlNoor #TelecomGCC #SaudiExpat",
        "author": "@dubai_expat_daily",
    },
    {
        "brand": "Al-Noor Telecom",
        "platform": "instagram",
        "lang": "ar",
        "sentiment": "negative",
        "theme": "Customer Support",
        "text": "خدمة عملاء النور @alnoor_telecom أسوأ تجربة ممكن تمر فيها.. مقدم على نقل خط الفايبر من أسبوعين وكل يوم موعد وهمي والفني ما يجي! 🤦‍♂️ #خدمة_العملاء #شكاوى_الاتصالات",
        "author": "@fahad_alotaibi_99",
    },
    {
        "brand": "Al-Noor Telecom",
        "platform": "tiktok",
        "lang": "mixed",
        "sentiment": "neutral",
        "theme": "Promotions & Offers",
        "text": "عرض باقة التجوال الدولي الجديدة من Al-Noor Telecom لدول الخليج.. 30GB بـ 150 ريال هل تسوى ولا اشتري eSIM محلي أفضل؟ شاركونا تجاربكم 👇 #travel #سفر #النور",
        "author": "@wanderlust_khaleeji",
    },

    # --- DesertPay (FinTech, Digital Wallet, Cashback, Remittance) ---
    {
        "brand": "DesertPay",
        "platform": "tiktok",
        "lang": "ar",
        "sentiment": "positive",
        "theme": "Promotions & Offers",
        "text": "والله محفظة ديزرت باي @DesertPay فكت أزمة! كاش باك 10% فوري على كل مشتريات السوبرماركت ومحطات الوقود طوال شهر رمضان المبارك 🌙💳 نزل الكاش باك بنفس اللحظة! #DesertPay #كاش_باك #ديزرت_باي #عروض_رمضان",
        "author": "@deals_hunter_ksa",
    },
    {
        "brand": "DesertPay",
        "platform": "instagram",
        "lang": "ar",
        "sentiment": "negative",
        "theme": "App & UX Experience",
        "text": "تطبيق نقد الصحراء (DesertPay) معلق عند صفحة التحقق من الهوية بعد التحديث الأخير v3.2. البطاقة مجمدة ورصيدي معلق ومحد يرد بتويتر أو الشات! حلوا المشكلة بسرعة 🚨 #ديزرت_باي #DesertPay #مشكلة_تقنية",
        "author": "@nora_fintech",
    },
    {
        "brand": "DesertPay",
        "platform": "tiktok",
        "lang": "en",
        "sentiment": "positive",
        "theme": "App & UX Experience",
        "text": "Just tested the international remittance feature on DesertPay to send money from Riyadh to Dubai. Instant settlement and zero FX markup fees for the first transfer! Sleek UI too. 💸✨ #FintechSaudi #DesertPay #MoneyTransfer",
        "author": "@mark_in_riyadh",
    },
    {
        "brand": "DesertPay",
        "platform": "instagram",
        "lang": "ar",
        "sentiment": "neutral",
        "theme": "Promotions & Offers",
        "text": "هل بطاقة ديزرت باي الائتمانية مقبولة لدخول صالات المطارات في دول الخليج بدون رسوم إضافية؟ يا ريت الإفادة من المجربين. ✈️ #ديزرت_باي #سفر #بطاقات_ائتمانية",
        "author": "@tariq_travels",
    },
    {
        "brand": "DesertPay",
        "platform": "tiktok",
        "lang": "ar",
        "sentiment": "negative",
        "theme": "Pricing & Billing",
        "text": "انتبهوا من رسوم التحويل الخفية في تطبيق ديزرت باي عند الدفع للمتاجر الدولية، تم خصم 3.5% رسوم معالجة عملة غير معلنة في الإعلان الرسمي! 📉 #نقد_الصحراء #توعية_مالية",
        "author": "@investor_khaleej",
    },

    # --- Oasis Retail (E-Commerce, Hypermarket, Delivery, Prices) ---
    {
        "brand": "Oasis Retail",
        "platform": "instagram",
        "lang": "ar",
        "sentiment": "positive",
        "theme": "Delivery & Logistics",
        "text": "طلبت مقاضي البيت الأسبوعية من تطبيق واحة التجزئة Oasis Retail، وصل الطلب مغلف ومرتب خلال 40 دقيقة بالضبط والفواكه طازجة جداً! تجربة 10/10 🍎🛒 @oasis_retail #واحة_التجزئة #توصيل_مقاضي #دبي",
        "author": "@dubai_mom_life",
    },
    {
        "brand": "Oasis Retail",
        "platform": "tiktok",
        "lang": "ar",
        "sentiment": "negative",
        "theme": "Delivery & Logistics",
        "text": "أسواق الواحة @oasis_retail للأسف مستوى التوصيل تراجع جداً في جدة.. مندوب التوصيل تأخر ساعتين والآيس كريم واصل ذايب تماماً ورافضين يرجعون المبلغ في المحفظة! 😡🍦 #واحة_التجزئة #تجارب_توصيل #جدة",
        "author": "@sara_jeddah_reviews",
    },
    {
        "brand": "Oasis Retail",
        "platform": "instagram",
        "lang": "en",
        "sentiment": "positive",
        "theme": "Promotions & Offers",
        "text": "Weekend mega clearance sale at Oasis Retail Festival City! Got premium kitchenware at 60% off. Clean aisles, automated checkout was super swift. Highly recommend checking it out. 🛍️🏷️ #OasisRetail #DubaiShopping #WeekendDeals",
        "author": "@uae_bargain_finds",
    },
    {
        "brand": "Oasis Retail",
        "platform": "tiktok",
        "lang": "ar",
        "sentiment": "neutral",
        "theme": "Promotions & Offers",
        "text": "جولة في فرع واحة التجزئة الجديد في الظهران مول.. هل هو أفضل من الفروع القديمة؟ شوفوا الأسعار وقارنوا بنفسكم. 🛒🔍 #الشرقية #الظهران #واحة_التجزئة #تسوق",
        "author": "@khobar_guide",
    },

    # --- Falcon Ride (Ride-hailing, Surge Pricing, Drivers) ---
    {
        "brand": "Falcon Ride",
        "platform": "tiktok",
        "lang": "ar",
        "sentiment": "negative",
        "theme": "Pricing & Billing",
        "text": "يا جماعة مو معقول أسعار صقر رايد Falcon Ride وقت خروج الموظفين في الرياض! المشوار من العليا إلى النرجس صار بـ 110 ريال والسعر العادي 35 ريال.. الدبل 3 مرات سلامات؟! 🚗💸 #صقر_رايد #زحمة_الرياض #اسعار_المشاوير",
        "author": "@riyadh_commuter",
    },
    {
        "brand": "Falcon Ride",
        "platform": "instagram",
        "lang": "en",
        "sentiment": "negative",
        "theme": "Customer Support",
        "text": "Falcon Ride driver cancelled after making me wait 20 minutes in 43°C heat outside Dubai Mall, and the app charged ME a cancellation fee! Support bot is useless. @FalconRide fix this! 🚗🔥 #FalconRide #DubaiTransport #CustomerServiceFail",
        "author": "@expat_dubai_life",
    },
    {
        "brand": "Falcon Ride",
        "platform": "tiktok",
        "lang": "ar",
        "sentiment": "positive",
        "theme": "App & UX Experience",
        "text": "ميزة الحجز المسبق في صقر رايد للمطار ممتازة جداً. السائق وصل قبل الموعد بـ 10 دقائق، سيارة نظيفة ومحترمة وقيادة هادئة. شكراً @falcon_ride 👍✈️ #سفر #مطار_الملك_خالد #صقر_رايد",
        "author": "@khalid_traveler",
    },
    {
        "brand": "Falcon Ride",
        "platform": "instagram",
        "lang": "mixed",
        "sentiment": "neutral",
        "theme": "Promotions & Offers",
        "text": "كود خصم صقر رايد FALCON25 شغال حالياً في أبوظبي والشارقة خصم 25% على أول 3 مشاوير.. جربوه وعطوني رايكم 🎟️ #FalconRide #AbuDhabi #توفير",
        "author": "@uae_promos_daily",
    },

    # --- GulfCloud (Enterprise Cloud, B2B, Cybersecurity, SLA) ---
    {
        "brand": "GulfCloud",
        "platform": "instagram",
        "lang": "ar",
        "sentiment": "positive",
        "theme": "App & UX Experience",
        "text": "فخورون بإتمام نقل البنية التحتية الرقمية لشركتنا بالكامل إلى مراكز بيانات سحابة الخليج GulfCloud في الرياض. زمن استجابة (Latency) أقل من 6ms وامتثال تام لضوابط الأمن السيبراني السعودية 🇸🇦☁️ #GulfCloud #التحول_الرقمي #رؤية_2030",
        "author": "@cto_saudi_tech",
    },
    {
        "brand": "GulfCloud",
        "platform": "tiktok",
        "lang": "en",
        "sentiment": "negative",
        "theme": "Network & Outage",
        "text": "GulfCloud me-central-1 region experiencing elevated API latency and partial database replication outages this afternoon. Our production services are running on fallback. Waiting on post-mortem. ⚠️☁️ #GulfCloud #CloudOutage #DevOpsGCC",
        "author": "@cloud_architect_ae",
    },
    {
        "brand": "GulfCloud",
        "platform": "instagram",
        "lang": "ar",
        "sentiment": "neutral",
        "theme": "Promotions & Offers",
        "text": "تعلن جلف كلاود GulfCloud عن برنامج دعم الشركات الناشئة في دول الخليج برصيد سحابي يصل إلى 50,000 دولار مع تدريب مجاني للفرق التقنية. رابط التقديم في البايو. 💡🚀 #ريادة_الأعمال #سحابة_الخليج #شركات_ناشئة",
        "author": "@venture_gulf",
    },
]


class SyntheticSocialAdapter(BaseAdapter):
    """
    Adapter generating realistic synthetic social media posts for TikTok and Instagram.
    Simulates authentic GCC discussions, slang, code-switching, engagement curves, and hashtags.
    """

    def __init__(self, platform: str = "tiktok"):
        """
        Args:
            platform: 'tiktok' or 'instagram'.
        """
        valid_platforms = {"tiktok": "tiktok_synthetic", "instagram": "instagram_synthetic"}
        if platform not in valid_platforms:
            raise ValueError(f"Platform must be one of {list(valid_platforms.keys())}")
        self.target_platform = platform
        super().__init__(name=valid_platforms[platform])

    def fetch(self, query: str, limit: int = 50, **kwargs) -> List[RawPost]:
        """
        Generate synthetic posts for the specified query/brand.
        """
        fetch_time = self.now_utc_iso()
        posts: List[RawPost] = []

        # Filter templates relevant to query or include all if generic
        matching_templates = [
            t for t in POST_TEMPLATES
            if query.lower() in t["brand"].lower() or query.lower() in t["text"].lower()
        ]
        if not matching_templates:
            matching_templates = POST_TEMPLATES

        now = datetime.now(timezone.utc)

        for i in range(limit):
            template = matching_templates[i % len(matching_templates)]
            # Spread timestamps across the last 30 days deterministically
            day_offset = (i * 2 + (hash(query) % 7)) % 28
            post_time = now - timedelta(days=day_offset, hours=(i * 3) % 24, minutes=(i * 17) % 60)
            post_id = f"{self.target_platform[:2]}_syn_{hashlib.md5(f'{query}_{i}_{post_time.isoformat()}'.encode()).hexdigest()[:10]}"

            # Platform-specific engagement profiles
            if self.target_platform == "tiktok":
                views = int(1200 * (1.15 ** (i % 25)) + (hash(f"v_{i}") % 3000))
                likes = max(10, int(views * 0.065))
                comments = max(2, int(likes * 0.08))
                shares = max(1, int(likes * 0.04))
                engagement = {
                    "views": views,
                    "likes": likes,
                    "comments": comments,
                    "shares": shares,
                }
            else:  # Instagram
                likes = int(350 * (1.12 ** (i % 20)) + (hash(f"l_{i}") % 1200))
                comments = max(3, int(likes * 0.05))
                saves = max(1, int(likes * 0.03))
                engagement = {
                    "likes": likes,
                    "comments": comments,
                    "saves": saves,
                }

            # Generate synthetic raw payload adhering to platform schema standards
            raw_payload = {
                "synthetic_id": post_id,
                "platform": self.target_platform,
                "author": template["author"],
                "caption": template["text"],
                "target_brand": template["brand"],
                "intended_sentiment": template["sentiment"],
                "intended_theme": template["theme"],
                "language_profile": template["lang"],
                "engagement_metrics": engagement,
                "created_at": post_time.isoformat(),
                "compliance_notice": "Generated synthetically to comply with platform terms of service prohibiting unauthorized scraping.",
            }

            post = RawPost(
                id=post_id,
                source=self.name,
                fetch_time=fetch_time,
                query=query,
                raw_json=raw_payload,
                published_at=post_time.isoformat(),
                text=template["text"],
                author=template["author"],
                url=f"https://www.{self.target_platform}.com/{template['author']}/status/{post_id}",
                engagement=engagement,
                metadata={
                    "platform": self.target_platform,
                    "target_brand": template["brand"],
                    "language_hint": template["lang"],
                    "intended_theme": template["theme"],
                    "is_synthetic": True,
                    "generator_version": "1.0.0",
                },
            )
            posts.append(post)

        return posts
