---
id: "2026-06-11-claude-fable-5をapiに入れる前に見るべき7つの本番チェックリスト-01"
title: "Claude Fable 5をAPIに入れる前に見るべき7つの本番チェックリスト"
url: "https://qiita.com/YushiYamamoto/items/3150aae08e4065f8a4d1"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "AI-agent", "TypeScript", "qiita"]
date_published: "2026-06-11"
date_collected: "2026-06-11"
summary_by: "auto-rss"
query: ""
---

![Claude Fable 5のモデルルーティング・フォールバック・データ保持を監視する管制画面](https://gist.githubusercontent.com/YushiYamamoto/6b4060f16f8952d2b93cabb76ec952a4/raw/bbcbd1f89973249205fa5e0bda31b8cd3736cb08/eyecatch.png)

2026年6月11日 JST 時点で、Anthropicの公式発表、Claude API Docs、移行ガイド、stop reason / fallback ドキュメント、データ保持ポリシー、Amazon Bedrockのモデルカードを確認しました。

Claude Fable 5は「Opusより賢い新モデル」とだけ見ると危険です。APIに組み込む側にとって重要なのは、**長時間エージェント向けの能力**と同時に、**refusal、fallback、always-on thinking、30日データ保持、料金、プラットフォーム差分**が一気に増えることです。

この記事では、Fable 5を本番プロダクトや社内エージェントに入れる前に、コードと運用で確認すべきポイントをチェックリスト化します。

## 結論

Fable 5は「全リクエストを差し替えるモデル」ではなく、**高難度・長時間・検証ループ付きのタスクに限定して使うべきモデル**です。

| 確認項目 | 何が変わるか | 実務での対応 |
|---|---|---|
| モデル選定 | `claude-fable-5` は長時間・複雑タスク向け | ルーティング条件を決める |
| stop reason | `refusal` がHTTP 200で返る | エラーではなく通常分岐として扱う |
| fallback | 自動再実行は環境ごとに差がある | API / Bedrock / Vertex / Foundryで実装を分ける |
| thinking | adaptive thinkingが常時有効 | `max_tokens` と遅延を再設計する |
| 料金 | $10 input / $50 output per 1M tokens | Opus 4.8との差額をワークロード単位で測る |
| データ保持 | Mythos-classは30日保持が必須 | ZDR前提の案件から除外する |
| tokenizer / cache | トークン数とcache条件が変わる | count_tokensと本番ログで再計測する |

## 1. まず「どのタスクにだけ使うか」を決める

Fable 5は、Claude API、Claude Platform on AWS、Amazon Bedrock、Vertex AI、Microsoft Foundryで一般提供されています。一方、Mythos 5はProject Glasswingの承認済み顧客向けです。

原文: "most capable widely released model"
日本語訳: 「広く提供されるモデルの中で最も高性能なモデル」
https://platform.claude.com/docs/en/about-claude/models/introducing-claude-fable-5-and-claude-mythos-5

公式ドキュメント上のスペックは、1M token context window、最大128k output tokens、価格は $10 / $50 per 1M tokens です。これは長い仕様書、巨大コードベース、調査から実装までまたぐエージェントには魅力があります。ただし、単発の要約、短いFAQ、軽い分類に使うと、価格差に見合わない可能性があります。

おすすめは、最初から次のようにルーティングを分けることです。

| タスク | 既定モデル | Fable 5へ上げる条件 |
|---|---|---|
| FAQ / 短文生成 | Haiku / Sonnet | ほぼ不要 |
| 通常のコード修正 | Sonnet / Opus | 依存関係が多く、1回で設計判断が必要 |
| 大規模移行 | Fable 5候補 | 複数ファイル・長時間・検証ループあり |
| セキュリティ / バイオ周辺 | Opus以下を基本 | refusal / fallbackの仕様を受け入れられる場合のみ |
| 顧客機密・ZDR必須 | Fable 5を除外 | 30日保持を契約上許容できる場合だけ再検討 |

## 2. `stop_reason: "refusal"` を正常系として扱う

Fable 5で一番壊れやすいのは、APIエラー処理です。Fable 5の安全分類器が応答を拒否した場合、HTTPステータスは200のまま、レスポンス本文の `stop_reason` が `refusal` になります。

原文: "`stop_reason: \"refusal\"` as a successful HTTP 200 response"
日本語訳: 「`stop_reason: \"refusal\"` を成功したHTTP 200レスポンスとして返す」
https://platform.claude.com/docs/en/about-claude/models/introducing-claude-fable-5-and-claude-mythos-5

つまり、`try/catch` だけでは拾えません。レスポンスを受け取った後の分岐が必要です。

```ts
type ClaudeStopReason =
  | "end_turn"
  | "max_tokens"
  | "tool_use"
  | "pause_turn"
  | "model_context_window_exceeded"
  | "refusal";

function classifyClaudeResponse(response: {
  stop_reason: ClaudeStopReason;
  stop_details?: { category?: string | null } | null;
  model?: string;
}) {
  if (response.stop_reason === "refusal") {
    return {
      status: "declined",
      category: response.stop_details?.category ?? "unknown",
      servedBy: response.model ?? "unknown",
      retryableByFallback: true,
    };
  }

  if (response.stop_reason === "max_tokens") {
    return { status: "truncated", retryableByContinuation: true };
  }

  return { status: "complete", servedBy: response.model ?? "unknown" };
}
```

特にストリーミングでは、途中まで出力されたあとに拒否されるケースもあります。その場合、部分出力は完成物として扱わず破棄します。

## 3. fallbackは「勝手に起きる」前提にしない

Fable 5のrefusalは、多くの場合、別のClaudeモデルで再実行できます。ただし、fallbackの実装はプラットフォームで違います。

原文: "There are three ways to retry"
日本語訳: 「再試行には3つの方法がある」
https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback

| 実行環境 | fallbackの置き場所 | 注意点 |
|---|---|---|
| Claude API | `fallbacks` parameter | beta headerが必要 |
| Claude Platform on AWS | server-side fallback | beta対象 |
| Amazon Bedrock | client-side / SDK middleware | `fallbacks` parameterは使えない |
| Vertex AI | client-side / SDK middleware | プラットフォーム側で実装差を吸収する |
| Microsoft Foundry | client-side / SDK middleware | Foundry側の提供条件を確認する |
| Message Batches API | 手動設計 | server-side fallback非対応 |

本番ログには、最低でも次を残します。

```json
{
  "requested_model": "claude-fable-5",
  "served_model": "claude-opus-4-8",
  "stop_reason": "end_turn",
  "fallback_attempted": true,
  "fallback_served": true,
  "stop_details_category": null,
  "workload_type": "large_code_migration"
}
```

ここを残さないと、後から「Fable 5で品質が出た」のか「Opus 4.8に逃げた結果なのか」を切り分けられません。

## 4. always-on adaptive thinkingで `max_tokens` を見直す

Fable 5ではadaptive thinkingが常時有効です。`thinking: {"type": "disabled"}` はサポートされず、thinkingの深さは `effort` で調整します。

原文: "adaptive thinking is the only thinking mode"
日本語訳: 「adaptive thinkingが唯一のthinking mode」
https://platform.claude.com/docs/en/about-claude/models/introducing-claude-fable-5-and-claude-mythos-5

移行ガイドで重要なのは、`max_tokens` が回答文だけでなくthinkingを含む出力全体の上限として効くことです。Opus 4.8でthinkingなしに動いていた処理をそのままFable 5へ変えると、同じ `max_tokens` でも体感が変わります。

```ts
const request = {
  model: "claude-fable-5",
  max_tokens: 16000,
  output_config: {
    effort: "high"
  },
  messages: [
    {
      role: "user",
      content: "このリポジトリの決済フローを安全に移行する計画と差分を作ってください。"
    }
  ]
};
```

まずは `high` を既定値にし、次の指標を見ながら `medium` / `xhigh` を切り替えます。

- 出力完了までの時間
- thinking tokensを含む出力トークン数
- tool use回数
- 人間レビューでの手戻り率
- fallback / refusalの発生率

## 5. 料金は「1リクエスト」ではなく「1ジョブ」で見る

Fable 5は $10 per 1M input tokens / $50 per 1M output tokens です。移行ガイドでは、Opus 4.8の $5 / $25 と比較して倍の単価として扱われています。

原文: "priced at $10 per million input tokens"
日本語訳: 「入力100万トークンあたり10ドル」
https://platform.claude.com/docs/en/about-claude/models/migration-guide

Fable 5の価値は、1回の応答が少し良いことではなく、**人間が数時間から数日かける仕事を、少ない往復で終わらせられるか**です。したがって、比較単位は1リクエストではなく1ジョブにします。

| 評価指標 | 悪い測り方 | 良い測り方 |
|---|---|---|
| コスト | 1回のAPI単価 | 完了までの総token / tool cost |
| 品質 | 1回答の印象 | PRレビュー指摘数、修正回数 |
| 速度 | 初回レスポンス速度 | 完了までの壁時計時間 |
| 安全性 | refusalが少ないか | refusal時のUXとfallback設計 |
| 採用判断 | ベンチマーク表 | 自社の代表タスク10件 |

サブスク利用者は、公式発表で6月22日までの追加費用なし期間と6月23日以降の使用クレジット制が案内されています。評価するなら、この日付をまたぐ前に代表タスクで比較しておくべきです。

https://www.anthropic.com/news/claude-fable-5-mythos-5

## 6. 30日データ保持を契約・顧客説明と照合する

Mythos-classモデルは、Fable 5を含めて30日データ保持が必要です。これは技術選定ではなく、契約・コンプライアンスの確認事項です。

原文: "retained for 30 days"
日本語訳: 「30日間保持される」
https://support.claude.com/en/articles/15425996-data-retention-practices-for-mythos-class-models

サポート記事では、ZDRを設定したClaude Console workspace、ZDR前提のClaude Enterprise / Claude Code、AWS Bedrock、Google Cloud Agent Platform、Microsoft Foundry経由の利用にも影響することが説明されています。移行ガイドでも、条件を満たさない組織からのFable 5リクエストは `400 invalid_request_error` になり得るとされています。

導入前に、次のようなrouting policyを先に作るのが現実的です。

```yaml
model_routing_policy:
  claude_fable_5:
    allow:
      - public_repository_migration
      - non_customer_internal_refactor
      - benchmark_without_sensitive_data
    deny:
      - zero_data_retention_contract
      - regulated_customer_data
      - private_security_report
      - raw_personal_information
    require:
      - stop_reason_logging
      - fallback_logging
      - cost_per_job_report
```

## 7. Bedrock / Vertex / Foundryは「同じFable 5」でも運用差が出る

Amazon Bedrockのモデルカードでは、Fable 5のcontext window、max output tokens、always-on adaptive thinking、`stop_reason: "refusal"`、prompt caching、region / service tierなどが整理されています。

原文: "handle `stop_reason: \"refusal\"` as a primary response path"
日本語訳: 「`stop_reason: \"refusal\"` を主要なレスポンス経路として扱う」
https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-fable-5.html

API仕様の見え方は似ていても、実際の本番運用では次が変わります。

- server-side fallbackが使えるか
- retained dataがどの環境に残るか
- regional availability / cross-region routingを許可できるか
- prompt cacheの最小token数が同じか
- batchやmanaged agentで使う場合の制約があるか

複数クラウドで同じアプリを動かす場合、`model = "claude-fable-5"` という1行だけを共通化するのではなく、platform adapterに分ける方が安全です。

## 実装チェックリスト

- [ ] Fable 5へ上げるタスク条件を定義した
- [ ] `stop_reason` をすべての成功レスポンスで確認している
- [ ] `refusal` をHTTPエラーではなく通常分岐として処理している
- [ ] `stop_details.category` をログに残している
- [ ] fallback前後の `requested_model` / `served_model` を記録している
- [ ] platformごとにfallback実装を分けている
- [ ] `thinking: {"type": "disabled"}` を送らない
- [ ] `max_tokens` をthinking込みで再設計した
- [ ] `effort` をジョブ別に測定している
- [ ] 30日データ保持とZDR契約の整合を確認した
- [ ] 1ジョブ単位でOpus 4.8 / Fable 5のコストと手戻りを比較した

## 失敗パターン

### 1. 「高性能だから全部Fable 5」にする

短いタスクでは単価差だけが目立ちます。まずは長時間・多段・レビュー負荷の高いタスクに限定します。

### 2. `refusal` を例外扱いにして監視から漏らす

Fable 5ではrefusalは本番で起こり得る正常な分岐です。`catch` ではなくレスポンスパーサーで拾います。

### 3. fallback後のモデルを記録しない

ユーザーには回答が返っていても、実際にはOpus 4.8が答えた可能性があります。評価ログに残さないと、Fable 5の効果測定が壊れます。

### 4. ZDR前提の顧客データを流す

Fable 5の導入可否は、技術より先にデータ保持条件で決まることがあります。契約・法務・セキュリティレビューを後回しにしない方が安全です。

## まとめ

Claude Fable 5は、長時間エージェントや大規模コード移行に強い一方で、API利用者に新しい責任を渡してくるモデルです。

導入前に見るべきポイントは、ベンチマークの順位ではありません。`refusal`、fallback、always-on thinking、30日保持、1ジョブ単位の費用対効果を測れるかです。ここを先に作ってからFable 5へルーティングすれば、強力なモデルを「高い実験」ではなく、再現性のある本番改善にできます。

## 参考リンク

- https://www.anthropic.com/news/claude-fable-5-mythos-5
- https://platform.claude.com/docs/en/about-claude/models/introducing-claude-fable-5-and-claude-mythos-5
- https://platform.claude.com/docs/en/release-notes/overview
- https://platform.claude.com/docs/en/about-claude/models/migration-guide
- https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons
- https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback
- https://support.claude.com/en/articles/15425996-data-retention-practices-for-mythos-class-models
- https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-fable-5.html

:::note
**この記事を書いた人✏️@YushiYamamoto**
ITPRODX.com代表 / AIアーキテクト
Next.js / TypeScript / n8nを活用した自律型アーキテクチャ設計を専門としています。
日々の自動化の検証結果や、ビジネス側の視点（ROI等）に関するより深い考察は、以下の公式サイトおよびnoteで発信しています。
:::

https://itprodx.com

https://note.com/prodouga
