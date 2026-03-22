---
id: "2026-03-22-claude-codeからwebブラウザを操作できるmcpサーバーを作った-01"
title: "Claude CodeからWebブラウザを操作できるMCPサーバーを作った"
url: "https://qiita.com/koyama-techno/items/8ae01a58f09d4a9d8183"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "LLM", "qiita"]
date_published: "2026-03-22"
date_collected: "2026-03-22"
summary_by: "auto-rss"
---

## なぜ作ったか

Claude Codeを使って開発していると、**Webサイトの動作確認やスクレイピングを自然言語で指示したい**場面が増えてきました。

例えば：
- 「Yahooでtechnosphereを検索して、公式サイトのスクリーンショットを撮って」
- 「Redmineにログインしてチケット一覧を確認して」
- 「このフォームに入力してsubmitして」

既存のブラウザ自動化ツールはスクリーンショットベースのものが多く、LLMが画像を解析する必要があるため**処理が遅く、トークンも消費**します。

そこで、**DOM構造を直接JSON形式で取得**し、LLMが効率的に操作できるMCPサーバーを作りました。

## 何ができるか

### スクリーンショットなしで高速にページ状態を取得

```
browser_get_state
```

↓ JSON形式でページの構造を返す

```json
{
  "url": "https://example.com/login",
  "title": "ログイン",
  "forms": [
    {
      "a
