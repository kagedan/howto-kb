---
id: "2026-01-31-oikon48-claude-code-の-hooks-のドキュメントが大幅に刷新されて分かりやすく-01"
title: "@oikon48: Claude Code の Hooks のドキュメントが、大幅に刷新されて分かりやすくなったので、ざっくりと変更点をみて"
url: "https://x.com/oikon48/status/2017520328508117193"
source: "x"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "AI-agent", "x"]
date_published: "2026-01-31"
date_collected: "2026-03-19"
summary_by: "auto-x"
---

Claude Code の Hooks のドキュメントが、大幅に刷新されて分かりやすくなったので、ざっくりと変更点をみて見る。
 
Hooksのライフサイクルは以下の通りで、これはClaude Codeの Agentic loop を理解する意味でも分かりやすい。
 
1. セッション開始 (SessionStart)
2. プロンプト入力 (UserPromptSubmit)
3. ツール起動 (PreToolUse)
4. 権限確認 (PermissionRequest)
5. ツール実行
6. ツール実行後処理 (PostToolUse/PostToolUseFailure)
7. (Optional) Subagent処理 (SubagentStart/SubagentStop)
8. Agent loopストップ (Stop)
9. (Optional) コンテキスト圧縮 (PreCompact)
10. セッション終了 (SessionEnd)
 
その他
・非同期通知 (Notification)
・セットアップ (Setup, ドキュメントには記載なし)
