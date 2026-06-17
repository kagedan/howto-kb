---
id: "2026-06-16-mcpサーバがfailed-to-connectしか言わない問題を診断するcliにした-01"
title: "MCPサーバが「failed to connect」しか言わない問題を、診断するCLIにした"
url: "https://zenn.dev/kensei0819/articles/mcp-doctor-diagnose-cli"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "zenn"]
date_published: "2026-06-16"
date_collected: "2026-06-17"
summary_by: "auto-rss"
query: ""
---

## MCPの追加は、いまだにコイン投げ

Claude Desktop や Cursor、Windsurf に MCP サーバを追加したとき、`failed to connect` とだけ出て黙り込まれた経験はないだろうか。

設定の何が悪いのか — コマンドのパスが違うのか、環境変数が足りないのか、そもそもサーバが起動直後にクラッシュしているのか — エラーは何も教えてくれない。結局、設定ファイルとにらめっこして30分溶かす。

毎回これをやっていたので、診断する CLI を書いた。`mcp-doctor` という。

## MCPの接続は「initialize ハンドシェイク」で決まる

MCP クライアントは、サーバプロセスを spawn して stdio 越しに JSON-RPC の `initialize` を投げ、レスポンスが返ってきて初めて「接続成功」とみなす。

つまり「接続できない」の裏には、だいたい次のどれかが隠れている。

* spawn するコマンド／パスが間違っている（`command not found`）
* 必要な環境変数が無く、サーバが起動直後に落ちる
* サーバは起動するが `initialize` を返す前にタイムアウト
* プロトコルバージョンの不一致

クライアントはこれを多くの場合「failed to connect」の一言に丸めてしまう。だから人間側で切り分けが要る。

## mcp-doctor がやること

設定を読んで、実際に各サーバを起動し、本物の `initialize` ハンドシェイクまで走らせて、どれがどう壊れているかを具体的に指し示す。

* Claude Desktop / Cursor / Windsurf / `.mcp.json` の設定を自動検出
* 各サーバを spawn して、実際の JSON-RPC `initialize` を実行（起動時クラッシュを捕まえる）
* 原因を特定：環境変数の欠落 / コマンド・パスの誤り / タイムアウト / プロトコル不一致

## 使い方

```
npx github:Isco0819/mcp-doctor
```

設定ファイルを探して、サーバを1つずつ叩いて、結果を並べてくれる。「接続できない」が「このサーバの、この環境変数が無い」まで分解される。

## 作ってみて

ハンドシェイクを自分で実装してみると、「failed to connect」がいかに情報を捨てているかがよく分かった。エラーメッセージは、握りつぶした瞬間に価値を失う。診断とは、捨てられた情報を拾い直す作業なのだと思う。

フィードバックや「こういう設定で詰まった」報告は歓迎です。
