---
id: "2026-05-17-google-スプレッドシートを-mcp-で-claude-に直接読み書きさせるtypescript-01"
title: "Google スプレッドシートを MCP で Claude に直接読み書きさせる【TypeScript 実装・実用コード全公開】"
url: "https://qiita.com/LemonCake/items/e9dc6ac31e323be92a65"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "API", "LLM", "TypeScript", "qiita"]
date_published: "2026-05-17"
date_collected: "2026-05-18"
summary_by: "auto-rss"
query: ""
---

:::note
この記事で作る Google Sheets MCP サーバーのような「外部 API 連携 MCP」は、**pay-per-call-mcp** に組み込むことで Claude から USDC 課金付きで呼び出せます。
- **npm**: https://www.npmjs.com/package/pay-per-call-mcp
- **Glama**: https://glama.ai/mcp/servers/@evid-ai/pay-per-call-mcp
:::

## この記事でわかること

- Google スプレッドシートを読み書きする MCP サーバーを TypeScript で自作する方法
- OAuth2 認証で安全に Google Sheets API に接続する手順
- `read_sheet` / `write_sheet` / `append_rows` / `create_sheet` の 4 ツール実装
- Claude Desktop から「この月の経費をスプレッドシートにまとめて」と話せるようになる構成
- freee・マネーフォワードの CSV エクスポート → Sheets 自動集計パターン

---

## はじめに

「Claude、今月の売上データをスプレッドシートに転記して」——これが MCP サーバー 1 本で実現できます。

Google Sheets API はドキュメントが充実していますが、OAuth2 の設定でつまずく人が多いです。この記事では **動くコードをそのままコピペできる**形で全手順を解説します。

---

## セットアップ

### 1. Google Cloud Console の設定

1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクト作成
2. **Google Sheets API** と **Google Drive API** を有効化
3. 認証情報 → OAuth 2.0 クライアント ID（デスクトップアプリ）を作成
4. `credentials.json` をダウンロード

### 2. npm パッケージ

```bash
mkdir google-sheets-mcp && cd google-sheets-mcp
npm init -y
npm install @modelcontextprotocol/sdk googleapis
npm install -D typescript @types/node tsx
```

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "node16",
    "moduleResolution": "node16",
    "outDir": "dist",
    "strict": true
  }
}
```

---

## 実装

### Google 認証モジュール

```typescript
// src/auth.ts
import { google } from "googleapis";
import * as fs from "fs";
import * as path from "path";
import * as readline from "readline";

const SCOPES = [
  "https://www.googleapis.com/auth/spreadsheets",
  "https://www.googleapis.com/auth/drive.readonly",
];
const TOKEN_PATH = path.join(process.env.HOME!, ".google-sheets-mcp-token.json");

export async function getAuthClient() {
  const credPath = process.env.GOOGLE_CREDENTIALS_PATH
    ?? path.join(process.env.HOME!, ".google-credentials.json");

  const credentials = JSON.parse(fs.readFileSync(credPath, "utf-8"));
  const { client_secret, client_id, redirect_uris } = credentials.installed;
  const oAuth2Client = new google.auth.OAuth2(client_id, client_secret, redirect_uris[0]);

  // キャッシュ済みトークンがあれば使用
  if (fs.existsSync(TOKEN_PATH)) {
    const token = JSON.parse(fs.readFileSync(TOKEN_PATH, "utf-8"));
    oAuth2Client.setCredentials(token);
    return oAuth2Client;
  }

  // 初回認証
  const authUrl = oAuth2Client.generateAuthUrl({ access_type: "offline", scope: SCOPES });
  console.error("以下の URL を開いて認証してください:");
  console.error(authUrl);

  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  const code = await new Promise<string>(resolve =>
    rl.question("認証コードを入力してください: ", answer => { rl.close(); resolve(answer); })
  );

  const { tokens } = await oAuth2Client.getToken(code);
  oAuth2Client.setCredentials(tokens);
  fs.writeFileSync(TOKEN_PATH, JSON.stringify(tokens));
  return oAuth2Client;
}
```

### MCP サーバー本体

```typescript
// src/index.ts
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { google } from "googleapis";
import { getAuthClient } from "./auth.js";

