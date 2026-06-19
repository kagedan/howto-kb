---
id: "2026-06-18-manager-ojisan-claude-codeにはhooksという機能があるsettingsj-01"
title: "@manager_ojisan: Claude Codeには「Hooks」という機能がある。settings.jsonにコマンドを書くと、特定の操作の前後"
url: "https://x.com/manager_ojisan/status/2067541501656355208"
source: "x"
category: "claude-code"
tags: ["claude-code", "x"]
date_published: "2026-06-18"
date_collected: "2026-06-19"
summary_by: "auto-x"
query: "Claude Code hooks 使い方 OR subagents 設定 OR Claude Code スケジュール"
---

Claude Codeには「Hooks」という機能がある。settings.jsonにコマンドを書くと、特定の操作の前後に自動でスクリプトが走る。コミット前のチェックに使い始めてから、見落としが減った。↓

具体的な仕様。PreToolUse/PostToolUseなどのイベントにシェルコマンドを紐付ける。例：ファイル保存前に構文チェック、コミット前に機密文字列スキャン、実行後にログ記録。全部settings.jsonの数行で済む。

実務での使い方。git commitの前にシークレットキーの混入を検知するスクリプトを走らせている。人間が確認し忘れても、Hookが止めてくれる。「忘れ」をアーキテクチャで潰す発想。

HooksはAI操作の文脈に確認トリガーを埋め込む仕組み。知っているかどうかで使い方の深さが変わる。Claude Codeを使っている方、Hooksは活用していますか？
#ClaudeCode #AIエージェント #開発効率
