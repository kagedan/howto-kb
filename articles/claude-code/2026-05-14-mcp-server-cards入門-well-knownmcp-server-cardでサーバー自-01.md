---
id: "2026-05-14-mcp-server-cards入門-well-knownmcp-server-cardでサーバー自-01"
title: "MCP Server Cards入門 — .well-known/mcp-server-cardでサーバー自動検出を実装する"
url: "https://zenn.dev/kai_kou/articles/213-mcp-server-cards-discovery-guide"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "Python", "TypeScript"]
date_published: "2026-05-14"
date_collected: "2026-05-15"
summary_by: "auto-rss"
query: ""
---

## はじめに

MCP（Model Context Protocol）サーバーを運用していると、「クライアントに手動で接続先URLを設定させる手間を省けないか」という課題に直面します。2026年4月現在、この問題を解決するのが **MCP Server Cards**（SEP-1649/SEP-2127）です。

MCP Server Cards は、MCPサーバーが自身の機能・接続情報・認証要件を `/.well-known/mcp-server-card` エンドポイントで公開する仕組みです。Claude Code、Cursor などの対応クライアントはこのエンドポイントを読むことで、設定ファイルなしにサーバーへ自動接続できます。

### この記事で解説すること

* MCP Server Cards の仕様と背景（SEP-1649/SEP-2127）
* Server Card のスキーマと各フィールドの意味
* Python（FastMCP + FastAPI）と TypeScript（MCP SDK + Express）での実装手順
* セキュリティ上の注意点（DNSリバインディング対策・OAuth2連携）
* Claude Code / Cursor での動作確認方法

### 対象読者

* MCPサーバーを開発・運用しているエンジニア
* AIクライアントの自動設定を実現したい開発者
* MCP 2026ロードマップの最新動向を把握したい方

### 前提知識

* MCP の基本概念（tools, resources, prompts）
* HTTP サーバーの実装経験（Python or TypeScript）

---

## TL;DR

* MCP Server Cards は `/.well-known/mcp-server-card` でサーバー情報を公開する新仕様（SEP-2127）
* AI クライアントが事前接続なしにサーバー機能を自動検出できる
* Python（FastMCP）または TypeScript（MCP SDK）で数十行の実装で対応可能
* セキュリティ: Origin ヘッダー検証・HTTPS・cryptographically secure なセッションIDが必須

---

## MCP Server Cards とは

### 背景：手動設定の課題

従来のMCPサーバー接続では、クライアントは `~/.claude/mcp_servers.json` などの設定ファイルに接続先URLを手動記述する必要がありました。サーバーが複数の機能を持つ場合や認証を要求する場合、この手動設定は複雑になりがちでした。

### Server Cards が解決すること

MCP Server Cards は、HTTP サーバーが `/.well-known/mcp-server-card` というエンドポイントを公開することで、以下を実現します。

| 従来方式 | Server Cards 方式 |
| --- | --- |
| クライアントが接続先URLを手動設定 | クライアントが URL から自動検出 |
| 認証情報を設定ファイルに記述 | OAuth2 メタデータから自動取得 |
| 利用可能ツールを接続後に確認 | 接続前にサーバー情報を取得可能 |
| IDE 拡張機能を手動インストール | 自動設定・ゼロコンフィグ接続 |

### 仕様の現状（2026年4月）

| 仕様 | 説明 | ステータス |
| --- | --- | --- |
| SEP-1649 | Server Cards 初期提案 | Closed/Completed（SEP-2127に引継） |
| SEP-2127 | 詳細スキーマ定義・パス変更 | PR レビュー中 |
| SEP-1960 | `/.well-known/mcp` マニフェスト | 仕様提案中 |

