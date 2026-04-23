---
id: "2026-03-23-claude-codeやcoworkの利用ログをdatadogで可視化する-01"
title: "Claude CodeやCoworkの利用ログをDatadogで可視化する"
url: "https://zenn.dev/hacobu/articles/0f0b436bcccf29"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "cowork", "zenn"]
date_published: "2026-03-23"
date_collected: "2026-03-24"
summary_by: "auto-rss"
---

## 背景

こんにちは、株式会社Hacobu プロダクト基盤部の栗山です。

弊社では、生成AIツールの活用を全社的に推進しています。  
その取り組みの中で、社内ではCoworkの利用も急速に浸透してきました。さらに最近では、エンジニアに限らず、非エンジニアのメンバーも自らコードを書いて業務を効率化するなど、職種の垣根を越えたAI活用が広がっています。

このような状況の中で、次のようなニーズが顕在化しました。

* 誰がどれくらいClaude CodeやCoworkを使っているのか把握したい
* コストを可視化したい
* AI活用の成果(例：コード生成量やPR作成量など)を定量的に見たい

上記の課題を解決すべく、Claude Code、CoworkのログやメトリクスをDatadogに送り可視化できるようにしたので、今回はその紹介をします。

## 方針

Claude CodeやCoworkはOpenTelemetryに対応しており、管理画面からの簡単な設定だけで外部のオブザーバビリティ基盤へClaude CodeやCoworkのログやメトリクスデータを送信することできます。

特にClaude Codeについては、単なるログだけでなく以下のようなメトリクスも取得できます。

* 変更されたコード行数
* 作成されたGitコミット数
* 作成されたプルリクエスト数

詳しくは[こちらのドキュメント](https://code.claude.com/docs/en/monitoring-usage#metrics)を参照ください

これらを活用することで、「AIをどれだけ使っているか」だけでなく、Claude Codeを使用して「作成されたPR数」や「変更行数」といった、より具体的なアウトプット指標の集計も可能になります。

弊社では既存のモニタリング基盤としてDatadogを採用しているため、全社のClaude Code、Coworkの利用ログ・メトリクスをDatadogに集約し、可視化することにしました。

## Claude Code の設定

Claude Code は、`組織設定`→`Claude Code`の設定画面から`管理設定（settings.json）`を設定することで一括設定できます。  
<https://claude.ai/admin-settings/claude-code>

`管理設定（settings.json）`とは管理者が配布する優先度の最も高い設定ファイルです。各ユーザーのローカル設定よりも優先されるため、全社員に強制的に適用されるのが特徴です。  
<https://code.claude.com/docs/en/settings>  
設定をすると、`~/.claude/remote-settings.json`というファイルが生成されます。

### Datadog への送信設定

以下の設定を追加することで、ログおよびメトリクスを Datadog に送信できます。

```
{
  "env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY":"1",
    "OTEL_EXPORTER_OTLP_HEADERS":"dd-api-key=<Datadog API Key>",
    "OTEL_EXPORTER_OTLP_LOGS_ENDPOINT":"https://http-intake.logs.datadoghq.com/v1/logs",
    "OTEL_EXPORTER_OTLP_LOGS_PROTOCOL":"http/protobuf",
    "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT":"https://otlp.datadoghq.com/v1/metrics",
    "OTEL_EXPORTER_OTLP_METRICS_PROTOCOL":"http/protobuf",
    "OTEL_LOGS_EXPORTER":"otlp",
    "OTEL_METRICS_EXPORTER":"otlp"
  }
}
```

`<Datadog API Key>`には実際のAPI Keyに置き換えてください。

エンドポイントの詳細に関しては以下を参照ください。

設定後、Datadogのログエクスプローラーにて `service:claude-code` で検索することでログを見ることが出来るようになります。

### 送信されるイベント、メトリクス

送信されるイベント、メトリクスはそれぞれ以下のドキュメントを参照ください  
イベント: <https://code.claude.com/docs/en/monitoring-usage#events>  
メトリクス: <https://code.claude.com/docs/en/monitoring-usage#metrics>

### プライバシーへの配慮

Claude Codeではデフォルトでプロンプトの本文は送信されません。環境変数 `OTEL_LOG_USER_PROMPTS` を `1` に設定すれば本文の取得も可能ですが、弊社では機密情報の保護とプライバシーの観点から、無効(デフォルト状態)のままにしています。

## Coworkの設定

`組織設定` → `Cowork`の`モニタリング`の項目から設定できます。

<https://claude.ai/admin-settings/cowork>

### Datadog への送信設定

設定値は以下の通りです。

* **OTLPエンドポイント:** `https://http-intake.logs.datadoghq.com`
* **OTLPプロトコル:** `http/protobuf`
* **OTLP ヘッダー:** `dd-api-key=<Datadog API Key>`

設定完了後、`service:cowork` でフィルタリングすることで利用ログを確認できるようになります。

### 送信されるイベント

Coworkの場合、Claude Codeと異なりメトリクスは送信されません。送信されるのはイベントのみです。

送信されるイベントは以下のドキュメントを参照ください  
イベント: <https://claude.com/docs/cowork/monitoring#events>

### Coworkのセキュリティ対策

CoworkのOpenTelemetry連携は、現時点(2026年3月現在)ではプロンプトの本文がログに含まれる仕様となっています。  
そのため弊社ではDatadog側のData Access機能を活用し、プロンプトを含むログは特定のRoleを持つメンバーしか閲覧できないように制限をかけて運用しています。

設定画面の場所は  
Logs → Configuration → [Data Access](https://app.datadoghq.com/logs/pipelines/data-access)です。

ドキュメントはこちら  
<https://docs.datadoghq.com/logs/guide/logs-rbac/?tab=ui#restrict-access-to-logs>

## DatadogのAI Agents Console機能について

Datadogには[AI Agents Console機能](https://docs.datadoghq.com/ai_agents_console/)というものがあります。  
AI Agents Console機能を使うと、Claude CodeをはじめとしたAIエージェントツールの使用状況の可視化ができるようです。  
2026/03/23時点でPreview段階なため、弊社ではまだ使用することが出来ていません。この機能を使うと独自にダッシュボードを作成する必要もなくなると思われるので、使えるようになるのを楽しみに待っています。

AI Agents Console機能の紹介記事はこちら

<https://www.datadoghq.com/blog/claude-code-monitoring/>

## まとめ

Claude Code / CoworkのOpenTelemetry機能と、Datadogを活用することによって、設定だけで全社的な利用可視化基盤を構築できました。

特に重要だったポイントは以下です

* Datadogへの直接送信によるシンプルな構成
* managed-settings.jsonによる強制適用(抜け漏れ防止)
* プロンプトログに対する適切なアクセス制御

本記事が、同様の取り組みを検討されている方々の一助となれば幸いです。
