---
id: "2026-05-11-mcpサーバーを1時間で自作するclaude-code-に自分のツールを持たせる最短ルート-01"
title: "MCPサーバーを1時間で自作する：Claude Code に自分のツールを持たせる最短ルート"
url: "https://zenn.dev/yokotaro/articles/41367484adb7f4"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "LLM", "OpenAI"]
date_published: "2026-05-11"
date_collected: "2026-05-12"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Code に「自社のDBを参照させたい」「自作のAPIを叩かせたい」と思ったことはないだろうか。それを実現するのが **MCP（Model Context Protocol）** だ。

公式ドキュメントは英語で、とっつきにくく見える。だが実態はシンプルで、TypeScript なら30行足らずでツールを1本定義できる。この記事では「MCPサーバーとは何か」の概念から、**hello-world MCPサーバーを動かすまで**を最短で説明する。

Notion API連携など実用的なユースケースへの踏み込みは、note 有料記事（リンクを後述）に譲る。まずは「動く体験」を優先する。

---

## MCPとは何か：AIとツールをつなぐ共通言語

MCP（Model Context Protocol）は Anthropic が2024年11月に公開したオープンプロトコルで、2026年5月時点で月間9,700万ダウンロードを超え、OpenAI・Google・Microsoft・AWS といった主要ベンダーが採用している。

一言で言えば **「AIとツールをつなぐUSB-C」** だ。

従来、AIに外部ツールを使わせるには各社独自の function calling 実装を書く必要があった。MCPはこれを標準化した。MCPサーバーを1本書けば、Claude Code・Claude Desktop・その他MCP対応クライアントすべてで再利用できる。

```
┌──────────────────────────────┐
│   Claude Code / Claude Desktop │  ← MCP クライアント
└──────────────┬───────────────┘
               │ JSON-RPC (stdio or HTTP)
┌──────────────▼───────────────┐
│        MCPサーバー             │  ← あなたが書く部分
│  ・tools（関数）               │
│  ・resources（データ）         │
│  ・prompts（テンプレ）         │
└──────────────┬───────────────┘
               │
┌──────────────▼───────────────┐
│  Notion / DB / 自作API など    │  ← 外部ツール・データ
└──────────────────────────────┘
```

MCPサーバーが提供できる機能は3種類ある。

| 機能 | 説明 | 使用例 |
| --- | --- | --- |
| **Tools** | LLMが呼び出せる関数 | DBにデータを書く、APIを叩く |
| **Resources** | 読み取り専用のデータ | ファイル内容、API レスポンス |
| **Prompts** | 再利用可能なテンプレ | 定型プロンプトの共有 |

初学者はまず **Tools** だけを理解すれば十分だ。

---

## 既製MCPサーバーを使う vs 自作する

