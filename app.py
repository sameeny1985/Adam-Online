# -*- coding: utf-8 -*-
import os
import logging
import threading
from datetime import datetime
from flask import Flask, jsonify, request, render_template_string

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("iran-news")
app = Flask(__name__)

try:
    from db import init_db
    init_db()
except Exception as e:
    logger.error(f"DB init: {e}")

HTML = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>اخبار جنگ ایران</title>
<style>
body{font-family:Tahoma,sans-serif;background:#0f172a;color:#e2e8f0;padding:1rem;line-height:1.7}
h1{color:#f43f5e;text-align:center}
.card{background:#1e293b;border-radius:10px;padding:1rem;margin:0.8rem 0;border:1px solid #334155}
.card a{color:#e2e8f0;text-decoration:none;font-weight:bold}
.meta{font-size:0.8rem;color:#94a3b8;margin-top:0.5rem}
.source{background:#f43f5e;color:#fff;padding:2px 6px;border-radius:4px}
.empty{text-align:center;color:#94a3b8;padding:3rem}
</style>
</head>
<body>
<h1>⚔️ اخبار جنگ ایران</h1>
{% if news %}
  {% for item in news %}
  <div class="card">
    <a href="{{ item.link }}" target="_blank">{{ item.title_fa or item.title_original }}</a>
    {% if item.description_fa %}<p>{{ item.description_fa[:250] }}...</p>{% endif %}
    <div class="meta"><span class="source">{{ item.source_name }}</span> {{ item.published_at[:16] }}</div>
  </div>
  {% endfor %}
{% else %}
  <p class="empty">هنوز خبری نیست. <a href="/trigger-fetch" style="color:#38bdf8">اینجا</a> را بزنید.</p>
{% endif %}
</body>
</html>
"""

@app.route("/")
def home():
    news = []
    try:
        from db import get_latest_news
        news = get_latest_news(80)
    except Exception as e:
        logger.error(f"home: {e}")
    return render_template_string(HTML, news=news)

@app.route("/health")
def health():
    return jsonify({"ok": True, "time": str(datetime.utcnow())})

def _run_in_background():
    try:
        from fetcher import run_fetch_cycle
        run_fetch_cycle()
    except Exception as e:
        logger.exception(f"background fetch error: {e}")

@app.route("/trigger-fetch", methods=["GET", "POST"])
def trigger():
    """فچ را در پس‌زمینه اجرا می‌کند تا ورکر timeout نشود"""
    try:
        t = threading.Thread(target=_run_in_background, daemon=True)
        t.start()
        return jsonify({
            "status": "ok",
            "message": "Fetch started in background. Wait 30-60 seconds then refresh the site and check Telegram."
        }), 200
    except Exception as e:
        logger.exception("trigger error")
        return jsonify({"status": "error", "error": str(e)}), 200

def start_scheduler():
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from fetcher import run_fetch_cycle
        sch = BackgroundScheduler(daemon=True)
        sch.add_job(run_fetch_cycle, "interval", minutes=3, id="fetch", max_instances=1)
        sch.start()
        logger.info("scheduler started (every 3 min)")
    except Exception as e:
        logger.error(f"scheduler: {e}")

if __name__ == "__main__":
    start_scheduler()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
else:
    try:
        start_scheduler()
    except Exception:
        pass
