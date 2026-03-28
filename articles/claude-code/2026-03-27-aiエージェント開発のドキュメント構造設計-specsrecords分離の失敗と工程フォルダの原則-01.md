---
id: "2026-03-27-aiエージェント開発のドキュメント構造設計-specsrecords分離の失敗と工程フォルダの原則-01"
title: "AIエージェント開発のドキュメント構造設計 — specs/records分離の失敗と工程=フォルダの原則"
url: "https://zenn.dev/saytooy_arch/articles/05-doc-structure-design"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-03-27"
date_collected: "2026-03-28"
summary_by: "auto-rss"
---

TL;DR
Claude Codeのマルチエージェント体制でSaaS開発をしている。ドキュメント構造を「specs（設計書）/ records（記録）」の2分類で始めたが、工程との対応が崩れて破綻した。「工程番号フォルダに全成果物を格納する」原則に転換した話。

 背景: specs/records 分離モデル
最初のドキュメント構造:


specs/ — 最新状態を示す設計書（上書き更新）

records/ — 経緯記録（追記のみ）

概念としては正しい。が、実運用で問題が起きた。

 何が起きたか


画面仕様書がEDにない: specs/screen/ に格納 → ED工程...
