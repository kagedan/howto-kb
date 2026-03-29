---
id: "2026-03-28-sugurukun-ai-ちなみにanthropicが公式で公開している-claude-codeベス-01"
title: "@SuguruKun_ai: ちなみにAnthropicが公式で公開している 「Claude Codeベストプラクティス」公式ガイドには絶対押さえてお"
url: "https://x.com/SuguruKun_ai/status/2037715971134374297"
source: "x"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "x"]
date_published: "2026-03-28"
date_collected: "2026-03-29"
summary_by: "auto-x"
---

ちなみにAnthropicが公式で公開している
「Claude Codeベストプラクティス」公式ガイドには絶対押さえておきたい基礎テクニックがかなり書いてるのでオススメです。
ㅤ
・コンテキスト管理からPlan Mode活用
・CLAUDE.mdの書き方
・並列セッションでのスケーリング

などなど、実践的なパターンを体系的にまとめてます：
ㅤ
Claude Code使ってる人はぜひ読んでみて欲しいです👇🧵  

個人的に刺さったのが「コンテキストウィンドウは管理する最も重要なリソース」という話
ㅤ
Claude Codeのパフォーマンスが落ちる最大の原因は、コンテキストが関係ない情報で埋まること
ㅤ
対策：
・タスク切り替え時に /clear でリセット
・調査はサブエージェントに委譲（メインの窓を汚さない）
・2回修正して直らなかったら /clear して最初からやり直す
ㅤ
これ意識するだけで体感2倍は違う    

公式ガイド👇
https://code.claude.com/docs/ja/best-practices      

ここのClaude mdについてはこちらに
