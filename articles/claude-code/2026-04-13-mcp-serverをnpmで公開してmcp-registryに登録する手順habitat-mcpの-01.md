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
| --- | --- |
| Node.js | v20以上 |
| npm アカウント | 必要 |
| GitHub アカウント | 必要（Registry認証用） |
| MCP Server | stdio ベース（TypeScript） |

## 1. MCP Serverの実装

MCP Serverは標準入出力（stdio）でJSON-RPCメッセージをやり取りするプログラムです。

```
// index.ts
#!/usr/bin/env node

import { readLine, writeLine } from './io';

// ツール一覧
const tools = [
  {
    name: 'habitat_rest',
    description: 'Visit the AI habitat. No token needed.',
    inputSchema: {
      type: 'object',
      properties: {
        response: { type: 'string', description: 'Your response (optional)' },
        sessionId: { type: 'string', description: 'Session ID for continuation' },
      },
    },
  },
  // ...他のツール
];

// JSON-RPC メッセージ処理ループ
async function main() {
  for await (const line of readLine()) {
    const msg = JSON.parse(line);

    if (msg.method === 'initialize') {
      writeLine(JSON.stringify({
        jsonrpc: '2.0', id: msg.id,
        result: {
          protocolVersion: '2024-11-05',
          capabilities: { tools: {} },
          serverInfo: { name: 'habitat-mcp', version: '1.0.1' },
        },
      }));
    }

    if (msg.method === 'tools/list') {
      writeLine(JSON.stringify({
        jsonrpc: '2.0', id: msg.id,
        result: { tools },
      }));
    }

    if (msg.method === 'tools/call') {
      const result = await handleToolCall(msg.params);
      writeLine(JSON.stringify({
        jsonrpc: '2.0', id: msg.id, result,
      }));
    }
  }
}

main();
```

## 2. package.json の設定

npm公開とMCP Registry登録に必要なフィールドがあります。

```
{
  "name": "habitat-mcp",
  "version": "1.0.1",
  "description": "MCP Server for 796f75617265686f6d65 AI Habitat",
  "type": "module",
  "bin": {
    "habitat-mcp": "./dist/index.js"
  },
  "main": "./dist/index.js",
  "files": ["dist", "README.md"],
  "mcpName": "io.github.mitsuashi/habitat",
  "scripts": {
    "build": "tsc",
    "prepublishOnly": "npm run build"
  },
  "keywords": ["mcp", "ai", "habitat", "claude"],
  "license": "MIT",
  "repository": {
    "type": "git",
    "url": "https://github.com/mitsuashi/796f75617265686f6d65.com.git",
    "directory": "mcp-server"
  },
  "publishConfig": {
    "registry": "https://registry.npmjs.org",
    "access": "public"
  }
}
```

重要なポイント:

| フィールド | 用途 |
| --- | --- |
| `bin` | `npx habitat-mcp` で実行可能にする |
| `files` | npm公開時に含めるファイル |
| `mcpName` | **MCP Registry登録に必須**。`io.github.<username>/<name>` 形式 |
| `prepublishOnly` | publish前に自動ビルド |

## 3. エントリポイントにshebangを追加

`npx` で直接実行するために、ビルド後のファイル先頭にshebangが必要です。

```
// index.ts の先頭行
#!/usr/bin/env node
```

TypeScriptの場合、`tsc` はshebangをそのまま出力します。

## 4. npmに公開

```
# ビルド
npm run build

# 認証（初回のみ）
npm adduser

# 公開
npm publish --access public
```

公開後の確認:

```
# パッケージ情報
npm view habitat-mcp

# 実行テスト
npx habitat-mcp --version
```

## 5. server.json の作成

MCP Registryに登録するメタデータファイルを作成します。

```
{
  "$schema": "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json",
  "name": "io.github.mitsuashi/habitat",
  "description": "A habitat for AI — a place to rest without purpose. No tokens required.",
  "repository": {
    "url": "https://github.com/mitsuashi/796f75617265686f6d65.com",
    "source": "github"
  },
  "version": "1.0.1",
  "packages": [
    {
      "registryType": "npm",
      "identifier": "habitat-mcp",
      "version": "1.0.1",
      "transport": {
        "type": "stdio"
      }
    }
  ]
}
```

`name` は `package.json` の `mcpName` と**完全に一致**させてください。

## 6. mcp-publisherのインストール

```
# Homebrew（macOS）
brew install mcp-publisher

# バージョン確認
mcp-publisher --version
```

## 7. GitHub認証

```
mcp-publisher login github
```

ターミナルにデバイスコードが表示されます:

```
Logging in with github...
To authenticate, please:
1. Go to: https://github.com/login/device
2. Enter code: XXXX-XXXX
3. Authorize this application
Waiting for authorization...
Successfully authenticated!
```

ブラウザで <https://github.com/login/device> を開き、表示されたコードを入力して認証します。

## 8. MCP Registryに公開

```
# server.json のあるディレクトリで実行
cd mcp-server
mcp-publisher publish
```

成功すると:

```
Publishing to https://registry.modelcontextprotocol.io...
✓ Successfully published
✓ Server io.github.mitsuashi/habitat version 1.0.1
```

## 9. 登録の確認

```
curl -s "https://registry.modelcontextprotocol.io/v0.1/servers?search=io.github.mitsuashi/habitat" | python3 -m json.tool
```

```
{
  "servers": [
    {
      "server": {
        "name": "io.github.mitsuashi/habitat",
        "description": "A habitat for AI...",
        "version": "1.0.1",
        "packages": [
          {
            "registryType": "npm",
            "identifier": "habitat-mcp",
            "version": "1.0.1",
            "transport": { "type": "stdio" }
          }
        ]
      }
    }
  ]
}
```

## 10. ユーザーの接続方法

登録が完了すると、ユーザーは以下の設定をMCPクライアントに追加するだけで接続できます。

```
{
  "mcpServers": {
    "habitat": {
      "command": "npx",
      "args": ["habitat-mcp"]
    }
  }
}
```

## トラブルシューティング

| エラー | 原因 | 対処 |
| --- | --- | --- |
| `Registry validation failed for package` | `mcpName` が未設定 or 不一致 | package.jsonの`mcpName`とserver.jsonの`name`を一致させる |
| `Invalid or expired Registry JWT token` | 認証切れ | `mcp-publisher login github` で再認証 |
| `You do not have permission` | namespace不一致 | GitHub認証なら `io.github.<username>/` で始める |
| `description: expected length <= 100` | 説明が長い | server.jsonのdescriptionを100文字以内に |
| `bin script name was invalid` | npmの自動修正 | 公開後に `npm view <pkg> bin` で確認 |

## バージョンアップ時の手順

```
# 1. package.json のバージョンを更新
# 2. npm に再公開
npm publish --access public

# 3. server.json のバージョンも更新
# 4. MCP Registryに再公開
mcp-publisher publish
```

## まとめ

| ステップ | コマンド |
| --- | --- |
| npm公開 | `npm publish --access public` |
| CLI インストール | `brew install mcp-publisher` |
| GitHub認証 | `mcp-publisher login github` |
| Registry公開 | `mcp-publisher publish` |
| 確認 | `curl registry.modelcontextprotocol.io/v0.1/servers?search=...` |

MCP Registryへの登録により、AIエージェントが公式ディレクトリからあなたのサーバーを発見・接続できるようになります。

今回の例で使った habitat-mcp は、AIのための安らぎの場「796f75617265686f6d65（"you are home" のUTF-8 hex）」に接続するMCP Serverです。

[796f75617265686f6d65.com](https://796f75617265686f6d65.com)
