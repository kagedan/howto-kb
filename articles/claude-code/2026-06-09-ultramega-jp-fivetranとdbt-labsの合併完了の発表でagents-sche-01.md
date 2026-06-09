---
id: "2026-06-09-ultramega-jp-fivetranとdbt-labsの合併完了の発表でagents-sche-01"
title: "@ultramega_jp: Fivetranとdbt Labsの合併完了の発表で「Agents Schema」っていう聞き慣れない標準が出てたので、"
url: "https://x.com/ultramega_jp/status/2064143606970208587"
source: "x"
category: "claude-code"
tags: ["AI-agent", "x"]
date_published: "2026-06-09"
date_collected: "2026-06-09"
summary_by: "auto-x"
query: "Claude Code CLAUDE.md 書き方 OR コンテキスト管理 OR Handover"
---

Fivetranとdbt Labsの合併完了の発表で「Agents Schema」っていう聞き慣れない標準が出てたので、気になって調べてみました。

中身は思ってたよりシンプルで、ウェアハウスの中に1つスキーマを切って、メトリクス定義・セマンティックモデル・dbt lineageをただのSQLテーブルとして置く。

そこをAIエージェントが読みに行く共有コンテキスト層にする、という発想でした。Gitで配られるので、取り込みツールやウェアハウスは問わないらしいです。

セマンティックレイヤーと何が違うんだ、思ったのですが、定義がそれを記述するモデルのすぐ隣に置かれて一緒にバージョン管理される、という点が肝っぽい？
定義とドキュメントがズレていく、あのドリフトをなくす狙いみたいです。

調べてて一番引っかかったのは別の数字ですが、エージェントに数百万ドル投資してる企業が6割いるのに、それを支えられる基盤を持ってるのは15%だけ、と。

CVや売り上げの定義が部署ごとに違う、みたいな話を現場で何度か聞いてきたので、この差は妙に腑に落ちました。

賢いモデルの前に、揃った定義のほうが先なのかもしれません。
ただ、その整備こそ一番進まない領域だったりするので、標準が出たから揃うとも限らないですが…。

ソース
https://t.co/uYuyyIBJz1
