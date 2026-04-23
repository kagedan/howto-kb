---
id: "2026-03-26-googleスプレッドシートでclaude-apiを使う方法gasで実装コード付き-01"
title: "GoogleスプレッドシートでClaude APIを使う方法【GASで実装、コード付き】"
url: "https://zenn.dev/ino38/articles/claude-api-google-sheets-gas"
source: "zenn"
category: "ai-workflow"
tags: ["API", "zenn"]
date_published: "2026-03-26"
date_collected: "2026-03-27"
summary_by: "auto-rss"
---

## はじめに

Anthropicが提供するClaude APIをGoogle Apps Script（GAS）から呼び出すことで、Googleスプレッドシート上で翻訳・要約・分類・感情分析などのAI処理を実行できます。`=CLAUDE_TRANSLATE(A1)` のようなカスタム関数として使えるようにすると、ExcelのVLOOKUPと同じ感覚でAI処理をセル関数として書けるようになります。

この記事では、GASからClaude APIを呼び出す基本コードから、スプレッドシートのカスタム関数として使えるようにするところまで実装方法を解説します。

---

## 前提

* Anthropicのアカウントがあり、APIキーを発行済みであること
* Googleスプレッドシートを操作できること

APIキーは [Anthropic Console](https://console.anthropic.com/) で発行できます。

---

## Claude APIをGASから呼び出す基本コード

まずGASエディタ（スプレッドシートのメニュー「拡張機能」→「Apps Script」）を開き、以下のコードを貼り付けます。

```
// APIキーはスクリプトプロパティから取得する（ハードコード禁止）
function getApiKey() {
  return PropertiesService.getScriptProperties().getProperty("ANTHROPIC_API_KEY");
}

/**
 * Claude APIにリクエストを送信する基本関数
 * @param {string} prompt - 送信するプロンプト
 * @param {string} model - 使用するモデル（省略時はhaiku）
 * @returns {string} Claudeの応答テキスト
 */
function callClaude(prompt, model) {
  model = model || "claude-haiku-4-5";

  var payload = {
    model: model,
    max_tokens: 1024,
    messages: [
      { role: "user", content: prompt }
    ]
  };

  var options = {
    method: "post",
    contentType: "application/json",
    headers: {
      "x-api-key": getApiKey(),
      "anthropic-version": "2023-06-01"
    },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };

  var response = UrlFetchApp.fetch("https://api.anthropic.com/v1/messages", options);
  var result = JSON.parse(response.getContentText());

  if (result.error) {
    throw new Error("API Error: " + result.error.message);
  }

  return result.content[0].text;
}
```

### APIキーの設定方法

APIキーをコードに直接書くのはセキュリティ上のリスクになります。スクリプトプロパティを使って外部から注入します。

1. GASエディタの左メニュー「プロジェクトの設定」（歯車アイコン）を開く
2. 「スクリプト プロパティ」→「プロパティを追加」
3. プロパティ名: `ANTHROPIC_API_KEY`、値: AnthropicのAPIキーを入力
4. 「スクリプト プロパティを保存」

---

## カスタム関数として実装する

### 翻訳関数

```
/**
 * テキストを指定した言語に翻訳する
 * スプレッドシートで =CLAUDE_TRANSLATE(A1, "English") として使用
 * @param {string} text - 翻訳するテキスト
 * @param {string} targetLang - 翻訳先の言語（例: "English", "日本語"）
 * @returns {string} 翻訳されたテキスト
 */
function CLAUDE_TRANSLATE(text, targetLang) {
  if (!text) return "";
  targetLang = targetLang || "English";

  var prompt = "Translate the following text to " + targetLang + ". Output only the translation, nothing else.\n\n" + text;
  return callClaude(prompt, "claude-haiku-4-5");
}
```

**使い方:**

```
=CLAUDE_TRANSLATE(A1, "English")     → A1の内容を英語に翻訳
=CLAUDE_TRANSLATE(B2, "日本語")     → B2の内容を日本語に翻訳
```

### 要約関数

```
/**
 * テキストを指定した文字数に要約する
 * @param {string} text - 要約するテキスト
 * @param {number} maxChars - 最大文字数（省略時は200）
 * @returns {string} 要約されたテキスト
 */
function CLAUDE_SUMMARIZE(text, maxChars) {
  if (!text) return "";
  maxChars = maxChars || 200;

  var prompt = "以下のテキストを" + maxChars + "文字以内で要約してください。要約文だけを出力してください。\n\n" + text;
  return callClaude(prompt, "claude-haiku-4-5");
}
```

**使い方:**

```
=CLAUDE_SUMMARIZE(A1)        → 200文字以内で要約
=CLAUDE_SUMMARIZE(A1, 100)   → 100文字以内で要約
```

### 分類関数

```
/**
 * テキストを指定したカテゴリに分類する
 * @param {string} text - 分類するテキスト
 * @param {string} categories - カンマ区切りのカテゴリ一覧
 * @returns {string} 分類結果（カテゴリ名のみ）
 */
function CLAUDE_CLASSIFY(text, categories) {
  if (!text) return "";
  categories = categories || "ポジティブ,ネガティブ,ニュートラル";

  var prompt = "以下のテキストを次のカテゴリのいずれかに分類してください。カテゴリ名だけを出力してください。\n"
    + "カテゴリ: " + categories + "\n\n"
    + "テキスト: " + text;
  return callClaude(prompt, "claude-haiku-4-5");
}
```

**使い方:**

```
=CLAUDE_CLASSIFY(A1)                                        → ポジティブ/ネガティブ/ニュートラルに分類
=CLAUDE_CLASSIFY(A1, "技術,営業,マーケティング,その他")    → 部門カテゴリに分類
```

### 感情分析関数

```
/**
 * テキストの感情スコアを1〜5で返す
 * @param {string} text - 分析するテキスト
 * @returns {number} 感情スコア（1=非常にネガティブ、5=非常にポジティブ）
 */
function CLAUDE_SENTIMENT(text) {
  if (!text) return "";

  var prompt = "以下のテキストの感情を1〜5のスコアで評価してください。1=非常にネガティブ、3=ニュートラル、5=非常にポジティブ。数字だけを出力してください。\n\n" + text;
  var result = callClaude(prompt, "claude-haiku-4-5");
  return parseInt(result.trim()) || 3;
}
```

---

## バッチ処理でAPI制限を回避する

カスタム関数はセルごとに個別にAPIを呼び出すため、大量のセルに適用するとAPI制限に引っかかることがあります。バッチ処理関数を作っておくと安全です。

```
/**
 * A列のテキストをまとめて翻訳してB列に書き出す
 * セルごとにカスタム関数を書くよりも安全で高速
 */
function batchTranslate() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getActiveSheet();

  var lastRow = sheet.getLastRow();
  var sourceRange = sheet.getRange(2, 1, lastRow - 1, 1); // A2から最終行
  var sourceValues = sourceRange.getValues();

  var results = [];

  for (var i = 0; i < sourceValues.length; i++) {
    var text = sourceValues[i][0];

    if (!text) {
      results.push([""]); // 空白セルはスキップ
      continue;
    }

    try {
      var translated = CLAUDE_TRANSLATE(text, "English");
      results.push([translated]);

      // API制限対策: 1リクエストごとに1秒待機
      if (i < sourceValues.length - 1) {
        Utilities.sleep(1000);
      }
    } catch (e) {
      results.push(["Error: " + e.message]);
    }
  }

  // B列に一括書き込み
  sheet.getRange(2, 2, results.length, 1).setValues(results);
  Logger.log("翻訳完了: " + results.length + "件");
}
```

---

## API料金の目安

Claude APIは使用量に応じた従量課金です（2025年時点）。

| モデル | 入力 | 出力 | 用途 |
| --- | --- | --- | --- |
| claude-haiku-4-5 | $0.80/MTok | $4.00/MTok | 翻訳・分類・要約などの単純タスク |
| claude-sonnet-4-5 | $3.00/MTok | $15.00/MTok | 複雑な文章生成・コード生成 |

**スプレッドシートでの実用的な目安:**

```
翻訳（1セル、平均200文字）のトークン数:
  プロンプト: 約100トークン
  応答: 約100トークン
  合計: 約200トークン

Haikuモデルでの1セルあたりのコスト:
  0.80 × (100/1,000,000) + 4.00 × (100/1,000,000)
  ≒ $0.00048 / セル

100セル翻訳する場合: 約$0.048（約7円）
1,000セル翻訳する場合: 約$0.48（約70円）
```

日常的な業務での使用では、月に数百円程度に収まることがほとんどです。

---

## ユースケース別の使い方

### 1. 多言語アンケートの日本語化

英語・中国語・韓国語が混在した顧客フィードバックを全て日本語に統一する。

```
A列: 元のフィードバック（多言語）
B列: =CLAUDE_TRANSLATE(A1, "日本語")
C列: =CLAUDE_CLASSIFY(B1, "機能要望,バグ報告,クレーム,称賛,その他")
D列: =CLAUDE_SENTIMENT(B1)
```

### 2. 商品説明文の自動生成

商品名と特徴をインプットとして、ECサイト用の説明文を一括生成する。

```
function generateProductDescription(productName, features) {
  var prompt = "以下の商品の説明文を150文字以内で書いてください。\n"
    + "商品名: " + productName + "\n"
    + "特徴: " + features;
  return callClaude(prompt, "claude-haiku-4-5");
}
```

### 3. 問い合わせメールの分類・優先度付け

問い合わせ内容を自動で分類して、担当者に振り分けるシートを作る。

```
A列: 問い合わせ本文
B列: =CLAUDE_CLASSIFY(A1, "技術サポート,返品・交換,請求・支払い,その他")
C列: =CLAUDE_SENTIMENT(A1)  // 1〜5で優先度の参考に
D列: =CLAUDE_SUMMARIZE(A1, 100)  // 担当者向け要約
```

---

## まとめ

* GASの `UrlFetchApp.fetch` でClaude APIを呼び出せる
* APIキーは `PropertiesService` で管理する（コードに直書きしない）
* カスタム関数として実装するとExcelの関数と同じ感覚で使える
* 大量処理は `Utilities.sleep(1000)` でAPI制限を回避する
* Haikuモデルであれば100セル処理しても約7円程度

スプレッドシートにAI処理を組み込むと、人間がやっていた分類・翻訳・要約の定型作業をほぼゼロにできます。処理量が増えれば増えるほど効果が出てきます。

---

## 100プロンプト集 + GASカスタム関数セットを配布中

この記事で紹介した翻訳・要約・分類・感情分析以外にも、業務で使えるプロンプト100個とGASカスタム関数をまとめたセットをGumroadで販売しています。コピー&ペーストですぐに使えます。

[Claude Prompt Pack for Business（Gumroad - $19）](https://inoshu.gumroad.com/l/etlfbf)
