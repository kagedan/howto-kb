---
id: "2026-03-26-oikon48-claude-code-2185-抜粋-hooksにパーミッションルール構文例-ba-01"
title: "@oikon48: Claude Code 2.1.85 (抜粋) ・Hooksにパーミッションルール構文（例: `Bash(git *"
url: "https://x.com/oikon48/status/2037313024793673930"
source: "x"
category: "claude-code"
tags: ["claude-code", "x"]
date_published: "2026-03-26"
date_collected: "2026-03-28"
summary_by: "auto-x"
---

Claude Code 2.1.85 (抜粋)
 
・Hooksにパーミッションルール構文（例: `Bash(git *)`）を使用した条件 `if` フィールドを追加。Hooksが実行されるタイミングをフィルタリングし、プロセス生成のオーバーヘッドを削減
 
・スケジュールタスク（`/loop`、`CronCreate`）が発火したときに、トランスクリプトへタイムスタンプマーカーを追加
 
・画像貼り付け時の `[Image #N]` プレースホルダーの後にスペースを追加
 
・組織ポリシー（`managed-settings.json`）でブロックされたプラグインはインストールや有効化ができなくなり、マーケットプレイスビューからも非表示に

・PreToolUse フックが `permissionDecision: "allow"` と共に `updatedInput` を返すことで `AskUserQuestion` に応答できるようになった。独自 UI で回答を収集するヘッドレス統合が実現可能に

・会話がコンパクトリクエスト自体に収まらないほど大きくなった場合に `/comp
