---
id: "2026-04-15-dispatchで複数サブセッションを指揮したら破綻した話-aiエージェントのpm役の難しさ-01"
title: "Dispatchで複数サブセッションを指揮したら破綻した話 — AIエージェントのPM役の難しさ"
url: "https://zenn.dev/fixu/articles/dispatch-multi-session-pm-failure"
source: "zenn"
category: "cowork"
tags: ["AI-agent", "cowork", "zenn"]
date_published: "2026-04-15"
date_collected: "2026-04-16"
summary_by: "auto-rss"
query: ""
---

Day053〜Day054 の作業で、Dispatch（Claude Agent SDK ベースのサブセッション指揮役）を使って複数の Cowork / Code サブセッションを並列運用した。単一セッションへのブリッジとしては機能したが、複数セッション跨ぎの PM 役としては完全に破綻した。その記録と反省。


 構成
今回の Dispatch は以下の 6 サブセッションを管理していた。
Notion 記入担当（N系）

[N1] プロジェクト全体のガイドライン
[N2] 本日の作業記録
[N3] 最終成果物の保管場所

Code 操作担当（C系）

[C1] AWS操作
[C2] ...
