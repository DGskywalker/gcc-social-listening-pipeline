"""
Language detection module tailored for GCC social media.
Detects Arabic (ar), English (en), and Mixed bilingual code-switching (ar-en).
"""

import re
from typing import Tuple

# Unicode range for Arabic characters (Arabic, Supplementary, Presentation Forms)
ARABIC_CHAR_PATTERN = re.compile(
    r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]"
)
LATIN_CHAR_PATTERN = re.compile(r"[a-zA-Z]")


def detect_language(text: str) -> str:
    """
    Detect language of post text.
    Returns:
      - 'ar': Arabic dominant (>60% of script chars or >10 Arabic chars with minimal Latin)
      - 'en': English dominant (>75% Latin chars)
      - 'mixed': Bilingual code-switching (both Arabic and Latin scripts present significantly)
      - 'other': Numerical, emoji-only, or unrecognized scripts
    """
    if not text:
        return "other"

    arabic_chars = len(ARABIC_CHAR_PATTERN.findall(text))
    latin_chars = len(LATIN_CHAR_PATTERN.findall(text))
    total_alpha = arabic_chars + latin_chars

    if total_alpha == 0:
        return "other"

    ar_ratio = arabic_chars / total_alpha
    en_ratio = latin_chars / total_alpha

    # Code-switching detection (common in GCC tech and urban social posts)
    if arabic_chars >= 5 and latin_chars >= 5 and (0.15 <= ar_ratio <= 0.85):
        return "mixed"

    if ar_ratio >= 0.55:
        return "ar"

    if en_ratio >= 0.60:
        return "en"

    return "mixed" if (arabic_chars > 0 and latin_chars > 0) else "other"


def get_language_confidence(text: str) -> Tuple[str, float]:
    """Return predicted language and rough script confidence score (0.0 to 1.0)."""
    lang = detect_language(text)
    arabic_chars = len(ARABIC_CHAR_PATTERN.findall(text))
    latin_chars = len(LATIN_CHAR_PATTERN.findall(text))
    total_alpha = arabic_chars + latin_chars

    if total_alpha == 0:
        return ("other", 0.0)

    if lang == "ar":
        conf = round(arabic_chars / total_alpha, 2)
    elif lang == "en":
        conf = round(latin_chars / total_alpha, 2)
    elif lang == "mixed":
        conf = round(1.0 - abs((arabic_chars / total_alpha) - 0.5) * 2, 2)
    else:
        conf = 0.5

    return lang, min(1.0, max(0.0, conf))
