---
id: "2026-03-21-mastra-changelog-解説-2026-03-13-技術解説mastracore1130-01"
title: "[Mastra Changelog 解説] 2026-03-13 技術解説（@mastra/core@1.13.0）"
url: "https://zenn.dev/shiromizuj/articles/84073f6da4df6e"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-03-21"
date_collected: "2026-03-22"
summary_by: "auto-rss"
---

[Mastra](https://mastra.ai/) の[公式Blog](https://mastra.ai/blog)で発表された[Changelogs](https://mastra.ai/blog/category/changelogs)を速報ベースでお伝えします。ただの直訳ではなく、関連ドキュメントも参照したうえで手厚くしたり省略したりします。速報性重視でAIの力を多分に使っているので、私自身の考察は少なめです。

---

3月17日に、MastraのVer1.11、1.12、1.13のChangelogsがいっぺんにアップされました。ひとつずつ解説していきます。

2026-03-13 の Mastra リリース（`@mastra/core@1.13.0`）は、**可観測性（Observability）の基盤全体を再整備**した回です。スキーマの標準化、イベントのバッチング、型安全なサーバールート推論、エージェントの永続的ファイルストレージ、そしてObservational Memoryのコスト最適化と、影響範囲の広いアップデートが並んでいます。

今回の焦点は大きく 5 つです。

1. **Observability ストレージドメイン** — スコアからログ・フィードバック・メトリクスまで、すべての可観測性シグナルに統一されたスキーマと in-memory 実装が入った
2. **`@mastra/agentfs`：セッションをまたいで消えないエージェントのファイル置き場** — Turso/SQLite バックの永続的ワークスペースファイルシステム
3. **Observability パイプラインのアップグレード** — 型名の統一と `EventBuffer` によるバッチ処理
4. **型安全なサーバールート推論** — `@mastra/server/schemas` でルート定義から自動的に型を導出
5. **Observational Memory のトークンコスト削減** — 長期会話でのオブザーバーコンテキスト膨張問題に対処

---

## ハイライト1: Observability ストレージドメイン

### 「何が起きたか」を記録する場所がバラバラだった

AI エージェントシステムを本番で運用するとき、開発者が知りたいのは「エージェントは何をして、どんな結果を出して、どこで詰まったか」です。Mastra の可観測性レイヤーはスコア・ログ・フィードバック・メトリクス・ディスカバリーといった多様なシグナルを扱いますが、これまでそれぞれのシグナルのスキーマが「ゆるい型付け」のままで、パッケージ間で形状が微妙にずれていることがありました。

v1.13 でこれを根本から整理しました。**すべての可観測性シグナルに Zod ベースのスキーマ定義が入りました**。Zod は TypeScript でスキーマを書くためのライブラリです。`z.string()` や `z.number()` のような形でデータの型を宣言し、実行時に自動でバリデーションしてくれます。「ここには数値が来るはずなのに文字列が来ていた」というような問題を、コード実行の早い段階で検出できるようになります。

また、各シグナルに対して **in-memory の実装クラス**も追加されました。これは「データを何らかのストレージに書き込む」前段階として、メモリ上で完全に動作するデフォルト実装です。自前で Postgres や ClickHouse などのストレージバックエンドを実装するなら、`ObservabilityStorage` ベースクラスを継承するだけで、必要なメソッドだけをオーバーライドして残りはデフォルト実装に任せる形が取れます。

```
// 例: 自前のストレージバックエンドを実装するシンプルな構造
import { ObservabilityStorage } from '@mastra/core';

class MyClickHouseStorage extends ObservabilityStorage {
  // 必要なメソッドだけを上書きする
  // 未実装のメソッドはベースクラスのデフォルトが動く
  async saveScore(score: ScoreRecord) {
    await this.clickhouse.query('INSERT INTO scores ...', score);
  }
}
```

シグナルの種類ごとに形状がバラバラだったシステムを「カノニカルなスキーマ」に揃えることで、エクスポーター・クエリレイヤー・UI ツールはどれも同じ形を前提に作れるようになります。長期的に見ると、可観測性まわりのコードの「ドリフト」（実装間でじわじわ食い違いが生まれる現象）を抑制する重要な基盤整備です。（[PR #14214](https://github.com/mastra-ai/mastra/pull/14214)）

---

## ハイライト2: `@mastra/agentfs` — セッションをまたぐエージェントの「作業場」

### エージェントはなぜファイルを「覚えて」おきたいのか

AI エージェントが外部ツールを呼び出したり、コードを編集したり、調査結果をまとめたりするとき、その成果物はどこに残るでしょうか。多くの実装では「実行の終わりとともに消える」か、ホストプロセスのローカルファイルシステムに書き込むため、クラウド上で別のプロセスが実行されると前回の作業が参照できない、という問題があります。

v1.13 で新たにパッケージ化された `@mastra/agentfs` は、**Turso**（クラウドで動く SQLite サービス）と **agentfs-sdk** を使い、ファイルをデータベースに保存する `AgentFSFilesystem` プロバイダーを提供します。

```
import { Workspace } from '@mastra/core/workspace';
import { AgentFSFilesystem } from '@mastra/agentfs';

const workspace = new Workspace({
  filesystem: new AgentFSFilesystem({
    agentId: 'research-agent', // このエージェント専用のファイル名前空間
  }),
});
```

これにより実現できるシナリオが広がります。

* **複数回の実行をまたいでメモを蓄積するエージェント** — 第 1 回の調査結果を第 2 回が読み取れる
* **キャッシュを書き込むツール** — API の結果を DB に保存して次のリクエストで再利用
* **再起動後に再開できるマルチステップワークフロー** — 中断前の中間データが DB に残っている

エージェントが「長期間の作業者」として振る舞うためには、記憶だけでなく「作業場」が必要です。`@mastra/agentfs` はその永続的な作業場をクラウドネイティブに提供します。（[PR #13450](https://github.com/mastra-ai/mastra/pull/13450)）

---

## ハイライト3: Observability パイプラインのアップグレード — 型名の統一と EventBuffer

### 「同じものに別の名前がついている」問題

ソフトウェアが育つにつれ、同じ概念に異なる名前がシステムの各所につくことがあります。v1.13 では `@mastra/observability` パッケージ内のエクスポーターとイベントバスが、`@mastra/core` 側でリネームされた可観測性型の名前に追従しました。ユーザーは core とエクスポーターの間で「型名の脳内変換」をしなくて済むようになります。

### EventBuffer — 小さなイベントをまとめて送る

もう一つの追加が `EventBuffer` です。ログ・フィードバック・スコアといった非トレーシングシグナルは、1 件 1 件をリアルタイムに送信している場合、会話量が増えるにつれてネットワーク呼び出しの本数が膨らんでいきます。

`EventBuffer` はこれらのイベントを**設定したフラッシュ間隔で束ねてから送信**します。「少しだけ遅延させてもよいシグナル」を巧みにまとめることで、スループットが上がり、バックプレッシャー（書き込みより処理が遅くなってキューが詰まる問題）が起きにくくなります。

```
Before: ログ1件 → 送信 → ログ1件 → 送信 → ログ1件 → 送信 ...
After:  ログ1件 → バッファ → ログ2件 → バッファ → ログ3件 → 一括送信（100msごとなど）
```

高頻度にシグナルが発生するエージェントシステムでは、この差はかなり大きく効いてきます。（[PR #14214](https://github.com/mastra-ai/mastra/pull/14214)）

---

## ハイライト4: 型安全なサーバールート推論 — `@mastra/server/schemas`

### 「サーバーのルートと型が合っているか」を手動で確認していた

Mastra サーバーに fetch する独自のクライアントや SDK ラッパーを書くとき、特定の URL に送るべきリクエストボディの形や、レスポンスとして返ってくるオブジェクトの形を「ドキュメントを見ながら手書き」するパターンが多かったはずです。サーバー実装が変わっても型定義は自動では更新されないため、実際の挙動と型の間に「静かなズレ」が生まれやすくなります。

v1.13 で新しく加わった `@mastra/server/schemas` は、`SERVER_ROUTES` の定義から**リクエスト/レスポンスの型を自動で導出するユーティリティ型集**です。`createRoute()` で追加したカスタムルートも `RouteMap` に自動的に現れるため、別ファイルに型契約を手書きする必要がありません。

```
import type {
  RouteMap,
  InferPathParams,
  InferBody,
  InferResponse,
} from '@mastra/server/schemas';

// パスパラメーターを推論
type GetAgentParams = InferPathParams<RouteMap['GET /agents/:agentId']>;
// => { agentId: string }

// リクエストボディを推論
type GenerateBody = InferBody<RouteMap['POST /agents/:agentId/generate']>;
// => { messages: CoreMessage[], ... }

// レスポンス型を推論
type AgentResponse = InferResponse<RouteMap['GET /agents/:agentId']>;
// => { name: string, tools: ..., ... }
```

これが特に役立つ場面は「サーバーのルートをリファクタリングしたとき」です。クライアントコードは TypeScript のコンパイルエラーで壊れた箇所を即座に教えてもらえるため、「デプロイしたら動かなかった」という暗黙のズレを防げます。typed fetch ラッパーや内部 SDK を育てているチームにとっては、かなりの工数削減になるはずです。（[PR #14008](https://github.com/mastra-ai/mastra/pull/14008)）

---

## ハイライト5: Observational Memory のトークンコスト削減

### "記憶"が増えるほど"思い出す"コストも増える問題

Observational Memory は Mastra のメモリ機能のひとつで、長い会話の流れを「オブザーバー」が要約・蓄積することで、エージェントに文脈を渡す仕組みです。しかし会話が長くなるにつれて「Previous Observations（過去の観察）」セクションが膨らみ、プロンプト全体のトークン消費が増加し続けるという課題がありました。

v1.13 で追加された `observation.previousObserverTokens` は、このセクションに**トークン予算の上限**を設けるオプションです。

```
const memory = new Memory({
  options: {
    observationalMemory: {
      model: 'google/gemini-2.5-flash',
      observation: {
        // 過去の観察を最大 10,000 トークン分だけ保持する
        // デフォルトは 2,000 トークン
        previousObserverTokens: 10_000,
      },
    },
  },
});
```

上限を設けたとき、Mastra は単純に古い観察を削除するわけではありません。**すでにバッファに反映済みの観察は要約サマリーに置き換え**、最新の観察を保持し続けます。「記憶の圧縮」を自動で行うことで、オブザーバーの精度を保ちながらコストだけを抑えられます。

| オプション値 | 挙動 |
| --- | --- |
| 数値（例: `10_000`） | 指定トークン以内に過去の観察を収める（デフォルト: `2000`） |
| `0` | 過去の観察をプロンプトに含めない |
| `false` | 切り詰めなし（全履歴を保持） |

長期的な会話を前提とするエージェント（カスタマーサポート、継続的なコーディングアシスタントなど）では、このスライダー一つでランニングコストが数割変わってくることもあります。（[PR #13568](https://github.com/mastra-ai/mastra/pull/13568)）

---

## その他の注目アップデート

### プロバイダーツールがカスタムゲートウェイを通っても消えなくなった

`openai.tools.webSearch()` のような AI プロバイダーが提供するビルトインツールを使いつつ、カスタムゲートウェイ（Portkey、LiteLLM など、複数のモデル API を束ねるプロキシ）を経由して呼び出す構成では、ゲートウェイが AI SDK v6（V3）形式のレスポンスを返すとツール定義が静かに消える問題がありました。調べてみると、ツールの "type" フィールドが `"provider-defined"` のままだとルーターが落としてしまう実装になっていたためです。

v1.13 のフィックスでは、V3 モデルへのデリゲート時に `provider-defined` を `provider` に変換するリマップ処理が入りました（[PR #13895](https://github.com/mastra-ai/mastra/pull/13895)）。カスタムゲートウェイ越しにプロバイダーツールを使っていた方には、設定変更なしで問題が解消されます。

### スレッドメタデータが途中で消えなくなった

`MASTRA_THREAD_ID_KEY` をリクエストコンテキストにセットしている環境で、`options.memory.thread` に渡したスレッドのタイトルやカスタムプロパティが無視されてしまう問題が修正されました（[PR #13146](https://github.com/mastra-ai/mastra/pull/13146)）。スレッド ID はコンテキストの値が引き続き優先されますが、それ以外のメタデータは正しく保持されるようになりました。

### ワークスペースツールが一部の実行パスで動かない問題

`mastra_workspace_list_files` や `mastra_workspace_read_file` が特定の実行パスで `WorkspaceNotAvailableError` を投げてしまう問題も解消されました（[PR #14228](https://github.com/mastra-ai/mastra/pull/14228)）。ワークスペースツールに依存している方は何も変えなくても恩恵を受けられます。

### esbuild のセキュリティアップデート

デプロイヤーが使用する esbuild が `^0.27.3` にバンプされました。Go の標準ライブラリに起因する CVE-2025-22871 と CVE-2025-61729 のアドバイザリに対処したものです（[PR #13124](https://github.com/mastra-ai/mastra/pull/13124)）。依存パッケージのセキュリティ問題を `npm audit` で検知していたプロジェクトでは、警告が解消されるはずです。

### バンドラーの `dynamicPackages` 設定

静的解析では検出できない、実行時に動的にロードされるパッケージを `bundler.dynamicPackages` に明示できるようになりました（[PR #11779](https://github.com/mastra-ai/mastra/pull/11779)）。

```
export const mastra = new Mastra({
  bundler: {
    // pino の transport や独自プラグインなど、動的ロードされるパッケージを列挙
    dynamicPackages: ['pino-opentelemetry-transport', 'my-custom-plugin'],
  },
});
```

なお pino のトランスポートターゲットについては、バンドラーが自動検出に対応したため、多くのケースでは設定不要です。

### Studio: Observabilityタブでスレッドごとのグループ化

Mastra Studio（ローカル開発 UI）の Observability タブで、トレースをスレッド ID でグループ化できるようになりました（[PR #14112](https://github.com/mastra-ai/mastra/pull/14112)）。マルチターンの会話ログを追うとき、複数回のターンが一つのスレッドとしてまとまって見えるようになるため、「どの会話でエージェントが詰まったか」をたどる手間が大幅に減ります。

### Studio: Prettier のレイジーロード

Studio がページロード時に Prettier コードフォーマッターを読み込んでいた部分が、フォーマットが実際にトリガーされるまで遅延されるようになりました。バンドルサイズが削減され、初回表示が速くなります（[PR #13934](https://github.com/mastra-ai/mastra/pull/13934)）。

---

## 破壊的変更

### MetricType が deprecated に（`@mastra/observability@1.5.0` 以降）

`counter` / `gauge` / `histogram` などの `MetricType` 値が deprecated になりました。メトリクスは「書き込み時に集計の意味論を持つ型付きイベント」ではなく「生のイベント」として扱い、集計はクエリ時に行う設計に移行します。

**マイグレーション**: `MetricType` に依存していたコードは、集計ロジックをデータの読み取り・クエリ時に移動してください。

### Score スキーマの `scorerName` → `scorerId`

スコアリングオブジェクトの識別子フィールドが `scorerName` から `scorerId` にリネームされました。

```
// Before
const score = {
  scorerName: 'toxicity-v1',
  // ...
};

// After
const score = {
  scorerId: 'toxicity-v1',
  // ...
};
```

フィルタリングや DB の JOIN、UI ラベルなど `scorerName` を使っている箇所を `scorerId` に更新してください。

### `ObservabilityBus` のコンストラクター変更

`ObservabilityBus` の設定方法がインスタンスメソッドから**コンストラクター引数**に変わりました。

```
// Before（概念的なコード）
const bus = new ObservabilityBus();
bus.setCardinalityFilter(myFilter);    // メソッドが削除
bus.enableAutoExtractedMetrics();       // メソッドが削除

// After
const bus = new ObservabilityBus({
  cardinalityFilter: myFilter,
  autoExtractMetrics: true,
});
```

`setCardinalityFilter()` と `enableAutoExtractedMetrics()` は削除されました。設定はすべてコンストラクターに渡してください。

---

## バージョン要件

```
@mastra/core@1.13.0
@mastra/memory@1.8.0
@mastra/observability@1.5.0
@mastra/agentfs@0.1.0（新規）
@mastra/server@1.13.0
@mastra/schema-compat@1.2.2
@mastra/deployer@1.13.0
```

自動コードモッドを使えば大半の破壊的変更を一括で修正できます。

```
npx @mastra/codemod@latest v1
```

詳細は[マイグレーションガイド](https://mastra.ai/guides/migrations/upgrade-to-v1/overview)を参照してください。
