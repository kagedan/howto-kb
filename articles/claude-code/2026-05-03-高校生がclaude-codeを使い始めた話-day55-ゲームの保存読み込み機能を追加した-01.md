---
id: "2026-05-03-高校生がclaude-codeを使い始めた話-day55-ゲームの保存読み込み機能を追加した-01"
title: "高校生がClaude Codeを使い始めた話 Day.55 ── ゲームの保存・読み込み機能を追加した"
url: "https://note.com/enube_1115/n/n59c5d3965fa4"
source: "note"
category: "claude-code"
tags: ["claude-code", "note"]
date_published: "2026-05-03"
date_collected: "2026-05-03"
summary_by: "auto-rss"
query: ""
---

**今日やったこと**

ビジュアルプログラミングエンジンに「💾 保存」「📂 読み込み」ボタンを追加した。作ったゲームをJSONファイルで保存・復元できるようになった。

**できたもの**

![](https://assets.st-note.com/img/1777356178-bpvPRjZQew9CsTKX4m6EkLGt.png?width=1200)

ツールバーに水色の「保存」と紫の「読み込み」ボタンが追加された。

保存すると game\_action\_2026-04-28.json のような形式でダウンロードされる。ブロックの配置・パラメータ・現在のモード（アクション／シューティング／パズル／クイズ）が全て記録される。

読み込みはJSONを選ぶだけで、モードの切り替えからブロックの復元まで自動でやってくれる。

**今回気づいたこと**

保存・読み込みがないと「せっかく作ったのにリロードで消える」という問題がある。ゲームエンジンとして使い続けてもらうには必須の機能だった。機能を作る順番として、先にゲームモードを全部揃えてから保存機能を追加したのは正解だった。逆だと保存形式が途中で変わって壊れる。

**次回予告**

作ったゲームをURLでシェアできる機能を追加する。

公開済みWebアプリ一覧

プログラミング未経験の高校生がClaude Codeで作りました。 バグ報告・フィードバックはこちら： <https://docs.google.com/forms/d/e/1FAIpQLSdLquvAAs3S2DeZ1u4dyF6XZ8pTCXodEmH--Kacn-vV6U0_-Q/viewform>
