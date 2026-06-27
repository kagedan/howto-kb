---
id: "2026-06-27-mastra-announce-外部イベントを優先度付きで溜め必要なときだけ-agent-に読ませる-01"
title: "[Mastra Announce] 外部イベントを優先度付きで溜め、必要なときだけ agent に読ませる"
url: "https://zenn.dev/shiromizuj/articles/ba40d4fe1e7aef"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "LLM", "OpenAI", "GPT", "zenn"]
date_published: "2026-06-27"
date_collected: "2026-06-28"
summary_by: "auto-rss"
query: ""
---

# [Mastra Announce] 外部イベントを優先度付きで溜め、必要なときだけ agent に読ませる

[Mastra](https://mastra.ai/) の [公式Blog](https://mastra.ai/blog) で発表された [Announcements](https://mastra.ai/blog/category/announcements) を速報ベースでお伝えします。ただの直訳ではなく、関連ドキュメントも参照したうえで手厚くしたり省略したりします。速報性重視で AI の力を多分に使っているので、私自身の考察は少なめです。

[Mastra Announcements 速報解説一覧](https://zenn.dev/shiromizuj/articles/cc91bb06db5b5b)

---

2026年6月24日、Mastra は **Notification Inbox** を発表しました。ひとことで言えば、**GitHub や Slack や Datadog から来る外部イベントを、priority 付きの durable record として thread にぶら下げ、agent が必要なときに自分で読みに行けるようにした** 機能です。

これは「通知を受け取れるようになった」というだけの話ではありません。すでに 6 月 3 日の [Agent Signals](https://mastra.ai/blog/announcing-agent-signals) で、Mastra は long-running agent に途中介入したり、外部イベントを thread へ流し込んだりできる基盤を出していました。今回の Notification Inbox は、その通知まわりを **標準化された保存形式、priority-aware delivery、agent 向けの inbox tool** まで含めて一段深く製品化したものだと見るのが正確です。

---

## 今回の発表をひとことで言うと

今回 Mastra が足したのは、単なる `sendSignal()` の sugar ではありません。外部イベントを扱う流れを、次の 3 つに分解して標準機能としてまとめています。

1. `sendNotificationSignal()` でイベントを inbox record として保存する
2. `notifications.deliveryPolicy` で priority ごとの配送ルールを決める
3. `createNotificationInboxTool()` で agent 自身が inbox を list / read / search / markSeen できるようにする

この 3 点がそろったことで、通知は「来た瞬間に文脈へ押し込まれるだけの signal」ではなくなりました。**あとで読める、検索できる、priority に応じて起こし方を変えられる、agent 側から能動的に取りに行ける** ものになっています。

公式ブログのタイトルは inbox ですが、実態としては「メール箱」ではありません。GitHub のレビュー、Slack のメンション、Sentry の障害、Datadog のアラート、社内ワークフローの承認依頼など、**external event 全般を thread ごとに整理する durable な通知ドメイン**です。

---

## 背景: Agent Signals の時点では何が足りなかったのか

6 月初旬の Agent Signals 発表時点でも、Mastra はかなり先に進んでいました。`sendMessage()` と `queueMessage()` で会話の途中参加ができ、`sendStateSignal()` で durable な state lane を持てて、`sendNotificationSignal()` で通知 record を保存して priority-aware delivery をかける土台も docs 上は見えていました。

ただ、その時点で利用者が自前で考える必要があった論点が 3 つあります。

### 1. 通知を agent にどう読ませるか

通知を保存できても、agent がそれをどう一覧し、どう必要なものだけ開き、どう既読や保留を表現するかはアプリ側で設計する必要がありました。CRUD ツールをばらばらに生やすと、instruction も UI もすぐ散らかります。

### 2. 通知を全部そのまま main loop に流すとノイズが増える

long-running agent にとって本当に困るのは「通知が来ないこと」よりも、**どうでもいい通知で reasoning loop が汚染されること**です。CI の軽微な成功ログ、Slack の雑談、GitHub の軽いリアクションまで全部割り込みで入ってくると、agent は賢くなるどころか落ち着いて仕事ができなくなります。

### 3. summary と full record の往復設計が難しい

priority-aware delivery を本気でやるなら、「いますぐ agent を起こすべき通知」と「いったん要約だけ渡して、必要ならあとで掘る通知」を分けたいはずです。ところが、その summary を見た agent があとから full record を読みに行く導線が標準化されていないと、結局アプリごとに独自流儀になります。

今回の Notification Inbox は、まさにこの 3 点を埋めています。

---

## 何がうれしいのか

### 1. summary と full record を分けて扱える

Signals docs が明確に書いている通り、Notification Signals の配信は 2 段階です。ingress では `sendNotificationSignal()` が record を保存して delivery policy を評価し、dispatch では due になった record を full notification か summary signal として流します。

この設計の何が良いかというと、agent の main loop に対して、**最初から全部の payload を投げ込まなくてよい**ことです。たとえば GitHub のコメント 20 件分や、監視アラートの詳細 JSON を毎回そのまま LLM に見せる必要はありません。まずは

* `urgent` なら即配送する
* `high` や `medium` なら summary を出す
* `low` は inbox に溜めておく

というように、文脈コストを抑えながら attention を制御できます。

### 2. 「通知を保存する層」と「モデルへ見せる層」が分離される

これまでは、外部イベントを受けたらそのまま `sendSignal()` でモデルへ渡す実装でも最低限は成立しました。しかしその方式だと、保存、既読、検索、アーカイブ、coalesce、dedupe といった運用上の論点が弱くなります。

Notification Inbox では record が先に作られ、そのうえで signal が出ます。つまり、**通知はまずデータであり、その後で文脈になる**わけです。ここがかなり実務的です。

この順番だからこそ、

* `dedupeKey` で同じ通知の重複発火を抑える
* `coalesceKey` で関連通知をまとめる
* `search` で過去通知を掘る
* `archive` や `dismiss` で inbox を掃除する

といった運用が自然にできます。

### 3. agent が能動的に inbox を読める

`createNotificationInboxTool()` が地味に重要です。このツールは notification 専用の CRUD を細切れに増やす代わりに、`list`、`read`、`markSeen`、`dismiss`、`archive`、`search` を 1 つの inbox tool にまとめます。

特に `read` が面白くて、full contents を普通の tool output として返すのではなく、**notification signal として thread に流し込む**設計になっています。つまり agent は「summary を見て、必要なら inbox を read して、その record を本物の notification context として取り込む」という自然な流れで動けます。

これは長時間エージェントにかなり合っています。最初から payload 全部を見せるのではなく、**summary で気づき、必要なときだけ掘る** からです。

### 4. 人間向け UI と agent の自律行動を両立しやすい

Notification Inbox は agent のためだけの機能にも見えますが、実は UI 側にも効きます。record が durable なので、人間向けの inbox 画面を作るのも簡単になりますし、同じ thread を見ている人間と agent が同じ通知基盤を共有できます。

たとえば SRE agent なら、

* urgent な障害だけは agent を即 wake する
* medium は summary として観測画面に出す
* low は夜間バッチでまとめて見る

というように、**自律行動と人間の triage を同じ inbox で共存**させやすくなります。

---

## 今までと比べて、どこがどう進んだのか

比較すると差分が見えやすいです。

| 観点 | 従来の `sendSignal()` ベース | Notification Inbox |
| --- | --- | --- |
| 保存 | 必要なら自前で設計 | `notifications` storage domain に durable record として保存 |
| 優先度 | attributes で表現はできるが配送制御は薄い | `priority` と `deliveryPolicy` が一級概念 |
| 重複抑止 | アプリ側で実装 | `dedupeKey` と `coalesceKey` を標準サポート |
| 既読・整理 | 自前ツールが必要 | inbox tool で `markSeen` / `dismiss` / `archive` |
| summary と full 詳細 | 自前設計 | summary signal と `read` の流れが標準化 |
| agent の能動利用 | そのままでは弱い | `createNotificationInboxTool()` で一覧・検索・既読が可能 |

この表が示しているのは、Notification Inbox が単に「通知 API をもう 1 本追加した」ものではなく、**通知をプロダクト機能として成立させる最低限のオペレーション面まで面倒を見るようになった** ということです。

---

## delivery policy のデフォルト挙動が実務的

docs を読むと、デフォルトの priority-aware delivery はかなり現実的です。

* `urgent`: すぐ full notification を配信する
* `high`: thread が idle なら即配送、active ならまず summary を出して full delivery は idle 時まで待つ
* `medium`: idle なら即配送、active なら summary バッチ化する
* `low`: active / idle の両方で summary バッチに寄せ、idle 時は model loop を起こさない

ここが良いのは、priority が単なるラベルで終わっていないことです。**priority がそのまま「agent の注意を今どれだけ奪ってよいか」の制御に変換される**からです。

とくに `high` の扱いがうまくて、作業中の agent に対してはまず summary を出し、落ち着いたタイミングで full delivery に回せます。これは「重要だけど、いまの思考をぶった切るほどではない」通知を扱うのにちょうどよいです。

---

## 具体的な実装方法

ここからは、GitHub の PR 通知を扱う review agent を例に最小構成を組みます。ポイントは 3 段階です。

1. `notifications` storage を取る
2. agent に inbox tool と delivery policy を載せる
3. 外部イベント受信口から `sendNotificationSignal()` を呼ぶ

Notification Inbox は Memory と durable storage が前提です。Signals docs では、notification inbox storage を使える adapter として libSQL、PostgreSQL、MongoDB が挙げられています。最小例なら libSQL が分かりやすいです。

```
import { Agent } from "@mastra/core/agent";
import { createNotificationInboxTool } from "@mastra/core/notifications";
import { Memory } from "@mastra/memory";
import { LibSQLStore } from "@mastra/libsql";

const storage = new LibSQLStore({
  id: "github-review-storage",
  url: "file:./mastra.db",
});

const notificationsStorage = await storage.getStore("notifications");

export const githubReviewAgent = new Agent({
  id: "github-review-agent",
  name: "GitHub Review Agent",
  instructions: [
    "あなたは GitHub の pull request を監視してレビュー対応を支援するエージェントです。",
    "notification-summary を受け取ったら、まず要約から PR への影響度を判断してください。",
    "詳細が必要なら notificationInbox を使って read または search を実行してください。",
    "urgent な通知は即座に PR のリスク、必要な確認事項、次のアクションを整理し、medium 以下は inbox を一覧して関連性の高いものだけ扱ってください。",
    "同じ PR から似た通知が繰り返し届いている場合は、dedupe や coalesce されている前提を踏まえて、重複対応を避けてください。",
  ],
  model: "openai/gpt-5.5",
  memory: new Memory(),
  tools: {
    notificationInbox: createNotificationInboxTool({
      storage: notificationsStorage,
    }),
  },
  notifications: {
    deliveryPolicy: {
      priorities: {
        urgent: "deliver",
        high: "summarize",
        medium: "defer",
        low: "persist",
      },
      decide: ({ record }) => {
        // 軽微な CI 成功通知はすぐ読ませず、後でまとめて扱う
        if (record.source === "github" && record.kind === "ci-success") {
          return {
            action: "summarize",
            summaryAt: new Date(Date.now() + 60 * 60 * 1000),
          };
        }
      },
    },
  },
});
```

ここで重要なのは、agent の instruction までセットで設計することです。Notification Inbox はツールを載せただけでは十分ではありません。モデルが

* summary を受けたら慌てて全部読まない
* まず list や search で inbox の形を見る
* 必要なときだけ read する
* 読み終えた通知は `markSeen` や `archive` で整理する

という運用を学んでいないと、せっかくの priority-aware delivery が効きません。

### 2. 外部イベントを `sendNotificationSignal()` で流し込む

次に、GitHub webhook から event を受けたら `sendNotificationSignal()` を呼びます。

```
import { mastra } from "../mastra";

const githubReviewAgent = mastra.getAgent("github-review-agent");

export async function handleGitHubWebhook(event: {
  action: "submitted" | "created" | "completed";
  repository: string;
  pullRequestNumber: number;
  reviewState?: "commented" | "approved" | "changes_requested";
  commentBody?: string;
  conclusion?: "success" | "failure";
}) {
  const priority =
    event.reviewState === "changes_requested" || event.conclusion === "failure"
      ? "urgent"
      : event.reviewState === "approved"
        ? "low"
        : "medium";

  await githubReviewAgent.sendNotificationSignal(
    {
      source: "github",
      kind: event.reviewState
        ? `pull-request-review-${event.reviewState}`
        : `ci-${event.conclusion}`,
      priority,
      summary:
        event.reviewState === "changes_requested"
          ? `PR #${event.pullRequestNumber} に変更要求レビューが付きました。`
          : event.reviewState === "approved"
            ? `PR #${event.pullRequestNumber} が承認されました。`
            : event.conclusion === "failure"
              ? `PR #${event.pullRequestNumber} の CI が失敗しました。`
              : `PR #${event.pullRequestNumber} に新しいレビューイベントがあります。`,
      payload: {
        repository: event.repository,
        pullRequestNumber: event.pullRequestNumber,
        reviewState: event.reviewState,
        commentBody: event.commentBody,
        conclusion: event.conclusion,
      },
      dedupeKey: `github:${event.repository}:pr:${event.pullRequestNumber}:${event.action}:${event.reviewState ?? event.conclusion ?? "event"}`,
      coalesceKey: `github:${event.repository}:pr:${event.pullRequestNumber}`,
      attributes: {
        repository: event.repository,
        pr: event.pullRequestNumber,
      },
    },
    {
      resourceId: "engineering-team",
      threadId: `github-pr-${event.repository.replace("/", "-")}-${event.pullRequestNumber}`,
    },
  );
}
```

この例では `threadId` を PR 単位にしています。ここはかなり大事です。Notification Inbox の使い勝手は、**どの粒度で thread を切るか** に強く依存します。

* PR 単位で追いたいなら `threadId` は PR ごと
* 顧客問い合わせなら ticket ごと
* CI 監視なら workflow や branch ごと

という設計にすると、inbox の意味がぶれにくくなります。

### 3. agent に inbox を能動利用させる

`createNotificationInboxTool()` の action は `list`、`read`、`markSeen`、`dismiss`、`archive`、`search` です。特に押さえたいのは次の 3 つです。

* `list`: いま何が溜まっているかを把握する
* `search`: source や priority や query で対象を絞る
* `read`: pending / delivered な record を signal として thread に取り込む

このとき `read` は普通の tool output として全文を返すのではなく、notification contents を signal として再注入します。つまり、agent から見ると「ツールで DB を読んだ」のではなく、**必要な通知だけが正式な notification context として届く** 振る舞いになります。ここが設計上かなりきれいです。

もし instruction をもう少し明示したいなら、次のように書くと安定しやすいはずです。

```
const instructions = [
  "あなたは GitHub 通知を扱うエージェントです。",
  "notification-summary を受け取ったときは、まず inbox の一覧を見て、priority と source を確認してください。",
  "summary だけで十分な場合は読み込まず、レビュー本文や CI 結果が必要な通知だけ read してください。",
  "対応不要な通知は dismiss、後で参照するがいまは不要な通知は archive、確認済みは markSeen を使って整理してください。",
];
```

### 4. 人間向け subscriber をつないでおくと運用しやすい

Signals 系機能なので、実際の運用では `subscribeToThread()` で thread を購読しておく構成が相性良いです。agent を wake した通知だけでなく、summary signal や full notification signal も同じ stream で観測できます。

UI 側では、

* `notification-summary` を受けたら inbox バッジを増やす
* urgent notification を受けたら対象 PR の詳細画面を前面に出す
* agent が `markSeen` した通知は一覧から薄くする

といった表現がしやすくなります。

---

## 実装時に気をつけたい点

### 1. `sendSignal({ type: "notification" })` との使い分けを誤らない

docs が明記している通り、`sendNotificationSignal()` は durable inbox record を前提にした API です。一方で `sendSignal({ type: "notification" })` は、notification っぽい形の低レベル文脈を thread へ入れたいだけのときに向いています。

つまり、

* 保存したい、あとで読みたい、優先度制御したい: `sendNotificationSignal()`
* 一時的な system context として差し込みたい: `sendSignal()`

という整理です。

### 2. storage adapter の対応を先に確認する

Signals docs では、notification inbox storage を扱える adapter として libSQL、PostgreSQL、MongoDB が挙げられています。SQLite 風だから何でもよい、という話ではありません。**`getStore("notifications")` を出せる adapter を使っているか** を先に確認したほうが安全です。

### 3. priority 設計を雑にしない

priority は UI の色分けではなく、agent の注意制御そのものです。`high` と `urgent` を全部同じ扱いにすると、せっかくの設計が死にます。

実務ではまず、

* いま思考を止めてでも見せたいか
* summary だけ先に見せればよいか
* agent を起こさず保存だけでよいか

の 3 観点で分類すると設計しやすいです。

### 4. thread 粒度が悪いと inbox 全体がノイズになる

Notification Inbox は thread 単位で効きます。つまり、thread 設計が雑だと通知整理も崩れます。たとえば「チーム全体の全通知を 1 thread に集める」構成だと、検索も既読管理も delivery policy もすぐ厳しくなります。

最初は、PR、incident、ticket のように **1 件の仕事単位で thread を切る** ほうがうまくいきやすいです。

---

## 既存機能との位置づけ

今回の発表は、ここ数週間の Mastra の流れとかなり綺麗につながっています。

* Agent Signals: thread へ途中入力や state を入れる通信路
* Task Lists: その thread の中で計画と進捗を構造化する仕組み
* Notification Inbox: 外部イベントを durable かつ priority-aware に管理する仕組み

この並びで見ると、Mastra は単なる tool-calling フレームワークから、**長時間・複数参加者・外部イベント駆動の runtime** をかなり本気で作り込んでいるのが分かります。

特に Notification Inbox は、thread を「会話履歴」ではなく **案件単位の実行面** として扱う方向をさらに押し進めています。会話、状態、進捗、通知が全部同じ thread に集まり、そのうえで agent も人間も途中参加できる。この構図が、いまの Mastra の強みです。

---

## まとめ

Notification Inbox の本質は、「agent が通知を受け取れる」ことではありません。**通知を durable record として持ち、priority に応じて注意の奪い方を変え、必要なときだけ agent が詳細を読みに行ける** ようになったことです。

これによって、これまで自前実装しがちだった

* 通知の保存
* 重複抑止
* summary と full delivery の分離
* 既読やアーカイブ
* agent からの能動的な inbox 利用

が、Mastra の標準設計に寄ってきました。

GitHub レビュー支援、SRE 障害対応、Slack ベースの業務エージェント、個人アシスタントなど、外部イベントを扱う agent ではかなり広く効くはずです。6 月 3 日の Signals 発表を読んだときに「通知 inbox を agent に与えると面白そう」と感じた人にとっては、今回はその予感がようやく **具体的な API と運用モデルになって降りてきた** 発表だったと言ってよいと思います。
