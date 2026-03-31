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

- Claude Desktop で `mcpServers.*.url` を使うと、今回のように起動時クラッシュになることがある
- 修正は `mcp-remote` を使った `command + args` 形式への置き換えでOK
- GitHub MCP だけは URL ではなく `@modelcontextprotocol/server-github` を直接実行する

## まず起きていた症状

Claude Desktop を起動すると毎回このダイアログが出て使えなくなった。

```text
We are so sorry, Claude Desktop failed
