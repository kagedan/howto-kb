---
id: "2026-03-21-notionページをclaude-aiで自動フラッシュカード化するwebアプリを作った-01"
title: "NotionページをClaude AIで自動フラッシュカード化するWebアプリを作った"
url: "https://qiita.com/tai0921/items/55a60a0e403a5cf8ff9e"
source: "qiita"
category: "ai-workflow"
tags: ["API", "qiita"]
date_published: "2026-03-21"
date_collected: "2026-03-22"
summary_by: "auto-rss"
---

## はじめに

**NotionページのURLを貼るだけで、Claude AIが自動でフラッシュカード（Q&A）を生成する** Webアプリを作りました。

工夫した点は **Notion → Claude → Notion の一気通貫フロー** です。

1. **Notion API** でページ本文（ブロック）を再帰的に取得
2. **Claude Opus 4.6** に送って問題・解説・難易度付きのカードを生成
3. 生成したカードを **Notionデータベース** に自動書き込み
4. ブラウザ上でカードをめくりながら自己評価（知ってた ✅ / 復習する 🔁）

---

## システム構成

```
ブラウザ (React + Vite, :5173)
  │
  └─ POST /api/generate
        │
        ├─ Notion API
        │     └─ ページID抽出 → ブロック再帰取得 → Markdownテキスト化
        │
        ├─ Claude API (Opus 4.6)
