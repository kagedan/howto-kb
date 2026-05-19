---
id: "2026-05-18-1password-cliを使ってmcpサーバーにapiキーを渡す-01"
title: "1Password CLIを使ってMCPサーバーにAPIキーを渡す"
url: "https://zenn.dev/tknhs/articles/ea24de4f89cad7"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "API", "zenn"]
date_published: "2026-05-18"
date_collected: "2026-05-19"
summary_by: "auto-rss"
query: ""
---

MCPサーバーの設定にAPIキーを直書きしたくないので、1Password CLIを使って解消する。  
実現方法は付録。現時点でイマイチなことを書きたかった。

## 注意点：起動のたびに認証を求められる

* `op run` は実行のたびに1Passwordに接続するため、MCPサーバーが複数あると、Claude起動時にその数だけ認証ダイアログが表示される。
* 事前に `op signin` でセッションを取得しておくと、その間だけは認証をスキップ可能だが、セッションの有効期限が切れると再び認証が必要になるため、いまいち。

```
eval $(op signin)
# → この後 Claude を起動すると認証なしで全サーバーが立ち上がる
```

## 実現方法

`op run` コマンドで MCP サーバーの起動コマンドをラップする。

## 手順

### 1. `~/.env.op` にシークレット参照を書く

~/.op/.env.op

```
CONTEXT7_API_KEY="op://Employee/context7/credential"
```

* `op://` の形式は `op://[Vault名]/[アイテム名 or UUID]/[フィールド名]`。
* 1Password アプリでアイテムを右クリック →「シークレット参照をコピー」で取得。

### 2. MCP の設定ファイルを書き換える

* `command` を `op` にして、`op run --env-file=... -- <元のコマンド>` の形にする。

**変更前（API キーの直書き）**

```
"context7": {
  "command": "npx",
  "args": ["-y", "@upstash/context7-mcp", "--transport", "stdio", "--api-key", "ctx7_xxxxxxxxxx"]
}
```

**変更後（1Password 経由）**

```
"context7": {
  "command": "op",
  "args": [
    "run",
    "--env-file=~/.op/.env.op",
    "--",
    "sh", "-c",
    "npx -y @upstash/context7-mcp --transport stdio --api-key $CONTEXT7_API_KEY"
  ]
}
```

**動作の仕組み**

```
Claude 起動
  └─ op run が ~/.env.op を読み込む
       └─ op:// 参照を 1Password から解決して環境変数にセット
            └─ MCP サーバーが $CONTEXT7_API_KEY を受け取って起動
```
