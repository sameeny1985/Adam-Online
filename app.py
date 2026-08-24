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
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>اخبار جنگ ایران</title>
<style>
:root { --bg:#0f172a; --card:#1e293b; --accent:#f43f5e; --text:#e2e8f0; --muted:#94a3b8; }
* { box-sizing:border-box; margin:0; padding:0; }
body { font-family:Tahoma, system-ui, sans-serif; background:var(--bg); color:var(--text); line-height:1.7; padding:1rem; }
h1 { color:var(--accent); text-align:center; font-size:1.7rem; margin-bottom:0.3rem; }
.subtitle { text-align:center; color:var(--muted); font-size:0.9rem; margin-bottom:1.2rem; }
.reader-wrap { text-align:center; margin:1rem 0 1.5rem; }
.glass-btn {
  display:inline-flex; align-items:center; gap:0.5rem;
  padding:0.75rem 1.6rem; border:none; border-radius:14px; cursor:pointer;
  font-size:1.05rem; font-weight:700; color:#fff;
  background: rgba(255,255,255,0.12);
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255,255,255,0.25);
  box-shadow: 0 8px 32px rgba(0,0,0,0.3);
  transition: all 0.2s ease;
}
.glass-btn:hover { background: rgba(244,63,94,0.35); border-color: rgba(244,63,94,0.6); transform: translateY(-2px); }
.glass-btn.playing { background: rgba(244,63,94,0.5); border-color: #f43f5e; }
.glass-btn:disabled { opacity:0.5; cursor:not-allowed; }
.card {
  background:var(--card); border-radius:12px; padding:1.1rem 1.3rem;
  margin-bottom:0.9rem; border:1px solid #334155; transition: border-color 0.2s;
}
.card.reading { border-color: var(--accent); box-shadow: 0 0 0 2px rgba(244,63,94,0.25); }
.card a { color:var(--text); text-decoration:none; font-weight:700; font-size:1.08rem; }
.card a:hover { color:var(--accent); }
.desc { color:var(--muted); font-size:0.95rem; margin:0.45rem 0; }
.meta { font-size:0.8rem; color:#64748b; display:flex; flex-wrap:wrap; gap:0.6rem; margin-top:0.4rem; }
.source { background:var(--accent); color:#fff; padding:2px 8px; border-radius:4px; font-weight:600; }
.empty { text-align:center; color:var(--muted); padding:3rem; }
.status { text-align:center; color:var(--muted); font-size:0.85rem; min-height:1.4em; margin-top:0.4rem; }
</style>
</head>
<body>
<h1>⚔️ اخبار جنگ ایران</h1>
<p class="subtitle">جدیدترین خبرها • ترجمه فارسی</p>

<div class="reader-wrap">
  <button class="glass-btn" id="readerBtn" onclick="toggleReader()">
    <span id="readerIcon">🔊</span>
    <span id="readerLabel">خبرخوان</span>
  </button>
  <p class="status" id="readerStatus"></p>
</div>

{% if news %}
  <div id="newsList">
  {% for item in news %}
  <div class="card" data-title="{{ (item.title_fa or item.title_original)|e }}" data-desc="{{ (item.description_fa or '')|e }}">
    <a href="{{ item.link }}" target="_blank" rel="noopener">{{ item.title_fa or item.title_original }}</a>
    {% if item.description_fa and 'Error 500' not in item.description_fa and 'Server Error' not in item.description_fa and 'Please try again' not in item.description_fa %}
    <p class="desc">{{ item.description_fa[:400] }}</p>
    {% endif %}
    <div class="meta">
      <span class="source">{{ item.source_name }}</span>
      <span>{{ item.published_at[:16] }}</span>
    </div>
  </div>
  {% endfor %}
  </div>
{% else %}
  <p class="empty">هنوز خبری نیست. <a href="/trigger-fetch" style="color:#38bdf8">اینجا</a> را بزنید.</p>
{% endif %}

<script>
(function() {
  let reading = false;
  let current = 0;
  let cards = [];
  const synth = window.speechSynthesis;

  function loadVoices() {
    return new Promise((resolve) => {
      let voices = synth.getVoices();
      if (voices.length) { resolve(voices); return; }
      synth.onvoiceschanged = () => resolve(synth.getVoices());
      setTimeout(() => resolve(synth.getVoices()), 1000);
    });
  }

  function pickVoice(voices) {
    return voices.find(v => /fa(-|_)?IR|Persian|Farsi/i.test(v.lang + " " + v.name))
        || voices.find(v => /^fa/i.test(v.lang))
        || voices.find(v => /^ar/i.test(v.lang))
        || voices.find(v => /^en/i.test(v.lang))
        || voices[0] || null;
  }

  function setStatus(msg) {
    var el = document.getElementById("readerStatus");
    if (el) el.textContent = msg || "";
  }

  function highlight(i) {
    cards.forEach(function(c, idx) { c.classList.toggle("reading", idx === i); });
    if (cards[i]) cards[i].scrollIntoView({ behavior: "smooth", block: "center" });
  }

  function speak(text) {
    return new Promise(function(resolve) {
      if (!text || !String(text).trim()) { resolve(); return; }
      try { synth.cancel(); } catch (e) {}
      var u = new SpeechSynthesisUtterance(String(text).trim());
      u.lang = "fa-IR";
      u.rate = 0.9;
      u.volume = 1;
      var voice = pickVoice(synth.getVoices());
      if (voice) { u.voice = voice; u.lang = voice.lang || "fa-IR"; }
      var done = false;
      function finish() { if (done) return; done = true; resolve(); }
      u.onend = finish;
      u.onerror = function(e) { console.warn("speech error", e); setStatus("خطا در پخش صدا"); finish(); };
      setTimeout(function() {
        try { synth.speak(u); } catch (err) { console.error(err); finish(); }
      }, 80);
      setTimeout(finish, Math.min(90000, Math.max(4000, text.length * 90)));
    });
  }

  async function readNext() {
    if (!reading) return;
    if (current >= cards.length) { stopReader(); setStatus("پایان خواندن"); return; }
    var card = cards[current];
    var title = card.getAttribute("data-title") || "";
    var desc = card.getAttribute("data-desc") || "";
    var text = (title + (desc ? ". " + desc : "")).trim();
    setStatus("در حال خواندن خبر " + (current + 1) + " از " + cards.length + "…");
    highlight(current);
    await speak(text);
    if (!reading) return;
    current += 1;
    readNext();
  }

  async function startReader() {
    cards = Array.from(document.querySelectorAll("#newsList .card"));
    if (!cards.length) { setStatus("خبری برای خواندن نیست"); return; }
    if (!window.speechSynthesis) { setStatus("مرورگر شما از خواندن متن پشتیبانی نمی‌کند"); return; }

    setStatus("در حال آماده‌سازی صدا…");
    var voices = await loadVoices();
    if (!voices.length) {
      setStatus("صدایی پیدا نشد. در ویندوز Settings > Time & Language > Speech یک صدا نصب کنید.");
      return;
    }

    reading = true;
    current = 0;
    document.getElementById("readerBtn").classList.add("playing");
    document.getElementById("readerLabel").textContent = "توقف";
    document.getElementById("readerIcon").textContent = "⏹";

    await speak("شروع خبرخوان");
    if (!reading) return;
    readNext();
  }

  function stopReader() {
    reading = false;
    try { synth.cancel(); } catch (e) {}
    cards.forEach(function(c) { c.classList.remove("reading"); });
    var btn = document.getElementById("readerBtn");
    if (btn) btn.classList.remove("playing");
    var label = document.getElementById("readerLabel");
    if (label) label.textContent = "خبرخوان";
    var icon = document.getElementById("readerIcon");
    if (icon) icon.textContent = "🔊";
  }

  window.toggleReader = function() {
    if (reading) { stopReader(); setStatus("متوقف شد"); }
    else startReader();
  };

  loadVoices();
})();
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


@app.route("/cleanup-garbage")
def cleanup_garbage():
    """پاک کردن خبرهای Error 500 از دیتابیس"""
    try:
        from db import get_connection
        conn = get_connection()
        c = conn.cursor()
        c.execute("""
            DELETE FROM news WHERE
            lower(coalesce(title_original,'')) LIKE '%error 500%' OR
            lower(coalesce(title_fa,'')) LIKE '%error 500%' OR
            lower(coalesce(title_original,'')) LIKE '%server error%' OR
            lower(coalesce(title_fa,'')) LIKE '%server error%' OR
            lower(coalesce(title_original,'')) LIKE '%that%error%' OR
            lower(coalesce(title_fa,'')) LIKE '%that%error%' OR
            lower(coalesce(description_original,'')) LIKE '%error 500%' OR
            lower(coalesce(description_fa,'')) LIKE '%error 500%' OR
            lower(coalesce(description_original,'')) LIKE '%server error%' OR
            lower(coalesce(description_fa,'')) LIKE '%server error%' OR
            lower(coalesce(description_original,'')) LIKE '%please try again%' OR
            lower(coalesce(description_fa,'')) LIKE '%please try again%' OR
            lower(coalesce(description_original,'')) LIKE '%!!1500%' OR
            lower(coalesce(description_fa,'')) LIKE '%!!1500%'
        """)
        deleted = c.rowcount
        conn.commit()
        conn.close()
        return jsonify({"status": "ok", "deleted": deleted, "message": f"Deleted {deleted} garbage items"})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 200

if __name__ == "__main__":
    start_scheduler()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
else:
    try:
        start_scheduler()
    except Exception:
        pass
