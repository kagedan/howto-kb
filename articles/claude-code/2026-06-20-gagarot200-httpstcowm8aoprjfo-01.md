---
id: "2026-06-20-gagarot200-httpstcowm8aoprjfo-01"
title: "@gagarot200: https://t.co/wm8AOPrjfO"
url: "https://x.com/gagarot200/status/2068241714586980739"
source: "x"
category: "claude-code"
tags: ["claude-code", "API", "x"]
date_published: "2026-06-20"
date_collected: "2026-06-21"
summary_by: "auto-x"
query: "Claude プロンプト 書き方 OR Claude 業務効率化 実例"
---

https://t.co/wm8AOPrjfO


--- Article ---
Claude CodeやCodexに指示を出してまた指示を出す。そんな日々に終止符を打つ記事です。オラの環境ではAI社員15人が「営業」「市場分析」「レポート作成」「請求書作成」全て勝手に毎日動いている。もはややることがないのでこの記事を主筆するに至った。寝ている間に仕事が終わるAI社員構築のすゝめとして読んでほしい。

# **【ここで緊急告知】**

![](https://pbs.twimg.com/media/HLPVsgAbcAAsSMT.jpg)

🪐遂に全て公開します🪐

📕『AI社員運用構築の教科書』📕

Claude Code × Codex対応

個人でも法人でも、
面倒な業務・集客・販売・運営をAIで自動化。

✔ 日々の雑務
✔ SNS集客
✔ コンテンツ制作
✔ 顧客対応
✔ 法人運営

AIを「使う側」から
AIに「働かせる側」へ。

非エンジニアでも導入できるよう
構築から運用まで全て解説しました🔥

🚨6月29日 20:00リリース🚨

限定オプチャ参加者は
最安値でご案内します👇
オープンチャット「ガガロットAI社員事前告知室」

https://line.me/ti/g2/iBrDDwcaNuzGyIOrYnTyM680m3CnfSPrCVDagg?utm_source=invitation&utm_medium=link_copy&utm_campaign=default

ーーーーーーーーーーーーーーーーーーーーーーーーーー

## Claudeは「話しかけるもの」から
「配備するもの」へ

ClaudeはAIチャットボットとして使われてきた。

質問を入力して回答をもらう

コードを貼り付けてレビューしてもらう

そういう「対話型」の使い方が一般的だった。

それが変わりつつある。

Anthropicがリリースした「**Routines**」は
Claudeの使い方を根本から変える機能だ。

タスクを一度定義すれば、あとはClaudeが自動で動き続ける。
PCを閉じていても、Claudeは働いている。

チャットボットでもコパイロットでもない
**クラウド上で稼働する自律型ワーカー**として機能する。

## Routinesとは何か

Routinesを一言で言えば
「**保存されたClaude Codeの設定を、自動で繰り返し実行する仕組み**」だ。

以下の4要素をひとまとめにして保存する。

プロンプト Claudeへの指示内容  ⬇︎
・リポジトリ
・操作対象のGitHubリポジトリ
・コネクター SlackやLinearなど
**連携サービス   トリガー いつ、何をきっかけに実行するか**

実行環境はAnthropicが管理するクラウドインフラ。
PCが起動していなくても
インターネットに繋がっていなくても、Claudeは動く。

深夜3時に本番環境でアラートが鳴っても
週末にオフィスが無人でも、定義したタスクは実行される。

対応プラン：**Pro・Max・Team・Enterprise**（Claude Code on the webが有効であること） 管理画面：[claude.ai/code/routines](https://claude.ai/code/routines)

## 3つのトリガー

**Schedule（スケジュール）**

**時刻・曜日を指定して定期実行する。**

> 頻度 内容     毎時 1時間ごとに実行   毎日 指定した時刻に毎日実行   平日のみ 月〜金の指定時刻に実行   毎週 指定した曜日・時刻に実行   カスタム cron式で細かく指定

> 時刻はローカルタイムゾーンで設定可。ClaudeがUTCへ自動変換する。実際の実行タイミングはスケジュール時刻から数分ずれることがあるが、そのオフセットはルーティンごとに一定。

「来週月曜の朝9時に先週のPRをまとめてほしい」といった
ワンオフ実行も設定可能。

ワンオフ実行は1日の実行上限にカウントされない。

**向いているタスク：** 毎朝のスタンドアップ準備、週次ドキュメントレビュー、夜間バックログ整理、朝のサマリー生成など。

> API

> HTTPリクエストを送ることでClaudeを起動する。ルーティンごとに専用エンドポイントURLが発行され、ベアラートークンで認証する。

> 

> text フィールドに追加コンテキストを渡せる。リクエストが成功するとセッションIDとURLが返る。そのURLを開けばClaudeの作業をリアルタイムで確認でき、途中から会話を続けることも可能。
