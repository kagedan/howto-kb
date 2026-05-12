---
id: "2026-05-12-claude-platform-on-awsをエンタープライズ企業で利用する上での考慮点とamazo-01"
title: "Claude Platform on AWSをエンタープライズ企業で利用する上での考慮点と、Amazon Bedrockとの違いを知る"
url: "https://qiita.com/nasuvitz/items/d0ad5d691790ff0eca71"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "LLM"]
date_published: "2026-05-12"
date_collected: "2026-05-12"
summary_by: "auto-rss"
query: ""
---

## はじめに
AWSは2026年5月11日、**[Claude Platform on AWSの一般提供開始](https://aws.amazon.com/jp/about-aws/whats-new/2026/05/claude-platform-aws/)を発表**しました。東京リージョンでも利用可能になっています。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/211986/85312e7a-ade9-4f45-afc4-80845f2aa1ab.png)

**Claude Platform on AWS**は、Anthropicが提供するネイティブなClaude Platformを、AWSアカウント、IAM、AWS Marketplace課金、CloudTrail監査ログと組み合わせて利用できるサービスです。

Claude Platform on AWSは「Amazon Bedrock上のClaudeモデルの新機能」ではなく、**AnthropicのClaude PlatformをAWS経由で利用するためのサービス**です。[AWSのプロダクトページ](https://aws.amazon.com/claude-platform/)では、**Claude Platform on AWSはAnthropicが運営し、顧客コンテンツはAWSの境界外でAnthropicにより処理される**と説明されています。一方、Amazon Bedrock上のClaudeはAWSインフラ内で処理され、AWSがデータをAnthropicや第三者と共有しない点が明示されています。

そのため、**Claude Platform on AWSは、Anthropicのネイティブ機能を利用しつつ、調達、課金、アクセス制御、監査をAWSアカウントの機能で実施したいエンタープライズ企業に適した選択肢**です。一方で、データ処理をAWSインフラ内に閉じたい場合や、Amazon BedrockのGuardrails、Knowledge Bases、PrivateLink、複数モデルの統一APIを重視する場合は、Amazon Bedrockの利用を優先して検討する必要があります。

本記事では、Claude Platform on AWSの一般提供開始を受けて、サービスの位置づけ、Amazon Bedrockとの違い、認証・IAM設計、監査、課金、企業利用時の確認ポイントを整理します。

## 発表内容

Claude Platform on AWSは2026年5月11日に一般提供が開始されました。[AWS What's Newの記事に](https://aws.amazon.com/jp/about-aws/whats-new/2026/05/claude-platform-aws/)によると、**ネイティブなClaude Platform体験**へのアクセスを提供する最初のクラウドプロバイダーと説明しています。

ここでいう「ネイティブなClaude Platform体験」とは、Amazon BedrockのAPIとしてClaudeモデルを呼び出すことではなく、**Anthropicが提供するClaude Platformそのものの機能、たとえばClaude Console、Messages API、Managed Agents、Skills、MCP connector、web search、code executionなどに、AWSアカウントを通じてアクセスできる**ことを指しています。つまり、AWSがClaudeモデルのホスティング基盤を提供するというよりも、Anthropicのネイティブな開発者体験を、AWSの購買、IAM、監査、課金の仕組みに接続する点が特徴です。この点が、Amazon Bedrock経由でClaudeを利用する場合との大きな違いになります。

AWSからは複数の記事で今回のClaude Platform on AWSが紹介されていますが、[AWS Machine Learning Blog](https://aws.amazon.com/blogs/machine-learning/introducing-claude-platform-on-aws-anthropics-native-platform-through-your-aws-account/)では、Anthropic側で個別のアカウント管理、請求管理、契約管理、利用状況のトラッキングを行わずに、AWSアカウントからAnthropicのClaude Platformにアクセスできると説明されています。また、認証はAWS IAM、課金はAWS Marketplaceの従量課金、監査はAWS CloudTrailで扱えると整理されています。

発表時点で紹介されている主な機能は次のとおりです。

- Messages API
- Claude Console
- Claude Managed Agents beta
- advisor tool beta
- web search / web fetch
- MCP connector beta
- Agent Skills beta
- code execution
- files API beta
- prompt caching
- citations
- batch processing

なお、上記は発表時点でAWS側の記事に挙げられている代表的な機能です。Claude Platform全体の最新の機能一覧は、Anthropicの[Claude API Docs](https://platform.claude.com/docs/en/home)で確認できます。

## Amazon Bedrockとの違い

[AWSのFAQ](https://aws.amazon.com/claude-platform/)では、Claude Platform on AWSとClaude on Amazon Bedrockの違いが明示されています。どちらもAWS顧客にClaudeを提供しますが、提供形態とデータ処理の境界が異なります。

| 観点 | Claude Platform on AWS | Claude on Amazon Bedrock |
| --- | --- | --- |
| 提供体験 | AnthropicのネイティブClaude Platform | AWSのBedrock APIおよびマネージドサービス |
| 運営主体 | Anthropic | AWS |
| データ処理 | AWSセキュリティ境界の外でAnthropicが処理 | AWSインフラ内で処理 |
| 認証 | AWS IAM SigV4またはAWS側で作成したAPI key | AWS IAMおよびBedrock API |
| 課金 | AWS Marketplace経由 | Amazon Bedrockの利用料金 |
| 監査 | CloudTrailに記録 | CloudTrailに記録 |
| 主な強み | Anthropicネイティブ機能、早期beta機能、Claude Console | データ境界、Guardrails、Knowledge Bases、PrivateLink、複数モデル |

この違いを踏まえると、Claude Platform on AWSは「**Anthropicの開発者体験をAWSの調達・統制レイヤーに統合する選択肢**」といえます。一方、Amazon Bedrockは「AWSネイティブな生成AI基盤として、データ統制やAWSマネージド機能との統合を重視する選択肢」と位置づけられます。

## アーキテクチャとセットアップの流れ

[Claude Platform on AWS User Guideのセットアップ手順](https://docs.aws.amazon.com/claude-platform/latest/userguide/setup.html)が公開されています。セットアップはClaude Platform on AWSのConsole service pageからサインアップし、AWS Marketplaceサブスクリプションを有効化するところから始まります。その後、Anthropic側のOrganizationセットアップ、Workspace IDの確認、必要に応じたClaude Consoleへのフェデレーションログインを行います。

注意点として、**[AWS Console経由のサインアップでは、AWSアカウントに紐づいた新しいAnthropic organizationが作成されます](https://docs.aws.amazon.com/claude-platform/latest/userguide/setup.html)**。既存のAnthropic organization、Claude Enterprise organization、API key、workspace、Claude Console設定がそのまま引き継がれるわけではありません。

また、API呼び出しも可能で、[認証ドキュメント](https://docs.aws.amazon.com/claude-platform/latest/userguide/authentication.html)では、次のリージョナルエンドポイントを利用すると説明されています。

```text
https://aws-external-anthropic.<region>.api.aws
```

データプレーンのリクエストには、workspace IDを`anthropic-workspace-id`ヘッダーで渡す必要があります。Anthropic SDKを使う場合は、`ANTHROPIC_AWS_WORKSPACE_ID`などの環境変数、またはクライアント設定で指定します。

SigV4認証とAPI key認証はいずれも同じbase URLとリクエスト形式を利用します。Anthropic SDKを使わない場合は、このリージョナルエンドポイントに対してSigV4署名付きリクエストを組み立てるか、API keyをbearer tokenとして送信する必要があります。

## 認証方式

[Claude Platform on AWSの認証ドキュメント](https://docs.aws.amazon.com/claude-platform/latest/userguide/authentication.html)では、次の2つの認証方式が説明されています。

1. AWS IAMによるSigV4認証
2. API key認証

SigV4認証では、[AWSの標準的な認証情報プロバイダーチェーン](https://docs.aws.amazon.com/claude-platform/latest/userguide/authentication.html)を利用します。エンタープライズ企業での利用では、既存のIAMロール、短期認証情報、権限境界、CloudTrailと整合しやすいため、SigV4認証が選択肢に挙がります。

API keyによる認証は、ローカル開発や簡易スクリプトでは扱いやすい方式です。ただし、[Claude Platform on AWSで利用できるAPI keyは、AWS ConsoleのClaude Platform on AWS画面で作成したものに限られます](https://docs.aws.amazon.com/claude-platform/latest/userguide/authentication.html)。通常のClaude Consoleで作成したfirst-party API keyやAmazon Bedrock API keyは、このサービスのエンドポイントでは利用できません。

API key経由の呼び出しには、[IAMで`aws-external-anthropic:CallWithBearerToken`が必要です](https://docs.aws.amazon.com/claude-platform/latest/userguide/iam-policies.html)。APIキーが存在するだけでアクセスできる設計ではなく、bearer tokenのパスもIAMで認可される設計である点を理解しておく必要があります。

また、[期限付きの短期API keyを発行するtoken generatorライブラリ](https://docs.aws.amazon.com/claude-platform/latest/userguide/authentication.html)も提供されています。デフォルトでは12時間の有効期限を持つ短期トークンをIAM credentialsから発行できるため、長期API keyの利用を避けたい場合の選択肢になります。

また、認証情報の優先順位とリージョンの解決にも注意が必要です。[認証ドキュメント](https://docs.aws.amazon.com/claude-platform/latest/userguide/authentication.html)では、一般に明示的なコンストラクタ引数が環境変数より優先され、`ANTHROPIC_AWS_API_KEY`はAWSの標準的な認証情報プロバイダーチェーンより優先されると説明されています。つまり、SigV4認証で動作させたい環境に`ANTHROPIC_AWS_API_KEY`が残っていると、意図せずAPI key認証が選択される可能性があります。

また、Claude Platform on AWSクライアントではリージョン指定が必須で、コンストラクタ、`AWS_REGION`、`AWS_DEFAULT_REGION`のいずれからもリージョンを解決できない場合はエラーになります。疎通確認では、認証情報、リージョン、base URL、workspace IDの4点が正しく設定されているかを確認する必要があります。

## IAM設計の要点

[Service Authorization Reference](https://docs.aws.amazon.com/service-authorization/latest/reference/list_claudeplatformonaws.html)によると、Claude Platform on AWSのサービスプレフィックスは`aws-external-anthropic`です。IAM actionは`aws-external-anthropic:<Action>`の形式を取ります。たとえば、同期的な推論は`CreateInference`、トークン計算は`CountTokens`、workspace取得は`GetWorkspace`で制御します。

リソースレベル権限の中心はworkspaceです。ARN形式は次のとおりです。

```text
arn:${Partition}:aws-external-anthropic:${Region}:${Account}:workspace/${ResourceId}
```

多くの操作はworkspaceに紐づきますが、[IAM policiesの例](https://docs.aws.amazon.com/claude-platform/latest/userguide/iam-policies.html)にもあるとおり、`CreateWorkspace`や`ListWorkspaces`のようなアカウントスコープ操作、`AssumeConsole`や`CallWithBearerToken`のようにworkspace ARNに束縛されない操作もあります。最小権限を設計する際は、workspaceに閉じられるactionと、`Resource:"*"`が必要なactionを分ける必要があります。

[IAM policiesドキュメント](https://docs.aws.amazon.com/claude-platform/latest/userguide/iam-policies.html)では、AWS管理ポリシーとして次のポリシーが説明されています。

- `AnthropicFullAccess`
- `AnthropicReadOnlyAccess`
- `AnthropicInferenceAccess`
- `AnthropicLimitedAccess`

[`AnthropicFullAccess`](https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AnthropicFullAccess.html)は、`aws-external-anthropic:*`に加え、AWS Marketplaceのsubscribe/unsubscribe、outbound web identity federation、STS token関連権限を含みます。初期検証では便利ですが、恒久的な運用ロールへ広く付与するには権限が強いため、用途別のカスタムポリシーへ分解することを推奨します。

[`AnthropicReadOnlyAccess`](https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AnthropicReadOnlyAccess.html)は、`Get*`、`List*`、`CallWithBearerToken`、STS token関連権限を含みます。ただし、read onlyであっても`GetFile`によるファイル内容取得や、`GetMemoryStore`によるメモリ内容取得が対象になり得ます。ポリシー名だけで安全性を判断せず、読み取り対象データの機密性を確認する必要があります。

[IAM policiesドキュメント](https://docs.aws.amazon.com/claude-platform/latest/userguide/iam-policies.html)では、ZDR（Zero Data Retention）制約のあるワークロードとして、リアルタイム推論は許可しつつバッチ推論をdenyするポリシーや、ファイルアップロードとバッチ推論をworkspace単位でdenyする設計例が示されています。ZDR制約のあるワークロードでは、入力された機密データや個人情報をLLM（大規模言語モデル）のベンダー側が一切保存・学習せず、処理が完了した直後に破棄する環境で実行される処理が求められます。高いセキュリティや規制遵守が求められる業界で採用されるアプローチです。

Claude Platformは利用できる機能の幅が非常に広く、機能ごとにデータ永続化や処理形態も異なるため、どのAPI機能を許可するかを分解して検討する必要があります。

## Claude Consoleフェデレーション

**Claude ConsoleはAnthropicのインフラ上で動作します。**[IAM policiesドキュメント](https://docs.aws.amazon.com/claude-platform/latest/userguide/iam-policies.html)では、AWS IAM principalが`AssumeConsole`を呼び出すと、AWS STSがAnthropic audience向けのweb identity tokenを発行し、Claude Console側でフェデレーションセッションが成立します。

そのため、Console利用には[`aws-external-anthropic:AssumeConsole`だけでなく、`sts:GetWebIdentityToken`と`sts:TagGetWebIdentityToken`も必要です](https://docs.aws.amazon.com/claude-platform/latest/userguide/iam-policies.html)。`AnthropicFullAccess`にはこれらが含まれますが、カスタムポリシー、SCP、permission boundaryを使っている環境では明示的に許可する必要があります。

また、[`AssumeConsole`には`aws-external-anthropic:Capability`条件キー](https://docs.aws.amazon.com/service-authorization/latest/reference/list_claudeplatformonaws.html)を使って、`developer`と`admin`のcapabilityを制御できます。`AnthropicFullAccess`はcapability制限なしで`AssumeConsole`を許可するため、Console管理権限を分離したい場合はカスタムポリシーで制御する必要があります。

## 監査とコスト管理

Claude Platform on AWSのアクティビティはCloudTrailに記録されます。[AWS Machine Learning Blog](https://aws.amazon.com/blogs/machine-learning/introducing-claude-platform-on-aws-anthropics-native-platform-through-your-aws-account/)では、workspace操作はmanagement eventsとしてデフォルトで記録され、推論アクティビティを捕捉するにはdata event loggingを有効化できると説明されています。

課金は[AWS Marketplace経由の従量課金](https://aws.amazon.com/blogs/machine-learning/introducing-claude-platform-on-aws-anthropics-native-platform-through-your-aws-account/)です。AWS Cost Explorerで他のAWSサービスと並べて確認できるため、workspaceやタグを使った費用配賦も検討対象になります。

ここで重要なのは、繰り返しになりますが**監査と課金はAWSに統合される一方で、データ処理境界はAWS内に閉じないという点**です。セキュリティレビューでは、CloudTrailとCost Explorerの統合だけで判断せず、データ処理主体、データ保存場所、Anthropic側のデータ利用ポリシーを別途確認する必要があります。

記事執筆時点では、Anthropicのデータ利用に関するポリシーまたは相当する内容に言及されている文章は、単一のページに集約されているわけではなく、目的別に複数のドキュメントに分散しています。Claude Platform on AWS の文脈で確認すべき主な一次情報源は次のとおりです。

| 目的 | ドキュメント名 | URL |
|---|---|---|
| ポリシー全体の入口 | Anthropic Privacy Center（商用顧客向け） | https://privacy.anthropic.com/en/collections/10663361-commercial-customers |
| プライバシーポリシー本文 | Privacy Policy | https://www.anthropic.com/legal/privacy |
| 商用利用規約（DPAを包含） | Commercial Terms of Service | https://www.anthropic.com/legal/commercial-terms |
| データ処理補遺（DPA） | DPAの確認方法（Commercial ToSに自動組み込み） | https://privacy.anthropic.com/en/articles/7996862-i-am-a-commercial-customer-how-do-i-view-your-data-processing-addendum-dpa |
| モデルトレーニングへのデータ利用 | How do you use personal data in model training?（商用向け） | https://privacy.anthropic.com/en/articles/7996885-how-does-anthropic-process-data-sent-through-the-api |
| データ保持期間 | How long do you store my organization's data? | https://privacy.anthropic.com/en/articles/7996866-how-long-do-you-store-personal-data |
| データ処理主体（Controller / Processor） | Does Anthropic Act as a Data Processor or Controller? | https://privacy.anthropic.com/en/articles/9267385-does-anthropic-act-as-a-data-processor-or-controller |
| セキュリティ・コンプライアンス全般 | Anthropic Trust Center | https://trust.anthropic.com/ |


## 価格情報

最新の公開情報を確認すると、Claude Platform on AWSの価格はAWS Marketplaceで課金されるが、実質的な単価は[Claude APIの標準価格](https://platform.claude.com/docs/en/about-claude/pricing)に基づくと整理できます。

[AWSのClaude Platform on AWSプロダクトページ](https://aws.amazon.com/claude-platform/)では、**価格はClaude APIに直接アクセスする場合と同じ**で、詳細はClaude API Pricingを参照するよう案内されています。[AWS Machine Learning Blog](https://aws.amazon.com/blogs/machine-learning/introducing-claude-platform-on-aws-anthropics-native-platform-through-your-aws-account/)では、**課金はAWS Marketplace経由の従量課金モデルであり、AWS Cost Explorerで他のAWSサービスと並べて確認できる**と説明されています。

[AnthropicのPricingドキュメント](https://platform.claude.com/docs/en/about-claude/pricing)では、Claude Platform on AWSはAWS MarketplaceでClaude Consumption Unit、略してCCUを使って課金されると説明されています。トークン利用量は、標準のモデル別・機能別USD価格で評価され、必要に応じてnegotiated discount（交渉による割引）が適用された後、1CCU=$0.01としてCCU数に変換されます。AWS MarketplaceにはCCU数が時間単位でメーター送信され、AWS請求上は単一のCCU line itemとして表示されます。

| 項目 | 公開情報ベースの整理 |
| --- | --- |
| 請求経路 | AWS Marketplace |
| 課金単位 | Claude Consumption Unit、CCU |
| CCU単価 | $0.01 / CCU |
| 価格計算 | Claude APIの標準モデル単価・機能単価でUSD評価し、CCUに変換 |
| 請求タイミング | AWS Marketplaceへ時間単位でmetering、月次請求 |
| 支払いモデル | 後払いのみで、前払いクレジットの対象外 |
| 割引 | private offerやnegotiated discountはCCU単価を下げるのではなく、meteringされるCCU数が少なくなる形で反映 |
| 税 | pre-tax meteringで、税処理はAWS Marketplace側 |
| 可視化 | Claude Console（AWS Console経由でアクセス）ではリアルタイムに内訳を表示し、AWS Cost Explorerでは集約されたCCUベースで表示 |

### モデル別トークン単価

[AnthropicのClaude API Pricing](https://platform.claude.com/docs/en/about-claude/pricing)で公開されている主なモデル単価は次のとおりです。単位はMTok、つまり100万トークンです。Claude Platform on AWSでは、これらの標準価格で評価した金額がCCUに変換されます。

| モデル | 入力 | 5分cache write | 1時間cache write | cache hit / refresh | 出力 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Claude Opus 4.7 | $5 / MTok | $6.25 / MTok | $10 / MTok | $0.50 / MTok | $25 / MTok |
| Claude Sonnet 4.6 | $3 / MTok | $3.75 / MTok | $6 / MTok | $0.30 / MTok | $15 / MTok |
| Claude Haiku 4.5 | $1 / MTok | $1.25 / MTok | $2 / MTok | $0.10 / MTok | $5 / MTok |

### 機能別の価格要素

Claude Platform on AWSでは、単純なinput/output token以外にも「**[Claude API Pricingに記載された機能別価格](https://platform.claude.com/docs/en/about-claude/pricing)**」を考慮する必要があります。

| 機能 | 価格上の扱い |
| --- | --- |
| Prompt caching | 5分cache writeはbase inputの1.25倍、1時間cache writeは2倍、cache readは0.1倍 |
| Batch API | input/output tokenとも50%discount |
| Data residency / `inference_geo:"us"` | Claude Opus 4.6、Claude Sonnet 4.6以降では1.1倍の乗数適用。デフォルトのglobalが標準価格 |
| Fast mode | Claude Platform on AWSでは利用不可と記載 |
| Tool use | tool定義やtool resultによる追加tokenは通常のtoken課金対象 |
| Web search | $10 / 1,000searchesに加え、検索結果由来のtokenが通常課金対象 |
| Web fetch | 追加料金なし。ただし取得コンテンツがconversation contextに入るためtoken課金は発生 |
| Code execution | web search / web fetchと併用する場合は追加料金なし。単独利用では実行時間課金があり、月1,550時間の無料枠後は$0.05 / hour / container |
| Claude Managed Agents | token課金に加えてsession runtimeが$0.08 / session-hour |

### Private offerと既存Bedrock契約

Claude Platform on AWSのサインアップ時、[AWS ConsoleはAWS Marketplace上でアカウントに紐づくprivate offerを確認し、該当する場合は受諾を促します](https://docs.aws.amazon.com/claude-platform/latest/userguide/setup.html)。[AnthropicのPricingドキュメント](https://platform.claude.com/docs/en/about-claude/pricing)では、private offerの条件はAnthropic社のアカウント担当者または担当営業に確認するよう案内されています。

既存のAmazon Bedrock private offerがある場合は、Claude Platform on AWSを有効化する前にAnthropicまたはAWSの担当者へ確認する必要があります。[公式ドキュメント](https://docs.aws.amazon.com/claude-platform/latest/userguide/setup.html)では、**private offerが受諾される前に発生した利用には割引を遡及適用できない**とされています。

### Amazon BedrockやClaude Enterpriseとの混同に注意

Claude Platform on AWSはAWS Marketplace経由でAWS請求に載りますが、Amazon Bedrockのモデル価格とは別の価格体系として見る必要があります。BedrockのClaudeはAWS Bedrock Pricingが公式価格であり、Claude Platform on AWSは[Claude API Pricing](https://platform.claude.com/docs/en/about-claude/pricing)を基準にCCUへ変換されます。

費用比較では、次の3つを分けて整理することが重要です。

- **Claude Platform on AWS**
  - Claude API標準価格、機能別価格、CCU変換、Marketplace private offer
- **Claude on Amazon Bedrock**
  - Bedrockのモデル別価格、global / regional endpointの価格差、Bedrock周辺機能の料金
- **Claude Enterprise / Claude Code**
  - Marketplace SaaSのシート課金で、Claude Platform on AWSのAPI従量課金とは別物

AWS MarketplaceではClaude EnterpriseなどのSaaSも公開されています。[AWS Marketplace Blog](https://aws.amazon.com/blogs/awsmarketplace/anthropics-claude-for-enterprise-now-available-in-aws-marketplace/)ではClaude for Enterpriseが$40 / user / month、25seat minimumと紹介されていますが、これはClaude Platform on AWSのAPI/CCU課金ではなく、Claude Enterpriseという別サービスのシート課金です。見積もり時には混同しないよう注意が必要です。

### 簡易的な試算

[Anthropic Pricing](https://platform.claude.com/docs/en/about-claude/pricing)では1CCU=$0.01と説明されています。そのため、Claude API価格で計算したUSD金額を0.01で割ると、おおよそのCCU数を算出できます。割引がある場合は、割引後のUSD相当額からCCUに変換されます。

例として、Claude Sonnet 4.6で100万input tokens、20万output tokensを通常APIとして処理する場合を考えます。

```text
input:  1.0 MTok * $3  = $3.00
output: 0.2 MTok * $15 = $3.00
total: $6.00
CCU:   $6.00 / $0.01 = 600 CCU
```

同じ処理をBatch APIで実行できる場合、input/outputとも50%のディスカウントが適用されます。

```text
input:  1.0 MTok * $1.50 = $1.50
output: 0.2 MTok * $7.50 = $1.50
total: $3.00
CCU:   $3.00 / $0.01 = 300 CCU
```

## 採用を検討しやすいケース

[AWS Machine Learning Blog](https://aws.amazon.com/blogs/machine-learning/introducing-claude-platform-on-aws-anthropics-native-platform-through-your-aws-account/)と[AWSプロダクトページ](https://aws.amazon.com/claude-platform/)で示された特徴を踏まえると、Claude Platform on AWSは次のようなケースで検討しやすいサービスです。

- Claude ConsoleやAnthropic SDKを中心に開発しているが、課金、認証、監査をAWSに一元的に統合したい場合
- Claude Managed Agents、Skills、MCP connector、web search、code execution、files APIなど、Anthropicネイティブ機能を早期に利用したい場合 (リリーススピードでAmazon Bedrock経由よりも優位になる可能性を考慮)
- 開発チーム単位、プロジェクト単位でworkspaceを分け、これをAWSのIAMとタグで統制したい場合
- 既存のAnthropic直契約や個別請求をAWS Marketplaceに統合したい場合

一方、[AWSプロダクトページのBedrockとの比較](https://aws.amazon.com/claude-platform/)と[セットアップ時のorganizationの分離仕様](https://docs.aws.amazon.com/claude-platform/latest/userguide/setup.html)を踏まえると、次のケースでは慎重な検討が必要です。

- 顧客データをAWS境界内に限定する必要がある場合
- 厳密なリージョナルデータレジデンシー要件がある場合
- PrivateLinkによるネットワーク閉域化を重視する場合
- Bedrock Guardrails、Knowledge Bases、Agents、複数モデル選択などAWSマネージド機能が前提になっている場合
- 既存のAnthropic organization、API key、workspace設定をそのまま移行できると期待している場合

## 実運用前の確認ポイント

Claude Platform on AWSを企業利用する場合は、少なくとも次の観点を確認することを推奨します。

- **データ分類**
  - Anthropicから参照または処理されても良いと扱える必要があります
- **データレジデンシー**
  - 利用リージョンと実際の処理・保存ポリシーを確認します
- **IAM**
  - `AnthropicFullAccess`を恒久運用ロールに使わず、workspace単位の最小権限を検討します
- **API key**
  - 長期API keyを避けられる場合はSigV4または短期API keyを検討します
- **Console**
  - `AssumeConsole`の`developer`と`admin`のcapabilityを分離します
- **Batch/File**
  - ZDRや永続化制約があるworkspaceではBatch APIとFiles APIを明示的にdenyします
- **CloudTrail**
  - Data event loggingを有効化する対象とコストを確認します
- **課金**
  - Cost Explorerとタグ設計でworkspace/team単位の費用配賦を設計します
- **移行**
  - 既存Anthropic organizationとは別organizationになる点を利用者に周知します
  - 移行への理解を求める必要があります

## まとめ

Claude Platform on AWSは、Amazon Bedrockの置き換えではなく、ClaudeをAWS経由で利用するための新しい選択肢です。Anthropicのネイティブな開発体験を活かしつつ、AWSの課金、IAM、CloudTrailに統合できる点が大きな特徴です。

一方で、AWSアカウントから利用できることと、AWS内でデータが処理されることは同義ではありません。公式資料でも、Claude Platform on AWSの顧客コンテンツはAnthropicによりAWS外で処理されることが明記されています。したがって、採用判断では、機能面だけでなく、データ処理境界、IAM設計、監査要件、課金体系を合わせて確認することが重要です。

実務上は、Anthropicのネイティブ機能やClaude Consoleを活かした開発者体験を重視する領域ではClaude Platform on AWSが有力な候補になります。一方、AWS境界内でのデータ処理、ネットワーク閉域化、Bedrock周辺機能との統合を重視する領域では、引き続きAmazon Bedrockを中心に検討するのが適切です。

本記事がClaude Platform on AWSを利用する上での判断材料の1つになれば幸いです。

## 参考文献

- [Claude Platform on AWS is now generally available-AWS What's New](https://aws.amazon.com/jp/about-aws/whats-new/2026/05/claude-platform-aws/)
- [Introducing Claude Platform on AWS:Anthropic's native platform, through your AWS account-AWS Machine Learning Blog](https://aws.amazon.com/blogs/machine-learning/introducing-claude-platform-on-aws-anthropics-native-platform-through-your-aws-account/)
- [Claude Platform on AWS Product Page-Amazon Bedrock](https://aws.amazon.com/claude-platform/)
- [AnthropicFullAccess-AWS Managed Policy Reference](https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AnthropicFullAccess.html)
- [AnthropicReadOnlyAccess-AWS Managed Policy Reference](https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AnthropicReadOnlyAccess.html)
- [Actions, resources, and condition keys for Claude Platform on AWS-Service Authorization Reference](https://docs.aws.amazon.com/service-authorization/latest/reference/list_claudeplatformonaws.html)
- [Set up your account-Claude Platform on AWS User Guide](https://docs.aws.amazon.com/claude-platform/latest/userguide/setup.html)
- [Authentication-Claude Platform on AWS User Guide](https://docs.aws.amazon.com/claude-platform/latest/userguide/authentication.html)
- [IAM policies-Claude Platform on AWS User Guide](https://docs.aws.amazon.com/claude-platform/latest/userguide/iam-policies.html)
- [Claude API Docs](https://platform.claude.com/docs/en/home)
- [Pricing-Claude API Docs](https://platform.claude.com/docs/en/about-claude/pricing)
- [Anthropic's Claude for Enterprise is now available in AWS Marketplace-AWS Marketplace Blog](https://aws.amazon.com/blogs/awsmarketplace/anthropics-claude-fo
