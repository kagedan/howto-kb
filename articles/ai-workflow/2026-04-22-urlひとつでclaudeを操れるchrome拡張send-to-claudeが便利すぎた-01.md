---
id: "2026-04-22-urlひとつでclaudeを操れるchrome拡張send-to-claudeが便利すぎた-01"
title: "URLひとつでClaudeを操れる。Chrome拡張「Send to Claude」が便利すぎた"
url: "https://qiita.com/yasu0000/items/1c80525cea58b9e27369"
source: "qiita"
category: "ai-workflow"
tags: ["API", "qiita"]
date_published: "2026-04-22"
date_collected: "2026-04-23"
summary_by: "auto-rss"
---

Claudeを日常的に使っている方、こんな経験はありませんか？

* 毎回同じようなプロンプトを手動でコピペしている
* 自分のWebアプリからClaudeにデータを投げたいけど、API利用はコストがかかる
* チームメンバーに「このプロンプトで聞いてみて」と共有するのが面倒

Send to Claude は、これらの課題をたった1つのChrome拡張で解決します。

---

## 何ができるの？

一言でいうと、**URLパラメーターやJavaScript APIを通じて、Claudeのプロンプトをプログラマブルに操作できる**Chrome拡張機能です。

これが何を意味するか。Claudeへのプロンプト入力を **「人間が手で打つもの」から「自動化できるもの」** に変えてくれるのです。

しかも、**Claude APIを使わず、ブラウザのClaude Chatをそのまま操作する仕組み**なので、APIの利用料金は一切かかりません。無料のClaudeアカウントでも、Claude Proでも、いつも使っているClaude Chatがそのまま自動化の対象になります。

---

## 一番の推しポイント：URLパラメーターでプロンプトを渡せる

使い方はシンプルすぎるほどシンプル。ClaudeのURLに `?prompt=` を付けるだけ。

```
https://claude.ai/new?prompt=今日の天気について教えて
```

このURLをブラウザで開くだけで、プロンプトが **自動入力＆自動送信** されます。たったこれだけ。

### これが何を可能にするか

#### 1. ブックマークがプロンプトになる

よく使う質問やプロンプトをブックマークに登録しておけば、**ワンクリックでClaudeに質問**できます。

```
📌 今日のニュース要約
https://claude.ai/new?prompt=今日の主要ニュースを3行で要約して

📌 英語メール添削
https://claude.ai/new?prompt=以下の英語メールを添削してください:&autosubmit=false
```

`autosubmit=false` を付ければ、プロンプトの入力だけで送信はしないので、後からテキストを追加してから送信することもできます。

#### 2. チームでプロンプトを共有できる

SlackやNotionにURLを貼るだけで、チーム全員が同じプロンプトでClaudeに質問できます。

> 「この障害の原因分析、このプロンプトで聞いてみて」  
> `https://claude.ai/new?prompt=以下のエラーログを分析して、根本原因と対策を提示してください:`

もう「どういうプロンプトで聞けばいいの？」と聞かれることはありません。

#### 3. 外部ツールからのリンクに埋め込める

ダッシュボードや社内ツールに「Claudeで分析」ボタンを設置することも可能。URLを動的に生成するだけで、あらゆるツールがClaudeと連携できます。

---

## もうひとつの武器：JavaScript APIで外部連携

URLパラメーターだけでも十分強力ですが、Send to Claudeはさらに踏み込んで **JavaScript API** も提供しています。

これにより、**自分のWebページやWebアプリから直接Claudeにプロンプトを送信**できます。

```
const extensionId = "あなたの拡張機能ID";

chrome.runtime.sendMessage(
  extensionId,
  {
    type: "autofill",
    prompt: "このデータを分析してください:\n" + yourData,
    autoSubmit: true
  },
  (response) => {
    if (response?.success) {
      console.log("Claudeに送信完了！");
    }
  }
);
```

### URLパラメーターとの違い

