# -*- coding: utf-8 -*-
"""
سایت اخبار جنگ ایران - نسخه مقاوم در برابر کرش
"""
import os
import logging
from datetime import datetime

from flask import Flask, render_template_string, jsonify, request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ---- دیتابیس ----
try:
    from db import init_db, get_latest_news
    init_db()
except Exception as e:
    logger.error(f"DB init failed: {e}")

# ---- زمان‌بندی (اگر خطا داد، سایت حداقل بالا می‌آید) ----
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from fetcher import run_fetch_cycle
    import atexit

    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(
        func=run_fetch_cycle,
        trigger="interval",
        minutes=2,          # کمی کمتر تهاجمی برای Render رایگان
        id="fetch_news",
        next_run_time=datetime.now()
    )
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown(wait=False))
    logger.info("Scheduler started")
except Exception as e:
    logger.error(f"Scheduler failed to start: {e}")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>اخبار جنگ ایران</title>
    <style>
        :root { --bg:#0f172a; --card:#1e293b; --accent:#f43f5e; --text:#e2e8f0; --muted:#94a3b8; }
        * { box-sizing:border-box; margin:0; padding:0; }
        body { font-family: Tahoma, system-ui, sans-serif; background:var(--bg); color:var(--text); line-height:1.7; padding:1rem; }
        header { text-align:center; padding:1.5rem 1rem; border-bottom:1px solid #334155; margin-bottom:1.5rem; }
        h1 { font-size:1.8rem; color:var(--accent); }
        .subtitle { color:var(--muted); font-size:0.95rem; margin-top:0.4rem; }
        .container { max-width:900px; margin:0 auto; }
        .card { background:var(--card); border-radius:12px; padding:1.2rem 1.4rem; margin-bottom:1rem; border:1px solid #334155; }
        .title { font-size:1.15rem; font-weight:700; margin-bottom:0.5rem; }
        .title a { color:var(--text); text-decoration:none; }
        .title a:hover { color:var(--accent); }
        .desc { color:var(--muted); font-size:0.95rem; margin-bottom:0.8rem; }
        .meta { display:flex; flex-wrap:wrap; gap:0.8rem; font-size:0.8rem; color:#64748b; }
        .source { background:#f43f5e; color:white; padding:0.15rem 0.5rem; border-radius:4px; font-weight:600; }
        .refresh { display:inline-block; margin:1rem auto; background:var(--accent); color:white; border:none; padding:0.6rem 1.2rem; border-radius:8px; cursor:pointer; font-weight:600; }
        footer { text-align:center; margin-top:2rem; color:var(--muted); font-size:0.85rem; }
    </style>
</head>
<body>
    <header>
        <h1>⚔️ اخبار جنگ ایران</h1>
        <p class="subtitle">فقط اخبار مرتبط با جنگ • بدون رسانه‌های داخل ایران • جدیدترین در بالا</p>
        <button class="refresh" onclick="location.reload()">بروزرسانی صفحه</button>
    </header>
    <div class="container">
        {% if news %}
            {% for item in news %}
            <article class="card">
                <div class="title">
                    <a href="{{ item.link }}" target="_blank" rel="noopener">{{ item.title_fa or item.title_original }}</a>
                </div>
                {% if item.description_fa %}
                <p class="desc">{{ item.description_fa[:280] }}{% if item.description_fa|length > 280 %}...{% endif %}</p>
                {% endif %}
                <div class="meta">
                    <span class="source">{{ item.source_name }}</span>
                    <span>{{ item.published_at[:16].replace('T', ' ') }} UTC</span>
                </div>
            </article>
            {% endfor %}
        {% else %}
            <p style="text-align:center;color:var(--muted);padding:3rem;">
                هنوز خبری ثبت نشده.<br>
                ۱ تا ۳ دقیقه صبر کنید یا <a href="/trigger-fetch" style="color:#38bdf8">اینجا</a> را بزنید.
            </p>
        {% endif %}
    </div>
    <footer>Iran War News Agent</footer>
</body>
</html>
"""

@app.route("/")
def index():
    try:
        from db import get_latest_news
        news = get_latest_news(limit=80)
    except Exception as e:
        logger.error(f"index error: {e}")
        news = []
    return render_template_string(HTML_TEMPLATE, news=news)

@app.route("/api/news")
def api_news():
    try:
        from db import get_latest_news
        limit = min(int(request.args.get("limit", 50)), 200)
        return jsonify(get_latest_news(limit=limit))
    except Exception as e:
        return jsonify({"error": str(e)}), 200

@app.route("/health")
def health():
    return jsonify({"status": "ok", "time": datetime.utcnow().isoformat()})

@app.route("/trigger-fetch", methods=["GET", "POST"])
def trigger():
    """
    این endpoint تقریباً غیرممکن است که Internal Server Error بدهد.
    همیشه JSON برمی‌گرداند.
    """
    result = {
        "status": "unknown",
        "added": 0,
        "message": "",
        "error": None
    }
    try:
        secret = os.getenv("FETCH_SECRET", "")
        if secret and request.headers.get("X-Secret") != secret:
            result["status"] = "unauthorized"
            result["message"] = "Wrong or missing X-Secret header"
            return jsonify(result), 200

        logger.info(">>> trigger-fetch started")
        from fetcher import run_fetch_cycle
        count = run_fetch_cycle()
        result["status"] = "ok"
        result["added"] = count
        result["message"] = f"Fetch finished. {count} new items. Check Telegram + site."
        logger.info(f">>> trigger-fetch done, added={count}")
    except Exception as e:
        logger.exception("trigger-fetch crashed")
        result["status"] = "error"
        result["error"] = str(e)
        result["message"] = "Fetch crashed. See error field and Render logs."
    return jsonify(result), 200   # همیشه 200 تا صفحه سفید 500 نبینید

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
