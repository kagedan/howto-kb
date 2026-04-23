---
id: "2026-03-31-mcpサーバー実装パターン-sdkfastmcpsse-の3種を試してみる-01"
title: "MCPサーバー実装パターン SDK・FastMCP・SSE の3種を試してみる"
url: "https://zenn.dev/yaahmi/articles/mcp-server-implementations"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "zenn"]
date_published: "2026-03-31"
date_collected: "2026-03-31"
summary_by: "auto-rss"
---

# MCPサーバー実装パターン　SDK・FastMCP・SSE の3種を試してみる

MCPサーバー（Model Context Protocol）を学ぶとき、「どの実装方法を選べばいいのか？」という疑問はよく湧いてきます。本記事では、同じ機能（挨拶・計算・時刻取得）を3種類の方法で実装したサンプルコードをもとに、それぞれのアーキテクチャと特徴を比較します。（こちらの実装は2025年12月に試したものです）

コードはこちら → <https://github.com/yaahmi/localmcp>

---

## 3つの実装パターン概観

|  | `local-mcp-server` | `fastmcp-server` | `fastmcp-p-server` |
| --- | --- | --- | --- |
| フレームワーク | 素のMCP SDK | FastMCP | FastMCP + FastAPI |
| トランスポート | stdio | stdio | SSE（HTTP） |
| コード量 | 多め（設計重視） | 少ない | 中程度 |
| 複雑さ | ★★★★☆ | ★☆☆☆☆ | ★★★☆☆ |
| 適した用途 | 本番・拡張性重視 | プロトタイピング | リモート公開 |

---

## 前提知識：MCPとは

MCP（Model Context Protocol）は、AIアシスタント（ClaudeなどのLLM）が外部ツールやデータソースと通信するためのオープンプロトコルです。

MCPサーバーは主に3つの概念を持ちます：

* **Tools**：LLMが呼び出せる関数（例：計算、検索）
* **Prompts**：再利用可能なプロンプトテンプレート
* **Resources**：LLMが参照できるデータ（設定、ドキュメントなど）

---

## 実装①：素のMCP SDK を使ったstdioサーバー（`local-mcp-server`）

### 概要

MCP公式SDKを直接使い、設計パターンを意識した「しっかりめ」の実装です。

```
local-mcp-server/
├── src/
│   ├── server.py           # エントリーポイント
│   ├── core/
│   │   ├── base.py         # 抽象基底クラス（BaseTool）
│   │   ├── registry.py     # ツールレジストリ
│   │   ├── middleware.py   # ミドルウェア（ロギング）
│   │   └── exceptions.py  # カスタム例外
│   ├── tools/
│   │   ├── hello.py        # 挨拶ツール
│   │   ├── math.py         # 計算ツール
│   │   └── time.py         # 時刻ツール
│   └── utils/
│       ├── logger.py       # 構造化ロガー
│       └── validators.py   # 入力バリデーター
└── config/
    └── tools.yaml          # ツール設定
```

### コア：エントリーポイント（server.py）

```
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

app = Server("hello-world-mcp")
registry = ToolRegistry()
registry.register_multiple([
    HelloTool(),
    AddTool(),
    GetTimeTool(),
])

@app.list_tools()
async def list_tools() -> list[Tool]:
    return registry.get_all_definitions()

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        return await registry.execute_tool(name, arguments)
    except MCPToolError as e:
        return [TextContent(type="text", text=f"エラー: {str(e)}")]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream,
                      app.create_initialization_options())
```

ポイントは `@app.list_tools()` と `@app.call_tool()` の2つのデコレータです。これがMCPプロトコルの `tools/list` と `tools/call` リクエストにそれぞれ対応します。

### 設計パターン：テンプレートメソッドパターン（base.py）

```
class BaseTool(ABC):
    async def execute(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """テンプレートメソッド：実行の骨格を定義"""
        # 1. バリデーション
        self.validate_input(arguments)
        # 2. 前処理（フック）
        await self.before_execute(arguments)
        # 3. 実行（サブクラスで実装）
        result = await self._execute(arguments)
        # 4. 後処理（フック）
        await self.after_execute(arguments, result)
        return result

    @abstractmethod
    async def _execute(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """サブクラスで実装する実処理"""
        pass
    
    async def before_execute(self, arguments):
        """フック：サブクラスでオーバーライド可能"""
        pass
```

