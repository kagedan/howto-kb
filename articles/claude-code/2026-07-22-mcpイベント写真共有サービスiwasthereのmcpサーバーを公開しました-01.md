---
id: "2026-07-22-mcpイベント写真共有サービスiwasthereのmcpサーバーを公開しました-01"
title: "【MCP】イベント写真共有サービス「iwasthere」のMCPサーバーを公開しました"
url: "https://qiita.com/yanso/items/81c1fba3c35da44aeba0"
source: "qiita"
category: "claude-code"
tags: ["MCP", "API", "qiita"]
date_published: "2026-07-22"
date_collected: "2026-07-23"
summary_by: "auto-rss"
query: ""
---

## はじめに

ランニング大会、クロスフィット大会、勉強会などのイベント集合写真の中から、**セルフィーだけで自分の写真を顔認識で見つけてダウンロードできる**サービス [iwasthere.pics](https://iwasthere.pics) を運営しています。

今回、このサービスのAPIをAIエージェントから自然言語で操作できる **MCPサーバー** を公開しました。

🎉 **現在、有料化前のため全機能を無料で公開中です！**

## iwasthere とは

https://iwasthere.pics

イベント写真の「あの写真どこ？」問題を解決するサービスです。

- 📷 イベント主催者が写真をアップロードしてリンクを共有
- 🔗 参加者はリンクからアクセス（**会員登録不要**）
- 🤳 セルフィーを撮るだけでAIが顔認識で自分の写真を検索
- 📥 ダウンロード・シェア可能

## MCP サーバーでできること

Claude、Cursor などMCP対応のAIツールからアワデAPIを**自然言語で**使えます。

### 提供ツール

ドキュメント検索ツールと主催者アクションツールを提供します。

| カテゴリ | ツール名 | 説明 |
|----------|----------|------|
| ドキュメント | `search_docs` | サービスドキュメントを検索 |
| ドキュメント | `get_page` | 指定ページの内容を取得 |
| イベント管理 | `create_event` | 新規イベントを作成 |
| イベント管理 | `list_events` | イベント一覧を取得 |
| イベント管理 | `get_event` | イベント詳細を取得 |
| イベント管理 | `get_event_status` | 状態＋インデックス進捗を確認 |
| イベント管理 | `patch_event` | イベント情報を更新 |
| イベント管理 | `delete_event` | イベントを削除 |
| 写真 | `upload_photo` | Presigned URLを発行（アップロード用） |
| 写真 | `complete_upload` | アップロード完了→インデックス開始 |
| 写真 | `get_indexing_status` | インデックスの進捗確認 |
| 共有 | `get_share_link` | 参加者向け共有リンクを取得 |
| プラン | `get_plan_and_limits` | 現在のプラン・残り枠を確認 |

:::message
**顔検索ツールは含まれません**（恒久的な非公開原則）。
顔認識による写真検索は、参加者がブラウザ上で直接行う機能です。
:::

## セットアップ

### 1. APIキーの発行

ログイン後、開発者ページでキーを発行します。発行時に原文は**1回だけ**表示されます。

👉 https://iwasthere.pics/dashboard/developer

### 2. MCPクライアント設定

MCPクライアント設定に以下を追加し、発行したAPIキーを入れてください：

```json
{
  "mcpServers": {
    "iwasthere": {
      "url": "https://7y62bns2zdo3xfpm6azyelalxq0gbelo.lambda-url.ap-northeast-2.on.aws/",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

**Claude Desktop**: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)
**Cursor**: `.cursor/mcp.json`
**Windsurf**: MCP設定ファイルに同様に追加

:::message alert
Remote MCPサーバー（URL方式）なので、`command` / `args` ではなく `url` / `headers` を使います。
npxインストールは不要です。
:::

## シナリオ例

ユーザーが自然言語で依頼すると、エージェントがツールを連携呼び出しします。

### 例1: イベント作成→共有リンク取得

```
あなた: 7月のワークショップイベントを作って共有リンクを教えて

Claude: イベントを作成しました。
  📎 共有リンク: https://iwasthere.pics/e/abc123
  参加者にこのリンクを送ると、セルフィーで写真検索できます。
```

内部では `create_event` → `get_share_link` が呼ばれます。

### 例2: 写真アップロード

```
あなた: この写真をイベントにアップして

Claude: アップロード完了しました。顔インデックスを開始します。
  進捗: 3/3枚 処理完了 ✅
```

内部フロー:
1. `upload_photo` → presigned URL + contentType を取得
2. HTTP PUT で画像をアップロード（Content-Typeヘッダ一致必須）
3. `complete_upload` → インデックス開始
4. `get_event_status` → 進捗確認

### 例3: プラン確認

```
あなた: 今月あと何個イベントを作れる？

Claude: 現在 Euro プランで、アクティブイベント 2/10 個です。
  あと8個作成可能です。
```

## 技術的な詳細

### アーキテクチャ

```
┌─────────────────┐                        ┌──────────────────┐
│  Claude Desktop │                        │  iwasthere MCP   │
│  Cursor         │ ── Streamable HTTP ──► │  Server (Lambda) │
│  Windsurf       │                        │  ap-northeast-2  │
└─────────────────┘                        └────────┬─────────┘
                                                    │
                                                    │ Internal API
                                                    ▼
                                           ┌──────────────────┐
                                           │  iwasthere.pics  │
                                           │  Backend          │
                                           └──────────────────┘
```

- **ホスティング**: AWS Lambda (ap-northeast-2 / ソウルリージョン)
- **Transport**: Streamable HTTP（Remote MCP Server）
- **認証**: API Key（Authorizationヘッダ）
- **プロトコル**: MCP 2025-03-26+

### なぜ Remote MCP にしたか

- ユーザー側にnpxインストール不要
- URLとAPIキーだけで即接続
- サーバーサイドでバージョン管理可能
- Lambda で自動スケーリング

## 料金

🎉 **現在、有料プラン実装前のため全機能を無料で公開中です！**

有料化は今後実装予定です。それまでは MCP を含むすべての機能を無料でお試しいただけます。

## 関連記事

MCPサーバーの開発背景やiwasthereのMVP開発プロセスについて、詳しくはこちらのブログ記事をご覧ください：

👉 [How I Built iwasthere MVP with Kiro Workflow](https://yanlog.yanbert.com/en/blog/how-i-built-iwasthere-mvp-with-kiro-workflow-20260630/)

## まとめ

MCPエコシステムに**イベント写真管理**というカテゴリのサーバーを追加しました。

主催者であれば：
- イベント作成 → 写真アップロード → 共有リンク発行

この一連の流れをAIに自然言語で依頼するだけで完結します。

ぜひ試してみてください：

🌐 **サービス**: https://iwasthere.pics
📖 **MCPドキュメント**: https://iwasthere.pics/ja/docs/mcp
📝 **開発ブログ**: https://yanlog.yanbert.com/en/blog/how-i-built-iwasthere-mvp-with-kiro-workflow-20260630/
🎉 **全機能無料公開中**（有料化前）

---

この記事が役に立ったら、いいね（❤️）お願いします！
質問やフィードバックはコメント欄までお気軽にどうぞ。
