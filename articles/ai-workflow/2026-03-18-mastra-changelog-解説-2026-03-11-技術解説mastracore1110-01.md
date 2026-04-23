---
id: "2026-03-18-mastra-changelog-解説-2026-03-11-技術解説mastracore1110-01"
title: "[Mastra Changelog 解説] 2026-03-11 技術解説（@mastra/core@1.11.0）"
url: "https://zenn.dev/shiromizuj/articles/091663e8962c5d"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-03-18"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

[Mastra](https://mastra.ai/) の[公式Blog](https://mastra.ai/blog)で発表された[Changelogs](https://mastra.ai/blog/category/changelogs)を速報ベースでお伝えします。ただの直訳ではなく、関連ドキュメントも参照したうえで手厚くしたり省略したりします。速報性重視でAIの力を多分に使っているので、私自身の考察は少なめです。

---

3月17日に、MastraのVer1.11、1.12、1.13のChangelogsがいっぺんにアップされました。ひとつずつ解説していきます。

2026-03-11 の Mastra リリース（`@mastra/core@1.11.0`）は、**モデルルーティングの表現力向上**、**スキーマ互換レイヤーの整備**、**RequestContext の全面貫通**、そして**ストレージ性能のドラスティックな改善**を軸としたアップデートです。

今回の焦点は大きく 5 つです。

1. **ダイナミックモデルフォールバック配列** — ランタイムで切り替わるモデルリストを一つの Agent 定義に収める
2. **Standard Schema + Zod v4 対応** — Zod v3/v4・AI SDK・JSON Schema を統一された変換パスで扱う
3. **バリデーションエラーのカスタマイズ** — 全サーバーアダプター横断で 400 を超えるエラーレスポンス設計
4. **RequestContext のエンドツーエンド貫通** — トレーシング・データセット・実験評価まで一本のスコープが通る
5. **ストレージ全面パフォーマンス改善** — 7,000 件スレッドを 30 秒 → 500ms に

---

## ハイライト1: ダイナミックモデルフォールバック配列（ランタイムルーティング）

### 問題の構造

AIエージェントをプロダクション運用していると、「全ユーザーに同じモデルを使う」という設計はすぐに限界を迎えます。課金プランによって使えるモデルを変えたい。地域規制で EU トラフィックは EU エンドポイントに向けたい。エンタープライズ顧客にはリトライ予算を厚く配分したい—— こういったニーズは「コードでエージェントを何パターンも書き分ける」か「実行時に動的に切り替える独自ルーティング機構を構築する」かという二択を強いていました。

Mastra 1.10 まではフォールバック配列を静的に記述するか、動的関数で「単一のモデル」を返すことはできました。しかし「動的関数でフォールバック配列ごとを返す」——これが v1.11 で実現した部分です。

### フォールバック配列を返す

最もシンプルなユースケースは **tier（ティア）ベースのルーティング**です。tier とはサービスの料金プランや会員ランクのことで、「Free・Premium・Enterprise」のような区分を指します。AI サービスを作る場合、有料プランのユーザーには高性能なモデルを、無料プランのユーザーには安価なモデルを使うといった設計が典型です。

「ルーティング」は「振り分け」を意味します。リクエストが来たとき、そのユーザーの tier 情報を見て「どのモデルに処理を任せるか」をその場で決める——これが tier ベースのルーティングです。

```
const agent = new Agent({
  model: ({ requestContext }) => {
    // requestContext にはリクエスト側から渡されたメタデータが入っている
    // たとえば「このユーザーは premium プランか」という情報
    const tier = requestContext.get('tier');

    if (tier === 'premium') {
      // Premium ユーザー: まず GPT-4 を試し、失敗したら Claude にフォールバック
      // maxRetries はそのモデルへの最大リトライ回数
      return [
        { model: 'openai/gpt-4', maxRetries: 2 },
        { model: 'anthropic/claude-3-opus', maxRetries: 1 },
      ];
    }

    // Free ユーザー: 安価なモデルのみ
    return [{ model: 'openai/gpt-3.5-turbo', maxRetries: 1 }];
  },
});
```

エージェント定義はこれ一つ。「Premium ユーザーかどうか」の判断はリクエストが届いた瞬間（ランタイム）に行われます。プランごとにエージェントを書き分ける必要も、外部でルーティングロジックを管理する必要もありません。

### ネストした動的関数

フォールバック配列の各要素を、さらに別の動的関数にすることもできます。「フォールバック配列を返す関数」の中に「モデルを選ぶ関数」が入れ子になる構造です。

これが役立つのは、判断の軸が二段階あるケースです。たとえば「第一候補のモデルはリージョンによって EU 版か通常版かを切り替えたい。ただし第一候補が落ちた場合のフォールバックは常に Claude で固定したい」——そういった要件を一つのエージェント定義に収められます。

```
const agent = new Agent({
  model: ({ requestContext }) => {
    // 第一段階：リクエストのリージョンを取得
    // EU からのアクセスは EU データセンターのエンドポイントに向ける必要がある
    const region = requestContext.get('region');

    return [
      {
        // 第二段階：第一候補のモデル自体も動的に決まる（入れ子の動的関数）
        // region が 'eu' なら EU エンドポイントの GPT-4、それ以外は通常の GPT-4
        model: ({ requestContext }) => {
          return region === 'eu' ? 'openai/gpt-4-eu' : 'openai/gpt-4';
        },
        maxRetries: 2, // この第一候補モデルは最大2回リトライ
      },
      // 第一候補が全リトライを使い切って失敗したら Claude にフォールバック
      // こちらはリージョンに関係なく常に同じモデルでよい
      { model: 'anthropic/claude-3-opus', maxRetries: 1 },
    ];
  },
  maxRetries: 1, // maxRetries を指定していないモデルはこのエージェントレベルの値を継承
});
```

### 非同期もサポート

tier の判別には「リクエストに含まれるメタデータを参照するだけ」で済むケースもありますが、実際のサービスでは「ユーザー ID でデータベースを引いてプランを確かめる」「フィーチャーフラグサービスに問い合わせて機能 ON/OFF を判定する」といった非同期処理が必要になることがほとんどです。

model 関数を `async` にするだけで対応できます。

```
const agent = new Agent({
  // async にすれば、関数の中で await が使える
  model: async ({ requestContext }) => {
    // requestContext から識別子だけ取り出す
    // DB のフル情報は requestContext に持たせず、ここで問い合わせる設計
    const userId = requestContext.get('userId');

    // DB を非同期で参照してユーザーのプランを確認
    // この await の間、エージェントは次の処理に進まず結果を待つ
    const user = await db.users.findById(userId);

    if (user.tier === 'enterprise') {
      // Enterprise ユーザー: 最も高性能なモデルを第一候補にし、
      // リトライ予算も厚めに確保する
      return [
        { model: 'openai/gpt-4', maxRetries: 3 },
        { model: 'anthropic/claude-3-opus', maxRetries: 2 },
      ];
    }

    // それ以外のプランは安価なモデルのみ
    return [{ model: 'openai/gpt-3.5-turbo', maxRetries: 1 }];
  },
});
```

DB 問い合わせを model 関数の中に書くのは責務の混在に見えるかもしれませんが、「どのモデルを使うか」の判断材料をすべてここに集約できる点で読みやすさには優れています。パフォーマンスが気になる場合は、`requestContext` を経由してリクエストスコープのキャッシュ済みユーザー情報を渡す設計にするのが実務的なアプローチです。

### 内部実装のポイント

| 仕様 | 動作 |
| --- | --- |
| 空配列を返した場合 | 早期にエラーをスロー（世代処理まで到達させない） |
| `maxRetries` 未指定のモデル | エージェントレベルの `maxRetries` を自動継承 |
| すでに正規化済みの静的配列 | 再正規化をスキップするパフォーマンス最適化 |
| 既存コードとの互換性 | 静的単一・静的配列・動的単一はすべて従来通り動作 |

この変更は **後方互換です**。既存の設定は何も変えなくて構いません。（[PR #11975](https://github.com/mastra-ai/mastra/pull/11975)）

---

## ハイライト2: Standard Schema + Zod v4 互換レイヤー

### スキーマの「方言問題」

Mastra のようなフレームワークには、ツール定義・構造化出力・エージェントネットワークなど、さまざまな入口からスキーマが渡ってきます。開発者が Zod v3 で書いたもの、Zod v4 で書いたもの、Vercel の AI SDK 形式、生の JSON Schema——と形式は一様ではありません。

問題はこれらをそのまま AI モデルの API（OpenAI・Anthropic・Google など）に渡す場面で起きます。たとえば Anthropic の API には通るスキーマが、OpenAI の strict mode（スキーマの記述ルールを厳格に検査するモード）では弾かれる、ということが起こります。つまり「スキーマの書き方の方言が複数あり、どの方言が各プロバイダーに通じるか」が一致しないことが問題の本質でした。

特に OpenAI の strict mode では、optional フィールドや default 付きフィールドが `required` 配列に入っていないと弾かれます。Zod v3 と v4 の間でも `z.record()` の引数形式が変わり、`ZodError.errors` が `ZodError.issues` に変わりました。

### 統一変換パス

Mastra v1.11 では `@mastra/schema-compat` を導入し、二つの変換関数を中心に整理します。

* **`toStandardSchema(schema)`** — Zod v3・Zod v4・AI SDK Schema・JSON Schema を受け取り、内部標準表現に変換する
* **`standardSchemaToJSONSchema(schema)`** — 標準表現から JSON Schema に変換する（strict mode プロバイダーとの互換性を保ちながら）

コア側では `PublicSchema` 型に統一し、ツール定義・構造化出力・エージェントネットワーク等すべての入口でこのパスを経由するようになりました。

### 破壊的変更: Zod 最小バージョンの引き上げ

Zod v4 対応に伴い、**Zod の最小バージョンが引き上げられます**。

| 利用パターン | 必要バージョン |
| --- | --- |
| Zod v3 のまま使う | `^3.25.0` 以上 |
| Zod v4 に移行する | `^4.0.0` 以上 |

v4 に移行する場合、コードベースの修正箇所は主に以下の 2 点です。

```
// Before: z.record() は v3 では 1 引数 OK
const schema = z.record(z.string());

// After: v4 では key schema + value schema の 2 引数必須
const schema = z.record(z.string(), z.string());
```

```
// Before: v3 では ZodError.errors
catch (err) {
  if (err instanceof z.ZodError) console.log(err.errors);
}

// After: v4 では ZodError.issues
catch (err) {
  if (err instanceof z.ZodError) console.log(err.issues);
}
```

ほとんどの破壊的変更には自動コードモッドが用意されています。

```
npx @mastra/codemod@latest v1
```

（[PR #12238](https://github.com/mastra-ai/mastra/pull/12238)）

---

## ハイライト3: バリデーションエラーのカスタマイズ（全サーバーアダプター対応）

### デフォルト 400 の問題

Mastra サーバーが Zod のバリデーションエラーを返すとき、デフォルトはシンプルな HTTP 400 です。内部サービス同士なら十分ですが、外部公開 API では「どのフィールドが何の理由で失敗したか」を構造化して返したい、ステータスコードを 422 にしたい、APIゲートウェイのレスポンスエンベロープに合わせたい——という要件がほぼ必ず出てきます。

### `onValidationError` フック

`ServerConfig` にグローバルフックを設定するか、`createRoute()` にルート個別のフックを渡すかの 2 パターンで制御できます。

```
const mastra = new Mastra({
  server: {
    onValidationError: (error, context) => ({
      status: 422,
      body: {
        ok: false,
        errors: error.issues.map(i => ({
          path: i.path.join('.'),
          message: i.message,
        })),
        // context には 'query' | 'params' | 'body' のどこで落ちたかが入る
        source: context,
      },
    }),
  },
});
```

ポイントは `context` に「クエリパラメータ・パスパラメータ・リクエストボディのどこでバリデーションが失敗したか」が含まれる点です。フロントエンド側でエラーハイライトするフィールドを決定するのに役立ちます。

このフックは **Hono・Express・Fastify・Koa の全アダプター**で同じ設定が効きます。（[PR #13477](https://github.com/mastra-ai/mastra/pull/13477)）

---

## ハイライト4: RequestContext のエンドツーエンド貫通

### RequestContext とはなにか

Mastra の `RequestContext` はリクエストスコープのメタデータストアです。テナント ID・ユーザー ID・リージョン・フィーチャーフラグといった「このリクエストをする人・環境に関する情報」を、ツール呼び出しや MCP サーバーアクセスに至るまで引き渡す仕組みです。

v1.11 では、この `RequestContext` が **実行 → トレーシング → ストレージ → 評価** の全フェーズで使えるようになりました。

### トレーシングスパンへの記録

各スパンが実行時の `RequestContext` のスナップショットを自動的に保持するようになりました。`ClickHouse・PostgreSQL・LibSQL・MSSQL` のスパンテーブルにも `requestContext` カラムが追加されています。

これにより、「tenant-A のトレースだけ絞り込む」「この region のレイテンシ分布を見る」といったクエリが、既存のスパンテーブルに対して直接書けます。

### データセットと実験評価

「テストデータを作った時点のコンテキスト情報」を一緒に保存し、実験を走らせるときにそのコンテキストをエージェントに再注入できます。

```
// キャプチャ時のコンテキストをデータセットアイテムに保存
await dataset.addItem({
  input: messages,
  groundTruth: expectedOutput,
  requestContext: { userId: '123', locale: 'en' },
});

// 実験実行時にグローバルコンテキストを注入
await runExperiment(mastra, {
  datasetId: 'my-dataset',
  targetType: 'agent',
  targetId: 'my-agent',
  requestContext: { environment: 'staging' },
});
```

アイテムレベルの `requestContext` は実験レベルのものより**優先**されます。「ほとんどは staging 環境だが、特定アイテムだけ production 環境でテストしたい」という構成が素直に書けます。

`@mastra/client-js` でも同様のオプションが追加されているため、API 経由でデータセットを操作するワークフローにもシームレスに組み込めます。（[PR #14020](https://github.com/mastra-ai/mastra/pull/14020), [PR #13938](https://github.com/mastra-ai/mastra/pull/13938)）

---

## ハイライト5: ストレージの全面パフォーマンス改善

### セマンティックリコールのボトルネック

長期間利用されるエージェントのスレッドは、何千ものメッセージを抱えることがあります。Mastra のセマンティックリコールは「意味的に近い過去メッセージ」をベクター検索で取り出す機能ですが、従来実装の多くは「必要なメッセージを返す前にスレッド全体を読み込む」ロジックになっていました。

結果として、7,000 件超のメッセージを持つ Postgres スレッドでは、リコールに **約 30 秒** かかることがありました。これは SLA 設計上ほぼ論外の数字です。

### 改善の内容

最終的に必要なのは「リコールされた特定メッセージ＋前後のコンテキスト」だけです。スレッド全体をロードする必要はない—— この当たり前の事実を各アダプターが実装するようになりました。

| アダプター | 改善前（大規模スレッド） | 改善後 |
| --- | --- | --- |
| PostgreSQL（7,000+ メッセージ） | ~30 秒 | 500ms 以下 |
| LibSQL / Cloudflare D1 / ClickHouse | 劣化あり | スレッドサイズに依存しない |
| MongoDB / DynamoDB / Convex / Upstash / Lance / MSSQL / Cloudflare | 劣化あり | 改善済み |

（[PR #14022](https://github.com/mastra-ai/mastra/pull/14022)）

### PgVector のメタデータインデックス

PgVector でベクターテーブルを作る際、`metadataIndexes` オプションでメタデータフィールドへの btree インデックスが張れるようになりました。

```
await pgVector.createIndex({
  indexName: 'my_vectors',
  dimension: 1536,
  metadataIndexes: ['thread_id', 'resource_id'],
});
```

Memory の `memory_messages` テーブルはこれを利用して `thread_id` と `resource_id` に自動でインデックスを作成します。これにより、負荷の高い環境でシーケンシャルスキャンが走る問題が解消されます。（[PR #14034](https://github.com/mastra-ai/mastra/pull/14034)）

### 新しいベクター型: `bit` と `sparsevec`

`@mastra/pg` が pgvector の `bit`（バイナリベクター）と `sparsevec`（スパースベクター）をサポートしました。

```
// バイナリベクター：ハミング距離・ジャカード係数での高速類似検索
await db.createIndex({
  indexName: 'my_binary_index',
  dimension: 128,
  metric: 'hamming',
  vectorType: 'bit',
});

// スパースベクター：TF-IDF や BM25 スタイルの表現に
await db.createIndex({
  indexName: 'my_sparse_index',
  dimension: 500,
  metric: 'cosine',
  vectorType: 'sparsevec',
});
```

バイナリベクターは推論時にビット演算で計算されるため、浮動小数点ベクターに比べて検索が大幅に速くなります。スパースベクターは伝統的な情報検索手法（BM25 など）とニューラル検索を組み合わせたハイブリッド検索を構築するときに役立ちます。pgvector >= 0.7.0 が必要です。（[PR #12815](https://github.com/mastra-ai/mastra/pull/12815)）

---

## その他の注目アップデート

### Agent Playground が大幅強化

`@mastra/playground-ui@16.0.0` で、**Agent Playground タブ**と **Traces タブ**がエージェント詳細ページに追加されました。

Playground タブはエージェントの設定（インストラクション・ツール・モデル設定）を本番エージェントに影響を与えずに変更しながら、ライブチャットで即時テストできるサンドボックスです。バージョン比較、RequestContext の設定、データセット実験のトリガーをこの画面から直接行えます。

Traces タブはエージェントのトレース履歴をコンパクトなテーブルで表示します。ステータス・タイムスタンプ・入出力プレビュー・処理時間が並び、日付範囲フィルタと無限スクロールを備えています。行を選んで「データセットに追加」するチェックボックス機能が特に使い勝手よく、「本番トレースから評価データセットを育てる」ワークフローを UI だけで完結させます。

### Observational Memory が画像・ファイル添付に対応

オブザーバーが会話履歴中の画像やファイルを認識して推論に活用できるようになりました。添付ファイルのトークンカウントも Observation の閾値判定に含まれ、プロバイダーバックドのトークンカウンティングが利用可能な場合はキャッシュされます。マルチモーダルなエージェントで Observational Memory を使う際に影響します。（[PR #13953](https://github.com/mastra-ai/mastra/pull/13953)）

### Observational Memory の古いバッファ観測バグ修正

長期間動作するスレッドで、Observation のアクティベーション時に古いバッファリング済みの観測が使われる問題が修正されました。アクティベーション時に最新のスレッド状態を使うようになり、正しい観測が昇格されます。（[PR #13955](https://github.com/mastra-ai/mastra/pull/13955)）

### ツール呼び出し引数の堅牢性強化

LLM が JSON に壊れた値を付け足すケースへの対策が二重に入りました。

一つ目は **JSON リペア**: Kimi/K2 など一部の LLM がプロパティ名のクォート欠落やシングルクォート使用、末尾のカンマなどの壊れた JSON を返した場合でも、修復を試みてからパースします。（[PR #14033](https://github.com/mastra-ai/mastra/pull/14033)）

二つ目は **内部トークンの除去**: OpenRouter や OpenAI 経由の一部モデルが `<|call|>` や `<|endoftext|>` などのトークンを JSON の後ろにつけることがあります。これらをパース前に除去し、有効なデータが無言で捨てられないようにします。文字列値の中に `<|...|>` が含まれる正当な JSON はそのまま通ります。（[PR #13400](https://github.com/mastra-ai/mastra/pull/13400)）

### モデルフォールバックのリトライ挙動の修正

これまでリトライの二重構造になっていた問題が修正されました。従来は p-retry によるリトライと独自フォールバックループが重複しており、`maxRetries: 2` の設定が実質 `(2+1)²= 9` 回の呼び出しにつながるケースがありました。修正後は、リトライのレイヤーは p-retry の一層のみ。また、認証エラー（401/403）のような「リトライしても無意味なエラー」では同一モデルへの再試行をスキップして即座に次のフォールバックモデルに移ります。（[PR #14039](https://github.com/mastra-ai/mastra/pull/14039)）

### `processOutputResult` にリゾルブ済みの結果オブジェクトが渡されるようになった

アウトプットプロセッサーの `processOutputResult` に `result` 引数が追加されました。使用トークン数・生成テキスト・ステップ数・終了理由がまとめて `OutputResult` オブジェクトとして渡ります。生のストリームチャンクを自分でパースする必要がなくなります。（[PR #13810](https://github.com/mastra-ai/mastra/pull/13810)）

### MCP サーバーのツール実行トレース対応

MCP サーバー経由で実行されたツール呼び出しが Observability UI のトレースに表示されるようになりました。（[PR #12804](https://github.com/mastra-ai/mastra/pull/12804)）

### agentic ループの異常終了バグ修正

`generate()` に `structuredOutput` を使っているとき、モデルが最大出力トークン（`finishReason: 'length'`）に達してもループが止まらず `maxSteps` まで走り続ける問題が修正されました。また、gpt-5.3-codex などツールコールを返しながら `finishReason: 'stop'` にもなるモデルで、ループが途中で打ち切られるバグも同時に修正されています。

### Transient ストリームチャンク

`writer.custom()` で `transient: true` を指定すると、チャンクはクライアントにストリーミングされるものの、DB には保存されません。大量の stdout/stderr をリアルタイム表示しつつストレージを無駄に膨らませたくない場合に使えます。Workspace ツールはこれを活用して標準出力のストリーミング部分を transient として送るようになりました。（[PR #13869](https://github.com/mastra-ai/mastra/pull/13869)）

---

## 破壊的変更

v1.11 の主な破壊的変更は **Zod の最小バージョン引き上げ**です。詳細はハイライト2を参照してください。

その他の変更はほぼ後方互換ですが、特に以下の点を確認してください。

* Observational Memory を使っていて `@mastra/core` のバージョンが `request-response-id-rotation` をサポートしていない場合、互換性チェックで早期エラーが出るようになりました。この場合は `@mastra/core` と `@mastra/memory` を同時にアップデートしてください。
* Zod v4 に移行する場合のコード変更については、自動コードモッドを活用してください。

```
npx @mastra/codemod@latest v1
```

---

## バージョン要件

```
{
  "dependencies": {
    "@mastra/core": "^1.11.0",
    "@mastra/memory": "^1.6.2",
    "mastra": "^1.11.0",
    "@mastra/pg": "^1.8.0",
    "zod": "^3.25.0"
  }
}
```

---

今回のリリースは、「プロダクションで動かし続ける」ための信頼性とパフォーマンスに特にフォーカスした内容です。とりわけセマンティックリコールの 30 秒 → 500ms 改善は、大規模スレッドを持つシステムにとってすぐにアップデートする価値があります。ダイナミックモデルフォールバック配列は、マルチテナント・マルチリージョンのエージェント設計を根本的にシンプルにしてくれます。

詳細は[公式 Changelog](https://mastra.ai/blog/changelog-2026-03-16) と [GitHub Release](https://github.com/mastra-ai/mastra/releases/tag/%40mastra%2Fcore%401.11.0) をあわせてご覧ください。
