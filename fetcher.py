# -*- coding: utf-8 -*-
"""
ایجنت جمع‌آوری اخبار از همه منابع، فیلتر ایران، ترجمه، ذخیره و ارسال به تلگرام.
"""
import hashlib
import logging
import time
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
import feedparser
import requests
from bs4 import BeautifulSoup

from sources import get_active_sources, IRAN_KEYWORDS
from translator import translate_to_persian
from db import init_db, news_exists, insert_news, get_unsent_news, mark_sent, cleanup_old
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# تنظیمات
HOURS_BACK = 12
USER_AGENT = "IranNewsAgent/1.0 (+https://github.com/yourusername/iran-news-agent)"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")  # مثل @YourChannel یا -100xxxxxxxxxx


def is_iran_related(title: str, description: str = "") -> bool:
    text = (title + " " + (description or "")).lower()
    for kw in IRAN_KEYWORDS:
        if kw.lower() in text:
            return True
    return False


def parse_date(entry) -> datetime:
    """تبدیل تاریخ RSS به datetime با timezone UTC"""
    for attr in ("published_parsed", "updated_parsed"):
        parsed = getattr(entry, attr, None)
        if parsed:
            try:
                return datetime(*parsed[:6], tzinfo=timezone.utc)
            except Exception:
                pass
    # fallback
    for attr in ("published", "updated"):
        raw = getattr(entry, attr, None)
        if raw:
            try:
                return parsedate_to_datetime(raw).astimezone(timezone.utc)
            except Exception:
                pass
    return datetime.now(timezone.utc)


def make_hash(title: str, link: str) -> str:
    raw = (title.strip() + "|" + (link or "")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def clean_html(html: str) -> str:
    if not html:
        return ""
    soup = BeautifulSoup(html, "lxml")
    return soup.get_text(separator=" ", strip=True)[:800]


def fetch_feed(source: dict) -> list:
    """خواندن یک فید RSS و برگرداندن لیست آیتم‌های مرتبط با ایران در ۱۲ ساعت اخیر"""
    results = []
    url = source.get("rss")
    if not url:
        return results

    try:
        feed = feedparser.parse(url, request_headers={"User-Agent": USER_AGENT})
        if feed.bozo and not feed.entries:
            logger.warning(f"Failed to parse {source['name']}: {feed.bozo_exception}")
            return results

        cutoff = datetime.now(timezone.utc) - timedelta(hours=HOURS_BACK)
        force_filter = source.get("filter_keywords", False)

        for entry in feed.entries[:40]:  # حداکثر ۴۰ آیتم از هر منبع
            title = getattr(entry, "title", "") or ""
            link = getattr(entry, "link", "") or ""
            summary = clean_html(getattr(entry, "summary", "") or getattr(entry, "description", "") or "")

            published = parse_date(entry)
            if published < cutoff:
                continue

            # فیلتر ایران
            if force_filter or source.get("type") in ("international", "x_account"):
                if not is_iran_related(title, summary):
                    continue
            # برای منابع ایرانی همه اخبار را قبول می‌کنیم (چون تمرکزشان ایران است)

            unique_hash = make_hash(title, link)
            if news_exists(unique_hash):
                continue

            results.append({
                "title_original": title.strip(),
                "description_original": summary,
                "link": link,
                "source_name": source["name"],
                "published_at": published.isoformat(),
                "unique_hash": unique_hash,
            })
    except Exception as e:
        logger.error(f"Error fetching {source['name']}: {e}")
    return results


def process_and_store(items: list) -> int:
    """ترجمه و ذخیره اخبار جدید"""
    added = 0
    for item in items:
        try:
            title_fa = translate_to_persian(item["title_original"])
            desc_fa = translate_to_persian(item["description_original"]) if item["description_original"] else ""
            item["title_fa"] = title_fa
            item["description_fa"] = desc_fa
            item["fetched_at"] = datetime.now(timezone.utc).isoformat()

            if insert_news(item):
                added += 1
                logger.info(f"Added: {item['title_fa'][:60]}... | {item['source_name']}")
            time.sleep(0.4)  # احترام به rate limit ترجمه
        except Exception as e:
            logger.error(f"Process error: {e}")
    return added


def send_to_telegram(item: dict) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        logger.warning("Telegram credentials not set")
        return False
    try:
        from telegram import Bot
        bot = Bot(token=TELEGRAM_BOT_TOKEN)

        text = (
            f"<b>{item['title_fa']}</b>\n\n"
            f"{item.get('description_fa', '')[:400]}\n\n"
            f"📰 منبع: {item['source_name']}\n"
            f"🔗 <a href=\"{item['link']}\">لینک خبر</a>\n"
            f"🕒 {item['published_at'][:16].replace('T', ' ')} UTC"
        )
        bot.send_message(
            chat_id=TELEGRAM_CHANNEL_ID,
            text=text,
            parse_mode="HTML",
            disable_web_page_preview=False
        )
        return True
    except Exception as e:
        logger.error(f"Telegram send failed: {e}")
        return False


def run_fetch_cycle():
    """یک چرخه کامل جمع‌آوری"""
    logger.info("=== Starting fetch cycle ===")
    init_db()
    sources = get_active_sources()
    all_new = []

    for src in sources:
        logger.info(f"Fetching: {src['name']}")
        items = fetch_feed(src)
        all_new.extend(items)
        time.sleep(1.2)  # فاصله بین درخواست‌ها

    logger.info(f"Found {len(all_new)} potential new items")
    added = process_and_store(all_new)
    logger.info(f"Stored {added} new news items")

    # ارسال به تلگرام
    unsent = get_unsent_news(limit=15)
    for news in unsent:
        if send_to_telegram(news):
            mark_sent(news["id"])
            time.sleep(1.5)
        else:
            break

    cleanup_old(days=5)
    logger.info("=== Fetch cycle finished ===")
    return added


if __name__ == "__main__":
    run_fetch_cycle()
