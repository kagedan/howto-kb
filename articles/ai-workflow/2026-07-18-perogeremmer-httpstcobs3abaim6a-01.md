---
id: "2026-07-18-perogeremmer-httpstcobs3abaim6a-01"
title: "@perogeremmer: https://t.co/bs3ABAim6a"
url: "https://x.com/perogeremmer/status/2078438185399615546"
source: "x"
category: "ai-workflow"
tags: ["MCP", "API", "x"]
date_published: "2026-07-18"
date_collected: "2026-07-19"
summary_by: "auto-x"
query: ""Model Context Protocol" tutorial OR "Claude MCP" integration"
---

https://t.co/bs3ABAim6a


--- Article ---
Setelah sebelumnya saya ngebahas [AionUI bagian introduction](https://x.com/perogeremmer/status/2078402785209397717?s=20), sekarang saya ingin membahas tentang bagaimana connect ke MCP TradingView dengan AionUI.

Di awal bulan Juli saya ikut webinar @xiayuejiu tentang memulai saham dari enol. Sejujurnya saya enggak enol banget sih tentang saham, tapi menarik untuk diikuti karena Aurel menjelaskan tentang bagaimana ia menggunakan Claude untuk trading, so ini yang membuat saya mau ikut kelasnya.

Pertanyaannya, apa itu MCP? MCP (*Model Context Protocol*) adalah tools yang digunakan AI untuk berkomunikasi dengan sebuah server. Sebenarnya ketika berkomunikasi dengan server AI bisa menggunakan HTTP dengan bantuan API atau REST API (whatever you name it lah). Tapi dengan MCP, AI kamu akan lebih on point dalam mengambil atau melakukan modifikasi terhadap data yang diperlukan.

MCP itu biasanya sekumpulan perintah (command) yang diberi label misalnya berikut merupakan MCP Google Tasks: 

```plaintext
create_task
get_tasks
update_task
delete_task
```

AI sudah bisa membayangkan mana command yang harus dipilih untuk mengeksekusi perintahmu, dan kamu cukup mengatakan kepada AI, misalnya:

> Dengan MCP Tasks, buatkan tugas baru bernama pergi ke laundry dimana tanggalnya besok jam 9.

AI secara otomatis mencari perintah create task dan membuatkan tugas tersebut, bahkan kalau ada sistem tagging, dia akan otomatis buatkan dan otomatis tugas tersebut akan muncul ke aplikasi Google Task kamu karena MCP tersebut merupakan jembatan untuk ke server Google.

# Apa hubungannya dengan TradingView?

TradingView merupakan sebuah web dimana kita bisa melakukan analisa terhadap grafik saham baik itu Indo dan luar, maupun kripto.

Jika pertanyaanya adalah apa hubungannya? Disini AI bekerja, dengan MCP kita bisa minta AI membuatkan grafik, membaca data, dan membuat prediksi supaya kita bisa melakukan trading.

Tentu saya tidak akan membahas banyak funda