const server = new Server(
  { name: "google-sheets-mcp", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

// ツール定義
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "read_sheet",
      description: "Google スプレッドシートの指定範囲を読み取る",
      inputSchema: {
        type: "object",
        properties: {
          spreadsheetId: { type: "string", description: "スプレッドシートの ID（URL の /d/XXXXX/ 部分）" },
          range: { type: "string", description: "A1 記法 例: Sheet1!A1:D10" },
        },
        required: ["spreadsheetId", "range"],
      },
    },
    {
      name: "write_sheet",
      description: "Google スプレッドシートの指定範囲に値を書き込む（上書き）",
      inputSchema: {
        type: "object",
        properties: {
          spreadsheetId: { type: "string" },
          range: { type: "string", description: "例: Sheet1!A1" },
          values: {
            type: "array",
            items: { type: "array" },
            description: "2次元配列 例: [[\"名前\",\"金額\"],[\"田中\",5000]]",
          },
        },
        required: ["spreadsheetId", "range", "values"],
      },
    },
    {
      name: "append_rows",
      description: "スプレッドシートの末尾に行を追加する",
      inputSchema: {
        type: "object",
        properties: {
          spreadsheetId: { type: "string" },
          sheetName: { type: "string", description: "シート名 例: Sheet1" },
          values: { type: "array", items: { type: "array" } },
        },
        required: ["spreadsheetId", "sheetName", "values"],
      },
    },
    {
      name: "create_sheet",
      description: "新しいスプレッドシートを作成する",
      inputSchema: {
        type: "object",
        properties: {
          title: { type: "string", description: "スプレッドシートのタイトル" },
          headers: {
            type: "array",
            items: { type: "string" },
            description: "1行目のヘッダー",
          },
        },
        required: ["title"],
      },
    },
  ],
}));

// ツール実行
server.setRequestHandler(CallToolRequestSchema, async (req) => {
  const auth = await getAuthClient();
  const sheets = google.sheets({ version: "v4", auth });

  switch (req.params.name) {
    case "read_sheet": {
      const { spreadsheetId, range } = req.params.arguments as any;
      const res = await sheets.spreadsheets.values.get({ spreadsheetId, range });
      const rows = res.data.values ?? [];
      return {
        content: [{
          type: "text",
          text: JSON.stringify({ range, rowCount: rows.length, values: rows }, null, 2),
        }],
      };
    }

    case "write_sheet": {
      const { spreadsheetId, range, values } = req.params.arguments as any;
      await sheets.spreadsheets.values.update({
        spreadsheetId,
        range,
        valueInputOption: "USER_ENTERED",
        requestBody: { values },
      });
      return {
        content: [{ type: "text", text: `✅ ${range} に ${values.length} 行書き込みました` }],
      };
    }

    case "append_rows": {
      const { spreadsheetId, sheetName, values } = req.params.arguments as any;
      await sheets.spreadsheets.values.append({
        spreadsheetId,
        range: `${sheetName}!A1`,
        valueInputOption: "USER_ENTERED",
        requestBody: { values },
      });
      return {
        content: [{ type: "text", text: `✅ ${values.length} 行追加しました` }],
      };
    }

    case "create_sheet": {
      const { title, headers } = req.params.arguments as any;
      const drive = google.drive({ version: "v3", auth });
      const res = await sheets.spreadsheets.create({
        requestBody: {
          properties: { title },
          sheets: [{ properties: { title: "Sheet1" } }],
        },
      });
      const id = res.data.spreadsheetId!;

      if (headers?.length) {
        await sheets.spreadsheets.values.update({
          spreadsheetId: id,
          range: "Sheet1!A1",
          valueInputOption: "USER_ENTERED",
          requestBody: { values: [headers] },
        });
      }

      return {
        content: [{
          type: "text",
          text: `✅ 作成しました: https://docs.google.com/spreadsheets/d/${id}`,
        }],
      };
    }

    default:
      throw new Error(`Unknown tool: ${req.params.name}`);
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);
```

---

## Claude Desktop に設定

```json
// ~/Library/Application Support/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "google-sheets": {
      "command": "npx",
      "args": ["tsx", "/path/to/google-sheets-mcp/src/index.ts"],
      "env": {
        "GOOGLE_CREDENTIALS_PATH": "/Users/yourname/.google-credentials.json"
      }
    }
  }
}
```

初回起動時にターミナルで認証 URL が表示されます。ブラウザで開いて認証コードを入力すると `~/.google-sheets-mcp-token.json` にトークンが保存され、以降は自動認証されます。

---

## 実際の使い方（Claude との会話例）

### 経費データの読み取り・分析

```
ユーザー: スプレッドシート（ID: 1BxiMVs0XRA...）の「経費」シートを読んで、
         カテゴリ別に集計して

