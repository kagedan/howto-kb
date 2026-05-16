---
id: "2026-05-15-非エンジニアがclaudeと対話しながらgoogleマップの保存場所をaiに相談できる環境を作った話-01"
title: "非エンジニアがClaudeと対話しながら、Googleマップの保存場所をAIに相談できる環境を作った話"
url: "https://zenn.dev/machin/articles/e43347cc418337"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-05-15"
date_collected: "2026-05-16"
summary_by: "auto-rss"
query: ""
---

非エンジニア向けです。

非エンジニアでコードが書けない私が、Claude（AI）と対話しながら、Googleマップに保存してある場所（スター付き・行きたい場所・お気に入りなど）をスプレッドシートに自動同期して、ClaudeにDrive経由で参照させるしくみを作りました。

コードは全部Claudeに書いてもらっています。私がやったのは、やりたいことを伝えて、エラーやログを貼り付けて、「これ何が起きてる？」と聞き続けることだけ。

同じことをやってみたい方の参考になればと、つまずいたところも含めて全部残します。**読者のメインターゲットはエンジニアではなく、AIを使って何か作ってみたい人**を想定して書いています。

## 作りたかったもの

おでかけのとき、AIに行き先を相談できる環境です。

Googleマップに、行きたいお店やカフェを長年スターしてきました。数えてみたら **911件**。せっかく集めたのに、いざ「今日どこ行こう」となると、地図上のピンを眺めるばかりで活用できていない。

「来週末、表参道行くんだけど、保存してたカフェで良さそうなとこある？」  
「明日、京都に日帰りするんだけど、行きたい場所リストから回れるルート組んで」

こんなふうに、自分のリストを踏まえた上でAIに相談できたら最高だな、と。

## できあがったもの

Claudeチャットで、自分のグーグルマップのスターや行きたいところを参照してもらいながら、Claudeに相談できるツールができました。  
プロジェクト機能を使って、好みや車で移動することが多いことなどを伝えています。

全体像はこんな流れです。

Google Takeoutで2ヶ月ごとに保存場所をDriveに自動エクスポート → DriveのzipをGASが毎日チェック → 新しいzipがあれば解凍してスプレッドシートに転記 → ClaudeのDriveコネクタからそのスプシを参照

人間のセットアップは初回のみ。あとは自動です。

## 手順

### 1. Google Takeoutで定期エクスポート設定

