# -*- coding: utf-8 -*-
"""
مترجم با کیفیت بالا به فارسی با استفاده از deep-translator (Google Translate backend).
برای کیفیت بهتر می‌توانید مدل‌های محلی یا OpenAI را جایگزین کنید.
"""
from deep_translator import GoogleTranslator
import time
import logging

logger = logging.getLogger(__name__)

translator = GoogleTranslator(source="auto", target="fa")

def translate_to_persian(text: str, max_retries: int = 3) -> str:
    if not text or not text.strip():
        return ""
    text = text.strip()
    # اگر متن خیلی کوتاه یا قبلاً فارسی است، برگردان
    if len(text) < 3:
        return text

    for attempt in range(max_retries):
        try:
            # محدودیت طول Google Translate حدود ۵۰۰۰ کاراکتر است
            if len(text) > 4500:
                text = text[:4500] + "..."
            result = translator.translate(text)
            return result if result else text
        except Exception as e:
            logger.warning(f"Translation attempt {attempt+1} failed: {e}")
            time.sleep(1.5 * (attempt + 1))
    return text  # در صورت شکست، متن اصلی را برگردان
