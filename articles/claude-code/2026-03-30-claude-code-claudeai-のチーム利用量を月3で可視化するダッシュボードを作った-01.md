---
id: "2026-03-30-claude-code-claudeai-のチーム利用量を月3で可視化するダッシュボードを作った-01"
title: "Claude Code / claude.ai のチーム利用量を月$3で可視化するダッシュボードを作った"
url: "https://qiita.com/Odin/items/f637f010c0274b0d9aa6"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-03-30"
date_collected: "2026-03-31"
summary_by: "auto-rss"
---

## はじめに

Anthropicが提供するClaude Codeを10人のチームで利用しています。Teamsプランの公式ダッシュボードでは取得できる情報が限られており、「誰がどれくらい使っているか」「トークン消費量の推移」といった情報が把握できませんでした。

そこで、[ZOZOのテックブログ記事](https://techblog.zozo.com/entry/claudecode-otel)を参考に、AWS上に自前のダッシュボードを構築しました。月額$3程度で運用できます。

## 何を作ったか

Claude CodeのOpenTelemetryテレメトリデータと、claude.aiのエクスポートデータを収集・可視化するダッシュボードです。

### Claude Code ダッシュボード

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3566513/19844f4d-a507-4cbf-981f-4e21f20fd07f.png)

- 日別セッション数・トークン推移
-
