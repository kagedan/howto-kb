---
id: "2026-03-26-claude-codevs-codeでcmdnが新規会話にならなくなった原因と対処法-01"
title: "【Claude Code】VS Codeでcmd+Nが新規会話にならなくなった原因と対処法"
url: "https://qiita.com/k_bobchin/items/4dee07aaaab49c5a8599"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-03-26"
date_collected: "2026-03-27"
summary_by: "auto-rss"
---

# 症状

Claude Code 拡張を VS Code のセカンダリサイドバーで使用中、`⌘N`（Cmd+N）で新規会話が開始できなくなった。

以前は `⌘N` で即座に新しいセッションが始まっていたが、拡張のアップデート後に突然動作しなくなった。

## 結論

**`claudeCode.enableNewConversationShortcut` のデフォルト値が `true` → `false` にサイレント変更されていた。**

| バージョン | デフォルト値 |
|-----------|-------------|
| v2.1.71 | `true` |
| v2.1.84 | `false` |

この変更は [CHANGELOG](https://github.com/anthropics/claude-code/releases) に記載されていない。

## 対処法

VS Code の `settings.json` に以下を追加する：

```json
"claudeCode.enableNewConversationShortcut": true
