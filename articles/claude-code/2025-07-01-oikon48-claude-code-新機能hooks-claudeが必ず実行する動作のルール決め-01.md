---
id: "2025-07-01-oikon48-claude-code-新機能hooks-claudeが必ず実行する動作のルール決め-01"
title: "@oikon48: 【Claude Code 新機能Hooks】 Claudeが必ず実行する動作のルール決め。 Claude Codeの"
url: "https://x.com/oikon48/status/1939862570871267571"
source: "x"
category: "claude-code"
tags: ["claude-code", "MCP", "x"]
date_published: "2025-07-01"
date_collected: "2026-03-31"
summary_by: "auto-x"
---

【Claude Code 新機能Hooks】
Claudeが必ず実行する動作のルール決め。
 
Claude Codeのアクションを検知して、事前に決められた動作を、指定のタイミングで行う機能。`/hooks`でsettings.jsonに設定可能。
 
検知されるアクション:
・Task, Bash, Glob, Grep, Read, Edit, MultiEdit, Write, WebFetch, WebSearch, MCPサーバー利用時など
 
事前に決められた動作:
・ユーザー定義のshellコマンド
 
タイミング:
・PreToolUse
・PostToolUse
・Notification
・Stop
 
何が良いか？:
・formatterの実行やログなど、実行して欲しかった動作を必ず実行してくれるようになる(JUnitのbefore, afterみたいなやつ)。
・複数hooksが存在する場合、並列で実行してくれるので決まった処理実行してくれる。
