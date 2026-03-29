---
id: "2026-03-23-lucianlamp-claude-code-channels-が公式リリースされたのでこれを拡張し-01"
title: "@lucianlamp: Claude Code Channels が公式リリースされたので、これを拡張して OpenClaw 的な自律エージェン"
url: "https://x.com/lucianlamp/status/2036089908071461298"
source: "x"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "x"]
date_published: "2026-03-23"
date_collected: "2026-03-29"
summary_by: "auto-x"
---

Claude Code Channels が公式リリースされたので、これを拡張して OpenClaw 的な自律エージェントにするボット『CCCBot 』を作りました。

最大の魅力は、Claude Code の OAuth 定額プランで動くこと。
API 従量課金じゃなく、月額固定で Claudeが自律的に動き続けます。

・スケジュールタスク
・HEARTBEAT死活監視 + MCP 切断時の自動復旧
・人格・ペルソナ設定
・ワンライナーでセットアップ

素の Channels は「繋がる」だけ。CCCBot は「自律的に動き続ける」ところまでやります。
https://github.com/lucianlamp/CCCBot
