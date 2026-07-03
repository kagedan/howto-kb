---
id: "2026-07-03-datadog-cloudwatch-metric-streams-でメトリクスを高速化-コスト削減-01"
title: "Datadog × CloudWatch Metric Streams でメトリクスを高速化 & コスト削減した話"
url: "https://zenn.dev/socialplus/articles/ada79030bb7b8c"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "zenn"]
date_published: "2026-07-03"
date_collected: "2026-07-04"
summary_by: "auto-rss"
query: ""
---

こんにちは、4月にソーシャルPLUSに入社した三口です!

Datadog では、AWS CloudWatch のメトリクスを取り込む方式として、デフォルトで API Polling が利用されます。この方式は約10分ごとにメトリクスを取得するため、実際のメトリクスとの間に少々遅延が発生してしまいます。

そこで今回、メトリクスの遅延を最小限に抑えられる Metric Streams へ移行したため、その内容について紹介します!

## 導入背景

API Polling によるメトリクスの遅延により、以下のような課題がありました。

* Datadog でダッシュボードを作成していたものの、メトリクスの遅延が大きく、鮮度の高いメトリクスを確認できなかった。そのため、CloudWatch にもダッシュボードを作成し、メトリクスを確認していた
* Datadog Monitor（アラート）を作成しているものの、メトリクスの遅延が大きいことから、アラートの検知が遅れる場面があった

## 懸念と回避策

一方で、Metric Streams の導入には、コスト増加の懸念もありました。実際、Datadog の公式ドキュメントにもコスト増加の可能性が明記されており、過去に一度移行が検討されていましたが、コスト増加への懸念から見送られていました。

