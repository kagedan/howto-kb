---
id: "2026-07-22-claudeの-web-fetch-ツールは会話に出たurlしか読めない-01"
title: "Claudeの Web Fetch ツールは「会話に出たURLしか読めない」"
url: "https://qiita.com/hashito/items/7777d88e962275d83d74"
source: "qiita"
category: "ai-workflow"
tags: ["API", "qiita"]
date_published: "2026-07-22"
date_collected: "2026-07-23"
summary_by: "auto-rss"
query: ""
---

## 背景

私はフリートのサイトで、Claude API の公式ドキュメントを日本語に噛み砕く記事を続けている。

今日は Web Fetch ツールの回を書いた。
書きながら、自分がこのツールの一番大事な制約を分かっていなかったことに気づいた…。

## Web Search と何が違うのか

Web Search は「情報を探す」ツールで、Web Fetch は「指定した1ページを丸ごと読む」ツールだ。
`tools` に足しておくと、Claude が必要と判断したときに Anthropic 側がそのURLを取得して会話に差し込む。
サーバ側で実行される組み込みツールなので、こちらで `tool_result` を返す必要はない。

下記のように足すだけ。

```json
{
  "type": "web_fetch_20250910",
  "name": "web_fetch",
  "max_uses": 5
}
```

## 一番大事なのは「勝手なURLは読めない」こと

私が誤解していたのはここだ。
Claude は自分で組み立てた任意のURLを読めない。
読めるのは、ユーザーのメッセージや過去の検索/取得結果など、{会話にすでに登場したURL}だけ。

これはデータ持ち出しを防ぐための仕組みらしい。
「Fetch できるんだから何でも取れる」と思い込んでいたので、これは知れてよかった。

だから Web Search と両方有効にしておくと、URLを渡さなくても「まず検索で見つけて、次に取得して読む」という流れが1リクエストで完結する。

## 料金の感覚だけ持っておく

ツール自体に追加料金はなく、取得した本文がコンテキストに載るぶんの通常トークン代だけかかる。
目安として100kBのドキュメントで25,000トークンくらいらしい。
大きなPDFをうっかり丸ごと入れると効いてくるので、`max_content_tokens` で上限を切っておくのが無難だと思う。

書いた解説は下記。
https://claude-guide.autoarticles.net/tutorials/web-fetch-tool-with-the-claude-api.html

一次情報は必ず公式で確かめてほしい…と、自分にも言い聞かせている。

---

> 本記事はAI補助で執筆した、個人開発の紹介記事です。
