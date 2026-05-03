---
id: "2026-05-02-mastra-announce-channels-登場-slack-discord-telegram-01"
title: "[Mastra Announce] Channels 登場 ― Slack / Discord / Telegram と接続"
url: "https://zenn.dev/shiromizuj/articles/b09eee651a06e9"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "LLM", "Gemini", "zenn"]
date_published: "2026-05-02"
date_collected: "2026-05-03"
summary_by: "auto-rss"
query: ""
---

[Mastra](https://mastra.ai/) の[公式Blog](https://mastra.ai/blog)で発表された[Announcements](https://mastra.ai/blog/category/announcements)を速報ベースでお伝えします。ただの直訳ではなく、関連ドキュメントも参照したうえで手厚くしたり省略したりします。普段このシリーズでは「速報性重視でAIの力を多分に使っているので、私自身の考察は少なめです」と書いているのですが、**今回も私の勝手解釈が多めです**。

[Mastra Announcements 速報解説一覧](https://zenn.dev/shiromizuj/articles/cc91bb06db5b5b)

---

## Mastra が「Channels」を発表

2026年4月28日、Mastra は **Channels for Mastra Agents** を発表しました。

アナウンスの冒頭を直訳すると以下のようになります。

> あなたのエージェントは、Slack、Discord、Telegram などでのメンションやメッセージに応答できるようになりました。チャンネルアダプターを取り付けることで、カスタム統合を構築しなくても、1つのエージェントを複数のプラットフォームに接続できます。
>
> Channels は、エージェントの動作方法を変更しません。Studio からこれまで通り対話し、テストし、反復改善し、観測できます。

要するに、Mastra エージェントを **Slack bot や Discord bot として動かすための公式の接続口**が入った、という発表です。

---

## 背景：AIエージェントは「どこで使われるか」が重要になる

AIエージェントを作るとき、最初はだいたいローカルの Playground としての Studio、あるいは API 経由で動作確認します。そして業務適用するにあたっては Mastra API を呼び出す UI を備えた専用アプリを開発することもあるでしょう。

一方で、多くのチームでは、仕事のやり取りは Slack、Discord、Teams、Telegram のようなチャットアプリ上で行われます。サポート依頼、障害報告、社内ナレッジの質問、レビュー依頼、デプロイ確認。こうした会話の流れの中でエージェントを呼び出せると、「AIツールを別画面で開く」のではなく、**普段の会話にAIエージェントが参加する**形になります。

ここで問題になるのが、各チャットプラットフォームごとの実装差です。Slack には Slack のイベント API や権限設定があり、Discord には Discord の bot / interaction の仕組みがあり、Telegram には Telegram Bot API があります。エージェント本体とは別に、プラットフォームごとの受信・返信・認証・重複排除・スレッド管理を毎回書くのはかなり面倒です。

Channels は、この部分を Mastra の `Agent` の設定として扱えるようにする機能です。

---

## Channels とは何か

Mastra の Channels は、エージェントを Slack、Discord、Telegram などのメッセージングプラットフォームへ接続するための仕組みです。ユーザーがプラットフォーム上でメッセージを送ると、Mastra はそれをエージェントの通常の処理パイプラインに流し、返答を同じ会話へストリーミングで返します。

重要なのは、Channels が「別種のエージェント」を作る機能ではない点です。エージェント本体はこれまでと同じです。

```
Slack / Discord / Telegram
        ↓
Channel Adapter
        ↓
Mastra Agent
        ↓
通常の model / tools / memory / workflow
        ↓
Channel Adapter
        ↓
元の会話へ返信
```

つまり Channels は、エージェントの「頭脳」を変えるのではなく、**入口と出口を増やす**機能です。Studio でテストできる同じエージェントを、Slack や Discord からも呼び出せるようになります。

---

## 使い方：Agent に `channels` を足す

最小構成はかなり素直です。`@mastra/core@1.22.0` 以降で、使いたいプラットフォームのアダプターを入れます。

```
npm install @chat-adapter/slack @chat-adapter/discord
```

そして `Agent` の `channels.adapters` に登録します。

```
import { Agent } from "@mastra/core/agent";
import { createSlackAdapter } from "@chat-adapter/slack";
import { createDiscordAdapter } from "@chat-adapter/discord";

export const channelAgent = new Agent({
  id: "channel-agent",
  name: "Channel Agent",
  model: "anthropic/claude-opus-4-6",
  instructions:
    "You are a helpful assistant. Answer questions, help with tasks, and have natural conversations.",
  channels: {
    adapters: {
      slack: createSlackAdapter(),
      discord: createDiscordAdapter(),
    },
  },
});
```

この例では、1つの `channelAgent` を Slack と Discord の両方に接続しています。アダプターは認証情報を環境変数から読み取ります。Slack 側、Discord 側で必要な Bot Token や Signing Secret などの具体的な設定は、Chat SDK の各アダプタードキュメントに従う形です。

Mastra は各アダプター向けに Webhook ルートを生成します。

```
/api/agents/{agentId}/channels/{platform}/webhook
```

たとえば今回の例なら、Slack 用の URL は次のようになります。

```
<your-server-url>/api/agents/channel-agent/channels/slack/webhook
```

この URL を Slack アプリ側の Event Subscriptions や Interactivity の Request URL として設定すると、Slack 上のイベントが Mastra に届くようになります。

---

## ローカル開発では public URL が必要

Slack や Discord のような外部サービスは、あなたのローカルマシンの `localhost:4111` に直接アクセスできません。そのため、ローカルで Channels を試す場合は、ngrok や cloudflared のようなトンネルツールで一時的な public URL を作ります。

または、

```
npx cloudflared tunnel --url http://localhost:4111
```

生成された URL をベースに、次のような Webhook URL を Slack / Discord 側へ登録します。

```
https://abc123.ngrok.io/api/agents/channel-agent/channels/slack/webhook
```

これは Webhook 型の連携では避けて通れないポイントです。ローカルの Mastra Server が外部プラットフォームから見える URL を持っていないと、イベントが届きません。

---

## なぜ「Storage」が重要なのか

Channels のドキュメントで地味に重要なのが、Mastra インスタンスに storage を設定する必要がある点です。

```
import { Mastra } from "@mastra/core";
import { LibSQLStore } from "@mastra/libsql";
import { channelAgent } from "./agents/channel-agent";

export const mastra = new Mastra({
  agents: { channelAgent },
  storage: new LibSQLStore({
    url: process.env.DATABASE_URL,
  }),
});
```

チャット連携では、「このメッセージは処理済みか」「このスレッドを購読中か」「どの会話履歴をどこまで持っているか」といった状態管理が必要になります。HTTP リクエストを受けて返すだけなら一見ステートレスに見えますが、実際には会話アプリとの連携はかなり状態を持ちます。

Mastra Channels では、この購読状態や重複排除などの状態を `StateAdapter` で扱い、デフォルトでは Mastra の storage に保存します。つまり Channels は「Webhook を受け取るだけの薄いラッパー」ではなく、**チャット上の会話をエージェントのスレッドとして扱うための状態管理レイヤー**まで含んでいます。

---

## スレッド文脈：途中から呼ばれても会話を読める

チャットアプリでエージェントを使うときに難しいのが、スレッド途中でのメンションです。

たとえば Slack のスレッドで、人間同士が10件ほど会話したあとに、

```
@agent ここまでの議論をまとめて、次のアクションを出して
```

と呼び出したとします。このとき、エージェントが最後のメンション1件だけを見ると、「ここまで」が何を指すのか分かりません。

Mastra Channels はこの問題に対応するため、非DMのスレッドで初回メンションされたときに、デフォルトでプラットフォームから直近10件のメッセージを取得します。そのメッセージをユーザーの入力に前置して、会話文脈としてエージェントへ渡します。返答後はそのスレッドを購読し、以後は Mastra の memory によって履歴を扱います。

この挙動は `threadContext` で制御できます。

```
const agent = new Agent({
  // ...
  channels: {
    adapters: {
      slack: createSlackAdapter(),
    },
    threadContext: {
      maxMessages: 0, // 初回メンション時の過去メッセージ取得を無効化
    },
  },
});
```

チャット上のエージェントは「会話の途中から呼ばれる」ことが多いので、この設計はかなり実用寄りです。

---

Channels の面白い点は、Mastra の tool approval ともつながっていることです。

Mastra の tool に `requireApproval: true` を設定しておくと、エージェントがそのツールを呼ぼうとしたときに、Slack / Discord 上で承認カードを表示できます。ユーザーは Approve / Deny ボタンで実行可否を判断し、承認されてからツールが実行されます。

これはかなり重要です。チャットアプリ上で動くエージェントは、ユーザーとの距離が近いぶん、危険な操作も自然に頼まれやすくなります。

* ファイルを削除する
* 外部サービスへ投稿する
* チケットを作成・更新する
* デプロイやジョブを実行する
* 顧客へメッセージを送る

こうした操作をすべて自動実行にすると危険ですが、毎回別画面に遷移して承認するのも面倒です。チャット内に承認 UI が出るなら、「会話の流れを切らずに人間が最後の判断をする」形にできます。

---

## マルチユーザー認識：誰が話したかを区別する

Slack や Discord のグループ会話では、複数人が同じスレッドで発言します。LLM に単純なテキストだけを渡すと、誰の発言なのか分からなくなることがあります。

Mastra Channels では、グループ会話の各メッセージに送信者名とプラットフォームIDを自動で付与します。

```
[Alice (@U123ABC)]: Can you help me with this?
[Bob (@U456DEF)]: I have a question too.
```

これにより、エージェントは「Alice の質問」と「Bob の質問」を区別できます。地味ですが、チーム利用ではかなり効く機能です。会話の要約、担当者ごとのタスク抽出、意思決定ログの整理などで精度に直結します。

---

## マルチモーダル：画像・動画・音声も会話に入る

Channels はテキストだけでなく、添付ファイルやリンクの扱いも考慮されています。

デフォルトでは画像が inline media としてモデルに渡されます。さらに設定すれば、動画、音声、PDF なども扱えます。たとえば Gemini のように画像・動画・音声をネイティブに処理できるモデルなら、Discord に貼られたスクリーンショットを説明したり、動画クリップを要約したり、YouTube リンクを動画として扱ったりできます。

```
export const visionAgent = new Agent({
  name: "Vision Agent",
  instructions: "You can see images, watch videos, and listen to audio.",
  model: google("gemini-3.1-flash-image-preview"),
  channels: {
    adapters: {
      discord: createDiscordAdapter(),
    },
    inlineMedia: ["image/*", "video/*", "audio/*"],
    inlineLinks: [
      { match: "youtube.com", mimeType: "video/*" },
      { match: "youtu.be", mimeType: "video/*" },
      "imgur.com",
    ],
  },
});
```

ここでのポイントは、チャットアプリがもともとマルチモーダルな場所だということです。人間はスクリーンショット、ログ画像、短い動画、PDF、リンクを気軽に貼ります。エージェントがそこに参加するなら、テキストだけでなく、添付物やリンクも扱える必要があります。

---

## 「Channels」は OpenClaw 的エージェントの最後の入口

ここからは私の解釈です。

Mastra はここ数か月で、エージェントに必要なプリミティブをかなり速いペースで積み上げています。

* **Memory**: 会話や観測をまたいで状態を保持する
* **Workspace**: ファイルシステムやサンドボックスを扱う
* **LSP**: ソースコードを意味ベースで理解する
* **Browser**: Webサイトを実際に操作する
* **Skills**: 手順や知識を再利用可能にする
* **Channels**: Slack / Discord / Telegram などから呼び出せるようにする

先日の [Browser 対応の記事](https://zenn.dev/shiromizuj/articles/45319f8282b6e4)でも触れましたが、 2026年4月24日 に開催・配信された Mastra の公式ワークショップ "[Build an OpenClaw-Style Agent with Mastra](https://www.youtube.com/live/4wGZlzzzEBE)" で、Mastra の共同創業者兼CPOである Shane は、OpenClaw が世界を席巻した理由について語っています。

> OpenClaw の個々の機能――メモリ、**ブラウザ操作**、ファイルシステムアクセス、スキル、**チャンネル**（**Slack/Telegram等への接続**）――はそれぞれ単体では目新しいものではない。しかしそれらが**パッケージとして組み合わさった**とき、「自分のマシンで動く、自律的なパーソナルアシスタント」という体験が生まれ、人々の想像力を爆発的に刺激した。

OpenClaw 的なエージェント、つまり単に「賢いチャットボット」ではなく、ブラウザを見て、ファイルを書き、ツールを実行し、記憶を持ち、必要なら人間とやり取りする、**作業環境に常駐するエージェント**。Mastra チームは、AIエージェントがその方向に進化していくと考えていて、エンタープライズで利用するに足る安全性とのバランスを取りながら強力に機能追加しているように思います。

今回発表の Channels は、その「人間とのやり取り」の入口を担当します。

今までの Mastra エージェントは、Studio や API から呼び出される存在でした。Channels によって、エージェントはチームの Slack チャンネルや Discord サーバーに常駐できます。これは体験としてかなり大きな差です。AIエージェントが「アプリの裏側にある機能」から、「会話に参加するチームメンバー」に近づくからです。

---

## 技術だけでは超えられない壁：組織のガバナンス

ただし、ここで率直に触れておきたいことがあります。

Mastra が Channels として Slack / Discord / Telegram への接続を簡単にしてくれたとしても、**実際に企業の Slack や Teams にボットを接続できるかどうかは、IT部門の許可次第**です。多くの組織では、外部サービスとの連携やカスタムアプリのインストールはデフォルトで制限されています。Slack であればアプリのインストールに管理者承認が必要であり、Teams であればサイドローディングやカスタムアプリの配布がポリシーで禁止されていることも珍しくありません。

これは Mastra のようなフレームワーク側の努力だけではどうにもならない部分です。いくら技術的に「数行のコードでエージェントを Slack に接続できる」としても、組織がその接続を許可しなければ、開発者の手元で閉じた実験にとどまります。

DX を本気で推進するのであれば、IT部門が「すべてを禁止する」のではなく、**最低限のセキュリティポリシーを守りながら障壁を緩めていく**姿勢が重要だと思います。たとえば、

* 特定のチャンネルやチームに限定したボットの試験導入を許可する
* 開発チーム向けにサンドボックス的なワークスペースを用意する
* 承認プロセスを設けつつも、リードタイムを短くする

といった形で、「全面禁止」と「野放し」の間にグラデーションを作ることが、組織としてAIエージェントの恩恵を受けるための前提条件になるはずです。

Mastra 側も、tool approval や可観測性、ガードレールといった安全機構を積み上げているのは、まさにこの「IT部門が許可を出しやすくする」ための材料を揃えている面があると思います。「このエージェントは何ができて何ができないか」「危険な操作には人間の承認が入る」「すべての実行が記録される」――こうした根拠があれば、IT部門も「条件付きで許可する」判断がしやすくなります。

---

## ただし、チャットに出すと責任も増える

Channels は便利ですが、チャットアプリにエージェントを出すと、利用者の期待値も上がります。

Studio や開発用 UI なら、多少失敗しても「検証中」で済みます。しかし Slack の本番チャンネルにいる bot が誤った情報を断定したり、危険なツールを勝手に実行したり、全員に見える場所でノイズを撒いたりすると、影響範囲が一気に広がります。

そのため、実運用では次の設計が重要になります。

* どのチャンネルでエージェントを有効化するか
* DM とグループメンションで挙動を変えるか
* 危険なツールには approval を必須にするか
* どの添付ファイルをモデルへ渡すか
* 会話履歴をどこまで取得するか
* 返信失敗や重複投稿をどう扱うか
* コストとレート制限をどう監視するか

Channels は「接続」を簡単にしますが、「運用設計」を不要にするものではありません。むしろ、AIエージェントがユーザーの日常導線に入るからこそ、権限・可観測性・承認フローがより重要になります。

---

## まとめ：エージェントの利用場所が Studio から会話の場へ広がる

今回の Channels 発表は、単に「Slack 連携ができるようになった」という話に見えます。しかし Mastra の文脈では、もう少し大きな意味があります。

エージェント本体は `Agent` として定義し、そこに memory、tools、browser、workspace、skills、channels を足していく。Mastra はこの方向で、AIエージェントを「単発のチャット応答」から「実際の作業環境に接続された実行主体」へ近づけています。

Channels は、その中でもユーザー接点を担うプリミティブです。Slack や Discord にいる人間が、いつもの会話の中でエージェントを呼び出し、必要なら承認し、結果を同じスレッドで受け取る。これはプロダクト体験としてかなり自然です。

技術的に見ると、ポイントは次の3つです。

1. **入口と出口の標準化**：Slack / Discord / Telegram などを `channels.adapters` として Agent に接続できる
2. **チャット特有の状態管理**：スレッド文脈、購読状態、重複排除、マルチユーザー認識を扱う
3. **安全な実行への接続**：tool approval をチャットUI上の承認カードとして表現できる

Mastra エージェントは、Studio の中で動くものから、チームの会話空間に参加するものへ広がり始めました。地味に見えて、かなり重要な一歩だと思います。

---

## 参考リンク
