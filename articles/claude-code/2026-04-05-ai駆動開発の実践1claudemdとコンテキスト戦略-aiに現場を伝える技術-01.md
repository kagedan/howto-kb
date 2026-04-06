---
id: "2026-04-05-ai駆動開発の実践1claudemdとコンテキスト戦略-aiに現場を伝える技術-01"
title: "AI駆動開発の実践（1）CLAUDE.mdとコンテキスト戦略 — AIに「現場」を伝える技術"
url: "https://zenn.dev/miyan/articles/ai-driven-dev-claude-md-context"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "zenn"]
date_published: "2026-04-05"
date_collected: "2026-04-06"
summary_by: "auto-rss"
---

TL;DR

CLAUDE.mdは「AIへの指示書」ではなく「現場の暗黙知を言語化したドキュメント」として設計する
書きすぎると逆効果。「この1行を消したらClaudeが間違えるか？」で削ぎ落とす
階層構造（グローバル → プロジェクト → ディレクトリ）を使い分け、情報をスコープごとに分離する


!
この記事は「AI駆動開発の実践的な進め方（Claude Code編）」シリーズの第1回です。テストなし・ドキュメント不足の既存プロジェクトを、Claude Codeを使って段階的に改善していくフェーズ別ガイドです。

CLAUDE.mdとコンテキスト戦略（この記事）
既存コードを読み...
