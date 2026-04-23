---
id: "2026-04-22-aiは知っているのに使わない-設計タスクの-task-kickoff-プロトコルで潜在能力を引き出す-01"
title: "AIは知っているのに使わない — 設計タスクの task-kickoff プロトコルで潜在能力を引き出す"
url: "https://zenn.dev/fixu/articles/task-kickoff-ai-design-protocol"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-22"
date_collected: "2026-04-23"
summary_by: "auto-rss"
---

はじめに
ある DB 設計の議論で、こんなことが起きました。
親会社・子会社のような階層構造を持つ企業の「利用ログ」テーブルに、どんなカラムを追加すべきか ― これを AI に相談していたときのことです。
私は「売上ログ側に場所 ID を直接持たせるべき」と主張しました。対して AI は「親テーブル経由で JOIN すれば解決できるので不要」と答えてきました。
ここで私が強めに言語化したのは、データ設計の教科書によく載っている一般論です。


マスタ系テーブル（企業・商品・契約など）は正規化する。JOIN で整合性を保つ

ログ系テーブル（売上・操作ログ・監査ログなど）はイベント発生...
