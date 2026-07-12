---
id: "2026-07-12-mastra-announce-外部イベント連携を-webhook-依存から解放する-custom-01"
title: "[Mastra Announce] 外部イベント連携を webhook 依存から解放する Custom Signal Providers"
url: "https://zenn.dev/shiromizuj/articles/ec70c023a4fc47"
source: "zenn"
category: "claude-code"
tags: ["API", "AI-agent", "zenn"]
date_published: "2026-07-12"
date_collected: "2026-07-13"
summary_by: "auto-rss"
query: ""
---

[Mastra](https://mastra.ai/) の [公式 Blog](https://mastra.ai/blog) で公開された新機能をもとに、今回の発表が何を解決するのかを整理します。今回は単なる API 追加ではなく、**長時間動くエージェントに外部イベントをどう接続するか** という、Signals の実運用に直結するアップデートです。すでに Mastra には Agent Signals と WebhookSignalProvider がありましたが、Custom Signal Providers によって **Webhook 以外の外部イベント源も、Mastra の subscription と通知配送の仕組みに自然に乗せられる** ようになりました。

[Mastra Announcements 速報解説一覧](https://zenn.dev/shiromizuj/articles/cc91bb06db5b5b)

---

2026年7月9日、Mastra は **Introducing Custom Signal Providers for Mastra Agents** を公開しました。今回のポイントは、**任意の外部イベント源を監視し、そのイベントを購読済みの agent thread に notification signal として届けるための拡張ポイントが公開された**ことです。

ぱっと見ると「Webhook の次に custom provider も書けるようになった」という話に見えます。ですが本質はそこではありません。今回 Mastra が埋めたのは、**Signals は強いが、外部イベントの取り込み口が webhook 前提だと足りない** という現実的なギャップです。

---

## 今回の発表をひとことで言うと

Custom Signal Providers は、**外部イベントの監視・購読管理・thread への通知配送をひとつの provider にまとめるための基底クラス**です。

Signal providers docs では、provider の責務は次の 3 つに整理されています。

* subscription tracking
* ingestion
* delivery

今回公開された `SignalProvider` を使うと、開発者は次を自分のソースに合わせて実装できます。

* `.start()` / `.stop()` で接続の開始と終了を管理する
* `.poll()` または `.handleWebhook()` でイベントを取り込む
* `.watch()` / `.unwatch()` で thread と外部 resource の対応を管理する
* `notify()` で一致したイベントを notification signal として配送する

つまり今回の追加で嬉しいのは、単に「好きなイベント源を扱える」ことよりも、**外部イベントをどの thread が見ているかという bookkeeping を Mastra の signal provider 層に寄せられる**ことです。

---

## 背景: これまでは何が足りなかったのか

Mastra は 2026年6月以降、Signals 周辺をかなり強化してきました。

* Agent Signals で `sendMessage()` / `queueMessage()` / `sendNotificationSignal()` などの thread 操作が整理された
* Notification Inbox で通知の保存と優先度付き配送が入った
* WebhookSignalProvider で webhook payload と subscribed thread の matching が標準化された

ここまでで、GitHub や Slack の webhook を thread に届けるルートはかなり整っていました。ただし、外部イベントは webhook だけではありません。

たとえば実務では次のようなソースがあります。

* Postgres `LISTEN/NOTIFY`
* Redis やメッセージキューの pub/sub
* CI や監視サービスの polling API
* 独自アプリケーションの長寿命ソケット接続
* 自前の DB や内部ジョブキューの状態変化

こうしたソースでは、従来は次のどちらかになりがちでした。

1. アプリ側でイベント受信、購読管理、thread 解決、通知送信まで全部自前で配線する
2. webhook に無理やり寄せるための中継レイヤを別途作る

`sendNotificationSignal()` 自体はすでにありましたが、これは **「送る先の thread が分かっている」ことが前提**です。Signal providers docs でも、one-off のイベントなら `agent.sendNotificationSignal()` を直接使えばよい、と切り分けています。裏を返すと、**どの thread がどの外部 resource を監視しているか** を継続的に管理する仕組みは、custom provider なしではアプリ側の責務でした。

WebhookSignalProvider はこの問題を push 型 webhook に対して解決しましたが、今回の発表が重要なのは、**その解法を webhook 以外にも広げた**ことです。

---

## 何が新しくなったのか

### 1. `SignalProvider` を継承して独自 provider を書ける

今回の発表で、外部イベント連携の土台として `SignalProvider` を継承するパターンが前面に出ました。ブログでは Postgres `LISTEN/NOTIFY` を例に、provider が自前で接続を持ち、イベントを受けたら該当 thread へ `notify()` する構成を示しています。

最小イメージは次のようになります。

```
import { SignalProvider } from "@mastra/core/signals";
import type { SignalProviderTarget } from "@mastra/core/signals";

export class PgNotifySignalProvider extends SignalProvider<"pg-notify"> {
  readonly id = "pg-notify" as const;
  readonly externalResourceId = "postgres";

  async start() {
    // ここで外部接続を開く
  }

  stop() {
    // ここで外部接続を閉じる
  }

  async watch(target: SignalProviderTarget) {
    return this.subscribe(target, this.externalResourceId);
  }

  async unwatch(target: SignalProviderTarget) {
    return this.unsubscribe(target, this.externalResourceId);
  }
}
```

重要なのは、Mastra が「通知 API」だけでなく、**購読と配送の骨格**を提供するようになったことです。

### 2. 取り込み方式を webhook 以外にも広げられる

WebhookSignalProvider は `handleWebhook()` による push 型 integration の共通化でした。Custom Signal Providers ではそこから一歩進み、**polling でも長寿命接続でもよい**という構図になります。

ブログの Postgres 例では、`start()` で `LISTEN` を開始し、イベントを受けたら購読一覧を見て `notify()` します。つまり、外部イベントの入口が HTTP である必要はありません。

これは地味ですがかなり大きいです。実際の業務システムでは、イベントの真の発生源が webhook よりも DB、キュー、内部サービスに近いことがよくあるからです。

### 3. subscription の持ち方が Mastra 側に寄る

provider の基底クラスは、thread と external resource の対応を in-memory registry として持ちます。これにより、開発者は「監視対象」と「thread」の関係を provider に閉じ込められます。

たとえば「この thread はこの DB を見ている」「この thread はこの pipeline を見ている」といった関係を、アプリ全体に散らさずに provider 層へ集約できます。

この整理が入ることで、外部イベント連携の設計は次のように分割しやすくなります。

* agent: 受け取った notification をどう扱うか
* provider: どの外部イベントをどの thread に届けるか
* storage / signals: 通知をどう保存し、どう配送するか

---

## 実装イメージ: Postgres のイベントで待機中エージェントを起こす

ブログでは、Postgres 側で `pg_notify` を投げ、Mastra 側の provider がそれを受ける例が紹介されています。要点だけ抜き出すと次の流れです。

### 1. provider が外部イベントを購読する

```
async start() {
  this.pgClient = new Client({ connectionString: process.env.DATABASE_URL });
  await this.pgClient.connect();
  await this.pgClient.query(`LISTEN "mastra_events"`);

  this.pgClient.on("notification", async msg => {
    if (!msg.payload) return;
    const payload = JSON.parse(msg.payload);
    const subscriptions = this.getSubscriptionsForResource(this.externalResourceId);

    for (const subscription of subscriptions) {
      await this.notify(
        {
          source: this.id,
          kind: payload.event,
          priority: payload.priority,
          summary: `${payload.event}: ${payload.schema}.${payload.name}`,
          payload,
        },
        {
          resourceId: subscription.resourceId,
          threadId: subscription.threadId,
          ifIdle: { behavior: "wake" },
        },
      );
    }
  });
}
```

ここで効いているのは、イベント受信と thread 解決が同じ provider にまとまっていることです。

### 2. agent 側は signal provider を登録するだけでよい

```
import { Agent } from "@mastra/core/agent";
import { pgNotify } from "../signals/pg-notify";

export const dbSentinel = new Agent({
  id: "db-sentinel",
  name: "DB Sentinel",
  instructions: "あなたはデータベース変更を監視し、重要な変更があれば短く説明するエージェントです。",
  model: "anthropic/claude-opus-4-8",
  signals: [pgNotify],
});
```

agent 側は、どこからイベントが来るかを深く知らなくても済みます。

### 3. thread を provider に購読させる

```
pgNotify.watch({
  resourceId: "user_123",
  threadId: "db-sentinel-thread",
});
```

この形にすると、アプリ側の責務は「どの thread を何に watch させるか」を決めることに寄ります。以後のイベント受信と通知配送は provider が担います。

---

## 何がうれしいのか

### 1. webhook 前提で考えなくてよくなる

これまで webhook provider だけだと、外部イベント源を webhook として表現しづらいケースでは中継層が必要でした。今回の custom provider で、**イベント発生源の自然な取り込み方をそのまま使える**ようになります。

特に、DB イベントや polling ベースの監視はこの恩恵が大きいです。

### 2. `sendNotificationSignal()` の前段を共通化できる

one-off の通知なら `sendNotificationSignal()` で十分ですが、継続監視では「誰が何を監視しているか」を毎回解決しなければなりません。Custom Signal Providers は、その前段を繰り返し書かなくてよいようにします。

つまり今回の追加は `sendNotificationSignal()` の代替ではなく、**その前にある matching と subscription 管理を再利用可能にする**ものです。

Signal providers docs では、provider は通知取り込みだけでなく、追加の lifecycle / processors / tools も持てると整理されています。

* `start()` / `stop()` で接続管理
* `getInputProcessors()` / `getOutputProcessors()` で processor を返す
* `getTools()` で agent callable な tool を返す

ここから分かるのは、Mastra が provider を単なる adapter ではなく、**外部システムとの統合単位**として見ていることです。将来的に「監視するだけでなく、その外部システムを調べる tool も一緒に持つ」といった設計がしやすくなります。

### 4. 実装の置き場所が明確になる

外部イベント統合のコードは、放っておくと API route、cron、DB クライアント、agent 本体にばらけがちです。provider を単位に切り出せるようになると、**外部イベント連携の責務を 1 か所にまとめやすい**です。

これは地味ですが、運用が長くなるほど効きます。

---

## 注意点: 便利だが全部を自動で解決するわけではない

### 1. subscription registry はデフォルトで in-memory

Signal providers docs にある通り、base registry は **in-memory かつ per-process** です。つまり再起動をまたいで subscription を残したい場合や、複数 instance で共有したい場合は、独自に永続化して `start()` で rehydrate する必要があります。

これはかなり重要です。Custom provider は event ingestion を整理してくれますが、**durable subscription までは自動ではない**と理解しておくべきです。

### 2. notification delivery には対応 storage が必要

docs では、`notify()` による notification delivery には notification 対応の storage adapter が必要だと明記されています。libSQL、PostgreSQL、MongoDB など、通知保存を扱える storage を Mastra instance に設定する前提です。

つまり provider だけ書いても、通知基盤が無ければ本番運用は完成しません。

### 3. 機能は beta

Signal providers docs では beta 扱いです。API がまだ固まりきっていない可能性があるので、アプリ側には薄い wrapper を置いておいた方が安全です。

---

## 既存機能との位置づけ

今回の発表は単独で見るより、Signals 系の流れに置くと理解しやすいです。

* Agent Signals: thread に途中参加し、状態や通知を扱う基盤を作った
* Notification Inbox: 通知の保存と優先度付き配送を整えた
* WebhookSignalProvider: webhook と subscribed thread の matching を標準化した
* Custom Signal Providers: webhook 以外のイベント源にも同じ設計を広げた

この順番で見ると、Custom Signal Providers は新しい思想というより、**Signals を現実の外部システムへ広くつなぐための不足分を埋めた**発表です。

特に大きいのは、Mastra が外部イベント統合を次の 2 段に分けてきたことです。

* built-in provider: 汎用 webhook のように共通化しやすいもの
* custom provider: ソース固有の接続方式や lifecycle が必要なもの

この切り分けはかなり筋が良いと思います。何でも built-in に寄せるのではなく、**抽象を用意して、複雑な統合は自分で拡張できる**状態にしたからです。

---

## まとめ

Custom Signal Providers は、派手な UI 機能ではありません。しかし、Signals を実務で使うとすぐにぶつかる「Webhook 以外の外部イベントをどう thread に結びつけるか」という問題に対して、かなりまっすぐな答えを出しています。

これまでは、通知を送る API はあっても、外部イベントの受信、購読管理、thread 解決はアプリ側で抱えがちでした。今回からは、そこを `SignalProvider` という形でまとまり良く切り出せます。

Mastra が前進したのは、外部イベントを受けられるようになったこと以上に、**外部システムとの継続的な接続を framework の拡張ポイントとして扱い始めた**ことです。長時間動くエージェントを本当に運用していくなら、この方向はかなり重要です。

---

## 関連リンク
