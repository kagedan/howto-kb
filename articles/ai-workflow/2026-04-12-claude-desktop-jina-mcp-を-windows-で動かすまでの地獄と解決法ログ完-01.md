---
id: "2026-04-12-claude-desktop-jina-mcp-を-windows-で動かすまでの地獄と解決法ログ完-01"
title: "Claude Desktop × Jina MCP を Windows で動かすまでの地獄と解決法（ログ完全公開）"
url: "https://zenn.dev/ikahan/articles/a723fd0e084a70"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "API", "zenn"]
date_published: "2026-04-12"
date_collected: "2026-04-13"
summary_by: "auto-rss"
query: ""
---

## 対象読者

* Claude Desktop の MCP を使いたい人
* Jina MCP (API) を導入したい人
* runningにならなくて詰んでいる人

---

# 結論（これで動く）

```
{
  "mcpServers": {
    "jina-mcp-server": {
      "command": "C:\\Program Files\\nodejs\\node.exe",
      "args": [
        "C:\\Program Files\\nodejs\\node_modules\\npm\\bin\\npx-cli.js",
        "-y",
        "mcp-remote",
        "https://mcp.jina.ai/v1",
        "--header",
        "Authorization: Bearer YOUR_API_KEY"
      ]
    }
  }
}
```

---

# やりたかったこと

Claude Desktop に Jina MCP を接続して

を使えるようにする

---

# 詰まったポイント

## ① JSON構文エラー

```
Error reading or parsing config file:
SyntaxError: Unexpected token
```

```
Expected ',' or ']' after array element in JSON
```

### 原因

---

## ② node.exe に -y 渡して死亡

```
C:\Program Files\nodejs\node.exe: bad option: -y
```

### 原因

```
"command": "node.exe",
"args": ["-y", ...]
```

👉 `-y` は npx 用  
👉 node に渡すと落ちる

---

## ③ Windows最大の罠

```
'C:\Program' は、内部コマンドまたは外部コマンド、
操作可能なプログラムまたはバッチ ファイルとして認識されていません。
```

### 原因

```
C:\Program Files\nodejs\npx.cmd
```

👉 空白で分割される

---

## ④ EPIPE（意味不明エラー）

```
Error: write EPIPE
Server transport closed unexpectedly
```

### 原因

👉 上記エラーの結果

---

# 実際に試したコマンド（重要）

## npx が使えるか確認

→ 何も出ない（罠）

---

## 正しい確認方法 wtかcmd

```
C:\Program Files\nodejs\npx
C:\Program Files\nodejs\npx.cmd
```

👉 PATH は通っている

---

## Node の存在確認

```
Test-Path "C:\Program Files\nodejs\node.exe"
Test-Path "C:\Program Files\nodejs\npx.cmd"
```

👉 True ならOK

---

## 実際に動くか確認

```
npx -y mcp-remote https://mcp.jina.ai/v1 --header "Authorization: Bearer YOUR_API_KEY"
```

```
Connected to remote server
Proxy established successfully
```

👉 ここで成功するならJina側は問題ない

---

# 私の環境でNGだったjson記述パターン集

## ❌ npx直接

👉 Claude環境だと不安定

---

## ❌ node直接

👉 -yで死ぬ

---

## ❌ npx.cmd直接

```
"command": "C:\\Program Files\\nodejs\\npx.cmd"
```

👉 空白で死ぬ

---

# 正解の組み合わせ

---

## なぜこれで動くか

```
node.exe npx-cli.js -y mcp-remote ...
```

になるため

* node → スクリプト実行
* npx → 正しく動作

👉 役割が分離される

---

# 最終ログ（成功例）

```
tool_search 成功（21ツール検出）
read_url 成功
https://jina.ai 取得成功
```

---

# 使えるツール一覧（一部）

* read\_url
* search\_web
* search\_arxiv
* extract\_pdf
* search\_images
* parallel\_read\_url

---

# 本質的な問題

今回の詰まりは3層

## ① JSON

## ② Windows

## ③ Node

---

# まとめ

![](https://static.zenn.studio/user-upload/b4a1d8f847c3-20260413.png)

> [!IMPORTANT]  
> 本記事では以下のパスを例にしていますが、環境によって異なります
>
> * Node.js のインストール場所は環境依存
> * nvm-windows を使っている場合はパスが異なる
>
> 必要に応じて以下を実行して確認してください
>
> ```
> where.exe node
> where.exe npx
> ```

```
npx直接は使うな
node + npx-cli.jsを使え
```

これだけ覚えておけばOK.

LLM参考文献:  
<https://github.com/jina-ai/MCP>  
<https://www.augmentcode.com/mcp/reader?utm_source=chatgpt.com>  
<https://github.com/anthropics/claude-code/issues/2682?utm_source=chatgpt.com>  
<https://github.com/anthropics/claude-code/issues/42323?utm_source=chatgpt.com>  
<https://jina.ai/ja/news/agentic-workflow-with-jina-remote-mcp-server/?utm_source=chatgpt.com>  
<https://github.com/kealuya/mcp-jina-ai?utm_source=chatgpt.com>
