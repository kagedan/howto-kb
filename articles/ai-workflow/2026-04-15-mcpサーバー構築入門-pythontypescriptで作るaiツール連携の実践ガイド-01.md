---
id: "2026-04-15-mcpサーバー構築入門-pythontypescriptで作るaiツール連携の実践ガイド-01"
title: "MCPサーバー構築入門 — Python/TypeScriptで作るAIツール連携の実践ガイド"
url: "https://note.com/gemini_hack_lab/n/n5f18585907fc"
source: "note"
category: "ai-workflow"
tags: ["MCP", "note"]
date_published: "2026-04-15"
date_collected: "2026-04-15"
summary_by: "auto-rss"
---

サーバー構築入門—で作るツール連携の実践ガイド2025年後半から急速に広がった「MCP（Model Context Protocol）」は、AIアシスタントと外部ツールを接続するためのオープンプロトコルです。Claude DesktopやCursor、VS Codeなどの主要AIツールがMCP対応を進めており、2026年4月現在、AIを業務に組み込むうえで避けて通れない技術になっています。

しかし、MCPに関する情報はまだ英語ドキュメントが中心で、「概念はなんとなく分かるが、実際にサーバーを作って動かすところまでたどり着けない」という声が多いのが現状です。

本記事では、MCPの基本概念から、Python・TypeScriptそれぞれでのサーバー構築、Claude Desktopとの接続、実務で使えるツール実装まで、コード付きで解説します。

この記事で得られること:  
・MCPの仕組み（クライアント・サーバー・トランスポート）を正確に理解できる  
・Python SDKを使ったMCPサーバーを構築・動作確認できる  
・TypeScript SDKを使ったMCPサーバーを構築・動作確認できる  
・Claude Desktopと自作MCPサーバーを接続して実際に動かせる  
・実務向けツール（DB検索、ファイル操作、API連携）の実装パターンを習得できる

第1章: MCPの基本アーキテクチャ

1-1. MCPとは何か

MCP（Model Context Protocol）は、Anthropicが2024年11月に公開したオープンプロトコルです。AIモデル（LLM）が外部のデータソースやツールと通信するための標準規格です。

3つの要素:  
・MCPホスト — MCPクライアントを内蔵するアプリ（Claude Desktop, Cursor, VS Code）  
・MCPクライアント — サーバーとの接続を管理（ホスト内に組み込み）  
・MCPサーバー — ツールやリソースを提供（自作サーバー、公式サーバー）

1-2. MCPが解決する問題

従来のAIツール連携では、ツールごとに個別のプラグイン実装が必要でした。MCPは「USB-Cのような統一規格」として機能し、一度MCPサーバーを作れば、対応するすべてのAIクライアントから利用可能になります。

1-3. MCPの3つの機能

1. Tools（ツール） — LLMが呼び出せる関数（API呼び出し、計算、DB操作など）
2. Resources（リソース） — LLMが参照できるデータ（ファイル内容、DB結果など）
3. Prompts（プロンプト） — 再利用可能なプロンプトテンプレート

第2章: Python SDKでMCPサーバーを構築

2-1. 環境セットアップ

```
pip install mcp[cli] httpx python-dotenv
```

## または uv を使う場合

```
uv add "mcp[cli]" httpx python-dotenv
```

2-2. 最小構成のMCPサーバー

```
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("my-tools")
```

```
@mcp.tool()
def add(a: int, b: int) -> int:
return a + b
```

```
@mcp.tool()
def get_weather(city: str) -> str:
return f"{city}の天気: 晴れ 22°C"
```

```
if name == "main":
mcp.run()
```

2-3. リソースの実装

```
@mcp.resource("config://app-settings")
def get_config() -> str:
return json.dumps({"version": "1.0", "debug": False, "max_retries": 3})
```

```
@mcp.resource("file://{path}")
def read_file(path: str) -> str:
with open(path, "r") as f:
return f.read()
```

2-4. Claude Desktopとの接続

```
claude_desktop_config.json:
{
"mcpServers": {
"my-tools": {
"command": "python",
"args": ["/path/to/server.py"]
}
}
}
```

第3章: TypeScript SDKでMCPサーバーを構築

