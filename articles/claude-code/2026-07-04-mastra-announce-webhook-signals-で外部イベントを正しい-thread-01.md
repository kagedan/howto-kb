---
id: "2026-07-04-mastra-announce-webhook-signals-で外部イベントを正しい-thread-01"
title: "[Mastra Announce] Webhook Signals で外部イベントを「正しい thread」に自動で届ける"
url: "https://zenn.dev/shiromizuj/articles/0cf9e56ce82c5d"
source: "zenn"
category: "claude-code"
tags: ["API", "AI-agent", "OpenAI", "GPT", "zenn"]
date_published: "2026-07-04"
date_collected: "2026-07-05"
summary_by: "auto-rss"
query: ""
---

[Mastra](https://mastra.ai/) の [公式Blog](https://mastra.ai/blog) で公開された [Features](https://mastra.ai/blog/category/features) 記事をもとに、今回の発表が何を意味するのかを整理します。今回は新しいモデル機能というより、Signals の実運用を一段現実的にするための接続レイヤです。すでに Mastra は Notification Signals や Notification Inbox を持っていましたが、WebhookSignalProvider によって **外部 webhook と agent thread の対応付け** がかなり素直になりました。

[Mastra Announcements 速報解説一覧](https://zenn.dev/shiromizuj/articles/cc91bb06db5b5b)

---

2026年7月1日、Mastra は **Webhook Signals for Mastra Agents** を公開しました。ひとことで言えば、**GitHub や Slack や Stripe の webhook payload を、subscribe 済み thread へ自動的に notification signal として配送する仕組み**です。

ぱっと見ると「webhook を受ける helper が増えた」程度にも見えますが、実際にはもう少し重要です。これまで external event を agent へ届けること自体は `sendNotificationSignal()` でできました。しかし、その event が **どの thread に属する通知なのか** を解決する部分は、アプリ側で配線する必要がありました。今回の WebhookSignalProvider は、そこを標準化します。

---

## 今回の発表をひとことで言うと

WebhookSignalProvider は、webhook payload から resource id を抜き出し、subscription registry と照合して、該当する thread へ notification を送るための built-in provider です。

Signal providers docs の言い方を借りると、signal provider が持つ責務は次の 3 つです。

* subscription tracking
* ingestion
* delivery

WebhookSignalProvider はそのうち、push 型 integration で毎回ほぼ同じになる部分を共通化した実装だと考えると分かりやすいです。

* `extractResourceId()` で payload から対象 resource を取り出す
* `handleWebhook()` で subscription と照合する
* `buildNotification()` で notification の形に整える
* 一致した thread に `notify()` 相当の処理で届ける

つまり今回の追加で嬉しいのは、external event を agent に送れること自体ではなく、**「どの外部イベントをどの thread が見ているか」という bookkeeping を Mastra 側へ寄せられる**ことです。

---

## 背景: `sendNotificationSignal()` だけでは何が足りなかったのか

Mastra は 2026年6月の時点で、Signals をかなり強くしていました。

* `sendMessage()` / `queueMessage()` で途中参加できる
* `sendStateSignal()` で durable な state lane を持てる
* `sendNotificationSignal()` で外部イベントを inbox record として保存できる
* Notification Inbox で summary と full record を分けて扱える

では、なぜ今回あらためて webhook provider が必要だったのか。理由は単純で、**通知の保存・配送ポリシーと、通知対象 thread の特定は別問題**だからです。

たとえば GitHub webhook を受ける場合、利用者は少なくとも次を考える必要がありました。

* どの repository / PR / channel / customer が event の対象なのか
* その対象を watch している thread はどれか
* 一致した thread にどう notification を投げるか
* 複数 thread が同じ resource を watch していたらどう fan-out するか

`sendNotificationSignal()` は「この thread に通知を送りたい」が決まったあとには便利ですが、その前段の **matching** は助けてくれません。WebhookSignalProvider は、まさにこの隙間を埋めています。

公式記事でも、以前は `.sendNotificationSignal()` を使えたが、payload を正しい thread に送るためには追加の wiring が必要だった、と説明されています。今回からは `handleWebhook()` に webhook payload を渡すだけで、subscription と照合して right thread へ届けられます。

---

## 何が追加されたのか

### 1. generic な webhook 用 SignalProvider が built-in で入った

これまでも独自の `SignalProvider` subclass を書けば、polling provider も webhook provider も作れました。docs にある `CiSignals` の例がそれです。ただし、generic webhook source に対して毎回 subclass を起こすのは少し重い。

そこで追加されたのが `WebhookSignalProvider` です。設定は基本的に 2 つで足ります。

* `extractResourceId(payload)`
* `buildNotification(payload, subscription)`

つまり、Mastra は「Webhook を受けて subscription へ fan-out する仕組み」そのものを用意し、開発者には **resource の見つけ方と通知の形だけ決めさせる** API を出したわけです。

### 2. `handleWebhook()` が routing を肩代わりする

いちばん大きいのはここです。`handleWebhook()` は payload を受け取り、そこから resource id を取り出し、対応する subscription を引き、各 thread へ notification を送ります。

たとえば GitHub issue webhook なら、`repository.full_name` を resource id として抜き、`mastra-ai/mastra` を subscribe している thread 全員へ通知できます。

この設計の良いところは、event producer 側が threadId を知らなくてよいことです。Webhook sender は repository や channel や customer id を知っていれば十分で、**thread の所在は Mastra の subscription layer が持つ**ようになります。

### 3. `.subscribeThread()` で thread と外部 resource を結びつけられる

WebhookSignalProvider は、thread 自体ではなく **externalResourceId** に対して subscribe します。つまり発想としては、「この会話はこの GitHub repository を監視する」「この会話はこの Slack channel を見続ける」という形です。

これは Signals を thread-centric に設計している Mastra と相性が良いです。agent にとっては「いまの会話が見ている外界の対象」が一貫して thread にぶら下がるからです。

---

## 実装イメージ: GitHub webhook を Repo Agent へつなぐ

最小構成はかなり素直です。まず provider を作り、resource id の抽出方法と notification の形を決めます。

```
import { WebhookSignalProvider } from "@mastra/core/signals";

export const githubSignals = new WebhookSignalProvider({
  extractResourceId: payload => {
    const {
      repository: { full_name },
    } = payload as { repository: { full_name: string } };

    return full_name;
  },
  buildNotification: (payload, subscription) => {
    const {
      action,
      issue: { number, title },
    } = payload as {
      action: string;
      issue: { number: number; title: string };
    };

    return {
      source: "github",
      kind: action,
      priority: "urgent",
      summary: `#${number} ${title}`,
      payload,
      dedupeKey: `github:${subscription.externalResourceId}:${action}:${number}`,
    };
  },
});
```

次に agent の `signals` へ登録します。

```
import { Agent } from "@mastra/core/agent";
import { Memory } from "@mastra/memory";
import { githubSignals } from "../signals/github-signals";

