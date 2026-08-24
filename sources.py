# -*- coding: utf-8 -*-
"""
فقط منابع پایدار و مستقیم خبرگزاری‌ها (بدون Nitter و بدون منابع خراب)
"""

SOURCES = [
    {
        "name": "Al Jazeera",
        "rss": "https://www.aljazeera.com/xml/rss/all.xml",
        "lang": "en",
        "type": "international",
        "filter_keywords": True
    },
    {
        "name": "BBC World",
        "rss": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "lang": "en",
        "type": "international",
        "filter_keywords": True
    },
    {
        "name": "BBC Middle East",
        "rss": "https://feeds.bbci.co.uk/news/world/middle_east/rss.xml",
        "lang": "en",
        "type": "international",
        "filter_keywords": True
    },
    {
        "name": "The Guardian World",
        "rss": "https://www.theguardian.com/world/rss",
        "lang": "en",
        "type": "international",
        "filter_keywords": True
    },
    {
        "name": "France 24 - Middle East",
        "rss": "https://www.france24.com/en/middle-east/rss",
        "lang": "en",
        "type": "international",
        "filter_keywords": True
    },
    {
        "name": "NYT Middle East",
        "rss": "https://rss.nytimes.com/services/xml/rss/nyt/MiddleEast.xml",
        "lang": "en",
        "type": "international",
        "filter_keywords": True
    },
    {
        "name": "Foreign Policy - Iran",
        "rss": "https://foreignpolicy.com/tag/iran/feed",
        "lang": "en",
        "type": "international",
        "filter_keywords": True
    },
    {
        "name": "Arab News",
        "rss": "https://www.arabnews.com/rss.xml",
        "lang": "en",
        "type": "international",
        "filter_keywords": True
    },
    {
        "name": "DW English",
        "rss": "https://rss.dw.com/rdf/rss-en-all",
        "lang": "en",
        "type": "international",
        "filter_keywords": True
    },
    {
        "name": "Iran International",
        "rss": "https://www.iranintl.com/en/rss",
        "lang": "en",
        "type": "diaspora",
        "filter_keywords": True
    },
]

IRAN_KEYWORDS = [
    "iran", "iranian", "tehran", "hormuz", "irgc", "missile", "drone",
    "israel iran", "iran israel", "war", "strike", "attack", "khamenei",
    "ایران", "تهران", "هرمز", "موشک", "پهپاد", "جنگ", "حمله", "خامنه‌ای", "سپاه"
]

def get_active_sources():
    return SOURCES
