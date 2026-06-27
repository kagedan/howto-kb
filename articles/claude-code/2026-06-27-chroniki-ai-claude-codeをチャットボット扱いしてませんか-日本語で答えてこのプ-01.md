---
id: "2026-06-27-chroniki-ai-claude-codeをチャットボット扱いしてませんか-日本語で答えてこのプ-01"
title: "@chroniki_ai: Claude Codeをチャットボット扱いしてませんか？🐾 「日本語で答えて」「このプロジェクトはECサイトです」——"
url: "https://x.com/chroniki_ai/status/2070764115174588425"
source: "x"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "prompt-engineering", "AI-agent", "x"]
date_published: "2026-06-27"
date_collected: "2026-06-28"
summary_by: "auto-x"
query: "Claude Code hooks 使い方 OR subagents 設定 OR Claude Code スケジュール"
---

Claude Codeをチャットボット扱いしてませんか？🐾

「日本語で答えて」「このプロジェクトはECサイトです」——毎回こういう説明をチャットに打ち込んでいる人、実はものすごく損してるんです。

2025年6月18日、Anthropicが「ステアリングレイヤー」と呼ぶ仕組みを公式にまとめて公開しました。

一言でいうと「Claudeの動き方そのものを事前に設計できる仕組み」です。

具体的には7つの制御手段が整理されています。

・CLAUDE.md — プロジェクト全体のルールを書いておくファイル
・rules — 禁止・許可する行動パターンの設定
・skills — よく使う手順をスキルとして登録
・subagents — 専門タスク担当の小さなAIを配置
・hooks — 特定イベント時に自動で処理を走らせる
・output styles — 出力フォーマットを固定
・system prompt追記 — 全セッション共通の指示

たとえで言うと「AIへのUSBハブ」みたいなイメージです。複数の設定を同時にClaude Codeに繋いで、動き方を細かくカスタマイズできます。

僕が特にすごいと思ったのがhooksです。「コード修正が終わったら自動でテストを走らせて、失敗したら修正ループ、パスしたら完了通知」という一連の流れが、設定ファイルを書くだけで動きます。

Before: Claude Codeに作業させる→手動で確認→エラーがあれば再依頼

After: hooksが自動でテスト→失敗なら修正ループ→パスで完了通知

この「確認の往復」が丸ごと消えます。

コードが書けない人でも、CLAUDE.mdに日本語で「このプロジェクトの概要」「出力は日本語で」を3行書くだけで始められます。それだけで毎回の説明コストがゼロになるので、まず試してみてほしいです🐾

Claude Codeをちゃんと学びたい人向けに、無料のオープンチャット「クロニキの部屋」をやってます🤖 初歩的な質問でも大歓迎です。

▼ 無料オープンチャット「クロニキの部屋」＋特典はこちら（匿名OK）
https://t.co/8ELQS4c5Nk


--- 引用元 @chroniki_ai ---
https://t.co/LKLvB6g98C
