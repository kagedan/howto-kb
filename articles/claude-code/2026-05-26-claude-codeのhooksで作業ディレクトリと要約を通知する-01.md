---
id: "2026-05-26-claude-codeのhooksで作業ディレクトリと要約を通知する-01"
title: "Claude Codeのhooksで『作業ディレクトリ』と『要約』を通知する"
url: "https://zenn.dev/kh37/articles/07e13338b66a18"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-05-26"
date_collected: "2026-05-27"
summary_by: "auto-rss"
query: ""
---

## TL;DR

* 通知センターにClaude Codeの完了 or 承認通知
* どのディレクトリでどんな内容かを通知内に記載
* 通知内で概要がわかるため、並列作業時にとても便利

## 想定読者

* 複数のClaude Codeを並走させる方
* 一旦放置できるくらいの時間でClaude Codeに実行させる方

## やったこと

![Claude Codeからの通知](https://static.zenn.studio/user-upload/02be2a5ff05b-20260526.png)  
*実際の通知画面の例*

* 通知センターにClaude Codeの完了 or 承認通知
  + タイトル：`Claude Code: my-project`（作業ディレクトリ名）
  + 本文：直近のアシスタントメッセージ or 承認待ちの理由
* 「完了したとき」と「ユーザーの承認を待っているとき」の2パターンで通知

## 何が嬉しいのか

* **どの作業ディレクトリのClaudeか一目で分かる**
  + タイトルにディレクトリ名が入っているので、3つ4つ並走していても迷子にならない
* **本文があるから「何で止まったか」が分かる**
  + 通知を見るだけで「あ、ファイル削除の承認待ちだな」と判別でき、戻る/戻らないの判断ができる
* **完了通知の本文に成果サマリが出る**
  + 直近メッセージが200文字くらい入るので、終わってる/詰まってる/質問されてるが即わかる

## 実装方法

Claude Codeで依頼したら5分くらいで出来ました。ぜひ依頼してみてください。

## まとめ

hooksの中でも一番使用頻度の高く満足度の高いものです。  
簡単に実装できるのでぜひ試してみてください。