自作前に確認したいのは「すでに誰かが作っていないか」だ。[MCP Servers の公式リスト](https://github.com/modelcontextprotocol/servers) には2026年5月時点で数百のサーバーが登録されており、Notion・GitHub・Slack・PostgreSQL など主要サービスはカバーされている。

**自作が必要なケース**は主に以下の3つ。

1. 社内専用API・プライベートDB への接続
2. 既製サーバーでは細かい要件が満たせない
3. ビジネスロジックを Claude Code に持たせたい

今回はこのうち「社内ツールに近い想定」で自作の手順を説明する。

---

## 環境構築：TypeScript SDK を選ぶ理由

Zennの読者層を考慮して **TypeScript（Node.js）版** をメインで説明する。Python版も構造は同じなので、適宜読み替えてほしい。

### 前提条件

* Node.js 18以上（`node --version` で確認）
* npm または pnpm

### プロジェクト初期化

```
mkdir hello-mcp
cd hello-mcp
npm init -y
npm install @modelcontextprotocol/sdk zod@3
npm install -D @types/node typescript
mkdir src
```

`package.json` に以下を追記する。

```
{
  "type": "module",
  "scripts": {
    "build": "tsc && chmod 755 build/index.js",
    "start": "node build/index.js"
  },
  "files": ["build"]
}
```

`tsconfig.json` をプロジェクトルートに作成。

```
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "outDir": "./build",
    "rootDir": "./src",
    "strict": true
  }
}
```

---

## ハンズオン：hello-world MCPサーバーを作る

`src/index.ts` を以下の内容で作成する。

```
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

// MCPサーバーのインスタンスを作成
const server = new McpServer({
  name: "hello-mcp",
  version: "1.0.0",
});

// Tool定義：挨拶を返すだけのシンプルなツール
server.tool(
  "greet",                        // ツール名
  "指定した名前への挨拶を返す",    // 説明（Claudeが理解するための文章）
  {
    name: z.string().describe("挨拶する相手の名前"),
  },
  async ({ name }) => {
    return {
      content: [
        {
          type: "text",
          text: `こんにちは、${name}さん！MCPサーバーが正常に動いています。`,
        },
      ],
    };
  }
);

// stdio 経由でクライアントと通信
const transport = new StdioServerTransport();
await server.connect(transport);
console.error("hello-mcp server started"); // stderr に出力（stdout は JSON-RPC 専用）
```

### 重要：stdout に print してはいけない

STDIO トランスポートを使う場合、**stdout は JSON-RPC メッセージの通信路**になる。`console.log()` を使うとメッセージが壊れてサーバーが機能しなくなる。デバッグログは必ず `console.error()` か、ファイルログを使うこと。

### ビルドと起動テスト

```
npm run build
node build/index.js
# → stderr に "hello-mcp server started" が表示されればOK
# Ctrl+C で停止
```

---

## Claude Code に MCPサーバーを登録する

Claude Code に MCPサーバーを認識させる方法は2つある。

**方法1: `claude mcp add` コマンド（手早く試す）**

```
# プロジェクトルートで実行
claude mcp add hello-mcp -- node /絶対パス/hello-mcp/build/index.js
```

**方法2: プロジェクトルートに `.mcp.json` を置く（チーム共有・Git 管理する）**

```
{
  "mcpServers": {
    "hello-mcp": {
      "command": "node",
      "args": ["/絶対パス/hello-mcp/build/index.js"]
    }
  }
}
```

`.mcp.json` をプロジェクトルートに置くと Claude Code が自動で読み込む。Git に含めればチーム全員が同じ MCP 構成で開発できる。

Windows の場合はバックスラッシュを二重にするか、フォワードスラッシュ（`/`）に置き換える。

```
{
  "mcpServers": {
    "hello-mcp": {
      "command": "node",
      "args": ["C:\\Users\\YourName\\hello-mcp\\build\\index.js"]
    }
  }
}
```

登録後、Claude Code 上で `/mcp` を叩くと登録済みサーバー一覧が表示される。「greet ツールで山田太郎に挨拶して」と話しかけると MCPサーバーが呼ばれて応答が返ってくる。

> **Claude Desktop で動かしたい場合**  
> 同じ `mcpServers` キーの JSON は Claude Desktop の `claude_desktop_config.json` にもそのまま貼れる。設置先は macOS が `~/Library/Application Support/Claude/claude_desktop_config.json`、Windows が `%APPDATA%\Claude\claude_desktop_config.json`。完全再起動後、チャット画面下部にハンマーアイコンが出れば成功。

---

## Python版：FastMCPを使う場合

Python 派の方向けに、同等の hello-world を示す。FastMCP は型ヒントとdocstringからツール定義を自動生成してくれる。

```
# uv add "mcp[cli]" で依存を追加してから実行
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("hello-mcp")

@mcp.tool()
async def greet(name: str) -> str:
    """指定した名前への挨拶を返す。

    Args:
        name: 挨拶する相手の名前
    """
    return f"こんにちは、{name}さん！MCPサーバーが正常に動いています。"

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

Python 版を Claude Code に登録する `.mcp.json` は以下の通り。

```
{
  "mcpServers": {
    "hello-mcp": {
      "command": "uv",
      "args": [
        "--directory", "/絶対パス/hello-mcp",
        "run", "server.py"
      ]
    }
  }
}
```

Python SDK は **1.2.0 以上**が必要（2026年5月時点の要件）。

---

## まとめ

* MCP は「AI とツールをつなぐ共通規格」で、2026年現在すべての主要 AI ベンダーが採用
* MCPサーバーの核は **Tools**（関数定義）で、TypeScript なら30行強で1ツールを定義できる
* STDIO トランスポートを使う場合、`console.log()` は使用禁止（`console.error()` か stderr のみ）
* `claude mcp add` コマンドか `.mcp.json` で登録するだけで Claude Code から即使用可能（Claude Desktop も同じ JSON で動く）

---

## 次のステップ：Notion API 連携まで踏み込む

hello-world の次は「実際の外部APIに繋ぐ」フェーズだ。Notion API を使ったページ検索・作成・更新の実装コード、複数ツールの設計パターン、Claude Code の `.claude/` フォルダと連携する実運用 Tips を **note の有料記事** にまとめている。

> **note 記事：MCPサーバーを1時間で自作する完全ガイド（Notion API 連携 実装編）**  
> [https://note.com/（公開後に更新）](https://note.com/%EF%BC%88%E5%85%AC%E9%96%8B%E5%BE%8C%E3%81%AB%E6%9B%B4%E6%96%B0%EF%BC%89)

---

## 参考
