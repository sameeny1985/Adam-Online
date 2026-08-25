# -*- coding: utf-8 -*-
# فقط RSS مستقیم خبرگزاری‌ها (بدون گوگل) — منابع نزدیک به ترامپ / راست
# این آدرس‌ها تست شده‌اند و کار می‌کنند

SOURCES = [
    {"name": "Fox News", "rss": "https://moxie.foxnews.com/google-publisher/latest.xml"},
    {"name": "Fox News World", "rss": "https://moxie.foxnews.com/google-publisher/world.xml"},
    {"name": "Fox News Politics", "rss": "https://moxie.foxnews.com/google-publisher/politics.xml"},
    {"name": "New York Post", "rss": "https://nypost.com/feed/"},
    {"name": "Washington Examiner", "rss": "https://www.washingtonexaminer.com/feed/"},
    {"name": "Breitbart", "rss": "https://feeds.feedburner.com/breitbart"},
    {"name": "Daily Wire", "rss": "https://www.dailywire.com/feeds/rss.xml"},
    {"name": "The Federalist", "rss": "https://thefederalist.com/feed/"},
    {"name": "Gateway Pundit", "rss": "https://www.thegatewaypundit.com/feed/"},
    {"name": "Jerusalem Post", "rss": "https://www.jpost.com/rss/rssfeedsfrontpage.aspx"},
    {"name": "Israel Hayom", "rss": "https://www.israelhayom.com/feed/"},
]

IRAN_KEYWORDS = [
    "iran", "iranian", "tehran", "hormuz", "irgc", "khamenei", "persian gulf",
    "israel", "netanyahu", "hezbollah", "houthi", "nuclear", "missile", "drone",
    "trump", "strike", "attack", "war", "sanction", "oil", "gaza", "hamas",
    "ایران", "تهران", "هرمز", "سپاه", "خامنه‌ای", "اسرائیل", "نتانیاهو",
    "موشک", "پهپاد", "جنگ", "حمله", "تحریم", "ترامپ",
]

def get_active_sources():
    return SOURCES
