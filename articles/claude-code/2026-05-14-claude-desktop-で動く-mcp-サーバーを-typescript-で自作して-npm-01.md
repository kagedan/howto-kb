---
id: "2026-05-14-claude-desktop-で動く-mcp-サーバーを-typescript-で自作して-npm-01"
title: "Claude Desktop で動く MCP サーバーを TypeScript で自作して npm publish するまで"
url: "https://qiita.com/LemonCake/items/1320efe815220fdeb259"
source: "qiita"
category: "claude-code"
tags: ["MCP", "API", "LLM", "JavaScript", "TypeScript", "qiita"]
date_published: "2026-05-14"
date_collected: "2026-05-15"
summary_by: "auto-rss"
query: ""
---

---
title: Claude Desktop で動く MCP サーバーを TypeScript で自作して npm publish するまで
---

## はじめに

**MCP（Model Context Protocol）** は Anthropic が策定したオープンプロトコルで、AI モデルが外部のツール・データソースを標準インターフェースで呼び出せるようにする仕組みです。HTTP でいう REST のような位置づけで、LLM クライアント（Claude Desktop など）と任意のサーバーの間を繋ぐ「共通言語」として機能します。

MCP サーバーを自作すると、Claude が自分のデータベース・社内 API・自作スクリプトを直接呼び出せるようになります。TypeScript + Node.js で実装でき、公式 SDK も整備されているため、習得コストは想像より低いです。

この記事では、最小構成の MCP サーバーを TypeScript で書き、esbuild でバンドルし、npm に publish するまでの全手順を説明します。

---

## 完成形のデモ

Claude Desktop に次の一文を送ると、

> hello_world を呼んで

このように返ってきます。

```
こんにちは！MCP サーバーから返答しています。
```

Claude が「ツールを呼ぶ」→「サーバーがレスポンスを返す」→「Claude が結果を解釈して回答する」という流れを stdio 経由で行っています。実際には HTTP リクエストは発生せず、Claude Desktop がサブプロセスとして MCP サーバーを起動します。

---

## プロジェクト構成

```
my-mcp-server/
├── src/
│   └── index.ts        # MCP サーバー本体
├── dist/               # esbuild が生成するバンドル済みファイル
│   └── index.mjs
├── build.mjs           # esbuild バンドルスクリプト
├── package.json
└── tsconfig.json
```

ポイントは `dist/` に単一ファイルを生成する構成にすることです。`node_modules` ごとバンドルするため、Claude Desktop のプロセスから呼び出すときにパス解決の問題が起きません。

---

## 実装

### パッケージのインストール

```bash
npm init -y
npm install @modelcontextprotocol/sdk
npm install -D typescript @types/node esbuild tsx
```

### src/index.ts の基本構造

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

// 1. Server インスタンスを作成
const server = new Server(
  { name: "my-mcp-server", version: "0.1.0" },
  { capabilities: { tools: {} } }
);

// 2. ツール一覧を返すハンドラ
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "hello_world",
      description: "挨拶メッセージを返すだけのサンプルツール。",
      inputSchema: {
        type: "object",
        properties: {
          name: {
            type: "string",
            description: "挨拶する相手の名前（省略可）",
          },
        },
        additionalProperties: false,
      },
    },
  ],
}));

// 3. ツール呼び出しを処理するハンドラ
server.setRequestHandler(CallToolRequestSchema, async (req) => {
  const { name, arguments: args } = req.params;

  if (name === "hello_world") {
    const target = (args as { name?: string }).name ?? "世界";
    return {
      content: [
        {
          type: "text",
          text: `こんにちは、${target}！MCP サーバーから返答しています。`,
        },
      ],
    };
  }

  throw new Error(`Unknown tool: ${name}`);
});

// 4. stdio transport で起動
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  // stderr にだけログを出す（stdout は MCP プロトコルが使う）
  console.error("my-mcp-server started");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
```

#### 重要な注意点

- **`console.log()` を使ってはいけない。** MCP の stdio トランスポートは stdout をプロトコル通信に使います。サーバー内でのログ出力は必ず `console.error()` で stderr に向けてください。
- `ListToolsRequestSchema` でツール定義を返し、`CallToolRequestSchema` で実行を受け取る、という二段構えが基本パターンです。
- `inputSchema` は JSON Schema 形式で書きます。Claude はここを見てどんな引数を渡すか判断します。

### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "strict": true,
    "outDir": "dist"
  },
  "include": ["src"]
}
```

---

## esbuild でバンドルして単一ファイルにする

TypeScript をそのままデプロイすると、実行環境に `tsx` や `ts-node` が必要になります。esbuild で依存ごと単一ファイルにバンドルすれば、`node dist/index.mjs` の一行で動きます。

### build.mjs

