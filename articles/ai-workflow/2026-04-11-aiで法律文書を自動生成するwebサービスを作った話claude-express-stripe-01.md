---
id: "2026-04-11-aiで法律文書を自動生成するwebサービスを作った話claude-express-stripe-01"
title: "AIで法律文書を自動生成するWebサービスを作った話（Claude + Express + Stripe）"
url: "https://qiita.com/Mildsolt2914491/items/fb1aa7ddbcfd4a098a67"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-04-11"
date_collected: "2026-04-12"
summary_by: "auto-rss"
---

# AIで法律文書を自動生成するWebサービスを作った話（Claude + Express + Stripe）

スタートアップや個人開発者が事業を始めるとき、必ずぶつかる問題があります。

**「契約書どうする？」**

弁護士に頼むと最低でも5〜20万円、時間もかかる。テンプレートをそのまま使うと抜けがある。かといって自分で0から書くのは無理。

この問題をAIで解決するWebサービスを作りました。

## 作ったもの

**AI法律文書作成サービス** → https://legal.mildsolt.jp

- NDA（秘密保持契約書）：¥30,000 即日
- SaaS利用規約：¥50,000 即日
- 業務委託契約書：¥40,000 即日
- プライバシーポリシー：¥30,000 即日

必要情報を入力 → Stripe決済 → Claude MAXが文書生成 → メールで即納品

## 技術スタック

```
バックエンド: Node.js / Express
DB: SQLite (better-sqlite3)
AI生成: Claude MAX (claude-hai