`BaseTool` を継承すれば、バリデーション・ロギング・フックが自動的に適用されます。新しいツールを追加するときは `_execute()` だけ実装すればOKです。

```
class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self.middleware = ToolMiddleware()
    
    def register(self, tool: BaseTool) -> None:
        self.tools[tool.name] = tool
    
    @ToolMiddleware().logging_middleware
    async def execute_tool(self, name: str, arguments: Dict) -> List[TextContent]:
        tool = self.get_tool(name)
        if not tool:
            raise ToolNotFoundError(name)
        return await tool.execute(arguments)
```

ミドルウェアデコレータにより、全ツール実行の前後に実行時間ログが自動挿入されます。

### ツールの実装例（hello.py）

```
class HelloTool(BaseTool):
    @property
    def name(self) -> str:
        return "hello"

    @property
    def description(self) -> str:
        return "シンプルな挨拶を返します"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "挨拶する相手の名前"}
            },
            "required": ["name"]
        }

    def validate_input(self, arguments):
        super().validate_input(arguments)
        if len(arguments.get("name", "")) > 50:
            raise ValueError("名前は50文字以内にしてください")

    async def _execute(self, arguments) -> list[TextContent]:
        user_name = arguments["name"]
        return [TextContent(type="text",
                            text=f"こんにちは、{user_name}さん！🎉")]
```

### Claude Desktop 設定

```
{
  "mcpServers": {
    "hello-world": {
      "command": "/path/to/venv/bin/python",
      "args": ["/path/to/src/server.py"],
      "env": {
        "PYTHONPATH": "/path/to/project/"
      }
    }
  }
}
```

### この実装の特徴

✅ **拡張性が高い**：新しいツールの追加がクラスの追加のみで完結  
✅ **テスタブル**：各クラスが独立しており単体テストが書きやすい  
✅ **ミドルウェア**：横断的関心事（ロギング・バリデーション）が分離されている  
⚠️ **コード量が多い**：小さなツールでも多くのファイルが必要

---

## 実装②：FastMCPを使ったstdioサーバー（`fastmcp-server`）

### 概要

FastMCPは、MCP SDK のボイラープレートを大幅に削減するフレームワークです。デコレータひとつで関数がツールになります。

### コア：1ファイルで完結（server\_fastmcp.py）

```
from fastmcp import FastMCP
from datetime import datetime

mcp = FastMCP("hello-world-mcp")

@mcp.tool()
def hello(name: str) -> str:
    """
    シンプルな挨拶を返します

    Args:
        name: 挨拶する相手の名前（50文字以内）
    """
    if len(name) > 50:
        raise ValueError("名前は50文字以内にしてください")
    return f"こんにちは、{name}さん！🎉"

@mcp.tool()
def add(a: float, b: float) -> str:
    """2つの数値を足し算します"""
    return f"計算結果: {a} + {b} = {a + b}"

@mcp.tool()
def divide(a: float, b: float) -> str:
    """2つの数値を割り算します"""
    if b == 0:
        raise ValueError("0で割ることはできません")
    return f"計算結果: {a} ÷ {b} = {a / b}"

if __name__ == "__main__":
    mcp.run()
```

これだけです。実装①と比べると、コード量が劇的に減っていることがわかります。

### FastMCPの自動変換の仕組み

FastMCPは**型ヒントとdocstring**からMCPのtoolスキーマを自動生成します。

| Pythonコード | MCPスキーマ |
| --- | --- |
| `name: str` | `{"type": "string"}` |
| `a: float` | `{"type": "number"}` |
| `names: list[str]` | `{"type": "array", "items": {"type": "string"}}` |
| `uppercase: bool = False` | `{"type": "boolean", "default": false}` |
| docstringの`Args:`セクション | `"description"` フィールド |

