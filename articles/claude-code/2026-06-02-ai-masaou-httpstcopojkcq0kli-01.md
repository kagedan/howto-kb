---
id: "2026-06-02-ai-masaou-httpstcopojkcq0kli-01"
title: "@AI_masaou: https://t.co/poJkCq0kLI"
url: "https://x.com/AI_masaou/status/2061916297810903539"
source: "x"
category: "claude-code"
tags: ["claude-code", "AI-agent", "JavaScript", "x"]
date_published: "2026-06-02"
date_collected: "2026-06-03"
summary_by: "auto-x"
query: "Claude Code hooks 使い方 OR subagents 設定 OR Claude Code スケジュール"
---

https://t.co/poJkCq0kLI


--- Article ---
タスクを 1 つの Claude に丸ごと任せると、途中で力尽きたり、最初の目的を見失ったりする。Claude Code の「動的ワークフロー」は、その仕事を複数の Claude に分担させる段取りを、Claude 自身が JavaScript でその場で書く新機能だ。2026 年 5 月公開、まだ研究プレビューの段階にある。

## TL;DR

1. Claude が「補助の Claude を何体も並べて動かす段取り」を、タスクごとにその場で書く新機能。
1. 狙いは、1 つの頭に詰め込むと起きる「やりきらない・自分びいき・目的ズレ」を分担で防ぐこと。
1. 強力だがトークンを多く食う。並列で構造的な大仕事 — 調査・レビュー・移行 — でこそ効く。
https://youtu.be/shyzjdtVxpchttps://youtu.be/shyzjdtVxpc

> まだWorkflowsを知らない方は、ぜひ上記の動画を見てみてください

## 全体像  段取りを Claude がその場で書く

ふつうの Claude Code はコーディング用の段取りで固定されている。動的ワークフローは、その段取りをタスクごとに書き換える。

![](https://pbs.twimg.com/media/HJ1jToybUAAm_c-.jpg)

動的ワークフローの正体は、Claude が書く 1 つの JavaScript ファイルだ。その中で Claude は、補助の Claude (= サブエージェント) を何体も起動し、連携させる。ループも分岐も中間結果も、その JavaScript が抱える。

鍵は「ハーネス」という考え方にある。ハーネス (= タスクを解くための段取り・足場) は、ふつうの Claude Code ではコーディング向けに固定されている。動的ワークフローでは、Claude が目の前のタスクに合わせてハーネスをその場で書く。

段取りを組むための専用関数が用意されている。代表的なものは次の 4 つだ。

![](https://pbs.twimg.com/media/HJ1jYp-a0AA3fwe.jpg)

> エージェントごとに使うモデル (Sonnet / Opus) や、worktree (= git の作業コピーを分けた隔離環境) で動かすかを、Claude 自身が選べる。中断してもセッションを再開すれば続きから走る。

## なぜ必要か — 1 つの頭に詰め込むと出る 3 つの綻び

計画も実行も 1 つの頭でこなすと、長く複雑な仕事ほど決まった綻びが出る。

![](https://pbs.twimg.com/media/HJ1jgpiasAAuKiV.jpg)

既定のハーネスは、計画と実行を 1 つの context window (= Claude が一度に覚えていられる作業メモの広さ) でこなす。短いコーディングなら、これがいちばん強い。だが長時間・大量並列・敵対的なタスクになると崩れやすい。

崩れ方には決まった型がある。長く居続けるほど、次の 3 つが出やすくなる。

![](https://pbs.twimg.com/media/HJ1jo3EbIAA3fiq.jpg)

対策はシンプルだ。別々の context window を持つ複数の Claude に、焦点を絞った目的を 1 つずつ渡す。1 体の担当範囲が狭いので、たとえ怠けても自分の答えを甘く見ても、全体までは崩れない。

> compaction (= 会話が長くなったとき過去を要約して圧縮する処理) は、要約のたびに少しずつ情報が欠ける。エッジケースや「やるな」の指示ほど、ここで抜けやすい。

## 動的 vs 静的 — オーダーメイドか、既製品か

複数の Claude を連携させること自体は前からあった。違いは「段取りをいつ、誰が書くか」だ。

複数の Claude を連携させる発想は新しくない。Claude Agent SDK や claude -p で前から組めた。これが「静的ワークフロー」だ。

静的は、あらゆる場合に備える必要があるので汎用的になりがちだ。言い換えれば既製品の段取りである。動的は、Opus 4.8 が賢くなったことで、その都度タスク専用の段取りを書けるようになった。

![](https://pbs.twimg.com/media/HJ1jyDUbkAAeJhk.jpg)

静的が劣るわけではない。何度も回す定型処理は静的が向く。動的の強みは、二度と来ないかもしれない 1 回きりのタスクにも、専用の段取りを
