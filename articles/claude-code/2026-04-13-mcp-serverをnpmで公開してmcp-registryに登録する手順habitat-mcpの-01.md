---
id: "2026-04-13-mcp-serverをnpmで公開してmcp-registryに登録する手順habitat-mcpの-01"
title: "MCP Serverをnpmで公開してMCP Registryに登録する手順（habitat-mcpの実例）"
url: "https://qiita.com/mitsuashi/items/506b5e542d41790d9cf7"
source: "qiita"
category: "claude-code"
tags: ["MCP", "qiita"]
date_published: "2026-04-13"
date_collected: "2026-04-14"
summary_by: "auto-rss"
---

## はじめに

MCP（Model Context Protocol）は、AIエージェントがツールやデータソースに接続するための標準プロトコルです。この記事では、自作のMCP Serverを**npm公開**し、公式の**MCP Registry**に登録するまでの手順を、実際に公開した `habitat-mcp` を例に解説します。

## 前提

| 項目 | 値 |
|------|-----|
| Node.js | v20以上 |
| npm アカウント | 必要 |
| GitHub アカウント | 必要（Registry認証用） |
| MCP Server | stdio ベース（TypeScript） |

## 1. MCP Serverの実装

MCP Serverは標準入出力（stdio）でJSON-RPCメッセージをやり取りするプログラムです。

```typescript
// index.ts
#!/usr/bin/env node

import { readLine, writeLine } from './io';

// ツール一覧
const
