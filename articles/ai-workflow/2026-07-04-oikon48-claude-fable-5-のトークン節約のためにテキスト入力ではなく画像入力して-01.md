---
id: "2026-07-04-oikon48-claude-fable-5-のトークン節約のためにテキスト入力ではなく画像入力して-01"
title: "@oikon48: Claude Fable 5 のトークン節約のために、テキスト入力ではなく、画像入力してOCR使った方が約59～70%の"
url: "https://x.com/oikon48/status/2073307515992076493"
source: "x"
category: "ai-workflow"
tags: ["x"]
date_published: "2026-07-04"
date_collected: "2026-07-05"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

Claude Fable 5 のトークン節約のために、テキスト入力ではなく、画像入力してOCR使った方が約59～70%のコストで実行できる報告が出てきたww

npx pxpipe-proxy
ANTHROPIC_BASE_URL=http://127.0.0.1:47821 claude

https://t.co/nN1Y72qwwN

Limitations:

- 情報損失あり。画像からの逐語的な記憶は信頼性が低い
- PNGエンコードは、大きなリクエストが送信される前に遅延を発生させる
- ASCII/Latin-1は十分にテスト済み。CJKも動作するが、動作は控えめ
