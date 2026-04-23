---
id: "2026-03-31-claude-desktop-がwe-are-so-sorryで起動しない原因は-mcp-の-url-01"
title: "Claude Desktop が「We are so sorry」で起動しない。原因は MCP の `url` 設定だった"
url: "https://qiita.com/noujiru/items/0fb7ba6857c19d47800f"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "qiita"]
date_published: "2026-03-31"
date_collected: "2026-03-31"
summary_by: "auto-rss"
---

Claude Desktop が突然 `We are so sorry` で落ちて、まったく起動しなくなった。  
再インストールやキャッシュ削除でも直らず、原因は `claude_desktop_config.json` に入っていた MCP の `"url"` 設定だった。  
この記事では、落ちた理由・直し方・GitHub MCP でハマりやすい設定まで、最短で復旧できる形でまとめる。

## 先に結論

* Claude Desktop で `mcpServers.*.url` を使うと、今回のように起動時クラッシュになることがある
* 修正は `mcp-remote` を使った `command + args` 形式への置き換えでOK
* GitHub MCP だけは URL ではなく `@modelcontextprotocol/server-github` を直接実行する

## まず起きていた症状

Claude Desktop を起動すると毎回このダイアログが出て使えなくなった。

```
We are so sorry, Claude Desktop failed to launch.
Please check the logs for more information.
```

再インストール・キャッシュ削除・plist 削除…何をしても再現。

## 原因は `claude_desktop_config.json` の `url` 設定だった

`claude_desktop_config.json` に **`"url": "..."` 形式の MCP 設定** が入っていたのが犯人だった。

```
// ❌ Claude Desktop では動かない
{
  "mcpServers": {
    "supabase": {
      "url": "https://mcp.supabase.com/mcp"
    },
    "notion": {
      "url": "https://mcp.notion.com/mcp"
    }
  }
}
```

ログ（`~/Library/Logs/Claude/main.log`）を見ると：

```
TypeError: Cannot read properties of undefined (reading 'value')
    at i._splat (...)
```

`url` フィールドを内部でパースしようとした際に `undefined.value` にアクセスしてクラッシュしている。

## なぜハマるのか: CLI では動いて Desktop では落ちる

ここがややこしいポイントで、手元では CLI 側では動く設定が Claude Desktop ではそのまま使えなかった。

| 環境 | `url` 形式 | `command + args` 形式 |
| --- | --- | --- |
| Claude Code CLI | 手元では動作 | 動作 |
| Claude Desktop | 今回はクラッシュ | 動作 |
| Codex CLI | 手元では動作 | 動作 |

同じ MCP 設定でも実行環境で挙動が変わるので、Desktop だけ落ちるときはまずここを疑うのが早い。

## 直し方: `mcp-remote` 経由の `command + args` に置き換える

`npx mcp-remote <URL>` を使えば Claude Desktop でもリモート MCP サーバーに接続できる。

```
// ✅ Claude Desktop でも動く
{
  "mcpServers": {
    "supabase": {
      "command": "/path/to/npx",
      "args": ["-y", "mcp-remote", "https://mcp.supabase.com/mcp"]
    },
    "notion": {
      "command": "/path/to/npx",
      "args": ["-y", "mcp-remote", "https://mcp.notion.com/mcp"]
    },
    "playwright": {
      "command": "/path/to/npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

npx のフルパスは `which npx` で確認。nvm 使いは以下のようになる場合が多い：

```
/Users/yourname/.nvm/versions/node/v24.13.0/bin/npx
```

## GitHub MCP は URL ではなく npm パッケージを使う

ここも最初ちょっと迷いやすいポイントで、GitHub MCP は URL 型のリモートサーバーではなく npm パッケージを直接実行する。

```
// ❌ よくある間違い（GitHub のリポジトリ URL を指定してしまう）
{
  "github": {
    "command": "npx",
    "args": ["-y", "mcp-remote", "https://github.com/modelcontextprotocol/servers"]
  }
}

// ✅ 正しい設定
{
  "github": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": {
      "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"
    }
  }
}
```

## 切り分けは最小構成から 1 件ずつ足すのが最短

「どの MCP が悪いか」を特定するときは最小設定からひとつずつ追加していくのが確実。

```
// Step 1: ここから起動確認
{ "mcpServers": {} }

// Step 2: preferences を追加して確認
{ "mcpServers": {}, "preferences": { "coworkWebSearchEnabled": true } }

// Step 3: MCP を 1 件ずつ追加して原因を特定
{
  "mcpServers": {
    "supabase": {
      "command": "/path/to/npx",
      "args": ["-y", "mcp-remote", "https://mcp.supabase.com/mcp"]
    }
  }
}
```

## まとめ

やることだけ並べるとこんな感じ。

1. `claude_desktop_config.json` に `"url": "..."` 形式の MCP 設定がないか確認する
2. 見つかったら `mcp-remote` を使った `command + args` 形式に置き換える
3. GitHub MCP はリポジトリ URL ではなく `@modelcontextprotocol/server-github` を使う

Claude Desktop だけ急に落ち始めたときは、再インストールに行く前に `claude_desktop_config.json` の `url` 形式をまず確認してみてほしい。
