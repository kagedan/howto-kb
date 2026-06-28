---
id: "2026-06-29-スプレッドシートの長文を1件ずつ読むのをやめた-gasclaude-apiで一括要約を自動化-01"
title: "スプレッドシートの長文を1件ずつ読むのをやめた ― GAS×Claude APIで一括要約を自動化"
url: "https://note.com/taka_gas_ai/n/nc4836332ab37"
source: "note"
category: "ai-workflow"
tags: ["API", "note"]
date_published: "2026-06-29"
date_collected: "2026-06-29"
summary_by: "auto-rss"
query: ""
---

スプレッドシートに溜まった問い合わせ本文やレビュー、議事録を、1行ずつ手で要約していませんか。GAS（Google Apps Script）からClaude APIを呼べば、指定した列の長文をまとめて要約し、隣の列に書き出せます。コピペで動くスクリプトを置いておくので、APIキーを設定すれば一括で処理できます。

## こんな人向け / 何が解決するか

## 準備するもの

* 対象のスプレッドシート（1列目に本文、2列目に要約を書き出す想定。1行目はヘッダ）
* Anthropic の APIキー（コンソールで発行）
* スプレッドシートの「拡張機能」→「Apps Script」を開ける状態

## 手順

### 1. APIキーをスクリプトプロパティに登録する

キーはコードに直書きせず、プロジェクト設定に保存します。Apps Scriptエディタの「プロジェクトの設定（歯車アイコン）」→「スクリプト プロパティ」で、プロパティ名 `CLAUDE\_API\_KEY`、値に発行したキーを登録します。こうしておくとコードを共有してもキーが漏れません。

### 2. スクリプトを貼り付ける

「拡張機能 → Apps Script」を開き、以下を貼り付けます。`MODEL` は安価なバルク要約向きの `claude-haiku-4-5` にしています。

```
// キーはハードコードせず、スクリプトプロパティから読む
const API_KEY = PropertiesService.getScriptProperties().getProperty('CLAUDE_API_KEY');
// 安価なバルク要約向き。品質を上げたいときは 'claude-sonnet-4-6' に変える
const MODEL = 'claude-haiku-4-5';

function summarizeColumn() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const rows = sheet.getDataRange().getValues();
  // 1行目はヘッダなので i = 1 から。1列目=本文、2列目=要約
  for (let i = 1; i < rows.length; i++) {
    const text = rows[i][0];
    if (!text || rows[i][1]) continue; // 空 or 要約済みはスキップ
    sheet.getRange(i + 1, 2).setValue(summarizeText(text));
    Utilities.sleep(500); // レート制限に配慮して少し待つ
  }
}

function summarizeText(text) {
  const payload = {
    model: MODEL,
    max_tokens: 300,
    messages: [
      { role: 'user', content: `次の文章を日本語で3行に要約してください。\n\n${text}` }
    ]
  };
  const res = UrlFetchApp.fetch('https://api.anthropic.com/v1/messages', {
    method: 'post',
    contentType: 'application/json',
    headers: {
      'x-api-key': API_KEY,
      'anthropic-version': '2023-06-01' // 必須。固定値
    },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true // エラー時もレスポンスを受け取って確認する
  });
  const data = JSON.parse(res.getContentText());
  // 応答の本文は content 配列の先頭テキストブロックに入る
  if (data.content && data.content[0]) {
    return data.content[0].text;
  }
  return 'ERROR: ' + res.getContentText();
}
```

## 動作確認

1列目に長文を数件入れ、`summarizeColumn` を手動で実行します。初回は外部リクエストの承認を求められるので許可します。2列目に3行の要約が入れば成功です。要約済みの行は再実行してもスキップされます。

## つまずきポイント

* **401や認証エラー** → スクリプトプロパティのキー名が `CLAUDE\_API\_KEY` になっているか、値に余分な空白が入っていないか確認します。
* **要約が入らずERRORになる** → `muteHttpExceptions: true` のおかげでレスポンス本文がそのまま入ります。`anthropic-version` の値や `model` の指定を見直します。
* **件数が多くて止まる** → GASは1回の実行時間に上限があります。処理する行数を区切るか、トリガーで分割実行します。
* **コストが気になる** → まずは `claude-haiku-4-5` で十分なことが多いです。要約品質を上げたいときだけ `claude-sonnet-4-6` に切り替えます。

## 応用・次の一歩

* 要約だけでなく「分類ラベル」を付ける：プロンプトを「次の問い合わせを『不具合／要望／質問』のいずれかに分類して」に変える。
* 1行ずつでなく複数行をまとめて1リクエストにして、件数の多いデータでも回数を減らす。
* トリガーで定期実行し、新しく追加された行だけを自動で要約する。

## まとめ

* GASの `UrlFetchApp` から `[https://api.anthropic.com/v1/messages`](https://api.anthropic.com/v1/messages%60) を叩けばAI要約を組み込める
* 必須ヘッダは `x-api-key` と `anthropic-version: 2023-06-01`、ボディは `model`・`max\_tokens`・`messages`
* キーはスクリプトプロパティに保存し、安価なバルク用途は `claude-haiku-4-5` から始める
