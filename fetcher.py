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
    """خواندن یک فید RSS با timeout قوی تا hang نشود"""
    results = []
    url = source.get("rss")
    if not url:
        return results

    try:
        resp = requests.get(
            url,
            timeout=12,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "application/rss+xml, application/xml, text/xml, */*"
            },
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
        force_filter = True  # همیشه فیلتر جنگ
        count_ok = 0

        for entry in feed.entries[:35]:
            title = (getattr(entry, "title", "") or "").strip()
            if not title:
                continue
            link = getattr(entry, "link", "") or ""
            summary = clean_html(getattr(entry, "summary", "") or getattr(entry, "description", "") or "")

            published = parse_date(entry)
            if published < cutoff:
                continue

            if force_filter or source.get("type") in ("international", "x_account"):
                if not is_iran_related(title, summary):
                    continue

            unique_hash = make_hash(title, link)
            if news_exists(unique_hash):
                continue

            results.append({
                "title_original": title,
                "description_original": summary,
                "link": link,
                "source_name": source["name"],
                "published_at": published.isoformat(),
                "unique_hash": unique_hash,
            })
            count_ok += 1

        if count_ok:
            logger.info(f"✓ {source['name']} → {count_ok} item(s)")
    except requests.Timeout:
        logger.warning(f"⏱ {source['name']} → TIMEOUT")
    except Exception as e:
        logger.error(f"✗ {source['name']} → {e}")
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
    """
    یک چرخه کامل جمع‌آوری:
    - اولین اجرا: همه اخبار ۱۲ ساعت اخیر
    - اجراهای بعدی: فقط خبرهای جدید (هر ۱ دقیقه)
    - اخبار جدید بلافاصله بالای سایت می‌آیند
    - در تلگرام از قدیمی به جدید فرستاده می‌شوند تا جدیدترین در پایین کانال باشد
    """
    logger.info("=== Starting fetch cycle (every 1 minute) ===")
    init_db()
    sources = get_active_sources()
    all_new = []

    for src in sources:
        logger.info(f"Fetching: {src['name']}")
        items = fetch_feed(src)
        all_new.extend(items)
        time.sleep(0.8)  # کمی سریع‌تر چون هر دقیقه اجرا می‌شود

    logger.info(f"Found {len(all_new)} potential new items")
    added = process_and_store(all_new)
    logger.info(f"Stored {added} new news items")

    # ارسال به تلگرام: از قدیمی‌ترین به جدیدترین
    # تا جدیدترین پیام در پایین کانال ظاهر شود
    unsent = get_unsent_news(limit=30)
    # مرتب‌سازی صعودی بر اساس زمان انتشار
    unsent_sorted = sorted(unsent, key=lambda x: x["published_at"])

    for news in unsent_sorted:
        if send_to_telegram(news):
            mark_sent(news["id"])
            time.sleep(1.2)  # فاصله برای جلوگیری از rate limit تلگرام
        else:
            break

    cleanup_old(days=3)
    logger.info("=== Fetch cycle finished ===")
    return added


if __name__ == "__main__":
    run_fetch_cycle()
