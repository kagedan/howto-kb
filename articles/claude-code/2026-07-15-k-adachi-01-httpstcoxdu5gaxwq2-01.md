---
id: "2026-07-15-k-adachi-01-httpstcoxdu5gaxwq2-01"
title: "@k_adachi_01: https://t.co/xdu5gaxwQ2"
url: "https://x.com/k_adachi_01/status/2077469253801026027"
source: "x"
category: "claude-code"
tags: ["GPT", "TypeScript", "x"]
date_published: "2026-07-15"
date_collected: "2026-07-16"
summary_by: "auto-x"
query: "Claude Code CLAUDE.md 書き方 OR コンテキスト管理 OR Handover"
---

https://t.co/xdu5gaxwQ2


--- Article ---
# **Kiro 1周年記念ライブ配信 詳細レポート**

2026年7月16日、AWSの提供するコーディングアシスタント「Kiro」のリリースからちょうど1周年を記念したライブ配信が開催されました。

AWSのDeveloper AdvocateであるDarko氏とEric氏がホストを務め、チャット参加者からの挨拶（インド、ミュンヘン、メキシコ、オーストラリアなど）を交えながら、Kiroのこれまでの1年間を振り返りました。

![](https://pbs.twimg.com/media/HNSf0W1acAAQg4g.jpg)

## Birthday Week Challenge

今週はBirthday Weekの取り組みとして、毎日異なるチャレンジが実施されています。

イベントページ: https://kiro.dev/birthday/

誰でも参加可能。賞品があり、1週間の累計で最大9,000クレジット獲得のチャンスもあります。有料ユーザーには一律500クレジット（30日間有効）が付与され、Darko氏自身もアカウントで確認したと報告しました。

新モデルとして、前日にリリースされた「GPT 5.6」の全モデル群（Luna、Terra、Sol）がPro/Pro+/Powerユーザー向けに即時利用可能になったことも発表されました。チャットでは「もっとオープンウェイトモデルを」という声が上がり、両氏は「チームが取り組んでいる」と回答しています。

公式ブログ: [GPT‑5.6 is now available in Kiro](https://kiro.dev/blog/gpt-5-6/)

![](https://pbs.twimg.com/media/HNSgO55a8AAb_Gg.jpg)

## Kiro開発の背景とローンチの経緯

KiroはAWS/Amazonの「ドキュメント重視・顧客起点」の文化から生まれました。顧客がエージェントツールを使う際に「思うような方向に進まない」という声を集め、1つのドキュメントを作成。それがKiroの原点（genesis）となり、Spec-driven developmentやHooksなどのコア機能がここに記されていました。

社内エンジニアリングチームによる長期間のDog-Fooding（数百件のフィードバック）を経て、2025年7月にプレビューローンチ。ローンチ直後は「eBayで早期アクセス権が売られる」ほどの反響で、段階的開放が必要になったほどでした。

10月にはウェイトリストが完全解除され、誰でも利用可能に。11〜12月のre:InventでGA（一般利用開始）となり、CLIが同時に導入されました。

公式ブログ: [Kiro is generally available: Build with your team in the IDE and terminal](https://kiro.dev/blog/general-availability/)

## Spec-driven development の詳細

Kiroの最大の特徴である**Spec-driven development**は、単なる「vibe coding」ではなく、最初に正式なドキュメントを作成するアプローチです。

- 要件定義書（EARS形式のユーザーストーリー＋受け入れ基準）
- 設計書（技術的意思決定＋Mermaidダイアグラムによるアーキテクチャ）
- タスクリスト
の3つを生成します。現在は「要件から始める」「設計から始める」「クイックプランモード（一括生成）」の柔軟な選択が可能で、人間が各ステップでレビューする「human-in-the-loop」が重視されています。

Eric氏はこれを「宇宙船の軌道修正」に例え、大きな機能開発でコードの重複や誤ったリファクタリングを防ぐ効果を強調しました。Darko氏は「MVPを素早く作ってテストしたい場合、20ステップのうち最初の4ステップだけを実行させる」といった実践例を紹介。プロダクショングレードやセキュリティに関わる変更では特に有効で、小さな週末プロジェクトでは省略可能としています。

![](https://pbs.twimg.com/media/HNSh9MPbkAAbmYD.jpg)

さらに**Property-based testing**が統合されており、要件定義書から自動でプロパティを抽出し、ランダム値で複数回検証（TypeScriptではfast-checkを使用）。実際に「20回実行された」テスト例も画面共有されました。こ
