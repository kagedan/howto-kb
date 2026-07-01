---
id: "2026-07-01-kurono-ai-ura-httpstcomnfi8bngde-01"
title: "@kurono_ai_ura: https://t.co/MnFi8bnGDe"
url: "https://x.com/kurono_ai_ura/status/2072264487164662098"
source: "x"
category: "claude-code"
tags: ["claude-code", "x"]
date_published: "2026-07-01"
date_collected: "2026-07-02"
summary_by: "auto-x"
query: "Claude Code hooks 使い方 OR subagents 設定 OR Claude Code スケジュール"
---

https://t.co/MnFi8bnGDe


--- Article ---
Claude Codeを使ってるのに、毎回「許可しますか？」への解答を自分で押してる。フォーマットも手動。PCに張り付いてる。

**それ、全部自動にできます。**

AI×SNSで7,000万マネタイズ。放置で月300万。Claude Code 1,500時間超え。僕が断言する。

「hooks」を設定するだけ。Claude Codeが別物になる。数行書くだけ。プログラミングも不要。

![](https://pbs.twimg.com/media/HMIpgH3aQAANX6y.jpg)

> **AIエージェントでの稼ぎ方はこちら👇

[>> くろのの公式LIN**E](https://utage-system.com/line/open/29eSgDJcxiWv?mtid=YdgBFzRGGHTL)

# Claude Codeを「手動」で使ってる人、まだそんなことやってるの？

## 毎回「許可しますか？」を押すのは設定を知らないだけ

Claude Codeでファイル編集するたび「許可しますか？」が出る。コマンド実行でも出る。あれ、毎回自分で押してませんか？

1タスクで10回、20回。ポチポチ押すだけで5分飛ぶ。**1日30分以上を「許可ボタン」に消えてます。** 1ヶ月で15時間のロス。

hooksを使えば一発で解決する。安全な操作は自動許可になる。ボタンを押す必要がなくなる。**最初の1回だけ設定すれば終わります。**

## hooks設定済みの人は「寝てる間にコードが完成」してる

hooks設定済みの人は全然違う。指示を出したらPCから離れる。完了したらSlackやDiscordに通知が飛ぶ。**画面を見張る必要がゼロになる。**

僕もAIエージェント100体以上を回してます。やることは承認ボタンだけ。手動で確認する時間がゼロになった。

朝起きたらコード完成。通知を見て承認する。**それだけで月300万が回ってます。** hooksを知ってるかどうかで、生産性が10倍変わる。

## この記事で、今日からClaude Codeが別物になる

![](https://pbs.twimg.com/media/HMIoC5Nb0AAWVNZ.jpg)

「hooks」は難しくない。ファイル1つ書くだけ。

- プログラミング知識は不要
- この記事のJSONをコピペでOK
- 即日で全自動化できる
- 設定にかかる時間は10分
**最高の設定を全部公開します。** 一気に持っていってください。Claude Codeの使い方が根本から変わる。知ってるだけで周りと圧倒的な差がつきます。

# hooks = ツール実行の前後に処理を差し込む仕組み

## 12種類あるけど最初はこの4つだけ

hooksには12種類のイベントがある。全部覚える必要はない。

最初に設定すべきは4つだけ。

![](https://pbs.twimg.com/media/HMIoK8QbQAA3Um-.jpg)

- **PreToolUse** — ツール実行「前」にチェック。自動許可やブロックができる
- **PostToolUse** — 実行「後」に処理を走らせる。フォーマットやテスト向き
- **Stop** — 作業完了時に発火する。完了通知を飛ばせる
- **Notification** — 許可待ち・入力待ちで通知する
**僕も最初はPreToolUseだけ設定した。** それだけで劇的に変わった。1つずつ追加していけばいい。

## settings.jsonに数行書くだけ

設定場所は .claude/settings.json。プロジェクトルートに .claude/ フォルダを作る。その中に settings.json を置く。

書くのはJSONだけ。次のセクションで全コード公開してます。**コピペするだけで動きます。**

シェルスクリプトも書けるけど最初はJSONだけで十分。難しいことは何もない。

## approve・block・modifyの3つだけ

![](https://pbs.twimg.com/media/HMIoPeeaQAA95QZ.jpg)

hooksの判定は3種類。

- **approve** — 許可する。そのまま実行
- **block** — 止める。AIが別の方法を考える
- **modify** — パラメータを変えて実行
exit code 0で承認。exit code 2でブロック。覚えるのはこれだけ。

**この3つで全操作をコントロールできる。** シンプルだけど恐ろしく
