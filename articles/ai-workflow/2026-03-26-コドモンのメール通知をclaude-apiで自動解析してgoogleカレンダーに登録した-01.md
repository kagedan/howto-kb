---
id: "2026-03-26-コドモンのメール通知をclaude-apiで自動解析してgoogleカレンダーに登録した-01"
title: "コドモンのメール通知をClaude APIで自動解析してGoogleカレンダーに登録した"
url: "https://zenn.dev/nori_sasa_dev/articles/codomon-gas-claude-calendar"
source: "zenn"
category: "ai-workflow"
tags: ["API", "zenn"]
date_published: "2026-03-26"
date_collected: "2026-03-28"
summary_by: "auto-rss"
---

## TL;DR

* 保育園から届くコドモンのメールを **Google Apps Script + Claude API** で自動解析
* 休園・早帰り・給食なし・行事などをGoogleカレンダーに自動登録
* サーバー不要・GASは無料枠内で動く（Claude APIの利用料は別途発生）

---

## 背景：子どもの予定が複数アプリに分散していた

子育て中、こんな状況になっていました。

* 保育園の連絡 → **コドモン**のアプリ通知 + メール
* 小学校の連絡 → **スクリレ**のアプリ通知
* 習い事の連絡 → **BAND**のグループ投稿

それぞれ別のアプリで通知が来るため、「今日、給食あったっけ？」「来週の早帰りはいつだっけ？」をGoogleカレンダーで一元管理できていませんでした。

手動でカレンダーに入れるのも忘れがちで、直前に気づくことが多く…。

**「どうせなら自動化してしまおう」** と思い、Claude APIを使って解決しました。

---

## アーキテクチャ

```
コドモン
  ↓ メール通知
Gmail
  ↓ GASが毎週金曜22時に検索
Google Apps Script
  ↓ メール本文をClaude APIに送信
Claude API（claude-sonnet-4-6）
  ↓ イベント情報をJSON形式で返す
Google Calendar
```

サーバーもデータベースも不要。GASとClaude APIだけで完結します。

---

## 実装のポイント

### 1. APIコストを抑えるキーワードフィルタ

全メールをClaude APIに投げるとコストが嵩むため、**件名にキーワードが含まれるメールだけAPIを呼ぶ**ようにしました。

```
const CALENDAR_KEYWORDS = [
  '休園', '早帰り', '給食なし',
  '行事', '提出', '面談', '運動会', '発表会', '遠足',
  '臨時', '変更', '中止', '弁当',
];

const hasKeyword = CALENDAR_KEYWORDS.some(kw => subject.includes(kw));
if (!hasKeyword) {
  markAsProcessed(message); // APIスキップ・処理済みにする
  return;
}
```

### 2. Claude APIへのプロンプト設計

メール本文から必要な情報を構造化JSONで返してもらいます。

```
const prompt = `あなたは保育園・学校からの連絡メールを解析するアシスタントです。
今日の日付: ${todayStr}（年が明記されていない場合は${yearStr}年とする）

以下のメール内容から、Googleカレンダーに登録すべき情報を抽出してください。

件名: ${subject}
本文: ${body}

【抽出対象】
- 休園日・休校日 / 早帰り / 給食なしの日
- イベント・行事 / 提出物の締め切り / 保護者会・面談

以下のJSON形式で返してください。

\`\`\`json
[
  {
    "title": "保育園 休園",
    "date": "2026-04-01",
    "allDay": true,
    "description": "詳細・注意事項",
    "priority": "high"
  }
]
\`\`\``;
```

`priority` を `high` / `normal` に分けることで、休園・早帰り・給食なしは**前日＋1時間前の二重ポップアップ通知**を設定しています。それ以外のイベントは前日のみの通知です。

### 3. 重複防止：処理済みラベル

同じメールを二重登録しないよう、処理済みのメールには「コドモン処理済み」ラベルを自動付与します。

```
function markAsProcessed(message) {
  let label = GmailApp.getUserLabelByName('コドモン処理済み');
  if (!label) {
    label = GmailApp.createLabel('コドモン処理済み');
  }
  message.getThread().addLabel(label);
}
```

---

## セットアップ手順

### 1. Google Apps Scriptプロジェクトを作成

[script.google.com](https://script.google.com) で新規プロジェクトを作成し、`Code.gs` と `constants.gs` を作成してコードを貼り付けます。

### 2. Claude APIキーを設定

「プロジェクトの設定」→「スクリプトプロパティ」に以下を追加：

| キー | 値 |
| --- | --- |
| `CLAUDE_API_KEY` | AnthropicのAPIキー |

### 3. カレンダーIDを設定

`constants.gs` の `CALENDAR_ID` を変更します。メインカレンダーなら `'primary'` のままでOK。

### 4. 動作確認

`testWithLatestEmail` 関数を手動実行して、最新のコドモンメールが正しく処理されるか確認します。

### 5. トリガー設定

`setupTrigger` 関数を一度実行すると、**毎週金曜22時の自動実行**が設定されます。

---

## 実際に動かしてみた結果

「保育園 休園のお知らせ」というメールが届いた後、自動的に以下がカレンダーに登録されました：

* タイトル：`保育園 休園`
* 日付：メール本文から正確に抽出
* ポップアップ通知：前日＋1時間前（二重設定）※ `priority: high` の場合。`normal` は前日のみ

手動で入力する手間がゼロになり、見落としもなくなりました。

---

## 現在の制限と今後

**現在の制限**

* 日付が本文に明記されていないメールは登録されない
* コドモン専用（スクリレ・BANDは未対応）

**Phase2 予定**

* スクリレ（学校）：メール通知がないためiOSショートカット＋スクショ解析で対応予定
* BAND（習い事）：同上

---

## まとめ

GAS + Claude APIの組み合わせは、**メール解析 × カレンダー登録**のような「構造化されていない自然言語を扱うタスク」に非常に相性がいいです。

サーバーレスで動き、GASの無料枠内に収まる点も実用的でした。

コードはGitHubで公開しています。

<https://github.com/nori-sasa-dev/education-architect-pocs/tree/main/pocs/family_hub>
