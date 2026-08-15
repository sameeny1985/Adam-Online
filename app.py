# -*- coding: utf-8 -*-
"""
سایت نمایش اخبار ایران - جدیدترین در بالا
قابل دیپلوی روی Render / Railway / GitHub Pages (با static) یا هر VPS
"""
from flask import Flask, render_template_string, jsonify, request
from db import init_db, get_latest_news
from fetcher import run_fetch_cycle
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import os
from datetime import datetime

app = Flask(__name__)

# اجرای اولیه دیتابیس
init_db()

# ---- زمان‌بندی هر ۱ دقیقه ----
# اولین اجرا بلافاصله بعد از استارت (اخبار ۱۲ ساعت اخیر)
# بعد از آن هر ۱ دقیقه چک می‌کند تا اولین نفر باشیم
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(func=run_fetch_cycle, trigger="interval", minutes=1, id="fetch_news", next_run_time=datetime.now())
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>اخبار لحظه‌ای ایران | Iran News Agent</title>
    <style>
        :root {
            --bg: #0f172a;
            --card: #1e293b;
            --accent: #38bdf8;
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
        .source { background: #0ea5e9; color: #0f172a; padding: 0.15rem 0.5rem; border-radius: 4px; font-weight: 600; }
        .refresh {
            display: inline-block;
            margin: 1rem auto;
            background: var(--accent);
            color: #0f172a;
            border: none;
            padding: 0.6rem 1.2rem;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
        }
        footer { text-align: center; margin-top: 2rem; color: var(--muted); font-size: 0.85rem; }
        @media (max-width: 600px) {
            h1 { font-size: 1.4rem; }
            .card { padding: 1rem; }
        }
    </style>
    <link href="https://cdn.jsdelivr.net/npm/vazirmatn@33.003/Vazirmatn-font-face.css" rel="stylesheet">
</head>
<body>
    <header>
        <h1>🇮🇷 اخبار لحظه‌ای ایران</h1>
        <p class="subtitle">جمع‌آوری از بیش از ۳۰ منبع معتبر جهان • ترجمه خودکار به فارسی • به‌روزرسانی هر ۱ دقیقه • جدیدترین در بالا</p>
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
            <p style="text-align:center;color:var(--muted);padding:3rem;">هنوز خبری ثبت نشده. لطفاً چند دقیقه صبر کنید یا فچر را دستی اجرا کنید.</p>
        {% endif %}
    </div>
    <footer>
        Iran News Agent • ساخته‌شده با Python • قابل دیپلوی روی Render / GitHub
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

@app.route("/trigger-fetch", methods=["POST"])
def trigger():
    """برای تست دستی یا cron خارجی"""
    secret = os.getenv("FETCH_SECRET", "change-me")
    if request.headers.get("X-Secret") != secret:
        return jsonify({"error": "unauthorized"}), 401
    count = run_fetch_cycle()
    return jsonify({"added": count})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
