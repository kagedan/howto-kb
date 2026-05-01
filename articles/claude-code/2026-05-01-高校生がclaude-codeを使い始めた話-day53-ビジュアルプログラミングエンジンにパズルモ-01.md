---
id: "2026-05-01-高校生がclaude-codeを使い始めた話-day53-ビジュアルプログラミングエンジンにパズルモ-01"
title: "高校生がClaude Codeを使い始めた話 Day.53 ── ビジュアルプログラミングエンジンにパズルモードを追加した"
url: "https://note.com/enube_1115/n/n81bc48a610bd"
source: "note"
category: "claude-code"
tags: ["claude-code", "note"]
date_published: "2026-05-01"
date_collected: "2026-05-01"
summary_by: "auto-rss"
---

**今日やったこと**

ビジュアルプログラミングエンジンに3つ目のゲームジャンル「パズル」を追加した。テトリス風の落ち物パズルがブロックで制御できる。

**できたもの**

![](https://assets.st-note.com/img/1777296709-R1iDnkzrObpHXKayMLY0UtPo.png?width=1200)

左上のタブが3つになった：

* 🏃 アクション（横スクロール）
* 🚀 シューティング
* 🧩 パズル（テトリス風）

パズルモード専用ブロック：

* ブロックを置く・消す
* つながりを確認する
* 重力をオン／オフ

▶実行を押すとテトリスが動く。矢印キーで移動、↑かZで回転、スペースでハードドロップ。

**今回気づいたこと**

タブのCSSが崩れて「パズル」タブが表示されない不具合が最初に出た。Claude Codeに再指示して修正してもらったが、複数の機能を同時に追加するとUIの整合性が壊れやすい。大きな変更は都度ブラウザで確認するのが正解。

**次回予告**

クイズゲームモードを追加する。

公開済みWebアプリ一覧

プログラミング未経験の高校生がClaude Codeで作りました。 バグ報告・フィードバックはこちら： <https://docs.google.com/forms/d/e/1FAIpQLSdLquvAAs3S2DeZ1u4dyF6XZ8pTCXodEmH--Kacn-vV6U0_-Q/viewform>
