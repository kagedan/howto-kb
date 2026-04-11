---
id: "2026-04-10-claude-code-hooks-で開発フローを全自動化した話-実戦で使っている15の-hook-01"
title: "Claude Code Hooks で開発フローを全自動化した話 ─ 実戦で使っている15の hook"
url: "https://qiita.com/kawabe0201/items/3fcf698abe60d57b211b"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-10"
date_collected: "2026-04-11"
summary_by: "auto-rss"
---

Claude Code の `hooks` 機能は、Claude のツール実行の前後や特定イベントで任意のシェルコマンドを差し込める仕組みだ。ここを設計すると、型チェック忘れ・破壊的コマンドの事故・作業ログの欠損といった「人間の不注意由来の事故」がゼロになる。

この記事では、俺が `~/.claude/settings.json` に実際に仕込んでいる15個の hook を全公開する。

## hooks の基本構造

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "echo 'pre-bash'" }
        ]
      }
    ],
    "PostToolUse": [],
    "UserPromptSubmit": [],
    "Stop": []
  }
}
```

使えるイベントは主に `PreToolUse` `P