### Prompts：再利用可能なプロンプトテンプレート

FastMCPではToolsだけでなく、Promptsも簡単に定義できます。

```
@mcp.prompt()
def greeting_template(name: str, style: str = "casual") -> str:
    """挨拶メッセージのテンプレート"""
    if style == "formal":
        return f"{name}様\n\nお世話になっております。"
    else:
        return f"こんにちは、{name}さん！👋\n今日は何をお手伝いしましょうか？"

@mcp.prompt()
def code_review(language: str, code: str) -> str:
    """コードレビュー用プロンプト"""
    return f"""以下の{language}コードをレビューしてください：

```{language.lower()}
{code}
```

1. コードの品質と可読性
2. パフォーマンスの問題点
3. セキュリティの懸念事項  
   """

```
### Resources：LLMが参照できるデータ

```python
@mcp.resource("config://server_info")
def get_server_info() -> str:
    """サーバー情報と統計"""
    return json.dumps({
        "name": "hello-world-mcp",
        "version": "2.0.0",
        "framework": "FastMCP",
        "tools_count": 9
    }, ensure_ascii=False, indent=2)

@mcp.resource("doc://readme")
def get_readme() -> str:
    """使い方ガイド"""
    return "# Hello World MCP Server\n\n..."
```

URIスキーム（`config://`、`doc://`など）は自由に定義でき、LLMがどのリソースを参照するかの文脈を明確にします。

### この実装の特徴

✅ **最小コード**：関数を書くだけ、クラス不要  
✅ **型安全**：型ヒントから自動バリデーション  
✅ **Tools / Prompts / Resources** の3つを統一的に扱える  
✅ **開発速度**：プロトタイピングに最適  
⚠️ **柔軟性が低い**：複雑なミドルウェアやカスタム設計は実装①の方が向いている

---

## 実装③：FastMCP + SSE（HTTPトランスポート）（`fastmcp-p-server`）

### 概要

これまでの2つは `stdio`（標準入出力）でClaude Desktopとやり取りしていました。③では **SSE（Server-Sent Events）** を使ったHTTP通信に切り替えます。

### SSEとは

SSE（Server-Sent Events）は、サーバーからクライアントへのリアルタイムプッシュ通信です。

WebSocketと比較した場合のSSEの特徴：

|  | WebSocket | SSE |
| --- | --- | --- |
| 方向 | 双方向 | サーバー→クライアント（単方向） |
| プロトコル | 専用 | HTTP標準 |
| 複雑さ | 高い | 低い |
| 自動再接続 | 手動実装が必要 | 組み込み |
| クライアントからの送信 | WebSocketで送信 | 別途POSTリクエスト |

### アーキテクチャ

### サーバー側（server\_http\_sse.py）

```
from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse
import asyncio, json, uuid

app = FastAPI()

# セッション管理
active_connections: Dict[str, asyncio.Queue] = {}
pending_responses: Dict[str, asyncio.Queue] = {}

@app.get("/sse")
async def sse_endpoint(request: Request):
    """SSEストリームエンドポイント"""
    session_id = str(uuid.uuid4())
    queue = asyncio.Queue()
    active_connections[session_id] = queue
    pending_responses[session_id] = asyncio.Queue()

    async def event_generator():
        # ① 接続確立イベントを送信（session_idを含む）
        yield {
            "event": "connected",
            "data": json.dumps({"session_id": session_id})
        }
        while True:
            if await request.is_disconnected():
                break
            try:
                message = await asyncio.wait_for(
                    pending_responses[session_id].get(), timeout=30.0
                )
                yield {"event": "message", "data": json.dumps(message)}
            except asyncio.TimeoutError:
                # キープアライブ
                yield {"event": "ping",
                       "data": json.dumps({"ts": datetime.now().isoformat()})}

    return EventSourceResponse(event_generator())

@app.post("/messages")
async def messages_endpoint(request: Request):
    """MCPリクエスト受信エンドポイント"""
    body = await request.json()
    session_id = request.headers.get("X-Session-Id")

    if not session_id or session_id not in pending_responses:
        return JSONResponse({"error": "Invalid session_id"}, status_code=400)

    # MCPプロトコルを処理し、レスポンスをSSEキューに追加
    response = process_mcp_request(body)
    if response:
        await pending_responses[session_id].put(response)

    return JSONResponse({"status": "queued"})
```

