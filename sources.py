# -*- coding: utf-8 -*-
"""
لیست بیش از ۳۰ منبع معتبر خبری (فارسی و انگلیسی) که بیشترین پوشش موضوعات ایران را دارند.
شامل خبرگزاری‌های دولتی/نیمه‌دولتی ایران، رسانه‌های بین‌المللی، و حساب‌های مهم X/Twitter.
برای X از RSS عمومی (مثل Nitter یا RSSHub) استفاده شده؛ در صورت نیاز می‌توانید API رسمی اضافه کنید.
"""

SOURCES = [
    # ========== خبرگزاری‌های ایرانی (انگلیسی + فارسی) ==========
    {
        "name": "Mehr News Agency",
        "rss": "https://en.mehrnews.com/rss",
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
        "name": "Tasnim News",
        "rss": "https://www.tasnimnews.com/en/rss/feed/0/7/0/all-stories",
        "lang": "en",
        "priority": 1,
        "type": "agency"
    },
    {
        "name": "IRNA English",
        "rss": "https://en.irna.ir/rss",
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
    {
        "name": "ISNA English",
        "rss": "https://en.isna.ir/rss",
        "lang": "en",
        "priority": 2,
        "type": "agency"
    },
    {
        "name": "Fars News (English proxy / topic)",
        "rss": "https://en.farsnews.ir/rss",
        "lang": "en",
        "priority": 1,
        "type": "agency"
    },
    {
        "name": "Iran Daily",
        "rss": "https://irannewsdaily.com/feed",
        "lang": "en",
        "priority": 2,
        "type": "agency"
    },
    {
        "name": "Kayhan International",
        "rss": "https://kayhan.ir/en/rss",
        "lang": "en",
        "priority": 2,
        "type": "agency"
    },

    # ========== رسانه‌های بین‌المللی با پوشش قوی ایران ==========
    {
        "name": "Al Jazeera - Iran",
        "rss": "https://www.aljazeera.com/xml/rss/all.xml",
        "lang": "en",
        "priority": 1,
        "type": "international",
        "filter_keywords": True
    },
    {
        "name": "BBC News World",
        "rss": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "lang": "en",
        "priority": 1,
        "type": "international",
        "filter_keywords": True
    },
    {
        "name": "Reuters World",
        "rss": "https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best",
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
        "name": "AP News Top",
        "rss": "https://rsshub.app/apnews/topics/apf-topnews",
        "lang": "en",
        "priority": 1,
        "type": "international",
        "filter_keywords": True
    },
    {
        "name": "NYT Middle East / World",
        "rss": "https://rss.nytimes.com/services/xml/rss/nyt/MiddleEast.xml",
        "lang": "en",
        "priority": 1,
        "type": "international",
        "filter_keywords": True
    },
    {
        "name": "Foreign Policy - Iran tag",
        "rss": "https://foreignpolicy.com/tag/iran/feed",
        "lang": "en",
        "priority": 1,
        "type": "international"
    },
    {
        "name": "Politico - Iran",
        "rss": "https://www.politico.com/rss/politics08.xml",
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
        "name": "Middle East Eye",
        "rss": "https://www.middleeasteye.net/rss",
        "lang": "en",
        "priority": 1,
        "type": "international",
        "filter_keywords": True
    },
    {
        "name": "The Jerusalem Post - Iran",
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
        "name": "Anadolu Agency",
        "rss": "https://www.aa.com.tr/en/rss/default?cat=guncel",
        "lang": "en",
        "priority": 2,
        "type": "international",
        "filter_keywords": True
    },

    # ========== رسانه‌های فارسی‌زبان خارج از ایران (پوشش بالا) ==========
    {
        "name": "Iran International",
        "rss": "https://www.iranintl.com/en/rss",
        "lang": "en",
        "priority": 1,
        "type": "diaspora"
    },
    {
        "name": "Radio Farda",
        "rss": "https://www.radiofarda.com/api/zq-$pqoeq",
        "lang": "fa",
        "priority": 1,
        "type": "diaspora"
    },
    {
        "name": "BBC Persian (via mirror / topic)",
        "rss": "https://feeds.bbci.co.uk/persian/rss.xml",
        "lang": "fa",
        "priority": 1,
        "type": "diaspora"
    },
    {
        "name": "VOA Persian",
        "rss": "https://ir.voanews.com/api/z$qitre-$pq",
        "lang": "fa",
        "priority": 1,
        "type": "diaspora"
    },
    {
        "name": "IranWire English",
        "rss": "https://iranwire.com/en/feed/",
        "lang": "en",
        "priority": 1,
        "type": "diaspora"
    },
    {
        "name": "HRANA (Human Rights)",
        "rss": "https://en-hrana.org/articles/feed",
        "lang": "en",
        "priority": 1,
        "type": "diaspora"
    },

    # ========== حساب‌های مهم X / Twitter / Truth Social (از طریق RSS عمومی) ==========
    # توجه: این‌ها ممکن است نیاز به Nitter یا RSSHub داشته باشند. در صورت قطع بودن، از API رسمی استفاده کنید.
    {
        "name": "Reza Pahlavi (@PahlaviReza)",
        "rss": "https://nitter.net/PahlaviReza/rss",
        "lang": "en",
        "priority": 1,
        "type": "x_account",
        "handle": "PahlaviReza"
    },
    {
        "name": "Benjamin Netanyahu (@netanyahu)",
        "rss": "https://nitter.net/netanyahu/rss",
        "lang": "en",
        "priority": 1,
        "type": "x_account",
        "handle": "netanyahu"
    },
    {
        "name": "Donald Trump (@realDonaldTrump)",
        "rss": "https://nitter.net/realDonaldTrump/rss",
        "lang": "en",
        "priority": 1,
        "type": "x_account",
        "handle": "realDonaldTrump"
    },
    {
        "name": "White House Press Secretary",
        "rss": "https://nitter.net/PressSec/rss",
        "lang": "en",
        "priority": 1,
        "type": "x_account",
        "handle": "PressSec"
    },
    {
        "name": "Secretary of War Pete Hegseth (@SecWar)",
        "rss": "https://nitter.net/SecWar/rss",
        "lang": "en",
        "priority": 1,
        "type": "x_account",
        "handle": "SecWar"
    },
    {
        "name": "US Treasury Secretary",
        "rss": "https://nitter.net/SecYellen/rss",  # یا حساب فعلی اسکات بسنت را جایگزین کنید
        "lang": "en",
        "priority": 1,
        "type": "x_account",
        "handle": "SecTreasury"
    },
    {
        "name": "Department of War (@DeptofWar)",
        "rss": "https://nitter.net/DeptofWar/rss",
        "lang": "en",
        "priority": 2,
        "type": "x_account",
        "handle": "DeptofWar"
    },
]

# کلمات کلیدی برای فیلتر اخبار مرتبط با ایران (انگلیسی + فارسی)
IRAN_KEYWORDS = [
    "iran", "iranian", "tehran", "persian", "khamenei", "pezezeshkian", "irgc", "hormuz",
    "ایران", "تهران", "خامنه‌ای", "پهلوی", "سپاه", "تنگه هرمز", "جمهوری اسلامی",
    "reza pahlavi", "netanyahu", "trump iran", "strait of hormuz"
]

def get_active_sources():
    """برگرداندن لیست منابع فعال"""
    return SOURCES
