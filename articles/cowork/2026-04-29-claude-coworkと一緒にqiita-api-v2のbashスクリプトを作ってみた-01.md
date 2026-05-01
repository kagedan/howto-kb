---
id: "2026-04-29-claude-coworkと一緒にqiita-api-v2のbashスクリプトを作ってみた-01"
title: "Claude Coworkと一緒にQiita API v2のBashスクリプトを作ってみた"
url: "https://qiita.com/stephen_appy/items/8bcaf76f414581614737"
source: "qiita"
category: "cowork"
tags: ["API", "qiita"]
date_published: "2026-04-29"
date_collected: "2026-05-01"
summary_by: "auto-rss"
---

## はじめに

Claude Coworkは、Claudeに自然言語で指示を出すとファイル操作やコード生成などを実行してくれるデスクトップツールです。今回は「Qiita API v2を叩けるBashスクリプトを作る」というタスクをClaude Coworkに任せてみました。

単にコードを生成してもらうだけでなく、**設計の相談 → 計画の提示・修正 → 実装 → 検証**という一連のプロセスをClaude Coworkと協力して進めています。



---

## 事前準備：外部通信の許可設定

Claude Coworkのサンドボックス環境はデフォルトでは外部通信が「パッケージマネージャーのみ」に制限されています。Qiita APIを実行するには、この設定を変更する必要があります。

**設定 → ネットワーク外部通信を許可** から設定を変更してください。

> **⚠️ 注意（執筆時点での状況）**
> 「追加の許可ドメイン」に `qiita.com` および `*.qiita.com` を追加する方法、**「すべて許可」** に変更する方法のいずれも試みましたが、設定が反映されませんでした。最終的に `qiita.com` / `*.qiita.com` を追加した状態に戻したうえでアプリを再インストールしたところ、問題が解消されました。同様の事象が発生した場合は、再インストールをお試しください。

---

## 参照したドキュメント

スクリプトは以下の公式ドキュメント・スキーマをもとに作成しています。

- [Qiita API v2ドキュメント](https://qiita.com/api/v2/docs)
- [JSON Schema](https://qiita.com/api/v2/schema)
- [JSON Schema（日本語）](https://qiita.com/api/v2/schema?locale=ja)

---

## 作ったもの

Qiita API v2の各エンドポイントをBashスクリプトから呼び出せるライブラリ群です。

### ファイル構成

```
QuiitaAPI/
├── config.sh          # APIトークン設定
└── lib/
    ├── common.sh      # 共通関数（curl・エラー処理・jq整形）
    ├── items.sh       # 記事 API（11関数）
    ├── comments.sh    # コメント API（4関数）
    ├── tags.sh        # タグ API（5関数）
    └── users.sh       # ユーザー API（7関数）
```

---

## 設計のポイント

### Claude Coworkから呼び出すことを前提にした設計

一般的なCLIツールとは異なり、**ClaudeがAPIを呼び出すための道具**として設計しています。「記事を検索して」「自分の記事一覧を出して」といった自然言語の指示をClaude Coworkに出すと、Claudeが適切な関数を選んでBashで実行します。

### 削除系APIは実装しない

誤操作のリスクを避けるため、DELETE系のAPIは意図的に除外しています。

### 共通関数で統一的なエラーハンドリング

`common.sh` にHTTPステータスコードの処理をまとめ、2xx系は整形済みJSON、4xx/5xx系はエラーメッセージを返します。`jq` がインストールされていれば自動で整形されます。

---

## セットアップ

### 1. 個人用アクセストークンを取得

Qiita設定 → アプリケーション → 個人用アクセストークン から発行します。

### 2. config.sh にトークンを設定

```bash
QIITA_TOKEN="your_token_here"
```

今回はClaude Coworkからローカルで実行することを前提としているため、トークンは `config.sh` に直接記載する方式を採用しています。GitHubなどのリモートリポジトリに公開する場合は、`config.sh` を `.gitignore` に追加するか、環境変数での管理をお勧めします。

---

## 使い方のイメージ

Claude Coworkに以下のように指示するだけでAPIが実行されます。

```
「bashタグの記事を20件取得して」
→ list_tag_items "bash" 1 20 を実行

「タイトル『テスト投稿』で限定共有記事を作成して」
→ create_item "テスト投稿" "..." '[{"name":"test"}]' true を実行
```

---

## 実装した関数一覧

### items.sh（記事）

| 関数名 | 説明 |
|--------|------|
| `list_items` | 記事一覧・検索 |
| `get_item` | 記事取得 |
| `create_item` | 記事作成 |
| `update_item` | 記事更新 |
| `list_authenticated_user_items` | 自分の記事一覧 |
| `stock_item` | ストック |
| `get_item_stock` | ストック確認 |
| `list_item_stockers` | ストックユーザー一覧 |
| `list_tag_items` | タグの記事一覧 |
| `list_user_items` | ユーザーの記事一覧 |
| `list_user_stocks` | ユーザーのストック一覧 |

### comments.sh（コメント）

| 関数名 | 説明 |
|--------|------|
| `get_comment` | コメント取得 |
| `update_comment` | コメント更新 |
| `list_item_comments` | 記事のコメント一覧 |
| `create_item_comment` | コメント作成 |

### tags.sh（タグ）

| 関数名 | 説明 |
|--------|------|
| `list_tags` | タグ一覧 |
| `get_tag` | タグ取得 |
| `get_tag_following` | フォロー確認 |
| `follow_tag` | タグフォロー |
| `list_user_following_tags` | フォロー中タグ一覧 |

### users.sh（ユーザー）

| 関数名 | 説明 |
|--------|------|
| `get_authenticated_user` | 自分の情報取得 |
| `list_users` | ユーザー一覧 |
| `get_user` | ユーザー取得 |
| `list_user_followees` | フォロー中一覧 |
| `list_user_followers` | フォロワー一覧 |
| `get_user_following` | フォロー確認 |
| `follow_user` | フォロー |

---

## おわりに

Claude Coworkとのやり取りでよかった点は、**計画段階でフィードバックを反映しやすい**ことです。最初の計画にはTeam用APIや削除系APIも含まれていましたが、「削除系は不要」「Teamトークンは持っていない」と伝えるだけでスコープを絞り込んでもらえました。

コードを書くだけでなく、設計の相談相手としても活用できるのがClaude Coworkの面白いところだと感じました。

---

## 参考

- Claude CoworkとQiitaを連携する方法【全オプション解説】
https://qiita.com/MidRiver/items/b8e3c979f3f66bfa6291
