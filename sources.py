# -*- coding: utf-8 -*-
"""
لیست منابع معتبر و نسبتاً پایدار که بیشترین پوشش ایران را دارند.
لینک‌های خراب یا ناپایدار (مثل خیلی از Nitterها) حذف یا جایگزین شدند.
"""

SOURCES = [
    # ===== خبرگزاری‌های ایرانی (پایدار) =====
    {
        "name": "Mehr News Agency",
        "rss": "https://en.mehrnews.com/rss",
        "lang": "en",
        "priority": 1,
        "type": "agency"
    },
    {
        "name": "Mehr News - Iran",
        "rss": "https://en.mehrnews.com/rss/tp/575",
        "lang": "en",
        "priority": 1,
        "type": "agency"
    },
    {
        "name": "Tehran Times",
        "rss": "https://www.tehrantimes.com/rss",
        "lang": "en",
        "priority": 1,
        "type": "agency"
    },
    {
        "name": "IRNA فارسی",
        "rss": "https://www.irna.ir/rss",
        "lang": "fa",
        "priority": 1,
        "type": "agency"
    },
    {
        "name": "Press TV",
        "rss": "https://www.presstv.ir/rss.xml",
        "lang": "en",
        "priority": 1,
        "type": "agency"
    },

    # ===== بین‌المللی (پوشش قوی ایران) =====
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
        "type": "international"
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
        "type": "international"
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
        "name": "Google News - Iran",
        "rss": "https://news.google.com/rss/search?q=Iran&hl=en-US&gl=US&ceid=US:en",
        "lang": "en",
        "priority": 1,
        "type": "international"
    },
    {
        "name": "Google News - ایران",
        "rss": "https://news.google.com/rss/search?q=%D8%A7%DB%8C%D8%B1%D8%A7%D9%86&hl=fa&gl=IR&ceid=IR:fa",
        "lang": "fa",
        "priority": 1,
        "type": "international"
    },

    # ===== رسانه‌های فارسی خارج =====
    {
        "name": "Iran International",
        "rss": "https://www.iranintl.com/en/rss",
        "lang": "en",
        "priority": 1,
        "type": "diaspora"
    },
    {
        "name": "IranWire",
        "rss": "https://iranwire.com/en/feed/",
        "lang": "en",
        "priority": 1,
        "type": "diaspora"
    },
    {
        "name": "HRANA",
        "rss": "https://en-hrana.org/articles/feed",
        "lang": "en",
        "priority": 1,
        "type": "diaspora"
    },

    # ===== حساب‌های مهم (Nitter ممکن است قطع باشد، ولی نگه داشتیم) =====
    {
        "name": "Reza Pahlavi",
        "rss": "https://nitter.net/PahlaviReza/rss",
        "lang": "en",
        "priority": 1,
        "type": "x_account",
        "handle": "PahlaviReza"
    },
    {
        "name": "Netanyahu",
        "rss": "https://nitter.net/netanyahu/rss",
        "lang": "en",
        "priority": 1,
        "type": "x_account",
        "handle": "netanyahu"
    },
    {
        "name": "Donald Trump",
        "rss": "https://nitter.net/realDonaldTrump/rss",
        "lang": "en",
        "priority": 1,
        "type": "x_account",
        "handle": "realDonaldTrump"
    },
    {
        "name": "White House Press Sec",
        "rss": "https://nitter.net/PressSec/rss",
        "lang": "en",
        "priority": 1,
        "type": "x_account",
        "handle": "PressSec"
    },
    {
        "name": "SecWar (Pete Hegseth)",
        "rss": "https://nitter.net/SecWar/rss",
        "lang": "en",
        "priority": 1,
        "type": "x_account",
        "handle": "SecWar"
    },
]

IRAN_KEYWORDS = [
    "iran", "iranian", "tehran", "persian", "khamenei", "pezezeshkian", "irgc", "hormuz",
    "ایران", "تهران", "خامنه‌ای", "پهلوی", "سپاه", "تنگه هرمز", "جمهوری اسلامی",
    "reza pahlavi", "netanyahu", "trump iran", "strait of hormuz", "islamic republic"
]

def get_active_sources():
    return SOURCES
