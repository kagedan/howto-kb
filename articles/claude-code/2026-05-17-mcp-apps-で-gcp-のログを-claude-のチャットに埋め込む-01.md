---
id: "2026-05-17-mcp-apps-で-gcp-のログを-claude-のチャットに埋め込む-01"
title: "MCP Apps で GCP のログを Claude のチャットに埋め込む"
url: "https://zenn.dev/choshosu/articles/7f6119a631635a"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "Gemini", "JavaScript", "TypeScript"]
date_published: "2026-05-17"
date_collected: "2026-05-18"
summary_by: "auto-rss"
query: ""
---

## はじめに

GCP の Logs Explorer を使っていると、画面右上に「Gemini に質問」ボタンがあるのをご存知でしょうか。ログの内容を Gemini が解釈して説明してくれる便利な機能です。

「これ、Claude でもできないだろうか？」

そう思って調べていたところ、 **MCP Apps** という仕組みを使えば、**Claude のチャット画面にインタラクティブな UI を埋め込める**ことがわかりました。これを使えば、Cloud Logging のログをビューアとして表示し、気になるログを選択して Claude に直接質問できるのでは？

本記事では、MCP Apps を使って **Cloud Logging のログビューア** を作成し、Claude Desktop 上でログの閲覧・選択・質問ができる環境を構築した手順を共有します。

### この記事でできるようになること

* MCP Apps の仕組みを理解する
* Cloud Logging API からログを取得する MCP サーバーを TypeScript で実装する
* Claude Desktop 上でログビューア UI を表示し、ログを選択して質問する

### 前提知識

* MCP（Model Context Protocol）の基本的な概念
* GCP プロジェクトの操作経験
* TypeScript の基礎

## MCP Apps とは

MCP Apps は、MCP サーバーに **HTML ベースのインタラクティブ UI** を持たせる拡張仕様です。実装には 2 つのステップがあります:

1. **UI リソースの登録** — `registerAppResource` で HTML（JS インライン済み）をリソースとして登録
2. **ツールと UI の紐付け** — `registerAppTool` のオプションに `_meta.ui.resourceUri` を指定し、ツール呼び出し時にどの UI を表示するかを宣言

通常の MCP ツールはテキストを返すだけですが、MCP Apps を使うと：

* チャット内に地図、グラフ、フォームなどの **リッチ UI** を表示できる
* UI 内でのユーザー操作を `updateModelContext` で **AI のコンテキストにフィードバック** できる
* UI は **iframe サンドボックス** 内で安全に実行される
* UI とサーバーは **直接通信しない** — 常に Host（Claude Desktop）が仲介する

公式の map-server サンプル（CesiumJS 地球儀）で仕組みを確認し、同じパターンでログビューアを作成しました。