これらは MCP コア仕様にはまだマージされていませんが、主要クライアントの対応が進んでいます。公式仕様は [modelcontextprotocol.io](https://modelcontextprotocol.io/specification/draft/schema) を参照してください。

---

## Server Card のスキーマ

### スキーマ例（SEP-2127 準拠）

```
{
  "name": "com.example/my-data-server",
  "title": "My Data Server",
  "description": "データ取得・分析ツールを提供するMCPサーバー",
  "version": "2.1.0",
  "remotes": [
    {
      "transportType": "streamable-http",
      "url": "https://api.example.com/mcp",
      "auth": {
        "type": "oauth2",
        "authorization_server": "https://api.example.com/.well-known/oauth-authorization-server"
      }
    }
  ]
}
```

### フィールド解説

| フィールド | 必須 | 説明 |
| --- | --- | --- |
| `name` | 必須 | 逆DNS形式の識別名（例: `com.example/server-name`） |
| `description` | 必須 | サーバーの機能説明文 |
| `version` | 任意 | サーバーのバージョン（SemVer 推奨） |
| `title` | 任意 | クライアント UI 表示用の人間可読な名前 |
| `remotes` | 必須 | トランスポート設定の配列（1件以上） |
| `remotes[].transportType` | 必須 | トランスポート種別（後述） |
| `remotes[].url` | 必須 | MCPエンドポイントの完全 URL（HTTPS 必須） |
| `remotes[].auth` | 任意 | OAuth2 認証設定 |
| `capabilities` | 任意 | サーバー機能の静的宣言（動的な primitive は対象外） |

### remotes[].transportType の選択肢

```
"streamable-http"  // 推奨: HTTP POST + SSE ストリーミング（MCP 2025-11-25以降）
"stdio"            // ローカル開発専用: 標準入出力
```

公式ドキュメントによると、HTTP ベースの本番サーバーには `"streamable-http"` が推奨されています（[MCP Transports](https://modelcontextprotocol.io/docs/concepts/transports) 参照）。旧来の HTTP+SSE トランスポートは MCP 2024-11-05 以前に使われていましたが現在は廃止済みです。

---

## 実装手順：Python（FastMCP + FastAPI）

### 環境準備

```
pip install fastmcp fastapi uvicorn
```

[FastMCP](https://github.com/PrefectHQ/fastmcp) はMCP Python SDKのハイレベルラッパーです。

### 実装コード

```
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastmcp import FastMCP
from contextlib import asynccontextmanager

# MCPサーバーの定義
mcp = FastMCP("my-data-server")

@mcp.tool()
def get_weather(city: str) -> str:
    """指定した都市の天気情報を返す"""
    return f"{city}の天気: 晴れ、気温 22°C"

@mcp.resource("data://users/{user_id}")
def get_user(user_id: str) -> str:
    """ユーザー情報を返す"""
    return f"ユーザーID: {user_id}"

# MCPのlifespanを FastAPI に結合
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with mcp.http_app().router.lifespan_context(app):
        yield

# FastAPIアプリ
app = FastAPI(title="My MCP Server", lifespan=lifespan)

# CORS設定（MCPクライアント向け）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Mcp-Session-Id"],
)

# Server Card エンドポイント（SEP-2127準拠）
@app.get("/.well-known/mcp-server-card")
async def server_card():
    return JSONResponse(
        content={
            "name": "com.example/my-data-server",
            "title": "My Data Server",
            "description": "天気情報・ユーザーデータを提供するMCPサーバー",
            "version": "2.1.0",
            "remotes": [
                {
                    "transportType": "streamable-http",
                    "url": "https://api.example.com/mcp",
                }
            ],
        },
        headers={
            "Cache-Control": "public, max-age=3600",
            "X-Content-Type-Options": "nosniff",
        },
    )

# MCPのHTTPアプリを /mcp にマウント
mcp_app = mcp.http_app(path="/mcp")
app.mount("/", mcp_app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 動作確認

```
# サーバー起動
uvicorn main:app --reload

# Server Card を確認
curl http://localhost:8000/.well-known/mcp-server-card | python3 -m json.tool
```

---

## 実装手順：TypeScript（MCP SDK + Express）

### 環境準備

```
npm install express @modelcontextprotocol/sdk cors zod
npm install -D typescript @types/express @types/cors ts-node @types/node
```

### 実装コード

```
import express, { Request, Response } from "express";
import cors from "cors";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { randomUUID } from "node:crypto";
import { z } from "zod";

const app = express();
app.use(express.json());
app.use(
  cors({
    origin: "*",
    methods: ["GET", "POST", "OPTIONS"],
    allowedHeaders: ["Content-Type", "Authorization", "Mcp-Session-Id"],
  })
);

// Server Card エンドポイント（SEP-2127準拠）
app.get("/.well-known/mcp-server-card", (_req: Request, res: Response) => {
  res.set({
    "Content-Type": "application/json",
    "Cache-Control": "public, max-age=3600",
    "X-Content-Type-Options": "nosniff",
  });
  res.json({
    name: "com.example/my-data-server",
    title: "My Data Server",
    description: "天気情報・ユーザーデータを提供するMCPサーバー",
    version: "2.1.0",
    remotes: [
      {
        transportType: "streamable-http",
        url: "https://api.example.com/mcp",
      },
    ],
  });
});

// MCPエンドポイント（リクエストごとに新しいインスタンスを作成）
// ⚠️ 単一インスタンスを複数クライアントで使い回すと
//    JSON-RPC ID 衝突によるクロスクライアントデータ漏洩が発生する（GHSA-345p-7cg4-v4c7）
app.post("/mcp", async (req: Request, res: Response) => {
  // Origin検証でDNSリバインディング対策（MCP Transports仕様で必須）
  const origin = req.headers.origin;
  const allowedOrigins = ["https://api.example.com", "http://localhost:8000"];
  if (origin && !allowedOrigins.includes(origin)) {
    return res.status(403).json({ error: "Origin not allowed" });
  }

  // リクエストごとに新インスタンスを作成（ステートレスパターン）
  const server = new McpServer({
    name: "my-data-server",
    version: "2.1.0",
  });

  server.tool(
    "get_weather",
    { city: z.string().describe("都市名") },
    async ({ city }) => ({
      content: [{ type: "text", text: `${city}の天気: 晴れ、気温 22°C` }],
    })
  );

  // sessionIdGenerator には暗号学的に安全な UUID を使用
  const transport = new StreamableHTTPServerTransport({
    sessionIdGenerator: () => randomUUID(),
  });

  await server.connect(transport);
  await transport.handleRequest(req, res, req.body);
});

app.listen(8000, () => {
  console.log("MCPサーバーが http://localhost:8000 で起動しました");
});
```

---

## セキュリティ上の注意点

### DNSリバインディング対策

MCP 仕様では、すべての HTTP リクエストに対して `Origin` ヘッダーの検証が必須とされています（[MCP Transports 仕様](https://modelcontextprotocol.io/docs/concepts/transports) 参照）。

```
# FastAPIでのOrigin検証ミドルウェア
@app.middleware("http")
async def validate_origin(request: Request, call_next):
    if request.url.path == "/mcp":
        origin = request.headers.get("origin", "")
        allowed = ["https://api.example.com", "http://localhost:8000"]
        if origin and origin not in allowed:
            return JSONResponse(
                status_code=403,
                content={"error": "Origin not allowed"}
            )
    return await call_next(request)
```

### HTTPS の強制

本番環境では `remotes[].url` に `https://` を使用し、HTTP URL は絶対に記載しないようにします。

```
# ✗ 危険: HTTP URL
{"transportType": "streamable-http", "url": "http://api.example.com/mcp"}

# ✓ 安全: HTTPS URL
{"transportType": "streamable-http", "url": "https://api.example.com/mcp"}
```

### TypeScript: transport インスタンスの使い回し禁止

単一の `StreamableHTTPServerTransport` インスタンスを複数のリクエストで共有すると、JSON-RPC ID の衝突によりクライアント間でレスポンスが漏洩します（[GHSA-345p-7cg4-v4c7](https://github.com/modelcontextprotocol/typescript-sdk/security/advisories/GHSA-345p-7cg4-v4c7)）。必ずリクエストごとに新しいインスタンスを作成してください。

### OAuth2 との連携

認証が必要なサーバーは、`remotes[].auth` に OAuth2 メタデータを追加します。

```
{
  "remotes": [
    {
      "transportType": "streamable-http",
      "url": "https://api.example.com/mcp",
      "auth": {
        "type": "oauth2",
        "authorization_server": "https://api.example.com/.well-known/oauth-authorization-server"
      }
    }
  ]
}
```

---

## Cache-Control の設定方針

| サーバーの性質 | 推奨 Cache-Control |
| --- | --- |
| 機能が固定（安定版） | `public, max-age=3600` |
| 機能が頻繁に変わる | `public, max-age=300, must-revalidate` |
| 認証情報を含む | `private, no-cache` |

---

## Claude Code での動作確認

Server Cards 対応クライアントでの接続は、URL を指定するだけで完了します。

```
# Claude Code での自動検出接続（Server Cards 対応時）
claude mcp add --url https://api.example.com

# 内部的に以下が自動実行される:
# 1. GET https://api.example.com/.well-known/mcp-server-card
# 2. JSON を解析して remotes[0].url 等を取得
# 3. https://api.example.com/mcp に自動接続
```

従来の手動設定方式（`mcp_servers.json` への直接記述）と比較すると、設定ステップが大幅に削減されます。

---

## まとめ

| ポイント | 内容 |
| --- | --- |
| 仕様 | SEP-1649/SEP-2127（MCPコア仕様へのマージ予定） |
| エンドポイント | `/.well-known/mcp-server-card` |
| 主なフィールド | name, description, version, title, remotes |
| 実装工数 | Python/TypeScript ともに 30〜50 行程度 |
| セキュリティ | Origin 検証・HTTPS・cryptographically secure なセッションID が必須 |

MCP Server Cards は、MCPエコシステムの普及に向けた「ゼロコンフィグ接続」を実現する重要な仕様です。SEP-2127 は 2026年4月現在レビュー中ですが、実装を先取りすることで早期にメリットを享受できます。

## 参考リンク
