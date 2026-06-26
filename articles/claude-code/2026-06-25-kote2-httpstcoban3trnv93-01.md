---
id: "2026-06-25-kote2-httpstcoban3trnv93-01"
title: "@kote2: https://t.co/BaN3tRnV93"
url: "https://x.com/kote2/status/2070148212615491986"
source: "x"
category: "claude-code"
tags: ["claude-code", "x"]
date_published: "2026-06-25"
date_collected: "2026-06-26"
summary_by: "auto-x"
query: "Claude Code hooks 使い方 OR subagents 設定 OR Claude Code スケジュール"
---

https://t.co/BaN3tRnV93


--- Article ---
こんにちは、kote2です。
非エンジニア向けの Claude Code のプロジェクトビルダー(kote2式ビルダー for Claude Code)がバージョンアップしましたのでお知らせします。

ダウンロードリンクはページ最後にあります。

## Fable 5で設計を全面見直し

まず、v2をFable 5で設計を全面見直しました。構造的矛盾などいろんな箇所を指摘されたため、ここは設計全体に関わることなのでv3として1から書き直しました。

![](https://pbs.twimg.com/media/HLqipTuasAEEgAh.jpg)

御存知の通り、Fable 5は登場してから3日で停止されるという事態になりましたが、ベースはFable 5で作成されており、これを引き継ぐ形でOpus4.8で改善を行いました。

## 今回の目玉機能「レシピ」

kote2式ビルダーv3の目玉機能はレシピ機能です。フリー版はレシピの取り込み機能、プロ版(メンバーシップ版)はレシピの取り込みに加え、レシピ作成機能が付いています。

![](https://pbs.twimg.com/media/HLqirlvbgAAR_ab.jpg)

プロ版を使用して開発を行うと、開発手順を自動でドラフト化し、開発が完了した時点で「このプロジェクトのレシピを作成して」とClaude Codeに言うと、ドラフトを結晶化、レシピファイルとして書き出します。

![](https://pbs.twimg.com/media/HLqitxTaMAAUAvM.png)

そして、このレシピファイルをkote2式ビルダーに「このレシピを元に同じものを作って」と言うと、そのレシピを元に作成します。つまり、kote2式ビルダーを通してレシピファイルだけを渡すだけで同じ物が作れるようになります。

![](https://pbs.twimg.com/media/HLqivNvaQAAS15W.png)

## 実行環境構築のハマりどころの解決法までレシピに反映

このレシピ機能の面白いところは、プロダクトの作り方レシピにとどまらないところです。

これはサンプルレシピにも付いてくるNotionライクなWordPressを使用した自分用ノートを作れるレシピを元に作成されたものです。

![](https://pbs.twimg.com/media/HLqix5AboAAVLmK.jpg)

これは、私kote2がMac環境で作り、ローカル環境でWordPressを動かすためにDockerというあなたのPC内に仮想的なサーバーを作るアプリケーションを使って動かしてますが、PC内の実行環境の設定まで全てレシピで言語化されています。つまり、レシピオーナーのやってる手順をそのまま再現し、ハマりどころを回避してスムーズに作成することが出来ます。なお、このNotionライクなWordPressノートはWindows環境でもテストして、作成出来る事を確認しています。

レシピが単なるプロンプトでも完成コードでもなく、

- 何を作ろうとしたか
- どう設計したか
- どこでつまずいたか
- どう回避したか
- macOSとWindowsで何が違ったか
- 正しく完成したと判断する条件
を、含んでおり、**一度うまくいったAI開発を、検証済みの再現可能な資産**に変える仕組みになります。

## 付いてくるレシピ

今のところ数が少ないですがどんどん増やすつもりです。またYouTubeなどで実演した内容も、レシピ配布も今後行っていくつもりです。

フリー版

**・recipes/notion-wp.md**
NotionライクなWordPressノートを作れるレシピ

プロ版

**・recipes/notion-wp.md**
NotionライクなWordPressノートを作れるレシピ

**・recipes/xserver-site-ops.md**
Xserver上のサイト管理ワークスペースレシピ

**・recipes/xserver-wp-triage.md**
Xserver上の既存 WordPress サイトを、Claude Code から直接編集して保守できるレシピ(site-ops とは別アプローチ)

※メンバーシップ掲示板ではkote2やメンバーシップの方々でレシピを公開しあえるように盛り上げていきましょう🎉

では、そもそもkote2式ビルダーを知らない方の方が多いと思うので説明します。

## kote2式ビルダー for Claude Codeとは

kote2式
