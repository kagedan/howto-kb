---
id: "2026-07-02-oikon48-claude-fable-5-にプランさせてopus-48-や-sonnet-5で実-01"
title: "@oikon48: Claude Fable 5 にプランさせて、Opus 4.8 や Sonnet 5で実行する手法で、個人的には以下が今"
url: "https://x.com/oikon48/status/2072599526771421364"
source: "x"
category: "claude-code"
tags: ["prompt-engineering", "AI-agent", "x"]
date_published: "2026-07-02"
date_collected: "2026-07-03"
summary_by: "auto-x"
query: "Claude Code hooks 使い方 OR subagents 設定 OR Claude Code スケジュール"
---

Claude Fable 5 にプランさせて、Opus 4.8 や Sonnet 5で実行する手法で、個人的には以下が今のところしっくりきた

・サブエージェントをFable以外に固定（CLAUDE_CODE_SUBAGENT_MODEL）
・システムプロンプトにFable運用用の指示を追記（--append-system-prompt）

例)
CLAUDE_CODE_SUBAGENT_MODEL=claude-sonnet-5 claude --append-system-prompt "基本的にタスクや作業の実行は、適切な粒度でsubagentsに実行手順が明確な指示を与えて委譲すること。あなたは全体進行の俯瞰と立案を行う。自己判断による例外は認める"

CLAUDE/.md やルールファイルと違って、簡単で設定をクリーンに保てるので、Fable 5が期間限定である限りしばらくはこれを試してみる
