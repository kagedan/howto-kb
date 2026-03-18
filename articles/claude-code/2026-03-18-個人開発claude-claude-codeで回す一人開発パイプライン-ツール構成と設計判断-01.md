---
id: "2026-03-18-個人開発claude-claude-codeで回す一人開発パイプライン-ツール構成と設計判断-01"
title: "【個人開発】Claude + Claude Codeで回す一人開発パイプライン — ツール構成と設計判断"
url: "https://qiita.com/imyshKR/items/c2de1c0e24f0245bff91"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-03-18"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

一人で企画から運営まで回すために、Claude.ai、Claude Code、[Claude Forge](https://github.com/sangrokjung/claude-forge)を組み合わせたプロセスシステムを構築しています。この記事はシステム全体の構成と各ツールの役割をまとめたものです。
![forge-pipeline-diagram.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4380119/5924eb46-667b-4938-be34-998366126aba.png)


> ※ 各ツールの詳細記事は順次公開予定です。公開後にリンクを追加していきます。

## システム全体像

![process-flow-diagram.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4380119/70d062a5-2273-4c41-bea7-70869c313613.png)

```
1. アイデ
