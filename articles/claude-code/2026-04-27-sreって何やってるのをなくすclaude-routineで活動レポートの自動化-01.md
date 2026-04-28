---
id: "2026-04-27-sreって何やってるのをなくすclaude-routineで活動レポートの自動化-01"
title: "SREって何やってるの？をなくす——Claude Routineで活動レポートの自動化"
url: "https://zenn.dev/dely_jp/articles/18cb5e7cc20fab"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "Python", "zenn"]
date_published: "2026-04-27"
date_collected: "2026-04-28"
summary_by: "auto-rss"
query: ""
---

クラシル株式会社でSREをやっているjoooee0000です！  
SREのAI活用として障害対応のトリアージ等の活用方法は有名かと思いますが、SREチームの課題あるあるとしてSREチームの動きが見えづらいというのもあると思います。

そこで、Claude Routineを使ってSREの活動のデイレポとウィークリーレポートを自動作成し、SREチームの動きを見える化してみました。

## 前提

### SREチームのタスク管理について

SREチームではスプリントの形式で下記のようにタスクを分割し、Notionで管理しています。

* **Epic**: 四半期単位の大きなテーマ（例: 監視基盤の整備、コスト最適化）
* **Story**: Epicを分解した施策単位
* **タスク**: Storyをさらに分解した実作業単位

### Working Out Loudの文化

全社的にWorking Out Loud（作業の過程をオープンに共有する）の文化があり、Slackで作業内容や意思決定の経緯を発信しながら仕事を進めています。

しかし、SREの活動はSlack上でも断片的になりがちだったり、チーム全体として「どの目標に対するアクションなのか、今日何に取り組んで、何が進んだのか」はまとまった形では可視化できていませんでした。

## Claude Routineとは

Claude Routineは、Claudeに定期的なタスクをクラウド上で自動実行させる機能です。2026年4月14日にClaude Codeのデスクトップアプリ刷新と合わせて発表されました。現時点ではリサーチプレビューとして提供されており、仕様や制限が今後変更される可能性があります。

### 特徴

* **PCの起動が不要** — Anthropicのクラウド基盤で実行されるため、ローカルマシンの状態に依存しない
* **MCP連携** — NotionやSlackなどの外部サービスと接続できる
* **プロンプトベースで設定** — やりたいことを自然言語で記述するだけで動作する
* **複数のトリガー** — スケジュール実行のほか、API経由やGitHubイベント（PR作成、リリースなど）をトリガーにした実行も可能

## デイリーレポートのSlack投稿の自動化

Claude Routineを使って、日々のSREチームの行動を可視化しました。  
設定はシンプルで、すでにどこかのツールにまとまっている情報をサマリして定期投稿するだけなら低コストでレポートを自動化できます。

### 1. MCP Serverの接続

今回はClaude RoutineからNotionとSlackにアクセスするため、それぞれのMCP Serverを接続します。Claude.aiの設定画面からIntegrationsを開き、NotionとSlackを追加します。

### 2. Routineの作成

Claude.aiのデスクトップアプリを開き、左メニューの「Code」からRoutinesタブを選択します。新規作成時に「リモート」を選択すると、ローカルでの実行ではなくクラウド上での実行となります。

挙動については、以下を設定します。

* **スケジュール**: 平日の夕方（例: 毎週月〜金 20:00）
* **プロンプト**: 後述のサンプルを参考に記述

