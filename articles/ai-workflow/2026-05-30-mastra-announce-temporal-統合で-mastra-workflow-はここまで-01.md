---
id: "2026-05-30-mastra-announce-temporal-統合で-mastra-workflow-はここまで-01"
title: "[Mastra Announce] Temporal 統合で Mastra Workflow はここまで強化された"
url: "https://zenn.dev/shiromizuj/articles/ab47e668fe3d92"
source: "zenn"
category: "ai-workflow"
tags: ["API", "LLM", "zenn"]
date_published: "2026-05-30"
date_collected: "2026-05-31"
summary_by: "auto-rss"
query: ""
---

[Mastra](https://mastra.ai/) の[公式Blog](https://mastra.ai/blog)で発表された[Features](https://mastra.ai/blog/category/features)記事を速報ベースでお伝えします。ただの直訳ではなく、周辺情報も補いながら、なるべく「なぜこの機能が必要なのか」まで分かるように整理します。速報性重視のため一部は公開情報ベースの解釈を含みますが、事実と推測は分けて書きます。

[Mastra Announcements 速報解説一覧](https://zenn.dev/shiromizuj/articles/cc91bb06db5b5b)

---

## 前回のアナウンスのさらなる深掘り記事が公開された

2026年5月12日の発表「Temporal Workflows 登場」の記事では、Mastra に Temporal 統合が追加されたことをお伝えしました。

<https://zenn.dev/shiromizuj/articles/4c812b32c421c0>

前回の記事で扱ったのは次のような内容です。

* Temporal とは何か（durable execution platform）
* なぜ Inngest の次に Temporal なのか
* Mastra の `createWorkflow()` / `createStep()` が Temporal Activity / Workflow にマッピングされる構造
* `@mastra/temporal` の基本的なセットアップ手順（init → import 差し替え → Worker 常駐）

これらは前回の記事で丁寧に書いたつもりなので、本記事では繰り返しません。

2026年5月27日、Mastra はそのフォローアップとして **「Mastra Workflows, Enhanced」** という Feature 記事を公開しました。今回は新機能ではなく、前回の統合で何ができるかをさらに深掘りした記事です。

タイトルの通り、「Temporal を入れると具体的に何が強化されるのか」を4つの軸で整理したものです。本記事ではその4つを深掘りしながら、技術的な背景と実務への影響を補足します。

---

## 1. Workflow Snapshots — 壊れにくさの仕組みを理解する

### Mastra のスナップショット機構

Mastra の Workflow は、各ステップの実行結果を**スナップショット**として永続化する仕組みを持っています。

「スナップショット」とはざっくり言うと、「**そのステップが完了した時点での全ステップのコンテキストを保存したデータ**」です。ステップ A → B → C という流れがあって B が失敗した場合、「A は成功済み」という情報がスナップショットとして残ります。再実行するとき、Mastra はこのスナップショットを読み込んで、**A をスキップして B から再開**できます。

公式記事はこう説明しています。

> Every step of a workflow persists as a data snapshot with all step context. Any failure can be restarted from the last step, providing workflow stability.

これは「数秒で終わる処理」ではあまり意味がないかもしれません。しかし実務では、一つ一つのステップが数十秒〜数分かかる処理を何十ステップも直列・並列で組み合わせるケースがあります。そういった場面でスナップショットは実質的な保険になります。

### Temporal が加える「分散レベルの耐障害性」

Mastra 単体のスナップショット機構は「プロセス内」での状態管理です。つまり、アプリケーション自体がクラッシュしたり、コンテナが強制終了されたりしたとき、スナップショットの保存先によって挙動が変わります。

Temporal を使うと、ワークフローの状態管理は **Temporal Server 側**に移ります。Temporal Server は独立したプロセスであり、複数のサーバーにクラスタリングして動かすことができます。

```
Mastra Worker (あなたのアプリ) ←→ Temporal Server (分散クラスタ)
                                         ↕
                                    永続化ストア (DB)
```

ワークフローの履歴や可変状態は Temporal Server の永続化ストアに保存されるため、**Mastra Worker がクラッシュしても、ネットワーク障害が発生しても、データセンターに問題が起きても**、ワークフローの状態は保たれます。Worker が復帰すれば、中断した地点から再開できます。

公式記事のフレーズを借りると：

> These workflows can survive failures, network outages, data center issues, etc. And no need for manual intervention.

「手動介入不要で、ネットワーク障害やデータセンター障害を乗り越えられる」というのが Temporal + Mastra の組み合わせが目指す姿です。

---

## 2. Advanced Retries — リトライをどこまで制御できるか

リトライは Workflow の安定性を左右する重要な仕組みです。今回の記事で最も情報が厚かったのがこのセクションです。

### Mastra 組み込みの `RetryConfig`

Mastra はもともと、ステップまたはワークフロー単位でリトライを設定できる `RetryConfig` インターフェースを持っています。

```
interface RetryConfig {
  /** 失敗と判定するまでの最大リトライ回数 */
  maxRetries?: number;

  /** リトライ間の待機時間（ミリ秒） */
  retryDelayMs?: number;

  /** 指数バックオフの倍率。次のリトライ待機時間 = retryDelayMs × backoffMultiplier^n */
  backoffMultiplier?: number;

  /** バックオフで延び続けた場合の上限（ミリ秒） */
  maxRetryDelayMs?: number;

  /** どのエラーをリトライ対象とするかを判定するコールバック */
  retryableErrors?: (error: Error) => boolean;
}
```

これだけでも、かなり細かく制御できます。たとえば「最大5回、初回は1秒待って倍々に増やすが上限は30秒まで、`NetworkError` だけリトライ対象にする」といった設定が書けます。

### Temporal 統合で何が変わるか

Temporal は Mastra の `RetryConfig` をそのまま受け継いだうえで、さらに4つの機能を追加します。

#### ① ステップの「中」をリトライできる

Mastra の `RetryConfig` は、**ステップ全体**をリトライの単位とします。ステップの中で複数の処理（外部 API 呼び出し → DB 保存 → 通知送信など）があっても、どれかが失敗したらステップを最初からやり直す形です。

Temporal では、**ステップ（Activity）の中の特定のアクション・コールだけをリトライ対象**にできます。Temporal の Activity は処理の最小単位として粒度を細かく設計できるため、「外部 API 呼び出しだけをリトライし、その後の DB 保存は成功していたら再実行しない」という構成が可能です。

これは規模が大きくなるほど効果的です。1ステップに多くの処理を詰め込んだワークフローでも、Temporal では失敗箇所の粒度で再試行を制御できます。

#### ② Jitter — カスケード障害を防ぐ散らし

**Jitter（ジッター）** とは、リトライのタイミングにランダムなばらつきを加える手法です。一見シンプルですが、大規模分散システムでは重要な設計原則です。

なぜ必要なのか。

あるサービスが一時的に過負荷になり、同時に 100 個のリクエストが失敗したとします。Jitter なしで全員が「3秒後にリトライ」を実行すると、**また同時に 100 個のリクエストがサービスに殺到**します。これが **Thundering Herd 問題**（または「同期リトライ」によるカスケード障害）の典型例です。

Jitter を入れると、100個のリトライが「2.1秒後」「3.4秒後」「2.8秒後」... のようにランダムに散らばるため、サービスへの集中が緩和されます。

Temporal はリトライに Jitter を標準で組み込んでいるため、Mastra + Temporal で組んだワークフローはこの問題を意識せずに自然に回避しやすい設計になります。

#### ③ Max Retry Time — 時間ベースの制限

Mastra の `RetryConfig` では `maxRetries` で「回数」を制限します。しかし実務では「何回まで」より「何分以内に諦める」の方が都合が良い場面があります。

たとえばバックオフが大きくなった状態でリトライを繰り返すと、件数が少なくても合計で数十分待つことがあります。そのような場合、**時間で上限を切る**方が SLA の観点で分かりやすいです。

Temporal では「15分以内にリトライを繰り返し続け、15分経ったら失敗扱い」という設定が可能です。SLA がある業務フローや「数時間かけても失敗したらアラートを上げたい」という場合、時間ベースの制限は回数ベースより直感的に設計できます。

#### ④ Separate Server — リトライ自体が壊れない

Mastra 単体のリトライ制御は Mastra プロセス内で管理されます。Worker プロセスがクラッシュすると、リトライのスケジュールそのものも失われます。

Temporal では、リトライのスケジュール管理も **Temporal Server 側**が担います。Worker がクラッシュしてもリトライのスケジュールは消えず、Worker が再起動すれば既定のタイミングで再試行が再開されます。

### `startToCloseTimeout` — Activity の実行時間上限

Temporal 統合で使える設定の中で、見落としやすいがよく使うのが `startToCloseTimeout` です。これは **1回の Activity（ステップ）が実行開始から完了するまでの最大時間**で、デフォルトは 1分です。

外部 API の呼び出しが想定以上に時間がかかるケースや、LLM の推論に数分かかるケースでは、この値を引き上げる必要があります。

```
export const { createWorkflow, createStep } = init({
  client,
  taskQueue: 'mastra',
  startToCloseTimeout: '5 minutes',  // デフォルト 1 minute から変更
})
```

`maxRetries` との組み合わせでリトライ設計をする際は、1回の実行時間上限も一緒に考えておくと、意図しないタイムアウトを防ぎやすくなります。

---

## 3. More Complex Scheduling — スケジューリングの比較

ワークフローを「いつ動かすか」を制御するスケジューリングも、今回の記事で取り上げられていた重要なトピックです。

### Mastra 組み込みの cron スケジューリング

Mastra は `createWorkflow()` の中で `cron` フィールドを指定するだけで、定期実行が設定できます。

```
const workflow = createWorkflow({
  id: 'daily-report-workflow',
  inputSchema: z.object({ reportType: z.string() }),
  outputSchema: z.object({ generated: z.boolean() }),
  steps: [generateReportStep],
  // 毎日深夜 0 時に実行
  cron: '0 0 * * *',
})
```

cron 構文で「毎日0時」「毎週月曜9時」「毎時15分」などを1行で設定できます。さらに `concurrency`（同時実行数の制限）、`rateLimit`（レートリミット）、`priority`（優先度）も組み合わせられます。

シンプルなユースケースであれば、これで十分です。

### Temporal のスケジューリング — 独立したリソースとして扱う

Temporal では、スケジュールはワークフロー定義とは**独立したリソース**として扱われます。`client.schedule.create()` を使って専用の定義を作ります。

```
// スケジュールを定義・作成する
const handle = await client.schedule.create({
  scheduleId: 'daily-report',
  spec: {
    intervals: [{
      every: Duration.ofDays(1)
    }]
  },
  action: {
    type: 'StartWorkflow',
    workflowType: 'dailyReport',
    input: { reportType: 'daily' }
  }
})
```

一見コードが増えますが、このアプローチには独自の強みがあります。

#### タイムゾーン対応

Mastra 組み込みの cron は UTC 基準で動作します。「東京時間の午前9時にバッチを走らせたい」のような要件は、UTC との時差計算を手動でやるか、ライブラリで吸収する必要があります。

Temporal のスケジュール定義ではタイムゾーンを直接指定できるため、「America/New\_York の営業時間内だけ実行する」「Asia/Tokyo の午前8時に毎日起動する」といった設定をコードレベルで素直に表現できます。グローバルなチームや地域ごとのバッチ処理では、この差が大きくなります。

#### カレンダーベースの実行

「毎月第一月曜日」「月末だけ実行」「特定の祝日を除く平日」といったルールは、通常の cron 構文では表現しにくいです。Temporal はカレンダーベースのスケジュール定義をサポートしており、より複雑なスケジューリングルールを自然に記述できます。

#### Temporal UI でのスケジュール管理

Temporal の UI では、作成済みのスケジュールを一覧表示し、過去の実行履歴を確認し、**一時停止・再開・手動トリガー**を行うことができます。

「このスケジュールが本当に動いているか」「前回はいつ実行されたか」「次回はいつか」を視覚的に確認できる管理インターフェースを、追加の開発なしに手に入れられます。本番運用では、モニタリングのコストを下げる点でも有用です。

### 使い分けの考え方

| ユースケース | 推奨 |
| --- | --- |
| 毎日・毎時など単純な定期実行 | Mastra 組み込み cron |
| タイムゾーン対応が必要 | Temporal スケジュール |
| カレンダーベースのルール（月末・第一月曜など） | Temporal スケジュール |
| UI でスケジュール一覧・履歴を確認したい | Temporal スケジュール |
| 長時間ワークフローの定期起動 | Temporal スケジュール |

---

## 4. Increased Observability — ワークフローの中を見る

可観測性は、開発段階でも本番運用でも欠かせない機能です。今回の記事では、Mastra 側と Temporal 側の可観測性が**補完し合う関係**として整理されていました。

### Mastra 側の観測機能

Mastra はすでに複数の観測機能を持っています。

#### スナップショットによるデバッグ

各ステップのスナップショットはデバッグにも使えます。「どのステップのどのデータが原因で失敗したか」を、スナップショットを遡ることで追えます。

#### Suspend / Resume

Mastra の Workflow は特定のステップで一時停止（Suspend）し、外部からの入力を受けてから再開（Resume）できます。「人間の承認待ち」を Workflow の中に組み込む際に使いますが、Suspend 中の状態も可観測性の文脈で重要です。「今どのワークフローがどのステップで止まっているか」を追える設計になっています。

#### Time Travel デバッグ

Mastra の Workflow には「time travel」と呼ばれるデバッグ機能があります。過去の実行履歴を追いながら、当時の入力データや出力データを確認できます。「本番でこの Workflow が失敗した3時間前の状態を再現したい」という場面で使えます。

#### Studio での個別テスト

Mastra Studio（開発・観測 UI）では、Workflow の個別実行をテストし、各ステップのトレースを探索できます。開発中のイテレーションや本番問題の切り分けで使いやすい UI が提供されています。

#### Mastra Observability（プラットフォーム機能）

2026年5月13日には、[Mastra Observability](https://mastra.ai/blog/announcing-mastra-observability) がプラットフォームの独立機能として発表されました。ClickHouse などの観測バックエンドを使って、エージェントやワークフローのトレースをスケールする形で収集・可視化するものです。今回の Feature 記事でも、この発表との連続性が明示されています。

> We know observability is a first-class feature. That's why we just announced Mastra's observability as a standalone part of Mastra's platform.

<https://zenn.dev/shiromizuj/articles/2202620087cd64>

### Temporal UI が追加する観測機能

Temporal を使うと、Temporal 自身の UI が新たな観測レイヤーとして加わります。

#### 実行履歴のクエリ

Temporal のワークフロー実行は、**完全な履歴イベント**として Temporal Server に保存されます。「このワークフローがいつどのステップで何ミリ秒かかったか」「どのリトライが何回起きたか」を Temporal UI 上で詳細にクエリできます。Mastra Studio がアプリケーションレベルのトレースを見るのに対し、Temporal UI は **Activity 単位の細粒度な履歴**を追う場面で補完的に機能します。

#### 属性によるワークフロー検索

Temporal は **Search Attributes** という機能を持っており、ワークフローに任意のキーバリューを付与してフィルタリングできます。「`customerID=12345` のワークフローだけを一覧表示する」「`status=TIMED_OUT` のワークフローを一覧に出す」といった検索が、コードを書かずに UI 上でできます。本番で特定顧客の処理状況を追うケースなど、運用場面で直接使いやすい機能です。

#### Worker と Queue のモニタリング

Temporal UI では、どの Worker が今何件のタスクを処理しているか、Task Queue にキューが詰まっていないかをリアルタイムで確認できます。スループットのボトルネック調査や Worker のスケールアウトのタイミングを判断する際に役立ちます。

### 2レイヤーの観測という設計

Mastra + Temporal の可観測性は、2つのレイヤーが補完する構成です。

```
Mastra Studio / Observability
  → ワークフロー全体のトレース、step の入出力、エージェント連携の観測
  → time travel デバッグ、suspend 中の状態確認

Temporal UI
  → Activity レベルの実行履歴、リトライ詳細
  → 属性によるワークフロー検索
  → Worker / Queue 状態のリアルタイム監視
```

大規模な分散ワークフローを本番で動かすとき、この2レイヤーが揃うと「どこで何が起きたか」の解像度が大幅に上がります。

---

## 5. 整理: Mastra が担う部分と Temporal が担う部分

今回の記事全体を通じて見えてきた構造を整理します。

| 機能 | Mastra 単体 | Temporal 統合後 |
| --- | --- | --- |
| **状態永続化** | プロセス内スナップショット | Temporal Server の分散ストレージ |
| **リトライ単位** | ステップ全体 | Activity 内の特定処理まで |
| **リトライ制御** | 回数・間隔・バックオフ・エラーフィルタ | + Jitter・時間制限・Server 管理 |
| **実行時間上限** | ステップの timeout 設定 | `startToCloseTimeout` で Activity 単位に設定 |
| **スケジューリング** | 組み込み cron | + タイムゾーン対応・カレンダー・UI 管理 |
| **可観測性** | Studio・Observability・time travel | + Temporal UI・実行履歴クエリ・Queue 監視 |
| **耐障害性** | プロセス再起動後の再開 | ネットワーク障害・DC 障害・Worker 再起動に耐える |

Mastra の API は薄く保ちつつ、必要な部分だけ Temporal の強みを取り込む、というレイヤリングの考え方がここから読み取れます。

公式記事はこう整理しています。

> At their core, Mastra workflows are best suited for application-level task sequences. For long-running distributed systems, an integration with Temporal provides a more comprehensive, durable workflow experience.

「アプリケーションレベルのタスク列は Mastra そのままで。長時間かつ分散した処理には Temporal を組み合わせる」という使い分けが推奨されています。

---

## 6. この夏にさらなるアップデートが来る

今回の記事には、さりげない予告が2か所含まれています。

1つ目：

> Mastra workflows are getting some major boosts this summer (stay tuned).  
> （Mastra のワークフローは今夏に大きなアップデートを控えています。お楽しみに）

2つ目：

> For long-running distributed systems, an integration with Temporal provides a more comprehensive, durable workflow experience (although we have exciting updates here coming very soon).  
> （長時間分散ワークフローには Temporal 統合が有効です。ただし、この領域にも近々 exciting なアップデートがあります）

`@mastra/temporal` が現時点で `experimental` 扱いである点と合わせると、今後の API 変更や機能拡充は十分あり得ます。

ここ数ヶ月の Mastra のリリースペースを振り返ると、Background Tasks（5月7日）、Temporal 統合（5月12日）、Mastra Observability（5月13日）と、ワークフローや長時間実行まわりを短い間隔で強化し続けています。「今夏の大きなアップデート」がどんな形で来るかは分かりませんが、ワークフローの実行基盤としての完成度がさらに上がる方向であることは確かそうです。

---

## まとめ

前回の記事で「Temporal が登場した」という発表を伝えたのに続き、今回の公式 Feature 記事では「何がどう強化されるのか」が4つの軸で整理されました。

| 軸 | 要点 |
| --- | --- |
| **Durable Workflows** | ステップごとのスナップショット + Temporal の分散耐障害性 |
| **Advanced Retries** | Activity レベルの粒度・Jitter・時間制限・Server 管理 |
| **Complex Scheduling** | タイムゾーン対応・カレンダーベース・UI 管理 |
| **Increased Observability** | Temporal UI の実行履歴クエリ・属性検索・Queue 監視 |

Mastra は「エージェントを作れるフレームワーク」から「長時間動く分散ワークフローを本番で安全に動かせる基盤」へと着実に進化しています。`@mastra/temporal` は現時点では experimental ですが、今夏の大きなアップデートへの布石として注目しておく価値があります。

---

## 参考リンク
