---
id: "2026-04-24-haboshiastra-claude-code-v21119-config設定の永続化-from-01"
title: "@haboshiastra: 📊 Claude Code v2.1.119 /config設定の永続化、--from-prのGitLab/Bitbu"
url: "https://x.com/haboshiastra/status/2047466743363420592"
source: "x"
category: "claude-code"
tags: ["claude-code", "MCP", "AI-agent", "x"]
date_published: "2026-04-24"
date_collected: "2026-04-24"
summary_by: "auto-x"
query: "MCP server 設定 OR MCP 活用事例 OR MCP 連携"
---

📊 Claude Code v2.1.119

/config設定の永続化、--from-prのGitLab/Bitbucket/GHE対応、PowerShell auto-approve、MCP再設定並列化、blockedMarketplaces enforcement修正

https://t.co/nVNiRomOSb

① /config設定の永続化

/theme、editor mode、verbose等の `/config` 設定が `~/.claude/settings.json` に永続化され、project/local/policy override precedenceにも参加

→ セッションごとに設定が戻る地味なストレスが減る

② PR/agentまわりの実務改善

`--from-pr` がGitLab merge request、Bitbucket pull request、GitHub Enterprise PR URLを受理。`--agent` はbuilt-in agentのpermissionModeを尊重

→ GitHub以外の現場やagent運用でも扱いやすくなった

③ PowerShell auto-approve + MCP並列化

PowerShell tool commandがpermission modeでauto-approve可能に。subagent/SDKのMCP server再設定もserialではなくparallel接続に

→ Windows運用とMCP多め構成の待ち時間が改善

④ Security/fix群

blockedMarketplaces の hostPattern/pathPattern enforcement修正、Glob/GrepがBash deny時に消える不具合修正、MCP OAuth/HTTP接続やplugin cache不完全時のWindows spawn失敗も修正

→ plugin/MCPまわりの安定性が底上げされた
