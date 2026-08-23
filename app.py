# -*- coding: utf-8 -*-
"""
سایت نمایش اخبار جنگ ایران - جدیدترین در بالا
فقط اخبار مرتبط با جنگ + بدون رسانه‌های داخل ایران
"""
from flask import Flask, render_template_string, jsonify, request
from db import init_db, get_latest_news
from fetcher import run_fetch_cycle
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# اجرای اولیه دیتابیس
init_db()

# زمان‌بندی هر ۱ دقیقه + اجرای فوری در استارت
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(
    func=run_fetch_cycle,
    trigger="interval",
    minutes=1,
    id="fetch_news",
    next_run_time=datetime.now()
)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>اخبار جنگ ایران | Iran War News</title>
    <style>
        :root {
            --bg: #0f172a;
            --card: #1e293b;
            --accent: #f43f5e;
            --text: #e2e8f0;
            --muted: #94a3b8;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Vazirmatn', 'Tahoma', system-ui, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.7;
            padding: 1rem;
        }
        header {
            text-align: center;
            padding: 1.5rem 1rem;
            border-bottom: 1px solid #334155;
            margin-bottom: 1.5rem;
        }
        h1 { font-size: 1.8rem; color: var(--accent); }
        .subtitle { color: var(--muted); font-size: 0.95rem; margin-top: 0.4rem; }
        .container { max-width: 900px; margin: 0 auto; }
        .card {
            background: var(--card);
            border-radius: 12px;
            padding: 1.2rem 1.4rem;
            margin-bottom: 1rem;
            border: 1px solid #334155;
            transition: transform 0.15s;
        }
        .card:hover { transform: translateY(-2px); border-color: var(--accent); }
        .title { font-size: 1.15rem; font-weight: 700; margin-bottom: 0.5rem; }
        .title a { color: var(--text); text-decoration: none; }
        .title a:hover { color: var(--accent); }
        .desc { color: var(--muted); font-size: 0.95rem; margin-bottom: 0.8rem; }
        .meta {
            display: flex;
            flex-wrap: wrap;
            gap: 0.8rem;
            font-size: 0.8rem;
            color: #64748b;
        }
        .source { background: #f43f5e; color: white; padding: 0.15rem 0.5rem; border-radius: 4px; font-weight: 600; }
        .refresh {
            display: inline-block;
            margin: 1rem auto;
            background: var(--accent);
            color: white;
            border: none;
            padding: 0.6rem 1.2rem;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
        }
        footer { text-align: center; margin-top: 2rem; color: var(--muted); font-size: 0.85rem; }
        code { background: #334155; padding: 2px 6px; border-radius: 4px; }
        @media (max-width: 600px) {
            h1 { font-size: 1.4rem; }
            .card { padding: 1rem; }
        }
    </style>
    <link href="https://cdn.jsdelivr.net/npm/vazirmatn@33.003/Vazirmatn-font-face.css" rel="stylesheet">
</head>
<body>
    <header>
        <h1>⚔️ اخبار جنگ ایران</h1>
        <p class="subtitle">فقط اخبار مرتبط با جنگ • بدون رسانه‌های داخل ایران • به‌روزرسانی هر ۱ دقیقه • جدیدترین در بالا</p>
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
                ۱ تا ۳ دقیقه صبر کنید یا با POST به <code>/trigger-fetch</code> دستی اجرا کنید.
            </p>
        {% endif %}
    </div>
    <footer>
        Iran War News Agent • فقط اخبار جنگ • بدون رسانه‌های داخلی ایران
    </footer>
</body>
</html>
"""

@app.route("/")
def index():
    news = get_latest_news(limit=80)
    return render_template_string(HTML_TEMPLATE, news=news)

@app.route("/api/news")
def api_news():
    limit = min(int(request.args.get("limit", 50)), 200)
    news = get_latest_news(limit=limit)
    return jsonify(news)

@app.route("/health")
def health():
    return jsonify({"status": "ok", "time": datetime.utcnow().isoformat()})

@app.route("/trigger-fetch", methods=["GET", "POST"])
def trigger():
    """فچ اجباری - مقاوم در برابر خطا"""
    secret = os.getenv("FETCH_SECRET", "")
    if secret and request.headers.get("X-Secret") != secret:
        return jsonify({"error": "unauthorized"}), 401

    logger.info(">>> Manual trigger-fetch called")
    try:
        count = run_fetch_cycle()
        return jsonify({
            "status": "ok",
            "added": count,
            "message": "Fetch finished. Check Telegram + site."
        })
    except Exception as e:
        logger.exception("Trigger failed")
        # حتی در صورت خطا JSON برگردان تا Internal Server Error ندهد
        return jsonify({
            "status": "error",
            "error": str(e),
            "message": "Fetch crashed. Check Render logs for details."
        }), 200  # 200 تا صفحه سفید 500 ندهد

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
