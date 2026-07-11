---
id: "2026-07-11-mastra-announce-schedules-で-agent-と-workflow-の定期実行-01"
title: "[Mastra Announce] Schedules で Agent と Workflow の定期実行がやっと同じ土俵に乗った"
url: "https://zenn.dev/shiromizuj/articles/e89be57cde5434"
source: "zenn"
category: "claude-code"
tags: ["prompt-engineering", "API", "AI-agent", "zenn"]
date_published: "2026-07-11"
date_collected: "2026-07-12"
summary_by: "auto-rss"
query: ""
---

[Mastra](https://mastra.ai/) の [公式Blog](https://mastra.ai/blog) で発表された [Announcements](https://mastra.ai/blog/category/announcements) を速報ベースでお伝えします。ただの直訳ではなく、関連ドキュメントも参照したうえで手厚くしたり省略したりします。速報性重視でAIの力を多分に使っているので、私自身の考察は少なめです。

[Mastra Announcements 速報解説一覧](https://zenn.dev/shiromizuj/articles/cc91bb06db5b5b)

---

2026年7月8日、Mastra は **Schedules** を発表しました。Agent と Workflow の両方を `cron` で定期実行し、その作成・停止・再開・手動実行までを **`mastra.schedules` という 1 つの API で扱える**ようにする機能です。

今回の価値は、単に「cron が書けるようになった」ことではありません。これまでの Mastra では、Workflow のスケジュールは Workflow 定義に寄り、Agent の定期実行は Workflow 経由や外部ジョブに逃がしがちでした。つまり **定期実行の考え方が Agent と Workflow で分裂していた**わけです。Schedules はそこを埋めて、Mastra の中で自動実行を統一的に扱えるようにしました。

---

## これまで何が課題だったのか

### Workflow には schedule があったが、Agent には「定期実行の第一級 API」がなかった

Mastra は以前から Workflow に `schedule` フィールドを持たせる仕組みを提供していました。たとえば「毎朝 9 時に日次レポートを走らせる」といった用途は、Workflow 側に宣言的に書けました。

ただしこのやり方は、あくまで **Workflow 定義の一部として schedule を宣言する**ものです。Agent を単体で「毎時 1 回動かす」「夜間にだけ実行する」「一時停止して再開する」といった運用を、同じ感覚では扱えませんでした。

結果として、Agent の定期実行をやりたいときは次のような回り道が必要でした。

* Workflow の step から `agent.generate()` や `agent.stream()` を呼ぶ
* Agent を Workflow の step としてラップする
* Mastra の外で cron やジョブキューを持ち、API 経由で Agent を起動する

つまり、**Agent 自体をスケジュールしたいのに、Workflow か外部運用基盤に責務を逃がす**構造になっていたわけです。

### 運用 API が分かれていた

従来の scheduled workflows は、基本的には「コードで定義して、Mastra 起動時に読み込ませる」モデルです。もちろん pause / resume のような運用操作はありましたが、概念の入り口は Workflow 定義でした。

一方で、今回の announcement が示しているのは、**Agent と Workflow を同じ CRUD ライクな surface で扱う**方向です。

* 作る: `create()`
* 止める: `pause()`
* 再開する: `resume()`
* いま 1 回だけ走らせる: `run()`
* 消す: `delete()`

この統一がない状態だと、開発者は「これは Workflow だからこの作法」「これは Agent だから別の作法」と覚え分ける必要がありました。

### 会話文脈を持つ定期実行がやや分かりづらかった

Agent は本来、会話や thread を持ちながら継続的に動けるのが強みです。Mastra では signals によって、稼働中の thread に新しい入力を差し込んだり、idle 中の thread を起こしたりできます。

ただ、定期実行の文脈ではこの仕組みが少し見えにくかった。定期的なチェックを「単発のバッチ」として走らせたいのか、それとも「既存 thread に毎朝のチェックインを送りたい」のかで、実装上の意味はかなり違います。

今回の Schedules はここを **threadless** と **threaded** に分けて明示しました。これは単なる API の都合ではなく、Agent 的な定期実行をどう考えるかを整理した、かなり重要な設計です。

---

## Schedules で何が変わったのか

### Agent と Workflow を 1 つの API で扱える

今回の中心は `mastra.schedules` です。Agent を実行したいなら `agentId`、Workflow を実行したいなら `workflowId` を渡して schedule を作ります。

```
const statusSchedule = await mastra.schedules.create({
  agentId: 'uptime-agent',
  cron: '0 * * * *',
  prompt: 'サービスの稼働状況を確認して、1 文で報告してください。',
})

const reportSchedule = await mastra.schedules.create({
  workflowId: 'daily-report',
  cron: '0 9 * * *',
  inputData: { userId: 'system' },
})
```

この統一によって、「定期実行したい対象が Agent か Workflow か」は入力 shape の違いに縮みます。運用の mental model はかなり単純になります。

### Agent schedule には threadless と threaded の 2 モードがある

Agent schedule の一番重要な設計はここです。

#### threadless

`threadId` を渡さなければ、各 fire は独立した `agent.generate()` 実行になります。会話履歴にぶら下がらないため、ヘルスチェック、日次要約、定型レポートのような **1 回ごとに完結する仕事** に向いています。

```
await mastra.schedules.create({
  agentId: 'uptime-agent',
  cron: '@hourly',
  prompt: '監視対象のエンドポイントを確認して現在の状態を報告してください。',
})
```

#### threaded

`threadId` と `resourceId` を渡すと、その schedule は thread に signal を送ります。つまり定期実行が **会話の続きとして入ってくる** 形になります。

```
await mastra.schedules.create({
  agentId: 'customer-success-agent',
  cron: '0 9 * * 1-5',
  prompt: '昨日から増えた重要通知を要約してください。',
  threadId: 'team-checkin-thread',
  resourceId: 'customer-success-team',
  signalType: 'user',
  ifIdle: { behavior: 'wake' },
})
```

この区別が入ったことで、「定期実行 = バッチ」ではなく、**定期的に thread へ入力する**という Agent らしいユースケースが正面から扱えるようになりました。

### Signals と自然につながる

threaded schedule は内部的に signal を使います。つまり、もともと Mastra が持っていた「idle なら起こす」「active なら捨てる / 次に回す / その場で扱う」といった thread 制御を、schedule 側にもそのまま持ち込めます。

たとえば docs の例では、次のような指定が可能です。

```
await mastra.schedules.create({
  agentId: 'pinger',
  cron: '0 9 * * *',
  prompt: '昨日からの変化を要約してください。',
  threadId: 'thread-123',
  resourceId: 'user-456',
  tagName: 'check-in',
  attributes: { source: 'cron' },
  ifActive: { behavior: 'discard' },
  ifIdle: {
    behavior: 'wake',
    streamOptions: { requestContext: { locale: 'ja-JP' } },
  },
})
```

ここで重要なのは、schedule が単なる時刻トリガーではなく、**Agent thread にどう届けるかまで含めた配送ルール**を持てることです。

### lifecycle hooks で「実行前後の運用ロジック」も載せられる

Schedules には `prepare`、`onFinish`、`onError`、`onAbort` といった hook が用意されています。これにより、fire の直前に prompt を差し替えたり、失敗時に通知したり、完了後に監査ログへ書いたりできます。

```
const mastra = new Mastra({
  agents: { uptimeAgent },
  storage: new LibSQLStore({ url: 'file:./mastra.db' }),
  schedules: {
    prepare: async ({ schedule, trigger }) => {
      return {
        prompt: `現在時刻 ${trigger.firedAt.toISOString()} 時点の稼働状況を確認してください。`,
      }
    },
    onError: async ({ phase, error }) => {
      console.error('schedule 実行エラー', phase, error)
    },
  },
})
```

以前は外部ジョブ基盤で持たせがちだった「実行ごとの差し替え」や「失敗時の運用処理」を、Mastra 側へ寄せやすくなりました。

---

## 今回の発表で、従来の課題はどう解決されたのか

### 解決したこと 1: Agent の定期実行が Workflow の回り道なしで書ける

これが最も分かりやすい改善です。今後は Agent を定期実行したいだけなら、わざわざ Workflow の step に閉じ込める必要がありません。

これは API の短縮以上の意味があります。Mastra が **「Agent を単発で呼ぶもの」ではなく「継続運用できる主体」** として定期実行を扱い始めた、ということだからです。

### 解決したこと 2: Workflow と Agent の運用 surface が揃った

統一 API により、作成・停止・再開・手動実行・削除の作法が揃いました。これで Studio やクライアント SDK、運用用 UI を作るときも一貫した扱いができます。

特に `pause()` と `resume()` が durable で、`run()` が cadence を崩さず即時実行できる点は実運用で効きます。トラブル時に止め、修正後に再開し、必要ならその場で 1 回だけ再実行する、という流れが自然になりました。

### 解決したこと 3: 「会話を持つ自動化」が API として見えるようになった

threaded schedule は、Agent の会話 thread に定期的な入力を送る仕組みです。これは単なる cron 実行ではなく、「昨日からの差分を毎朝伝える」「営業時間の開始時にチェックインさせる」「通知の要約を一定間隔で投入する」といった、**対話型エージェントらしい自動化** を素直に表現できます。

ここは Workflow の schedule だけでは埋めづらかった部分です。今回の発表は、Signals と Schedules をつなぐことで、その空白をかなりきれいに埋めています。

---

## ただし、まだ理解しておきたい前提もある

### storage adapter は必須

Schedules は永続化される仕組みなので、schedules ドメインをサポートした storage adapter が必要です。リファレンスでは `@mastra/libsql`、`@mastra/pg`、`@mastra/mysql`、`@mastra/mongodb`、`@mastra/convex`、`@mastra/spanner` などが挙がっています。

つまり、インメモリ実行のまま「ちょっと cron だけ使う」という機能ではありません。**再起動や再デプロイをまたいで残る運用機能** として設計されています。

### threaded schedule には thread と resource の設計が要る

threaded schedule を使うなら、`threadId` と `resourceId` を設計しなければなりません。どの会話に対して、誰の文脈として、どの schedule が信号を送るのかを決める必要があります。

これは面倒にも見えますが、逆に言えば Mastra が「会話に対する定期入力」を雑に隠していないということです。Agent を会話主体として使うなら、ここは避けて通れない設計点です。

### 長寿命プロセス前提の理解は引き続き重要

Workflow の schedule ドキュメントでは、組み込み scheduler が schedules table をポーリングする長寿命プロセス前提であること、サーバーレス環境ではそのままでは tick が継続しないことが説明されています。

今回の unified schedules も同じ Mastra の scheduler / storage / dispatch の流れに乗るため、**どこで scheduler を動かすのか** は引き続き重要です。発表だけ読んで「Vercel に置けば自動で毎時動く」と思い込むと危険です。

---

## どんなユースケースで効きそうか

### Agent schedule 向き

* 稼働監視やヘルスチェック
* 毎朝の通知要約や inbox triage
* 営業開始前のチェックイン
* 定期的なナッジやリマインダー送信

### Workflow schedule 向き

* 日次 / 週次のバッチレポート
* ETL やデータ集計の定期実行
* 複数 step を持つ決まった業務フロー

使い分けの目安は単純です。**会話 thread に入れたいなら Agent schedule、決まった入力で deterministic に流したいなら Workflow schedule** と考えると整理しやすいです。

---

## まとめ

今回の Schedules は、Mastra に cron が増えたというより、**自動化の置き場所を Agent と Workflow の両方に対して揃えた**発表です。

これまで Workflow 側に寄っていた schedule の考え方と、Signals を通じて会話主体として動ける Agent の世界が、`mastra.schedules` でようやく接続されました。とくに threaded schedule は、定期実行を「会話への入力」として扱える点で、Agent framework らしい設計になっています。

一方で、storage adapter、thread 設計、長寿命プロセスといった運用前提はむしろ明確になりました。手軽な sugar ではなく、**本番運用を見据えた scheduling surface が Mastra に入った**と捉えるのがいちばん正確だと思います。
