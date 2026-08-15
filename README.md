# 🇮🇷 Iran News Agent

ایجنت پایتون برای جمع‌آوری **لحظه‌ای** اخبار مرتبط با ایران از **بیش از ۳۰ منبع معتبر** جهان (خبرگزاری‌های ایرانی + بین‌المللی + حساب‌های مهم X).

### ویژگی‌ها
- فیلتر فقط اخبار مربوط به ایران (۱۲ ساعت اخیر)
- ترجمه خودکار عنوان و خلاصه به فارسی با کیفیت بالا (Google Translate)
- نمایش روی سایت ساده و زیبا (جدیدترین بالا)
- ارسال خودکار به کانال تلگرام
- آماده دیپلوی روی **GitHub + Render** (یا Railway / VPS)
- دیتابیس SQLite سبک و بدون نیاز به سرویس خارجی

---

## منابع انتخاب‌شده (بر اساس میزان پوشش موضوعات ایران)

**خبرگزاری‌های ایرانی:**  
Mehr, Tehran Times, Tasnim, IRNA (EN + FA), Press TV, ISNA, Fars, Iran Daily, Kayhan

**بین‌المللی:**  
Al Jazeera, BBC, Reuters, Guardian, France 24, AP, NYT, Foreign Policy, Politico, DW, Middle East Eye, Jerusalem Post, Arab News, Anadolu

**رسانه‌های فارسی خارج:**  
Iran International, Radio Farda, BBC Persian, VOA Persian, IranWire, HRANA

**حساب‌های مهم X/Twitter:**  
- رضا پهلوی (`@PahlaviReza`)
- نتانیاهو (`@netanyahu`)
- ترامپ (`@realDonaldTrump`)
- سخنگوی کاخ سفید (`@PressSec`)
- وزیر جنگ آمریکا (Pete Hegseth – `@SecWar`)
- وزیر خزانه‌داری
- Department of War (`@DeptofWar`)

> برای حساب‌های X از Nitter RSS استفاده شده. اگر قطع شد، می‌توانید RSSHub یا API رسمی X را جایگزین کنید.

---

## نصب و اجرا محلی

```bash
git clone https://github.com/YOUR_USERNAME/iran-news-agent.git
cd iran-news-agent
python -m venv venv
source venv/bin/activate   # ویندوز: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# فایل .env را ویرایش کنید و توکن تلگرام را بگذارید
python fetcher.py          # تست یک‌بار فچ
python app.py              # اجرای سایت روی http://localhost:5000
```

---

## دیپلوی روی Render (رایگان)

1. ریپو را روی GitHub بگذارید.
2. به [render.com](https://render.com) بروید → New → Web Service.
3. ریپو را انتخاب کنید.
4. تنظیمات:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`
   - Environment Variables:
     - `TELEGRAM_BOT_TOKEN`
     - `TELEGRAM_CHANNEL_ID`
     - `FETCH_SECRET` (اختیاری)
5. Deploy کنید.

### فچ دوره‌ای روی Render رایگان
Render رایگان خواب می‌رود. دو راه:
- از سرویس رایگان مثل [cron-job.org](https://cron-job.org) هر ۱۵ دقیقه به endpoint زیر درخواست POST بزنید:
  ```
  POST https://YOUR-APP.onrender.com/trigger-fetch
  Header: X-Secret: your-secret
  ```
- یا یک Background Worker جدا بسازید که فقط `python fetcher.py` را در حلقه اجرا کند.

---

## ساختار پروژه

```
iran-news-agent/
├── app.py              # سایت Flask + scheduler
├── fetcher.py          # ایجنت جمع‌آوری + ترجمه + تلگرام
├── sources.py          # لیست ۳۰+ منبع
├── translator.py       # مترجم فارسی
├── db.py               # SQLite
├── requirements.txt
├── .env.example
└── README.md
```

---

## نکات مهم

- **ترجمه:** از `deep-translator` (Google) استفاده شده. برای کیفیت بالاتر می‌توانید مدل‌های محلی (Helsinki-NLP) یا APIهای دیگر را جایگزین کنید.
- **Rate Limit:** بین درخواست‌ها فاصله گذاشته شده تا بلاک نشوید.
- **X/Twitter:** Nitter ممکن است گاهی قطع شود. در آن صورت از [RSSHub](https://rsshub.app) یا Twitter API v2 استفاده کنید.
- **Truth Social ترامپ:** فعلاً RSS عمومی پایدار ندارد؛ می‌توانید از سرویس‌های شخص‌ثالث یا scraping کنترل‌شده اضافه کنید.
- دیتابیس در پوشه `data/` ذخیره می‌شود (روی Render ephemeral است؛ برای ماندگاری می‌توانید به PostgreSQL مهاجرت دهید).

---

## لایسنس
MIT – آزاد برای استفاده شخصی و تجاری.

اگر سوالی داشتید یا خواستید منبعی اضافه/حذف شود، issue باز کنید.
