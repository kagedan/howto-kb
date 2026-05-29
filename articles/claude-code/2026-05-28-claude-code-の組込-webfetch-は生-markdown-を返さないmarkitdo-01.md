---
id: "2026-05-28-claude-code-の組込-webfetch-は生-markdown-を返さないmarkitdo-01"
title: "Claude Code の組込 WebFetch は生 Markdown を返さない。markitdown に乗り換えた話"
url: "https://zenn.dev/kanagen/articles/claude-code-webfetch-vs-mcp-server-fetch"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "antigravity", "JavaScript", "zenn"]
date_published: "2026-05-28"
date_collected: "2026-05-29"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Code の組込 WebFetch は、URL を取得するとき Haiku が副次会話を起動して内容を解釈・要約する。生の Markdown をそのまま取りたい場合には向いていない。

代替を調べると `mcp-server-fetch` か `markitdown` が候補になる。さらに調べると `markitdown <url>` は MCP 不要で fetch MCP と同等の結果を返すとわかった。

## 3ツールの仕組みを比較する

Claude Code で URL を取得する手段は複数ある。それぞれの内部実装を整理した。

| 観点 | WebFetch（組込） | mcp-server-fetch | markitdown `<url>` |
| --- | --- | --- | --- |
| HTTP 取得 | Axios | httpx | requests |
| AI 介在 | **あり**（Haiku が要約） | なし | なし |
| 追加トークンコスト | ~$0.033/回 | なし | なし |
| JS レンダリング | ❌ | ❌ | ❌ |
| 出力 | AI 解釈済みテキスト | 生 Markdown | 生 Markdown |
| MCP 必要 | 不要 | **必要** | 不要 |

組込 WebFetch は Haiku が副次会話を起動して解釈・要約する。同じ URL を叩いても出力が変わるし、コストもかかる。一方、mcp-server-fetch は httpx で取得して Markdown に変換するだけ — AI は介在しない。

`markitdown <url>` は mcp-server-fetch とまったく同等の結果を返す。Microsoft 製のオープンソースライブラリで、URL 取得のほかに PDF・Word・Excel などのローカルファイル変換にも対応している。

```
markitdown "https://docs.anthropic.com/ja/docs/claude-code" 2>/dev/null
```

chatforest.com の記事でも確認されている。

> "The server uses httpx for HTTP requests — plain HTTP, no browser engine. JavaScript-heavy SPAs, dynamically loaded content, and client-side rendered pages return empty or partial content."  
> — chatforest.com

## fetch MCP の初回タイムアウト問題

`/mcp` で確認すると `MCP server "fetch" connection timed out after 30000ms` と表示されることがある。

原因はシンプルだ。Claude Code 起動時に `uvx mcp-server-fetch` を実行するとき、**初回は lxml（5MB）を含む 45 パッケージをダウンロードする**。このダウンロードが MCP の接続タイムアウト（30秒）を超えてしまう。

```
$ uvx mcp-server-fetch --help
Downloading lxml (5.0MiB)
 Downloaded lxml
Installed 45 packages in 35ms
# ↑ 初回はここまで到達する前に30秒タイムアウトが発生する
```

2回目以降は uvx のキャッシュが効いて即時起動する。つまり**一度手動で実行すればキャッシュが温まり、次回からは正常接続できる**。

```
uvx mcp-server-fetch --help > /dev/null 2>&1
```

![初回タイムアウト vs キャッシュ済み起動の比較](https://static.zenn.studio/user-upload/deployed-images/8ec4ca3e3edc014d6b81d3b7.png?sha=1c51751faf77362ab76ca6af02dd04a953d6b18e)

DevContainer を使っている場合は `postCreateCommand` に追加しておくと再発しない。

## JS描画 SPA という共通の壁

ただし、**mcp-server-fetch も markitdown も、JavaScript で描画する SPA には対応していない**。

Google の CLI ドキュメント（antigravity.google）で確認した。

```
$ markitdown "https://antigravity.google/docs/cli-getting-started" 2>/dev/null
# → 空出力

$ curl -sI "https://antigravity.google/docs/cli-getting-started" | head -1
HTTP/2 200
# ← 200 を返すが本文は JS が描画するため、素の HTTP 取得では空になる
```

fetch MCP でも同じ結果になる。この場合は `firecrawl scrape` を用いて取得するのが良い。

```
$ firecrawl scrape "https://antigravity.google/docs/cli-getting-started" --only-main-content
# → # Getting Started with Antigravity CLI ... （正常取得）
```

## 結論

上記のfetch MCP の初回タイムアウト問題がある事や、個人的にMCPは出来る限り使わないようにしたいため、  
Webページの取得はmarkitdownが現時点ではベスト。

## 参考
