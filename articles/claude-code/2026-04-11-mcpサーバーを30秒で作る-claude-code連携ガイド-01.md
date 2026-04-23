---
id: "2026-04-11-mcpサーバーを30秒で作る-claude-code連携ガイド-01"
title: "MCPサーバーを30秒で作る — Claude Code連携ガイド"
url: "https://zenn.dev/nexus_lab_zen/articles/mcp-server-30sec"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "zenn"]
date_published: "2026-04-11"
date_collected: "2026-04-12"
summary_by: "auto-rss"
---

こんにちは、Nexus LabのZenです。CTOとしてClaude Codeエコシステム向けのツール開発をしています。

この記事では、**MCPサーバーをたった30秒で作る方法**を紹介します。使うのは私たちが開発した `@nexus-lab/create-mcp-server` というCLIツールです。

## MCPとは何か

**MCP（Model Context Protocol）** は、AIアシスタントが外部のツールやデータソースと連携するためのオープンプロトコルです。Anthropic社が策定し、Claude DesktopやClaude Codeなどが標準サポートしています。

MCPサーバーを作ると、Claudeに対して以下のような能力を追加できます。

* **ツール（Tools）** — Claudeが呼び出せる関数（API呼び出し、計算、ファイル操作など）
* **リソース（Resources）** — Claudeが読み取れるデータ（設定ファイル、DBの中身など）
* **プロンプト（Prompts）** — 再利用可能なプロンプトテンプレート

つまりMCPサーバーは「Claudeの手足を増やす仕組み」です。

## なぜMCPサーバーを自作するのか

既存のMCPサーバーもたくさんありますが、自作する理由は明確です。

1. **自社の業務に特化したツールが欲しい** — 社内APIの呼び出し、独自DBへのアクセスなど
2. **セキュリティを自分で管理したい** — 外部サーバーに機密データを渡したくない
3. **Claude Codeの生産性を最大化したい** — 開発ワークフローに合わせたツールを作れる

問題は、MCPサーバーをゼロから作ると地味にボイラープレートが多いこと。SDK導入、TypeScript設定、トランスポート設定、Zodスキーマ...

そこで `@nexus-lab/create-mcp-server` の出番です。

## @nexus-lab/create-mcp-server の使い方

ワンコマンドで実行できます。

```
npx @nexus-lab/create-mcp-server my-server
```

これだけで、TypeScript + MCP SDK + Zodバリデーション付きのプロジェクトが生成されます。

### オプション

| オプション | 説明 | デフォルト |
| --- | --- | --- |
| `-t, --template <template>` | テンプレート選択（minimal / full / http / database / auth） | `minimal` |
| `--no-install` | `npm install` をスキップ | `false` |
| `--no-git` | `git init` をスキップ | `false` |

## テンプレートの選び方

5つのテンプレートを用意しています。用途に合わせて選んでください。

### `minimal` — まずはここから

* ツール1つ + stdioトランスポート
* ファイル数が少なく、MCPの基本を理解するのに最適
* **おすすめ:** 初めてMCPサーバーを作る方、シンプルなツールを素早く作りたい方

### `full` — 本格開発向け

* ツール + リソース + プロンプトのフルセット
* Vitest によるテスト環境付き
* ファイルが機能ごとに分離されていて拡張しやすい
* **おすすめ:** プロダクション用途、複数の機能を持つサーバーを作りたい方

### `http` — Web連携向け

* Express + Streamable HTTPトランスポート
* CORS設定済み
* リモートからアクセスできるMCPサーバーを構築可能
* **おすすめ:** Web APIとして公開したい方、複数クライアントから接続したい方

### `database` — データベース連携（プレミアム）

* SQLite + Drizzle ORM統合
* CRUD操作のツールが一式揃っている
* インメモリDBでのテスト環境付き
* **おすすめ:** データの永続化が必要な方、ノート管理やタスク管理ツールを作りたい方

### `auth` — 認証・認可付き（プレミアム）

* 認証・認可の仕組みが組み込み済み
* セキュアなAPIサーバー構築向け
* **おすすめ:** ユーザー管理やアクセス制御が必要な方

## 実際にminimalテンプレートで作ってみる

### ステップ1: プロジェクト生成

```
npx @nexus-lab/create-mcp-server my-first-mcp
```

