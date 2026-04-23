---
id: "2026-04-09-kabehub対応claudeさんgeminiさんchatgptさん-のapiキー取得方法まとめ-01"
title: "【KabeHub対応】Claudeさん・Geminiさん・ChatGPTさん のAPIキー取得方法まとめ"
url: "https://zenn.dev/ruimatsumoto/articles/8f5bd4a4f8ac5b"
source: "zenn"
category: "ai-workflow"
tags: ["API", "Gemini", "GPT", "zenn"]
date_published: "2026-04-09"
date_collected: "2026-04-10"
summary_by: "auto-rss"
query: ""
---

## 【KabeHub対応】Claudeさん・Geminiさん・ChatGPTさん のAPIキー取得方法まとめ

AIツール「KabeHub」を使うには、各AIサービスのAPIキーを自分で取得して設定する必要があります。  
この記事では3つのAPIキーの取得手順をまとめます。

> **APIキーとは？**  
> AIサービスを外部アプリから使うための「合言葉」のようなものです。KabeHubに登録することで、Claudeさん・Geminiさん・ChatGPTさんを直接利用できるようになります。キーはあなたのブラウザにのみ保存され、KabeHubのサーバーには送信されません。

> **💡 まず無料で試したい方へ**  
> GeminiさんのAPIキーは無料枠が太く、クレジットカード登録も不要です。まずGeminiさんだけ登録してKabeHubを試してみることをおすすめします。

---

## 1. Claudeさん（Anthropic）のAPIキー取得

### アカウント作成・クレジット購入

1. <https://console.anthropic.com> にアクセス
2. 「Sign up」からアカウントを作成（Googleアカウントでも可）
3. 「What type of account sounds right?」という画面が表示されるので「Individual」を選択
4. クレジット購入画面に進むので、最低金額（$5〜）を入力して購入する

![](https://static.zenn.studio/user-upload/7c86f1d81c28-20260409.png)

> ⚠️ ClaudeさんのAPIは無料枠がなく、最低$5（約750円〜）のクレジット購入が必要です。壁打ち用途なら$5で数週間〜1ヶ月程度使えます。

![](https://static.zenn.studio/user-upload/c7a50a948d74-20260409.png)  
*5ドルって高いですね*  
![](https://static.zenn.studio/user-upload/61589bff8efe-20260409.png)  
*You're in!の画面の右から作れます（最初のログインの時のみだと思います）*

### APIキーの発行

1. ログイン後、左メニューの「API Keys」をクリック
2. 「Create Key」ボタンをクリック
3. 「Name your key」にキー名を入力（例：`kabehub`）して「Add」をクリック
4. 「Save your API key」のポップアップに `sk-ant-...` で始まる文字列が表示される
5. **この画面を閉じると二度と表示されないので、必ずコピーして保存する**

![](https://static.zenn.studio/user-upload/d7285faaaf46-20260409.png)

---

## 2. Geminiさん（Google）のAPIキー取得

### APIキーの発行

1. <https://aistudio.google.com/apikey> にアクセス（Googleアカウントでログイン）
2. 「APIキーを作成」ボタンをクリック  
   ![](https://static.zenn.studio/user-upload/a4f69bc24c9a-20260409.png)
3. 「新しいキーを作成する」を選択
4. キー名は「Gemini API Key」のままでOK
5. プロジェクトは「Default Gemini Project」を選択して作成
6. 「APIキーの詳細」ポップアップに `AIza...` で始まる文字列が表示される  
   ![](https://static.zenn.studio/user-upload/2d76728be68c-20260409.png)
7. 「キーをコピー」ボタンでコピーして保存する

> ✅ Geminiさんは無料枠が非常に太く、個人の壁打ち用途なら無料枠内で十分使えます（2026年4月現在）。クレジットカード登録も不要です。  
> ※商用利用やプライバシー設定については公式ドキュメントをご確認ください

---

## 3. ChatGPTさん（OpenAI）のAPIキー取得

### アカウント作成・クレジット購入

1. <https://platform.openai.com> にアクセス
2. 「Sign up」からアカウントを作成
3. ログイン後、画面中央の黄色い「Add credits」ボタンからクレジットを購入する  
   ※ もし見当たらない場合は左メニューのSettingsを確認してください。  
   ![](https://static.zenn.studio/user-upload/70e7b94cc06f-20260409.png)

> ⚠️ OpenAIのAPIもクレジットカード登録と事前チャージが必要です。

### APIキーの発行

1. ログイン後、画面中央あたりの「Create API key」をクリック
2. 以下の設定で作成する
   * **Owned by**: You
   * **Name**: 任意（例：`kabehub`）
   * **Project**: Default project
   * **Permissions**: All
3. 「Create secret key」ボタンをクリック
4. 「Save your key」のポップアップに `sk-...` で始まる文字列が表示される
5. **この画面を閉じると二度と表示されないので、必ずコピーして保存する**

![](https://static.zenn.studio/user-upload/b4b6b3ff6222-20260409.png)

---

## KabeHubへの設定方法

1. <https://kabehub.com> にアクセスしてGoogleログイン
2. 右上メニューから「設定」を開く
3. 「APIキー」セクションに取得したキーをそれぞれ入力
4. 「APIキーを保存」ボタンをクリック

![](https://static.zenn.studio/user-upload/4368a2524374-20260409.png)

3つ全部登録しなくてもOKです。使いたいAIのキーだけ入れてください。

---

## まとめ

| AI | 取得先 | 費用 | キーの形式 |
| --- | --- | --- | --- |
| Claudeさん | console.anthropic.com | 最低$5〜（約750円〜） | `sk-ant-...` |
| Geminiさん | aistudio.google.com/apikey | 無料 | `AIza...` |
| ChatGPTさん | platform.openai.com | クレジット購入が必要 | `sk-...` |

**まず無料で試したい方はGeminiさんだけ登録するのがおすすめです。**

APIキーを設定したら、ぜひKabeHubで壁打ちを始めてみてくださいね！  
使い方はこちらから  
<https://zenn.dev/ruimatsumoto/articles/25049f44d91b2c>

🔗 <https://kabehub.com>
