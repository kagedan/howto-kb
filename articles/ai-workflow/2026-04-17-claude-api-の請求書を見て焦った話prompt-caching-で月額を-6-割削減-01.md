---
id: "2026-04-17-claude-api-の請求書を見て焦った話prompt-caching-で月額を-6-割削減-01"
title: "Claude API の請求書を見て焦った話：Prompt Caching で月額を 6 割削減"
url: "https://zenn.dev/jixiaopan/articles/claude-prompt-caching-cost"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "zenn"]
date_published: "2026-04-17"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

> **TL;DR**
>
> * 静的な system prompt に `cache_control: { type: "ephemeral" }` を 1 行足すだけで大きなコスト削減が可能
> * 100 クエリ/日のケースで **$28/月 → $12/月（約 60% 削減）**、キャッシュ対象部分だけ見れば 90% 減
> * 落とし穴は「**TTL 5 分**」と「**cache\_control の配置順序**」

---

## 結論

Claude API の月額コストを見直したとき、**Prompt Caching を正しく組み込むだけで全体コストが 6 割近く下がった**のが一番の発見でした。

工業向け AI アシスタント（エラーコード手册 + few-shot 例、合計 約 2000 tokens を毎回送信していた）で、`cache_control` を 1 行追加するだけで毎日のコストが約 $0.93 から $0.40 に。月額換算で $28 → $12 程度の差になります。

本記事で扱うこと：

* どのような内容をキャッシュすべきか・すべきでないか
* 実装方法（TypeScript + Anthropic SDK）
* 実測データ（Before / After の比較）
* 実運用で気づいた 3 つの落とし穴

---

## 背景：コストが気になり始めた瞬間

産業向けの AI 故障診断アシスタントを試作していました。100 種類以上のエラーコードを持つ現場で、運用者がコードだけを見ても即座に原因と対処法が分かる UI が必要だったためです。

設計はシンプルで、**エラーコード一覧 + 過去の修復履歴 + few-shot 例**を system prompt に全部載せて、`user` メッセージでは「このコードが出た」とだけ送る構成でした。Claude Sonnet 4.5 は 200K コンテキストを扱えるので、手册を丸ごと載せても余裕があります。動作は問題なく、精度も十分でした。

問題は **Anthropic の使用量ダッシュボードを開いたとき** です。まだプロト段階で 100 クエリ/日しか回していないのに、月額見込みが **約 $28** と表示されていて、思わず手が止まりました。

$28 自体は破綻的な金額ではありません。ただ、これは **1 アシスタント × プロト 1 台分** の数字です。本番想定の複数拠点 × 複数台数 × 1 日数百クエリにスケールすると、単純計算でも桁が 1〜2 上がる。しかも **95% は毎回同じ内容の繰り返し送信** で消えていく。

「同じ内容を毎回送るのは無駄では？」という素朴な疑問が出発点でした。

---

## 問題設定：毎回 2000 tokens を送っていた

アーキテクチャを並べてみると、無駄が見えてきます。

### システムプロンプトの構成

system prompt は大きく 3 ブロックに分かれていました：

| ブロック | 内容 | サイズ | 変化頻度 |
| --- | --- | --- | --- |
| Role 定義 | AI の役割・制約 | ~100 tokens | 不変 |
| エラーコード手册 | 100+ コード + 対処手順 | ~1500 tokens | 月 1 回更新 |
| Few-shot 例 | 6 個の対話例 | ~400 tokens | ほぼ不変 |

合計 **約 2000 tokens が全リクエストで同一**。対して `user` メッセージは「とあるエラーコードが出た、バッテリー 23%」のような短文で、せいぜい 100 tokens。

つまり、送信データの **95% は毎回同じ内容を繰り返し送っている**状態でした。LLM 側も毎回同じ処理を経由してから、その先の 5% の動的部分を理解し始める。ネットワーク帯域にとっても、Anthropic の課金メーターにとっても、明らかに最適化の余地があります。

