---
id: "2026-05-29-keitowebai-httpstcoajazgz4ji7-01"
title: "@keitowebai: https://t.co/aJAzGZ4jI7"
url: "https://x.com/keitowebai/status/2060326002363187237"
source: "x"
category: "claude-code"
tags: ["claude-code", "x"]
date_published: "2026-05-29"
date_collected: "2026-05-30"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

https://t.co/aJAzGZ4jI7


--- Article ---
2025年5月、Anthropicが最新モデル「Claude Opus 4.8」をリリースしました。目玉機能が「Dynamic Workflow」です。

この記事では、Dynamic Workflowがどんな機能なのか、どんな場面で使えるのか、従来のやり方と何が違うのかを、初心者にもわかるようにまとめます。最後に、実際にDynamic Workflowでゲームを作った事例も紹介します。

## Dynamic Workflowとは？

一言で言うと、「ゴールを1回伝えるだけで、AIが勝手に計画を立てて、複数の作業を同時に進めてくれる機能」です。

たとえば「Webアプリを作って」と指示すると、AIが自動で以下を行います。

1. 1.タスクを分解する（デザイン、コード実装、テスト…）
1. 2.それぞれ専門の「サブエージェント」を立ち上げる
1. 3.複数のサブエージェントが同時並行で作業する
1. 4.完成したら結果を統合して納品する
人間がやることは「ゴールを伝える」だけ。途中経過の管理もAIが自動で行います。

![](https://pbs.twimg.com/media/HJe86mTa0AAxo_L.jpg)

## 従来のやり方と何が違う？

「AIにサブエージェントを使わせる」という発想自体は以前からあります。ただし、従来は人間が設計・管理する必要がありました。

Dynamic Workflowでは、AIが自動で設計・管理する点が根本的に異なります。

![](https://pbs.twimg.com/media/HJe9HYSa4AANanO.jpg)

![](https://pbs.twimg.com/media/HJe-qpDbYAAfIOx.jpg)

イメージとしては、従来型が「自分で段取りを組んで、1人ずつ部下に指示を出す」スタイル。Dynamic Workflowは「優秀なプロジェクトマネージャーに丸投げしたら、チームを編成して勝手に完成させてくれる」スタイルです。

## **Dynamic Workflowの**使い方

Dynamic Workflowの使い方はClaude Codeのターミナル上で「workflow」と入力しワークフローを含んで欲しいことを言及する。

もしくは、「/effort」で設定推論レベルをultracodeのモードにすることで常時発動することになります。

![](https://pbs.twimg.com/media/HJgBhX2bUAUqVKq.jpg)

またDynamic Workflow発動中は「/workflow」でバックグラウンドで実行されているworkflowを確認することが可能。

## どんな場面で使える？

Dynamic Workflowが特に力を発揮するのは、以下のような場面です。

**① 大規模なコード作業**

数千ファイルのリファクタリングやフレームワーク移行。並列でファイルを処理し、テストが通るまで自動修正を繰り返します。

**② セキュリティ監査**

コードベース全体を同時にスキャンし、脆弱性を洗い出して修正パッチまで当てます。

**③ ディープリサーチ（深層調査）**

/deep-researchコマンドを使うと、複数の検索エージェントが異なる角度から情報を集め、信頼性を相互検証した上でレポートにまとめます。

**④ ゲームやアプリの一発構築**

画像生成、コード実装、テスト、デプロイまでを1つの指示で完結させます（後述の事例参照）。

## 【実践】Dynamic Workflowでゲームを作ってみた

実際にDynamic Workflowの実力を試すため、以下の指示を1回だけ出しました。

> 横スクロールアクションシューティングゲームを作ってください。画像生成でキャラクター・敵・背景などのアセットをすべて作成し、実装後にデプロイまで進めてください。

AIが自動で実行したこと

指示を受けたClaude Opus 4.8は、自動で2つのワークフローを構築しました。

アセット生成ワークフロー
5のサブエージェントが同時に起動し、キャラクター・敵・背景・エフェクトなどの画像を並列生成

テストワークフロー
コード実装後、6つの検証エージェントが自動テストを実行。30件のバグを検出し、28件を自動修正

人間の介入なしで、約1時間で完成・デプロイまで到達しました。

# 完成したゲーム

![](https://pbs.twimg.com/media/HJe86mTa0AAxo_L.jpg)

背景、アイテム、ボス戦
