---
id: "2026-03-30-claude-code-claudeai-のチーム利用量を月3で可視化するダッシュボードを作った-01"
title: "Claude Code / claude.ai のチーム利用量を月$3で可視化するダッシュボードを作った"
url: "https://qiita.com/Odin/items/f637f010c0274b0d9aa6"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-03-30"
date_collected: "2026-03-31"
summary_by: "auto-rss"
---

## はじめに

Anthropicが提供するClaude Codeを10人のチームで利用しています。Teamsプランの公式ダッシュボードでは取得できる情報が限られており、「誰がどれくらい使っているか」「トークン消費量の推移」といった情報が把握できませんでした。

そこで、[ZOZOのテックブログ記事](https://techblog.zozo.com/entry/claudecode-otel)を参考に、AWS上に自前のダッシュボードを構築しました。月額$3程度で運用できます。

## 何を作ったか

Claude CodeのOpenTelemetryテレメトリデータと、claude.aiのエクスポートデータを収集・可視化するダッシュボードです。

### Claude Code ダッシュボード

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3566513%2F19844f4d-a507-4cbf-981f-4e21f20fd07f.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=77e2e644a7daf9fca1b7c378fd56bb51)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3566513%2F19844f4d-a507-4cbf-981f-4e21f20fd07f.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=77e2e644a7daf9fca1b7c378fd56bb51)

* 日別セッション数・トークン推移
* ユーザー別トークン消費量
* モデル別利用比率
* 期間フィルタ（7日/30日/90日/1年）
* 表示項目のトグル（コスト表示ON/OFF等）

### Claude.ai ダッシュボード

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3566513%2F125944f6-125a-4a8e-8d0c-eeb4fb2d0b68.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=ea40c579e9fc68641fb96428c91e20a0)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3566513%2F125944f6-125a-4a8e-8d0c-eeb4fb2d0b68.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=ea40c579e9fc68641fb96428c91e20a0)

* ZIPファイルをドラッグ&ドロップでアップロード
* ユーザー別・日別のトークン消費推移（推定値）
* 期間フィルタ

## 構成

```
[Claude Code]
各メンバーのPC
  ↓ OpenTelemetry (OTLP/protobuf)
Lambda Function URL (Collector)
  ↓
CloudWatch Logs (/otel/claude-code)
  ↓ 日次 EventBridge
Lambda (Dashboard Generator)
  ↓
S3 → CloudFront (Basic認証)

[Claude.ai]
claude.aiでエクスポート → ZIPをダッシュボードにドラッグ&ドロップ
  ↓ 署名付きURL
S3 (Upload Bucket) → Lambda (Processor)
  ↓
CloudWatch Logs (/claude-ai/usage)
  ↓
Lambda (API) → ダッシュボードに動的表示
```

ALBやAPI Gatewayを使わず、Lambda Function URLで直接HTTPSエンドポイントを公開することで、固定費を最小化しています。

### コスト

| コンポーネント | 月額 |
| --- | --- |
| Lambda (Collector + Generator + Processor + API) | ~$1 |
| CloudWatch Logs | ~$1-2 |
| S3 + CloudFront | ~$0 |
| **合計** | **~$3** |

## 実装のポイント

### 1. OTelデータの受信：protobufデコード

Claude Codeは `OTEL_EXPORTER_OTLP_PROTOCOL` の設定に関わらず、常に **protobuf形式** でテレメトリデータを送信します。当初JSON形式を期待していたため、Lambdaでパースエラーが発生しました。

`@opentelemetry/otlp-transformer` パッケージに含まれるprotobuf定義を利用してデコードしています。

```
// lambda/collector/proto-decoder.mjs
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const root = require('@opentelemetry/otlp-transformer/build/src/generated/root.js');

const ExportLogsServiceRequest = root.opentelemetry.proto.collector.logs.v1.ExportLogsServiceRequest;

export class JsonCollectorExporter {
  static decode(buffer, path) {
    if (path.includes('/v1/logs')) {
      const decoded = ExportLogsServiceRequest.decode(buffer);
      return ExportLogsServiceRequest.toObject(decoded, {
        longs: String, bytes: String, defaults: true,
      });
    }
    // ...metrics も同様
  }
}
```

### 2. Claude Code OTelで取得できるデータ

Claude Codeが送信するテレメトリには以下が含まれます：

| イベント | 主なフィールド |
| --- | --- |
| `claude_code.session.count` | セッション開始 |
| `claude_code.user_prompt` | プロンプト送信（本文はREDACTED、文字数のみ） |
| `claude_code.api_request` | model, input\_tokens, output\_tokens, cost\_usd, duration\_ms |
| `claude_code.tool_decision` | ツール実行判断 (accept/reject) |
| `claude_code.tool_result` | ツール実行結果 |