この「静的 vs 動的」の比率こそ、Prompt Caching が効く典型的なパターンです。

---

## 解決策：Prompt Caching の仕組みと実装

Anthropic の Prompt Caching は、system prompt 内の「動かないブロック」を `cache_control` で指定することで、5 分間キャッシュしてくれる機能です。初回のリクエストでキャッシュが作成され、以降のリクエストは **通常の 1/10 のコスト** で同じ内容を「読み込む」だけで済みます。

仕組みは想像より単純で、`system` の配列の中に `cache_control` を含むブロックを置くだけです。

### 実装コード（TypeScript）

```
import Anthropic from "@anthropic-ai/sdk";
import { readFile } from "node:fs/promises";

const client = new Anthropic();

// 静的コンテンツを別ファイルで管理
const ERROR_MANUAL = await readFile("./data/error_manual.md", "utf-8");
const FEW_SHOT_EXAMPLES = await readFile("./data/few_shot.md", "utf-8");

const response = await client.messages.create({
  model: "claude-sonnet-4-5",
  max_tokens: 1024,
  system: [
    {
      type: "text",
      text: `You are an industrial diagnostic assistant.
Respond in Japanese, following the format in the examples.`,
    },
    {
      type: "text",
      text: `<error_manual>\n${ERROR_MANUAL}\n</error_manual>`,
      cache_control: { type: "ephemeral" }, // ← ここがキモ
    },
    {
      type: "text",
      text: `<examples>\n${FEW_SHOT_EXAMPLES}\n</examples>`,
      cache_control: { type: "ephemeral" },
    },
  ],
  messages: [
    { role: "user", content: "エラーコード X、バッテリー 23%" },
  ],
});

console.log(response.usage);
// 初回: { cache_creation_input_tokens: 1950, cache_read_input_tokens: 0, ... }
// 2回目以降: { cache_creation_input_tokens: 0, cache_read_input_tokens: 1950, ... }
```

ポイントは 3 つあります。

**1. `system` を配列で書く** — `string` 型ではなく `TextBlock[]` 型で渡すことで、ブロックごとに `cache_control` を指定できます。

**2. キャッシュするのは「動かない部分」だけ** — Role 定義は数百 tokens 程度なのでキャッシュしなくても影響が少ないですが、エラーコード手册（~1500 tokens）と few-shot（~400 tokens）は必ずキャッシュすべきです。

**3. `user` メッセージはキャッシュしない** — 毎回変わるので、キャッシュに含めてはいけません。含めると cache miss ばかりで逆効果になります。

### 何をキャッシュするかの判断基準

私はこのルールで判断しています：

* ✅ **1024 tokens 以上**（Sonnet の最小キャッシュサイズ）
* ✅ **5 分以内に複数回呼ばれる**
* ✅ **内容が動的に変わらない**

3 つ全部満たせばキャッシュ対象。1 つでも欠けると cache creation のオーバーヘッド（1.25x コスト）だけが発生して、むしろ損をします。

---

## 実測結果：Before / After の比較

計算前提：

* モデル：Claude Sonnet 4.5
* 静的 system prompt：2000 tokens
* 動的 user メッセージ：100 tokens
* Output：200 tokens
* 頻度：100 クエリ/日

### 価格（2026-04 時点）

| 項目 | 単価（per 1M tokens） |
| --- | --- |
| Input（通常） | $3.00 |
| Input（cache write） | $3.75（= 1.25x） |
| Input（cache read） | $0.30（= 0.1x） |
| Output | $15.00 |

### Before：キャッシュなし

```
Input:  100 × 2100 tokens × $3.00  / 1M = $0.630 / 日
Output: 100 × 200  tokens × $15.00 / 1M = $0.300 / 日
─────────────────────────────────────────────
合計:                                     $0.930 / 日
月額（30 日）:                             $27.90
```

### After：キャッシュあり

