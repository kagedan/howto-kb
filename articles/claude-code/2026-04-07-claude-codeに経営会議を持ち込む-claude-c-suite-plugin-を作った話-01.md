---
id: "2026-04-07-claude-codeに経営会議を持ち込む-claude-c-suite-plugin-を作った話-01"
title: "Claude Codeに「経営会議」を持ち込む — claude-c-suite-plugin を作った話"
url: "https://qiita.com/kiyotaman/items/29718a0d5f6363ccb8a2"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-07"
date_collected: "2026-04-08"
summary_by: "auto-rss"
---

## TL;DR
https://github.com/JFK/claude-c-suite-plugin

- Claude Code に **CEO・CTO・CSO・CFO
など14人の経営層レビュー**を呼び出せるプラグインを作った
- `/claude-c-suite:ceo` を打つだけで、リポジトリを自動診断 →
最適な3つの専門家視点を選定 → 統合された経営判断を返す
- 「どのレビューを呼べばいいか分からない」問題を解決する単一質問ルーター `/ask` も用意
- 全コマンドが**解析のみ・変更しない**ので、どんなリポでも安全に試せる

## なぜ作ったか

Claude Codeでコードレビューを頼むと、たいてい「とりあえず良さそうな提案」が返ってきます。でも実際の開発現場では、レビューする人の**役割**で見るポイントがまったく違うはず。

- CTO は技術的負債とアーキの一貫性を見る
- CSO は OWASP Top 10 と秘匿情報の漏洩を見る
- CFO は N+1 クエリと無駄なリソース消費を見る
- CMO は SEO と Core Web Vi
