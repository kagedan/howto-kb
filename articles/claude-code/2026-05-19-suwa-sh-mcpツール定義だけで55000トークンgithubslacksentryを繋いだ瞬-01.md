---
id: "2026-05-19-suwa-sh-mcpツール定義だけで55000トークンgithubslacksentryを繋いだ瞬-01"
title: "@suwa_sh: MCPツール定義だけで55,000トークン。GitHub+Slack+Sentryを繋いだ瞬間に起きる現象です。 DA"
url: "https://x.com/suwa_sh/status/2056525445013614744"
source: "x"
category: "claude-code"
tags: ["MCP", "API", "LLM", "TypeScript", "x"]
date_published: "2026-05-19"
date_collected: "2026-05-19"
summary_by: "auto-x"
query: "Claude Code CLAUDE.md 書き方 OR コンテキスト管理 OR Handover"
---

MCPツール定義だけで55,000トークン。GitHub+Slack+Sentryを繋いだ瞬間に起きる現象です。

DADLという論文がこの構造問題に答えを出していたので整理しました。

#MCP #LLMエージェント #生成AI

問題は2つに分解できます。

・1API=1MCPサーバーで、デプロイと認証管理が線形に増える
・接続中の全ツール定義を毎ターンLLMに載せる設計でコンテキストが肥大する

公式レジストリのツールの92%がbare APIラッパーで、上流APIの19%しかカバーしていない、という調査もあります。

DADLのアプローチは、REST APIを1つのYAMLで宣言し、LLMには「search」と「execute」の2メタツールだけを提示する形です。

LLMはsearchで署名を引き、executeでTypeScriptスニペットをsandbox実行する。

論文では1,833ツールを約1,000トークンで提示できるとされています。

ただし142倍削減という数字は、そのままは使えません。

・median backend(約92ツール)では5.9倍
・Cloudflare Code Modeが同時期に同思想で公開済み
・MemToolが9ヶ月先行して動的ツール管理を学術評価済み

論文単著・未査読・独立採用ゼロ、という条件と一緒に読む必要があります。

では何を取り込むか。記事ではaccess 4ラベル / coverage / hints / Toolsmithingを「独自DSLに依存せず使える設計テンプレ」として整理しています。

特に「accessはcontract、enforcementはOpenFGA」という分離は、自社MCP設計でもそのまま使えます。

https://t.co/HLlA575B0w
