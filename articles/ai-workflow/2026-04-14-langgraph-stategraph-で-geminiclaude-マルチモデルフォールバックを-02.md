---
id: "2026-04-14-langgraph-stategraph-で-geminiclaude-マルチモデルフォールバックを-02"
title: "LangGraph StateGraph で Gemini/Claude マルチモデルフォールバックを実装する"
url: "https://qiita.com/keita2399_swimmer/items/3756ad0b9027f87e48da"
source: "qiita"
category: "ai-workflow"
tags: ["API", "qiita"]
date_published: "2026-04-14"
date_collected: "2026-04-14"
summary_by: "auto-rss"
---

## はじめに

AIを使ったAPIサーバーを本番運用していると、避けられない問題があります。それは **APIキーのレート制限** です。

Gemini APIは無料枠のリクエスト上限が厳しく、ユーザーが集中するとすぐに `429 Too Many Requests` が返ってきます。「APIキーを複数持てばよい」と思っても、複数キーのフォールバック処理を手書きするのは案外面倒です。さらに「Geminiが全滅したらClaudeに切り替えたい」という要件が加わると、状態管理のコードが複雑になりがちです。

この記事では、**LangGraph StateGraph** を使ってこのフォールバックロジックをエレガントに実装する方法を紹介します。

```
Gemini キー1 → 失敗
Gemini キー2 → 失敗  
Gemini キー3 → 失敗
     ↓ 2秒待機してリトライ
Gemini キー1〜3 → 全滅
     ↓
Claude (Haiku) → 成功 ✅
```

## 完成形のコード概要

今回実装したのは、AI見積もりシステムのバックエンドAPIサーバーで
