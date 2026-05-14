---
id: "2026-05-13-mastra-announce-temporal-workflows-登場-長時間ワークフローを壊れ-01"
title: "[Mastra Announce] Temporal Workflows 登場 - 長時間ワークフローを壊れにくく実行"
url: "https://zenn.dev/shiromizuj/articles/4c812b32c421c0"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "LLM", "TypeScript", "zenn"]
date_published: "2026-05-13"
date_collected: "2026-05-14"
summary_by: "auto-rss"
query: ""
---

[Mastra](https://mastra.ai/) の[公式Blog](https://mastra.ai/blog)で発表された[Announcements](https://mastra.ai/blog/category/announcements)を速報ベースでお伝えします。ただの直訳ではなく、周辺情報も補いながら、なるべく「なぜこの機能が必要なのか」まで分かるように整理します。速報性重視のため一部は公開情報ベースの解釈を含みますが、事実と推測は分けて書きます。

[Mastra Announcements 速報解説一覧](https://zenn.dev/shiromizuj/articles/cc91bb06db5b5b)

---

## Mastra が Temporal Workflows 対応を発表

2026年5月12日、Mastra は **Temporal Support for Mastra Workflows** を発表しました。

アナウンス冒頭をざっくり訳すと、次のような内容です。

> Mastra のワークフローを Temporal 上で実行できるようになり、耐障害性のある durable execution、自動リトライ、長時間実行、スケジューリング、永続状態管理が使えるようになりました。

要するに、**Mastra の `createWorkflow()` / `createStep()` で書いたワークフローを、ほぼ同じ開発体験のまま Temporal の実行基盤に載せられるようになった**、という発表です。

これは単なるデプロイ先の追加ではありません。Mastra の Workflow 機能に、「**何時間も、場合によっては何日もかかる処理を、途中でプロセスが落ちても継続しやすくする仕組み**」が加わった意味があります。

---

## 前提の解説

この発表は、5月上旬のロードマップ解説記事でも予告されていました。そこでは「InngestはすでにサポートされていてTemporalも多くのリクエストがあったため対応」と述べられていました、このあたりの前提を整理しておきます。

<https://zenn.dev/shiromizuj/articles/f8ed4ed72c414b>

### そもそも Temporal とは何か

Temporal は、**分散システムでのワークフローを管理するためのオープンソースのワークフローエンジン**です。もう少し噛み砕くと、複数のサービスや API、データベース、人間承認などをまたぐ「長い処理の流れ」を、途中で失敗しても継続・再試行しやすい形で動かすための基盤です。

開発元は **Temporal Technologies** で、OSS の Temporal Server を公開すると同時に、マネージド版の **Temporal Cloud** も提供しています。つまり Temporal は「製品名」であると同時に、**オープンソース版とクラウド版の両方を持つ workflow platform** と考えると理解しやすいです。

普通のアプリケーションコードでもワークフローは書けますが、実運用では次のような問題がすぐ出ます。

* 途中の API 呼び出しが失敗したときに、どこから再開するか
* 数時間後、数日後の処理再開をどう管理するか
* Worker やサーバーが再起動したあとも状態をどう保持するか
* 並列実行、タイムアウト、リトライをどう安全に扱うか

Temporal は、こうした面倒な部分を基盤側で引き受けてくれるのが強みです。だから、EC の注文処理、請求処理、データパイプライン、長時間の AI ジョブのように、「**1回の HTTP リクエストでは終わらない処理**」と特に相性が良いわけです。

アーキテクチャをかなり大づかみに言うと、Temporal は次のように分かれます。

* **Temporal Service / Temporal Server**: ワークフローの履歴、可変状態、タスクキュー、タイマーなどを管理する中核サービス
* **永続化ストア**: Temporal Service が状態を保持するためのデータベース群。少なくとも RDB や Cassandra などの永続層を背後に持つ
* **アプリケーション側の SDK**: 開発者が自分のアプリに組み込み、Workflow や Activity のコードを書くための SDK
* **Worker**: SDK を使って自作した実行プロセス。Task Queue をポーリングし、実際のタスク処理を担う

ここが少し重要です。Temporal を導入しても、業務ロジックそのものを Temporal が勝手に実装してくれるわけではありません。**ワークフローを開始するアプリケーションも、各タスクを実際に処理する Worker も、SDK を使って自分たちで作る**のが基本です。Temporal Server は、その背後で状態管理、履歴管理、再試行、タイマー、タスク配送を担います。

Temporal Server 自体も内部では単一プロセスではなく、たとえば公式ドキュメントでは次の4サービスで説明されています。

* **Frontend**: クライアントや Worker からのリクエスト受付、認可、ルーティング
* **History**: Workflow の履歴や mutable state の保持
* **Matching**: Task Queue の管理と Worker へのディスパッチ
* **Worker Service**: Temporal 自身の内部ワークフローやバックグラウンド処理

そのため、「Temporal を使う」と言ったときに実際にやっていることは、**状態管理サーバと永続化層を持つ専用基盤を別に立て、その上に自分たちの Workflow 実装と Worker 実装を載せる**、という構成に近いです。

提供形態も2通りあります。

* **セルフホスト**: OSS の Temporal Server を自前のインフラで運用する
* **Temporal Cloud**: Temporal Technologies が運用するマネージドサービスを使う

Temporal Cloud でも、アプリケーションコードや Worker コードは自分たちの環境で動かすのが基本です。クラウド側に任せるのは主に Temporal Service の運用部分であり、SDK で書いた Workflow や Activity の実行プロセスまで丸ごと預けるわけではありません。この点は「単なる SaaS」ではなく、**実行基盤だけをマネージド化したサービス**と捉えると分かりやすいと思います。

### Inngest とは何か

**Inngest** もまた、イベント駆動や長時間ジョブに強いワークフロー基盤です。開発者は TypeScript などで処理フローを書き、イベントをきっかけに関数やステップを実行できます。時間待ち、再試行、ステップ管理、スケジュール実行といった機能を持っており、こちらも「壊れにくいバックグラウンド処理」を作るための選択肢として知られています。

Temporal と Inngest は細かな設計思想や運用モデルこそ違いますが、Mastra の文脈ではひとまず **「Workflow の実行基盤」** という理解で十分です。つまり、Mastra の Workflow をどこで安定実行させるか、という観点で並べて語られる存在です。

### なぜ「Inngest の次に Temporal なのか」

ロードマップ記事で触れた通り、Mastra はすでに Inngest を Workflow の実行先としてサポートしていました。そのうえで、コミュニティやユーザーから **Temporal 対応の要望が多かった** ため、今回の発表につながったと見られます。

この流れは自然です。Temporal は、分散システムや業務システムの文脈で durable execution の代表格として広く認知されており、すでに社内導入している企業も少なくありません。そうした環境では、Mastra の Workflow も既存の Temporal 運用に乗せたい、という需要が出てきます。

言い換えると今回の発表は、Mastra が独自の Workflow API を持ちながらも、**実行基盤は一つに固定せず、現場でよく使われる durable workflow engine に接続していく**方向を示したものとも言えます。

---

## 背景: 普通のワークフロー実行では何がつらいのか

Mastra の Workflow は、複数のステップを順番に、あるいは条件分岐や並列化を交えながら実行する仕組みです。たとえば次のような処理に向いています。

* 外部 API からデータ収集
* 収集結果の整形
* LLM で要約や分類
* 結果を別システムへ保存
* 必要なら人間の確認待ち

Mastra の Workflow に関する解説記事はこちらを参照ください。  
<https://zenn.dev/shiromizuj/articles/1ab564dea7e488>  
<https://zenn.dev/shiromizuj/articles/c1873a589354b8>

こうした処理は、短時間で終わるとは限りません。実務では次のような事情がよくあります。

* 外部 API が遅い、あるいは一時的に失敗する
* レートリミットの都合で待ち時間が発生する
* 夜間バッチのように数時間単位で走らせたい
* 人間承認や別システムの完了待ちで長時間止まる
* 実行中に Worker やサーバーが再起動する

通常の Node.js プロセスの中だけでこうしたワークフローを回すと、**プロセスが落ちた瞬間に途中経過ごと失われやすい**という問題があります。自前で再試行、状態保存、再開処理を書くこともできますが、かなり面倒です。

そこで使われる代表的な基盤が **Temporal** です。

---

## Mastra では Temporal をどう使うのか

Temporal 自体の基本像は上記で触れたので、ここでは **Mastra とのつながり方** に絞ります。

今回の統合で Mastra は、Workflow API の見た目をあまり変えずに、Temporal の durable execution を利用できるようにしました。Mastra のドキュメントでは、**各 `createStep()` は Temporal Activity に、各 `createWorkflow()` は Temporal Workflow に変換される**と説明されています。

つまり開発者は、Mastra の Workflow を書く体験を大きく崩さずに、裏側の実行基盤だけを Temporal に差し替えられる、というわけです。

---

## 何が追加されたのか

今回の Temporal 統合では、Mastra の標準的な Workflow API を保ったまま、実行基盤だけを Temporal に寄せられるようになりました。

アナウンスと公式ガイドをまとめると、全体像は次の通りです。

1. Temporal クライアントに紐づいた `createWorkflow()` と `createStep()` を用意する
2. 既存の Workflow 定義で、その関数を import するよう差し替える
3. Temporal の Task Queue を監視する Worker プロセスを別途立ち上げる

Mastra のドキュメントでは、**各 `createStep()` は Temporal Activity に変換され、各 `createWorkflow()` は Temporal Workflow に変換される**と説明されています。つまり、Mastra 側の抽象と Temporal 側の抽象がかなり素直に対応しています。

イメージするとこんな構成です。

```
アプリケーション
  ↓
Mastra Workflow API
  ↓
@mastra/temporal
  ↓
Temporal Workflow / Activity
  ↓
Temporal Worker + Task Queue + 永続状態
```

重要なのは、**Workflow の書き方を全面的に書き換えるわけではない**ことです。既存の Mastra 利用者にとっては、API を大きく変えずに durable execution を取り込みやすい形になっています。

---

## 使い始め方

必要なパッケージは次の通りです。

```
npm install @mastra/temporal @temporalio/client @temporalio/worker @temporalio/envconfig
```

公式アナウンスでは、**`@mastra/core@1.32.0` 以降が必要**とされています。なお、`@mastra/temporal` は現時点で experimental 扱いです。つまり便利そうでも、API は今後変わる可能性があります。

### 1. Temporal クライアントを初期化する

まず、Mastra 用にバインドされた `createWorkflow` と `createStep` を作ります。

```
import { init } from "@mastra/temporal";
import { Client, Connection } from "@temporalio/client";
import { loadClientConnectConfig } from "@temporalio/envconfig";

const config = loadClientConnectConfig();
const connection = await Connection.connect(config.connectionOptions);
const client = new Client({ connection });

export const { createWorkflow, createStep } = init({
  client,
  taskQueue: "mastra",
});
```

ここでのポイントは、**Mastra の Workflow 定義が特定の Temporal Task Queue に結びつく**ことです。後で Worker 側も同じ `taskQueue` を監視する必要があります。

### 2. Workflow 定義の import を差し替える

Workflow の中身そのものは大きく変えず、`createWorkflow` と `createStep` の import 元を Temporal 初期化モジュールへ差し替えます。

```
import { createWorkflow, createStep } from "../temporal";
```

この作りはかなり実用的です。既存の Workflow コードの差分を小さくできるので、まず通常実行で開発し、必要になったワークフローだけ Temporal 化する、といった移行もやりやすいはずです。

### 3. Worker を常駐させる

Temporal 版 Workflow では、Worker は非常に重要です。Mastra のガイドでは、`MastraPlugin` を使って Workflow と Step を自動登録する構成が案内されています。

```
import { MastraPlugin } from "@mastra/temporal/worker";
import { NativeConnection, Worker } from "@temporalio/worker";

const connection = await NativeConnection.connect({
  address: "localhost:7233",
});

const mastraPlugin = new MastraPlugin();

await mastraPlugin.prebuild({
  entryFile: import.meta.resolve("./index.ts"),
});

const worker = await Worker.create({
  connection,
  namespace: "default",
  taskQueue: "mastra",
  plugins: [mastraPlugin],
});

await worker.run();
```

ここで重要なのは、**Worker は長寿命プロセスとして常駐させる必要がある**ということです。公式ガイドでも、短時間で終了するサーバーレス環境には向かず、コンテナ、VM、Kubernetes、Fly.io、Railway のような常駐しやすい実行基盤が推奨されています。

---

## この機能がうれしいユースケース

Temporal 統合が特に効くのは、以下のようなケースです。

### 1. 外部 API をまたぐ長時間処理

複数の SaaS や社内 API を順次たたくワークフローでは、どこか一箇所が不安定なだけで全体が崩れがちです。Temporal を使うと、ステップごとのリトライや状態継続の仕組みを持ち込みやすくなります。

### 2. 人間確認を挟む処理

たとえば「下書き作成 → 承認待ち → 本送信」のような業務フローは、数分で終わるとは限りません。人間が翌日承認しても処理を再開できる設計は、Temporal が本来得意とする領域です。

### 3. 数時間から数日動くエージェント処理

Mastra は最近、Background Tasks や Durable Agents など、長く動くエージェント実行基盤に力を入れています。Workflow 側も Temporal を使えるようになったことで、**「会話型エージェント」だけでなく「長時間の手続き的処理」も壊れにくくする**方向がさらに明確になりました。

### 4. スケジュール実行や定期バッチ

アナウンスでも scheduling が明示されています。日次集計、週次レポート、夜間の再処理など、定期ジョブを Workflow として組みたい場面と相性が良いでしょう。

---

## Mastra の最近の流れの中で見ると分かりやすい

この発表は突然出てきたわけではありません。5月4日の Mastra ロードマップウェビナーでも、**Temporal Workflows 対応は数週間以内に出す予定**と予告されていました。そこでは、すでに Inngest 対応があり、Temporal を求める声も多かったため開発を進めていると説明されています。

ここ数ヶ月の Mastra は、次の方向を強めています。

* Background Tasks
* Durable Agents
* Workspaces / Remote Filesystems / Remote Sandboxes
* Browser 操作のような長めのエージェント実行

これらに共通するのは、「**AI エージェントを単発の推論ではなく、現実の業務フローの中で長く安全に動かしたい**」という発想です。Temporal Workflows は、そのうち特に「手続き型でステップが明確な処理」を支えるピースだと考えると理解しやすいです。

---

## 注意点と制約

便利そうな一方で、現時点ではいくつか注意点があります。

* `@mastra/temporal` は **experimental**。本番採用前に API 変更リスクを見ておきたい
* Temporal クラスタが必要。ローカルでも Docker などで用意する必要がある
* Worker は常駐プロセス前提。短命サーバーレスには向かない
* Workflow の `id` は **静的な文字列リテラル** が必要。ビルド時変換の都合による制約

特に最後の `id` 制約は見落としやすいです。通常の Mastra Workflow では気にしない書き方をしていても、Temporal 向けビルドでは変換のために静的解析しやすい形が求められます。

---

## どんな人が使うべきか

逆に言うと、すべての Workflow を Temporal に乗せる必要はありません。数秒で終わる簡単な処理なら、通常の Mastra Workflow のままで十分なことも多いです。

導入を真剣に検討すべきなのは、次のようなチームです。

* エージェントやワークフローが数分以上動く
* 外部 API 障害を前提に自動再試行したい
* サーバー再起動で実行が消えるのを避けたい
* バッチや承認フローを Mastra で統一したい
* すでに社内で Temporal を使っている

特に「AI エージェントの前後にある業務処理」まで一続きで設計したい場合、Temporal はかなり自然な選択肢です。単に LLM を呼ぶだけでなく、その前後の待機・再試行・定期実行・人的承認まで含めて一つの Workflow として運用しやすくなるからです。

---

## まとめ

Mastra の Temporal Workflows 対応は、Workflow API の見た目を大きく変えずに、**durable execution と fault-tolerant execution を持ち込める**のが最大の価値です。

Mastra はもともと「エージェントを作りやすい」だけでなく、「実運用できる形に持っていく」方向へどんどん広がっています。Temporal 統合は、その流れの中でもかなり重要な一手です。長時間動くエージェントや業務フローを本気で扱うなら、今後の Mastra ではかなり注目度の高い機能になるはずです。

---

## 参考リンク
