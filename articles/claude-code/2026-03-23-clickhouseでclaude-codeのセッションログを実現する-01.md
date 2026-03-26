---
id: "2026-03-23-clickhouseでclaude-codeのセッションログを実現する-01"
title: "ClickHouseでClaude Codeのセッションログを実現する"
url: "https://qiita.com/skillogy/items/23b8f09f203ba3bbb834"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "qiita"]
date_published: "2026-03-23"
date_collected: "2026-03-26"
summary_by: "auto-rss"
---

## Claude Codeはセッションをまたげない

Claude Codeを使い込んでいる開発者なら、一度はこう思ったことがあるはずです。

「昨日のセッションの続きから再開したいのに、コンテキストが全部消えている」

Claude Codeには`~/.claude/`配下にMarkdownベースのメモリ機能がありますが、これは手動で「覚えて」と指示する必要があり、作業の全体像を自動的に保持するものではありません。

そこで本記事では、Claude CodeのHooks機能を使ってセッションの内容をClickHouseに自動蓄積し、新しいセッション開始時に前回の作業内容を自動で注入する仕組みを構築します。

## 全体像

```
【記録フェーズ：セッション中に自動実行】
Claude Code
  ├─ UserPromptSubmit hook → ユーザーの指示を記録
  ├─ PostToolUse hook      → ファイル編集・コマンド実行を記録
  └─ Stop hook             → Claudeの応答を記録 + セッション要約を生成
