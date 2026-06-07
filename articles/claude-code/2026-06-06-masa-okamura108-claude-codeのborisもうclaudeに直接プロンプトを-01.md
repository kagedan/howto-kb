---
id: "2026-06-06-masa-okamura108-claude-codeのborisもうclaudeに直接プロンプトを-01"
title: "@masa_okamura108: Claude CodeのBoris「もうClaudeに直接プロンプトを書くより、仕事を回すループを書く」 実際にどんなル"
url: "https://x.com/masa_okamura108/status/2063395534866637010"
source: "x"
category: "claude-code"
tags: ["claude-code", "x"]
date_published: "2026-06-06"
date_collected: "2026-06-07"
summary_by: "auto-x"
query: "Claude Code hooks 使い方 OR subagents 設定 OR Claude Code スケジュール"
---

Claude CodeのBoris「もうClaudeに直接プロンプトを書くより、仕事を回すループを書く」
実際にどんなループを書いているのか？を調べたら凄かった。
これは自社にも取り入れる一択。

# まずループとは？
/loopコマンド（スケジュールされた自動実行ループ）：Claude Codeの機能として実装されたcron-likeな機能。

/loop [間隔] [プロンプト or /コマンド] で、定期的にClaudeにタスクを投げて自動実行させる。

# 最大3日（またはそれ以上） unattended（人間介入なし）で動き続ける。

# Boris本人の実例：

/loop 5m /babysit：PRのコードレビュー自動対応、rebase、productionまでshepherd。

/loop 30m /slack-feedback：Slackフィードバックを自動でPR化。

/loop 1h /pr-pruner：古いPRを自動クローズ。

他にもpost-merge sweeperなど複数常時稼働。
