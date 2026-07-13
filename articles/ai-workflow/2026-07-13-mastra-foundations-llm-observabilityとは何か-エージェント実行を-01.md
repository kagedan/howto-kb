---
id: "2026-07-13-mastra-foundations-llm-observabilityとは何か-エージェント実行を-01"
title: "[Mastra Foundations] LLM observabilityとは何か？ エージェント実行をspan単位で読む"
url: "https://zenn.dev/shiromizuj/articles/d4e3c9fe76bcc2"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "AI-agent", "LLM", "TypeScript", "zenn"]
date_published: "2026-07-13"
date_collected: "2026-07-14"
summary_by: "auto-rss"
query: ""
---

[Mastra](https://mastra.ai/) の公式 Foundations 記事 [What is LLM observability? A span-by-span breakdown](https://mastra.ai/blog/what-is-llm-observability) をもとに、LLM observability がなぜ必要になったのか、そして Mastra がその問題をどう整理しているのかを解説します。今回は新機能の発表というより、**従来監視では見えなかったエージェントの失敗を、trace と span で可視化するための考え方を整理する記事**です。

先に要点を言うと、今回 Mastra が提示している解決策は「応答の見た目」ではなく **実行過程そのものを観測対象にする**ことです。モデル呼び出し、ツール呼び出し、メモリ操作、RAG、workflow step などを span の木として残せば、これまで 200 OK の陰に埋もれていた誤答、ループ、ツール失敗、コスト肥大化を後から追えるようになります。

---

---

## 先に結論

LLM observability は、LLM やエージェントの出力だけを見るのではなく、**その出力に至る途中の判断と入出力を operation 単位で記録する**考え方です。

従来のアプリ監視は、HTTP ステータス、例外、CPU、メモリ、レイテンシのような deterministic なソフトウェアを前提に設計されていました。ところがエージェントでは、システムが正常に返答していても内容だけが間違っていることが普通に起きます。ここが本質的なズレです。

Mastra の今回の記事は、そのズレを次のように埋めています。

* 最終応答の良し悪しだけでなく、model call と tool call の流れを trace に残す
* 1 回の agent run を 1 つの大きな処理ではなく、複数 step の span tree として扱う
* token、cost、tool success、finishReason、evaluation score のような LLM 固有 signal を追う
* OTel GenAI conventions に対応できる形で export し、backend lock-in を避ける

つまり今回の主張は「AI 用に別の監視製品が必要」という話だけではありません。**監視の粒度を、リクエスト単位から reasoning と tool execution の単位へ下げないと、agent の不具合は読めない**という整理です。

---

## これまで何が課題だったのか

### 誤答してもシステムは正常に見える

これが LLM observability の出発点です。通常の Web アプリなら、重大な問題は 500 エラーやタイムアウトとして現れます。ところが LLM アプリでは、もっと厄介な失敗が起きます。

* それっぽいが間違った答えを返す
* 本当はツール参照すべきなのに、内部知識だけで答える
* ユーザーの質問を取り違える
* 拒否すべきでない問い合わせを拒否する

このとき API レベルでは 200 OK で、メトリクス上の平均レイテンシも正常に見えることがあります。つまり、**インフラ監視が正常でも、知能部分だけ壊れている**状態が普通に起こります。

### 同じ失敗を再現しづらい

従来の不具合調査は、失敗条件を再現してログやブレークポイントで追うやり方が基本でした。しかし LLM では、同じ prompt を投げても同じ誤答になるとは限りません。モデル更新、temperature、周辺ツールの応答差分、履歴の積み上がりで結果が揺れます。

そのため、問題が起きた瞬間の実行内容を **本番で記録しておく**ことが重要になります。Mastra が tracing を強く押し出しているのはこのためです。

### 1 リクエストの中に複数の失敗地点がある

エージェントの 1 実行は、ふつう次のようなループです。

1. モデルが履歴と指示を読む
2. ツールを呼ぶか判断する
3. ツールを呼ぶ
4. 結果を受けてモデルが再度推論する
5. 必要ならさらにツールを呼ぶ
6. 最終応答を返す

この構造では、全体レイテンシ 1 個だけ見ても意味が薄いです。遅かったのがモデルなのか、ツールなのか、retrieval なのか、history 肥大化による token 増加なのか切り分けられません。

### 従来 signal と対応関係がずれる

Mastra の記事がうまいのは、従来監視と LLM observability の対応関係を明示している点です。

* status code に近いものは evaluation score
* request latency に近いものは time to first token、step latency、total loop time
* request count に近いものは token usage と cost
* exception/stack trace に近いものは tool error、wrong-tool decision、loop、refusal
* request 単位のログ行に近いものは span tree

ここから分かるのは、既存監視を捨てるのではなく、**既存監視の上に LLM 専用の観測面を追加する**必要があるということです。

---

## 今回 Mastra はどう整理したのか

### span tree で agent run を読む

Mastra の observability では、1 回の agent 実行を trace として保存し、その中に複数の span をぶら下げます。代表的には次のような構造です。

* `agent_run`: 実行全体
* `model_generation`: 1 回の生成サイクル
* `model_step`: generation の各 step
* `model_inference`: 実際の推論時間
* `model_chunk`: ストリーミング中の chunk
* `tool_call`: ツール実行
* `memory` / `rag` / `workflow` 系 span: 周辺処理

これにより、「1 回の回答を返すまでに何が起きたか」を木構造で読めます。重要なのは、**何が何を呼んだかという因果関係が trace の構造自体に残る**ことです。

この分離は非常に重要です。従来は「応答がおかしい」と分かったとき、原因がモデル判断なのか、ツール不達なのか、ツールは正しく返したがモデルが使い方を誤ったのかをログから推測する必要がありました。

span ベースでは、少なくとも次の切り分けがしやすくなります。

* モデルは何の引数でツールを呼ぼうとしたか
* ツールは成功したか、失敗したか
* ツールは何を返したか
* その後のモデルはどう応答したか

つまり、**モデルの意思決定とツールの実行結果を別々の観測事実として保存する**のが、従来監視からの大きな転換点です。

### 型付き span で「何を記録すべきか」を固定する

Mastra の span は自由形式ログではなく、型付きです。記事でも、span type ごとに持てる属性が TypeScript で制約される点が強調されています。

これは地味ですが効きます。AI 系 observability は、各社が好きな名前でフィールドを足し始めるとすぐ読みにくくなるからです。型付き span にしておけば、たとえば model generation span には model 名、provider、finishReason、usage を持たせ、tool call span には success や toolDescription を持たせる、という整理を崩しにくくなります。

### framework-native instrumentation で境界を見失いにくい

記事では telemetry の取り方を 3 つに分けています。

* framework-native instrumentation
* provider SDK を patch する auto-instrumentation
* API gateway / proxy 型の監視

Mastra が押しているのは 1 です。フレームワーク自身が agent loop を知っているので、tool 呼び出し、workflow step、memory、RAG などの境界で素直に span を切れます。

逆に SDK patch や gateway は導入が簡単な代わりに、アプリケーション内部のロジックやツール間の関係は見えにくくなります。ここは observability 設計の典型的なトレードオフです。

---

## trace を読むと、どんな失敗が見えるのか

### 誤答とインフラ障害を切り分けられる

たとえばツール呼び出しに失敗した場合、`tool_call` span に `success: false` が残り、エラー原因も付けられます。これなら「モデルが勝手に hallucination した」のか、「正しくツールを呼んだが orders API が落ちていた」のかが分かります。

この違いは運用上かなり重要です。前者なら prompt や tool selection の改善、後者ならインフラ対応が必要だからです。

### ループや遅延やコスト肥大化も span tree で読める

AI エージェントの不具合は例外だけではありません。むしろ多いのは、失敗していないのに効率が悪いケースです。

* 同じ tool を何 step も繰り返す loop
* `model_inference` だけ異様に遅い
* 会話履歴の積み上がりで `inputTokens` が step ごとに増える
* reasoning token が過剰でコストが膨らむ

これらは最終回答だけでは見えません。span ごとの時間、token usage、親子関係を見ることで初めて分かります。

---

## OpenTelemetry との関係

### LLM telemetry にも共通語彙が必要になってきた

AI observability の世界はまだ若いですが、OpenTelemetry の GenAI semantic conventions によって共通語彙が整い始めています。Mastra の記事は、この標準化をかなり前向きに評価しています。

その理由は単純で、span 名や属性名が backend ごとにバラバラだと、Langfuse から Datadog に移るだけで実装が壊れるからです。

Mastra は内部 span model を持ちつつ、export 時に OTel naming へ map します。つまり、アプリの内部表現は Mastra 側で安定させ、外向きの互換性は exporter で吸収する設計です。

この設計はかなり実務的です。規格変更が起きても exporter だけ直せば済み、アプリ全体の instrumentation を張り替えずに済むからです。

---

## 本番運用では何に気をつけるべきか

### 1. 秘密情報の混入

prompt や tool output には、ユーザー入力、社内 API 応答、token、key、個人情報が平然と混ざります。そのため observability は「詳しく取るほど良い」で終わりません。

Mastra docs でも `SensitiveDataFilter` が既定の processor として扱われています。少なくとも本番では、機密値を export 前に redact する前提で考えるべきです。

```
import { Mastra } from '@mastra/core'
import { LibSQLStore } from '@mastra/libsql'
import {
  Observability,
  MastraStorageExporter,
  SensitiveDataFilter,
} from '@mastra/observability'

export const mastra = new Mastra({
  storage: new LibSQLStore({
    id: 'app-storage',
    url: 'file:./mastra.db',
  }),
  observability: new Observability({
    configs: {
      default: {
        serviceName: 'support-app',
        exporters: [new MastraStorageExporter()],
        spanOutputProcessors: [
          // prompt や tool 出力に含まれる秘密情報を保存前にマスクする
          new SensitiveDataFilter(),
        ],
      },
    },
  }),
})
```

### 2. 保存量の肥大化

会話履歴やツール返却値を全部入れると、1 trace あたりのサイズはすぐ大きくなります。Mastra docs では `serializationOptions` で文字列長、配列長、オブジェクト key 数、ネスト深さを制限できます。

つまり observability の設計は、デバッグ容易性と保存コストの綱引きです。開発環境では広く取り、本番では上限を厳しくする設計が自然です。

### 3. 全件 trace する必要はない

sampling も重要です。Mastra では always / never / ratio / custom の 4 種類が使えます。

```
export const mastra = new Mastra({
  observability: new Observability({
    configs: {
      default: {
        serviceName: 'support-app',
        sampling: {
          type: 'ratio',
          probability: 0.1,
        },
        exporters: [new MastraStorageExporter()],
      },
    },
  }),
})
```

開発中は全件、本番は 1 割、ただし新機能や重要顧客だけは custom sampling で厚めに取る、といった運用が考えられます。

### 4. trace と metrics は保存先の向きが違う

Mastra docs では、trace は多くのストレージで扱える一方、metrics や集計は DuckDB や ClickHouse のような OLAP 向きストアが欲しいと整理されています。ここも実務上大事です。

つまり observability は単に exporter を足すだけではなく、**どの信号をどの保存先に送るか**まで含めて設計する必要があります。

---

## 何がうれしいのか

今回の記事は「Mastra に observability 機能がある」という紹介に留まりません。もっと重要なのは、**エージェント運用のデバッグ単位が変わる**ことをはっきり示している点です。

* レスポンスの成否ではなく、step ごとの挙動を見られる
* ツール失敗とモデル誤判断を分けて改善できる
* token と cost の増え方を trace 上で追える
* trace ID を起点に logs や metrics と結び付けられる
* OTel ベースで backend を選び直しやすい

特に、Mastra docs が tracing を observability の土台として位置付けているのは筋が良いです。traces から duration、token、cost を metrics に派生させ、logs や feedback を trace ID で相関させる構造は、AI アプリの運用設計としてかなり分かりやすいからです。

---

## まとめ

LLM observability が必要になった理由は明快です。**AI エージェントの失敗は、システム障害としてではなく、実行過程のどこかの判断ミスとして現れる**からです。

従来の監視は、その手前までは見えても、その中身までは見えませんでした。今回 Mastra が示した解き方は、agent run を span tree として保存し、model、tool、memory、workflow の各境界を framework-native に記録することです。

そのうえで、redaction、truncation、sampling、span filtering、適切な storage 分離を組み合わせれば、実用的な observability 基盤として運用できます。言い換えると、今回のテーマは単なる可視化ではなく、**エージェントを本番で改善し続けるための観測面をどこまで下げるか**にあります。

応答がまともに見えるだけでは、もう十分ではありません。これからの AI アプリでは、「どう答えたか」より先に **「どうその答えに至ったか」** を読めることが、品質改善の起点になります。

---

## 参考リンク
