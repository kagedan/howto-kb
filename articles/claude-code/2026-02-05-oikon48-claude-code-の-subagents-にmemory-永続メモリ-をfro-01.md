---
id: "2026-02-05-oikon48-claude-code-の-subagents-にmemory-永続メモリ-をfro-01"
title: "@oikon48: Claude Code の Subagents に、memory (永続メモリ) をFrontmatterで設定できるよ"
url: "https://x.com/oikon48/status/2019370311238709534"
source: "x"
category: "claude-code"
tags: ["claude-code", "AI-agent", "x"]
date_published: "2026-02-05"
date_collected: "2026-03-19"
summary_by: "auto-x"
---

Claude Code の Subagents に、memory (永続メモリ) をFrontmatterで設定できるようになりました。

e.g.)
---
name: code-reviewer
description: Review code
memory: user
---
 
.claude/agent-memory/<name-of-agent> のディレクトリに、Subagentsはメモリを書き込むことで知識を蓄積することができます。
 
Scope:
・user
・project
・local

３種類あり、これらは /agents コマンドを実行してSubagentsを作成する際にも指定することが可能です。

以下のようなコンテキストをSubagentsの設定ファイルに含めることで、Subagentsが能動的に知識のアップデートをしてくれるとのこと。
 
```md
**Update your agent memory** as you discover codepaths, patterns, library locations, and key architect