Claude: read_sheet で取得します...

Sheet1!A1:E50 のデータを取得しました（48行）

カテゴリ別集計:
- 交通費: 32,400円（12件）
- 消耗品: 18,700円（8件）
- 外食接待: 45,000円（6件）
- 通信費: 9,800円（3件）
合計: 105,900円
```

### freee CSV → スプレッドシート転記

```
ユーザー: freee からエクスポートした CSV を貼るから、
         毎月の売上サマリーシートに追記して

Claude: append_rows で追記します...

✅ 5行追加しました（2026年4月分）
```

### 在庫管理シートの自動更新

```
ユーザー: 在庫が10個を切った商品を調べて、
         「発注リスト」シートに書き出して

Claude: まず在庫シートを読みます...

在庫10個未満: 3商品
- SKU-001 ノートPC用スタンド: 残7個
- SKU-034 USBハブ 7ポート: 残3個
- SKU-091 キーボードカバー: 残9個

write_sheet で「発注リスト」シートに書き込みました ✅
```

---

## freee・マネーフォワードとの連携パターン

```typescript
// freee CSVをパースしてスプレッドシートに転記
async function importFreeeToSheets(
  csvContent: string,
  spreadsheetId: string
) {
  const lines = csvContent.split("\n").slice(1); // ヘッダー除く
  const rows = lines
    .filter(l => l.trim())
    .map(l => {
      const cols = l.split(",");
      return [
        cols[0], // 日付
        cols[2], // 勘定科目
        cols[4], // 金額
        cols[6], // 摘要
      ];
    });

  // append_rows ツール経由で追記
  await callMcpTool("append_rows", {
    spreadsheetId,
    sheetName: "仕訳データ",
    values: rows,
  });
}
```

---

## よくあるエラー

| エラー | 原因・対処 |
|---|---|
| `The caller does not have permission` | Drive API も有効化されているか確認 |
| `Range not found` | シート名が正確か確認（全角スペースに注意）|
| `Token has been expired` | `~/.google-sheets-mcp-token.json` を削除して再認証 |
| `invalid_grant` | credentials.json が古い可能性。再ダウンロード |

---

## まとめ

| 機能 | ツール |
|---|---|
| データ読み取り | `read_sheet` |
| 上書き書き込み | `write_sheet` |
| 行末尾追加 | `append_rows` |
| 新規作成 | `create_sheet` |

Google Sheets MCP を使えば「データを見て → 分析して → 書き直す」という繰り返し作業を Claude に委託できます。freee や マネーフォワードの CSV を組み合わせると、経理業務のほぼ全自動化が視野に入ります。

---

## よくある質問（FAQ）

**Q. サービスアカウント（SA）でも使えますか？**
A. 使えます。SA の場合は `credentials.json` の代わりに SA の JSON キーを使い、スプレッドシートをそのメールアドレスに共有してください。ユーザー操作不要でサーバー上でも動きます。

**Q. スプレッドシートの ID はどこで確認できますか？**
A. URL の `https://docs.google.com/spreadsheets/d/【ここ】/edit` の部分です。

**Q. 1,000 行以上のデータを扱えますか？**
A. Sheets API の 1 リクエスト上限は 1,000 × 1,000 セルです。大量データの場合は `range` を分割してページング処理を実装してください。

**Q. Claude から直接 Google アカウントにアクセスされないですか？**
A. MCP サーバーはローカルで動くため、ネットワーク的には「あなたの PC → Google API」です。トークンはローカルの `~/.google-sheets-mcp-token.json` に保存され、Claude に渡るのはデータのみです。