セッション管理がこの実装のキモです。各クライアントは `GET /sse` で接続すると一意の `session_id` を受け取り、以後の `POST /messages` でそのIDを使うことでレスポンスが正しいSSEストリームに届きます。

### プロキシ側（proxy\_stdio\_http.py）

Claude Desktopは `stdio` でのみMCPサーバーと通信できます。そのため、stdioをSSEに変換するプロキシが必要です。

```
class SSEStdioProxy:
    """stdio と SSE の間を中継するプロキシ"""
    
    async def run(self):
        # 4つのタスクを並行実行
        tasks = [
            asyncio.create_task(self.sse_event_listener()),  # SSEを受信
            asyncio.create_task(self.stdin_reader()),         # stdinを読む
            asyncio.create_task(self.stdout_writer()),        # stdoutに書く
            asyncio.create_task(self.message_forwarder()),    # HTTPに転送
        ]
        done, pending = await asyncio.wait(tasks, 
                                           return_when=asyncio.FIRST_COMPLETED)
        # いずれかが終了したら全タスクを停止
```

4つのコルーチンが並行動作し、それぞれのキューを介して連携します：

### 通信シーケンス

### Claude Desktop 設定

```
{
  "mcpServers": {
    "hello-world-http": {
      "command": "/path/to/venv/bin/python",
      "args": ["/path/to/proxy_stdio_http.py"],
      "env": {
        "PYTHONPATH": "/path/to/project",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

SSEサーバーは別途起動しておく必要があります：

```
python server_http_sse.py --host 127.0.0.1 --port 8999
```

### この実装の特徴

✅ **ネットワーク越しに公開できる**：LAN内の別マシンや将来的にはクラウドへ移行可能  
✅ **複数クライアント対応**：session\_idによるセッション分離  
✅ **ヘルスチェック対応**：`GET /health` でサーバー状態を監視  
⚠️ **2プロセス必要**：サーバーとプロキシの両方を起動する必要がある  
⚠️ **複雑さが増す**：セッション管理、非同期処理の理解が必要

---

## 3実装の比較まとめ

### コード量の比較

同じ「helloツール」の実装に必要なコード：

**実装①（素のMCP SDK）**

```
# base.py + hello.py + registry.py + server.py ... 合計約200行
class HelloTool(BaseTool):
    @property
    def name(self): return "hello"
    @property
    def description(self): return "..."
    @property
    def input_schema(self): return {...}
    async def _execute(self, arguments): ...
```

**実装②（FastMCP）**

```
# 1ファイル、5行
@mcp.tool()
def hello(name: str) -> str:
    """シンプルな挨拶を返します"""
    return f"こんにちは、{name}さん！"
```

**実装③（FastMCP + SSE）**

```
# server_http_sse.py の execute_tool 関数内に直書き
if name == "hello":
    return f"こんにちは、{arguments['name']}さん！🎉"
```

---

## 学習パスとしての読み方

このリポジトリを学習として活用するなら、以下の順序がおすすめです：

1. **実装②から始める**：FastMCPで動くものを最速で作り、MCPの概念を掴む
2. **実装①に進む**：設計パターンを学び、本番向けの実装を理解する
3. **実装③に挑戦**：SSEの仕組みとネットワーク通信の詳細を把握する

---

## まとめ

MCPサーバーの実装方法は一つではありません。

* **FastMCP** は学習・プロトタイピングに圧倒的に速い
* **素のMCP SDK** は設計の自由度と拡張性が高い
* **SSE（HTTPトランスポート）** はネットワーク公開・マルチクライアントに対応できる

どの方法も「JSON-RPC 2.0でLLMと通信する」という本質は同じです。まずFastMCPで感覚を掴んでから、必要に応じて素のSDKやSSEに移行していくのが現実的な学習ルートと言えるでしょう。

---

## 参考リンク
