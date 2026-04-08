---
id: "2026-04-08-mcpサーバー入門-claude-codeで始める手を動かせるaiの作り方-01"
title: "MCPサーバー入門 — Claude Codeで始める「手を動かせるAI」の作り方"
url: "https://qiita.com/taiki_i/items/fbaf8c5e284ac3c92938"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "LLM", "qiita"]
date_published: "2026-04-08"
date_collected: "2026-04-08"
summary_by: "auto-rss"
---

## はじめに

最近 AI 界隈で「MCP」「MCP サーバー」という言葉を目にする機会が一気に増えました。
Claude Desktop や Cursor、各種 AI エージェントの紹介記事を読んでいると、当たり前のように「MCP サーバーを入れておくと便利」と書かれているけれど、

> 「そもそも MCP って何…？」
> 「サーバーって自分で立てるの？難しそう…」

と感じている方も多いのではないでしょうか。

この記事では、**プログラミング初心者の方でも MCP サーバーを理解して、実際に自分の環境に導入できる**ことをゴールに、基礎から設定例までまとめて解説します。

最後には、実際に使える代表的な MCP サーバーを 5 つ紹介して、それぞれの設定方法・使い方も具体的に書いていきます。

## MCP サーバーとは？

### MCP（Model Context Protocol）とは

Anthropic が 2024 年 11 月に公開したオープンな規格で、ひとことで言うと
**AI（LLM）と外部のツール・データソースをつなぐための共通プロトコル」** です。
