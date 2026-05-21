---
id: "2026-05-20-mastra-announce-agent-to-agent-をサポート-別フレームワークのエージェ-01"
title: "[Mastra Announce] Agent-to-Agent をサポート - 別フレームワークのエージェント同士が会話する"
url: "https://zenn.dev/shiromizuj/articles/d8123a18c899a4"
source: "zenn"
category: "claude-code"
tags: ["MCP", "API", "AI-agent", "OpenAI", "GPT", "Python"]
date_published: "2026-05-20"
date_collected: "2026-05-21"
summary_by: "auto-rss"
query: ""
---

[Mastra](https://mastra.ai/) の [公式Blog](https://mastra.ai/blog) で発表された [Announcements](https://mastra.ai/blog/category/announcements) を速報ベースで解説します。ただの直訳ではなく、関連情報も補いながら、なるべく「何がうれしいのか」「前は何が足りなかったのか」まで分かるように整理します。速報性重視のため一部は公開情報ベースの解釈を含みますが、事実と推測は分けて書きます。

[Mastra Announcements 速報解説一覧](https://zenn.dev/shiromizuj/articles/cc91bb06db5b5b)

---

## Mastra が A2A 対応を正式に入れた

2026年5月19日、Mastra は **Agent-to-Agent（A2A）サポート** を発表しました。

今回の発表をひとことで言うと、**Mastra のエージェントが、Mastra の外にいる別実装のエージェントと、共通プロトコルで会話できるようになった**という話です。

発表本文で強調されている利用パターンは次の2つです。

* A2A 対応の外部エージェントを、Mastra のサブエージェントとして使う
* Mastra の Client SDK から、A2A 対応エージェントへ直接リクエストを送る

必要バージョンは次の通りです。

* `@mastra/core@1.33.1` 以降
* `@mastra/client-js@1.18.1` 以降

この発表の重要点は、単に「HTTP で他サービスを叩ける」という話ではないことです。**相手がエージェントであることを前提に、能力の発見、長時間タスクの追跡、ストリーミング、再接続、プッシュ通知まで含めて標準化された**ことに価値があります。

---

## 背景: なぜ今 A2A なのか

最近の Mastra は、単体のエージェントを作るところから一歩進んで、複数エージェントが連携する世界をかなり強く意識しています。

その流れは、以前に紹介したロードマップでも予告されていました。

<https://zenn.dev/shiromizuj/articles/f8ed4ed72c414b>

このロードマップ記事では、5月以降の注目ポイントとして次が挙げられていました。

* Background Agents
* Durable Agents
* Dynamic Sub-Agents
* Temporal Workflows
* A2A サポートの強化

特に A2A については、**「複数チームが別々のエージェントを作っており、そのうち連携が必要になる」** という実務上の要請に対する答えとして説明されていました。

これはかなり自然な流れです。現実の組織では、全部のエージェントを一つのフレームワーク、一つの言語、一つのチームで統一できるとは限りません。

* 社内の業務エージェントは Python 製
* 顧客向けチャットは TypeScript 製
* ある部門は Google ADK を採用
* 別の部門は LangGraph や独自実装を使っている

こうなると、本当に必要なのは「全部 Mastra に書き換えること」ではなく、**別々に作られたエージェントが、安全に仕事を委譲し合える共通ルール**です。A2A はそこを狙っています。

---

## A2A とは何か

### A2A は「エージェント同士の仕事の受け渡し」プロトコル

[A2A](https://a2a-protocol.org/latest/) は Agent-to-Agent の略で、Google 主導で公開され、現在は [Linux Foundation](https://www.linuxfoundation.org/) 配下で進められているオープンプロトコルです。

目的は明快です。**異なる会社・異なるフレームワーク・異なるサーバー上で動いているエージェント同士が、エージェントとして協調動作できるようにする**ことです。

ここで重要なのは、「ただの API 呼び出し」とは発想が少し違うことです。A2A では相手を単なるツールではなく、**自分なりのプロンプト、メモリ、ワークフロー、内部ツールを持つ独立したエージェント**として扱います。

つまり呼び出し元は、相手の内部実装を知らなくてもよいし、相手も内部事情を公開しなくてよい。公開するのは、「どんな仕事ができるか」「どこに依頼を送ればよいか」「どんな認証が必要か」といった最小限の契約だけです。

---

## エージェント同士の会話はどんなルールで行われるのか

ここが A2A の核心です。A2A の会話には、少なくとも次のルールがあります。

### 1. まず Agent Card で相手を発見する

A2A では、各エージェントが **Agent Card** という JSON の自己紹介カードを公開します。これは `.well-known` 配下に置かれるのが基本です。

Agent Card には例えば次の情報が入ります。

* エージェント名
* 説明
* 実行用エンドポイント URL
* 提供元
* ストリーミングやプッシュ通知への対応可否
* 認証方式
* スキル一覧

Mastra のドキュメントでも、A2A はまずこの Agent Card を読んで相手の能力を把握する仕組みだと説明されています。ここでいう `.well-known` は、基本的には**公開する側のサーバーが Agent Card を配信するための既定パス**です。利用する側は、その URL を HTTP で読みに行って内容を確認することで相手の Agent について理解します。公開側の Agent Card を呼び出し側のローカルやサーバー上の `.well-known` 配下に保存しておくわけではありません。

```
{
  "name": "Weather Agent",
  "description": "Provides weather information.",
  "url": "https://agent.example.com/api/a2a/weather-agent",
  "provider": {
    "organization": "Acme",
    "url": "https://acme.example.com"
  },
  "capabilities": {
    "streaming": true,
    "pushNotifications": true,
    "stateTransitionHistory": false
  },
  "skills": [
    {
      "id": "weather",
      "name": "weather",
      "description": "Gets weather conditions for a location.",
      "tags": ["tool"]
    }
  ]
}
```

この時点で、呼び出し元エージェントは「この相手は天気質問を受けられる」「SSE が使える」「認証が必要」といったことを判断できます。

### 2. 通信は HTTP 上の JSON-RPC 2.0 で行う

A2A は既存標準の上に作られています。主要な土台は次の通りです。

* HTTP(S)
* JSON-RPC 2.0
* SSE（Server-Sent Events）

この設計の利点は、企業システムに組み込みやすいことです。完全に新しい専用トランスポートではなく、既存の Web スタックの延長で扱えます。

### 3. やり取りの基本単位は Message と Task

A2A のやり取りでは、単なる 1 回きりの応答だけでなく、**状態を持つ仕事** を扱えます。主要な概念は次の通りです。

* **Message**: 1ターン分の通信。質問、指示、返答、補足文脈などを運ぶ
* **Task**: 状態を持つ作業単位。ID とライフサイクルを持ち、長時間実行を追跡できる
* **Artifact**: タスクの成果物。文書、画像、構造化データなど
* **Part**: Message や Artifact の中身を構成する最小単位。テキスト、URL、バイナリ、JSON データを扱える

ここで重要なのは、`Task` が必ずしもワンショットの 1 リクエスト 1 レスポンスだけを意味しないことです。1つの仕事に対して「依頼する」「追加情報を渡す」「途中結果を受け取る」「入力待ちに応答する」といった複数ターンの往復が、同じ `taskId` の下で続くことがあります。さらに A2A には `contextId` という概念もあり、複数の Task をまたぐ会話文脈やセッションのまとまりを論理的に束ねる用途に使えます。

### 4. 長時間タスクを前提にしている

A2A の設計原則の一つに、長時間タスク対応があります。深いリサーチ、複数ステップの承認、人的確認を挟む処理などは、1回の HTTP 応答で終わりません。

そこで A2A では次の手段が標準で考慮されています。

* 同期応答
* SSE によるストリーミング更新
* タスク ID を使った再購読
* Webhook へのプッシュ通知
* キャンセル
* follow-up input による追加入力

Mastra の A2A ドキュメントでも、`resumeGenerate()`、`resumeStream()`、`resubscribeTask()`、push notification の扱いが明示されています。ここは「ただの外部 API 呼び出し」より一段エージェント向けです。

### 5. モダリティ非依存である

A2A はテキストだけを想定していません。Part にはテキスト、ファイル参照、バイナリ、JSON データを載せられるため、フォーム入力、画像、構造化レスポンスを含むやり取りに拡張できます。

Google の発表でも、A2A の設計原則として **modality agnostic** が挙げられていました。

### 6. 認証と信頼をプロトコルの外に逃がさない

A2A は認証そのものを独自方式で抱え込むのではなく、標準的な Web の認証を前提にしています。Agent Card に認証要件を載せ、実際の資格情報は HTTP ヘッダー等で渡します。

Mastra ではさらに、次のような安全策も用意されています。

* Agent Card 署名
* クライアント側での署名検証
* サブエージェントとして呼ぶ前の `verifyAgentCard`

つまり A2A は「つながれば何でもよい」ではなく、**信頼できる相手にだけ委譲する**ための仕組みも意識しています。

---

## A2A は MCP と何が違うのか

ここは混同しやすいので短く整理します。

* **MCP**: エージェントにツールやコンテキストを渡すための標準
* **A2A**: エージェント同士が互いに仕事を依頼し、結果を受け渡すための標準

Google の発表でも、A2A は Anthropic の MCP を補完するものだと説明されています。

感覚的にはこうです。

* MCP は「エージェントが外界の機能を使う」ための接続口
* A2A は「エージェントが別のエージェントに任せる」ための接続口

Mastra は MCP も A2A も取り込む方向に進んでおり、最近のロードマップ全体を見ると、「単独エージェント」から「エージェントのネットワーク」へ視野を広げているのが分かります。

---

## Mastra 以外にどんな AI エージェントが A2A をサポートしているのか

ここは少し丁寧に言い分ける必要があります。

まず、A2A は特定ベンダー専用ではありません。Google の立ち上げ発表時点で、50社超の技術パートナーやサービスパートナーが協力していました。発表文で名前が挙がっている企業には、たとえば次が含まれます。

* Atlassian
* Box
* Cohere
* Intuit
* LangChain
* MongoDB
* PayPal
* Salesforce
* SAP
* ServiceNow
* UiPath
* Weights & Biases

ただし、ここでの「サポート」は幅があります。**仕様策定への参加** と **すでに A2A エンドポイントを実装していること** は同じではありません。

現時点で比較的はっきり言いやすいのは次の層です。

### 1. A2A を直接扱う SDK 群

A2A プロジェクト本体は、少なくとも次の SDK を公開しています。

* Python SDK
* Go SDK
* JavaScript SDK
* Java SDK
* .NET SDK

これは「どの言語でも A2A サーバーやクライアントを作りやすくする」ための基盤です。

### 2. A2A で公開・接続する例が明示されているフレームワーク群

A2A プロジェクトの README や学習コースでは、A2A 対応の例として次の名前が明示されています。

* Google ADK
* LangGraph
* BeeAI

さらに今回の Mastra 発表では、Mastra の Client SDK から **Mastra エージェント、Google ADK サービス、LangChain エージェント、または A2A を話せる任意の実装** に接続できると説明されています。

A2A は、**A2A を話せるようにした実装同士をつなぐための共通言語**として見るのが正確です。

### 3. エンタープライズ製品側の採用機運

Google のローンチ発表では、SAP Joule、Salesforce Agentforce、ServiceNow、UiPath などの名前も並んでいました。こちらはフレームワークというより、**企業向けのエージェントプラットフォームや製品群が A2A を相互運用の標準候補として見ている**と理解するのがよいです。

---

## Mastra では A2A をどう使うのか

Mastra での使い方は、大きく3つに整理すると分かりやすいです。

### 1. 自分の Mastra エージェントを A2A 対応エージェントとして公開する

Mastra は A2A をサポートしており、Mastra Server 上に登録したエージェントは A2A エンドポイントとして公開できます。

Mastra ドキュメントでは、デフォルトの `apiPrefix` が `/api` の場合、`weather-agent` というエージェントは次の URL を持つと説明されています。

* Agent Card: `/api/.well-known/weather-agent/agent-card.json`
* 実行エンドポイント: `/api/a2a/weather-agent`

つまり、**Mastra で作ったエージェントをそのまま「他のエージェントから呼ばれる側」にできる**ということです。

この時点で公開されるのは Agent Card と A2A エンドポイントであり、内部プロンプト、メモリ、ツール実装までは露出しません。ここが A2A の「opaque agent」思想と一致しています。

### 2. 外部の A2A エージェントを Mastra のサブエージェントとして使う

発表で最も分かりやすく紹介されているのがこのパターンです。`A2AAgent` でリモートエージェントを包み、それを親エージェントの `agents` に渡します。

```
import { Agent } from "@mastra/core/agent";
import { A2AAgent } from "@mastra/core/a2a";

const remoteWeatherAgent = new A2AAgent({
  url: "https://weather.example.com/api/.well-known/weather-agent/agent-card.json",
  headers: {
    Authorization: `Bearer ${process.env.WEATHER_AGENT_TOKEN}`,
  },
});

export const supportAgent = new Agent({
  id: "support-agent",
  name: "Support Agent",
  instructions: "ユーザーの質問に答え、天気に関する質問は必要に応じて委譲してください。",
  model: "openai/gpt-5.4",
  agents: {
    remoteWeatherAgent,
  },
});
```

このとき `A2AAgent` は次のことを内部で処理します。

* Agent Card の取得とキャッシュ
* 相手の実行 URL と capability の把握
* ストリーミング可否に応じた `message/send` または `message/stream` の使い分け
* リモートの task / message / artifact / status update を Mastra のサブエージェント結果へ変換

つまり開発者は、相手が Mastra 製でなくても、かなり自然に「外部の専門エージェントを部品として組み込む」ことができます。

### 3. アプリケーションコードから A2A エージェントへ直接呼び出す

エージェントからエージェントへではなく、通常のアプリケーションコードから A2A エージェントを呼びたい場合は `MastraClient.getA2A()` を使います。

```
import { MastraClient } from "@mastra/client-js";

const client = new MastraClient({
  baseUrl: "https://agent.example.com",
  headers: {
    Authorization: `Bearer ${process.env.AGENT_API_TOKEN}`,
  },
});

const a2a = client.getA2A("weather-agent");

const stream = a2a.sendMessageStream({
  message: {
    kind: "message",
    role: "user",
    messageId: crypto.randomUUID(),
    parts: [{ kind: "text", text: "プラハの天気はどうですか？" }],
  },
});

for await (const event of stream) {
  console.log(event);
}
```

これはフロントエンドやバックエンドのアプリケーションコードから、A2A 対応エージェントに直接アクセスしたいときに向いています。

さらに Mastra では次も用意されています。

* `getAgentCard()` で Agent Card を取得
* `resubscribeTask()` で長時間タスクに再接続
* `setTaskPushNotificationConfig()` で Webhook 通知を設定

---

## Mastra の A2A 実装で重要な点

### サブエージェントの拡張ではあるが、単なる supervisor の焼き直しではない

Mastra には以前から supervisor / subagent パターンがありました。今回の A2A は、その考え方を**ネットワーク越しの別実装エージェント**まで広げたものだと理解すると分かりやすいです。

<https://zenn.dev/shiromizuj/articles/50513de990ca0b>

ただし単なる HTTP ツール呼び出しではなく、Agent Card による discovery、task lifecycle、resubscribe、push notification まで持ち込んでいるので、設計レベルでは一段本格的です。

### 長時間稼働エージェント路線と相性がよい

Mastra は最近、Background Tasks、Temporal Workflows、Durable / long-running 系にかなり力を入れています。A2A はそこにぴったり噛み合います。

理由は簡単で、外部の専門エージェントに委譲した仕事が数秒で終わるとは限らないからです。深い調査、社内承認、別システムでの処理待ちなどを考えると、**タスク ID を持ち、進捗を追え、切断後に再接続できる**ことは現実的な要件です。

### 信頼境界をまたぐ設計になっている

同じプロセス内の subagent と違い、A2A の相手は別チーム、別会社、別インフラで動いている可能性があります。Mastra が Agent Card 検証や署名確認の話まで用意しているのは、この違いをきちんと踏まえているからです。

---

## どういう場面で効くか

この発表が特に効くのは、次のようなケースです。

* TypeScript の Mastra エージェントから、Python の専門エージェントへ仕事を委譲したい
* 社内の複数チームが別々に作ったエージェント資産を、作り直さずにつなぎたい
* あるエージェントは UI 対話に強く、別のエージェントは業務処理や検索に強い、といった分業をしたい
* 長時間タスクを扱う外部エージェントと、進捗付きで連携したい
* ベンダーを固定せず、将来も差し替え可能な形で multi-agent 構成を組みたい

逆に、同じプロセス内ですべて完結する単純な分岐で十分なら、必ずしも A2A が必要とは限りません。A2A は、**信頼境界や実装境界をまたいでエージェントをつなぐ必要がある時**に真価を発揮します。

---

## まとめ

Mastra の A2A 対応は、「外部エージェントを呼べます」という以上の意味があります。Agent Card による能力発見、Task による長時間処理、SSE や push notification による更新、署名検証による信頼確保まで含め、**エージェント同士の協調を実運用寄りの形で扱える入口**ができました。

特に重要なのは次の3点です。

* A2A はツール呼び出しではなく、独立したエージェントへの委譲のための標準
* Mastra は「公開する側」「サブエージェントとして使う側」「Client SDK から呼ぶ側」の3方向で対応している
* ロードマップで予告されていた multi-agent / long-running 路線が、実際の機能としてつながり始めた

Mastra を使っている人にとっては、今後「全部 Mastra で書くか」よりも、**Mastra を軸にして周辺のエージェントとどうつなぐか** が設計論点になってきそうです。今回の発表は、その第一歩としてかなり重要です。

---

## 関連リンク
