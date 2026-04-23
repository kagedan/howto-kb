---
id: "2026-03-28-claude-codeで海外saas-hightouch-のuiを日本語化するブラウザ拡張機能を作っ-01"
title: "Claude Codeで海外SaaS (Hightouch) のUIを日本語化するブラウザ拡張機能を作ってみた"
url: "https://qiita.com/justin_hieher/items/dcac59891591219e168c"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-03-28"
date_collected: "2026-03-29"
summary_by: "auto-rss"
---

## はじめに

私は業務で[Hightouch](https://growth-marketing.jp/hightouch/)という海外SaaSの提供に携わっているのですが、UIが英語中心なこともあり、幅広いユーザーの利用を考えると少し敷居が高いよな…と感じることが多くありました。

製品のUI自体はかなり使いやすいので「言語が日本語に対応してくれたらな」と思いHightouch社にも何度か伝えていましたが、日本語対応には少し時間がかかりそうでした。

また「翻訳のアプリケーションを自分で作るか」と思いもしましたが、私はエンジニアではないのでハードルは高く、これまでは諦めていました。

そんな中、昨今話題の[Claude Code](https://claude.ai/claude-code)を興味本位で個人で使っていた時に、「これでブラウザの拡張機能作れるんじゃないか？」と思い作ってみたところ、思いの他ちゃんとしたものができたので紹介します。

---

## Hightouchとは

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3908381%2F04db6f23-a152-43d8-b9b5-61def5dc0360.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=499b21d1f92b373366bbc28ce0d2ccc7)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3908381%2F04db6f23-a152-43d8-b9b5-61def5dc0360.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=499b21d1f92b373366bbc28ce0d2ccc7)

[Hightouch](https://growth-marketing.jp/hightouch/)は、クラウドデータウェアハウス（BigQuery、Snowflakeなど）に蓄積されたデータを、各種マーケティングツール（Salesforce、Braze、Google Ads 等）にノーコードで連携できる**リバースETL/CDPプラットフォーム**です。

従来のCDP製品とは異なり、Hightouch自体ではデータを持たず、データソースを自社で管理するデータウェアハウスに一元化できることが特徴です。

ただ、**UIは現状ほぼ英語**。機能自体はノーコードでとても使く、UIもシンプルなのですが、英語が苦手な方や、初めて触るマーケターには少し取っつきにくい印象がありました。

---

## 作ったもの

プロダクト：**[hightouch-ja](https://github.com/justin-hieher/hightouch-ja)** (GitHubで公開しています)

HightouchのUIをより精度の高い日本語に翻訳するChrome/Edge向けブラウザ拡張機能です。

機能をONにした状態でHightouchのサービス画面にアクセスするだけで、UIのメニュー・ボタン・ステータス表示などが自動的に日本語化されます。

**主な特徴：**

* ナビゲーション、ステータス、ボタン類など1,000件以上の翻訳に対応
* ON/OFFをトグルで切り替え可能
* データやSQLエディタなどの入力エリアは翻訳対象外（翻訳が不要な箇所を制御するようにしました）
* 外部への通信は一切なし（完全オフライン動作）

[![Screenshot 2026-03-27 at 13.02.11.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3908381%2F2fef53ae-a253-47c4-8bb0-f6b4913f71dd.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=36ed282cd9b2d493eefe87b2aa9ea118)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3908381%2F2fef53ae-a253-47c4-8bb0-f6b4913f71dd.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=36ed282cd9b2d493eefe87b2aa9ea118)  
(※Hightouchの実際のUIと拡張機能のON/OFF切り替え)

---

## 使い方

Chrome Web Storeへの申請はしていないので、GitHubから直接インストールします。

### 1. ZIPをダウンロード

[GitHubのReleasesページ](https://github.com/justin-hieher/hightouch-ja/releases)から最新の `hightouch-ja-vX.X.X.zip` をダウンロードして解凍します。

### 2. 拡張機能として読み込む

(Chromeの場合)

1. Chromeのアドレスバーに `chrome://extensions` と入力
2. 右上の「デベロッパーモード」をONにする
3. 「パッケージ化されていない拡張機能を読み込む」をクリック
4. 解凍したフォルダを選択

### 3. Hightouchにアクセスするだけ

`app.hightouch.com` を開けば、自動的に日本語表示になります。

---

## 仕様のポイント

今回は非エンジニアによる作成でしたが、細かい仕様まで考慮してClaude codeが作成してくれました。

### 辞書ファイルで翻訳を管理

この拡張機能の翻訳は `translations/ja.json` という辞書ファイルで一元管理しています。

```
{
  "Syncs": "同期",
  "Models": "モデル",
  "Destinations": "送信先",
  "Running": "実行中",
  "Failed": "失敗"
}
```

この辞書を編集すれば、**自社の用語に合わせたカスタマイズ**ができます。たとえば「Destination」を「送信先」ではなく「配信先」にしたい場合も、辞書を1行書き換えるだけです。

HightouchのUI自体が更新されて新しい文言が増えた場合も、辞書に追記するだけで対応できます。

### Claudeで翻訳追加もできる

辞書ファイル自体は平易なJSON形式なので、Claude等のAIに辞書ファイルを渡して「この英語テキストの翻訳を追加して」と依頼することで、エンジニアでなくても翻訳の追加・修正ができます。

### オープンソース（MIT）

[GitHubで公開](https://github.com/justin-hieher/hightouch-ja)しているので、誰でもダウンロードして利用できます。  
(もし使ってみた方がいて翻訳の改善やバグ報告があればぜひお願いします。)

---

## Claude Codeで作ってみた感想

自分はエンジニアではないのですが、Claude Codeを使うことで「こういう動きにしたい」をコードに落とし込む部分をほぼ任せることができました。

例えば、Hightouchの場合はUI上でデータをプレビューしたりSQLエディタを開けたりするので、そうした翻訳して欲しくない箇所はそのままにするような調整が必要でした。

また、UIに直接記載されている文章以外のホバーで表示される文章などもあり、単純に表示されたものを翻訳するだけの仕様では使いやすさがあまり向上しない感覚がありました。

こうした細かい要件に対してもClaude codeは結構柔軟に、よしなに対応してくれました。  
コードを書く、というより**どう動いてほしいかを説明する**作業が中心で、むしろユーザーに対する理解が求められた印象で非エンジニアの私でもスムーズに作業ができました。

作成にかかった時間も半日程度で、「土曜に作り、日曜に手直しする。」ぐらいの作業量でできました。

## おわりに

今回は私がずっと抱えていた課題を、Claude codeを活用することでかなりあっさりと解消することができました。  
(これでHightouchももっと使いやすくなったはず。)

非エンジニアでもこれだけできるとは思っていなかったので、正直驚きでした。

今Claude codeについて調べると「skills」や「subagents」、「Claude dispatch」など色々な新しい言葉が出てきて正直「うっ」となりますが、私のような初心者にとっては「とにかくまず触ってみる」が大事だなと改めて思わされました。  
それこそ分からないことはやっていく中でAIに聞けば良いですし。

今後も積極的に活用して、できれば個人利用だけでなく誰かの役に立てるようなものも共有できたらなと思いました。

作成した拡張機能のGitHubリポジトリ：<https://github.com/justin-hieher/hightouch-ja>

#### ※免責事項

この拡張機能は個人による開発です。動作の保証や、利用による動作不具合等については一切の責任を負いかねます。ご利用される場合はMITライセンスのもと自己責任でお願いします。
