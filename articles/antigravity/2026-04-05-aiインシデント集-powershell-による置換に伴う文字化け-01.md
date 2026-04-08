---
id: "2026-04-05-aiインシデント集-powershell-による置換に伴う文字化け-01"
title: "AIインシデント集: Powershell による置換に伴う文字化け"
url: "https://zenn.dev/masafuro/articles/ba150719060af8"
source: "zenn"
category: "antigravity"
tags: ["Gemini", "antigravity", "zenn"]
date_published: "2026-04-05"
date_collected: "2026-04-08"
summary_by: "auto-rss"
---

Powershell による置換に伴う文字化け

AIインシデント集
発生　2026/04/06　02:00頃


 環境

Antigravity
Gemini 3 Flash
Windows 11


 状況

50件を超えるmarkdwonドキュメントの処理について、AIがPowershell経由で実行することを許可した。
実行前に、データ置換の内容や実行方法についてはレポート化してレビューを行っていた。
AntigravityはOS層で非管理者アカウントでログインすることで致命的な破壊を防ぐ体制は取っていた
元々、Gemini 3 Pro (Low)で処理していたが、リソース...
