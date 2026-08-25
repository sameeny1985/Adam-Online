# -*- coding: utf-8 -*-
import logging
from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)

def translate_to_persian(text: str) -> str:
    if not text or not str(text).strip():
        return ""
    text = str(text).strip()[:4500]
    try:
        fa = sum(1 for c in text if "\u0600" <= c <= "\u06FF")
        if fa > len(text) * 0.3:
            return text
        return GoogleTranslator(source="auto", target="fa").translate(text) or text
    except Exception as e:
        logger.warning(f"translate: {e}")
        return text