|  | URLパラメーター | JavaScript API |
| --- | --- | --- |
| **手軽さ** | ◎ URLを貼るだけ | ○ コードが必要 |
| **テキスト量** | △ URL長制限あり | ◎ 数千行でもOK |
| **動的データ** | △ 事前にエンコード必要 | ◎ 変数をそのまま渡せる |
| **ユースケース** | ブックマーク、リンク共有 | Webアプリ連携、データ分析 |

JavaScript APIなら、URLの長さ制限を気にせず **数千行のログやコードをまるごとClaudeに投げる** ことも可能です。

そして改めて強調したいのが、**これらすべてが無課金で使える**という点。通常、アプリケーションからClaudeを呼び出すにはClaude APIを契約し、トークン数に応じた従量課金が発生します。しかしSend to Claudeは、あくまでブラウザ上のClaude Chatを操作する拡張機能。APIキーの発行も不要、課金も一切なし。個人開発でも、チームでの試用でも、コストを気にせず気軽にClaude連携を試せます。

### async/awaitにも対応

モダンなJavaScriptに合わせて、Promise版も簡単に書けます。

```
function sendToClaude({ prompt, autoSubmit = true }) {
  return new Promise((resolve, reject) => {
    chrome.runtime.sendMessage(
      extensionId,
      { type: "autofill", prompt, autoSubmit },
      (response) => {
        if (chrome.runtime.lastError) {
          reject(new Error(chrome.runtime.lastError.message));
        } else if (response?.success) {
          resolve(response);
        } else {
          reject(new Error("送信に失敗しました"));
        }
      }
    );
  });
}

// 使い方
await sendToClaude({
  prompt: "以下のコードをレビューしてください:\n" + codeBlock,
  autoSubmit: true
});
```

---

## まだまだある便利機能

### 右クリックメニューで即送信

Webページ上のテキストを選択して右クリック → 「Claudeに送る」。これだけでClaudeの新しいタブが開き、選択テキストがプロンプトに入力されます。

気になる記事やエラーメッセージを、コピー＆ペーストなしでClaudeに送れます。

### カスタムプロンプト

「英語に翻訳」「要約して」「コードを説明して」など、よく使うプロンプトテンプレートを右クリックメニューに登録できます。

選択テキスト ＋ カスタムプロンプトが自動的に連結されるので、テキストを選んで右クリックするだけで **翻訳も要約もワンアクション** で完了します。

各カスタムプロンプトごとに自動送信の有効/無効を設定できるのも嬉しいポイントです。

### 8言語対応

日本語・英語・ドイツ語・スペイン語・フランス語・韓国語・ポルトガル語・中国語に対応。ブラウザの言語設定に合わせてUIが自動的に切り替わります。

---

## 活用アイデア

| シーン | 方法 |
| --- | --- |
| 毎朝のニュース要約 | URLをブックマーク登録 |
| コードレビュー依頼 | JavaScript APIで自動送信 |
| 記事の翻訳 | テキスト選択 → 右クリック → カスタムプロンプト |
| エラーログの分析 | JavaScript APIで大量テキスト送信 |
| チームへのプロンプト共有 | URLをSlack/Notionに貼る |
| 社内ツールとの連携 | APIで「Claudeで分析」ボタンを実装 |

---

## まとめ

**Send to Claude** の本質は、「Claudeをプログラマブルにする」ことにあります。

* **URLパラメーター**で、ブックマークやリンク共有を通じた手軽な自動化
* **JavaScript API**で、Webアプリからの本格的な外部連携

Claude APIの契約もAPIキーもサーバーサイドの実装も不要。**課金ゼロ**で、ブラウザだけでこれが実現できるのは画期的です。

Claudeをもっと日常のワークフローに溶け込ませたい方は、ぜひ試してみてください。

👉 **[Send to Claude - Chrome Web Store](https://chromewebstore.google.com/detail/send-to-claude/gcbomhdkipopmgjemnonhhmmfggffnno?authuser=0&hl=ja)**
