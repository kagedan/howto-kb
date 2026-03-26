---
id: "2026-03-25-超個人的なclaudecodeのsettingsjsonの設定2026325時点-01"
title: "超個人的なClaudeCodeのsettings.jsonの設定（2026/3/25時点）"
url: "https://qiita.com/TatApp/items/1f2feeb5ac2a785dcbd7"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-03-25"
date_collected: "2026-03-26"
summary_by: "auto-rss"
---

## はじめに

Claude Code を使い始めて、毎回権限の確認ダイアログが出たり、処理が終わっても気づかなかったりと、使用している上でネックだった部分があったので、グローバル設定（`~/.claude/settings.json`）を整理しました。

完全に個人の好み全開の設定ですが、誰かの参考になれば。

## 設定ファイルの場所

```
%USERPROFILE%\.claude\settings.json
```

Windows の場合は `C:\Users\<ユーザー名>\.claude\settings.json` です。

## 全体像

```json
{
  "permissions": {
    "allow": [
      "Bash",
      "Read",
      "Edit",
      "Write",
      "Glob",
      "Grep",
      "WebFetch",
      "WebSearch"
    ],
    "deny": [
      "Bash(rm -rf *)",
