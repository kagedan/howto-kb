---
id: "2026-03-28-wsl2-claude-code-unity-mcpでaiにunityを操作させるハマり全記録-01"
title: "WSL2 × Claude Code × Unity MCPで、AIにUnityを操作させる【ハマり全記録】"
url: "https://zenn.dev/acropapa330/articles/unity_mcp_wsl_claude"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "Python", "zenn"]
date_published: "2026-03-28"
date_collected: "2026-03-29"
summary_by: "auto-rss"
---

WSL2 × Claude Code × Unity MCPで、AIにUnityを操作させる【ハマり全記録】

 はじめに
「Claude CodeにUnityを操作させたい」と思って調査を始めたところ、MCP for Unity というOSSパッケージを発見。
ただしWSL2環境では素直に繋がらず、ポート競合・Python競合など複数のハマりどころがありました。
この記事では完全に動作するまでにつまずいたポイントをすべて記録しています。同じ環境で試す人の時間を節約できれば幸いです。
そして最後に、想定外のおまけ発見もあります。


 環境・構成
Windows 11
├── Uni...