```javascript
#!/usr/bin/env node
import { build } from "esbuild";
import { chmodSync, rmSync, mkdirSync } from "fs";

// ビルド前に dist を掃除
rmSync("dist", { recursive: true, force: true });
mkdirSync("dist", { recursive: true });

await build({
  entryPoints: ["src/index.ts"],
  bundle: true,          // node_modules ごとバンドル
  platform: "node",
  target: ["node18"],
  format: "esm",
  outfile: "dist/index.mjs",
  banner: {
    js: [
      "#!/usr/bin/env node",
      // ESM バンドル内で require() を使うパッケージへの対応
      'import { createRequire as __cr } from "module";',
      'import { fileURLToPath as __ftp } from "url";',
      'import { dirname as __dn } from "path";',
      "var require = __cr(import.meta.url);",
      "var __filename = __ftp(import.meta.url);",
      "var __dirname = __dn(__filename);",
    ].join("\n"),
  },
  define: {
    "process.env.NODE_ENV": '"production"',
  },
  logLevel: "warning",
});

// 実行権限を付与（npx で直接起動するために必要）
chmodSync("dist/index.mjs", 0o755);
console.log("✓ dist/index.mjs bundled");
```

`banner` で `require` のポリフィルを埋め込んでいるのは、ESM バンドルに CJS 形式のパッケージが混入したときのクラッシュを防ぐためです。依存が純粋 ESM だけなら不要ですが、保険として入れておくと安心です。

ビルドは次のコマンドで実行します。

```bash
node build.mjs
```

---

## claude_desktop_config.json への追加方法

Claude Desktop の設定ファイルに MCP サーバーを登録します。

**設定ファイルの場所:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

### ローカルパスで直接指定する場合

```json
{
  "mcpServers": {
    "my-mcp-server": {
      "command": "node",
      "args": ["/absolute/path/to/my-mcp-server/dist/index.mjs"]
    }
  }
}
```

### npm publish 後に npx で使う場合

```json
{
  "mcpServers": {
    "my-mcp-server": {
      "command": "npx",
      "args": ["-y", "my-mcp-server"]
    }
  }
}
```

設定を変更したら Claude Desktop を再起動します。ツールアイコンが表示されれば接続成功です。

環境変数を渡したい場合は `"env"` キーを追加します。

```json
{
  "mcpServers": {
    "my-mcp-server": {
      "command": "npx",
      "args": ["-y", "my-mcp-server"],
      "env": {
        "MY_API_KEY": "sk-xxxx"
      }
    }
  }
}
```

---

## npm publish の手順

### package.json の設定

```json
{
  "name": "my-mcp-server",
  "version": "0.1.0",
  "description": "My first MCP server",
  "main": "dist/index.mjs",
  "bin": {
    "my-mcp-server": "./dist/index.mjs"
  },
  "files": [
    "dist",
    "README.md",
    "LICENSE"
  ],
  "scripts": {
    "build": "node build.mjs",
    "dev": "tsx src/index.ts",
    "prepublishOnly": "npm run build"
  },
  "publishConfig": {
    "access": "public"
  }
}
```

#### 各フィールドの役割

| フィールド | 役割 |
|---|---|
| `bin` | `npx my-mcp-server` で起動できるようにする。Claude Desktop の `"command": "npx"` 構成に必須 |
| `files` | publish に含めるファイルを制限。`src/` や `node_modules/` を除外してサイズを削減 |
| `prepublishOnly` | `npm publish` 前に自動でビルドを走らせる。ビルド忘れ防止 |
| `publishConfig.access` | スコープ付きパッケージ（`@scope/name`）を public で出すのに必要 |

### publish の実行

```bash
# npm にログイン（初回のみ）
npm login

# publish（prepublishOnly でビルドが自動実行される）
npm publish
```

`npm login` は Granular Access Token を使った認証に対応しています。npmjs.com の Account Settings → Access Tokens から **Granular Access Token** を発行し、`~/.npmrc` に設定するか、`npm login` のフローに従ってください。

publish が成功すると、数分後に `npx my-mcp-server` で世界中から呼び出せるようになります。

---

## まとめ・参考リンク

TypeScript で MCP サーバーを書く際の最小ステップをまとめます。

1. `@modelcontextprotocol/sdk` をインストール
2. `ListToolsRequestSchema` でツール定義を返す
3. `CallToolRequestSchema` で処理を実装
4. `StdioServerTransport` で起動（ログは必ず `console.error`）
5. esbuild でバンドルして `dist/index.mjs` を生成
6. `package.json` の `bin` に登録して `npm publish`
7. `claude_desktop_config.json` に `npx` 経由で登録

一度この構成を作ってしまえば、あとはツールを増やすだけです。ファイル操作・DB クエリ・社内 API の呼び出しなど、何でも Claude から呼べるようになります。

### 参考リンク

- [Model Context Protocol 公式ドキュメント](https://modelcontextprotocol.io/)
- [@modelcontextprotocol/sdk (npm)](https://www.npmjs.com/package/@modelcontextprotocol/sdk)
- [MCP サーバー一覧 (awesome-mcp-servers)](https://github.com/punkpeye/awesome-mcp-servers)

---

### 応用例：複数の有料 API を MCP 経由で叩く

MCP サーバーを量産していくと「各サーバーに API キーを個別に設定するのが面倒」という問題に当たります。

[**LemonCake / pay-per-call-mcp**](https://github.com/evidai/lemon-cake) はこの課題へのひとつのアプローチです。Tavily（検索）、Hunter（メール検索）、NTA（法人番号）など複数の有料 API を一つの MCP サーバーにまとめ、USDC でまとめて従量課金できる構成になっています。「API キーを揃えるほどでもないが、Claude から呼びたい」という用途に向いています。こういう多機能サーバーの組み立て方の参考にもなると思います。
