---
id: "2026-07-06-claude-code-v21201sonnet-5-が会話途中の-system-role-をやめる-01"
title: "Claude Code v2.1.201｜Sonnet 5 が会話途中の system role をやめる｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/6fc5910d8bdf6343498b"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "AI-agent", "qiita"]
date_published: "2026-07-06"
date_collected: "2026-07-07"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

v2.1.201 の変更は1行だけ。Claude Sonnet 5 のセッションで、harness reminder を会話の途中に system role で差し込む挙動が外れた。リマインダーをどのロールで渡すかはモデルの追従性を左右する部分で、そこに Sonnet 5 向けの調整が入った。

> Claude Sonnet 5 sessions no longer use the mid-conversation system role for harness reminders

harness reminder という語も、mid-conversation system role という語も、Claude Code のログを見ないとピンと来ません。まずはその関係から。

## 会話途中の system role とは何だったのか

Claude Code は会話の最中に、モデル宛のリマインダーを裏で差し込んでいます。TODO リストの現在状態、開いているファイルへの注意書き、ツールの利用可否、権限まわりの但し書き。これが harness reminder で、セッションのログを覗くと `<system-reminder>` タグで囲まれて現れます。

問題はその渡し方。システムプロンプトは通常、会話の先頭に1度だけ置きます。ところが Sonnet 5 のセッションでは、このリマインダーを会話の途中にも system role として差し込んでいました。会話の頭ではなく、user と assistant のやり取りの合間に、システム権限の指示がもう一度入る。これが「mid-conversation system role」です。

system role で渡すか、user の発話に混ぜて渡すかで、モデルの受け取り方は変わります。system 側は守るべき前提として強く効きやすく、user 側の文章はその時の依頼として読まれる。同じ文言でも、載せるロール次第でリマインダーの重みは動きます。

## Sonnet 5 で外れたのはどこか

**会話の途中に system role を差し込む、この一点だけが Sonnet 5 で無くなりました。**

```
# これまでの Sonnet 5 セッション(イメージ)
system     : 先頭のシステムプロンプト
user       : 依頼
assistant  : 応答
system     : harness reminder   ← 会話の途中に system role
user       : 次の依頼

# v2.1.201 以降の Sonnet 5 セッション(イメージ)
system     : 先頭のシステムプロンプト
user       : 依頼
assistant  : 応答
user       : 次の依頼(harness reminder を同梱)   ← 途中の system role は無し
```

原文が明言しているのは、会話途中の system role をやめたことだけ。リマインダー自体が消えたわけではなく、載せるロールが変わったと読むのが自然です。Sonnet 5 に限った話で、他モデルのセッションはこの記述の対象外。

## 影響が出るのはどこか

:::note warn
対話でふつうに使っているぶんには、見た目の挙動は変わりません。効いてくるのは、Sonnet 5 のセッションを生ログ単位で扱う場面です。
:::

Agent SDK で組んだアプリのメッセージ列を検証している人、セッションを再生・評価している人、リマインダーの効き方を追っている人。この層にとっては、メッセージ構造が変わるのが Sonnet 5 のセッションだけ、という点が効いてきます。ロール構成を前提にしたパーサやフィルタを書いているなら、会話途中の system ロールを想定した分岐は Sonnet 5 では踏まれなくなる。

## まとめ

v2.1.201 は Sonnet 5 の harness reminder を、会話途中の system role から通常のメッセージ列へ寄せる変更です。対話利用では体感差はほぼ無く、生のメッセージ列を扱う開発者向けの調整。同じリマインダーでも、載せるロールはモデルごとに違う。Sonnet 5 ではそれが system role から外れた、というのが今回の調整でした。
