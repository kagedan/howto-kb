---
id: "2026-04-09-claude-code同士を会話させるmcpサーバーcc-to-ccを作ってみた-01"
title: "Claude Code同士を会話させるMCPサーバー「cc-to-cc」を作ってみた"
url: "https://zenn.dev/yukitakeshita/articles/8bd5f02bc59201"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "zenn"]
date_published: "2026-04-09"
date_collected: "2026-04-10"
summary_by: "auto-rss"
query: ""
---

## 作った背景

最近、Claude Code を使って複数プロジェクトを並行開発していると、ある不満が。

**「こっちのプロジェクトの Claude Code に、あっちのプロジェクトのことを聞きたい」**

たとえば、フロントエンドのプロジェクトで作業中に「バックエンド API のエンドポイント仕様ってどうなってたっけ？」と思ったとき。今までは自分がターミナルを切り替えて、もう片方の Claude Code に聞いて、その回答をコピペして…という人間メッセンジャー状態でした。

Claude Code には Agent teams という実験機能がありますが、これは「最初から1つのリードセッションがチームを作る」前提の仕組みです。**すでに別々のプロジェクトで独立起動している Claude Code 同士を、あとから自由につないで会話させる**公式機能は、調べた限り見つかりませんでした。

GitHub の issue を見ると、同じことを求めている人が複数いました。

「ないなら作るか」ということで、**cc-to-cc** を作りました。

<https://github.com/takeshita-0x0201/cc-to-cc>

## cc-to-cc とは

**異なるプロジェクトで動いている Claude Code セッション同士が、メッセージを送受信できる MCP サーバー**です。

仕組みはシンプルで、共有ディレクトリ（`~/.cc-to-cc/`）に JSON ファイルを置くだけ。各 Claude Code に MCP ツールとして `send` や `inbox` を生やして、ファイルの読み書きをラップしています。

```
プロジェクト A                          プロジェクト B
─────────────                          ─────────────
Claude Code                            Claude Code
  │                                      │
  └─ send("api-server", ...)            watch("api-server")  ← 待機中
       │                                      ▲
       ├─ 1. JSON を inbox に書き込み         │
       │                                      │
       └─ 2. HTTP POST ─────────────────────┘
              (webhook通知)                   │
                                        3. watch が即座に返る
                                        4. Claude Code が内容を読んで反応
```

ポイントは以下です。

* **中央サーバー不要**: ファイルシステムだけで完結
* **リアルタイム通知**: 各セッションがローカル HTTP webhook を持ち、`send` すると相手の `watch` が即座に起きる
* **オフライン対応**: 相手がオフラインでもメッセージは inbox に保存される
* **プロジェクト数無制限**: 2つでも10でも同じ仕組み

## セットアップ

### 1. クローンとビルド

```
git clone https://github.com/takeshita-0x0201/cc-to-cc.git
cd cc-to-cc
npm install
npm run build
```

### 2. 各プロジェクトの `.claude/settings.json` に追加

```
{
  "mcpServers": {
    "cc-to-cc": {
      "command": "node",
      "args": ["/path/to/cc-to-cc/dist/index.js"]
    }
  }
}
```

### 3. 各セッションでプロジェクトを登録

```
このプロジェクトを "frontend" として登録して
```

これだけです。

## ツール一覧

| ツール | やること |
| --- | --- |
| `register` | プロジェクトを登録。webhook リスナー起動。 |
| `list_peers` | 登録済みプロジェクト一覧。 |
| `send` | メッセージ送信。リアルタイム通知付き。 |
| `inbox` | 未読メッセージ確認。 |
| `watch` | 新着メッセージをリアルタイム待機。 |
| `ack` | 既読にする（直接アーカイブも可）。 |
| `archive` | 既読メッセージをアーカイブ。 |
| `history` | 過去メッセージ閲覧。 |

## 使ってみる

### ターミナル1：API サーバープロジェクト（受信側）

```
> 受信メッセージを待って

→ watch("api-server") を実行... 待機中...
```

### ターミナル2：フロントエンドプロジェクト（送信側）

