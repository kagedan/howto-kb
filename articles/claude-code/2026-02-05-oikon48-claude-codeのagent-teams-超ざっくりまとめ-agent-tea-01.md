---
id: "2026-02-05-oikon48-claude-codeのagent-teams-超ざっくりまとめ-agent-tea-01"
title: "@oikon48: 【Claude CodeのAgent Teams 超ざっくりまとめ】"
url: "https://x.com/oikon48/status/2019533240537878581"
source: "x"
category: "claude-code"
tags: ["claude-code", "AI-agent", "x"]
date_published: "2026-02-05"
date_collected: "2026-03-19"
summary_by: "auto-x"
---
【Claude CodeのAgent Teams 超ざっくりまとめ】
 
・Agent Teams とは: 
チームリーダーがタスクを割り振り、チームメイトが独立したコンテキストウィンドウで作業し、相互にメッセージ送受信できる
 
・Subagents との違い: 
Subagents は1つのセッション内で動き結果を返すだけだが、Agent Teams はエージェント間の並列通信が可能
 
・有効化方法: CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
 
・２種の表示モード: 
in-process (メインターミナル内)
split panes (tmux/iTerm2 で分割表示）
 
・タスク管理:
共有タスクリストでチームメイトがタスクを自己割当て・完了管理
 
・ユースケース: 
並列コードレビュー、仮説対決型デバッグえ、新機能の並列開発
 
・制限事項: 
セッション再開不可、タスク状態の遅延、ネストされたチーム不可等
