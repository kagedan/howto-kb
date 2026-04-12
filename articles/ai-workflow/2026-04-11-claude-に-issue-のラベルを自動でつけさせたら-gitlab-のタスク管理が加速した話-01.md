---
id: "2026-04-11-claude-に-issue-のラベルを自動でつけさせたら-gitlab-のタスク管理が加速した話-01"
title: "Claude に issue のラベルを自動でつけさせたら GitLab のタスク管理が加速した話"
url: "https://qiita.com/autoaim-jp/items/0556b3514c5001b3a52d"
source: "qiita"
category: "ai-workflow"
tags: ["API", "qiita"]
date_published: "2026-04-11"
date_collected: "2026-04-12"
summary_by: "auto-rss"
---

## はじめに

自宅の Raspberry Pi で GitLab をセルフホストして、日常のタスク管理をすべて Issue で行っています。「〇〇を実装する」「マヨネーズを買う」「明日の出社準備」——こういった雑多な issue を 2,000 件以上ため込んできました。

その中で長年の課題だったのが **ラベル管理**です。「issue を作るときにラベルを設定するマイルールを決めよう」と何度か試みたのですが、面倒で続きませんでした。ラベルのない issue が溜まっていくと、「前にも同じこと書いた気がするな」と思っても探せない。同じラベルで絞り込んで俯瞰する、ということもできない。

この記事では、この問題を **Claude（Anthropic API）+ GitLab の Webhook + CI ジョブ**で解決した話を紹介します。

### テイクアウトメニュー

- GitLab のタスク管理でラベルが使えるようになる仕組み
- Webhook とジョブの使い分けの考え方
- GitLab に Claude を組み込む最小構成の試し方

---

## 以前の状況