[Google Takeout](https://takeout.google.com/) で以下の項目にチェック。

* **マップ（マイプレイス）** ← 本命。スター付き・行きたい場所・保存済みリストが含まれます
* マップ
* マイマップ

配信方法を「Google ドライブに追加」、頻度を「1年間、2か月ごとにエクスポート」に。

**注意点**: 「マップ」と「マップ（マイプレイス）」は別カテゴリです。私は最初「マップ」だけ選んで肝心のリストが取れず空振りしました。

### 2. 転記先スプレッドシートを作成

新規スプレッドシートを作り、URLから ID をコピー（`/d/` と `/edit` の間）。

### 3. GASをセットアップ

[script.google.com](https://script.google.com/) で新規プロジェクト作成 → 以下のコードを貼り付け → `SPREADSHEET_ID` だけ自分の値に変更。

```
// ====== 設定 ======
const CONFIG = {
  TAKEOUT_FOLDER_NAME: 'Takeout',
  SPREADSHEET_ID: 'ここに自分のスプシIDを入れる',
  PROCESSED_PROP_KEY: 'processedZipIds',
  TARGET_PATH_KEYWORD: 'マップ',
};

function processNewTakeoutZips() {
  const folder = DriveApp.getFoldersByName(CONFIG.TAKEOUT_FOLDER_NAME).next();
  const zipFiles = folder.getFiles();
  const props = PropertiesService.getScriptProperties();
  const processedIds = JSON.parse(props.getProperty(CONFIG.PROCESSED_PROP_KEY) || '[]');
  
  while (zipFiles.hasNext()) {
    const zipFile = zipFiles.next();
    if (!zipFile.getName().toLowerCase().endsWith('.zip')) continue;
    const fileId = zipFile.getId();
    if (processedIds.includes(fileId)) continue;
    
    console.log(`処理開始: ${zipFile.getName()}`);
    try {
      extractAndImport(zipFile);
      processedIds.push(fileId);
      props.setProperty(CONFIG.PROCESSED_PROP_KEY, JSON.stringify(processedIds));
      console.log(`完了: ${zipFile.getName()}`);
    } catch (e) {
      console.error(`エラー: ${zipFile.getName()} - ${e.message}`);
    }
  }
}

function extractAndImport(zipFile) {
  const blobs = Utilities.unzip(zipFile.getBlob());
  const ss = SpreadsheetApp.openById(CONFIG.SPREADSHEET_ID);
  
  blobs.forEach(blob => {
    const name = blob.getName();
    if (!name.includes(CONFIG.TARGET_PATH_KEYWORD)) return;
    
    const lowerName = name.toLowerCase();
    const baseName = name.split('/').pop().replace(/\.(csv|json)$/i, '');
    const sheetName = baseName.substring(0, 95);
    let data = null;
    
    if (lowerName.endsWith('.csv')) {
      data = Utilities.parseCsv(blob.getDataAsString('UTF-8'));
    } else if (lowerName.endsWith('.json')) {
      data = jsonToTable(blob.getDataAsString('UTF-8'));
    } else {
      return;
    }
    
    if (!data || data.length === 0) return;
    
    let sheet = ss.getSheetByName(sheetName);
    if (sheet) ss.deleteSheet(sheet);
    sheet = ss.insertSheet(sheetName);
    
    const maxCols = Math.max(...data.map(row => row.length));
    const normalized = data.map(row => {
      const r = row.slice();
      while (r.length < maxCols) r.push('');
      return r;
    });
    
    sheet.getRange(1, 1, normalized.length, maxCols).setValues(normalized);
    sheet.getRange(1, 1, 1, maxCols).setFontWeight('bold');
    sheet.setFrozenRows(1);
    console.log(`  → シート作成: ${sheetName} (${normalized.length}行)`);
  });
}

function jsonToTable(jsonText) {
  let obj;
  try { obj = JSON.parse(jsonText); } catch (e) { return null; }
  
  let items = null;
  if (obj.features && Array.isArray(obj.features)) {
    items = obj.features.map(f => {
      const props = f.properties || {};
      const coords = (f.geometry && f.geometry.coordinates) || [];
      return { ...props, longitude: coords[0] || '', latitude: coords[1] || '' };
    });
  } else if (Array.isArray(obj)) {
    items = obj;
  } else {
    for (const key in obj) {
      if (Array.isArray(obj[key])) { items = obj[key]; break; }
    }
  }
  if (!items || items.length === 0) return null;
  
  const keySet = new Set();
  items.forEach(item => {
    if (typeof item === 'object' && item !== null) {
      Object.keys(item).forEach(k => keySet.add(k));
    }
  });
  const keys = Array.from(keySet);
  
  const table = [keys];
  items.forEach(item => {
    const row = keys.map(k => {
      const v = item[k];
      if (v === null || v === undefined) return '';
      if (typeof v === 'object') return JSON.stringify(v);
      return v;
    });
    table.push(row);
  });
  return table;
}

function setupTrigger() {
  ScriptApp.getProjectTriggers().forEach(t => {
    if (t.getHandlerFunction() === 'processNewTakeoutZips') ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('processNewTakeoutZips')
    .timeBased().everyDays(1).atHour(3).create();
}

function resetProcessedRecord() {
  PropertiesService.getScriptProperties().deleteProperty(CONFIG.PROCESSED_PROP_KEY);
}
```

`processNewTakeoutZips` を手動実行して動作確認 → `setupTrigger` を実行して毎日3時の自動実行をON。

### 4. ClaudeのDriveコネクタを有効化

Claudeの設定でGoogle Drive連携をONにして、上記スプレッドシートを参照できる状態に。

## ハマりどころ（全部Claudeとの対話で解決）

非エンジニアの私がClaudeとどうやって問題を解決していったか、過程をそのまま残します。

### つまずき1: 実行しても何も起きない

「実行開始」と「実行完了」が0.8秒で終わる。何も処理されていない。

Claudeに「実行数を見ると、期間が0.8秒でステータスが完了になっています」と伝えると、デバッグ用関数を提示してくれて、Drive内のzipは存在することを確認。

### つまずき2: zipのMIMEタイプ問題

ファイルは見つかっているのに処理対象になっていない。ログの `application/x-zip` という表記を見たClaudeが原因を特定。当初のコードは `MimeType.ZIP`（`application/zip`）でフィルタしていたため、Takeoutが出力する `application/x-zip` のzipは検出漏れになっていた、と。

**対処**: ファイル名の拡張子で判定する方式に変更。

```
if (!zipFile.getName().toLowerCase().endsWith('.zip')) continue;
```

### つまずき3: zipは解凍されるのに、シートにデータが入らない

「処理開始」「完了」は出るのに「シート作成」のログが出ない。

これも対話で原因判明。**zip内のフォルダパスは言語環境依存**で、日本語環境だと `Takeout/マップ/...` のようになっており、英語キーワード `Saved` ではマッチしませんでした。

**対処**: `TARGET_PATH_KEYWORD` を `'マップ'` に変更。さらにzip内ファイル一覧を表示するデバッグ関数を作って、実際のパスを確認してから設定するように。

### つまずき4: そもそも欲しいデータが入っていなかった

Takeout側のカテゴリ選択ミス。「マップ」と「マップ（マイプレイス）」は別物で、後者にスター付きリストが入っていました。

これも、Takeoutの選択画面の文言をClaudeに見せたら、説明文の「スター付きの場所と場所のクチコミの記録」という記述から本命を見つけてくれました。

最終的に **911件の保存場所** と **5件のクチコミ** が、スプレッドシートに自動転記される状態に。

## 使ってみて

「○○エリアで保存してたカフェある？」「ジャンル別に分類して」みたいに、保存リストを踏まえた相談ができるようになりました。

地図上のピンを眺めながら「えーっと何保存したっけ……」と探す時間がなくなり、過去の自分が集めた情報を、今の自分がちゃんと使える感覚があります。

## 非エンジニアが対話で作って気づいたこと

技術的には、GAS、zip、MIMEタイプ、文字コード、JSON構造などが関わっていて、自分で書こうとしたら絶対無理でした。

でも、**やりたいことを言葉で伝えて、起きた現象（ログ、エラー、画面の文言）をそのまま貼り付けて、対話を続ける**。これだけで、ここまでのものが作れました。

特に効果が大きかったのは、エラーや想定外の挙動が出たときに**ログをまるごと貼り付ける**こと。Claudeはそこから的確に原因を切り分けてくれます。

エンジニアの方からすると当たり前のことかもしれませんが、非エンジニアの感覚としては「コードが書けなくても、何かを作る経路ができている」という発見でした。同じような立場の方の参考になればうれしいです。

## 参考
