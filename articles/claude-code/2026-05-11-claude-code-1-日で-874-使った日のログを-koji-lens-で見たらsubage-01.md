---
id: "2026-05-11-claude-code-1-日で-874-使った日のログを-koji-lens-で見たらsubage-01"
title: "Claude Code 1 日で $874 使った日のログを koji-lens で見たら、subagent経由Bashが68%だった"
url: "https://zenn.dev/kojihq/articles/2c211edbf84727"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "zenn"]
date_published: "2026-05-11"
date_collected: "2026-05-12"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Code を毎日使っていると、「結局どのくらいコストかかってるんだろう」「ヘビーに使った日は何にリソースが流れてるんだろう」という疑問が浮かびます。Anthropic Console は月次の合計を見せてくれますが、「今日の 24 時間で何にいくら使ったか」「どのツール呼び出しが重かったか」までは降りてきません。

`/usage` コマンドはセッション単位の合計を出してくれますが、複数セッションを束ねた時間軸 (1 日 / 1 週間) や、ツール別 (Bash / Edit / Read) の内訳は見えません。

この「降りてこないところ」をローカル JSONL から取り出すために、`@kojihq/lens` という CLI を作って npm に公開しました。本記事では、自分の **集中作業日 (2026-04-27 → 2026-04-28 の 24 時間)** のログを `koji-lens` で見たときに気づいた数字を共有します。普段の 1 日ではなく「集中して開発に張り付いた日」のスナップショットです。

## 過去 1 日のコストを見てみる

`koji-lens summary --since 24h` を叩くと、直近 24 時間の集計が出ます。

```
$ koji-lens summary --since 24h
koji-lens — analyzed 15 session(s)
period: 2026-04-27 15:00 → 2026-04-28 15:00 local (last 24h)
============================================================
TOTAL
  sessions:       15
  duration (sum): 16h 24m 10s
  turns:          assistant=1622, user=833, sidechain=100
  tokens:         input=133,976, output=2,855,592, cache_read=353,399,039, cache_create=7,356,247
  cost:           $874.1162 (¥135,488)
  cost by model:  claude-opus-4-7=$865.4523, claude-sonnet-4-6=$8.6639
  tools:          Bash×238, Edit×194, Read×179, TaskUpdate×72, Write×55, TaskCreate×37, Grep×30, Glob×18, Agent×8, ToolSearch×3
  models:         claude-opus-4-7×1562, claude-sonnet-4-6×60

  note: Cost is API-rate equivalent (token × Anthropic API price).
        Actual billing depends on your plan — Claude Pro / Max
        subscribers pay a flat fee regardless of this number.
============================================================
```

24 時間で **$874 (API 換算)**。Claude Pro / Max のサブスクで使っているので実請求はサブスク料金（$20 / $200）固定ですが、API レート換算では $874 分のリソースが動いていたことになります。

「重い 1 日」と書きましたが、自分にとっては「集中作業した 1 日」程度の感覚で、特別異常な使い方をした日ではありません。それでも 24h で $874 は予想を超えていました。

## 一番重い数字: subagent 経由 Bash 呼び出しが 68%

注目したいのは `tools` の行です。

```
tools: Bash×238, Edit×194, Read×179, TaskUpdate×72, Write×55, TaskCreate×37, Grep×30, Glob×18, Agent×8, ToolSearch×3
```

Bash が 238 回。総ツール呼び出し回数で見ると 1 位です。さらに、これらのツール呼び出しを **メインセッション vs subagent** で分解すると、**Bash 呼び出しの 68% が subagent 経由** でした。

つまり、自分が `Agent` を 8 回使った中で、その配下で subagent が走らせた Bash 呼び出しがメインセッション直接の Bash よりも多い、という構図です。`Agent` 1 回起動するごとに、subagent が平均 30 回ほど Bash を叩いている計算になります。

これは `/usage` には出ません。`/usage` は session 単位の入出力トークン合計を出すだけで、ツール呼び出し内訳までは降りてきません。Anthropic Console も同様で、月次合計とプロジェクト別概要までは見えますが、ツール別 / subagent vs メインセッション分解は見えません。

「降りてこないところ」が、ここでした。

## どう使うか

この数字が見えると、行動が変わります。

* **subagent 起動の重さを認識**: `Agent` を起動するときのコストが、メインで Bash を直接叩く場合の数十倍になることがわかる
* **モデル選択の判断材料**: subagent も Opus を使うので、軽い処理なら Sonnet 指定で動かす指針になる
* **改善追跡**: 来月同じ作業をして 68% → 50% に下がったら、subagent 起動を減らした効果が数字で見える

3 番目が特に大きいです。`koji-lens` には `compare` サブコマンドがあって、「先週」と「今週」を比較した差分が出るので、「自分の使い方が改善しているか」をログから直接確認できます。

## ccusage との関係

[ccusage](https://github.com/ryoppippi/ccusage) を既に使っている方は、`koji-lens` も同じ `~/.claude/projects/**/*.jsonl` を読んでいることに気づくと思います。**読むファイルは同じ** で、両方並行運用できます。差分は per-tool breakdown / subagent vs メインセッション分解 / Web ダッシュボード同梱 / SQLite キャッシュ。ccusage が per-project の集計を nail しているなら、その上にツール別 / エージェント別の breakdown を重ねる関係です。

## 試す

```
npm install -g @kojihq/lens
koji-lens summary --since 24h
```

Node 22+ が必要です。100% ローカル、サインアップ不要、テレメトリなし、MIT ライセンス。

数字フックは「24h で $874」と「月次で $8,833」の 2 つあります。前者はある重い 1 日のスナップショット、後者は 1 ヶ月通した平均的なヘビーユース。両方とも自分の実データで、サブスク料金固定で使っているので「これだけ API 換算で価値が動いていた」という観測です。

何か気づきや質問があれば、Bluesky `@kojihq.com` か X `@kojihq_jp` まで。
