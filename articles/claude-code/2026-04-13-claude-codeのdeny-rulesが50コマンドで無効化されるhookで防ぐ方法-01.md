---
id: "2026-04-13-claude-codeのdeny-rulesが50コマンドで無効化されるhookで防ぐ方法-01"
title: "Claude Codeのdeny rulesが50コマンドで無効化される——hookで防ぐ方法"
url: "https://qiita.com/yurukusa/items/f9c48bb44569bbf4492e"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-13"
date_collected: "2026-04-13"
summary_by: "auto-rss"
query: ""
---

Claude Codeのdeny rules（禁止ルール）に、深刻な脆弱性が見つかった。

**50個以上のサブコマンドを連結すると、すべてのdeny rulesが無効化される。**

[Adversa AI](https://adversa.ai/blog/claude-code-security-bypass-deny-rules-disabled/)の調査で判明した。内部的に50サブコマンドの上限があり、50を超えるとセキュリティチェックがスキップされて「ユーザーに確認」にフォールバックする。自律運行中（`--dangerously-skip-permissions`等）ではそのまま実行される。

## 何が起きるか

settings.jsonにこう書いてあるとする:

```json
{
  "permissions": {
    "deny": ["Bash(rm *)"]
  }
}
```

`rm -rf /important-data` は単体ではブロックされる。しかし:

```bash
true; true; true; true; true; true; t
