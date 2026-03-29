---
id: "2026-03-28-リポジトリに置くだけでaiが空気を読む-copilot-instructionsmd-と各aiツール-01"
title: "リポジトリに置くだけでAIが空気を読む — copilot-instructions.md と各AIツールの指示ファイルまとめ"
url: "https://qiita.com/idw-coder/items/f26adfbcba2449f2464a"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "Gemini", "qiita"]
date_published: "2026-03-28"
date_collected: "2026-03-29"
summary_by: "auto-rss"
---

## この記事について

GitHub Copilot、Claude Code、Gemini Code Assist、Cursor など、AIコーディング支援ツールが当たり前になってきた。しかしデフォルトのままでは、プロジェクト固有の規約やレビュー方針を無視したコードや提案が出てくることも多い。

各ツールには「リポジトリにファイルを置くだけで、AIにプロジェクト固有の指示を与えられる」仕組みがある。本記事ではその概要と、実際にどんな内容を書くと効果的かを整理する。

---

## 各AIツールの指示ファイル一覧

| ツール | ファイルパス | 備考 |
|---|---|---|
| GitHub Copilot | `.github/copilot-instructions.md` | VS Code / GitHub上で自動読み込み |
| Claude Code | `.claude/instructions.md`, `CLAUDE.md` | サブディレクトリごとの指示も可 |
| Gemini Code Assist | `.gemini/instructions.
