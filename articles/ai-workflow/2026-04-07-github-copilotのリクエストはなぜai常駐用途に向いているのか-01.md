---
id: "2026-04-07-github-copilotのリクエストはなぜai常駐用途に向いているのか-01"
title: "GitHub CopilotのリクエストはなぜAI常駐用途に向いているのか"
url: "https://zenn.dev/imudak/articles/copilot-request-billing-vs-token"
source: "zenn"
category: "ai-workflow"
tags: ["API", "zenn"]
date_published: "2026-04-07"
date_collected: "2026-04-08"
summary_by: "auto-rss"
---

OpenClawのAPIキー移行（Part1・Part2）をやっているときに、気づいたことがあります。
GitHub CopilotのPro+プラン（$39/月・1,500リクエスト）に切り替えたあと、コンソールを見て「あ、これは向いているかも」と思いました。

 トークン課金とリクエスト課金の違い
Anthropic APIはトークン課金です。入力・出力それぞれのトークン数に応じた金額がかかります。
GitHub Copilotはリクエスト課金です。1回の返答が1リクエスト（モデルによって乗数あり）として計上されます。



課金モデル
消費の増え方




トークン課金（Anthro...