3-1. 環境セットアップ

```
npm init -y
npm install @modelcontextprotocol/sdk zod
```

3-2. TypeScript版MCPサーバー

```
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
```

```
const server = new McpServer({ name: "my-ts-tools", version: "1.0.0" });
```

```
server.tool("calculate", { expression: z.string() }, async ({ expression }) => {
const result = eval(expression);
return { content: [{ type: "text", text: String(result) }] };
});
```

```
const transport = new StdioServerTransport();
await server.connect(transport);
```

3-3. SSEトランスポート（HTTPサーバー型）

HTTP経由でMCPサーバーを公開し、リモートからアクセス可能にする方法。Express + SSEトランスポートで構築。ポート3001で起動し、/sseエンドポイントと/messagesエンドポイントを提供。

第4章: 実務向けツール実装パターン

4-1. データベース検索ツール

SQLiteやPostgreSQLに接続し、自然言語でDB検索可能にするツール。テーブル一覧取得、SQL実行、スキーマ情報取得の3つのツールを提供。

4-2. ファイル操作ツール

ディレクトリ内のファイル一覧取得、ファイル読み書き、ファイル検索のツール。セキュリティのため、ベースディレクトリ外へのアクセスを制限するバリデーション付き。

4-3. 外部API連携ツール

REST APIを呼び出すツール。HTTPメソッド、URL、ヘッダー、ボディを指定して任意のAPIを呼び出し可能。認証ヘッダーの自動付与にも対応。

第5章: テストとデバッグ

5-1. MCP Inspector

```
npx @modelcontextprotocol/inspector python server.py
```

ブラウザベースのデバッグUIが起動。ツール一覧表示、ツール実行テスト、リソース確認が可能。

5-2. ログ出力の設定

```
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("mcp-server")
```

[各ツール実行時にlogger.info/logger.errorでログ出力。stderrに出力されるため、stdoutのMCP通信と干渉しない。](http://xn--logger-od4elz5ktfv950bwctaot5auu3h.info/logger.error%E3%81%A7%E3%83%AD%E3%82%B0%E5%87%BA%E5%8A%9B%E3%80%82stderr%E3%81%AB%E5%87%BA%E5%8A%9B%E3%81%95%E3%82%8C%E3%82%8B%E3%81%9F%E3%82%81%E3%80%81stdout%E3%81%AEMCP%E9%80%9A%E4%BF%A1%E3%81%A8%E5%B9%B2%E6%B8%89%E3%81%97%E3%81%AA%E3%81%84%E3%80%82)

5-3. ユニットテスト

pytest + mcp.server.testing でサーバーのツール一覧取得、ツール実行結果の検証を自動テスト。

第6章: 本番デプロイと運用

6-1. Docker化

```
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "server.py"]
```

6-2. セキュリティ対策

・入力バリデーション（Zodスキーマ / Pydanticモデル）  
・ファイルアクセスのサンドボックス化（ベースディレクトリ制限）  
・APIキーの環境変数管理  
・レート制限の実装  
・SQLインジェクション対策（パラメータ化クエリ）

6-3. 複数サーバーの管理

claude\_desktop\_config.jsonに複数のMCPサーバーを登録。サーバーごとに異なる環境変数やargs設定が可能。

第7章: よくあるエラーと対処法

・サーバーが起動しない → Python/Node.jsバージョン確認、依存パッケージ確認  
・Claude Desktopに表示されない → config.jsonのパス確認、Claude Desktop再起動  
・ツールが呼び出されない → ツール名のtypo確認、引数スキーマの確認  
・タイムアウトエラー → 処理時間の長いツールにはprogressトークン対応  
・stdoutに余分な出力 → print文をすべてstderrに変更（sys.stderr）

まとめ

MCPはAIと外部ツールを接続する標準プロトコルとして急速に普及しています。本記事で解説した内容を実践すれば、自社業務に特化したAIツール連携を構築できます。

次のステップ:

1. 本記事のサンプルコードでMCPサーバーを動かす
2. 社内DBやAPIに接続するツールを作る
3. Claude Desktop/Cursorで実際に業務に活用する
4. チーム内でMCPサーバーを共有・運用する
