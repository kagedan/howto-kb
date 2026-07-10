---
id: "2026-07-10-bookunt-httpstcoeaymfbb3ke-01"
title: "@bookunt: https://t.co/eaYmFBB3Ke"
url: "https://x.com/bookunt/status/2075503860689281453"
source: "x"
category: "ai-workflow"
tags: ["AI-agent", "GPT", "x"]
date_published: "2026-07-10"
date_collected: "2026-07-11"
summary_by: "auto-x"
query: ""Model Context Protocol" tutorial OR "Claude MCP" integration"
---

https://t.co/eaYmFBB3Ke


--- Article ---
اگه می‌خوای یه AI Agent حرفه‌ای داشته باشی که از کد زدن گرفته تا اتوماسیون کارهای روزمره رو برات انجام بده، این مقاله دقیقاً برای تو نوشته شده.

هرمس Agent یه AI Agent متن‌باز قدرتمنده که توسط Nous Research توسعه داده شده. با بیش از ۶۰ ابزار داخلی، ۹۰ مهارت پیش‌فرض، و پشتیبانی از ۲۰+ پلتفرم پیام‌رسان، یکی از کامل‌ترین ابزارهای AI Agent دنیاست.

---

## 📍 فاز ۱: نصب و راه‌اندازی اولیه

اولین سوالی که ممکنه بپرسی اینه: «Hermes دقیقاً چیه و چرا با یه ChatGPT ساده فرق داره؟»

جواب کوتاه: ChatGPT یا Claude معمولی فقط باهات چت می‌کنن. Hermes یه Agent هست، یعنی می‌تونه واقعاً کار انجام بده، فایل بسازه، کد اجرا کنه، توی وب سرچ کنه، پیام تلگرام بفرسته، و حتی به صورت خودکار و زمان‌بندی‌شده کارهایی رو تکرار کنه، بدون اینکه تو هر بار بهش بگی.

**نصب روی سیستم‌عامل‌های مختلف**

**برای Linux/macOS/WSL2:**این دستور رو توی ترمینال می‌زنی و منتظر می‌مونی تا اسکریپت نصب همه‌چیز رو خودکار انجام بده:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash

```

این خط چیکار می‌کنه؟ curl فایل نصب رو از سرور Nous دانلود می‌کنه، و bash یعنی همون فایل رو بلافاصله اجرا کن. بعد از چند ثانیه، Hermes روی سیستمت نصب می‌شه.

**برای Windows (PowerShell):**

```bash
iex (irm https://hermes-agent.nousresearch.com/install.ps1)

```

اینجا irm (Invoke-RestMethod) اسکریپت نصب رو می‌گیره و iex (Invoke-Expression) اجراش می‌کنه. اگه با پاورشل راحت نیستی، Hermes Desktop رو نصب کن که یه رابط گرافیکی داره و نیازی به خط فرمان نداری.

**راه‌اندازی سریع بعد از نصب**

بعد از نصب، این دستور رو می‌زنی:

```bash
hermes setup --portal

```

این دستور یه ویزارد راه‌اندازی باز می‌کنه که:

۱- با OAuth ازت می‌خواد وارد حساب Nous Portal بشی (شبیه لاگین با گوگل) که با زدن کلیدهای Ctrl + C میتونی ازش بپری
۲- یه مدل پیش‌فرض برات انتخاب یا تایید می‌کنه
۳- چهار تا ابزار اصلی رو خودکار فعال می‌کنه: **web search** (جستجوی وب)، **image generation** (تولید تصویر)، **text-to-speech** (تبدیل متن به صدا)، و **browser** (مرورگر برای باز کردن و خوندن صفحات وب)

بعد از این
