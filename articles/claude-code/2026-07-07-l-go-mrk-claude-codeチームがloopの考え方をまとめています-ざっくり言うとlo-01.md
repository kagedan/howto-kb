---
id: "2026-07-07-l-go-mrk-claude-codeチームがloopの考え方をまとめています-ざっくり言うとlo-01"
title: "@L_go_mrk: Claude Codeチームが「loop」の考え方をまとめています。 ざっくり言うと、loopは「停止条件を満たすまで"
url: "https://x.com/L_go_mrk/status/2074418392736649459"
source: "x"
category: "claude-code"
tags: ["claude-code", "AI-agent", "x"]
date_published: "2026-07-07"
date_collected: "2026-07-08"
summary_by: "auto-x"
query: "Claude Code hooks 使い方 OR subagents 設定 OR Claude Code スケジュール"
---

Claude Codeチームが「loop」の考え方をまとめています。

ざっくり言うと、loopは「停止条件を満たすまで、Agentが作業サイクルを繰り返すこと」。

種類は大きく4つ。

Turn-based: 人間が毎回プロンプトで進める
Goal-based: 完了条件を渡して、達成まで回す
Time-based: 時間間隔やスケジュールで回す
Proactive: イベントや定期実行で、人間不在でも定義済み作業を回す

重要なのは、いきなり複雑な自動化にしないこと。

まずは「何を手放すのか？」を決める。

確認作業を手放すならSkill。
停止判断を手放すなら /goal。
起動タイミングを手放すなら /loop や /schedule。

AIに仕事を渡すほど、プロンプト単体より「検証方法」「停止条件」「使用量の境界」が効いてきます。


--- 引用元 @ClaudeDevs ---
https://t.co/v694m8Eaj6
