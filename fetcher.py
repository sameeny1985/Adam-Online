# -*- coding: utf-8 -*-
"""
ایجنت جمع‌آوری اخبار جنگ - نسخه سریع و پایدار
"""
import hashlib
import logging
import time
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
import feedparser
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

from sources import get_active_sources, IRAN_KEYWORDS
from translator import translate_to_persian
from db import init_db, news_exists, insert_news, get_unsent_news, mark_sent, cleanup_old

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

HOURS_BACK = 12
USER_AGENT = "Mozilla/5.0 (compatible; IranWarNews/1.0)"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")


def is_iran_related(title: str, description: str = "") -> bool:
    text = (title + " " + (description or "")).lower()
    return any(kw.lower() in text for kw in IRAN_KEYWORDS)


def is_garbage(title: str, description: str = "") -> bool:
    """فیلتر سخت‌گیرانه خطاها و محتوای بی‌معنی"""
    t = (title + " " + (description or "")).lower()
    bad = [
        "error 500", "server error", "that’s an error", "thats an error",
        "please try again later", "that’s all we know", "internal server error",
        "502 bad gateway", "503 service", "404 not found", "access denied",
        "captcha", "unusual traffic", "enable javascript", "robot check",
        "!!1500", "error!!", "there was an error", "try again later",
        "that is an error", "all we know", "http error", "page not found",
        "temporarily unavailable", "service unavailable", "just a moment"
    ]
    if any(b in t for b in bad):
        return True
    clean = (title or "").strip()
    if len(clean) < 20:
        return True
    if clean.lower().startswith("error"):
        return True
    return False


def parse_date(entry) -> datetime:
    for attr in ("published_parsed", "updated_parsed"):
        parsed = getattr(entry, attr, None)
        if parsed:
            try:
                return datetime(*parsed[:6], tzinfo=timezone.utc)
            except Exception:
                pass
    for attr in ("published", "updated"):
        raw = getattr(entry, attr, None)
        if raw:
            try:
                return parsedate_to_datetime(raw).astimezone(timezone.utc)
            except Exception:
                pass
    return datetime.now(timezone.utc)


def make_hash(title: str, link: str) -> str:
    return hashlib.sha256((title.strip() + "|" + (link or "")).encode()).hexdigest()


def clean_html(html: str) -> str:
    if not html:
        return ""
    try:
        return BeautifulSoup(html, "lxml").get_text(" ", strip=True)[:600]
    except Exception:
        return str(html)[:600]


def fetch_feed(source: dict) -> list:
    results = []
    url = source.get("rss")
    if not url:
        return results
    try:
        resp = requests.get(
            url,
            timeout=8,  # کوتاه‌تر تا ورکر timeout نشود
            headers={"User-Agent": USER_AGENT, "Accept": "application/rss+xml, application/xml, text/xml, */*"},
            allow_redirects=True
        )
        if resp.status_code != 200:
            logger.warning(f"{source['name']} → HTTP {resp.status_code}")
            return results

        feed = feedparser.parse(resp.content)
        if not feed.entries:
            logger.warning(f"{source['name']} → 0 entries")
            return results

        cutoff = datetime.now(timezone.utc) - timedelta(hours=HOURS_BACK)
        count = 0
        for entry in feed.entries[:25]:
            title = (getattr(entry, "title", "") or "").strip()
            if not title:
                continue
            link = getattr(entry, "link", "") or ""
            summary = clean_html(getattr(entry, "summary", "") or getattr(entry, "description", "") or "")

            if is_garbage(title, summary):
                continue

            published = parse_date(entry)
            if published < cutoff:
                continue

            if not is_iran_related(title, summary):
                continue

            h = make_hash(title, link)
            if news_exists(h):
                continue

            results.append({
                "title_original": title,
                "description_original": summary,
                "link": link,
                "source_name": source["name"],
                "published_at": published.isoformat(),
                "unique_hash": h,
            })
            count += 1
        if count:
            logger.info(f"✓ {source['name']} → {count} item(s)")
    except requests.Timeout:
        logger.warning(f"⏱ {source['name']} → TIMEOUT")
    except Exception as e:
        logger.error(f"✗ {source['name']} → {e}")
    return results


def process_and_store(items: list) -> int:
    added = 0
    for item in items:
        try:
            title_o = item.get("title_original", "")
            desc_o = item.get("description_original", "") or ""

            # اگر عنوان یا توضیح خراب باشد، رد کن
            if is_garbage(title_o, desc_o):
                logger.warning(f"SKIP garbage before translate: {title_o[:50]}")
                continue

            title_fa = translate_to_persian(title_o)
            desc_fa = translate_to_persian(desc_o) if desc_o else ""

            # بعد از ترجمه دوباره چک کن
            if is_garbage(title_fa, desc_fa):
                logger.warning(f"SKIP garbage after translate: {title_fa[:50]}")
                continue

            # اگر توضیح فقط Error بود، خالی بگذار
            if is_garbage("", desc_fa):
                desc_fa = ""

            item["title_fa"] = title_fa
            item["description_fa"] = desc_fa
            item["fetched_at"] = datetime.now(timezone.utc).isoformat()
            if insert_news(item):
                added += 1
                logger.info(f"Added: {title_fa[:55]}... | {item['source_name']}")
            time.sleep(0.3)
        except Exception as e:
            logger.error(f"Process error: {e}")
    return added


def send_to_telegram(item: dict) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        logger.warning("Telegram credentials not set")
        return False
    try:
        text = (
            f"<b>{item['title_fa']}</b>\n\n"
            f"{item.get('description_fa', '')[:350]}\n\n"
            f"📰 منبع: {item['source_name']}\n"
            f"🔗 <a href=\"{item['link']}\">لینک خبر</a>\n"
            f"🕒 {item['published_at'][:16].replace('T', ' ')} UTC"
        )
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        r = requests.post(url, json={
            "chat_id": TELEGRAM_CHANNEL_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }, timeout=12)
        if r.status_code == 200 and r.json().get("ok"):
            logger.info(f"Telegram OK: {item['title_fa'][:45]}")
            return True
        logger.error(f"Telegram API: {r.status_code} {r.text[:150]}")
        return False
    except Exception as e:
        logger.error(f"Telegram send failed: {e}")
        return False


def run_fetch_cycle():
    logger.info("=== Starting fetch cycle ===")
    init_db()
    all_new = []
    for src in get_active_sources():
        logger.info(f"Fetching: {src['name']}")
        all_new.extend(fetch_feed(src))
        time.sleep(0.4)

    logger.info(f"Found {len(all_new)} potential new items")
    added = process_and_store(all_new)
    logger.info(f"Stored {added} new news items")

    unsent = sorted(get_unsent_news(30), key=lambda x: x["published_at"])
    for news in unsent:
        title_check = (news.get("title_fa") or "") + " " + (news.get("title_original") or "")
        desc_check = (news.get("description_fa") or "") + " " + (news.get("description_original") or "")
        if is_garbage(title_check, desc_check):
            logger.warning(f"SKIP garbage: {title_check[:60]}")
            mark_sent(news["id"])
            continue
        if send_to_telegram(news):
            mark_sent(news["id"])
            time.sleep(1.0)
        else:
            break

    cleanup_old(3)
    logger.info("=== Fetch cycle finished ===")
    return added


if __name__ == "__main__":
    run_fetch_cycle()
