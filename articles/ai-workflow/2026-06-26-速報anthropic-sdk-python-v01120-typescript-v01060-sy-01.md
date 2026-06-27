---
id: "2026-06-26-速報anthropic-sdk-python-v01120-typescript-v01060-sy-01"
title: "【速報】Anthropic SDK Python v0.112.0 / TypeScript v0.106.0 — system.message ストリーミングほか新機能を3分で解説"
url: "https://qiita.com/kinamocchi_tech/items/159623f451f0f2a1aa60"
source: "qiita"
category: "ai-workflow"
tags: ["API", "LLM", "Python", "TypeScript", "qiita"]
date_published: "2026-06-26"
date_collected: "2026-06-27"
summary_by: "auto-rss"
query: ""
---

> この記事は **きなこもっちーのテック深掘り** の速報記事です。公式リリースノートを元に最速でお届けします。

## 🚀 リリース概要

Anthropic の公式 SDK が Python・TypeScript 同時にアップデートされました。

| SDK | バージョン | リリース日 |
|-----|-----------|-----------|
| anthropic-sdk-python | v0.112.0 | 2026-06-26 |
| anthropic-sdk-typescript | v0.106.0 | 2026-06-26 |

---

## 🆕 新機能① system.message ストリーミング対応

ストリーミングレスポンスで `system.message` イベントが扱えるようになりました。

```python
with client.messages.stream(
    model="claude-opus-4-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello!"}],
) as stream:
    for event in stream:
        # system.message イベントをリアルタイム処理
        print(event)
```

リアルタイムでシステムメッセージを処理できるため、エージェントのデバッグや詳細なログ収集に役立ちます。Python・TypeScript の両 SDK で同時サポートされています。

---

## 🚫 新機能② refusal_category フィールド追加

拒否されたリクエストに `refusal_category` フィールドが付与されます。拒否の理由を細かく分類できるため、アプリ側でのコンテンツポリシー対応がしやすくなります。

---

## 👤 新機能③ ユーザープロフィール ID をリクエストヘッダーに送信可能

マルチユーザー環境でのトレーサビリティ向上のため、リクエストにユーザー ID を付与できるようになりました。ログ・デバッグ・監査用途に活用できます。

---

## 🐛 バグ修正（Python のみ）

- **memory ツール**: 親ディレクトリを正しいパーミッションで作成するよう修正

---

## まとめ

今回のアップデートは **破壊的変更なし**。後方互換を維持しつつ、API 開発ツールとしての便利さが着実に上がっています。特に `system.message` ストリーミング対応と `refusal_category` は、本格的なエージェント開発をしているチームに役立つ機能です。

---

## 出典

- [anthropic-sdk-python v0.112.0 リリースノート](https://github.com/anthropics/anthropic-sdk-python/releases/tag/v0.112.0)
- [anthropic-sdk-typescript v0.106.0 リリースノート](https://github.com/anthropics/anthropic-sdk-typescript/releases/tag/sdk-v0.106.0)

---

*きなこもっちーのテック深掘り — AI/LLM の最新情報を最速でお届けします*