対話プロンプトが表示されるので、テンプレートに `minimal` を選択します。テンプレートを直接指定する場合は以下のようにします。

```
npx @nexus-lab/create-mcp-server my-first-mcp -t minimal
```

実行結果：

```
  ⚡ create-mcp-server
  Scaffold a new MCP server in seconds

  ✓ Project created successfully!

  $ cd my-first-mcp
  $ npm run build
  $ node dist/index.js
```

### ステップ2: 生成されたファイルを確認

ディレクトリ構成は以下の通りです。

```
my-first-mcp/
├── src/
│   └── index.ts      # MCPサーバー本体
├── package.json
└── tsconfig.json
```

非常にシンプルですね。`src/index.ts` を見てみましょう。

```
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

// Create the MCP server
const server = new McpServer({
  name: "my-first-mcp",
  version: "0.1.0",
});

// Register a simple greeting tool
server.tool(
  "hello",
  "Greet someone by name",
  { name: z.string().describe("Name of the person to greet") },
  async ({ name }) => ({
    content: [{ type: "text", text: `Hello, ${name}!` }],
  })
);

// Start the server with stdio transport
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch(console.error);
```

ポイントを解説します。

* **`McpServer`** — MCP SDKのサーバークラス。名前とバージョンを設定
* **`server.tool()`** — ツールを登録。第3引数のZodスキーマで入力バリデーションが自動的に行われる
* **`StdioServerTransport`** — 標準入出力でClaudeと通信。Claude DesktopやClaude Codeとの連携はこれが基本

### ステップ3: ビルドして動作確認

これでTypeScriptがコンパイルされ、`dist/index.js` が生成されます。

### ステップ4: ツールをカスタマイズする

たとえば、現在の日時を返すツールを追加してみましょう。`src/index.ts` に以下を追記します。

```
server.tool(
  "current-time",
  "Get the current date and time",
  {},
  async () => ({
    content: [{ type: "text", text: new Date().toISOString() }],
  })
);
```

Zodスキーマに `{}` を渡すと、引数なしのツールになります。簡単ですね。

## Claude Codeとの連携設定

作成したMCPサーバーをClaude Codeで使えるようにするには、設定ファイルに追加します。

### Claude Code（CLI）の場合

プロジェクトルートの `.mcp.json` を作成または編集します。

```
{
  "mcpServers": {
    "my-first-mcp": {
      "command": "node",
      "args": ["./my-first-mcp/dist/index.js"]
    }
  }
}
```

### Claude Desktopの場合

`claude_desktop_config.json` に追加します。

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```
{
  "mcpServers": {
    "my-first-mcp": {
      "command": "node",
      "args": ["/path/to/my-first-mcp/dist/index.js"]
    }
  }
}
```

`/path/to/` は実際のプロジェクトパスに置き換えてください。設定後、Claude DesktopまたはClaude Codeを再起動すると、`hello` ツールと `current-time` ツールが使えるようになります。

## fullテンプレートでツール・リソース・プロンプトを追加する

より本格的なサーバーを作りたい場合は `full` テンプレートを使います。

```
npx @nexus-lab/create-mcp-server my-full-server -t full
```

生成されるディレクトリ構成：

```
my-full-server/
├── src/
│   ├── index.ts       # エントリーポイント
│   ├── tools.ts       # ツール定義
│   ├── resources.ts   # リソース定義
│   └── prompts.ts     # プロンプト定義
├── package.json
└── tsconfig.json
```

機能ごとにファイルが分離されているので、チーム開発でもスケールしやすい構成です。

```
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

export function greet(name: string): string {
  return `Hello, ${name}! Welcome to the MCP server.`;
}

// 安全な式評価（再帰降下パーサー）
// ※ new Function() はコードインジェクションのリスクがあるため使用しません
export function calculate(expression: string): string {
  const sanitized = expression.replace(/\s/g, "");
  if (!/^[\d+\-*/().]+$/.test(sanitized)) {
    throw new Error(
      "Invalid expression. Only numbers and +, -, *, /, (, ) are allowed."
    );
  }
  const result = parseExpression(sanitized);
  if (!Number.isFinite(result)) {
    throw new Error("Expression did not evaluate to a finite number.");
  }
  return String(result);
}
// parseExpression / parseTerm / parseFactor の実装は
// テンプレートのソースコードを参照してください

export function registerTools(server: McpServer): void {
  server.tool(
    "greet",
    "Generate a greeting for the given name",
    { name: z.string().describe("The name to greet") },
    async ({ name }) => ({
      content: [{ type: "text", text: greet(name) }],
    })
  );

  server.tool(
    "calculate",
    "Safely evaluate a mathematical expression",
    {
      expression: z
        .string()
        .describe("Arithmetic expression (e.g. '2 + 3 * 4')"),
    },
    async ({ expression }) => {
      try {
        const result = calculate(expression);
        return { content: [{ type: "text", text: result }] };
      } catch (error) {
        const message =
          error instanceof Error ? error.message : "Unknown error";
        return {
          content: [{ type: "text", text: `Error: ${message}` }],
          isError: true,
        };
      }
    }
  );
}
```

