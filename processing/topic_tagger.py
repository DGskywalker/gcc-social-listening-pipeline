"""
Topic and Domain Theme Tagger for GCC Social Listening Pipeline.
Categorizes posts into core operational and business themes.
"""

import re
from typing import List, Dict, Any, Optional
from processing.cleaning import normalize_arabic


TOPIC_RULES: Dict[str, Dict[str, Any]] = {
    "Customer Support": {
        "keywords_ar": [
            "خدمة العملاء", "الدعم الفني", "خدمه العملاء", "ما يردون", "محد يرد",
            "رفعت بلاغ", "رقم الشكوى", "تطنيش", "مماطلة", "ردوا علي", "خدمة سيئة",
            "الموظف", "الكول سنتر", "شات الدعم", "تذكرة دعم", "مافي تجاوب", "المحادثة"
        ],
        "keywords_en": [
            "customer service", "customer support", "support team", "helpdesk",
            "no response", "ticket", "care team", "complaint", "call center",
            "waiting on line", "useless support", "unresponsive", "chat support"
        ],
    },
    "Network & Outage": {
        "keywords_ar": [
            "شبكة", "الشبكة", "فاصل", "انقطاع", "عطل", "تغطية", "فايف جي", "5g",
            "فايبر", "ألياف", "الياف", "بطيء", "النت معلق", "مافي شبكة", "ضعف النت",
            "تقطيع", "برج", "ابراج", "راوتر", "مودم", "latency", "ping"
        ],
        "keywords_en": [
            "network", "outage", "down", "offline", "5g", "fiber", "latency",
            "ping", "packet loss", "no signal", "slow internet", "disconnection",
            "cell tower", "coverage", "broadband", "disconnected"
        ],
    },
    "Pricing & Billing": {
        "keywords_ar": [
            "سعر", "اسعار", "أسعار", "غالي", "رسوم", "فاتورة", "فواتير", "اشتراك",
            "خصموا", "مبالغ", "دبل", "سعر خيالي", "رسوم خفية", "ارتفاع الاسعار",
            "ضريبة", "عمولة", "تسعيرة", "تكلفة"
        ],
        "keywords_en": [
            "price", "pricing", "expensive", "fee", "fees", "bill", "billing",
            "invoice", "charged me", "surge", "surge pricing", "hidden fees",
            "overpriced", "subscription fee", "cost"
        ],
    },
    "Delivery & Logistics": {
        "keywords_ar": [
            "توصيل", "التوصيل", "مندوب", "المندوب", "تأخير", "تأخر", "سائق",
            "شحن", "الشحنة", "الطلب ما وصل", "طلب معلق", "ذايب", "كرتون",
            "عنوان التوصيل", "توصيل متأخر"
        ],
        "keywords_en": [
            "delivery", "driver", "courier", "rider", "arrived late", "delay",
            "shipping", "package", "melted", "order missing", "cancelled order",
            "turnaround"
        ],
    },
    "Promotions & Offers": {
        "keywords_ar": [
            "عرض", "عروض", "كود", "كود خصم", "كاش باك", "كاشباك", "مجانا", "مجاني",
            "تخفيضات", "خصومات", "يوم وطني", "رمضان", "عيد", "مسابقة", "هدية",
            "وفر", "توفير", "باقة مجانية"
        ],
        "keywords_en": [
            "promo", "promotion", "promotions", "discount", "code", "coupon",
            "cashback", "sale", "deals", "offer", "offers", "clearance",
            "ramadan deal", "national day", "free", "save"
        ],
    },
    "App & UX Experience": {
        "keywords_ar": [
            "تطبيق", "التطبيق", "معلق", "يعلق", "تحديث", "شاشة سوداء", "تسجيل دخول",
            "كود التحقق", "رمز التحقق", "otp", "بصمة", "خطأ في النظام", "تهنيج",
            "اصدار", "واجهة", "تجربة المستخدم"
        ],
        "keywords_en": [
            "app", "application", "crash", "crashes", "crashing", "frozen",
            "bug", "bugs", "glitch", "update", "login", "authentication",
            "otp", "biometrics", "ui", "ux", "interface"
        ],
    },
}


class TopicTagger:
    """Rule-based Topic & Domain Theme Tagger."""

    def __init__(self):
        self._rules = TOPIC_RULES
        self._precomputed_rules = {}
        for theme, rule in self._rules.items():
            en_kws = [kw.lower() for kw in rule["keywords_en"]]
            ar_kws = list(set([kw.lower() for kw in rule["keywords_ar"]] + [normalize_arabic(kw.lower()) for kw in rule["keywords_ar"]]))
            self._precomputed_rules[theme] = {"en": en_kws, "ar": ar_kws}

    def tag_topics(self, text: str) -> Dict[str, Any]:
        """
        Identify matching themes from text content.
        Returns matched themes, scores, and primary theme.
        """
        if not text:
            return {"primary_theme": "General", "all_themes": [], "scores": {}}

        clean_text_lower = text.lower()
        norm_ar = normalize_arabic(clean_text_lower)

        scores: Dict[str, int] = {}

        for theme, pre in self._precomputed_rules.items():
            hit_count = 0
            # Check English keywords
            for kw in pre["en"]:
                if kw in clean_text_lower:
                    hit_count += 1

            # Check Arabic keywords (pre-normalized)
            for kw in pre["ar"]:
                if kw in clean_text_lower or kw in norm_ar:
                    hit_count += 1

            if hit_count > 0:
                scores[theme] = hit_count

        if not scores:
            return {"primary_theme": "General", "all_themes": ["General"], "scores": {}}

        sorted_themes = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary_theme = sorted_themes[0][0]
        all_themes = [t[0] for t in sorted_themes]

        return {
            "primary_theme": primary_theme,
            "all_themes": all_themes,
            "scores": scores,
        }