export const repoAgent = new Agent({
  id: "repo-agent",
  name: "Repo Agent",
  model: "openai/gpt-5.5",
  instructions: [
    "あなたは GitHub repository を監視するエージェントです。",
    "notification-summary を受け取ったら、まず何が起きたかを短く整理してください。",
    "urgent な notification は issue や PR の状態変化として扱い、必要なら追加調査を提案してください。",
  ].join("\n"),
  signals: [githubSignals],
  memory: new Memory(),
});
```

最後に webhook route から `handleWebhook()` を呼びます。

```
import { Mastra } from "@mastra/core/mastra";
import { registerApiRoute } from "@mastra/core/server";
import { repoAgent } from "./agents/repo-agent";
import { githubSignals } from "./signals/github-signals";

export const mastra = new Mastra({
  agents: { repoAgent },
  server: {
    apiRoutes: [
      registerApiRoute("/webhooks/github", {
        method: "POST",
        handler: async c => {
          const body = await c.req.json();
          const headers = Object.fromEntries(c.req.raw.headers);

          const result = await githubSignals.handleWebhook({ body, headers });

          return c.json({ ok: true, matched: result.body.matched }, 200);
        },
      }),
    ],
  },
});
```

この後、対象 thread を subscribe すれば、matching resource に対する webhook event が自動で届きます。

```
githubSignals.subscribeThread(
  { threadId: "thread-123", resourceId: "repo-agent" },
  "mastra-ai/mastra",
);
```

---

## 何がうれしいのか

### 1. webhook sender が threadId を知らなくてよい

これは地味ですが重要です。Webhook の発信元は普通、repository 名や channel 名や customer id は知っていても、Mastra 内部の threadId は知りません。今回の provider は、その溝を埋めます。

結果として、integration 側は「どの外部 resource の event か」だけを送ればよく、**thread 解決は agent runtime 側に閉じ込められる**ようになります。

### 2. `sendNotificationSignal()` の前段が標準化される

Notification Inbox や delivery policy はすでに強力でしたが、使うたびに manual wiring を書くなら再利用性が落ちます。WebhookSignalProvider によって、notification records を活かすまでの経路が一段短くなりました。

特に GitHub、Slack、Stripe のように「resource 単位で watch し、event が来たら thread へ知らせたい」系では、そのままはまりやすいです。

### 3. custom provider と built-in provider の使い分けが明確になった

Signal providers docs は、この点をかなりうまく整理しています。

* push source を generic に受けたい: `WebhookSignalProvider`
* polling が必要: custom `SignalProvider` を書く
* durable subscriptions や独自 lifecycle、tools、processors が必要: custom provider
* GitHub の PR 活動のようにドメイン特化した機能が欲しい: `@mastra/github-signals`

つまり今回の追加は、最終形の万能 provider ではありません。**custom subclass を毎回書くには重いが、notification signals は活かしたい** という中間層を埋める API です。

### 4. thread-centric な event 設計がより実用的になる

Mastra の Signals は、最初から thread を中心に設計されています。WebhookSignalProvider はそこへ自然に乗っています。ユーザー会話、background task の結果、notification summary、external webhook がすべて同じ thread へ集まるので、agent は「いま見ている仕事」に関係する event を会話文脈の中で扱えます。

これは単なる webhook forwarding より一段上です。Mastra が狙っているのは、外部システムから agent を叩くだけではなく、**agent thread を外界と継続接続すること**だと見えてきます。

---

## 注意点: subscription registry はデフォルトでは in-memory

ここは実務上かなり大事です。Signal providers docs に明記されていますが、provider の base registry は **in-memory かつ per-process** です。つまり、デフォルトのままでは restart をまたいで subscription は残りません。

そのため本番で次の要件があるなら、追加設計が必要です。

* 再起動後も watch 状態を残したい
* 複数 instance で subscription を共有したい
* provider 起動時に過去 subscription を rehydrate したい

この場合は custom provider を作って `start()` で durable store から復元するか、外部 DB に subscription を保存する設計が必要です。WebhookSignalProvider は便利ですが、**subscription durability まで自動で解決するわけではない**点は押さえておくべきです。

また、distributed deployment では shared pub/sub も重要です。Signals docs にある通り、multi-instance で follow-up signal や wake-up を正しく扱うには Redis Streams などの共有 backend が必要です。Webhook 入口だけ作っても、配送先 run が別 instance にいるなら、そこまで届く transport も必要になります。

---

## 既存機能・関連発表との位置づけ

今回の発表は単独で見るより、6月から7月にかけての Signals 系の流れに置くと理解しやすいです。

* Agent Signals: thread へ途中参加する基本 API を整えた
* Notification Inbox: external event を durable notification として整理した
* Event System / PubSub: cross-process delivery の土台を見せた
* WebhookSignalProvider: webhook payload と subscribed thread の matching を標準化した

この順に見ると、WebhookSignalProvider は新しい哲学というより、**Signals を日常的な integration で使うための missing piece** です。

特に重要なのは、`sendNotificationSignal()` と競合する機能ではないことです。むしろ関係は次のように整理できます。

* one-off で特定 thread に通知したい: `sendNotificationSignal()`
* resource watch を前提に webhook から自動配送したい: `WebhookSignalProvider`

この切り分けはかなり分かりやすいです。

---

## まとめ

WebhookSignalProvider は、派手な新機能ではありません。しかし、Signals と Notification Inbox を実際の外部 integration へつなぐ最後の 1 マイルとしてはかなり重要です。

今回の発表で Mastra が前進したのは、agent が webhook を受けられるようになったこと以上に、**外部 resource と agent thread の対応関係を runtime の関心事として扱い始めた**ことです。これにより、GitHub repository、Slack channel、Stripe customer、独自 API の object といった「外界の対象」を、agent thread に継続的に紐づけやすくなります。

custom SignalProvider を毎回書くほどではないが、manual wiring は減らしたい。そんな現実的なユースケースにちょうど刺さる追加でした。Signals を中核に据えた Mastra の設計が、また少し実務寄りになった発表だと思います。

---

## 関連リンク
