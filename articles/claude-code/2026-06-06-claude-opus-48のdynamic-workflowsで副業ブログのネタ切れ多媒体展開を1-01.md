---
id: "2026-06-06-claude-opus-48のdynamic-workflowsで副業ブログのネタ切れ多媒体展開を1-01"
title: "Claude Opus 4.8のDynamic Workflowsで、副業ブログの「ネタ切れ＋多媒体展開」を1プロンプトに畳む設計案"
url: "https://zenn.dev/jun_eng/articles/4cf7f715f1dc3f"
source: "zenn"
category: "claude-code"
tags: ["AI-agent", "zenn"]
date_published: "2026-06-06"
date_collected: "2026-06-07"
summary_by: "auto-rss"
query: ""
---

* 2026/5/28リリースのClaude Opus 4.8は `Effort Control` と `Dynamic Workflows` を搭載
* subagentの並列実行で「ネタ収集 → note記事 → Zenn記事」を1プロンプトに統合する設計案
* 筆者は副業ブログ運営者で、まだ結果は出していない。これから運用に乗せる構成の共有  
  :::

## 背景：副業ブログの2大ペイン

副業でnote / Zennを並走運営しようとすると、技術記事を毎日出す前に2つの壁にぶつかります。

1. **ネタ切れ**：本業の合間にX / Hacker News / Redditを巡回するのが重い
2. **多媒体展開**：1テーマをnote用・Zenn用・X用に書き分ける手間

このコストを毎日払うのは現実的に厳しく、自動化の設計を考えました。

## Claude Opus 4.8 の新機能まとめ

2026年5月28日にリリースされたOpus 4.8では、副業ブログ運営に直結しそうな新機能が2つ入っています。

| 機能 | 概要 | 副業ブログでの使い所 |
| --- | --- | --- |
| Effort Control | 思考の深さをユーザーが指定可能 | タイトル生成だけ`high`に振る |
| Dynamic Workflows | 1セッションで数百のsubagentを並列実行 | ネタ収集 / note執筆 / Zenn執筆を同時走行 |
| Fast mode | 2.5倍速、従来比約1/3の価格 | 朝の確認サイクルが軽い |

価格は入力 $5 / 出力 $25 (per 1M tokens) で4.7と据え置きです。

## 設計：3つのsubagentを並列で走らせる

実装といっても、プロンプトを1本書くだけです。

* subagent A：`research` (effort=low) — 過去24hのX / HN / Redditからトレンド3件
* subagent B：`note-writer` (effort=high) — 3200〜3500字、です/ます調、見出しは##
* subagent C：`zenn-writer` (effort=medium) — frontmatter付き、テーブル記法、`:::message`

ポイントは「同じテーマで2媒体を同時生成する」こと。  
ネタを1回拾えば、note向け文体とZenn向け文体に分岐するだけで2本完成する想定です。

## プロンプト本体（再利用可）

```text  
You are an editor for a side-job blog.  
Run the following in parallel subagents.

[subagent A: research, effort=low]

* Extract 3 trending topics about AI x side-job  
  from X / Hacker News / Reddit (last 24h)

[subagent B: note-writer, effort=high]

* Pick 1 theme from A and write a 3200-3500 char note article
* Pick the best title from 9 hook patterns
* Use Japanese desu/masu tone, ## headings, "・" bullets

[subagent C: zenn-writer, effort=medium]

* Write a Zenn article on the same theme
* Include YAML frontmatter
* Use ":::message" for TL;DR, tables for comparisons
* No "・" — use "-" only  
  ```

## 期待する効果（実測ではなく想定）

| 工程 | 想定の従来工数 | 自動化後の想定 |
| --- | --- | --- |
| ネタ収集 | 60分 | 数分 |
| note執筆 | 120分 | 数分 |
| Zenn変換 | 60分 | 数分 |

実測は運用に乗せてから別途記事化する予定です。

## 注意点：人間が残すべき工程

完全自動化に振り切ると、AI臭い記事が量産されやすいと想定しています。  
このため、人間側で必ず残す工程を2つ決めました。

* タイトル最終決定（生成された候補から自分で選ぶ）
* 冒頭3行の手直し（フックは自分の言葉でないと刺さらない）

ここを残すかどうかで、滞在時間が大きく変わると予想しています。

## まとめ

* Opus 4.8の `Dynamic Workflows` は「並列subagent」が本体
* `Effort Control` で品質メリハリ：タイトルだけhighに振るのが効きそう
* 副業ブログは「機械に任せる工程」と「人間が残す工程」の分業設計が9割