![](https://static.zenn.studio/user-upload/5a5863b887d8-20260422.png)

### 3. プロンプト

実際に使用しているプロンプトです。  
ちなみにこのプロンプトも、どういう内容を可視化したいかをリクエストすればClaudeが自動で生成してくれました。

```
SREチームのdaily活動サマリーを作成してSlackに投稿してください。

## タイムスタンプの計算
- 集計期間は JST 前日17:51 〜 当日17:50
- JST = UTC+9 なので、Slack APIに渡すUnixタイムスタンプはUTCに変換すること
- 前日 17:51 JST → 前日 08:51 UTC、当日 17:50 JST → 当日 08:50 UTC

## 手順

### 1. タイムスタンプ計算
今日の日付から oldest / latest のUnixタイムスタンプを計算する

### 2. Slackデータ収集
- slack_read_channel でチームチャンネル (チャンネルID: XXXXXXXXXXX) のメッセージを取得
- oldest / latest パラメータで集計期間を指定
- slack_read_channel でGitHub通知チャンネル (チャンネルIDは初回に検索して特定) のメッセージも取得
- oldest / latest パラメータで同じ集計期間を指定
- GitHubアクティビティ通知から、対象メンバーのGitHubアカウントに紐づく活動（PR作成/マージ/レビュー、Issue、コミットなど）を抽出

### 3. Notionデータ収集

#### 3a. ドキュメントDB (SREタブ)
- notion-query-data-sources でSREデータベース (collection://xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx) をクエリ
- Created time または最終更新日時が集計期間内のエントリを取得（UTCで指定）
- タイトルが必要な場合は notion-fetch で個別ページを取得

#### 3b. SprintDB / TaskDB / StoryDB
現在のスプリントのタスク進捗を取得し、Epic > Story > Task の階層で可視化する。

1. SprintDB (collection://xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx) からスプリントステータス=「現在」を取得
2. TaskDB (collection://xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx) から、現在スプリントに紐づくタスクで集計期間内に更新されたものを取得
3. 各タスクの「関連Story」URLから StoryDB (collection://xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx) を参照し、Story名とEpicを取得
4. 担当者のNotion User IDでメンバーにマッピング

Notion User ID → メンバーのマッピング:
- xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx = メンバーA
- xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx = メンバーB
- xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx = メンバーC
- xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx = メンバーD

GitHub アカウント → メンバーのマッピング:
- github-user-a = メンバーA
- github-user-b = メンバーB
- github-user-c = メンバーC
- github-user-d = メンバーD

### 4. サマリー作成
以下のSlack mrkdwnフォーマットで日本語サマリーを作成する。
注意: Slack MCP投稿では標準Markdown記法を使うこと。
- 太字: `**bold**`（`*bold*` ではなく）
- イタリック: `_italic_`
- コード: `` `code` ``
- リンク: `<url|text>`
- リスト: `•`
- Slackでは `---` 区切り線・Markdown見出し `#` は使えない

📊 **SRE Daily Summary - [今日の日付] ([曜日])**
集計期間: M/D HH:MM - M/D HH:MM JST
 
🏃 **Sprint タスク概況**

集計期間内に更新のあったSprintタスクをEpic別にまとめる。
担当者を括弧で表示し、新規作成タスクには 🆕 を付ける。

**Epic: [Epic名]**
• Story名 → タスク名 _Status_ (担当者) 🆕
• Story名 → タスク名 _Status_ (担当者)

**Epic: [Epic名2]**
• Story名 → タスク名 _Status_ (担当者)

**Epic: [その他]**（Epicなしの場合）
• Story名 → タスク名 _Status_ (担当者)
• タスク名 _Status_ (担当者)（Storyなしの場合）

👤 **メンバー別アクティビティ**

Sprint タスクは上のセクションにまとめて表示済みなので、ここでは重複して記載しない。
Slack活動とGitHubアクティビティを箇条書きでまとめる。

**メンバーA**
_GitHub:_
• PR/レビュー/マージなどのGitHubアクティビティ
_Slack:_
• Slackでの活動内容（時系列や重要度で並べる）

**メンバーB**
[同様]

**メンバーC**
[同様]

**メンバーD**
[同様]

📝 **まとめ**

[1-2文で今日の全体的な活動を要約]

### ルール
- 対象メンバーのSlack ID: XXXXXXXXXXX (メンバーA), XXXXXXXXXXX (メンバーB), XXXXXXXXXXX (メンバーC), XXXXXXXXXXX (メンバーD)
- 対象外メンバーのメッセージは無視（ただし対象メンバーへのメンションなど関連する場合は記載OK）
- Slackは活動ごとに行を分ける（複数トピックなら複数行）
- 活動がない場合は「該当期間の活動なし」
- Slackbot/リマインダーは除外

### 5. Slack投稿
- slack_send_message でチームチャンネルに投稿
```

### 4. 動作確認

設定後、Routineを手動実行して意図通りの投稿が行われるか確認します。Notionのタスク更新状況が正しく取得できているか、Slackの投稿フォーマットが崩れていないかをチェックしてください。

一度AIが急にMCPのツール名を間違えて動かなかったことがありました。利用するMCPツールを明示的に指定すると意図しないエラーが起こりづらくなります。  
![](https://static.zenn.studio/user-upload/ace0a292de87-20260422.png)

### 実際の投稿

![](https://static.zenn.studio/user-upload/a52c11735f8a-20260424.png)  
![](https://static.zenn.studio/user-upload/4ccba73b37c7-20260424.png)

※ 本名、セキュリティ関連情報、社外秘の情報はマスキングさせていだだいています

## Weekly Sprint Reportへの展開

デイレポの仕組みがうまく回り始めたので、同じClaude Routineで**Weekly Sprint Report**も自動生成するようにしました。EMとのスプリント共有MTG用のサマリーです。

### デイレポとの違い

|  | デイレポ | Weekly Sprint Report |
| --- | --- | --- |
| 頻度 | 毎日 | 週1回（Sprint共有MTG前） |
| 出力先 | Slack投稿 | Notionページ作成 |
| 対象範囲 | 当日更新されたタスク | Sprint全タスク（全ステータス） |
| 情報源 | Notion | Notion + Slack（1週間分） |
| 用途 | チーム内・他チームへの共有 | EMとの進捗共有MTG資料 |

デイレポは「今日何をしたか」の軽い共有ですが、Weeklyは「Sprintに対してどこまで進んでいるか」を俯瞰するためのものです。

### プロンプト

工夫した点は、タスクが完了したことでどのような成果がでたのか、をレポートする欄を作成したことです。成果のアウトプット自体は自動化ができていないので、タスクをDONEにするときに明示的な成果があれば記載するルールにしています。

```
SREチームのWeekly Sprint ReportをNotionページとして作成してください。
EMとのSprint共有MTG用のサマリーです。

## 手順

### 1. Sprint情報の取得

#### 1a. 現在のSprint取得
- mcp__claude_ai_Notion__notion-query-data-sources で SprintDB (collection://<SprintDB_ID>) をクエリ
- スプリントステータス=「現在」のSprintを取得し、Sprint名と期間を特定

#### 1b. 全タスク取得（集計期間の制限なし）
- mcp__claude_ai_Notion__notion-query-data-sources で TaskDB (collection://<TaskDB_ID>) をクエリ
- 現在スプリントに紐づく**全タスク**を取得（dailyと違い期間制限なし）
- 完了タスクについては mcp__claude_ai_Notion__notion-fetch でページ本文を取得し、アウトカムの記載があるか確認する（記入がある場合のみ使用）

#### 1c. Story/Epic情報の取得
- 各タスクの「関連Story」URLから StoryDB (collection://<StoryDB_ID>) を参照
- Story名とEpicを取得

### 2. Slackデータ収集（1週間分）
- pythonで今日の日付からSprintの直近1週間分のoldest/latestを計算
  - oldest: 7日前の月曜 09:00 JST → 月曜 00:00 UTC
  - latest: 今日の現在時刻 JST → UTC変換
- mcp__claude_ai_Slack__slack_read_channel で #team-channel (<CHANNEL_ID>) のメッセージを取得

### 3. メンバーマッピング

Notion User ID → メンバー:
- <notion_user_id_1> = メンバーA
- <notion_user_id_2> = メンバーB
- <notion_user_id_3> = メンバーC
- <notion_user_id_4> = メンバーD

Slack ID:
- <slack_id_1> = メンバーA
- <slack_id_2> = メンバーB
- <slack_id_3> = メンバーC
- <slack_id_4> = メンバーD

### 4. Notionページ作成

mcp__claude_ai_Notion__notion-create-pages でドキュメントDBにページを作成する。

#### ページプロパティ
- parent: data_source_id = "<data_source_id>"
- "": "SRE Weekly Sprint Report - [Sprint名] ([今日の日付])"  ※タイトルプロパティ
- "Category": "SRE"
- icon: "📋"

#### ページコンテンツ（Notion Markdown形式）

以下のNotionフレーバーMarkdownでコンテンツを作成する。

<callout icon="🧭" color="blue_bg">
        **SRE戦略**: [SRE戦略ページ](戦略ページのURL)
</callout>

## 🎯 Sprint 目標達成度

<table header-row="true">
<tr>
<td>ステータス</td>
<td>件数</td>
</tr>
<tr>
<td>✅ 完了</td>
<td>X件</td>
</tr>
<tr>
<td>🔄 進行中</td>
<td>X件</td>
</tr>
<tr>
<td>👀 レビュー中</td>
<td>X件</td>
</tr>
<tr>
<td>🔲 未着手</td>
<td>X件</td>
</tr>
</table>

## 🏗️  Epic別 進捗サマリー

全タスクをEpic > Story > Task の階層で表示する。
各Epicについて、完了タスクにアウトカムの記入があればサマリーを表示する。
アウトカムが1件も無いEpicではアウトカムセクションを省略する。

### Epic: [Epic名]

**🏆 アウトカム**（※アウトカム記入がある場合のみ表示）
- [完了タスクのアウトカムをEpic単位でサマライズして1-3行で記載]

- ✅ Story名 → タスク名 (担当者)
- 🔄 Story名 → タスク名 (担当者)
- 🔲 Story名 → タスク名 (担当者)

### Epic: [Epic名2]

- ...

### その他（Epicなしの場合）

- ...

## 👤 メンバー別ハイライト

メンバーごとに、タスク状況のサマリーと今週のSlackでの主な活動をまとめる。
Slackは全トピックを列挙せず、重要なもの3-5件に絞る。

### メンバーA
- **タスク**: 完了X件 / 進行中X件
- **主な活動**: ...

### メンバーB
（同様）

### メンバーC
（同様）

### メンバーD
（同様）

## ⚠️  ブロッカー/リスク

- (Slackやタスクから検出されたブロッカーを記載。なければ「特になし」)

## 📝 まとめ

1-2文で今週の全体サマリー。Sprint目標に対する進捗と来週の注力ポイント。

### ルール
- 対象外メンバーのメッセージは無視（対象メンバーへのメンション等関連する場合はOK）
- Slackbot/リマインダーは除外
- タスクは全件表示（dailyと違い更新分だけでなく全ステータスのタスクを網羅）
- メンバー別Slack活動は重要トピックに絞る（週次なので全件列挙しない）
- 作成後、NotionページのURLをユーザーに返すこと
```

### 実際の投稿

![](https://static.zenn.studio/user-upload/cc0c55bdc1b1-20260424.png)  
![](https://static.zenn.studio/user-upload/c7ee9616c622-20260424.png)  
![](https://static.zenn.studio/user-upload/e20cc04965b3-20260424.png)  
![](https://static.zenn.studio/user-upload/d133677c6aa8-20260424.png)

※ 本名、セキュリティ関連情報、社外秘の情報はマスキングさせていだだいています

## 運用してみて

可視化することで、日々の業務でどのような成果がでているかをより意識できるようになりました！また、チーム外のメンバーもSREチームがやっていることを理解しやすくなったとフィードバックをもらいました。  
手動でやっていたら想定週に2~3時間かかっていた業務を自動化でき、地味に大きいトイルの削減担ったと感じています。

## 今後の展望

デイレポとウィークリーレポートで、日次・週次の活動可視化はカバーできました。今後は四半期目標に対する進捗の可視化にも取り組みたいと考えています。Notionに目標と紐づけた進捗情報を持たせれば、「目標に対して今どのあたりにいるか」をレポートに含めることもできるはずなので、今後はより視覚的に成果を可視化することを目指していきたいです。

SREチームの活動の可視化は、チームの信頼構築にもつながる取り組みです。小さな自動化から始めてみませんか！
