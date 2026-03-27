---
id: "2026-03-26-claude-apiのextended-thinkingレスポンスが2ブロックあるの知ってた-01"
title: "Claude APIのExtended Thinking、レスポンスが2ブロックあるの知ってた？"
url: "https://qiita.com/yurukusa/items/efdbd03a7c173c845e8c"
source: "qiita"
category: "ai-workflow"
tags: ["API", "qiita"]
date_published: "2026-03-26"
date_collected: "2026-03-27"
summary_by: "auto-rss"
---

Anthropic Academyのクイズで間違えた。Extended Thinkingのレスポンス構造を完全に勘違いしていた。

## 2ブロック構造

Extended Thinkingを有効にすると、レスポンスの`content`配列に**2つのブロック**が返る。

```json
{
  "content": [
    {
      "type": "thinking",
      "thinking": "ステップバイステップで考えてみよう...",
      "signature": "eyJhbGciOiJFZDI1NTE5..."
    },
    {
      "type": "text",
      "text": "答えは42です。"
    }
  ]
}
```

`thinking`ブロックが先、`text`ブロックが後。

自分のコードは最後のcontentブロックだけ読んでいた。偶然動いていた。正しくは動いていなかった。

## ストリーミングの罠

ストリーミング時は`thinking_delta`イベントと`text_delta`イ
