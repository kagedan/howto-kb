---
id: "2026-06-30-mastra-announce-mastra-組込イベントで-agentworkflow外部システム-01"
title: "[Mastra Announce] Mastra 組込イベントで agent・workflow・外部システムを Pub/Sub でつなげる"
url: "https://zenn.dev/shiromizuj/articles/b0ab05c8e94e4e"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "zenn"]
date_published: "2026-06-30"
date_collected: "2026-07-01"
summary_by: "auto-rss"
query: ""
---

# [Mastra Announce] Mastra 組込イベントで agent・workflow・外部システムを Pub/Sub でつなげる

[Mastra](https://mastra.ai/) の [公式Blog](https://mastra.ai/blog) で発表された [Announcements](https://mastra.ai/blog/category/announcements) を速報ベースでお伝えします。ただの直訳ではなく、関連ドキュメントも参照したうえで手厚くしたり省略したりします。速報性重視で AI の力を多分に使っているので、私自身の考察は少なめです。

[Mastra Announcements 速報解説一覧](https://zenn.dev/shiromizuj/articles/cc91bb06db5b5b)

---

2026年6月25日、Mastra は **組み込みのイベントシステム**を発表しました。ひとことで言えば、**これまで Mastra の内部で workflow、background task、agent stream、signals を動かしていた Pub/Sub 基盤が、開発者からも使える形で前面に出てきた** という発表です。

この発表のポイントは、単に「Redis や Google Cloud Pub/Sub が使えます」という話ではありません。Mastra が最近強化してきた **Agent Signals**、**Background Tasks**、**resumable streams**、**long-running workflows** を、単一 process の都合ではなく、複数 process や複数 host を前提に動かすための共通基盤が見えやすくなったことに意味があります。

---

## 今回の発表をひとことで言うと

Mastra の event system は、workflow や agent の「裏側のイベント配送」を、そのままアプリケーション統合の表側へ持ち上げる仕組みです。

docs によれば、同じ pub/sub bus の上で次のものがすでに動いています。

* workflow execution
* scheduled workflows
* background tasks
* agent signals
* resumable streams

つまり今回の発表は、新しい単独機能というより、**Mastra 全体をつないでいるイベントバスを first-class API として公開した** ものです。これにより、Mastra 内部イベントを外部へ出すことも、外部イベントを Mastra の agent や workflow に入れることも、同じ抽象で扱えるようになります。

---

## 背景: なぜ今 event system が必要なのか

Mastra の初期の体験は、かなり自然に「1 回の API 呼び出しで agent を動かす」形でした。これは単一 process、単一 UI、短い実行時間なら十分です。しかし 2026 年の Mastra は、そこからかなり先に進んでいます。

たとえば recent release を振り返るだけでも、次のような要件が増えています。

* 数分から数時間動き続ける workflow や background task
* Slack や GitHub や監視システムから途中で割り込む agent
* 一度切れた client が stream を再接続して続きを受け取る運用
* UI を配信する instance と、実際に run を抱えている instance が別になる構成

この状況で、すべてを「その request を受けた process の中だけ」で閉じるのは苦しくなります。docs でも、たとえば active な agent run へ signal を送るには、その signal event が **その run を持っている別 process / 別 instance まで届かなければいけない** と明記されています。

要するに、Agent Signals や notification 系の機能が本当に強くなるには、その下に **process 境界を越えられるイベント基盤** が必要だったわけです。今回の発表はそこを表に出したものです。

---

## 何が追加されたのか

### 1. `Mastra` に `pubsub` backend を設定できる

いちばん分かりやすい変化は、`Mastra` インスタンスに `pubsub` を差し込めることです。開発者は backend を一度選ぶだけで、Mastra の内部イベント配送と自分の publish / subscribe の両方に同じ transport を使えます。

```
import { Mastra } from "@mastra/core";
import { RedisStreamsPubSub } from "@mastra/redis-streams";

export const mastra = new Mastra({
  pubsub: new RedisStreamsPubSub({
    url: process.env.REDIS_URL!,
  }),
});
```

選べる backend は、現時点では大きく 4 系統です。

| backend | 想定スコープ | 特徴 |
| --- | --- | --- |
| `EventEmitterPubSub` | 単一 process | デフォルト。外部サービス不要だが永続化や process 越えはしない |
| `UnixSocketPubSub` | 同一 host の複数 process | 1 process が broker になり、他 process が client として接続する |
| `RedisStreamsPubSub` | 複数 host をまたぐ分散構成 | persistence、consumer group、redelivery、replay に強い |
| `GoogleCloudPubSub` | GCP 上の分散構成 | Cloud Pub/Sub ベースで instance 間配送を担う |

この切り分けが良いのは、「アプリコードはそのままで、配送範囲だけ差し替えられる」ことです。小さく始めるときはデフォルトの in-process、複数 instance に広がったら Redis Streams へ移る、というスケールの仕方ができます。

### 2. 開発者が自分で event を publish / subscribe できる

今回、Mastra の pub/sub bus は内部専用ではなくなりました。自分の topic を定義して、外部 webhook や業務イベントを流し込めます。

```
type SignupFormData = {
  id: string;
  company: string;
  email: string;
};

type TrackedEvent = {
  name: string;
  path: string;
};

export const publishSignup = async (
  signupFormData: SignupFormData,
  trackedEvents: TrackedEvent[],
) => {
  const analystAgent = mastra.getAgent("leadAnalystAgent");
  const { text: summary } = await analystAgent.generate(
    "サインアップ前の行動ログを日本語で要約してください。",
  );

  await mastra.pubsub.publish("acme.user.signup", {
    type: "signup.created",
    runId: signupFormData.id,
    data: {
      ...signupFormData,
      trackedEvents,
      summary,
    },
  });
};
```

購読側も単純です。

```
await mastra.pubsub.subscribe("acme.user.signup", async event => {
  console.log("受け取ったイベント", event.type, event.data);
});
```

この API が嬉しいのは、Mastra を「agent framework」としてだけでなく、**agent が参加する event-driven application runtime** として扱いやすくなることです。

### 3. replay と resumable stream を transport 側で支えられる

今回の docs では replay もかなり重要な論点として扱われています。切断した client が取りこぼした stream を追いつけるのは、長時間 run や不安定な接続では本当に重要です。

`PubSub` base reference には `getHistory()`、`subscribeWithReplay()`、`subscribeFromOffset()` があり、history を持つ backend なら reconnect 後の catch-up ができます。Redis Streams のような永続化 backend ではこれが自然に効きますし、in-process の `EventEmitterPubSub` でも `CachingPubSub` をかぶせれば replay を足せます。

これは「配信が豪華になった」だけではありません。**long-running stream を現実のネットワーク事情に合わせて運用できる** という意味です。

---

## 何がうれしいのか

### 1. Agent Signals が本当に分散構成で使える

Signals docs には、active な run に送った signal は thread topic に publish され、別 process で実行中の run でも受け取れるとあります。これは逆に言うと、分散構成で signal を真面目に使うには pub/sub backend が必須だということです。

今回 event system が明確に出たことで、`sendMessage()`、`queueMessage()`、`sendSignal()`、`sendNotificationSignal()` のような API を、単なる便利機能ではなく **cross-process message delivery の上に成り立つ仕組み** として理解しやすくなりました。

長く動く coding agent や support agent を複数 instance で運用したい人には、ここがいちばん実利があります。

### 2. 外部システムとの接続点を自前キューなしで作れる

従来も、GitHub webhook を受けて database に保存し、queue に投げ、worker が拾い、必要なら agent を起こす、という構成は組めました。ただしこの設計は、アプリごとに queue の選定、再配信、consumer group、切断復旧を別々に考える必要があります。

Mastra の event system を使うと、workflow や background task がすでに乗っている bus をそのまま流用できます。つまり、**Mastra の中のイベント駆動と、業務アプリのイベント駆動を分断しなくてよい** のです。

たとえば次のような流れが素直になります。

1. Webhook が `signup.created` を publish する
2. 別 subscriber が CRM 連携を行う
3. 同時に agent が pre-signup 行動を要約する
4. 必要なら workflow が後続の onboarding 処理を走らせる

このとき topic と event type を共有しているだけで、各処理は疎結合のまま保てます。

### 3. workflow / task / stream の観測点がそろう

Appendix に並んでいる event family を見ると、この発表の意味がよく分かります。workflow orchestration、workflow watch、background task、durable agent stream、agent thread runtime まで、すでにかなり多くの runtime event が整理されています。

これは observability の観点でも嬉しいです。たとえば、

* workflow の step 完了を購読して独自メトリクスに送る
* background task の `task.failed` を拾って incident を起こす
* agent stream の `finish` や `error` を監視 UI に流す

といった連携が、Mastra の外側からも見通しよくなります。

### 4. reconnect 前提の UI を作りやすい

記事本文でも「切断した client が見逃したイベントを replay できる」と強調されています。これは派手ではありませんが、実運用ではかなり大事です。

agent や workflow が 30 秒以上動くだけで、ブラウザの再接続、モバイル回線の瞬断、reverse proxy の idle timeout は普通に起きます。そこで replay がないと、ユーザーは「今どこまで進んだのか」を見失います。

Mastra が replay を pub/sub contract の一部として持つことで、アプリ側は「再接続時に offset から購読し直す」という戦略を取りやすくなります。これがあると、長時間 run を扱う UI の設計難度がかなり下がります。

### 5. backend の切り替え基準が明確になった

Pub/Sub overview は、いつ `EventEmitterPubSub` で十分で、いつ `UnixSocketPubSub` や `RedisStreamsPubSub` が必要かをかなり明快に整理しています。

特に重要なのは、「subscriber がどこで動くか」が backend 選定基準だと明言されている点です。これにより、将来マルチ process やマルチ host へ広げる可能性があるチームでも、早い段階で構成を誤りにくくなります。

---

## 既存手法・関連機能との位置づけ

今回の発表は、6 月の Mastra の流れの中で見るとかなり納得しやすいです。

* 6 月 3 日の Agent Signals は、thread に対して message / signal / state / notification を入れる仕組みを整えた
* 6 月 24 日の Notification Inbox は、外部通知を durable record として管理する標準形を出した
* 6 月 25 日の Event System は、それらの配送を支える Pub/Sub 層を正式に見せた

つまり、Signals や Inbox が「エージェントへの文脈注入」の話だとすると、今回の Event System は **その文脈をどこからどこへ運ぶか** の話です。

また、一般的な event-driven architecture と比べても立ち位置が面白いです。多くのアプリでは queue、workflow engine、stream transport、agent runtime が別製品になりがちですが、Mastra はそれらの境界面をかなり寄せています。もちろん Redis や Google Cloud Pub/Sub は外部依存ですが、**Mastra 側の抽象は 1 つ** で済みます。

---

## まとめ

Mastra の組み込みイベントシステムで嬉しいのは、「イベントを飛ばせる」こと自体よりも、**Mastra の内部 runtime と外部システム連携が同じ bus 上にそろった** ことです。

これによって、

* signals を分散構成で安全に届けられる
* workflow や background task を外部イベントで起動しやすくなる
* reconnect 前提の stream を作りやすくなる
* observability や通知連携を runtime event ベースで組みやすくなる

という実利が出ます。

単体の blog 記事だけだと Redis Streams 対応の小粒な発表にも見えますが、docs を読むと実態はもっと広いです。これは **Mastra を単なる agent SDK から、event-driven な AI application runtime へ寄せる一歩** だと見るのがいちばんしっくりきます。