```
Cache create (初回 1 回):   1 × 2000 × $3.75  / 1M = $0.0075
Cache read   (99 回):      99 × 2000 × $0.30  / 1M = $0.0594
Dynamic input(100 回):    100 × 100 × $3.00  / 1M = $0.0300
Output       (100 回):    100 × 200 × $15.00 / 1M = $0.3000
──────────────────────────────────────────────────
合計:                                              $0.397 / 日
月額（30 日）:                                      $11.91
```

### 削減効果

| 指標 | Before | After | 削減率 |
| --- | --- | --- | --- |
| 日額 | $0.93 | $0.40 | **−57%** |
| 月額 | $27.9 | $11.9 | **−57%** |
| キャッシュ対象の input 部分のみ | $0.63 | $0.07 | **−89%** |

**全体で約 60% 削減**、キャッシュ対象部分だけ見れば **約 90% 削減**。

実運用では、キャッシュヒット率が高ければ（同じ手册を 5 分以内に複数回呼ぶケースが多ければ）削減率はさらに上がります。私の試算では、ピーク時間帯に限れば **80% 以上の削減** が見えました。

---

## ハマりどころ：実装時に気づいた 3 つの罠

### 罠 1：TTL 5 分の壁

ephemeral キャッシュは **5 分で自動破棄** されます。これは知っていたつもりでしたが、低頻度のバッチ処理では毎回 cache creation の課金が発生していました。

解決策は用途による：

* **連続的なリクエスト**（チャット UI など）→ そのまま使える
* **間欠的なリクエスト**（1 時間おきの分析など）→ キャッシュを諦める、または定期的な pinger で保温する
* **不確定なタイミング**（ユーザー問い合わせ駆動）→ アプリ側で頻度をモニタリング、低いなら機能オフ

### 罠 2：`cache_control` の配置順序

`cache_control` は **そのブロックまでの全ての前ブロックを含めてキャッシュ** します。つまり、動的コンテンツが前にあると意図せずキャッシュ対象になってしまい、cache miss ばかりになります。

```
// ❌ ダメな例：動的な userContext が前にある
system: [
  { type: "text", text: userContext },        // 毎回変わる
  {
    type: "text",
    text: ERROR_MANUAL,
    cache_control: { type: "ephemeral" },
  },
]
// 結果：userContext ごとに新しいキャッシュが作られる → 意味なし

// ✅ 正しい例：静的な内容を前に
system: [
  {
    type: "text",
    text: ERROR_MANUAL,
    cache_control: { type: "ephemeral" },
  },
  { type: "text", text: userContext },        // 毎回変わる
]
```

### 罠 3：最小キャッシュサイズ

キャッシュには **最小サイズ** があります（Sonnet 4.5: 1024 tokens、Haiku 4.5: 2048 tokens）。これを下回ると `cache_control` を書いても **無視される** だけで、エラーにもなりません。

「効いていない気がする」と思ったら、まず `usage.cache_creation_input_tokens` が 0 でないか確認するのが早道です。

---

## まとめ：いつ使うべきか、いつ使うべきでないか

**使うべき**：

* system prompt に 1024+ tokens の動かないコンテンツがある
* 5 分以内に複数回呼ばれる
* コストスケールが懸念

**使うべきでない**：

* system prompt が全体的に小さい（1024 tokens 未満）
* リクエスト間隔が 5 分以上（かつ pinger も難しい）
* キャッシュ対象にすべき内容が曖昧

Prompt Caching は「**正しく使えば魔法、間違えるとノーオペ**」な機能です。まずは `cache_creation_input_tokens` と `cache_read_input_tokens` を usage で観測しながら、削減効果を実測してから本番投入するのが安全です。

Claude 以外でも、OpenAI（Structured Outputs / prompt caching）や Google Gemini（Context Caching）で類似の機能が提供されています。LLM API のコスト最適化の第一歩として、覚えておいて損はないテクニックです。

---

## 参考リンク
