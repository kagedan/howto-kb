---
id: "2026-05-18-claude-code-の-token-を節約する-5-つのコツ-実データで検証-01"
title: "Claude Code の token を節約する 5 つのコツ (実データで検証)"
url: "https://zenn.dev/kojihq/articles/3ef8b697063323"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "prompt-engineering", "API", "AI-agent", "zenn"]
date_published: "2026-05-18"
date_collected: "2026-05-19"
summary_by: "auto-rss"
query: ""
---

## はじめに

Pro / Max サブスクは flat fee なので体感少ないですが、  
API ユーザーは token 使用量がコスト直結です。

Anthropic 公式の `/usage` では cache 効率や tool 別パターンまでは見えないので、自分の 18 日間 266 sessions のログを集計したところ、節約に効くポイントがいくつか見えてきました。  
本記事ではそれを 5 つのコツとして共有します。

数字は手元の `~/.claude/projects/` 配下の JSONL ログから集計した実測値です。

## コツ 1: cache\_read を最大化する

Claude Code の API token 構成は  
`input` + `output` + `cache_read` + `cache_create` の 4 種類。  
このうち **cache\_read は単価が他の約 1/10** で、再利用すればするほど安くなります。

実データ検証 (18 日間累計):

* 累積 token 合計: 8,784,272,475
* うち cache\_read: 8,460,081,782 = **96.3%**
* input: 0.02% / output: 0.5% / cache\_create: 3.1%

ほとんど cache\_read で回っています。

cache\_read 最大化のコツ:

* 同じファイルや context を 1 session 内で繰り返し参照する (2 回目以降は cache hit)
* session を頻繁に切らない (新 session = cache reset)
* CLAUDE.md / system prompt など共通 context は活性維持

## コツ 2: モデル動的選択を信頼する (API ユーザー向け)

Claude Code は内部で task complexity 判定して opus / sonnet / haiku を自動選択する設計です。

実データ検証 (18 日間 cost 内訳):

* claude-opus-4-7: $20,745 = **98.5%**
* claude-haiku-4-5: $233 = 1.1%
* claude-sonnet-4-6: $79 = 0.4%

「動的選択」と聞いていましたが、実態は opus 一辺倒でした。  
sonnet / haiku はサブ的な役割 (軽量タスク / subagent 用と推測)。

Pro / Max サブスクユーザーは flat fee なので「opus を使い倒している」 = 最適戦略。  
API ユーザーは opus 比率を抑える設定 (model hint や明示指定) で大幅コスト削減余地があります。

実データ検証 (18 日間 tool 呼び出し top 4):

* Bash: 4,955 回
* Read: 3,957 回
* Edit: 3,883 回
* TaskUpdate: 1,619 回

Claude Code は「コードリーディング + Bash 実行 + 編集 + タスク管理」のパターン。  
シェル操作と読み込みが圧倒的に多く、Write (新規ファイル作成) は Edit の約 1/5 です。  
既存コードへの増分編集中心の使用パターンが見えます。

無駄な tool 呼び出し (大量 Grep 連発、同一 Read 繰り返し、効果薄い WebFetch 連打など) を削減すると token 節約に直結します。

## コツ 4: subagent ネストを最小化する

subagent 起動 = 親 context + 子 context で重複部分が token 倍増します。  
深いネスト (depth 3 以上) はさらに倍々ゲーム。

subagent は「主タスクから独立 + 並列で価値ある」場合のみ使う。  
安易な「とりあえず subagent」は token 浪費になります。

## コツ 5: 長時間 session を分割する

session の context window が膨らむと、古い context が排出されて cache\_read 効率が低下します。  
1 〜 2 時間で session を切る (`/clear` か新 session) のが cache 効率最適化に効きます。

集中作業で 8 時間連続 session を続けると、後半で cache miss が急増し、cache\_create token 量が前半の 2 〜 3 倍になる傾向が観察できました。

## まとめ + 確認方法

5 つのコツの実証は自分の `~/.claude/projects/` 配下の JSONL ログから集計可能です。  
手動 grep でも追えますが、自前で集計するのは手間なので CLI を自作して OSS で公開しています:

* `koji-lens summary --since 7d` = cache 比率 + cost 比率を 1 行表示
* `koji-lens tools --since 7d` = tool 別 invocation 数 + 比率 + バーグラフ

OSS / MIT、`npm i -g @kojihq/lens@beta`、リポジトリは <https://github.com/etoryoki/koji-lens> です。

質問や感想あれば GitHub Discussions か本記事のコメントで。