コストやトークン数が直接取れるのは `api_request` イベントです。

### 3. claude.aiのトークン推定

claude.aiのWeb版はOTelに対応しておらず、Admin APIでもトークン量を取得できません。唯一のデータソースは**エクスポート機能**（設定 → データをエクスポート）で取得できるZIPファイルです。

エクスポートデータにはトークン数が含まれないため、テキストの文字数から推定しています。

```
// 日本語中心なので 1文字 ≈ 1.5トークン で推定
const estimatedInputTokens = Math.round(humanChars * 1.5);
const estimatedOutputTokens = Math.round(assistantChars * 1.5);
```

エクスポートの `conversations.json` には全会話が含まれ、`account.uuid` と `users.json` を突き合わせることでユーザー別の集計が可能です。

### 4. CloudWatch Logs Insightsのハマりポイント

CloudWatch Logs Insightsを分析基盤として使う際、いくつかハマりポイントがありました。

**14日以上前のタイムスタンプはインデックスされない**

`PutLogEvents` のタイムスタンプに過去日付を指定すると、`filter-log-events` では取得できるのに Logs Insights ではヒットしません。claude.aiのエクスポートデータは過去の会話を含むため、タイムスタンプは現在時刻で記録し、JSON本文の `conv_date_num`（YYYYMMDD形式の数値）で期間フィルタする設計にしました。

**`type` フィールドが予約語と競合**

```
filter type = "claude_ai_conversation"  // → マッチしない
filter @message like "claude_ai_conversation"  // → OK
```

JSONの `type` キーは Logs Insights の予約語と競合するようで、`filter type = "..."` が動作しません。`@message like` で回避しました。

**文字列の >= 比較が動作しない**

```
filter created_at >= "2026-03-01"  // → マッチしない
filter conv_date_num >= 20260301   // → OK（数値比較）
```

ISO 8601形式の文字列に対する `>=` 比較が期待通りに動作しないため、YYYYMMDD形式の数値フィールドを別途用意して数値比較しています。

### 5. ダッシュボードの動的データ取得

当初は日次でLambdaが静的HTMLを生成するだけの構成でしたが、期間フィルタの要件に対応するため、CloudFront経由でLambda APIを叩く構成に拡張しました。

```
ブラウザ → CloudFront (/api?days=30) → Lambda Function URL
  → CloudWatch Logs Insights クエリ → JSON返却
```

HTMLはChart.jsを使ったSPA的な構成で、期間ボタンを押すとfetchでAPIを叩いてチャートを再描画します。

### 6. メンバーへの設定配布

各メンバーの `~/.claude/settings.json` に `env` ブロックを追加するだけです。管理者権限不要で、各自が設定できます。

```
{
  "env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "OTEL_METRICS_EXPORTER": "otlp",
    "OTEL_LOGS_EXPORTER": "otlp",
    "OTEL_EXPORTER_OTLP_PROTOCOL": "http/json",
    "OTEL_EXPORTER_OTLP_ENDPOINT": "https://<your-collector-url>",
    "OTEL_RESOURCE_ATTRIBUTES": "user.email=<メールアドレス>"
  }
}
```

プロンプトの本文は収集されません（文字数のみ）。

## インフラ構成（CDK）

AWS CDK (TypeScript) で全リソースを管理しています。主なリソース：

* Lambda × 4（Collector, Dashboard Generator, Claude AI Processor, Claude AI API）
* CloudWatch Logs × 2
* S3 × 2（ダッシュボードホスティング, ZIPアップロード）
* CloudFront × 1（Basic認証 + URLリライト + API/S3ルーティング）
* EventBridge × 1（日次スケジュール）

Basic認証の資格情報は `cdk.context.json`（git管理外）から読み込む設計で、リポジトリに機密情報を含みません。

## まとめ

| 項目 | 内容 |
| --- | --- |
| 対象 | Claude Code (OTel) + claude.ai (エクスポート) |
| 月額コスト | ~$3 |
| IaC | AWS CDK (TypeScript) |
| 可視化 | Chart.js + 静的HTML (S3 + CloudFront) |
| 認証 | CloudFront Functions + Basic認証 |
| 対応チーム規模 | 10人程度（スケール可能） |

公式ダッシュボードでは見えないチームの利用状況が可視化でき、「誰がどのモデルをどれくらい使っているか」が一目で分かるようになりました。Teamsプランを利用しているチームで、利用量の把握に困っている方の参考になれば幸いです。
