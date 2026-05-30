---
id: "2026-05-29-sin5d-claude-codeのdynamic-wokflowsgrok君も参加させられないかな-01"
title: "@sin5d: Claude CodeのDynamic Wokflows、Grok君も参加させられないかなって試してみたらすんなり出来た"
url: "https://x.com/sin5d/status/2060248747062493673"
source: "x"
category: "claude-code"
tags: ["claude-code", "AI-agent", "x"]
date_published: "2026-05-29"
date_collected: "2026-05-30"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

Claude CodeのDynamic Wokflows、Grok君も参加させられないかなって試してみたらすんなり出来た
同じ感じでヘッドレスで動作できるコーディングエージェントならいけるんじゃないかな
大雑把にGrokで調査した内容をOpusで深堀りしてCodexで精査、Grok Imagineでグラフ画像作成みたいな分業もできそう https://t.co/MAR8kDfnvZ

あかんかった
https://t.co/RbV2emilpu

いやほんといっぱい閲覧もらってる所申し訳ないんですけど、これ動きませんでしたのでご注意くださいね。。
Dynamic Workflow の外ならgrok -pで呼び出し出来ますんで


--- 引用元 @oikon48 ---
Claude Code の新機能 「Dynamic Workflows」

Claudeが自分でオーケストレーション（指揮）スクリプトを書き、1つのセッション内で数十〜数百の並列サブエージェントを動かす。

【使い方】

/config の "Dynamic workflows" が trueになっていることを確認し、以下のような指示を出す

「ワークフローを作って（Create a workflow）」

ワークフローが起動すると、Claudeはプロンプトに基づいて動的に計画を立て、サブタスクに分解し、並列稼働するサブエージェントに作業を振り分ける。
Agent Teamsのようにエージェントが独立した複数の角度から問題に取り組み、別のエージェントがその発見を反証しようとし、答えが収束するまで反復し続ける点が取り上げられている。

長時間(数時間〜数日に及ぶ)・並列の作業向けに作られており、途中で中断しても進捗が保存されているため最初からやり直さずに再開可能。

ざっくり使ってみた感じはAgent Teamsの強化版という印象。タスクの整合性を事前にしっかりスクリプトで作成しているので、大規模タスクに向いてそう。

(ちなみに "workflow" は ultrathink みたいに虹色に光る)

Introducing dynamic workflows in Claude Code

https://t.co/eaxo0FtqFj
Dynamic workflows について↓

https://t.co/Aw92BMpd7X
