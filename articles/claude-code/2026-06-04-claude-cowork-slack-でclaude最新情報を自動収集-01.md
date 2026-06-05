---
id: "2026-06-04-claude-cowork-slack-でclaude最新情報を自動収集-01"
title: "Claude Cowork × Slack でClaude最新情報を自動収集"
url: "https://zenn.dev/tom1414/articles/87cab2ae7fabff"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "cowork", "zenn"]
date_published: "2026-06-04"
date_collected: "2026-06-05"
summary_by: "auto-rss"
query: ""
---

初めまして。  
3年目エンジニアの「とむ」と申します。  
これからAIやAWSに関する情報を少しずつ発信していきたいと思っておりますので、どうぞよろしくお願いします！

今回は、Claude Coworkを用いた記事になります。  
本記事では、Claudeの最新情報をSlackへ投稿する内容になりますが、必要に応じて得たい情報や投稿先を変更してみても面白いと思いますので、参考にしてみてください！

# はじめに

今回こちらを取り組もうと思ったきっかけは、毎日Claudeの最新情報をチェックしたいけど、情報収集だけであまり時間を取られたくない、というのでした。  
そんな課題を、Claude Coworkで解決してみました。

# Claude Coworkとは？

Claude CoworkはAnthropicが提供する、デスクトップエージェントです。

Claude（AIモデル）の能力をベースに、ローカルのファイル操作・ブラウザ操作・外部サービス連携を自然言語で指示できます。

「いつもの作業をそのままAIに任せる」というイメージが一番近いです。

## Claude CodeやChatとの違い

|  | Claude Chat | Claude Code | Claude Cowork |
| --- | --- | --- | --- |
| 主な用途 | 会話・質問 | コーディング | デスクトップ作業全般 |
| ファイル操作 | ❌ | ✅ | ✅ |
| ブラウザ操作 | ❌ | ❌ | ✅ |
| 外部サービス連携 | ❌ | △ | ✅ |
| スケジュール実行 | ❌ | ✅ | ✅ |

大雑把に言うと：

* **Chat** → 聞く・考える
* **Code** → コードを書く・動かす
* **Cowork** → 人間の代わりに手を動かす

外部サービス連携で、Claude Codeは△、Coworkは✅としている理由は、Coworkの場合**GUI操作**で「コネクタ」というのを使用して外部サービス連携を実現できるので、その差になります！

# 今回作るもの

Cowork スケジュールタスク（毎日・自動(※)）  
→ anthropic.com/news, claude.com/blog 等を収集  
→ Obsidian に daily note として保存  
AI-News\Daily\Claude\YYYY-MM-DD.md  
→ Slack の #claude-news に概要を投稿

**(※)自動で実行してはくれますが、Claudeのデスクトップアプリを開き続けている必要があります！！！**

## 事前準備

* Claude Desktop インストール済み
* Obsidian セットアップ済み（任意）
* Slackワークスペースあり（無料プランでもOK）

# 実装手順

## ① Slackコネクタを繋ぐ

