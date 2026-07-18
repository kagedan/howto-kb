---
id: "2026-07-18-個人開発の集客を全自動化xtwitterのai広報エージェントを作ったらapiの隠し仕様5の壁に泣か-01"
title: "個人開発の集客を全自動化！「X(Twitter)のAI広報エージェント」を作ったら、APIの隠し仕様（$5の壁）に泣かされた話"
url: "https://zenn.dev/ponsuko/articles/2363dcebafda94"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "LLM", "Gemini", "zenn"]
date_published: "2026-07-18"
date_collected: "2026-07-19"
summary_by: "auto-rss"
query: ""
---

## はじめに

個人開発において「作ること」と同じくらい、あるいはそれ以上に難しいのが「集客」です。  
現在、タスクや目標をRPGゲームのように楽しめるSaaS「LifeQuest」を開発しているのですが、毎日SNSで発信を続けるリソースが足りない……。

そこで、「**アプリのコンセプトに合った魅力的なポストを、毎日AIに考えてもらい、勝手にX（旧Twitter）へ投稿するAIエージェント**」をBFF（Node.js）上に構築しました。  
本記事では、その具体的なシステム構成と実装例、そして現在X API v2を利用する開発者の多くが絶望している **`402 Payment Required (credits depleted)` の解決方法** について解説します。

## 構築したシステムの全体像

開発者が寝ていても、毎日19時に自動で発信し続けるバッチシステムです。

* **実行環境:** Node.js (Express / Renderで稼働)
* **定期実行:** `node-cron`
* **AI (テキスト生成):** Gemini API (LLM)
* **X連携:** `twitter-api-v2` (X API v2)

### 処理フロー

1. `node-cron` が毎日19時に発火。
2. BFF側で「今日のテーマ（運動、学習、仕事など）」をランダムに選定。
3. 選定したテーマをLLMに渡し、「RPG風のクエスト案」を生成させる。
4. 生成されたテキストを `twitter-api-v2` 経由でXに自動投稿する。

## 実装のポイントと実際のコード

### 1. LLMへのプロンプト設計

単なる「アプリの宣伝」では誰も見てくれません。LifeQuestの「日常をゲーム化する」というコア体験をタイムライン上でデモするため、以下のようなプロンプトを組んでいます。

`const prompt = \`  
`あなたはタスク管理アプリ『LifeQuest』の広報AIです。`  
`指定されたテーマ「\${theme}」で、日常をRPG風に楽しむ『今日のクエスト案（目標、達成条件、得られるステータス）』を考案してください。`  
`条件:`  
`- 130文字以内に収めること`  
`- ユーモアを交えること`  
`- 最後に必ずハッシュタグ #LifeQuest #個人開発 とアプリURL(\${APP_URL})を入れること`  
`;`

投稿処理自体は非常にシンプルです。

`const { TwitterApi } = require('twitter-api-v2');`

`const client = new TwitterApi({`  
`appKey: process.env.TWITTER_API_KEY,`  
`appSecret: process.env.TWITTER_API_SECRET,`  
`accessToken: process.env.TWITTER_ACCESS_TOKEN,`  
`accessSecret: process.env.TWITTER_ACCESS_SECRET,`  
`});`

`const postToX = async (text) => {`  
`try {`  
`const { data } = await client.v2.tweet({ text });`  
`console.log('投稿成功:', data.id);`  
`} catch (error) {`  
`console.error('Xへの投稿エラー:', error);`  
`}`  
`};`

## 🚨 最大の罠：Freeプランなのに「402 credits depleted」エラーが出る

実装を終え、いざテスト投稿！……と意気込んだところで、以下のエラーに遭遇しました。

`bash ApiResponseError: Request failed with code 402 detail: 'credits depleted', title: 'Payment Required'`

「えっ、Freeプラン（無料枠）で申請したはずなのに、なぜ支払い要求が？」  
ここが現在のX APIにおける最大の罠でした。

### 原因と解決策：「入場料」としての$5課金が必要

現在のX APIは、スパムボット対策として仕様が変更されており、**Freeプランであってもアカウントに最低限の課金実績（クレジット残高）がないとWrite（書き込み）APIが弾かれる**仕様になっています。

つまり、「投稿枠自体は無料だが、機能を開放するためのデポジットが必要」という状態です。

**【解決手順】**

1. X Developer Portalの「Billing（支払い）」メニューを開く。
2. 「Top-up」から最低金額である **$5（約750円）** をチャージする。
3. ダッシュボードのクレジット残高が「$5.00」になったことを確認して再度実行。

これだけで、先ほどの402エラーが嘘のように消え去り、無事に自動投稿が成功しました。

### ⚠️ もう一つの落とし穴：権限変更とトークン再発行

APIキーを発行する際、アプリの権限（App permissions）を初期状態の「Read（読み取り専用）」から「Read and Write（読み書き両方）」**に変更する必要があります。  
**この権限変更を行う前に発行したAccess Tokenは、古い権限（読み取り専用）のまま**です。権限を変更した後は、必ず「Access Token and Secret」を**Regenerate（再生成）し、環境変数を書き換えることを忘れないでください。（私はこれでも少しハマりました）

## おわりに：本番デプロイ時の注意点

ローカルで動いたコードをRenderなどのPaaSにデプロイする際、`package.json` に `twitter-api-v2` と `node-cron` を追加し忘れて `MODULE_NOT_FOUND` エラーを出すという個人開発あるあるも経験しました（笑）。

わずか$5の初期投資で、毎日文句も言わずに自作アプリの魅力を発信し続けてくれるAI広報担当を雇えたと思えば、非常に安い投資です。  
SNS集客に悩む個人開発者の方は、ぜひBFFとLLMを組み合わせたAIエージェントの構築を試してみてください！

こちらが開発し、運用中のアプリとなります。ぜひ遊んでみて下さいね  
<https://lifequest-71606.web.app/>
