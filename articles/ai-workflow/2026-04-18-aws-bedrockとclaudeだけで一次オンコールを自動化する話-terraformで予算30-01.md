---
id: "2026-04-18-aws-bedrockとclaudeだけで一次オンコールを自動化する話-terraformで予算30-01"
title: "AWS BedrockとClaudeだけで一次オンコールを自動化する話 — Terraformで予算30USD以内に組む障害検知エージェント"
url: "https://zenn.dev/okamyuji/articles/aws-bedrock-claude-incident-response"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-18"
date_collected: "2026-04-19"
summary_by: "auto-rss"
query: ""
---

!
本記事は執筆時点である2026年4月にAWS us-east-1で実動作を確認した内容です。登場するClaude Haiku 4.5、Sonnet 4.6、Opus 4.5は、執筆時点でAWS Bedrockの米国系リージョンから利用できるモデル世代であり、実在のモデルです。ただし、Amazon Bedrockのモデル有効化手順、モデルIDの命名規則、Step Functionsの挙動などはAWS側で頻繁に更新されます。読者が本記事を参照される時点では、モデル名、UI、ポリシー仕様が変わっている可能性があります。実際に手を動かす際は、AWS公式ドキュメントと手元のコンソール表示を一次...
