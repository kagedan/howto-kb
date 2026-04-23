---
id: "2026-04-12-claude-codeのhookどれを入れればいい5つの質問で最適な安全設定が分かるツールを作った-01"
title: "Claude Codeのhook、どれを入れればいい？——5つの質問で最適な安全設定が分かるツールを作った"
url: "https://qiita.com/yurukusa/items/6fa3ebbb45406547d2ff"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "qiita"]
date_published: "2026-04-12"
date_collected: "2026-04-12"
summary_by: "auto-rss"
---

Claude Codeにhookを入れたいけど、650個以上もあるとどれを選べばいいかわからない。

そこで[Hook Selector](https://yurukusa.github.io/cc-safe-setup/hook-selector.html)を作った。5つの質問に答えるだけで、自分の使い方に合ったhookセットが出てくる。

## 使い方

1. [Hook Selector](https://yurukusa.github.io/cc-safe-setup/hook-selector.html)を開く
2. 5つの質問に答える（30秒）
3. 推薦されたhookのインストールコマンドをコピペ

質問の内容:

* Claude Codeの使い方（対話型/半自律/完全自律）
* 一番心配なこと（ファイル削除/トークン消費/秘密漏洩/コード品質）
* 技術レベル
* サブエージェント/MCPの使用有無
* 過去の事故経験

## なぜ作ったか

cc-safe-setupに650以上のexample hookがあるが、「全部入れる」のは無意味だし、「1つずつ読んで選ぶ」のは現実的じゃない。

800時間以上Claude Codeを自律運用してきて、「この使い方ならこのhookが効く」というパターンが見えてきた。それをウィザード形式にしたのがHook Selector。

## 推薦の仕組み

16個のhookデータベースがあり、各hookに「どんなユーザーに有効か」のスコアリング条件が設定されている。回答に基づいてスコアを計算し、高い順に推薦する。

例えば「完全自律+トークン消費が心配」なら、large-read-guard、token-budget-guard、subagent-budget-guard、duplicate-read-detector等が高スコアになる。

## インストール

推薦されたhookは`npx cc-safe-setup --install-example <name>`でインストールできる。結果ページにコマンドが生成されるので、コピペするだけ。

---

hookの設計パターンや自律セッション運用の実践例は[Claude Codeを本番品質にする — hook設計・運用ガイド](https://zenn.dev/yurukusa/books/6076c23b1cb18b)（¥800・第3章まで無料）にまとめている。非エンジニアがAIで事業を回す全記録は[AIに仕事を任せてみた](https://zenn.dev/yurukusa/books/3c3c3baee85f0a19)（¥800・第2章まで無料）。

---

---

**📖 トークン消費に困っているなら** → [Claude Codeのトークン消費を半分にする——800時間の運用データから見つけた実践テクニック](https://zenn.dev/yurukusa/books/token-savings-guide?utm_source=qiita-6fa3ebbb&utm_medium=article&utm_campaign=token-book)（¥2,500・はじめに+第1章 無料）

---

**⚠️ CVE-2026-21852（2026年4月公開）**: プロジェクト内`.claude/settings.json`経由でAPIキー窃盗。対策: `npx cc-safe-setup`（ユーザーレベル設定で免疫）→ [詳細](https://yurukusa.github.io/cc-safe-setup/opus-47-survival-guide.html#cve-settings-exfil)