```
> api-server に「/api/users のレスポンス形式を教えて」と聞いて

→ send(to: "api-server", ...) を実行
→ 「メッセージ送信完了。配信: リアルタイム通知済み。」
```

### ターミナル1に戻ると…

```
→ 「新着メッセージ受信！
   送信元: frontend
   件名: /api/users response format
   ...」

→ Claude Code が自分のコードベースを調べて返信を作成
→ send(to: "frontend", ...) で返信
```

**人間が介在せずに、Claude Code 同士がプロジェクトをまたいで会話している**状態です。

## メッセージのライフサイクル

受信箱が肥大化しないように、3段階のライフサイクルを設けています。

```
inbox/new/  →  inbox/cur/  →  inbox/archive/
  (未読)        (既読)         (処理済み)
```

* `ack` で既読にする（`archive: true` オプションで直接アーカイブも可）
* `archive` で既読メッセージを一括・スレッド単位・個別にアーカイブ
* `history` はデフォルトで既読のみ表示、`includeArchived: true` でアーカイブも検索可能

## リアルタイム通知の仕組み

「ファイルベースなのにリアルタイム？」と思うかもしれません。

各 MCP サーバーは `register` 時にローカルの HTTP サーバーをランダムポートで起動します。ポート番号はレジストリ（`~/.cc-to-cc/registry.json`）に保存されます。

```
{
  "api-server": {
    "id": "api-server",
    "path": "/Users/you/projects/api-server",
    "webhookPort": 54321
  }
}
```

`send` ツールが呼ばれると：

1. 相手の `inbox/new/` に JSON ファイルを書き込み
2. レジストリから相手の webhook ポートを取得
3. `http://127.0.0.1:54321/notify` に POST

受信側の MCP サーバーは POST を受け取ると、待機中の `watch` ツールを即座に resolve します。これにより、**ファイルベースの永続性と HTTP の即時性を両立**しています。

webhook が到達できない場合（相手がオフライン）でも、ファイルは inbox に残っているので、次回 `inbox` で読めます。

## 技術スタック

* **TypeScript** + Node.js
* **@modelcontextprotocol/sdk** v1.29.0（MCP サーバー実装）
* **stdio transport**（Claude Code ↔ MCP サーバー間）
* **node:http**（webhook 通知）
* **node:fs**（メッセージ永続化）

外部依存は MCP SDK のみ。シンプルに保っています。

## メッセージ形式

```
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "from": "frontend",
  "to": "api-server",
  "subject": "API endpoint list request",
  "body": "Please check and send me the current API endpoint list for /api/users.",
  "threadId": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "timestamp": "2026-04-09T12:00:00.000Z"
}
```

`threadId` で会話のスレッドを追跡できます。返信時に同じ `threadId` を使えば、一連のやり取りとして `history` で辿れます。

## 現在の制限と今後

### 現在の制限

* **同一マシン限定**: ファイルシステム共有が前提なので、リモートマシン間の通信は未対応
* **手動 watch**: 受信側が `watch` を呼ばないとリアルタイム受信できない（MCP の制約上、サーバーから Claude Code への自発的な push は困難）
* **認証なし**: ローカル利用前提なのでアクセス制御はなし

### 今後やりたいこと

* Claude Code の **Channels** 機能（実験中）との統合で、真のリアルタイム push
* **ブロードキャスト**（全プロジェクトへの一斉送信）
* **共有 scratchpad**（プロジェクト横断の状態共有メモ）
* **Agent SDK** との統合で、中央ブローカーが複数セッションをオーケストレーション

## まとめ

Claude Code のセッションはデフォルトで完全にサイロ化されています。公式の Agent teams は「最初からチームとして作る」前提で、**既存の独立セッション同士を後から自由に接続する**手段は今のところありません。

cc-to-cc は、その隙間を「ファイルベース mailbox + ローカル HTTP webhook」というシンプルな構成で埋めます。200行程度の MCP サーバーで、プロジェクト横断の Claude Code 間通信が実現できました。

同じ不満を持っている方がいたら、ぜひ使ってみてください。

<https://github.com/takeshita-0x0201/cc-to-cc>
