"""
Rule-based Brand Tagger for GCC Social Listening Pipeline.
Includes comprehensive Arabic aliases, hashtags, handles, and spelling variations
for fictional benchmark brands.
"""

import re
from typing import List, Dict, Any, Optional
from processing.cleaning import normalize_arabic


# Comprehensive brand dictionary with aliases, hashtags, handles, and Arabic orthographic forms
BRAND_DICTIONARY: Dict[str, Dict[str, Any]] = {
    "Al-Noor Telecom": {
        "sector": "Telecommunications",
        "aliases_ar": [
            "النور للاتصالات",
            "شركة النور",
            "اتصالات النور",
            "شبكة النور",
            "النور للالياف",
            "النور فايبر",
            "النور",
        ],
        "aliases_en": [
            "al-noor telecom",
            "al noor telecom",
            "alnoor telecom",
            "al-noor",
            "al noor",
            "alnoor",
        ],
        "handles": ["@alnoor_telecom", "@alnoortelecom", "@alnoor_care"],
        "hashtags": [
            "#النور_للاتصالات",
            "#شبكة_النور",
            "#شركة_النور",
            "#alnoortelecom",
            "#alnoor",
        ],
    },
    "DesertPay": {
        "sector": "FinTech / Digital Banking",
        "aliases_ar": [
            "ديزرت باي",
            "ديزرت_باي",
            "نقد الصحراء",
            "محفظة ديزرت باي",
            "محفظة ديزرت",
            "تطبيق ديزرت باي",
            "ديزرت",
        ],
        "aliases_en": [
            "desertpay",
            "desert pay",
            "desert-pay",
            "desert wallet",
        ],
        "handles": ["@desertpay", "@desert_pay", "@desertpay_care"],
        "hashtags": [
            "#ديزرت_باي",
            "#نقد_الصحراء",
            "#desertpay",
            "#desert_pay",
        ],
    },
    "Oasis Retail": {
        "sector": "E-Commerce & Hypermarket",
        "aliases_ar": [
            "واحة التجزئة",
            "واحة_التجزئة",
            "اسواق الواحة",
            "هايبرماركت الواحة",
            "سوبرماركت الواحة",
            "متاجر الواحة",
            "تطبيق الواحة",
        ],
        "aliases_en": [
            "oasis retail",
            "oasis hypermarket",
            "oasis market",
            "oasis supermarket",
            "oasis stores",
        ],
        "handles": ["@oasis_retail", "@oasisretail", "@oasis_care"],
        "hashtags": [
            "#واحة_التجزئة",
            "#اسواق_الواحة",
            "#oasisretail",
            "#oasis_retail",
        ],
    },
    "Falcon Ride": {
        "sector": "Mobility & Delivery",
        "aliases_ar": [
            "صقر رايد",
            "صقر_رايد",
            "تطبيق صقر",
            "توصيل صقر",
            "كابتن صقر",
        ],
        "aliases_en": [
            "falcon ride",
            "falconride",
            "falcon app",
            "falcon mobility",
        ],
        "handles": ["@falcon_ride", "@falconride", "@falcon_care"],
        "hashtags": [
            "#صقر_رايد",
            "#تطبيق_صقر",
            "#falconride",
            "#falcon_ride",
        ],
    },
    "GulfCloud": {
        "sector": "Enterprise Cloud & SaaS",
        "aliases_ar": [
            "سحابة الخليج",
            "سحابة_الخليج",
            "جلف كلاود",
            "جلف_كلاود",
            "خدمات سحابة الخليج",
        ],
        "aliases_en": [
            "gulfcloud",
            "gulf cloud",
            "gulf-cloud",
            "gulf cloud platform",
        ],
        "handles": ["@gulfcloud", "@gulf_cloud", "@gulfcloud_tech"],
        "hashtags": [
            "#سحابة_الخليج",
            "#جلف_كلاود",
            "#gulfcloud",
            "#gulf_cloud",
        ],
    },
}


class BrandTagger:
    """Rule-based Brand Tagger with multi-lingual pattern matching."""

    def __init__(self):
        self._compiled_patterns = self._build_compiled_patterns()

    def _build_compiled_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Pre-compile regex patterns for each brand for optimal matching speed."""
        compiled = {}
        for brand, data in BRAND_DICTIONARY.items():
            patterns = []
            all_terms = (
                data["aliases_ar"]
                + data["aliases_en"]
                + data["handles"]
                + data["hashtags"]
            )
            for term in all_terms:
                # Escape for regex and allow word boundary if alphanumeric
                escaped = re.escape(term)
                # For Arabic terms, match after normalize_arabic
                patterns.append((term, re.compile(rf"(?:\b|(?<=[\s#@_])){escaped}(?:\b|(?=[\s#@_]))", re.IGNORECASE)))
            compiled[brand] = patterns
        return compiled

    def tag_brands(self, text: str) -> Dict[str, Any]:
        """
        Scan text and return matched brands, mention details, and primary brand.
        """
        if not text:
            return {"brands": [], "primary_brand": None, "details": {}}

        clean_lower = text.lower()
        norm_ar = normalize_arabic(clean_lower)

        matched_brands: List[str] = []
        details: Dict[str, List[str]] = {}

        for brand, patterns in self._compiled_patterns.items():
            brand_hits = []
            for original_term, regex in patterns:
                # Check against raw text
                if regex.search(clean_lower):
                    brand_hits.append(original_term)
                    continue

                # Check against Arabic normalized text
                norm_term = normalize_arabic(original_term.lower())
                if norm_term in norm_ar:
                    brand_hits.append(original_term)

            if brand_hits:
                matched_brands.append(brand)
                details[brand] = list(set(brand_hits))

        primary_brand = matched_brands[0] if matched_brands else None

        return {
            "brands": matched_brands,
            "primary_brand": primary_brand,
            "details": details,
        }
