---
id: "2026-03-23-tmux-wait-for-がai同士のオーケストレーションで便利だった-01"
title: "tmux wait-for がAI同士のオーケストレーションで便利だった"
url: "https://zenn.dev/genda_jp/articles/cfcaeeb51d23e7"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "zenn"]
date_published: "2026-03-23"
date_collected: "2026-03-24"
summary_by: "auto-rss"
---

## はじめに

株式会社GENDA 開発部エンジニアの奥山です。

Claude Code v2.1.32（2026 年 2 月 5 日）で [Agent Teams](https://code.claude.com/docs/en/agent-teams.md) が Research Preview としてリリースされました。  
以前から tmux などを活用したオーケストレーション手法が話題になっていましたが、同じような機能を公式が提供したということで話題となりました。  
独自にオーケストレーションを構成していたがこれに移行した、という方は少なくないと思います。

私も SKILL として tmux でのオーケストレーションを独自に組んでいましたが、委譲元となる Claude Code で継続してプロンプト入力をしていると委譲先から `send-keys` で送られてくる返信によって入力中のものが強制的に送信されてしまう、という問題を抱えていたため、これを機に Agent Team に移行していました。

```
# ユーザーが Claude Code にプロンプトを入力中:
> このバグを修正して_

# 委譲先の Claude Code から send-keys で到着:
> このバグを修正して調査結果: handler.go の 42 行目に nil チェック漏れ

# → 意図しない合体プロンプトとして送信されてしまう
```

しかし、設計・調査の質に関しては Codex の方が優位だと感じることが多く、これを活用したいという気持ちも依然としてありました。  
最近 GPT-5.4 や Composer2 など Claude Code 以外で扱える model も評価されていることから改めて tmux によるオーケストレーション SKILL の再構築を行っていたところ、tmux が標準搭載している `wait-for` という機能が先の問題を解決してくれることがわかりました。

## tmux wait-for とは

`tmux wait-for` はチャンネルベースのシグナリング機能です（[tmux 1.8 CHANGES](https://github.com/tmux/tmux/blob/1.8/CHANGES)）。  
`send-keys` とは違い、ターミナルへのキー入力を一切行わず tmux 内部でシグナルを送受信します。

[tmux.1](https://github.com/tmux/tmux/blob/master/tmux.1) には以下のように記載されています。

> When used without options, prevents the client from exiting until woken using wait-for -S with the same channel.

基本形は `tmux wait-for <CHANNEL>` と `tmux wait-for -S <CHANNEL>` です。前者を実行すると同じ `<CHANNEL>` に対して `-S` オプション付きのシグナルが送信されるまでロックがかかり後続処理が実行されない状態になります。

| フラグ | 動作 |
| --- | --- |
| （なし） | 指定チャンネルがシグナルされるまでブロック |
| `-S` | チャンネルにシグナルを送信（待機中の全クライアントのブロックが解除される） |

## Claude Code への応用

`tmux wait-for` を Claude Code のオーケストレーションで利用します。  
ここで重要なのが、`tmux wait-for <CHANNEL>` を**フォアグラウンドではなくバックグラウンドで実行する**という点です。  
`tmux wait-for <CHANNEL>` はブロッキングコマンドのため、フォアグラウンドで実行するとシグナルが届くまで Claude Code は一切の作業ができなくなります。

```
# Bash tool: run_in_background: true
tmux wait-for codex-orch-{SESSION_ID}-{ROLE_KEY}
```

こうすると Claude Code はブロックされず、委譲先が作業している間に自分自身もコードベースの読解や設計仮説の形成を進めることができます。委譲先が `tmux wait-for -S` を実行することで、background task の完了通知として Claude Code に届きます。  
つまり `tmux wait-for` 単体は同期的なブロッキングプリミティブですが、`run_in_background` と組み合わせることで**非同期の完了通知**として機能するようになります。

委譲先が複数ある場合でも `<CHANNEL>` を別々で用意すればそれぞれからの完了通知を非同期で受け取れます。バックグラウンドであれば複数チャンネルの `wait-for` を同時に発行でき、先に完了したものから順に結果を取得できます。

![](https://static.zenn.studio/user-upload/6c8b1ed05bb2-20260323.png)  
*3つの wait-for を実行している様子*

![](https://static.zenn.studio/user-upload/ff6d851dc079-20260323.png)  
*1つの wait-for -S が実行されて完了通知が来た様子*

## send-keys の問題が解消される理由

`wait-for` は tmux 内部のチャンネルを介したシグナリングであり、ターミナルへのキー入力を一切行いません。  
これにより、ユーザーが委譲元 pane でプロンプトを入力中であっても委譲先からのシグナルが入力に干渉することはありません。  
Enter キー送信も行われないので強制送信の問題も解決されます。

また、これは副産物的なものですが、`wait-for` + `run_in_background` の構成にしたことで委譲元自身の作業中に通知を受けても、自分の作業が完了してから確認・対応するようになりました。これにより、`wait-for` の活用が「委譲先の完了を知る仕組み」「委譲元が主導権を保ったまま非同期に待てる仕組み」に変わりました。

## オーケストレーションの流れ

これらを組み合わせた全体の流れは以下のようになります。

`tmux wait-for` はシグナリングのみを担い、データを運ぶ仕組みではありません。委譲先が調査結果をファイルに書き出してからシグナルを送り、委譲元は完了通知を受けてそのファイルを読みに行きます。

## 具体的なコマンド

各ステップで実際に実行しているコマンドを示します。`{SESSION_ID}` は一意であれば形式は問いませんが、現在はセッション開始時に `date +%s` で生成した Unix タイムスタンプを利用し、`{ROLE_KEY}` はタスクの識別子（例: `investigator-api`）を与える運用にしています。

**Launch**: 別 pane を作成し、委譲先の CLI エージェントを起動します。作業指示や完了指示テンプレートを含むプロンプトは長くなるため、事前にファイルに書き出しておき、起動時に読み込ませています。

```
tmux split-window -v -c "$PWD" \
  "codex --yolo -C $PWD 'Read /tmp/codex-orch-{SESSION_ID}-{ROLE_KEY}.prompt and follow all instructions including the completion signal.'"
```

**Wait**: `run_in_background: true` で実行し、Claude Code 自身は他の作業を続行します。

```
# Bash tool: run_in_background: true
tmux wait-for codex-orch-{SESSION_ID}-{ROLE_KEY}
```

**Read**: background task 完了通知を受け取ったら、Claude Code が自発的に結果ファイルを読みます。

## 委譲先への完了指示テンプレート

このパターンは、委譲先が作業完了時にシグナルを送ってくれることを前提としています。そのために、委譲先に渡す prompt file の末尾に以下のテンプレートを付加しています。

```
## Completion Instructions

When you have completed the task:
1. Write your final answer:
   cat <<'EOF'> /tmp/codex-orch-{SESSION_ID}-{ROLE_KEY}.output
   <your answer>
   EOF
2. Signal completion:
   tmux wait-for -S codex-orch-{SESSION_ID}-{ROLE_KEY}

Both steps are REQUIRED.
```

## SKILL の簡易例

ここまでの内容を SKILL としてまとめた簡易版を示します。  
単一の委譲先に調査を依頼して結果を受け取る最小構成にしています。

```
---
name: investigate
description: 委譲先に調査を依頼し、結果を受け取る
---

$ARGUMENTS について調査を委譲する。

## Prerequisites

`$TMUX` が未設定なら中断する。

## Step 1: SESSION_ID を生成

date +%s で生成する。

## Step 2: プロンプトファイルを書き出し

調査内容と以下の完了指示を `/tmp/orch-{SESSION_ID}-investigator.prompt` に書き出す（Write tool）。

```
## Completion Instructions

When you have completed the task:
1. Write your final answer:
   cat <<'EOF' > /tmp/orch-{SESSION_ID}-investigator.output
   <your answer>
   EOF
2. Signal completion:
   tmux wait-for -S orch-{SESSION_ID}-investigator

Both steps are REQUIRED. If the signal is not sent, the orchestrator will wait indefinitely.
```

## Step 3: pane を起動

```bash
tmux split-window -v -c "$PWD" \
  "codex --yolo -C $PWD 'Read /tmp/orch-{SESSION_ID}-investigator.prompt and follow all instructions including the completion signal.'"
```

## Step 4: バックグラウンドで待機

```bash
# Bash tool: run_in_background: true
tmux wait-for orch-{SESSION_ID}-investigator
```

待機中は自分の作業を続行する。

## Step 5: 結果を読み取り

background task 完了通知を受け取ったら、
`/tmp/orch-{SESSION_ID}-investigator.output` を Read tool で読み取り、
結果をユーザーに報告する。
```

## 今後の課題

`send-keys` の問題は回避できましたが、`wait-for` ベースの構成にも課題が残っています。

### サンドボックスと tmux ソケットの制約

Codex CLI を `--full-auto` モードで起動すると、サンドボックスが tmux ソケットへのアクセスをブロックします。委譲先が `tmux wait-for -S` を実行できずシグナルが送れない状態になるため、筆者の環境では `--yolo` (`--dangerously-bypass-approvals-and-sandbox`) で回避させています。  
セキュリティ上のトレードオフがあるため注意が必要です。

### 委譲先がシグナルを送らなかった場合のリカバリ

このパターンは、委譲先が完了指示に従って `tmux wait-for -S` を確実に実行することを前提としています。しかし実際には、委譲先が指示を無視したりエラーが起きたりしてシグナルを送らないケースがあります。

tmux にある別の機能の活用、Claude Code の `/loop` や Stop Hook の活用、Codex の notify の活用、など対処法はありそうなので、調べておこうと思います

<https://code.claude.com/docs/en/hooks>

<https://developers.openai.com/codex/config-advanced>

### Claude Code が終了した場合のリカバリ

委譲先の pane は独立したプロセスなので、委譲元の Claude Code が終了しても生き続けます。しかし、委譲先が `wait-for -S` でシグナルを送った時点で待機者がいないため空振りになります。

`/resume` で Claude Code を復帰させた場合、結果ファイル（例: `/tmp/codex-orch-{SESSION_ID}-{ROLE_KEY}.output`）が残っていれば読み取ることはできますが、`wait-for` による通知の流れは途切れているため、ファイルの存在確認から再開する形になります。この resume 後のリカバリパターンはまだ確立できていません。

## まとめ

`tmux wait-for` を `run_in_background` と組み合わせることで、`send-keys` のドッキング問題を解消し、ターミナル入力に干渉しない非同期の完了通知を実現できました。

一方でオーケストレーションとしての課題はまだ残っています。`wait-for` は完了通知の仕組みとしては機能しますが、それだけで堅牢なオーケストレーションが完成するわけではなく、周辺の仕組みを含めて引き続き改善していきたいと考えています。
