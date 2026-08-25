# -*- coding: utf-8 -*-
"""
فچ مستقیم از RSS خبرگزاری‌ها — بدون گوگل
تیتر کامل + توضیح کامل + منبع → سایت و تلگرام
"""
import hashlib
import logging
import os
import time
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

import feedparser
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from sources import get_active_sources, IRAN_KEYWORDS
from translator import translate_to_persian
from db import init_db, news_exists, insert_news, get_unsent_news, mark_sent, cleanup_old

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

HOURS_BACK = 12
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT = os.getenv("TELEGRAM_CHANNEL_ID")


def is_related(title, desc=""):
    t = (title + " " + (desc or "")).lower()
    return any(k.lower() in t for k in IRAN_KEYWORDS)


def is_garbage(title, desc=""):
    t = (title + " " + (desc or "")).lower()
    bad = [
        "error 500", "server error", "that's an error", "please try again",
        "internal server error", "!!1500", "captcha", "just a moment",
        "access denied", "enable javascript", "cf-browser",
    ]
    return any(b in t for b in bad)


def parse_date(entry):
    for a in ("published_parsed", "updated_parsed"):
        p = getattr(entry, a, None)
        if p:
            try:
                return datetime(*p[:6], tzinfo=timezone.utc)
            except Exception:
                pass
    for a in ("published", "updated"):
        raw = getattr(entry, a, None)
        if raw:
            try:
                return parsedate_to_datetime(raw).astimezone(timezone.utc)
            except Exception:
                pass
    return datetime.now(timezone.utc)


def clean_html(html):
    if not html:
        return ""
    try:
        return BeautifulSoup(html, "lxml").get_text(" ", strip=True)[:1500]
    except Exception:
        return str(html)[:1500]


def fetch_feed(src):
    out = []
    try:
        r = requests.get(
            src["rss"], timeout=10,
            headers={"User-Agent": UA, "Accept": "application/rss+xml, application/xml, text/xml, */*"},
        )
        if r.status_code != 200:
            logger.warning(f"{src['name']} HTTP {r.status_code}")
            return out
        feed = feedparser.parse(r.content)
        cutoff = datetime.now(timezone.utc) - timedelta(hours=HOURS_BACK)
        n = 0
        for e in feed.entries[:30]:
            title = (getattr(e, "title", "") or "").strip()
            if not title:
                continue
            link = getattr(e, "link", "") or ""
            summary = getattr(e, "summary", "") or getattr(e, "description", "") or ""
            if not summary and getattr(e, "content", None):
                try:
                    summary = e.content[0].get("value", "")
                except Exception:
                    pass
            summary = clean_html(summary)
            if is_garbage(title, summary):
                continue
            pub = parse_date(e)
            if pub < cutoff:
                continue
            if not is_related(title, summary):
                continue
            h = hashlib.sha256(f"{title}|{link}".encode()).hexdigest()
            if news_exists(h):
                continue
            out.append({
                "title_original": title,
                "description_original": summary,
                "link": link,
                "source_name": src["name"],
                "published_at": pub.isoformat(),
                "unique_hash": h,
            })
            n += 1
        if n:
            logger.info(f"OK {src['name']}: {n}")
    except requests.Timeout:
        logger.warning(f"TIMEOUT {src['name']}")
    except Exception as e:
        logger.error(f"ERR {src['name']}: {e}")
    return out


def process_and_store(items):
    added = 0
    for item in items:
        try:
            if is_garbage(item["title_original"], item.get("description_original", "")):
                continue
            title_fa = translate_to_persian(item["title_original"])
            desc_o = item.get("description_original") or ""
            desc_fa = translate_to_persian(desc_o) if desc_o else ""
            if is_garbage(title_fa, desc_fa):
                continue
            item["title_fa"] = title_fa
            item["description_fa"] = desc_fa
            item["fetched_at"] = datetime.now(timezone.utc).isoformat()
            if insert_news(item):
                added += 1
                logger.info(f"+ {title_fa[:55]} | {item['source_name']}")
            time.sleep(0.2)
        except Exception as e:
            logger.error(f"process: {e}")
    return added


def send_telegram(item):
    if not TOKEN or not CHAT:
        logger.warning("Telegram env missing")
        return False
    title = item.get("title_fa") or item.get("title_original") or ""
    desc = item.get("description_fa") or item.get("description_original") or ""
    if is_garbage(title, desc):
        return False
    text = (
        f"<b>{title}</b>\n\n"
        f"{desc[:900]}\n\n"
        f"📰 منبع: {item['source_name']}\n"
        f"🔗 <a href=\"{item['link']}\">لینک خبر</a>\n"
        f"🕒 {str(item.get('published_at',''))[:16].replace('T',' ')} UTC"
    )
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": CHAT, "text": text, "parse_mode": "HTML", "disable_web_page_preview": False},
            timeout=15,
        )
        if r.status_code == 200 and r.json().get("ok"):
            logger.info(f"TG OK: {title[:40]}")
            return True
        logger.error(f"TG fail: {r.status_code} {r.text[:150]}")
        return False
    except Exception as e:
        logger.error(f"TG err: {e}")
        return False


def run_fetch_cycle():
    logger.info("=== FETCH START (12h) ===")
    init_db()
    all_items = []
    for src in get_active_sources():
        all_items.extend(fetch_feed(src))
        time.sleep(0.25)
    all_items.sort(key=lambda x: x.get("published_at", ""))
    logger.info(f"candidates: {len(all_items)}")
    added = process_and_store(all_items)
    logger.info(f"stored: {added}")

    for news in sorted(get_unsent_news(40), key=lambda x: x.get("published_at", "")):
        if is_garbage(news.get("title_fa", ""), news.get("description_fa", "")):
            mark_sent(news["id"])
            continue
        if send_telegram(news):
            mark_sent(news["id"])
            time.sleep(1.0)
        else:
            break
    cleanup_old(3)
    logger.info("=== FETCH END ===")
    return added
