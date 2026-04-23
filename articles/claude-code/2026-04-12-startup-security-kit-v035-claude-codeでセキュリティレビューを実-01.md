---
id: "2026-04-12-startup-security-kit-v035-claude-codeでセキュリティレビューを実-01"
title: "Startup Security Kit v0.3.5: Claude Codeでセキュリティレビューを実行する仕組みを追加しました"
url: "https://zenn.dev/hisa_tech_2973/articles/6d4b74c4bf0b7c"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-12"
date_collected: "2026-04-13"
summary_by: "auto-rss"
query: ""
---

**Startup Security Kit** に Claude Code を使ってセキュリティレビューを実行する仕組みを追加しました。

<https://github.com/st-hisatoshi-2973/startup-security-kit>

## なぜ作ったのか

最近の開発では、AIを使ってコードを書くことが当たり前になってきました。

一方で、このように感じることが増えています。

* AIでコードは速く書ける
* でもセキュリティレビューは人任せ
* 結果として、リスクも同じ速度で増えていく

特にスタートアップのようにスピードが求められる環境では、

「便利だから使う」ではなく

**「先に安全に使う仕組みを作る」**

ことが重要だと考えています。

## AIと人の役割

AIを使えば、コードのレビュー自体はできるようになってきています。

しかし、そのままでは

といった問題があります。

そのため重要なのは、

**AIにどの観点でレビューさせるかを定義すること**

だと考えています。

今回のアップデートでは、

* 認証・認可
* トークンや秘密情報
* ログの扱い
* 外部通信や依存関係
* AI利用に伴うリスク

といった観点をベースにレビューを行うようにしています。

また、最終的な判断は人が行う前提とし、

* どの程度危険なのか
* 何が問題か
* なぜ問題か
* どう修正するか
* どう検知するか
* 人が確認すべきポイント

を出力するようにしています。

## 「検知」まで含める理由

個人的に重要だと思っているのはここです。

多くのセキュリティレビューは、「問題があるかどうか」で終わります。

しかし実際の運用では、

**「問題が起きたときに気づけるか」**

の方が重要です。

そのため、Startup Security Kitでは

**検知（Detection）を前提にした設計**

を意識しています。

## 今回のアップデートでできること

Claude Code上で、

と実行するだけで、

* Startup Security Kit のセキュリティ観点でのレビュー
* 改善案
* 検知方法
* 人の確認ポイント

をまとめて出力できます。

## 目指しているもの

このプロジェクトでやりたいのは、

セキュリティの知識をまとめることではなく

**セキュリティを「実行できる形」にすること**

です。

を組み合わせて、

**誰でも同じレベルのセキュリティレビューができる状態**

を目指しています。

## GitHub

<https://github.com/st-hisatoshi-2973/startup-security-kit>

`/ssk-security-review` の実際のサンプルも用意しています。  
<https://github.com/st-hisatoshi-2973/startup-security-kit-example>

もしご意見や改善案があれば、Issue / PR 大歓迎です。  
一緒にセキュリティを **習慣** にしていければ嬉しいです。

## 関連記事

Startup Security Kit v0.3.4: 検知する設計  
<https://zenn.dev/hisa_tech_2973/articles/f18912935dcf13>
