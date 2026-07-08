---
id: "2026-07-08-databricksjp-databricksのomnigentが提唱するコンテキストポリシーが面白-01"
title: "@DatabricksJP: 🔐 DatabricksのOmnigentが提唱する「コンテキストポリシー」が面白いです AIエージェントのガバナンス"
url: "https://x.com/DatabricksJP/status/2074954055475155376"
source: "x"
category: "claude-code"
tags: ["claude-code", "LLM", "x"]
date_published: "2026-07-08"
date_collected: "2026-07-09"
summary_by: "auto-x"
query: "Claude Code CLAUDE.md 書き方 OR コンテキスト管理 OR Handover"
---

🔐 DatabricksのOmnigentが提唱する「コンテキストポリシー」が面白いです

AIエージェントのガバナンスを次のレベルに引き上げる仕組みを紹介します👇
https://t.co/e98teflspb

📌 何ができるのか？
• セッション中の「何を読んだか」「いくら使ったか」などの状態をリアルタイムで追跡します
• Claude CodeやCodexなど既存エージェントにも適用できるメタハーネスとして機能します

🛡️ 標準搭載の3つのポリシー
• Google Driveへの書き込みを「そのセッションで作成したドキュメントのみ」に限定します
• 機密資料へのアクセス量に応じてリスクスコアを動的に上昇させ、閾値を超えると人間の承認を求めます
• セッションごとの支出上限を管理するコストポリシーで暴走を防ぎます

🧠 注目ポイント：意図に基づく認可
• ユーザーの最初の指示内容を状態として記憶します
• 指示から逸脱する不審なツール呼び出しを自動ブロックします
• プロンプトインジェクション攻撃への実用的な防御になります

単純な許可/拒否ルールでは実現できなかった「文脈を理解するセキュリティ」がオープンソース（アルファ版）で公開されています。

エージェント時代のガバナンス設計として要注目です🔥
#Databricks #AIエージェント #LLMセキュリティ
