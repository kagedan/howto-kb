---
id: "2026-07-02-claudecode-aca-httpstcoaj9krogbj3-01"
title: "@ClaudeCode_aca: https://t.co/aj9krOgBJ3"
url: "https://x.com/ClaudeCode_aca/status/2072609823997505653"
source: "x"
category: "claude-code"
tags: ["claude-code", "x"]
date_published: "2026-07-02"
date_collected: "2026-07-03"
summary_by: "auto-x"
query: "Claude Code hooks 使い方 OR subagents 設定 OR Claude Code スケジュール"
---

https://t.co/aj9krOgBJ3


--- Article ---
Claude Code アカデミアです。

2,000時間以上Claude Codeを使い込んだガチ勢が集まって運営しています。

ぶっちゃけ、これを知ってるかどうかで作業効率が倍変わる。

僕らが実務で検証し尽くした内容を全部出します。

正直に言うと、**Claude Codeを「ただのコード生成ツール」として使ってる人が多すぎます**。

Anthropicの社内調査がある。132名・20万件のデータ分析で、PRマージ数が**1日あたり67%増加**。30人規模のチーム導入でも**持続的に35%の生産性向上**。

でもこれ、ただ使ってるだけじゃ出ない数字です。

僕らが2,000時間使い込んだ結論——**「1日のOS」として設計し直すと、次元が変わる**。今回はその具体的なワークフロー設計を全部出します。

![](https://pbs.twimg.com/media/HMNhy6gb0AAEA9w.jpg)

# ■ ほとんどの人が犯している「セッション設計」の致命的ミス

![](https://pbs.twimg.com/media/HMNh91laMAA4dZS.jpg)

## ▍ 1セッションに全部詰め込んでいないか？

まだ1つのセッションで朝から夕方まで全作業をやってる人、**今すぐやめてください**。

僕も最初はやってました。でもコンテキストが埋まるとClaudeの品質が落ちます。具体的にはこんなサインが出ます。

- さっき教えたファイルパスを「もう一度教えてください」と聞いてくる
- 先に述べたパターンを無視したコードを生成する
- 同じ話題について繰り返し質問してくる
**1日は「4〜6の独立したセッション」で構成する**。これが正解です。僕はこれに切り替えてから応答品質が全然違うと実感しています。

## ▍ タスク切り替え時の鉄則

僕が徹底しているルールはシンプルで、たった4つしかありません。

- **無関係なタスクに切り替えるとき**: /clearでコンテキストを完全リセット
- **中断して再開するとき**: claude --continue（直前）or claude --resume（選択）
- **セッション管理**: /rename auth-refactorで後から探せるように命名
- **並列セッションの区別**: /color redで色分け——視覚的にどのセッションか一瞬でわかります
> **2,000時間やった結論——「/clearを制する者がClaude Codeを制する」。これは冗談じゃなくマジです。**

# ■ Explore → Plan → Code → Commit——この4フェーズがすべての基本

![](https://pbs.twimg.com/media/HMNiXbjbwAAW-_N.jpg)

## ▍ なぜ「いきなりコードを書く」とダメなのか

公式が推奨する**4フェーズワークフロー**がある。僕も毎日回しています。

ぶっちゃけ、僕は最初の500時間くらい「指示→生成→修正」でやってた。でも**手戻りが多すぎて結局遅い**。

4フェーズにしてから実装時間が**体感で40%減った**。

## ▍ 4フェーズの具体的な回し方

```
# Phase 1: Explore（探索）— Plan Modeで読み取り専用
# Shift+Tab でPlan Modeに切り替え
"read /src/auth and understand how sessions work.
 also check environment variables for secrets."

# Phase 2: Plan（計画）— 設計レビュー
"I want to add Google OAuth. What files need to change?
 Create a plan. Don't implement yet."
# Ctrl+G でプランをエディタで直接編集可能

# Phase 3: Code（実装）— Plan Modeを解除して実行
"implement the OAuth flow from your plan.
 write tests, run the suite, fix any failures."

# Phase 4: Commit（記録）
"commit with a descriptive message and open a PR"
```

僕が重視してるのは**Phase 1-2に時間の60%を使うこと**。ある開発チームで
