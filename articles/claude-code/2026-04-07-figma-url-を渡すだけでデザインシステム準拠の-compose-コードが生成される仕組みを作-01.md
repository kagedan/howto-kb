---
id: "2026-04-07-figma-url-を渡すだけでデザインシステム準拠の-compose-コードが生成される仕組みを作-01"
title: "Figma URL を渡すだけでデザインシステム準拠の Compose コードが生成される仕組みを作った"
url: "https://zenn.dev/dely_jp/articles/2cc6637e4d0aad"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "zenn"]
date_published: "2026-04-07"
date_collected: "2026-04-08"
summary_by: "auto-rss"
---

はじめに
クラシルで Android エンジニアをしている go です。
「Figma の URL を渡すだけで Compose UI を実装できたら最高だな」と思い、Figma MCP Server を使った PoC 検証を行いました。結果として Figma MCP は強力ですが、そのままではプロジェクト固有のデザインシステム（以下 KurashiruTheme）に準拠したコードが生成されないという課題に直面しました。
Figma MCP の出力と Android のデザインシステムをマッピングする Claude Code ルールを作成することで、Figma → Kurashiru...