1. Claude Desktop 左サイドバー「Customize」  
   ![](https://static.zenn.studio/user-upload/35efe254ec6c-20260604.png)
2. 「アプリを接続」を押下  
   ![](https://static.zenn.studio/user-upload/664556c513ec-20260604.png)
3. 検索欄に「Slack」と入力  
   ![](https://static.zenn.studio/user-upload/ebbe4ae60aca-20260604.png)
4. 「Connect」→ ブラウザでSlack認証(接続済み、となればOK！)  
   ![](https://static.zenn.studio/user-upload/e97e92d227b4-20260604.png)  
   ![](https://static.zenn.studio/user-upload/ea5eaa80572e-20260604.png)

## ② Slackに #claude-news チャンネルを作る

Slackで通知を受け取る専用チャンネルを作っておきます。  
名前は何でもOKですが、プロンプトと一致させてください。

## ③ Coworkでテスト実行

左サイドバー「+ New task」から新規タスクを作成し、  
以下のプロンプトをそのまま貼って実行します。  
![](https://static.zenn.studio/user-upload/f0026d47f7a6-20260604.png)

```
以下を順番に実行してください。

## ステップ1: 情報収集
直近24時間のClaude／Anthropic関連の更新をウェブ検索で調べる。
チェック対象:
- anthropic.com/news
- claude.com/blog
- Claude Code リリースノート

## ステップ2: Obsidianに保存
以下の形式でまとめ、指定パスにMarkdownファイルとして保存する。

保存先:
C:\iCloudDrive\iCloud~md~obsidian\AI-News\Daily\Claude\[今日の日付 YYYY-MM-DD].md

ファイル内容のフォーマット:
---
date: [今日の日付]
tags: [claude, anthropic, daily]
---

# Claude日次ニュース [今日の日付]

## トピック一覧
各トピックを以下の形式で記載:

### [見出し]
- 概要: 3行以内
- 出典: [URL]
- 記事ネタメモ: [1行]

## 本日のサマリー
全体を3行でまとめる。

※更新がない場合は「本日更新なし」とだけ記載。

## ステップ3: Slackに投稿
Slackの #claude-news チャンネルに以下の形式で投稿する。

📰 *今日のClaude更新* [今日の日付]

[トピックの見出しを箇条書き、各1行]

詳細はObsidianを確認。
```

## ④ 動作確認

実行後に以下を確認します。

* 実行が正常終了しているか  
  ![](https://static.zenn.studio/user-upload/aaeac2fa3049-20260604.png)
* ObsidianにYYYY-MM-DD.mdが生成されているか  
  ![](https://static.zenn.studio/user-upload/851159f49dde-20260604.png)
* Slackの #claude-news に投稿が届いているか  
  ![](https://static.zenn.studio/user-upload/4e3d3a55e9b2-20260604.png)

## ⑤ スケジュール登録

動作確認が取れたら、同じチャットでスケジュールを設定します。  
![](https://static.zenn.studio/user-upload/4f8914ea3355-20260604.png)  
![](https://static.zenn.studio/user-upload/29b7190f8f6b-20260604.png)

（テスト実行をしていなかったため、以下、やり直しました）  
テスト実行したことで、左サイドバーの「Scheduled」に登録されれば完了です。  
![](https://static.zenn.studio/user-upload/d4c309e72a7a-20260604.png)

> 注意：スケジュール実行はPCが起動中かつ  
> Claude Desktopが開いている時のみ動作します。  
> スリープ中はスキップされ、次回起動時に実行されます。

## 実行結果

テスト実行した際には、しっかりとスケジュールタスクとして動いたものがSlack等に反映されておりました！  
![](https://static.zenn.studio/user-upload/484f9a16307e-20260604.png)

その後、実際のスケジュールタスクとして実行されていた際には、内容が重複していた故にSlackへの投稿は行われませんでした。(正常終了しているため、OKとする)  
![](https://static.zenn.studio/user-upload/ad8e025879a6-20260604.png)

また、面白いことに、サーバーの混雑時間というものが存在しており、ぴったりに実行されないということもあるみたいでした！(21:30予約でしたが、21:36に実行されていました。)

# まとめ

Claude Coworkを使うことで、情報収集・保存・通知という一連の流れをプログラムなしで自動化できました！  
プログラムなし、という観点ではClaude Codeでも全任せにしてしまえばできますが、GUI操作で出来てしまうというところが、ターミナルやIDE上での操作が慣れてしまう人にも嬉しいポイントなのかなと思いました！

ポイントは4つです。

* **Slackコネクタ**を使えば、外部通知も自然言語で完結する
* **スケジュール機能**で毎日完全自動化できる
* **サーバー混雑影響**により、必ずしも指定の時刻に実行されない場合がある
* (**Obsidian連携**で蓄積された情報が、振り返り時に役立つ)

Claude Coworkは「GUIを操作する作業の代行」が本領ですが、情報収集→通知という定型タスクにも十分使えます。  
まずは手動で1回試してみることをおすすめします！

次回はデスクトップアプリを開いていなくても、完全自動で実行できるようにClaude Codeを使った版をご紹介できればと思います！

最後までご覧いただき、ありがとうございました！
