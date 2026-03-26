---
id: "2026-03-25-claude会話ウィンドウのネーミングルール-custom-instructionで自動提案させる-01"
title: "Claude会話ウィンドウのネーミングルール — Custom Instructionで自動提案させる"
url: "https://qiita.com/imyshKR/items/495bb9e910bea3c682b6"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-03-25"
date_collected: "2026-03-26"
summary_by: "auto-rss"
---

Claudeでプロジェクトを複数並行すると、サイドバーの自動生成タイトルでは「どの会話がどの段階か」が判別できなくなります。この記事では、Custom Instruction（User Preferences）に入れるだけで、Claudeが会話開始時にネーミングを自動提案してくれる仕組みを紹介します。

## やりたいこと

> ![네이밍_전_대화목록.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4380119/1079e499-a4e1-4d66-8d54-45bdba9b89af.png)


- 会話ウィンドウ名で**プロジェクト名**と**作業段階**を一目で把握
- Claudeが自動で名前を提案、手動リネームするだけ
- すべてのプロジェクトで一貫適用

## 設定方法

Settings > Profile > User Preferencesに以下を追加します。

```
## 会話ウィンドウのネーミング
すべてのClaude会話開始時、会話の目標/内容を把握
