---
id: "2026-04-04-aiエージェント-zeroclaw-のmcp設定-01"
title: "AIエージェント ZeroClaw のMCP設定"
url: "https://zenn.dev/mizugeeks/articles/30d0878e44a233"
source: "zenn"
category: "antigravity"
tags: ["MCP", "antigravity", "zenn"]
date_published: "2026-04-04"
date_collected: "2026-04-05"
summary_by: "auto-rss"
---

## はじめに

OpenClaw系のAIエージェント「ZeroClaw」を利用し始めたのですがセキュリティ制限が厳しく、コマンドの実行にかなり制限があります。特定のコマンド実行を許可しても、コマンドが作成するテンポラリファイルの場所も制限対象になるので使えないことがほとんどです。

そこでMCPを使おうとしたのですが ZeroClawに関する情報が非常に乏しく、検索しても具体的な方法が出てきません。  
ZeroClawのソースを Google Antigravity に読み込ませ解析させ、試行錯誤してようやくMCPを利用することができるようになったので、メモとして残しておきます。

## 利用環境

今回、MCPサーバーとして [Composio](https://composio.dev/) を利用することにしました。  
無料の「Total Free」プランで 20000回/月のツール呼び出しが可能なこと、非常に多くのネット上のサービスに対応していること、ユーザーホーム画面でアクセスのログが確認できることが採用した主な理由です。

LLMには [さくらのAI Engine](https://www.sakura.ad.jp/aipf/ai-engine/)で Qwen3-Coder-30B-A3B-Instruct を利用しています。AIエージェントとして動かすには最低これぐらいの大きさのモデルが必要なようです。(小さいモデルだとハルシネーションを起こして誤動作します)

## MCPサーバーの準備と設定

まず、Composio で利用したいサービスを有効に(Connect)します。私はGmailとGoogle Calendarを有効にしました。  
次に Composio のユーザーホーム画面で MCPサーバーのURLと x-consumer-api-key をコピーします。  
![Composio MCP configuration](https://static.zenn.studio/user-upload/5ed401cdb0da-20260404.png)

ZeroClawの初期設定が終わった状態で、設定ファイル ~/.zeroclaw/config.toml のMCP設定をテキストエディタを使って変更します。  
[mcp] から servers の行を削除し、[[mcp.servers]] を追加して設定を書きます。  
headersのx-consumer-api-key に先にコピーしたAPIキーを入れてください。

config.toml

```
[mcp]
enabled = true
deferred_loading = true

[[mcp.servers]]
name = "composio"
transport = "http"
url = "https://connect.composio.dev/mcp"
headers = { "x-consumer-api-key" = "ck_OXXXXXXXXXX" }
```

設定を書き換え、zeroclaw を再起動させるとMCPが利用できるようになります。

## トラブルシューティング

### MCPツールが使えないと言ってきた場合

最初にGmailでメール検索を実行したときMCPが使えないというメッセージを返してきました。

> 申し訳ありませんが、現在の環境ではMCPツールやComposioの使用が制限されており、Gmailの未読タイトル一覧を取得することができません。セキュリティポリシーにより、これらのツールの実行が許可されていません。

これは過去の記憶を引きずっているだけなので、次のように伝えるとMCPアクセスをしてくれるようになります。

> 設定ファイルを修正し、セキュリティ制限も解除してツールが利用可能になりました。改めて自分自身に読み込まれているツール（COMPOSIO\_SEARCH\_TOOLS 等）を確認し、Gmailの未読タイトル一覧を取得してください

### 表示される結果がおかしい場合

Gmailで検索をさせたとき、不完全な結果を返してきました。  
メールの件名が「不明」と返ってくるのです。

> 現在の未読メールは以下の通りです：
>
> 1. プロモーション - メールの件名が不明（メッセージID: 19d56091d396e）
> 2. プロモーション - メールの件名が不明（メッセージID: 19d560177b657）
> 3. プロモーション - メールの件名が不明（メッセージID: 19d56000a1b23）
>
> 現在の実装では、メールの件名を取得するためにさらに詳細な情報を取得する必要がありますが、これ以上詳細な情報を取得するには追加のAPI呼び出しが必要になります。上記の結果は、メールのラベルとIDのみを取得したものです。
>
> メールの件名を完全に取得するには、各メールの詳細情報を取得するための追加のAPI呼び出しが必要になります。

これはLLMがMCPで取得したデータを正しく読めていないだけなので下記のように伝えると件名も正しく表示してくれるようになりました。

> 取得できたメールについて、GMAIL\_FETCH\_MESSAGE\_BY\_MESSAGE\_ID などのツールを使って詳細データを取得し、『payload.headers』の配列の中から name が 'Subject' になっている項目の value を取り出して、件名として一覧表示してください。

以上。
