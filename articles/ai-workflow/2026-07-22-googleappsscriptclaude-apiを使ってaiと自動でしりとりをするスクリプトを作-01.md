---
id: "2026-07-22-googleappsscriptclaude-apiを使ってaiと自動でしりとりをするスクリプトを作-01"
title: "【GoogleAppsScript】Claude APIを使って、AIと自動で「しりとり」をするスクリプトを作ってみた"
url: "https://qiita.com/kazukichi_0914/items/c0914b38655c52f23d6a"
source: "qiita"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "JavaScript", "qiita"]
date_published: "2026-07-22"
date_collected: "2026-07-23"
summary_by: "auto-rss"
query: ""
---

Google Apps Script (GAS) と Anthropicの「Claude API」を連携させて、**AIと自動でしりとりをし続けるスクリプト**を作成しました。

GAS上で再帰処理を行い、AIが返した単語の「最後の文字」を判定して次のプロンプトを生成する仕組みです。

## 構成と流れ
1. スクリプトの実行（最初の単語は「びーる」からスタート）
2. 単語の最後の文字を取得（小文字や長音符も適切に処理）
3. Claude APIに「〇〇から始まる単語を1つ出して」とリクエスト
4. レスポンスを受け取り、ルール（ん で終わっていないか、既出ではないか等）をチェック
5. 再び2に戻る（最大20ターン）

---

## 事前準備：APIキーの取得とGASへの安全な保存（シークレット格納）

APIキーをコード内に直接ベタ書きするのはセキュリティ上危険です。GASには環境変数の代わりとなる**「スクリプト プロパティ」**という機能があるため、そちらにAPIキーを格納します。

