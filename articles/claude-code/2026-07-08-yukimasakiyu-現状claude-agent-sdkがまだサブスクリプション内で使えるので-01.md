---
id: "2026-07-08-yukimasakiyu-現状claude-agent-sdkがまだサブスクリプション内で使えるので-01"
title: "@yukimasakiyu: 現状Claude Agent SDKがまだサブスクリプション内で使えるので、一旦Fable 5の呼び出しはSDK経由が一"
url: "https://x.com/yukimasakiyu/status/2074859918717538411"
source: "x"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "x"]
date_published: "2026-07-08"
date_collected: "2026-07-09"
summary_by: "auto-x"
query: "MCP server 設定 OR MCP 活用事例 OR MCP 連携"
---

現状Claude Agent SDKがまだサブスクリプション内で使えるので、一旦Fable 5の呼び出しはSDK経由が一番Input Tokenのオーバーヘッドを抑えられそうかな。Codexをベースエージェントにしつつ、Claude Codeの既定のsystem prompt、tool definitions、mcp server設定、skillsなどは一切読み込ませず、API呼び出しと同じようなクリーンコンテキスト状態でUser Promptだけで完結させる。claude -p --bareはOAuth/keychainや認証トークンを読んでくれないためサブスクリプション内では使えないので、 サブスク内かつワンショットで使う場合はSDK経由が一番軽量化できそう。Fable 5側でSafety Filterで弾かれそうな危険フレーズや単語はCodex側でサニタイズさせリクエストの失敗率を下げる。Codexは標準速度モードであれば、サブエージェントの並列稼働数を抑えていれば5時間レートリミットで止まることは無いので、ロングランも可能。
