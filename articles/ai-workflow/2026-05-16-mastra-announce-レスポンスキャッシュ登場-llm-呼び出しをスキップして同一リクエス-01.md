---
id: "2026-05-16-mastra-announce-レスポンスキャッシュ登場-llm-呼び出しをスキップして同一リクエス-01"
title: "[Mastra Announce] レスポンスキャッシュ登場 - LLM 呼び出しをスキップして同一リクエストをキャッシュから返す"
url: "https://zenn.dev/shiromizuj/articles/235852ea2de555"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "AI-agent", "LLM", "OpenAI", "GPT"]
date_published: "2026-05-16"
date_collected: "2026-05-17"
summary_by: "auto-rss"
query: ""
---

[Mastra](https://mastra.ai/) の [公式Blog](https://mastra.ai/blog) で発表された [Announcements](https://mastra.ai/blog/category/announcements) を速報ベースで解説します。ただの直訳ではなく、関連情報も補いながら、なるべく「何がうれしいのか」「前は何が足りなかったのか」まで分かるように整理します。速報性重視のため一部は公開情報ベースの解釈を含みますが、事実と推測は分けて書きます。

[Mastra Announcements 速報解説一覧](https://zenn.dev/shiromizuj/articles/cc91bb06db5b5b)

---

## Mastra が `ResponseCache` を正式導入した

2026年5月15日、Mastra は **Response Caching** 機能を発表しました。

エージェントに届いた同一リクエストに対し、LLM を呼び出さずキャッシュから直接レスポンスを返す仕組みです。LLM の呼び出しコストとレイテンシの両方を削減できます。

要点をまとめると次の通りです。

* `ResponseCache` を `inputProcessors` に追加するだけで有効化できる
* 最初の呼び出しはLLMに渡り、レスポンスをキャッシュに書き込む
* 以降の同一リクエストはLLM呼び出しをスキップし、キャッシュから返す
* `ttl`（秒）でキャッシュの有効期間を設定できる
* 本番では `RedisCache` などカスタムバックエンドに差し替えられる
* `@mastra/core@1.33.0` 以降が必要（実験的機能）

---

## 背景

### LLM 呼び出しのコスト問題

LLM API はリクエストごとに課金されます。GPT-5 や Claude Sonnet クラスのモデルでは、同じ質問に毎回課金されるのは無視できないコストです。

エージェントベースのアプリケーションでは、ユーザー全体で見ると同一または非常に類似したリクエストが繰り返されるケースが多くあります。

* FAQ bot や社内ヘルプデスクエージェント
* UI に設置された「おすすめ質問」ボタン（押す人が多い）
* ガードレールエージェント（同一のポリシーで同一の入力を繰り返し分類）
* プロンプトテンプレートが固定されたバッチ処理

こうした場面では、LLM を毎回呼ぶことにメリットはなく、むしろレイテンシの無駄でもあります。

### inputProcessors という設計の位置付け

Mastra には `inputProcessors` という仕組みがあります。エージェントの実行パイプラインに対して、LLM 呼び出しの前後に処理を差し込める拡張ポイントです。以前に発表された **Guardrails** や **Processors** も同じ仕組みの上に作られています。

今回の `ResponseCache` も `inputProcessors` の一つとして実装されており、エージェントコードに対してほとんどコードの侵食なく追加できます。

---

## ニュースリリースの内容紹介

### 発表概要

2026年5月15日、Mastra は `ResponseCache` を正式に導入しました。`@mastra/core@1.33.0` 以降で利用可能です（[PR #16283](https://github.com/mastra-ai/mastra/pull/16283)）。

エージェントに届いた同一リクエストに対し、最初の呼び出しでLLMのレスポンスをキャッシュし、以降の同一リクエストではLLM呼び出しをスキップしてキャッシュから返します。

### 最小構成のコード例

```
import { Agent } from "@mastra/core/agent";
import { InMemoryServerCache } from "@mastra/core/cache";
import { ResponseCache } from "@mastra/core/processors";

const cache = new InMemoryServerCache();

export const searchAgent = new Agent({
  id: "search-agent",
  name: "Search Agent",
  model: "anthropic/claude-sonnet-4-6",
  instructions: "You answer questions concisely.",
  inputProcessors: [
    new ResponseCache({
      cache,
      ttl: 600  // 10分間キャッシュ
    })
  ]
});
```

```
// 1回目: LLMを呼び出し、キャッシュに書き込む
await searchAgent.generate("What is the capital of France?");

// 2回目以降（TTL内）: キャッシュから返す、LLM呼び出しなし
await searchAgent.generate("What is the capital of France?");
```

開発では `InMemoryServerCache`、本番では `RedisCache` 等のカスタムバックエンドを推奨しています。

### 公式リリース URL

---

## 具体的な掘り下げ

### キャッシュの仕組み: `processLLMRequest` と `processLLMResponse`

`ResponseCache` は2つのフックを使って動作します。

* **`processLLMRequest`**: LLM呼び出しの前にキャッシュを参照する。ヒットした場合はキャッシュのチャンクを返して LLM 呼び出しを短絡（short-circuit）する
* **`processLLMResponse`**: LLM呼び出しが完了した後にレスポンスをキャッシュに書き込む

エラーになった実行はキャッシュされないため、次の呼び出しはクリーンな状態でリトライされます。

`agent.generate()` と `agent.stream()` の両方に対応しており、ストリーミング用のキャッシュヒットでも `fullStream` を反復したり `text`、`usage`、`finishReason` を await したりする消費者から見て、通常の呼び出しと同じ形で値が返ってきます。

### キャッシュキーの導出

キャッシュキーは、LLM の応答に影響する次の要素を元に決定論的に生成されます。

* `agentId`: エージェントの識別子
* `stepNumber`: ツールループ内のステップ番号（各ステップが独立してキャッシュされる）
* `scope`: テナントやユーザーのスコープ
* モデルの識別情報（`provider`、`modelId`、スペックバージョン）
* 解決済みプロンプト（メモリのロードと前段プロセッサの処理を経た後）

これらのいずれかが変わると自動的にキャッシュが無効化されます。**メモリのロードや前段プロセッサによる変換が済んだ後のプロンプト**を元にキーを作るため、実際にLLMに届く内容に基づいてキャッシュが管理されます。

キャッシュキーはカスタマイズも可能です。

```
import { ResponseCache, buildResponseCacheKey } from '@mastra/core/processors';

await agent.stream(input, {
  requestContext: ResponseCache.context({
    // モデルIDと末尾200文字だけでキャッシュ
    key: ({ model, prompt }) =>
      `qa:${model.modelId}:${JSON.stringify(prompt).slice(-200)}`,
  }),
});

// deterministic helper を再利用しつつ scope だけ上書き
await agent.stream(input, {
  requestContext: ResponseCache.context({
    key: inputs => buildResponseCacheKey({ ...inputs, scope: 'global' }),
  }),
});
```

### テナントスコープ: デフォルトはユーザー分離

`ResponseCache` はデフォルトで `MASTRA_RESOURCE_ID_KEY` をリクエストコンテキストから読み取り、スコープとして使用します。Mastra のメモリ機能が `resourceId` を既にセットしているエージェントでは、自動的にユーザーごとの分離が適用されます。つまり、**別のユーザーのキャッシュ結果が混入しない**ようになっています。

スコープは明示的に上書きできます。

```
new Agent({
  // ...
  inputProcessors: [
    new ResponseCache({
      cache,
      scope: 'org-123',  // 組織単位でスコープを固定
    }),
  ],
});
```

パブリックかつ非パーソナライズなコンテンツでは `scope: null` を渡すと全ユーザー共有のキャッシュになります。

### 呼び出し単位のオーバーライド: `RequestContext`

`ResponseCache.context()` または `ResponseCache.applyContext()` を使うと、1回の呼び出し単位でキャッシュ挙動を変えられます。

```
import { ResponseCache } from '@mastra/core/processors';

// カスタムキーを指定して呼び出す
await agent.stream('hello', {
  requestContext: ResponseCache.context({ key: 'custom-key', bust: true }),
});
```

オーバーライド可能なフィールドは3つです。

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `key` | `string | function` | キャッシュキーをこの呼び出しのみ上書き |
| `scope` | `string | null` | スコープをこの呼び出しのみ上書き。`null` でスコープ無効化 |
| `bust` | `boolean` | `true` にするとキャッシュ読み取りをスキップし、書き込みは行う（「強制リフレッシュ」ボタン向け） |

`cache`、`ttl`、`agentId` はコンストラクタで固定されるインスタンスレベルの設定なので、呼び出し単位では変更できません。

### カスタムバックエンド: 本番では Redis を推奨

`InMemoryServerCache` はプロセス再起動でデータが消え、分散環境では共有できないため、開発専用です。本番環境には `@mastra/redis` の `RedisCache` を使います。

```
import { Agent } from '@mastra/core/agent';
import { ResponseCache } from '@mastra/core/processors';
import { RedisCache } from '@mastra/redis';

const cache = new RedisCache({ url: process.env.REDIS_URL });

export const agent = new Agent({
  name: 'Cached Agent',
  instructions: '...',
  model: 'openai/gpt-5',
  inputProcessors: [new ResponseCache({ cache })],
});
```

`MastraServerCache` インターフェースを実装すれば、任意のストレージへの接続も可能です（プロセッサが呼び出すのは `get` と `set` のみ）。

### どんな用途に向いているか、向いていないか

公式ドキュメントが明確に述べています。

**向いているケース**:

* 同じリクエスト形式がユーザーやセッションをまたいで繰り返す
* プロンプトテンプレートが固定されたバッチ処理
* おすすめプロンプトボタン（同じ入力を多数のユーザーが押す）
* 繰り返し同じ入力を分類するガードレールLLM

**向いていないケース**:

* ツール経由で外部に副作用を起こす呼び出し（キャッシュヒット時はツール呼び出しを再実行しないため）

---

## この発表の文脈: Mastra のプロセッサ体系

Mastra は近年、エージェントの実行パイプラインを拡張するための `inputProcessors` の仕組みを整備してきました。今回の `ResponseCache` はその中の最新の追加です。

```
エージェント実行パイプライン
  ↓
inputProcessors（順番に実行）
  ├─ Guardrail（入力検証・安全フィルタ）
  ├─ その他カスタムプロセッサ
  └─ ResponseCache（キャッシュ参照 → ヒット時はここで短絡）
  ↓
LLM呼び出し（キャッシュミス時のみ）
  ↓
ResponseCache のレスポンスフック（キャッシュ書き込み）
```

Guardrails が「入力を通過させるか検証する」仕組みであるのに対し、`ResponseCache` は「同一リクエストに対し以前の出力を再利用する」仕組みです。いずれも `inputProcessors` という同一の差し込み口を通じてエージェントに追加できます。

この設計は **責務の分離** と **組み合わせの柔軟性** を両立しています。ガードレールとキャッシュを同一エージェントに組み合わせることも可能です。

---

## 実験的機能について

アナウンス末尾でも公式ドキュメントでも明示されていますが、`ResponseCache` は現在 **実験的機能** として提供されています。リリース間でAPIが変わる可能性があります。

実験的フラグが付いている理由については公式に詳細は語られていませんが、ドキュメントには次の一文があります。

> Caching is implemented as the `ResponseCache` input processor. Mastra doesn't provide an agent-level option. To enable caching, register the processor explicitly. This keeps the API surface small while Mastra collects feedback; per-call overrides flow through `RequestContext`.

つまり「フィードバックを集めながらAPIサーフェスを小さく保つ」というスタンスです。今後の利用事例やフィードバックに応じて、設定方法やキャッシュキーの戦略が変わる可能性を含めての実験的扱いと読むのが妥当です。

---

## まとめ

Mastra の `ResponseCache` は、エージェントへの同一リクエストに対してLLM呼び出しをスキップし、コストとレイテンシを削減するための `inputProcessor` です。

ポイントは以下の3点です。

1. **導入が軽い**: `inputProcessors` に追加するだけで既存エージェントを変えずに動く
2. **テナント安全**: デフォルトでユーザーごとのスコープ分離が行われる
3. **本番対応可能**: `RedisCache` やカスタム `MastraServerCache` でスケールする

現時点では実験的機能のため、本番利用の際はAPIの変更に注意が必要です。ただし、設計の方向性は明確であり、「同じリクエストが繰り返される」ユースケースではすぐに試す価値があります。

---

## 参考リンク