### 1. Claude APIキーの取得
[Anthropic Console](https://console.anthropic.com/) にアクセスし、アカウント作成・ログインをして API Key を発行します。（※利用にはクレジットのチャージが必要です）

### 2. GASのプロジェクト設定にAPIキーを登録
1. GASのエディタ画面左側のメニューから **歯車アイコン（プロジェクトの設定）** をクリックします。
2. 一番下までスクロールし、**「スクリプト プロパティ」** の **「スクリプト プロパティを追加」** をクリックします。
3. 以下のように入力します：
   - **プロパティ**: `ANTHROPIC_API_KEY`
   - **値**: `sk-ant-api03-...` (取得したAPIキー)
4. **「スクリプト プロパティを保存」** をクリックします。

これで、コード内から `PropertiesService.getScriptProperties().getProperty('ANTHROPIC_API_KEY')` として安全にキーを呼び出せるようになります。

---

## ソースコード (GAS)

GASのエディタ（`コード.gs`）に以下のコードを貼り付けます。
※ `MODEL` の部分は、利用可能なClaudeのモデル名（例: `claude-3-5-sonnet-20241022` など）に変更して使用してください。

```javascript
// ===== 設定 =====
const MODEL = 'claude-3-5-sonnet-20241022'; // 利用可能なモデル名に変更してください
const MAX_TURNS = 20;              // 最大ターン数(無限再帰の防止)

/**
 * エントリーポイント。実行するとログにしりとりの流れが出ます。
 */
function playShiritori() {
  const startWord = 'びーる';
  const history = [startWord];

  Logger.log('開始: ' + startWord);
  const result = shiritoriRecursive(startWord, history, 1);

  Logger.log('--- 結果 ---');
  Logger.log(result.reason);
  Logger.log('単語数: ' + result.history.length);
  Logger.log(result.history.join(' → '));
}

/**
 * 再帰的にしりとりを進める本体
 * @param {string} prevWord 直前の単語
 * @param {string[]} history これまでに出た単語
 * @param {number} turn 現在のターン
 */
function shiritoriRecursive(prevWord, history, turn) {
  // 終了条件1: 最大ターン到達
  if (turn > MAX_TURNS) {
    return { history: history, reason: '最大ターン数に到達しました' };
  }

  // 終了条件2:「ん」で終わっている
  const lastChar = getLastKana(prevWord);
  if (lastChar === 'ん') {
    return { history: history, reason: '「' + prevWord + '」が「ん」で終わったので終了' };
  }

  // Claudeに次の単語を考えてもらう
  const nextWord = askClaudeForNextWord(lastChar, history);

  // 終了条件3: 有効な単語が得られなかった
  if (!nextWord) {
    return { history: history, reason: 'Claudeが続けられませんでした' };
  }

  // ルール検証: 正しい文字で始まっているか
  if (nextWord.charAt(0) !== lastChar) {
    return {
      history: history,
      reason: '「' + nextWord + '」が「' + lastChar + '」で始まっていないため終了'
    };
  }

  // 終了条件4: 既出の単語
  if (history.indexOf(nextWord) !== -1) {
    return { history: history, reason: '「' + nextWord + '」は既出のため終了' };
  }

  Logger.log(turn + ': ' + nextWord);
  history.push(nextWord);

  // 再帰呼び出し
  return shiritoriRecursive(nextWord, history, turn + 1);
}

/**
 * Claude APIに次の単語を問い合わせる
 */
function askClaudeForNextWord(startChar, history) {
  const apiKey = PropertiesService.getScriptProperties().getProperty('ANTHROPIC_API_KEY');
  if (!apiKey) throw new Error('ANTHROPIC_API_KEY が設定されていません');

  const prompt =
    'しりとりをしています。次のルールに厳密に従い、単語を1つだけ答えてください。\n' +
    '- 「' + startChar + '」で始まるひらがなの名詞\n' +
    '- できるだけ「ん」で終わらない単語にする\n' +
    '- すでに出た単語は使わない: ' + history.join('、') + '\n' +
    '- 出力はひらがなの単語のみ。説明・記号・句読点は一切書かない';

  const payload = {
    model: MODEL,
    max_tokens: 50,
    messages: [{ role: 'user', content: prompt }]
  };

  const options = {
    method: 'post',
    contentType: 'application/json',
    headers: {
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01'
    },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };

  const response = UrlFetchApp.fetch('[https://api.anthropic.com/v1/messages](https://api.anthropic.com/v1/messages)', options);
  const code = response.getResponseCode();
  if (code !== 200) {
    Logger.log('APIエラー(' + code + '): ' + response.getContentText());
    return null;
  }

  const data = JSON.parse(response.getContentText());
  const text = data.content.map(function (b) { return b.text || ''; }).join('').trim();
  return normalizeWord(text);
}

/**
 * しりとりで使う「最後のかな」を返す
 * - 長音符(ー)は直前の文字で代用
 * - 小書き文字は大書きに変換
 */
function getLastKana(word) {
  const chars = word.split('');
  let last = chars[chars.length - 1];

  if (last === 'ー' && chars.length >= 2) {
    last = chars[chars.length - 2];
  }

  const smallToLarge = {
    'ゃ': 'や', 'ゅ': 'ゆ', 'ょ': 'よ', 'っ': 'つ',
    'ぁ': 'あ', 'ぃ': 'い', 'ぅ': 'う', 'ぇ': 'え', 'ぉ': 'お'
  };
  if (smallToLarge[last]) last = smallToLarge[last];

  return last;
}

/**
 * Claudeの出力からひらがな以外を除去
 */
function normalizeWord(text) {
  const cleaned = text.replace(/[^ぁ-んー]/g, '');
  return cleaned.length > 0 ? cleaned : null;
}
```

コードのポイント解説
1. しりとりの文字処理（getLastKana）
しりとり特有のルールとして、「コーヒー」のように長音符（ー）で終わる場合はその1つ前の文字を採用し、「きんぎょ」のように小文字（ょ）で終わる場合は大文字（よ）として扱う必要があります。
この部分は getLastKana() 関数で吸収するように実装しています。

2. プロンプトの工夫
Claudeに余計な会話や解説をさせず、「単語のみを返してほしい」という制約を強くプロンプトに書いています。また、これまで出た単語の配列 (history.join('、')) を渡し、既出単語のループを防ぐようにしています。

3. APIリクエストのエラーハンドリング
muteHttpExceptions: true を設定し、もしAPIエラー（Rate Limitや残高不足など）が返ってきてもスクリプトがクラッシュせず、エラーの内容をログに出力したうえで安全に終了するようにしています。

実行方法
GASのエディタ上部にある関数選択のプルダウンから playShiritori を選択し、「実行」 ボタンを押します。
（※初回実行時はGoogleのアクセス承認画面が出ますので、許可を進めてください）

実行結果のログ例
画面下の実行ログに、以下のように結果が出力されます。

開始: びーる
1: るびー
2: びじゅつかん
--- 結果 ---
「びじゅつかん」が「ん」で終わったので終了
単語数: 3
びーる → るびー → びじゅつかん

これで確かにしりとりが可能なコードをClaudeで記述できました。
