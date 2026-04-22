---
id: "2026-04-21-claude-code-desktop-の記憶-osskiokuに-pdf-url-取り込みを実装し-01"
title: "Claude Code / Desktop の記憶 OSS「KIOKU」に PDF / URL 取り込みを実装した"
url: "https://zenn.dev/megaphone_tokyo/articles/9c0cffdf9e176b"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "zenn"]
date_published: "2026-04-21"
date_collected: "2026-04-22"
summary_by: "auto-rss"
---

はじめに
前回の記事 で Claude Code の記憶を育てる OSS「KIOKU」を公開してから、Phase N で Claude Desktop 対応（.mcpb バンドル化）も済ませました。
今回は、その次に実装した 外部ソース取り込み機能 の話を書きます。


v0.2.0: kioku_ingest_pdf — PDF / Markdown を即時取り込み

v0.3.0: kioku_ingest_url — HTTP/HTTPS URL を本文抽出して取り込み

「Claude に PDF 読ませて」「この URL の記事をメモして」と言えば、KIOKU が自動で ...