[課金](https://docs.datadoghq.com/ja/integrations/guide/aws-cloudwatch-metric-streams-with-kinesis-data-firehose/?tab=cloudformation#%E8%AA%B2%E9%87%91)

> AWS は、CloudWatch メトリクスストリームのメトリクスアップデートの数および Amazon Data Firehose に送信されたデータ量に基づいて課金します。そのため、ストリーミングしている特定のメトリクスに関して CloudWatch コストが増加する可能性があります。

しかし、このコスト増加については、Metric Streams 特有のメトリクス取得方法によって、回避どころか削減できる可能性があります!

API Polling では、サービス単位でしかメトリクスの取得を制御できません。そのため、例えば ALB で1つでも取得したいメトリクスがある場合は、ALB 全体のメトリクスを取得する必要があります。一方 Metric Streams では、一部のメトリクスのみ必要なサービスについては、必要なメトリクスだけを取得できます。これにより、コスト増加を回避できるだけでなく、削減につながる可能性があるのです。（今回実際にコスト削減に成功しました✌️）

## 実装

### Terraform による構築

Metric Streams を導入するために、以下のリソースを Terraform で作成しました。実装コード全体の紹介は割愛しますが、Datadog の AWS Integration から、CloudFormation のスタックが辿れるので、Claude Code にそのテンプレを Terraform に読み替えるようにお願いし、弊社の環境にあった Terraform のコードを作成してもらいました。

![](https://static.zenn.studio/user-upload/a2773cff8585-20260703.png)

導入時の懸念でもあったコスト増加については、以下のように、メトリクス単位で取得するサービスと、サービス全体のメトリクスを取得するサービスとで設定を分けることで対応しました。弊社の環境では、EKS で利用している EC2 と RDS のメトリクス取得にコストがかかることが分かったため、それ以外のサービスはサービス全体のメトリクスを取得し、EC2 と RDS のみメトリクス単位で取得するようにしています。（EC2 などの Datadog Agent を導入しているホストであれば system メトリクスを取得できます。そのため、それらのメトリクスで代替できるものについては、CloudWatch から取得するメトリクスをさらに減らせる可能性があります。）

terraform

```
# ----------------------------------------------------------------------------
# CloudWatch Metric Stream
# ----------------------------------------------------------------------------

resource "aws_cloudwatch_metric_stream" "datadog_metrics_stream" {
  name          = "datadog-metrics-stream"
  role_arn      = aws_iam_role.datadog_metric_stream_role[0].arn
  firehose_arn  = aws_kinesis_firehose_delivery_stream.datadog_metrics_stream[0].arn
  output_format = "opentelemetry1.0"

  # サービスの全メトリクスを送信する
  include_filter {
    namespace = "AWS/ApplicationELB"
  }
  include_filter {
    namespace = "AWS/ElastiCache"
  }
  include_filter {
    namespace = "AWS/Firehose"
  }
  ...

  # EC2: コストを抑えるため、必要なメトリクスのみ取得する。
  include_filter {
    namespace = "AWS/EC2"
    metric_names = [
      # Status Check (可用性)
      "StatusCheckFailed",
      "StatusCheckFailed_Instance",
      "StatusCheckFailed_System",
      ...
    ]
  }

  # RDS: コストを抑えるため、必要なメトリクスのみ取得する。
  include_filter {
    namespace = "AWS/RDS"
    metric_names = [
      # CPU / Memory
      "CPUUtilization",
      "FreeableMemory",
      # 接続・セッション
      "DatabaseConnections",
      ...
    ]
  }
```

### メトリクス単位で取得する際のポイント

メトリクス単位で取得対象を絞る場合、どのメトリクスを残すかを決める必要があります。今回は、既存のダッシュボードや Monitor で利用しているメトリクスを Datadog MCP で洗い出し、その結果をもとに Claude Code に Terraform の `metric_names` 候補を整理してもらいました。これを手作業で一つずつ確認するとかなり時間がかかっていたと思うので、このあたりは AI の恩恵を受けられています 🤖

また、導入当初は、すべてのサービスで必要なメトリクスだけを取得し、さらなるコスト削減を図ることも考えました。しかしその分、メトリクスのメンテナンスコストが増加します。また、今は不要と思われるメトリクスでも、後から過去の状況を確認するために必要になることもあります。そのため、まずは広めにメトリクスを取得し、コストへの影響を見ながら必要に応じて絞り込んでいくのがよいと思います。そもそもリソース数が少ないサービスは、メトリクス数も少なく、メトリクス単位で取得することによるコスト削減効果も小さいため、サービス全体のメトリクスを取得してしまって問題ないと個人的には思っています 💪

### 実装時に確認したポイント

実装を進める中で、いくつか疑問点がありました。Datadog サポートへ確認しながら進めたため、その Q&A も紹介します。

#### Q1. AWS Integration のタグフィルタは Metric Streams にも適用されるか

A. 適用される

* AWS Integration に設定したタグフィルタは、 Metric Streams にも適用される
* つまり、タグフィルタに一致するリソースのみメトリクスが取り込まれる

EC2 の Infra Host を管理している方であればご存じかもですが、AWS Integration のタグフィルタを設定することで、Infra Host の収集対象となる EC2 インスタンスを制御できます。例えば、EC2 に `Datadog:Monitored` のタグを付与し、そのタグが付いたインスタンスのみを収集対象とすることができます。実装時に気になったのは、このタグフィルタが Metric Streams にも適用されるのかということでした。（Metric Streams になると、すべての EC2 インスタンスのメトリクスが収集されるかもという懸念がありました。）結果として、Infra Host と同様にタグフィルタが適用され、一致したリソースのメトリクスのみが取り込まれることを確認できました。

#### Q2. Metric Streams でメトリクスを絞った場合、対象外のメトリクスは API Polling で取得されるか

A. 取得されない

* Metric Streams で取得対象外としたメトリクスは、API Polling でも取得されない
* Metric Streams の対象サービスでは、メトリクス取得用の API Polling が自動的に停止する
* つまり、対象外のメトリクスは Stream にも Polling にも流れない

公式ドキュメントには、Metric Streams を有効化した後も、AWS Integration はタグやメタデータを取得するために有効のまま運用すると記載されています。

[API ポーリングからメトリクスストリームへの切り替え](https://docs.datadoghq.com/ja/integrations/guide/aws-cloudwatch-metric-streams-with-kinesis-data-firehose/?tab=cloudformation#api-%E3%83%9D%E3%83%BC%E3%83%AA%E3%83%B3%E3%82%B0%E3%81%8B%E3%82%89%E3%83%A1%E3%83%88%E3%83%AA%E3%82%AF%E3%82%B9%E3%82%B9%E3%83%88%E3%83%AA%E3%83%BC%E3%83%A0%E3%81%B8%E3%81%AE%E5%88%87%E3%82%8A%E6%9B%BF%E3%81%88)

> API ポーリングメソッドを通じて特定の CloudWatch ネームスペースのメトリクスを既に受け取っている場合、Datadog は自動的にこれを検出し、ストリーミングを開始するとそのネームスペースのメトリクスポーリングを停止します。Datadog は引き続き API ポーリングを使用して、ストリームされたメトリクスに対してカスタムタグや他のメタデータを収集するため、AWS インテグレーションページの構成設定は変更しないままにしておきます。

つまり、Metric Streams を有効化した後も、AWS Integration は無効化せず、有効化のままにしておく必要があります。そこで気になったのが、Metric Streams で取得するメトリクスを絞った場合の挙動です。例えば、`AWS/EC2` を Metric Streams の対象とし、`CPUUtilization` のみを取得する設定にした場合、指定していない `CPUCreditUsage` などのメトリクスは、API Polling 側で従来どおり取得されるのではないか（それによって、API Polling 側の課金が発生するのではないか）という懸念がありました。しかし、Metric Streams の対象となったサービスではメトリクス取得用の API Polling が停止するため、フィルタ外のメトリクスも API Polling で取得されることはないということでした 😌

#### Q3. OpenTelemetry の出力フォーマットのバージョンは v0.7 と v1.0 のどちらが推奨か

A. v1.0

日本語版の公式ドキュメントでは、OpenTelemetry v0.7 出力フォーマットのみをサポートしていると記載されているのですが、英語版の公式ドキュメントでは、最新バージョンは v1.0 であり、v0.7 はサポートされているものの、メトリクスが欠落する可能性があると記載されています。

[Amazon Data Firehose を使用した AWS CloudWatch メトリクスストリーム](https://docs.datadoghq.com/ja/integrations/guide/aws-cloudwatch-metric-streams-with-kinesis-data-firehose/?tab=cloudformation)

> 注: Datadog へのメトリクスストリーミングは現在、OpenTelemetry v0.7 出力フォーマットのみをサポートしています。

[AWS CloudWatch Metric Streams with Amazon Data Firehose](https://docs.datadoghq.com/integrations/guide/aws-cloudwatch-metric-streams-with-kinesis-data-firehose/?tab=cloudformation)

> Note: Metric streaming only supports OpenTelemetry output format. Latest version is v1.0; v0.7 is supported but may result in missing metrics.

サポートに確認したところ、現時点では v1.0 を利用することが推奨とのことでした。（先ほど紹介した Terraform コードでも v1.0 を設定しています。）

## 導入の効果

### メトリクスへの効果

メトリクスが届く速さは10分から2〜3分ほどに短縮されました ✨  
![](https://static.zenn.studio/user-upload/753d0da82859-20260701.png)  
*Before*

![](https://static.zenn.studio/user-upload/8cfbc12a8024-20260701.png)  
![](https://static.zenn.studio/user-upload/816f6bd8e1b1-20260701.png)  
*After*

これにより、ダッシュボードで鮮度の高いメトリクスを確認できるようになりました。

また、メトリクスの遅延短縮にあわせて Datadog Monitor の設定も見直しました。AWS メトリクスを参照している Monitor の `evaluation_delay` を `900s` から `180s` に短縮し、 `last_1h` と長めに設定していた評価ウィンドウも `last_5m` を中心に短縮することで、アラートの検知遅延を改善しています。

### コストへの効果

Datadog へのメトリクス送信に関わるリソースタイプに絞った料金なのですが、切り替え後は約40％ほどの削減に成功しました ✨  
![](https://static.zenn.studio/user-upload/ab98776663f7-20260626.png)

## まとめ

今回は、Datadog のメトリクスを API Polling から Metric Streams へ移行した内容を紹介しました!

Metric Streams は「コストが増加しそう」というイメージがありましたが、メトリクス単位でのフィルタリングを活用することで、むしろコスト削減につながる可能性があります。実際に弊社でも約40%のコスト削減を実現できました。また、メトリクスの遅延も10分から2〜3分に短縮され、Datadog のダッシュボードや Monitor をより実用的に使えるようになりました。

導入時に悩んだポイントとして、タグフィルタの適用範囲や API Polling との併用挙動など、ドキュメントだけでは分かりにくい部分がありました。同じところで迷っている方の参考になれば嬉しいです!
