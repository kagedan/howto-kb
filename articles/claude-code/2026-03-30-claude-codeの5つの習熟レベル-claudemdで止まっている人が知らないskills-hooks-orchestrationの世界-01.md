---
id: "2026-03-30-claude-codeの5つの習熟レベル-claudemdで止まっている人が知らないskills-hooks-orchestrationの世界-01"
title: "Claude Codeの5つの習熟レベル。CLAUDE.mdで止まっている人が知らないSkills・Hooks・Orchestrationの世界について"
url: "https://qiita.com/miruky/items/43a6828c806a9ebcfdd1"
source: "notebooklm"
category: "claude-code"
tags: ["claude-code", "skill", "hooks", "orchestration", "qiita"]
date_published: "2026-03-25"
date_collected: "2026-03-30"
summary_by: "auto-notebooklm"
---

## 概要

Claude Codeの習熟度を5段階のレベルで体系化したフレームワークを紹介する記事（著者: miruky）。Reddit投稿者DevMoses氏の実例「198エージェントを32セッションで並列実行、マージコンフリクト率3.1%」を基に解説。

## 5つの習熟レベル

| レベル | 名称 | 特徴 |
|--------|------|------|
| 1 | Raw Prompting | 毎回同じ指示を繰り返す初期段階 |
| 2 | CLAUDE.md | プロジェクトルールをファイルに永続化（200行以下推奨） |
| 3 | Skills | オンデマンドで読み込まれる手順書（使用時のみトークン消費） |
| 4 | Hooks | ライフサイクルに自動品質ゲートを組み込む |
| 5 | Orchestration | 複数エージェントの並列統制とチーム運用 |

## ポイント

「自分で進級するのではなく、天井にぶつかって必然的に進む」という洞察。各レベルは前のレベルの課題解決として積み上がる構造になっている。
