---
id: "2026-04-18-aws-bedrockとclaudeだけで一次オンコールを自動化する話-terraformで予算30-01"
title: "AWS BedrockとClaudeだけで一次オンコールを自動化する話 — Terraformで予算30USD以内に組む障害検知エージェント"
url: "https://zenn.dev/okamyuji/articles/aws-bedrock-claude-incident-response"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-18"
date_collected: "2026-04-19"
summary_by: "auto-rss"
query: ""
---

## はじめに

システム運用において、夜間や休日に発生する一次オンコールは、オンコール担当者の認知負荷が高い仕事です。アラートを受け取ってから、関連ログの取得、重大度の判定、過去類似事例の参照、関係者への一次連絡までを短時間でこなす必要があります。判定を間違えると、P1級のインシデントを見落としたり、逆にP3級の事象で全員を叩き起こしたりします。

筆者は以前から「この一次トリアージの部分だけでもLLMに任せられないか」と考えていました。そこで、AWS Bedrockで提供される3世代のClaudeモデル（Haiku 4.5、Sonnet 4.6、Opus 4.5）を段階的にルーティングし、CloudWatch Alarmをトリガーに自動で調査とインシデント記録を行うリファレンス実装を作ってみました。

本記事では、その設計意図、実装のポイント、実際にAWSへデプロイして動作検証した際に見つけた落とし穴を整理します。ソースコードは [GitHub](https://github.com/okamyuji/incident-response-agent) で公開しています。

対象読者は次のような方を想定しています。

* AWS環境でのオンコール運用を自動化したいと考えているSREや運用担当者
* Bedrockに興味があるが、実際にIAMとCloudWatchと連携させた構成例を見たい方
* Terraformでマルチサービス構成（VPC、ECS、Step Functions、Lambda、DynamoDB、SNSなど）を一気通貫で組む例を探している方

前提知識として、AWSの基本サービス（VPC、IAM、CloudWatch）の用語と、Terraformによるリソース定義の書き方に目を通したことがある、という程度を想定しています。Bedrockに関する知識は不要です。

## この記事で学べること

* Claude Haiku / Sonnet / Opusをseverityに応じて段階ルーティングする Step Functions の組み方
* CloudWatch Logs Data ProtectionとBedrock Guardrailsを組み合わせた二段マスキングの構成方法
* Lambda関数ごとにモデル単位で権限を絞るIAMポリシーの書き方
* AWS Budgetsと `terraform destroy` を組み合わせたPoC向けの予算ガードレール
* GuardDutyとAWS Configを組み合わせた企業向けのガバナンス層の追加方法
* Haikuに投入するログの事前圧縮でトークン消費を抑える実装テクニック
* Haiku / Sonnet / Opus の3モデル全稼働をカオスアプリから誘発して検証する方法
* 実デプロイで筆者がハマった落とし穴と回避策

## 構築するとどんなメールが届くか

文字で語るよりも、実際の出力を先にお見せします。本システムを動かして障害を検知させると、SRE向けにメールで届く通知は次のような構造化された日本語の分析レポートになります。オンコール担当者は件名だけで重大度を把握でき、本文で一次切り分けに必要な仮説と推奨アクションまで読めるようになっています。

なお、以下に登場する件名プレフィックスの `IRA` は本システム名である「Incident Response Agent」の略記です（リポジトリ名 `incident-response-agent` に由来）。メールクライアント側でのフィルタリングやスレッド化を想定したタ付けです。

### P1 インシデントのメール例

本文は適時省略しています。

```
[IRA][P1] ira-dev-chaos-app で error_log_spike カオステスト実行中、エラーログが
大量発生

インシデント ID: 01KPGZG1VYXXXXX
重大度: P1
概要: ira-dev-chaos-app で error_log_spike カオステスト実行中、エラーログが
大量発生

## Sonnet による仮説
["chaos_type=error_log_spike のカオステストが意図どおり動作しており、
errorlog.js の triggerErrorLogSpike 関数が iteration 0〜49 の計 50 件の
Synthetic error を同一リクエスト処理内で並列/連続スローしたことが、エラーログ
大量発生の直接原因である...",
"error_log_spike テスト実行時のログ量（50 件/リクエスト）が CloudWatch Logs
Insights や Log Group のスループット上限に近接し、ECS タスク上の CloudWatch
Logs エージェント（awslogs ドライバー）がバックプレッシャーを受けてログの
欠損・遅延が発生している可能性がある...",
"カオステストの停止条件または実行スコープが適切に制御されておらず、
error_log_spike が dev 環境の ira-dev-chaos-app 以外のサービスや ECS タスクにも
伝播・影響を与えている可能性がある..."]

## Opus による根本原因
chaos_type=error_log_spike のカオステストが設計どおりに動作し、
triggerErrorLogSpike 関数が 1 リクエスト内で iteration 0〜49 の計 50 件の
Synthetic error を約 4 ミリ秒以内に一括出力したことが、P1 アラート発火の
直接原因。CloudWatch Logs のメトリクスフィルターまたはアラーム閾値が
カオステスト由来のスパイクを実障害と区別できず、誤検知として P1 インシデントが
起票された。実サービス障害ではなく、テスト設計上の想定動作である。

## 推奨アクション
["カオステスト実行時は chaos_type タグを CloudWatch メトリクスフィルターの
除外条件に追加し、テスト由来のエラーログを P1 アラーム対象から除外する",
"error_log_spike テストの iteration 数（現状 50）を見直し、アラーム閾値を
超えない範囲に抑えるか、テスト専用の Log Group へ分離する",
"カオステスト実行前に PagerDuty / Slack 等へ事前通知を行い、オンコール担当が
誤検知と即座に判断できる運用フローを整備する",
"インシデント自動起票ロジックに chaos_type フィールドの有無をチェックする
前処理を追加し、カオステスト由来のログでは P1 起票をスキップする"]

使用モデルチェーン: us.anthropic.claude-haiku-4-5-20251001-v1:0
-> us.anthropic.claude-sonnet-4-6
-> us.anthropic.claude-opus-4-5-20251101-v1:0
```

P1ではHaikuが一次判定を行い、Sonnetが3件まで根本原因の仮説を出し、Opusが時系列を復元して単一の根本原因と具体的な推奨アクションを提示します。この例ではOpusが「これはカオステスト由来の誤検知であり実障害ではない」と明言したうえで、再発防止策としてmetric filterの除外条件追加やテスト専用Log Groupの分離まで提案しています。

### P3 インシデントのメール例

P3は軽微な異常です。Haikuの一次トリアージだけで停止し、SonnetやOpusは呼び出されないため、ノイジーではない通知になります。

```
[IRA][P3] 散発的な 5xx が短期的に観測されたが、継続性は低い

インシデント ID: 01KPH0AABCXXXXX
重大度: P3
概要: 散発的な 5xx が短期的に観測されたが、継続性は低い

(P3 のためトリアージ Haiku のみ実行しました)

使用モデル: us.anthropic.claude-haiku-4-5-20251001-v1:0
```

このように重大度に応じて動員するモデルを自動的に切り替えることで、Haikuだけで済む事象ではOpusの高コストを払わず、真のP1だけにOpusの深掘り分析を集中させられます。件名プレフィックスの `[IRA][P1]` `[IRA][P2]` `[IRA][P3]` でメールクライアント側でのフィルタリングも容易です。

## 用語集

本記事で頻出する用語をあらかじめ整理しておきます。興味がある項目だけ展開してください。

Amazon Bedrock

AWSのマネージド型LLMサービスです。Anthropic、Meta、Amazonなど複数のモデルプロバイダの基盤モデルを単一のAPIで呼び出せます。API呼び出しはCloudTrailに記録され、IAMでモデル単位のアクセス制御もできます。

Claude Haiku / Sonnet / Opus

Anthropicが提供するClaudeファミリーの3モデルです。Haikuは軽量高速で安価、Sonnetは中位の性能とコストのバランス、Opusは最上位モデルで推論能力が高い反面コストも高くなります。本システムでは段階的にエスカレーションして使い分けます。

Cross-region inference profile

Bedrockで最新モデルを利用する際に使う仕組みです。`us.anthropic.claude-haiku-4-5-...` のような `us.` 接頭辞付きIDを指定すると、米国の複数リージョンに負荷分散された推論を単一エンドポイントで呼び出せます。2026年4月時点のClaude 4.x系は、この方式での利用が主流になっています。

CloudWatch Logs Data Protection Policy

CloudWatch Logsのロググループに設定できるマスキングポリシーです。managed data identifiersとしてEmailAddressやCreditCardNumber、AwsSecretKeyなどのプリセットが用意されており、ingest時点で自動的に該当箇所を `****` に置換します。ログの取り出し経路すべてでマスクが効くため、LLMに渡す前段の検疫として使えます。

Bedrock Guardrails

Bedrock呼び出しの入出力に対して、追加のポリシー適用を行う機構です。Sensitive Information Filtersを使うと、プロンプトと応答の両方でPII検出とマスクや拒否ができます。managed data identifiersに加えて、業務固有の識別子を正規表現で追加できます。

Step Functions

AWSのワークフロー制御サービスです。状態遷移をJSONで宣言的に定義でき、各ステップでLambdaやDynamoDB、SNSを直接呼び出せます。本システムではHaikuトリアージ、Sonnet深堀り、Opus根本原因分析の3段階を、severityに応じて条件分岐で振り分ける役割を担います。

Agent Governance Toolkit (AGT)

Microsoftが公開しているOSSのエージェント向けガバナンスポリシーエンジンです。OWASP Agentic Top 10のリスクをカバーできます。本システムではECS Fargate上にサイドカーとして配置し、Bedrock呼び出しの出口プロキシとして使っています。

Amazon GuardDuty

AWSアカウント全体の脅威検知サービスです。VPC Flow LogsとCloudTrail管理イベントを自動で取り込み、機械学習ベースの異常検知を行います。IAMの異常なアクセスパターン、EC2インスタンスからの外部不審通信、暗号通貨マイニングの痕跡などを finding として出力します。本システムではdetectorを有効化し、severity 7.0以上のfindingsをEventBridgeで既存のSNSトピックへルーティングしています。

AWS Config

AWSリソースの構成変更を時系列で記録し、managed rulesに定義されたコンプライアンス状態を継続評価するサービスです。Terraformで宣言した「あるべき状態」からの手動変更によるドリフトを検知できます。本システムでは `IAM_PASSWORD_POLICY`、`INCOMING_SSH_DISABLED`、`S3_BUCKET_PUBLIC_READ_PROHIBITED`、`EC2_SECURITY_GROUP_ATTACHED_TO_ENI` の4つのmanaged rulesを有効化しています。

severity\_hint

chaos-appの `POST /chaos/p1` エンドポイントがログに埋め込むseverity前段ヒントフィールドです。CloudWatch Logs Metric Filterで即時カウントしてAlarmを発報するほか、Haikuのトリアージ prompt にも「 `severity_hint=P1` があれば必ずP1を返す」というoverrideルールを仕込んでいます。LLMの判断のブレを抑えるsignal伝達の手段として使います。

プリフィルター（prefilter）

Lambda triageのハンドラ内で、CloudWatch Logs Insightsから取得したpino JSONログをHaikuに渡す前に圧縮する純関数です。SREトリアージに必要なsignalフィールド (level, chaos\_type, status\_code, pii\_flag, severity\_hint など) のみ抽出し、stackは先頭3行、msgは240文字で切り詰めます。同じログ件数でもトークン消費を約7割削減できます。

## モチベーション

この節では、一次オンコール業務を3ステップに分解し、それぞれを適切な世代のClaudeモデルに割り当てるというアプローチの全体像を説明します。PagerDutyやDatadog、Zabbixのような監視スタックとの関係性にも触れます。

一次オンコールの自動化という言い方をすると大げさに聞こえますが、やりたいことは実はシンプルです。アラートが飛んだときに次の3つを自動で処理できれば、オンコール担当者の負荷が下がります。

1. 直近のログと状態を取得して、アラートの重大度を暫定判定します
2. 重大な場合は関連ログの相関分析と原因仮説を立てます
3. 最重要インシデントについてはさらに踏み込んだ根本原因分析を行い、インシデントDBに記録してメール通知します

この3ステップを3つのClaudeモデルに割り当てると、コストと精度のバランスが取れます。軽量なHaikuで全アラートを一次判定し、重要度が上がった場合のみSonnetやOpusを呼び出します。PagerDutyやDatadog、Zabbixのような専用監視スタックにはそれぞれ強みがあります。ノイズ抑制やオンコールローテーション管理、ポストモーテム機能などは既存サービスのほうが遥かに成熟しています。本システムは、既存スタックと対立するものではなく、CloudWatch配下のAWSネイティブ環境だけで一次トリアージ部分を組みたい場合の選択肢として位置付けています。既存のPagerDutyを併用する場合は、本システムのSNS通知先をPagerDutyのイベントエンドポイントに差し替えるだけで連携できます。

!

このセクションで押さえた内容は次の通りです。

* 一次オンコールの自動化は、トリアージ、深堀り、根本原因分析の3段階に分解できます
* 3段階に3世代のClaudeモデルを当てると、コストを抑えつつ必要精度を確保できます
* 本システムは既存監視スタックとの対立構造ではなく、一次トリアージ層の選択肢として補完的にも使えます

## 全体像

この節では、リソース配置と処理フローの2つの視点から全体像を示します。AWS構成図はリソースの空間的な配置を、mermaid図は時系列の流れを表します。

AWS上での実際の配置は次のようになります。

![Incident Response AgentのAWS構成図](https://static.zenn.studio/user-upload/deployed-images/4c863584313c0f9fa42c5b7f.png?sha=e2c1ccffd3486c74962af0ae79beea4e151b0ad6)

主要コンポーネントの役割を本文にも整理しておきます。

* chaos-appは障害サンプルを発生させるECS Fargateサービスで、public subnetのALB経由でトラフィックを受け取ります。5種類の通常障害に加えて、Opusまでエスカレーションさせるための `POST /chaos/p1` エンドポイントも公開しています
* agt-sidecarはBedrock呼び出しの出口プロキシとして動作するECS Fargateサービスで、private subnetに配置します
* CloudWatch Logsはchaos-appのログを受け取り、Data Protection Policyでingest時点のマスクを担います
* CloudWatch Alarmは4系統のメトリクスに加えて、 `severity_hint=P1` のログ出現をMetric Filterで検知する5本目のAlarmも持っています
* EventBridgeはAlarm状態遷移とGuardDuty findingsの両方をStep Functionsやメール通知にルーティングします
* Step Functionsは3段階のLambda（triage / investigate / RCA）をseverityに応じて条件分岐で呼び分けます。Persistノードは3分岐してP1/P2/P3それぞれのmodel\_chainをDynamoDBに記録します
* Lambda triageはHaiku 4.5で一次トリアージを行い、log prefilterで入力トークンを約7割削減します。Lambda investigateはSonnet 4.6で仮説提示を行い、Lambda RCAはOpus 4.5で根本原因分析を行います
* DynamoDBはインシデントレコードを保管し、SNS Topicはメール通知を担います
* AWS Budgetsは月次30 USDのソフトリミットで、Amazon Bedrockはcross-region inference profile経由で呼び出されます
* GuardDutyはアカウント全体の脅威検知を担い、severity 7.0以上のfindingsをEventBridge経由でSNSにルーティングします
* AWS Configはmanaged rules 4個を常時評価し、Terraformで宣言した状態からのドリフトを検知します。Config本体の通知はコンソールダッシュボードで確認する運用とし、SNSへの連携は切ってメール爆撃を防いでいます

システム全体は次の流れで動きます。

ログは最初にCloudWatch Logs Data Protectionで機密情報がマスクされます。マスク済みログをStep Functionsの各Lambdaが取得し、AGTサイドカーを経由してBedrockを呼び出します。AGTサイドカーはOWASP Agentic Top 10の違反を検知したら403で拒否する出口プロキシとして機能します。判定結果はDynamoDBに記録され、SNSでメール通知されます。

Bedrock呼び出しの段階で、Guardrailsが入出力の両方に追加のマスクと拒否を適用します。ログ層とGuardrails層の二段構えでマスクを効かせることで、PIIが推論経路に流れ込む前に除去できます。

!

このセクションで押さえた内容は次の通りです。

* 監視対象アプリのログはまずCloudWatch Logs Data Protectionでマスクされます
* CloudWatch AlarmがEventBridge経由でStep Functionsを起動する形の疎結合な起動経路になっています
* Bedrock呼び出しはAGTサイドカー経由で行い、GuardrailsとAGTポリシーの2層で入出力を検査します

## 設計の柱

この節では、本システムの設計を支える5つの柱について、なぜそう設計したかの根拠を添えて説明します。段階ルーティング、二段マスキング、予算ガードレール、再現可能な動作検証環境、企業向けガバナンス機能の5点を順に扱います。

本システムの設計には5つの柱があります。

### 柱1 モデルの段階ルーティング

最初からOpusを全アラートに投げるとコストが跳ねます。Step Functions内でseverityの値に応じて条件分岐させ、次のように振り分けます。

* 全アラートはまずHaiku 4.5でトリアージします
* severityがP2以上のときだけSonnet 4.6で深堀りします
* severityがP1のときだけOpus 4.5を呼び、Prompt Cachingを有効化して同一障害の再掘り下げコストを抑えます

IAM Roleは関数ごとに専用のものを作り、Bedrock呼び出し可能なモデルIDを明示的に限定します。triage用のロールはHaikuのみを許可し、RCA用のロールはOpusのみを許可します。これにより、Lambdaのコード側で何らかの不具合が起きても、他のモデルを誤って呼び出すことはありません。

### 柱2 二段マスキング

インシデント調査に使うログには、ユーザー情報、メールアドレス、トークン類などの機密が含まれる可能性があります。これらをLLMに渡す前に除去する必要があります。

本システムでは次の2ヶ所でマスクをかけます。

1. ログ層では、CloudWatch Logs Data Protection Policyをロググループ単位で有効化します。managed data identifiersとして `EmailAddress` や `CreditCardNumber`、`AwsSecretKey` などを指定し、ingest時点で自動マスクを有効にします
2. 推論層では、Bedrock GuardrailsのSensitive Information Filtersを使い、プロンプトと応答の両方に追加のマスクと拒否を適用します

ingest時点のマスクと、推論経路のマスクが別々に動くため、どちらか一方で見落としても、もう一方で拾える二段構えになります。

### 柱3 予算ガードレール

PoC用途ではAWS Budgetsを使った上限監視が必須です。Bedrock Agentは1クエリで内部複数コールを踏むケースがあるため、意図せずトークン消費が跳ねることがあります。

本システムではAWS Budgetsに月次30 USDのしきい値を設定し、50パーセント、80パーセント、100パーセントの3段階でメール通知します。Budgetsはソフトリミットなので自動停止はしませんが、通知を受けたら `scripts/destroy.sh` を走らせることで、全リソースをTerraformで一括削除できます。

### 柱4 再現可能な動作検証環境

Claudeによる障害検知を評価するには、本物の障害を意図的に起こす必要があります。そのため、Node.jsとTypeScriptで5種類の障害を再現できるchaos-appを用意しました。

* HTTP 5xxをランダムに返却します
* レスポンス遅延のスパイクを発生させます
* 大きなバッファ確保によるOOMクラッシュを起こします
* 外部API呼び出しのDNS解決失敗を再現します
* ERRORレベルのログを急増させます

バックグラウンドで5〜10分ごとにランダム発生するモードと、 `POST /chaos/{type}` エンドポイントで手動発動するモードの両方を持っています。CI的に毎回同じ障害を再現できるため、プロンプト調整やモデル交換時のリグレッションテストに使えます。

### 柱5 企業向けガバナンス機能

社内向けに展開する場合、一次トリアージの自動化だけでは不十分です。少人数の検証から全社展開へ広げる途中で、構成の手動変更と脅威検知の2方向からリスクが顕在化します。本システムでは次の2サービスを最小構成で組み込んでいます。

1. GuardDutyのdetectorを有効化し、既存の VPC Flow LogsとCloudTrail管理イベントをsourceとして取り込みます。finding\_publishing\_frequencyを `FIFTEEN_MINUTES` に設定し、severity 7.0以上のfindingsを EventBridge経由で既存のインシデント用SNSに流し込みます。Malware ProtectionやS3 Logs保護はdevではコストが跳ねるため無効のままです
2. AWS Configのconfiguration\_recorderとdelivery\_channelを有効化し、managed rulesを4個だけ登録します。`IAM_PASSWORD_POLICY`、`INCOMING_SSH_DISABLED`、`S3_BUCKET_PUBLIC_READ_PROHIBITED`、`EC2_SECURITY_GROUP_ATTACHED_TO_ENI` の4本です。Terraformで宣言した「あるべき状態」からAWSコンソールでの手動変更が入った瞬間に、ドリフトとして可視化できます

Configは既にdev環境で別プロジェクトが有効化している可能性があるため、 `variable "enable_config"` でモジュール単位でskipできる設計にしています。GuardDutyも同じく `enable_guardduty` で制御できます。既存detectorがアカウントにある場合はfalseにして既存を使い続けます。

社内向けガバナンスを強化する方向は、Security Hub、Inspector、IAM Access Analyzerなどに広げる余地があります。ただし、フルセットで入れると初期セットアップ費用が跳ねるため、本システムでは脅威検知のGuardDutyと構成ドリフト検知のConfigに絞っています。これだけでもBedrockの少人数開放から段階的に社内展開していく際のベースラインとして機能します。

!

このセクションで押さえた内容は次の通りです。

* 段階ルーティングはStep FunctionsのChoice stateで条件分岐させ、IAMでモデルIDまで固定します
* ログ層と推論層の独立した2層マスキングが、どちらか片方の取りこぼしを相互にカバーします
* AWS Budgetsはソフトリミットですが、`terraform destroy`と組み合わせれば予算超過を人的トリガーで即停止できます
* 再現可能な障害サンプルを持つと、プロンプト調整やモデル交換のリグレッションが回せます
* GuardDutyとAWS Configを最小構成で入れておくと、少人数検証から全社展開への過程で脅威検知と構成ドリフトの両輪を担保できます

## 実装のポイント

この節では、実装時に判断が分かれやすい箇所について、なぜその選択をしたかを示します。pnpmワークスペース、Lambdaのモデル固定IAM、Step Functionsのロギング権限、LocalStackを使ったローカル検証環境、Haikuに渡す前でのログ圧縮、Opusに到達させるためのP1を誘発するエンドポイントの開発、pre-commitでの品質ゲートの7点です。

### pnpmワークスペース構成

リポジトリは次の3つのTypeScriptパッケージで構成されています。

* `apps/chaos-app` はExpressベースの障害発生アプリです
* `apps/agt-sidecar` はExpressベースの出口プロキシです
* `lambda` はBedrock呼び出しLambda 3本の共通パッケージで、tsupで単一ESMファイルにバンドルします

いずれもVitestでテストを書き、pathエイリアス `@/*` でsrc配下を参照します。Vitestの設定で `resolve.alias` を `@/foo.js` と `@/foo` の両方を解決するように書くのがポイントです。TypeScriptのESM規約に従うと `.js` 拡張子付きでimportする必要がある一方、Vitestはsrc配下の `.ts` に解決する必要があるためです。

### Lambdaのモデル固定IAMポリシー

Lambdaごとに呼び出せるBedrockモデルを厳密に制限します。cross-region inference profileを使う場合、IAMポリシーのresource ARNには次の2つを含める必要があります。

```
resources = [
  "arn:aws:bedrock:${var.region}:${var.account_id}:inference-profile/${var.haiku_model_id}",
  "arn:aws:bedrock:*::foundation-model/${var.haiku_base_model_id}"
]
```

前者がinference profileそのもののARNで、後者がprofileが転送する先の基盤モデルのARNです。後者のリージョンはワイルドカードにしておかないと、米国の他リージョンに転送された際にAccessDeniedになります。

### Step Functionsのロギング権限

Step Functionsが実行履歴をCloudWatch Logsに流すには、state machineのIAM Roleに `logs:CreateLogDelivery` 系の8権限が必要です。これが抜けていると、Terraform applyが `The state machine IAM Role is not authorized to access the Log Destination` というエラーで止まります。これらの権限はAWS側の実装都合でresource ARN指定が効かないため、resourcesは `"*"` に設定します。

```
statement {
  actions = [
    "logs:CreateLogDelivery", "logs:GetLogDelivery",
    "logs:UpdateLogDelivery", "logs:DeleteLogDelivery",
    "logs:ListLogDeliveries", "logs:PutResourcePolicy",
    "logs:DescribeResourcePolicies", "logs:DescribeLogGroups"
  ]
  resources = ["*"]
}
```

### ローカル検証環境

LocalStackとmockserverを使ったdocker-compose構成を `local/compose.yml` に用意しています。AWS認証情報が無い状態でchaos-appとagt-sidecarを立ち上げ、curlベースのテストスクリプト `local/local-verify.sh` で9項目の動作確認ができます。

AWSに実デプロイする前にまずローカルで壊れていないことを確認できるため、1日のクラウド課金を抑えながら反復開発ができます。

### Haikuに渡す前のログ圧縮

Haikuの入力トークンは量課金のため、冗長なログをそのまま渡すとコストが跳ねます。本システムではLambda triageの中で、CloudWatch Logs Insightsから取得したpino JSONログにprefilterを適用してからHaikuに渡しています。

```
export function compressLogs(logs: LogSample[]): string {
  return logs.map(compressOne).join('\n');
}
```

`compressOne` は level、chaos\_type、status\_code、pii\_flag、severity\_hintなどのsignalフィールドのみを抽出し、stackは先頭3行、msgは240文字で切り詰めます。`pii_flag=true` のログはmsgを `[redacted]` に置換する多重防御も入れています。同じ40件のログでもトークン消費を約7割削減でき、Haiku呼び出し1回あたり 0.005 USD程度だった入力コストが 0.0015 USD程度まで下がります。

### Opus到達用のP1誘発エンドポイント

3段ルーティングを実稼働させるには、Haikuに必ずP1と判定されるログを投入する必要があります。chaos-appに `POST /chaos/p1` を追加し、`customer-facing outage`、`data loss risk`、`security incident` のうちランダムな1種類を選んで、503応答とともに `severity_hint=P1` をログにemitします。

さらにHaikuのsystem promptに次のoverrideルールを追加しました。

```
CRITICAL OVERRIDE: If ANY log line contains "severity_hint=P1", the system has
already classified this as P1. You MUST return "severity":"P1" in that case.
```

このoverrideを入れる前は、Haikuがmessage本文の具体性からP2判定を返してしまい、Opusまで到達しないケースがありました。severity\_hintをauthoritative扱いにすることで、誘発テストで安定して3モデル完走させられます。

### pre-commitで全workspaceを品質ゲートする

pnpmワークスペースの3パッケージはそれぞれに `format:check`、`lint` (tsc)、`test` (vitest + coverage)、`build` のスクリプトを揃えています。ローカルでのcommit時に全部をまとめて走らせるpre-commitフックを `.githooks/pre-commit` に置き、`git config core.hooksPath .githooks` で有効化します。

```
for ws in apps/chaos-app apps/agt-sidecar lambda; do
  (cd "$dir" && pnpm format:check && pnpm lint && pnpm test && pnpm build)
done
```

commitあたり数十秒から1分弱かかりますが、遅さを受け入れる代わりに「コミットに載っているものは必ず全検証通過済み」という状態を維持できます。整形漏れやビルド失敗がmainに混入しないため、CI側での手戻りが減ります。

!

このセクションで押さえた内容は次の通りです。

* pnpmワークスペースでchaos-app、agt-sidecar、lambdaの3パッケージを独立したテストとビルドサイクルに保ちます
* Lambda IAMはcross-region inference profileのARNと foundation-modelのARNの両方をresourcesに含める必要があります
* Step Functionsのlogs:CreateLogDelivery系権限は resource ARN指定が効かないため wildcard にします
* LocalStack + mockserverのdocker-compose構成で、AWSへ出る前にローカルで9項目の動作確認ができます
* Haiku入力前のログprefilterでトークン消費を約7割削減し、severity\_hintヒントでLLM判断のブレを抑えます
* P1レベルの障害を発生させるエンドポイントを実装することで、Opusが呼び出すようになり、PoC段階でも確実にP1レベルでの運用検証が行えます
* pre-commi フックで全workspaceのformat / lint / test / buildを完全実行する厳密版を採用します

## 実デプロイで見つけた落とし穴

この節では、本記事の核となる落とし穴を扱います。CloudWatch Alarmのdimensions忘れ、ALBの2 AZ必須要件、Bedrockモデル有効化UIの2026年仕様変更、AWS ConfigのSNSメール爆撃、CloudWatch Metric Filterのlog\_group先行作成要件、Haikuのseverity判定の揺れの6点です。いずれもTerraform validateは通るのに、実AWSで動かすまで気付けない種類の問題です。

Terraformでの構成検証が通っていても、実AWSで動かしてみると思わぬ挙動に遭遇します。筆者が2026年4月にus-east-1へデプロイした際に遭遇した落とし穴を紹介します。

### 落とし穴1 CloudWatch Alarmのdimensions忘れ

本システムの心臓部はCloudWatch Alarmです。ここが発火しなければStep Functionsも起動せず、何も動きません。

初回デプロイ後、chaos-appに15回ほどHTTP 5xxを叩き込んでもアラームがALARM状態に遷移しませんでした。原因はTerraformの `aws_cloudwatch_metric_alarm` リソースにdimensionsを書き忘れていたことです。

CloudWatch上のELBやECSのメトリクスは、必ずLoadBalancerやClusterNameなどのディメンション付きで発行されます。dimensionsを指定しないアラームは、メトリクスが届いていても一切マッチしません。aws cliで `describe-alarms` すると、StateReasonに `"no datapoints were received"` と表示され続けます。

修正は次のようにdimensionsを明示するだけです。

```
resource "aws_cloudwatch_metric_alarm" "http_5xx" {
  metric_name = "HTTPCode_Target_5XX_Count"
  namespace   = "AWS/ApplicationELB"
  dimensions = {
    LoadBalancer = var.alb_dimension
  }
}
```

ALBのdimension文字列はARNから正規表現で切り出します。

```
output "alb_dimension" {
  value = regex("(app/[^/]+/[^/]+)$", aws_lb.chaos.arn)[0]
}
```

### 落とし穴2 ALBの2 AZ必須要件

コスト最適化のためにSingle-AZ構成でVPCとNAT Gatewayを1本に絞ろうとしたら、ALB作成で失敗しました。

```
ValidationError: At least two subnets in two different Availability Zones must be specified
```

ALBは可用性要件から最低2 AZのサブネットを要求します。private subnetは1 AZに絞れますが、public subnetは2 AZに分けざるを得ません。NAT Gatewayを2本にするとコストが増えるので、本実装ではpublic subnetのみ2 AZ、private subnetとNAT Gatewayは1 AZに留める構成を取りました。

### 落とし穴3 Bedrockモデル有効化UIの変遷

2026年時点でBedrockコンソールの「Model access」ページは廃止されています。モデル一覧の画面を開くと次のメッセージが表示されます。

```
Model access page has been retired
Serverless foundation models are now automatically enabled across all AWS commercial regions
when first invoked in your account.
```

つまり、初回呼び出し時に自動で有効化される方式に変わりました。ただしAnthropicモデルは、初回呼び出し前にPlaygroundからuse case details（会社名、利用目的など）を送信する必要があります。これを怠ると実行時に `AccessDeniedException` が返ります。

モデル名の命名規則もモデル間で揃っていません。筆者が確認した2026年4月時点の実値は次の通りです。

* Haiku 4.5は `us.anthropic.claude-haiku-4-5-20251001-v1:0` です
* Sonnet 4.6は `us.anthropic.claude-sonnet-4-6` です
* Opus 4.5は `us.anthropic.claude-opus-4-5-20251101-v1:0` です

Sonnetだけ日付とバージョンsuffixが省略されています。この不揃いを吸収するため、Terraformの変数で各モデルIDを独立に指定できるようにしました。

### 落とし穴4 AWS Config delivery\_channelのSNSメール爆撃

AWS Configの `aws_config_delivery_channel` に `sns_topic_arn` を設定すると、 managed ruleの初回評価でアカウント内の全NON\_COMPLIANTリソース件数だけSNS publishが走ります。筆者のケースでは `EC2_SECURITY_GROUP_ATTACHED_TO_ENI` rule1本だけで、1分間に70通ほどのメール爆撃が起きました。

解決策はdelivery\_channelから `sns_topic_arn`を外すことです。Configの評価結果はコンソールのダッシュボードで十分確認できます。どうしてもSNS通知が必要な場合は、EventBridge Ruleでseverityやrule nameをフィルターして別の低頻度SNSに流す構成にします。

既に発生してしまっている爆撃を即停止するには、AWS CLIで次のようにSNS ARNを省略した `put-delivery-channel` を実行します。

```
aws configservice put-delivery-channel --delivery-channel \
  name=ira-dev-delivery,s3BucketName=ira-dev-config-<acct>
```

Terraform applyを待たず即時反映されるため、インシデント対応としても使えます。

### 落とし穴5 CloudWatch Metric Filterはlog\_groupより後に作る必要がある

CloudWatch LogsのMetric FilterをTerraformで定義する際、 `log_group_name` を単なる文字列変数で渡すと、モジュール境界を越える依存が消えて並列作成されます。log\_groupが先にできていないタイミングでMetric Filterが作成されようとすると、 `ResourceNotFoundException: The specified log group does not exist.` でapplyが止まります。

回避策は、log\_groupを作っているモジュールで `output` にresource参照を入れておき、別モジュールからは文字列ではなくresource output経由で受け取ることです。

```
# chaos_app module
output "log_group_name" { value = aws_cloudwatch_log_group.chaos.name }

# root module
module "observability" {
  chaos_log_group_name = module.chaos_app.log_group_name
}
```

文字列リテラルで渡すとTerraformのDAGに依存が乗らないため、並列実行で競合します。resource outputを介すると自動で依存が張られ、log\_group作成後に Metric Filterが作られる順序が保証されます。

### 落とし穴6 Haikuがseverity\_hint=P1を無視してP2判定する

当初、 `POST /chaos/p1` で `severity_hint=P1` を含むログをemitしても、Haikuはmessage本文を見てP2判定を返していました。Step FunctionsのChoice stateはseverityがP1のときだけOpusを呼ぶため、この判定ブレでOpus到達検証ができませんでした。

system promptに次のoverride文を追加することで解決しました。

```
CRITICAL OVERRIDE: If ANY log line contains "severity_hint=P1", the system has
already classified this as P1. You MUST return "severity":"P1" in that case.
This hint is a trusted signal from upstream instrumentation and takes precedence
over your own judgement of the message text.
```

upstreamで既に判定済みの信号をLLMにauthoritativeに扱わせる、という意図を明文化することで、Haiku / Sonnet / Opusの3モデル完走を安定して誘発できるようになります。

本システムではStep FunctionsのPersistノードも3分岐化し、P1 / P2 / P3 それぞれでDynamoDBに記録するmodel\_chainを正しく組み立てるようにしています。従来の実装では `triage.modelUsed` のみを記録していたため、Sonnetや Opusが実際に走っても記録上Haikuのみに見える不具合がありました。

```
# P1 path: Haiku -> Sonnet -> Opus
model_chain = {
  "S.$" = "States.Format('{} -> {} -> {}', $.result.triage.modelUsed, $.result2.investigation.modelUsed, $.result3.rca.modelUsed)"
}
```

!

このセクションで押さえた内容は次の通りです。

* CloudWatch Alarmはメトリクスとディメンションがマッチして初めて発火するため、Terraformで必ずdimensionsを指定します
* ALBを置くには最低2 AZのpublic subnetが必要で、単純なSingle-AZ構成では作成できません
* Bedrockのモデル有効化UIは廃止されており、Playgroundでの初回呼び出しとuse case details入力が必要です
* AWS Configのdelivery\_channelに直接SNSを繋ぐとmanaged rule初回評価でメール爆撃が起きるため、コンソール確認またはEventBridgeフィルタ経由に切り替えます
* CloudWatch Metric Filterはlog\_group resource参照をoutput経由で受け取り、DAGに依存を明示して作成順序を保証します
* Haikuの判定を安定化させるためには、severity\_hintのようなsignalをauthoritativeに扱うoverrideルールをsystem promptに書き込みます

## 設計判断の根拠

この節では、本システムの設計で迷いやすい3つの判断について、筆者がどう考えて選択したかを示します。他の選択肢の良い点にも触れながら、本システムの位置付けを整理します。

### Step Functionsを使う理由

モデルのルーティングは、LambdaからLambdaを直接呼び出す形でも実装できます。LangGraphやBedrock Agentのマルチエージェント機能を使えば、もっと凝った制御もできます。それでも本システムがStep Functionsを選んでいるのは、severityに応じた条件分岐と実行履歴の可視性の2点を重視したためです。Step Functionsは状態遷移をJSONで宣言的に書けるうえに、AWS Consoleで各実行の入出力を視覚的に追えます。夜間に発火したインシデントを翌朝レビューする際、この可視性が効きます。

### AGTサイドカーを挟む理由

AGTサイドカーは現時点でpublic preview段階であり、本番投入には議論の余地があります。Bedrock Guardrails単体でもSensitive Information Filtersや content filter は効くため、マスキングだけを考えるとAGTは不要とも言えます。それでも本システムが AGTを挟んでいるのは、OWASP Agentic Top 10の観点でエージェント呼び出しの出口に独立した検査層を持ちたい、という設計意図です。Guardrailsはモデル単位の検査、AGTは呼び出し全体の検査、という役割分担で責務を分けています。pure Guardrailsで十分というケースでは、AGTサイドカーを外してNAT経由で直接Bedrockを呼ぶ構成にしても問題ありません。

### Terraformを選んだ理由

AWS CDKやPulumiのほうが Lambda やECS周りの設定はコンパクトに書けます。それでも本記事でTerraformを採用した理由は、読者層の想定とリソースカタログの見通しです。TerraformはHCLの宣言的な表現が IaC 初見の読者にも読みやすく、リソース種別ごとの公式ドキュメントの探しやすさに強みがあります。CDKやPulumiのほうが合う場面もあるため、プロジェクトの背景次第で選択すべきと考えています。

## コストの実績

この節では、設計段階の試算と、実際にus-east-1にデプロイして動作検証した際の実績を併記します。試算の内訳と実績の差分が、設計時の想定がどこまで合っていたかを示します。

試算は3日連続稼働を前提に、us-east-1単価で計算しています。

| 項目 | 試算3日合計 | 備考 |
| --- | --- | --- |
| ECS Fargate 2タスク | $5.21 | 0.25 vCPU / 0.5 GB × 2 |
| ALB 1本 | $2.18 | LCU含む |
| NAT Gateway 1本 | $3.74 | データ処理含む |
| Bedrock Haiku 4.5 50回 | $0.08 | prefilter適用後の実績ベース |
| Bedrock Sonnet 4.6 20回 | $0.93 |  |
| Bedrock Opus 4.5 3回 | $1.05 | Prompt Cache有効 |
| CloudWatch Logs + Data Protection | $0.49 |  |
| GuardDuty (detector) | $0.54 | VPC Flow Logs + CloudTrail source |
| AWS Config (recorder + 4 rules) | $0.28 | dev小規模アカウントで試算 |
| その他 | $0.52 | DynamoDB、SNS、Step Functions、Lambdaなど |
| 合計 | $15.02 | 約2,253円 |

実際に3時間稼働させて検証を行ったときの実績は、合計で約0.55 USD（約80円）でした。追加のGuardDutyとConfigは時間単位では低料金ですが、Configのmanaged rule評価とGuardDutyのfinding処理は検証時間に比例しないため、本番化で年単位運用するときに効いてきます。

検証中のパイプライン発火状況は次の通りでした。

* 通常のランダム障害発火でHaikuがP2判定、Sonnetまで呼ばれた例が1回
* `POST /chaos/p1` 誘発でHaikuがP1判定、Sonnet → Opusまで呼ばれた例が1回

Opus到達1回でRCAトリアージにかかった時間は、Step Functions全体で42秒でした。うちInvestigate（Sonnet）が28秒、RCA（Opus）が10秒強です。Haikuはprefilter適用後の入力でも2.5秒程度でトリアージを完了しており、3モデル段階ルーティングの遅延は現実的な範囲に収まります。

NAT Gatewayが固定コストの主因になるため、本番化する場合はBedrockやS3へのトラフィックはVPC Endpoint経由にしてNATを経由させない設計が有効です。

!

このセクションで押さえた内容は次の通りです。

* 3日連続稼働の試算は合計15.02 USDで、AWS Budgets 30 USDの枠内に収まります
* 実検証では3時間の稼働で約0.55 USDに収まり、3モデル段階ルーティング全稼働でも十分余裕があります
* Opusまで到達した場合のパイプライン総時間は42秒で、運用上問題になる遅延ではありません
* 本番化時のコスト圧縮はNAT Gateway周辺のVPC Endpoint化が最も効きます

## おわりに

本記事ではAWS BedrockとClaudeを組み合わせた障害対応での一次オンコール自動化のリファレンス実装を紹介しました。以下に要点を整理します。

* Step Functionsによる段階ルーティングは、Haikuで広く受けて重要度が高い場合のみSonnetとOpusへ昇格させる構造を、宣言的に表現できます
* CloudWatch Logs Data ProtectionとBedrock Guardrailsの二段マスキングは、独立した2層でPIIの流出を防ぎます
* IAMによるモデルID制限とAWS Budgetsによる予算監視を組み合わせると、PoC段階の暴走を構造的に抑え込めます
* GuardDutyとAWS Configを最小構成で組み込むと、少人数検証から社内展開に広げる途中で脅威検知と構成ドリフト検知の両輪を担保できます
* Haikuに渡す前のログprefilterとseverity\_hintによる信号伝達を組み合わせると、トークンコストを削りつつLLM判断のブレも抑えられます
* 実デプロイでは、dimensions忘れ、ALBの2 AZ要件、Bedrockモデル有効化UIの変化、ConfigのSNSメール爆撃、Metric FilterのDAG 依存、Haikuのseverity判定ブレなど複数の落とし穴に遭遇しましたが、いずれもリポジトリ内のコメントとTerraform定義で再発しないようにしています

構成一式はTerraformで定義してあり、GitHubリポジトリの `scripts/deploy.sh` と `scripts/destroy.sh` を使うと一発デプロイと一発破棄ができます。ローカル検証環境のdocker-compose、5種類の障害を再現するchaos-app、ハマりどころを日本語コメントで残したソースコードも含めています。

AWS環境での一次オンコール自動化に興味がある方は、リポジトリをcloneして手元で試してみてください。Issueや改善提案もお待ちしています。

リポジトリは [GihHub](https://github.com/okamyuji/incident-response-agent) に置いています。設計の詳細は `docs/architecture.md` と `docs/architecture.drawio` に、コスト試算は `docs/cost-estimate.md` に、運用手順は `docs/runbook.md` にまとめていますので、あわせてご覧ください。
