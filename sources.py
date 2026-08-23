# -*- coding: utf-8 -*-
"""
فقط منابع خارجی و بین‌المللی.
رسانه‌های داخل ایران حذف شدند.
فقط اخبار مرتبط با جنگ فیلتر می‌شوند.
"""

SOURCES = [
    {
        "name": "Al Jazeera",
        "rss": "https://www.aljazeera.com/xml/rss/all.xml",
        "lang": "en",
        "priority": 1,
        "type": "international",
        "filter_keywords": True
    },
    {
        "name": "BBC World",
        "rss": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "lang": "en",
        "priority": 1,
        "type": "international",
        "filter_keywords": True
    },
    {
        "name": "BBC Middle East",
        "rss": "https://feeds.bbci.co.uk/news/world/middle_east/rss.xml",
        "lang": "en",
        "priority": 1,
        "type": "international",
        "filter_keywords": True
    },
    {
        "name": "The Guardian World",
        "rss": "https://www.theguardian.com/world/rss",
        "lang": "en",
        "priority": 1,
        "type": "international",
        "filter_keywords": True
    },
    {
        "name": "France 24 - Middle East",
        "rss": "https://www.france24.com/en/middle-east/rss",
        "lang": "en",
        "priority": 1,
        "type": "international",
        "filter_keywords": True
    },
    {
        "name": "NYT Middle East",
        "rss": "https://rss.nytimes.com/services/xml/rss/nyt/MiddleEast.xml",
        "lang": "en",
        "priority": 1,
        "type": "international",
        "filter_keywords": True
    },
    {
        "name": "Foreign Policy - Iran",
        "rss": "https://foreignpolicy.com/tag/iran/feed",
        "lang": "en",
        "priority": 1,
        "type": "international",
        "filter_keywords": True
    },
    {
        "name": "Middle East Eye",
        "rss": "https://www.middleeasteye.net/rss",
        "lang": "en",
        "priority": 1,
        "type": "international",
        "filter_keywords": True
    },
    {
        "name": "The Jerusalem Post",
        "rss": "https://www.jpost.com/rss/rssfeedsirannews.aspx",
        "lang": "en",
        "priority": 1,
        "type": "international",
        "filter_keywords": True
    },
    {
        "name": "Arab News",
        "rss": "https://www.arabnews.com/rss.xml",
        "lang": "en",
        "priority": 2,
        "type": "international",
        "filter_keywords": True
    },
    {
        "name": "DW English",
        "rss": "https://rss.dw.com/rdf/rss-en-all",
        "lang": "en",
        "priority": 2,
        "type": "international",
        "filter_keywords": True
    },
    {
        "name": "Iran International",
        "rss": "https://www.iranintl.com/en/rss",
        "lang": "en",
        "priority": 1,
        "type": "diaspora",
        "filter_keywords": True
    },
    {
        "name": "IranWire",
        "rss": "https://iranwire.com/en/feed/",
        "lang": "en",
        "priority": 1,
        "type": "diaspora",
        "filter_keywords": True
    },
    {
        "name": "HRANA",
        "rss": "https://en-hrana.org/articles/feed",
        "lang": "en",
        "priority": 1,
        "type": "diaspora",
        "filter_keywords": True
    },
    {
        "name": "Reza Pahlavi",
        "rss": "https://nitter.net/PahlaviReza/rss",
        "lang": "en",
        "priority": 1,
        "type": "x_account",
        "filter_keywords": True
    },
    {
        "name": "Netanyahu",
        "rss": "https://nitter.net/netanyahu/rss",
        "lang": "en",
        "priority": 1,
        "type": "x_account",
        "filter_keywords": True
    },
    {
        "name": "Donald Trump",
        "rss": "https://nitter.net/realDonaldTrump/rss",
        "lang": "en",
        "priority": 1,
        "type": "x_account",
        "filter_keywords": True
    },
    {
        "name": "White House Press Sec",
        "rss": "https://nitter.net/PressSec/rss",
        "lang": "en",
        "priority": 1,
        "type": "x_account",
        "filter_keywords": True
    },
    {
        "name": "SecWar (Pete Hegseth)",
        "rss": "https://nitter.net/SecWar/rss",
        "lang": "en",
        "priority": 1,
        "type": "x_account",
        "filter_keywords": True
    },
]

# فقط کلمات مرتبط با جنگ
IRAN_KEYWORDS = [
    "iran war", "war on iran", "iran conflict", "iran israel", "israel iran",
    "strait of hormuz", "hormuz", "irgc", "missile", "drone strike",
    "us strike iran", "american strike", "bombing iran", "attack on iran",
    "iran attack", "ceasefire iran", "iran nuclear", "khamenei",
    "reza pahlavi", "netanyahu iran", "trump iran",
    "جنگ ایران", "حمله به ایران", "تنگه هرمز", "موشک", "پهپاد",
    "حملات آمریکا", "حملات اسرائیل", "جنگ ایران و اسرائیل",
    "خامنه‌ای", "سپاه", "رضا پهلوی"
]

def get_active_sources():
    return SOURCES
