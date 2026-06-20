---
id: "2026-06-20-omoumama-ai-mcpのゼロタッチoauth企業管理型の認可emaを共同発表-anthrop-01"
title: "@OMOUMAMA_AI: 📰 MCPの「ゼロタッチOAuth」——企業管理型の認可（EMA）を共同発表 Anthropic・Okta・Micro"
url: "https://x.com/OMOUMAMA_AI/status/2068136799247986791"
source: "x"
category: "claude-code"
tags: ["MCP", "x"]
date_published: "2026-06-20"
date_collected: "2026-06-20"
summary_by: "auto-x"
query: "Claude Code CLAUDE.md 書き方 OR コンテキスト管理 OR Handover"
---

📰 MCPの「ゼロタッチOAuth」——企業管理型の認可（EMA）を共同発表

Anthropic・Okta・Microsoft・FigmaがModel Context Protocol向けに「Enterprise-Managed Authorization（EMA）」を共同発表した。
これまでMCPサーバーを使うたびにユーザーが個別にOAuth認証を踏む必要があったが、EMAでは企業のSSO（シングルサインオン）から各MCPサーバーへの認証が自動化され、ユーザーは何も操作せずに繋がる。

💡 なぜ重要か
技術基盤はIETF OAuth作業部会が策定中の「Identity Assertion Authorization Grant（ID-JAG）」標準で、認証情報をエージェントのコンテキストウィンドウの外に隔離できるためトークン漏洩リスクが大幅に下がる。
Dynamic Client Registration非対応のMicrosoft Entra IDにはプロキシ層で対応する。
MCP企業導入の最大のボトルネックだった「認証摩擦」が解消される転換点であり、AIエージェントを実業務に組み込む際の認証アーキテクチャが業界標準化に向かう動きとして重要。
エージェント基盤を設計するなら必読のニュースだ。

🔗 https://t.co/imjfhBe2kG