> 参考: [MCP Apps 入門概要 — Classmethod](https://dev.classmethod.jp/articles/mcp-apps-introduction-overview/)

## アーキテクチャ

今回のアーキテクチャは以下の構成です。MCP サーバーはローカルで動作し、Claude Desktop と stdio で通信します。

![image.png](https://res.cloudinary.com/zenn/image/fetch/s--LkF1j9Gt--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4054284/87dbde8f-919f-41ed-9ed2-242a89946226.png?_a=BACAGSGT)

## 事前準備

### GCP 側

1. **Cloud Logging API の有効化を確認**

   * GCP Console → APIs & Services → Library → 「Cloud Logging API」が有効であること（通常はデフォルトで有効）
2. **ADC（Application Default Credentials）の設定**

   ```
   gcloud auth application-default login
   ```

   ADC で認証されるユーザーには、対象プロジェクトに対する `roles/logging.viewer`（ログ閲覧者）以上の権限が必要です。プロジェクトオーナーであれば問題ありません。
3. **対象プロジェクトの確認**

   * ログが存在するプロジェクト ID をメモ（例: `my-project-id`）
   * GCP Console → Logging → Logs Explorer でログが見えることを確認

### ローカル環境

* Node.js 20 以上
* Claude Desktop（最新版）

## 実装

### プロジェクト構成

```
mcp-apps-sample/
├── package.json
├── tsconfig.json
├── vite.config.ts          # UI を単一 HTML にバンドル
├── server.ts               # MCP サーバー（Cloud Logging API 呼び出し）
├── index.ts                # エントリポイント（stdio / HTTP 切替）
├── mcp-app.html            # UI テンプレート
└── src/
    └── mcp-app.ts           # UI ロジック（ログ表示 + 選択）
```

### セットアップ

```
git clone https://github.com/chososu/mcp-apps-sample.git
cd mcp-apps-sample
npm install
npm run build
```

### サーバーと UI の役割分担

MCP Apps では **サーバー（server.ts）** と **UI（mcp-app.ts）** が明確に分かれています。

| ファイル | 言語 | 実行環境 | 役割 |
| --- | --- | --- | --- |
| `server.ts` | TypeScript (Node.js) | ローカルプロセス | Cloud Logging API を叩いてログデータを取得・返却 |
| `mcp-app.ts` | TypeScript (ブラウザ) | iframe サンドボックス | ログデータを受け取って表示、ユーザー操作を Claude にフィードバック |

サーバーは 2 つのツールを提供します。

| ツール | UI | 用途 |
| --- | --- | --- |
| `show-log-viewer` | あり（MCP Apps） | ログをビューアで表示、選択して質問 |
| `get-logs` | なし | Claude にテキストでログを渡して直接分析 |

#### ハマりポイント: `@google-cloud/logging` ではなく REST API を直接叩く

最初は `@google-cloud/logging` の Node.js ライブラリを使っていましたが、**AuditLog（protoPayload）が protobuf の Buffer のまま返される**という問題に遭遇しました。

```
// ❌ @google-cloud/logging の getEntries()
// protoPayload が {type_url: "...", value: <Buffer>} で返る
// JSON.stringify すると [18,0,26,52,...] というバイト配列になる
```

Cloud Logging REST API (`entries:list`) を直接叩くと、**protoPayload がデコード済みの JSON で返ってきます**。

```
// ✅ REST API の応答
// entry.protoPayload.authenticationInfo.principalEmail → "user@example.com"
// entry.protoPayload.methodName → "google.cloud.bigquery.v2.JobService.InsertJob"
```

これにより、ログメッセージを人間が読める形で表示できるようになりました。

```
import { GoogleAuth } from "google-auth-library";

const auth = new GoogleAuth({
  scopes: ["https://www.googleapis.com/auth/logging.read"],
});

async function fetchLogEntries(options: {
  projectId: string;
  startTime: string;
  endTime: string;
  severity?: string;
  maxEntries?: number;
}) {
  const client = await auth.getClient();
  const tokenResponse = await client.getAccessToken();

  const filterParts = [
    `timestamp >= "${options.startTime}"`,
    `timestamp <= "${options.endTime}"`,
  ];
  if (options.severity) {
    filterParts.push(`severity >= "${options.severity.toUpperCase()}"`);
  }

  const response = await fetch(
    "https://logging.googleapis.com/v2/entries:list",
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${tokenResponse.token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        resourceNames: [`projects/${options.projectId}`],
        filter: filterParts.join(" AND "),
        orderBy: "timestamp desc",
        pageSize: options.maxEntries ?? 100,
      }),
    },
  );

  const data = await response.json();
  return (data.entries ?? []).map((entry: any) => ({
    timestamp: entry.timestamp,
    severity: entry.severity ?? "DEFAULT",
    message: extractMessage(entry),
    resource: entry.resource?.type ?? "",
  }));
}
```

#### MCP Apps ツールの登録

MCP Apps のツールは、通常のツール定義に `_meta.ui.resourceUri` を追加するだけです。

```
import {
  registerAppTool,
  registerAppResource,
  RESOURCE_MIME_TYPE,
} from "@modelcontextprotocol/ext-apps/server";

const resourceUri = "ui://cloud-logging/mcp-app.html";

// ① UI リソースの登録（HTML をリソースとして返す）
registerAppResource(
  server,
  resourceUri,       // リソース URI
  resourceUri,       // リソース名
  { mimeType: RESOURCE_MIME_TYPE },
  async () => ({
    contents: [{
      uri: resourceUri,
      mimeType: RESOURCE_MIME_TYPE,
      text: await fs.readFile(
        path.join(DIST_DIR, "mcp-app.html"), "utf-8"
      ),
    }],
  }),
);

// ② UI 付きツールの登録
registerAppTool(
  server,
  "show-log-viewer",
  {
    title: "Show Log Viewer",
    description: "Display an interactive log viewer for GCP Cloud Logging.",
    inputSchema: {
      projectId: z.string().describe("GCP Project ID"),
      startTime: z.string().optional(),
      endTime: z.string().optional(),
      severity: z.string().optional(),
      maxEntries: z.number().optional().default(100),
    },
    _meta: { ui: { resourceUri } },  // ← ①で登録した URI を指定
  },
  async ({ projectId, startTime, endTime, severity, maxEntries }) => {
    const entries = await fetchLogEntries({
      projectId,
      startTime: startTime ?? new Date(Date.now() - 3600000).toISOString(),
      endTime: endTime ?? new Date().toISOString(),
      severity,
      maxEntries,
    });
    return {
      content: [{
        type: "text",
        text: JSON.stringify({ projectId, totalEntries: entries.length, entries }),
      }],
    };
  },
);
```

### UI 実装（src/mcp-app.ts）

ここからは **iframe 内で動くフロントエンド側**の実装です。サーバーが取得したログデータを受け取り、ブラウザ上でレンダリングします。

サーバーとUIの紐付けは、サーバー側で `registerAppTool` に指定した `_meta.ui.resourceUri` によって行われます。Claude Desktop がこの URI を見て、ツール呼び出し時に対応する HTML を iframe に読み込みます。

UI は `@modelcontextprotocol/ext-apps` SDK を使って実装します。

```
import { App } from "@modelcontextprotocol/ext-apps";

const app = new App(
  { name: "Cloud Logging Viewer", version: "1.0.0" },
  { tools: { listChanged: true } },
);

// ツールの実行結果（ログデータ JSON）を受け取って表示
app.ontoolresult = async (result) => {
  // result はツールの CallToolResult 形式で来る
  // content 配列内のテキストからログデータを取り出す
  const parsed = parseLogData(result);
  if (parsed) {
    renderLogEntries(parsed.entries);
  }
};

// ログをクリックで選択 → 選択内容をコンテキストとして Claude に送信
// これにより、ユーザーが「選択したログについて教えて」と聞けばすぐ回答できる
function onSelectionChange(selectedEntries: LogEntry[]) {
  app.updateModelContext({
    content: [{
      type: "text",
      text: `ユーザーが ${selectedEntries.length} 件のログを選択しました:\n` +
        selectedEntries.map(e =>
          `${e.timestamp} [${e.severity}] ${e.message}`
        ).join("\n"),
    }],
  });
}

await app.connect();
```

ここでのポイントは `ontoolresult` と `updateModelContext` の役割の違いです:

* **`ontoolresult`**: サーバーがツールを実行した結果を UI が受け取るコールバック。ここでログデータを受け取って画面に描画する
* **`updateModelContext`**: UI から Claude に情報を送るメソッド。ユーザーがログを選択するたびに呼び出し、Claude が選択内容を把握できるようにする

#### ハマりポイント: Vite のビルド設定

MCP Apps の UI は iframe の `srcdoc` として読み込まれるため、**JavaScript を外部ファイルとして参照できません**。`vite-plugin-singlefile` で HTML に JS をインラインで埋め込む必要があります。

```
// vite.config.ts
import { viteSingleFile } from "vite-plugin-singlefile";

export default defineConfig({
  plugins: [viteSingleFile()],
  build: {
    outDir: "dist",
    emptyOutDir: false,
  },
});
```

これを忘れると、UI は表示されるものの JavaScript が読み込まれず、黒い画面のまま動かないという状態になります。

### Claude Desktop の設定

`claude_desktop_config.json` に MCP サーバーを追加します。

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`  
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```
{
  "mcpServers": {
    "cloud-logging": {
      "command": "node",
      "args": ["C:/path/to/dist/index.js", "--stdio"]
    }
  }
}
```

> **注意**: `mcpServers` はトップレベルに配置してください。`preferences` の中に入れると認識されません。

設定後、Claude Desktop を再起動すると MCP サーバーが有効になります。

## 動作デモ

Claude に「`my-project` の直近1時間のログを表示して」と話しかけると、`show-log-viewer` ツールが呼び出され、チャット内にログビューアが表示されます。（機密情報のためマスクしていますが、実際にはログの具体的な内容も表示されます。）

![image.png](https://res.cloudinary.com/zenn/image/fetch/s--hwUY1FSi--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4054284/18f4a4a5-50c6-4845-a9bc-f7387053f888.png?_a=BACAGSGT)

### ログの表示内容

ログエントリは以下のような形式で表示されます：

```
2026/03/15 22:17:35  INFO  user@example.com | google.cloud.bigquery.v2.TableDataService.List | (bigquery.googleapis.com) → projects/my-project/datasets/my_dataset/tables/...
```

* **タイムスタンプ**: JST（日本標準時）固定
* **Severity**: INFO / NOTICE / WARNING / ERROR をカラーで区別
* **メッセージ**: 誰が（メール）、何をしたか（APIメソッド）、どのリソースに対して

### ログを選択して質問する

ログエントリをクリックすると選択状態になります（複数選択可）。

![image.png](https://res.cloudinary.com/zenn/image/fetch/s--THVIp3Yv--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4054284/892dc3a8-5f7b-4c17-a5f1-7a427604bfb0.png?_a=BACAGSGT)

選択したログの内容は自動的に Claude のコンテキストに送信されるので、そのままチャットで「選択したログについて教えて」と質問できます。

![image.png](https://res.cloudinary.com/zenn/image/fetch/s--YcBpknt_--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4054284/e983bf2c-81b8-495e-8c00-ac60ffb5bfed.png?_a=BACAGSGT)

> **注意**: ログの選択機能は実験的な実装であり、選択/解除の操作が正しく反映されない場合があります。

## 技術的な学び

### 1. `@google-cloud/logging` は protoPayload をデコードしない

Node.js の公式ライブラリは AuditLog の protoPayload を protobuf Buffer のまま返します。REST API を直接呼べば JSON でデコード済みのデータが取得できます。これは公式ドキュメントに明記されておらず、実装して初めてわかる落とし穴です。

### 2. MCP Apps の UI は単一 HTML にバンドルする必要がある

iframe の `srcdoc` で読み込まれるため、外部スクリプト参照（`<script src="...">`）は動作しません。`vite-plugin-singlefile` でインライン化が必須です。

### 3. `updateModelContext` は応答をトリガーしない

MCP Apps の `updateModelContext` は Claude のコンテキストを更新するだけで、Claude の応答を自動でトリガーする仕組みではありません。ユーザーがチャットで質問を入力する必要があります。

## まとめ

MCP Apps を使うことで、Claude のチャット画面に Cloud Logging のログビューアを埋め込み、GCP の「Gemini に質問」に近い体験を Claude で実現できました。

実装のポイントは以下の 3 つです：

1. **MCP Apps は `_meta.ui` を足すだけ** — 既存の MCP ツールに UI を追加するのは非常に簡単
2. **Cloud Logging は REST API を直接叩く** — Node.js ライブラリの protobuf 問題を回避
3. **`vite-plugin-singlefile` でインライン化** — iframe 制約への対応

MCP Apps はまだ新しい仕様ですが、クラウドリソースの可視化や運用ダッシュボードなど、DevOps 領域での活用可能性を感じています。

> **注意**: ソースコードは AI（Claude Code）による実装を多く含んでいます。特に認証周りやセキュリティ要件については、ご自身の環境に合わせて十分にご確認のうえご利用ください。

## 参考リンク
