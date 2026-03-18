---
id: "2026-03-17-aiがspaを読めない問題chrome-devtools-mcpで解決した-01"
title: "AIがSPAを読めない問題、Chrome DevTools MCPで解決した"
url: "https://zenn.dev/canaria_john/articles/91ad50759abbbb"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "GPT", "JavaScript", "zenn"]
date_published: "2026-03-17"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

はじめに
AIに「このページの内容教えて」とURLを渡す場面は、最近かなり増えた。
Claude CodeやChatGPTを使っていると、調べたいドキュメントやダッシュボードのURLを渡して情報を取得してもらうことがよくある。
ところが、SPAで実装されているサイトだと、これがうまくいかない。
たとえば、Google Mapsのような動的なサイトにURLを渡しても、AIが返してくるのは「ページタイトルとJavaScriptのコードだけです」といった内容になる。
実際にブラウザで開けば地図もUIも見えているのに、AIには何も見えていない。
これが、SPA特有の問題だ。
この記事では、次...
