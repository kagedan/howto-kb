---
id: "2026-02-18-oikon48-claude-code-2147-多いので抜粋-機能-stop-とsubagents-01"
title: "@oikon48: Claude Code 2.1.47 (多いので抜粋)

【機能】

・Stop とSubagentStop Hooks"
url: "https://x.com/oikon48/status/2024251736597344473"
source: "x"
category: "claude-code"
tags: ["claude-code", "AI-agent", "x"]
date_published: "2026-02-18"
date_collected: "2026-03-19"
summary_by: "auto-x"
---

Claude Code 2.1.47 (多いので抜粋)

【機能】

・Stop とSubagentStop Hooksの入力に`last_assistant_message`フィールドを追加

- `added_dirs`をStatusline JSONの`workspace`セクションに追加

・マルチライン入力のための`chat:newline`キーバインドアクションを追加

・ESCを二回押す代わりに`ctrl+f`ですべてのバックグラウンドエージェントを停止

【修正】

・Context Compaction後にPlanモードが失われ、モデルが計画モードから実装モードに切り替わる問題を修正

・Context Compaction後にセッション名が失われる問題を修正

・単一のファイル書き込み/編集エラーが他のすべての並列ファイル書き込み/編集操作を中断する問題を修正

・settings.jsonで`alwaysThinkingEnabled: true`を設定してもBedrockおよびVertexプロバイダーで思考モードが有効にならない問題を修正

・チームメイトを生成