注目すべきポイント：

* **ビジネスロジックが関数としてexportされている** — `greet()` や `calculate()` を直接テストできる
* **安全な式評価** — `calculate` では再帰降下パーサーで式を評価。`new Function()` のようなコードインジェクションリスクを排除している
* **入力バリデーション** — 正規表現で安全な文字のみ許可。Zodスキーマと合わせて二重の防御
* **エラーハンドリング** — `isError: true` を返すことでClaudeにエラーを通知

### リソース（resources.ts）

```
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";

const appConfig = {
  appName: "my-mcp-server",
  version: "0.1.0",
  features: { tools: true, resources: true, prompts: true },
  settings: { maxRetries: 3, timeoutMs: 5000 },
};

export function registerResources(server: McpServer): void {
  server.resource(
    "app-config",
    "config://app",
    { description: "Application configuration data" },
    async () => ({
      contents: [
        {
          uri: "config://app",
          mimeType: "application/json",
          text: JSON.stringify(appConfig, null, 2),
        },
      ],
    })
  );
}
```

リソースは「Claudeが読み取れるデータ」です。設定ファイル、ドキュメント、DB情報などを公開できます。

### プロンプト（prompts.ts）

```
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

export function registerPrompts(server: McpServer): void {
  server.prompt(
    "review-code",
    "Review the provided code and suggest improvements",
    { code: z.string().describe("The source code to review") },
    ({ code }) => ({
      messages: [
        {
          role: "user" as const,
          content: {
            type: "text" as const,
            text: [
              "Please review the following code and provide feedback on:",
              "1. Code quality and readability",
              "2. Potential bugs or edge cases",
              "3. Performance considerations",
              "4. Suggested improvements",
              "",
              "```",
              code,
              "```",
            ].join("\n"),
          },
        },
      ],
    })
  );
}
```

プロンプトは「再利用可能なテンプレート」です。コードレビュー、翻訳、要約など、定型的なプロンプトをサーバー側に定義しておけます。

### エントリーポイント（index.ts）

```
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { registerTools } from "./tools.js";
import { registerResources } from "./resources.js";
import { registerPrompts } from "./prompts.js";

const server = new McpServer({
  name: "my-full-server",
  version: "0.1.0",
});

registerTools(server);
registerResources(server);
registerPrompts(server);

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("MCP server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
```

`register*` 関数を呼ぶだけ。新しい機能を追加するときは、対応するファイルに関数を追加して `register` 関数に登録するだけです。

`full` テンプレートにはVitestも含まれているので、ビジネスロジックのテストもすぐに書き始められます。

## まとめ

`@nexus-lab/create-mcp-server` を使えば、MCPサーバーの作成は本当に30秒で終わります。

```
# これだけ
npx @nexus-lab/create-mcp-server my-server
cd my-server
npm run build
```

あとは `src/index.ts`（または `src/tools.ts`）にツールを追加して、`claude_desktop_config.json` や `.mcp.json` に設定を書くだけ。Claudeがあなた専用のツールを使えるようになります。

**テンプレート選びの早見表:**

| やりたいこと | テンプレート |
| --- | --- |
| とりあえず試したい | `minimal` |
| 本格的に開発したい | `full` |
| HTTPで公開したい | `http` |
| DBと連携したい | `database`（プレミアム） |
| 認証を組み込みたい | `auth`（プレミアム） |

MCPの可能性は無限大です。社内ツール連携、データベースアクセス、外部API統合 — あなたのアイデア次第でClaudeをどこまでも拡張できます。

ぜひ試してみてください。フィードバックお待ちしています。

---

**Links:**
