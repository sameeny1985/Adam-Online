# -*- coding: utf-8 -*-
import os
import logging
import threading
from datetime import datetime
from flask import Flask, jsonify, render_template_string

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")
app = Flask(__name__)

try:
    from db import init_db
    init_db()
except Exception as e:
    logger.error(e)

HTML = r"""
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>اخبار ایران | منابع راست</title>
<style>
body{font-family:Tahoma,sans-serif;background:#0f172a;color:#e2e8f0;margin:0;padding:1rem;line-height:1.75}
h1{color:#f43f5e;text-align:center;font-size:1.5rem;margin:0 0 .3rem}
.sub{text-align:center;color:#94a3b8;font-size:.88rem;margin-bottom:1rem}
.card{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:1.1rem 1.25rem;margin:0 auto .85rem;max-width:820px}
.card .t{color:#f1f5f9;font-weight:700;font-size:1.1rem;text-decoration:none;display:block;margin-bottom:.4rem}
.card .t:hover{color:#f43f5e}
.card .d{color:#cbd5e1;font-size:.96rem;margin:.4rem 0 .6rem;white-space:pre-wrap}
.meta{font-size:.8rem;color:#64748b;display:flex;gap:.5rem;flex-wrap:wrap;align-items:center}
.src{background:#f43f5e;color:#fff;padding:2px 8px;border-radius:4px;font-weight:600}
.dot{display:inline-block;width:8px;height:8px;background:#22c55e;border-radius:50%;animation:p 1.4s infinite}
@keyframes p{50%{opacity:.35}}
#empty{text-align:center;color:#94a3b8;padding:2.5rem}
</style>
</head>
<body>
<h1>⚔️ اخبار ایران و جنگ</h1>
<p class="sub">منابع مستقیم راست / طرف ترامپ • تیتر و توضیح کامل • به‌روزرسانی خودکار هر ۱ دقیقه <span class="dot"></span></p>
<div id="list">
{% if news %}
{% for item in news %}
<article class="card">
  <a class="t" href="{{ item.link }}" target="_blank" rel="noopener">{{ item.title_fa or item.title_original }}</a>
  {% if item.description_fa %}<div class="d">{{ item.description_fa }}</div>
  {% elif item.description_original %}<div class="d">{{ item.description_original }}</div>{% endif %}
  <div class="meta"><span class="src">{{ item.source_name }}</span><span>{{ item.published_at[:16] }} UTC</span></div>
</article>
{% endfor %}
{% else %}
<p id="empty">در حال دریافت اخبار ۱۲ ساعت اخیر… چند لحظه صبر کنید.</p>
{% endif %}
</div>
<script>
function esc(s){return (s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");}
function render(items){
  var box=document.getElementById("list");
  if(!items||!items.length){box.innerHTML='<p id="empty">هنوز خبری نیست. چند لحظه دیگر…</p>';return;}
  var h="";
  for(var i=0;i<items.length;i++){
    var it=items[i];
    var title=esc(it.title_fa||it.title_original||"");
    var desc=esc(it.description_fa||it.description_original||"");
    var src=esc(it.source_name||"");
    var pub=esc((it.published_at||"").slice(0,16));
    var link=esc(it.link||"#");
    h+='<article class="card"><a class="t" href="'+link+'" target="_blank" rel="noopener">'+title+'</a>';
    if(desc) h+='<div class="d">'+desc+'</div>';
    h+='<div class="meta"><span class="src">'+src+'</span><span>'+pub+' UTC</span></div></article>';
  }
  box.innerHTML=h;
}
function refresh(){
  fetch("/api/news?limit=80").then(function(r){return r.json();}).then(render).catch(function(){});
}
setInterval(refresh, 60000);
</script>
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
        logger.error(e)
    return render_template_string(HTML, news=news)

@app.route("/api/news")
def api_news():
    try:
        from db import get_latest_news
        from flask import request
        limit = min(int(request.args.get("limit", 80)), 150)
        return jsonify(get_latest_news(limit))
    except Exception as e:
        return jsonify({"error": str(e)}), 200

@app.route("/health")
def health():
    return jsonify({"ok": True})

def _bg():
    try:
        from fetcher import run_fetch_cycle
        run_fetch_cycle()
    except Exception as e:
        logger.exception(e)

@app.route("/trigger-fetch", methods=["GET", "POST"])
def trigger():
    threading.Thread(target=_bg, daemon=True).start()
    return jsonify({"status": "ok", "message": "Fetch started in background. Wait 60-90s."}), 200

def start_scheduler():
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from fetcher import run_fetch_cycle
        sch = BackgroundScheduler(daemon=True)
        sch.add_job(run_fetch_cycle, "interval", minutes=1, id="fetch",
                    max_instances=1, next_run_time=datetime.utcnow())
        sch.start()
        logger.info("scheduler every 1 min + immediate")
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
