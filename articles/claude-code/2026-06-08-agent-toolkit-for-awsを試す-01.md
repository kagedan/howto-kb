---
id: "2026-06-08-agent-toolkit-for-awsを試す-01"
title: "Agent Toolkit for AWSを試す"
url: "https://zenn.dev/exwzd/articles/20260601_agent_toolkit_aws_1"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "LLM", "Python"]
date_published: "2026-06-08"
date_collected: "2026-06-09"
summary_by: "auto-rss"
query: ""
---

先端技術開発グループ（WAND）の小島です。AWSが2026年5月に発表した「[Agent Toolkit for AWS](https://aws.amazon.com/jp/about-aws/whats-new/2026/05/agent-toolkit/)」を試してみました。コーディングエージェントからAWSのドキュメント検索やリソース操作までを一手に担うツールキットですが、実際に触ってみると、便利な点と過渡期ゆえのハマりどころの両方が見えてきました。本記事では、具体的なユースケースを通じてその実像を紹介します。

Agent Toolkit for AWSは、コーディングエージェントに対して、AWSサービスを操作するためのツール・知識・ガードレールを提供するものです。具体的には、AWSのサービスや仕様の調査、アーキテクチャ設計、現在のAWS環境のリソースへの問い合わせや操作などを可能にします。

## 本記事のスコープ

本記事では、Agent Toolkit for AWSがどのようなことをできるのかに焦点をあて、

* インストール方法
* 接続確認
* ドキュメント検索のユースケース
* AWSリソースに対する問い合わせ
* AWSリソースの作成・変更
* その他ハマりどころ

について解説します。アーキテクチャ図作成については別記事で解説します。

[Agent Toolkit for AWS](https://github.com/aws/agent-toolkit-for-aws)は、Claude CodeやCodexでは、マーケットプレイスのプラグインとして提供されています。

Claude Codeの場合、以下のようにインストール可能です（[参考](https://docs.aws.amazon.com/agent-toolkit/latest/userguide/quick-start.html)）。

```
/plugin marketplace add aws/agent-toolkit-for-aws
/plugin install aws-core@agent-toolkit-for-aws
/reload-plugins
```

インストールして`/plugin`で確認すると、「**aws-core Plugin**（プラグイン）」と「**aws-mcp**（MCP）」の2つがインストールされています。

![](https://static.zenn.studio/user-upload/deployed-images/390763b9cb0999efbfb358d3.png?sha=dd51b624f436531663e548dbdc2005275a9405b4)

MCPは、初期状態では接続されておらず（failed）、AWSの認証情報を渡すことで有効化できます。

## プラグインによってインストールされるスキル

プラグインのインストールにより、以下のスキル群がエージェント側に追加されました。

* `aws-core:aws-sdk-swift-usage`
* `aws-core:amazon-bedrock`
* `aws-core:aws-iam`
* `aws-core:aws-amplify`
* `aws-core:aws-cloudformation`
* `aws-core:aws-sdk-js-v3-usage`
* `aws-core:aws-observability`
* `aws-core:aws-serverless`
* `aws-core:aws-billing-and-cost-management`
* `aws-core:aws-sdk-python-usage`
* `aws-core:aws-containers`
* `aws-core:aws-cdk`
* `aws-core:aws-messaging-and-streaming`

## 接続確認（MCPなし）

AWSの認証情報を渡さず、MCPを使わない場合は、プラグインの**スキルのみの動作**になります。

> * What AWS Regions are available?
> * What AWS services should I use to build a serverless API?
> * Create an Amazon S3 bucket with versioning enabled and a lifecycle policy that transitions objects to Glacier after 90 days.

[チュートリアル通り](https://docs.aws.amazon.com/agent-toolkit/latest/userguide/quick-start.html)に、上記の3つの質問に答えさせます。

1つ目の質問はLLMの知識だけでも答えられるため、接続確認としてはやや弱いものの、Skillsが呼ばれていれば成功です。2つ目では`aws-core:aws-serverless`、3つ目では`aws-core:aws-cloudformation`のスキルが起動しました。

3つ目は、MCPなしでは認証情報がないため、S3バケットをデプロイできません。**スキルはCloudFormationテンプレートの作成までを担い**、デプロイは別ウィンドウでAWS CLIのコマンドから実行します。

```
# EC2 内で AWS CLI が認証情報を読めることを確認
aws sts get-caller-identity

# デプロイ
aws cloudformation deploy \
  --template-file <PATH_TO_YOUR_WORK_DIR>/s3-archive-bucket.yaml \
  --stack-name poc-archive-bucket \
  --region <REGION>
```

実践的にAWSリソースをデプロイする場合は、このように**コーディングエージェントでIaCのスクリプトを作成し、TerraformやCloudFormationのコマンドでデプロイする**ことが推奨されます。

IaCを経由しないと、LLMの確率的な挙動により操作に一貫性がなくなります。また、後述するAWS MCP経由のリソース操作はMCP自体の安定性に課題があり、IaCを経由させたほうが速く頑強です。

## MCPと接続する

「Failed」となっているMCPを接続する場合、別のコンソールから`aws login`でログインします。

```
# ブラウザから認証情報をコールバック可能な場合
aws login

# ブラウザから認証情報をコールバック不可能な場合（EC2環境など）
aws login --remote
```

EC2の場合は、`--remote`オプションをつけ、「検証コードをコピー」を押してコンソールにコピーします。

![](https://static.zenn.studio/user-upload/deployed-images/06c08abae1c1a3b6040dcc75.png?sha=483ec908528015968bf6b25a94750a960b19928c)

![](https://static.zenn.studio/user-upload/deployed-images/48aada9554d6e9acbf390e9f.png?sha=185a7d6c3a0b185866c2bfdcc8152913c33ea2dc)

![](https://static.zenn.studio/user-upload/deployed-images/239d6d701d1b5badaea1c7b3.png?sha=d12829d1dba1b0a201e354e4852abf163f32a2be)

Claude Codeの場合、`/mcp`でMCP一覧を開き、AWS MCPサーバーを選択します。

「Reconnect」を選択し、「Reconnect to plugin:aws-core...」と表示されればOKです。MCPの一覧リストでも、「connected」と表示されているはずです。

![](https://static.zenn.studio/user-upload/deployed-images/b1516c99d9d1f3868446533c.png?sha=c015d498ec03e3a2a3b2ab3db1b7659812a61d16)

![](https://static.zenn.studio/user-upload/deployed-images/af88a902129cf17254e48d2b.png?sha=1ffa80abe5918f1358c0163dc00bf759d7fa8cd2)

## ドキュメントを検索する

これまでのAWS公式MCPには、ブラウザを開かずにAWSのドキュメントや仕様を引けるものがあり、非常に便利でした。

「ドキュメント検索」という用途で、Agent Toolkit for AWSがどう動くかを見ていきます。

### テストする質問

最新情報が変わりやすい内容で聞いてみます。例えば、Bedrock AgentCoreの中身について質問します。

> Bedrock AgentCoreとCognitoを統合する方法を教えて

### MCPと接続なし→スキルの知識で回答

MCPと接続しない場合（AWSの認証情報がない場合）、**プラグインのスキルの知識から回答**します。

MCPなしの場合の返答全文

# Bedrock AgentCore における Cognito 統合の認証方法

AgentCore の認証は **OAuth 3 層アーキテクチャ** に分かれており、Cognito を統合できるレイヤーは限られています。スキルのリファレンス（`agentcore-credentials-and-security.md` / `agentcore-runtime.md`）から以下のとおりです。

## 1. Inbound JWT（Cognito の最も一般的な使い方）

呼び出し元 → AgentCore Runtime / Gateway に対する認証で、**Cognito は公式に「Inbound JWT」の IdP としてサポート**されています。

* サポート IdP: **Cognito、Okta、Auth0、Azure AD、カスタム OIDC**（`agentcore-credentials-and-security.md:69`）
* Runtime 作成時の `--authorizer-configuration` で JWT 検証を構成（`agentcore-runtime.md:58`, `:108-109`）
* 本番では authorizer 必須（未認証エンドポイントは禁止）

Cognito User Pool が発行する JWT（Access Token / ID Token）を、AgentCore がトークン検証して呼び出しを許可するパターンです。

## 2. Outbound OAuth Credential Provider（エージェント → 外部 API）

エージェント側から外部 API へ OAuth で認証するために、`create-oauth2-credential-provider` を使います。

* `--credential-provider-vendor` に **Cognito を含むベンダー** を指定可能
* クライアントシークレットは Secrets Manager に自動格納される（`clientSecretArn` が返る）
* 構成項目: token endpoint URL、client ID、scopes、grant type

ただし「外部 API として Cognito を呼ぶ」用途は実運用では稀で、主用途は Inbound JWT 側です。

## 3. Gateway OAuth（Gateway → 上流 MCP）

Gateway が上流の MCP サーバーへ認証するレイヤー。Cognito を上流に置くケースは少ないですが構成可能です。

## レイヤーの整理

| レイヤー | 方向 | Cognito の用途 |
| --- | --- | --- |
| **Inbound JWT** | Caller → AgentCore | ★ User Pool の JWT を AgentCore で検証（最も一般的） |
| Outbound Credential Provider | Agent → 外部 API | Cognito を外部 OAuth プロバイダーとして呼ぶ場合 |
| Gateway OAuth | Gateway → Upstream MCP | 上流 MCP が Cognito 保護されている場合 |

## 公式ドキュメント

スキル内のリファレンスは、最新の構成手順・CDK サンプル・サポート対象 grant type については AWS 公式ドキュメントを参照するよう指示しています。

### MCPと接続済み→ドキュメントを検索して回答

MCPと接続済みの場合（AWSの認証情報がある場合）、**AWSのドキュメントをリアルタイムで検索して回答**します。これは従来のDocumentation MCPと同様の挙動です。

MCPありの場合の返答

## Bedrock AgentCore × Amazon Cognito 認証方法

Amazon CognitoはAgentCoreの**ID プロバイダー**として、以下の2方向で利用できます。

### 1. Inbound Auth（受信認証）— AgentCore Gateway / Runtime へのアクセス制御

AgentCore Runtimeには2種類の認証メカニズムがあり、Cognitoは **JWT Bearer Token** 方式で利用します（IAM SigV4とJWTは同時には使えません）。

**(a) ユーザー認証（User Pool + Bearer Token）**

* Cognito User Poolを作成し、ユーザー認証で発行されたアクセストークン（JWT）をBearerトークンとしてAgentCore Runtimeに渡す
* `USER_PASSWORD_AUTH` などのフローでトークンを取得
* AgentCore Runtime側では `customJWTAuthorizer` に以下を設定：
  + `discoveryUrl`: `https://cognito-idp.{region}.amazonaws.com/{poolId}/.well-known/openid-configuration`
  + `allowedClients`: Cognito Client ID
  + `allowedAudience`: aud クレーム（任意）

**(b) Machine-to-Machine 認証（Client Credentials Grant）**

* Resource Server + Scopes + Client Credentialsを設定
* AgentCore Gateway へのM2Mアクセス用途
* 例: `client_credentials` フローで `read` / `write` スコープを付与

**JWT検証パラメータ（authorizerConfiguration）**

| 設定項目 | 検証対象クレーム |
| --- | --- |
| `discoveryUrl` → issuer | `iss` |
| `allowedClients` | `client_id` |
| `allowedAudience` | `aud` |
| `allowedScopes` | `scope` |
| 必須カスタムクレーム | 任意のクレーム名/値 |

### 2. Outbound Auth（送信認証）— AgentCoreから外部リソースへのアクセス

エージェントがCognitoで保護されたリソースにアクセスする場合、AgentCore Identity の **Credential Provider** にCognitoをOAuth2プロバイダとして登録：

```
{
  "name": "Cognito",
  "credentialProviderVendor": "CognitoOauth2",
  "oauth2ProviderConfigInput": {
    "includedOauth2ProviderConfig": {
      "clientId": "...",
      "clientSecret": "...",
      "authorizationEndpoint": "https://{domain}.auth.{region}.amazoncognito.com/oauth2/authorize",
      "tokenEndpoint": "https://{domain}.auth.{region}.amazoncognito.com/oauth2/token",
      "issuer": "https://cognito-idp.{region}.amazonaws.com/{userPoolId}"
    }
  }
}
```

### サポートされるOAuth 2.0 フロー

* **Authorization Code Grant**（ユーザー代理 / 3LO） — `X-Amzn-Bedrock-AgentCore-Runtime-User-Id` ヘッダーでユーザーIDを伝播
* **Client Credentials Grant**（M2M / 2LO）

### 参考ドキュメント

特定のユースケース（Webアプリからの呼び出し、MCPサーバ、社内IdPフェデレーションなど）があれば、より具体的な実装パターンをご案内できます。

### 考察

**AWSの一次情報により忠実なのは「MCPあり」**ですが、ドキュメント検索のためにAWSの認証情報を渡すのは**過剰権限**です。

ドキュメント検索自体は、原理的には認証情報がなくても動きます。しかし2026年6月現在のAWS MCPは、認証情報がないとClaude Codeから切断（disconnect）される実装になっているため、実質的に認証情報が必須になってしまっています。

背景としては、乱立したAWS公式MCPを統合する形でAgent Toolkitや単一のAWS MCPが生まれたと推測されます。1個にまとめた結果、AWSリソースの読み書きに認証情報が必要となり、必要な権限と不要な権限をまだ分離設計できていない、というのが現状でしょう。

ドキュメント検索目的だけで使いたいなら、認証情報が不要な**旧来のMCP**（Knowledge MCP、Documentation MCP）**を活用する**のが現状の選択肢です。

ただし、これらが将来EOLになるリスクはあります。AWS公式のメッセージも「Agent Toolkitに移行せよ」というものです。

## AWSリソースに対する問い合わせ

### 稼働中のインスタンス数の取得

MCPあり（AWSの認証情報あり）の場合のみ可能です。例えば、稼働中のEC2の個数を問い合わせます。

> 東京リージョンにEC2は何個あって、何個稼働してる？

するとMCPは、AWS CLIのコマンド（`aws ec2 describe-instances`）を裏で実行し、以下のように返答します。

```
## サマリー

| 項目 | 台数 |
|------|------|
| **合計** | **53台** |
| 🟢 稼働中 (running) | **22台** |
| ⚪ 停止中 (stopped) | 31台 |
```

ただし、これは数え間違いで、**実際の稼働中は19台**でした。LLMの回答は以前から**個数の数え上げミスが起きがち**でしたが、その性質は相変わらずのようです。

### コスト分析

検証環境における、EC2-Otherのコスト内訳を自然言語で問い合わせます。AWS Cost Explorerのような専用サービスもありますが、こうした**分析系のユースケースでは便利そう**です。

今回は試していませんが、ログ分析もおそらく得意でしょう（Amazon QやDevOps Agentとの棲み分けという問題は残りますが）。

コスト分析の返答（一部マスク）

EC2-Other（$xx.xx）の内訳です。usage type を整理しました。

## カテゴリ別内訳

| カテゴリ | コスト(USD) | 構成比 |
| --- | --- | --- |
| **EBSボリューム（容量＋IOPS＋スループット）** | **$xx.xx** | 78.7% |
| NAT Gateway | $xx.xx | 12.4% |
| EBSスナップショット | $xx.xx | 7.2% |
| t4g CPUクレジット（バースト超過） | $xx.xx | 1.6% |
| データ転送ほか | $x.x 未満 | ~0% |

## EBSボリューム($xx)の詳細

| usage type | コスト |
| --- | --- |
| gp3 容量（東京 APN1） | $xx.xx |
| gp3 容量（**バージニア us-east-1**） | $xx.xx |
| gp3 プロビジョンドIOPS（東京） | $xx.xx |
| gp3 プロビジョンドスループット（東京） | $xx.xx |
| gp2 容量（東京） | $xx.xx |

## NAT Gateway($xx)の詳細

| usage type | コスト |
| --- | --- |
| NAT GW 稼働時間（東京） | $xx.xx |
| NAT GW 稼働時間（**バージニア us-east-1**） | $xx.xx |
| Regional NAT GW 時間 | $xx.xx |
| データ処理量 | $xx.xx |

## 読み取れること

**① EC2-Otherの正体はほぼEBS**  
EBS（ボリューム $xx + スナップショット $xx）＝ **$xx、EC2-Otherの86%**。やはり先ほどの仮説どおり、**停止中インスタンスのEBSが効いています**。停止中もボリューム容量・スナップショットは課金されるため、31台の停止インスタンス（特にGPU系は大容量ディスク）が主因と見られます。

**② バージニア(us-east-1)にもリソースがある**  
EBS $xx.xx + NAT GW $xx.xx が us-east-1 で発生。東京以外にも使われていないリソースが残っている可能性があります。

**③ NAT Gatewayは「時間課金」が主**  
データ処理量($x.xx)はほぼゼロで、ほとんど **立てっぱなしの基本料金($xx)**。使われていないVPCのNAT GWがあれば削減候補です。

## 次のアクション候補

* **未アタッチ（available状態）のEBSボリューム棚卸し** — 完全に無駄なので削除候補
* **停止中インスタンスのEBS容量ランキング** — GPU系の大容量ディスクを特定
* **古いスナップショットの棚卸し**
* **us-east-1の使われていないNAT GW / EBSの確認**

どれを掘り下げますか？まず「未アタッチEBS」と「停止中インスタンスのEBS容量」を見るのが削減効果を測りやすくおすすめです。

## AWSリソースの作成・変更

ここまではGET系のユースケースでしたが、AWS MCPを通じてリソースの作成・変更も可能です。

### EC2インスタンスの作成

以下のように、EC2インスタンスを起動してみます。

> kojima-test-ec2-from-mcp というEC2を1台起動して。東京リージョンで

次のようにメッセージが表示され、EC2が起動します。

```
● まず最新のAmazon Linux 2023 AMIのIDを東京リージョンで取得します。

  Called plugin:aws-core:aws-mcp (ctrl+o to expand)

● Latest AL2023 AMI: ami-0b53194d9d4d5cfea。このAMIで t3.micro を1台起動します。

  Called plugin:aws-core:aws-mcp (ctrl+o to expand)

● EC2インスタンスを起動しました ✅
```

![](https://static.zenn.studio/user-upload/deployed-images/60759576bee3852ae877e43a.png?sha=3a6d80b92d4079124d359ade4dad1f6fd3739f3b)

### EC2インスタンスの変更

インスタンスタイプを変更してみます。

> このインスタンスタイプをt3.nanoに変更して

```
● インスタンスタイプの変更は停止中でないとできないので、停止 → タイプ変更 → 再起動の順で行います。まず停止します。

  Called plugin:aws-core:aws-mcp 2 times (ctrl+o to expand)
```

いくつかのステップを経て`t3.nano`に変更されていました。

![](https://static.zenn.studio/user-upload/deployed-images/7e2a53e74bff8743312f54e9.png?sha=815aa0a03e24f0827888165aad474ee346084c62)

## Tips : AWS MCP接続のハングについて

現在のAWS MCPには、Claude Code上ではMCPがconnectedと正常に表示されているのに、**接続がハングする不具合**があります（aws-coreプラグイン1.0.0、aws-mcp 1.6.0）。

* 承認プロンプトも出ず、応答も返さず、エラーにもならない
* Claude Code 上は延々「考え中」のまま固まる
* 待っても自己回復せず、実際に 4 時間ハングし続けた

### 原因

ローカルのプロキシ（`uvx mcp-proxy-for-aws`）が、落ちた接続を再接続できずに固まっていました。

* アイドル中に、裏側の永続 SSE 接続が落ちる
* 次の呼び出しでプロキシが再接続を試みる
* このとき、すでに落ちたタスクを待ち続けてしまう

### 何が課題か

注意したいのは、これが「タイムアウトの設定漏れ」ではないという点です。

* タイムアウトは何重にも入っていた。それでも止まらなかった
* 原因は、落ちた接続を張り直す処理が固まると、どんなタイムアウトも素通りしてしまうこと
* つまり本質は、タイムアウトの数や長さではなく、壊れた接続を安全に作り直せないという堅牢性の不足

一度この状態になると**Claude Codeの再起動**しか有力な解決方法がないため、「考え中」で長時間ハングした場合は、回答を待たずに再起動してしまうほうが良さそうです。

Documentation MCPなど旧来のAWS公式MCPは安定して動作していただけに、この不具合は使い勝手の悪さとして感じられるかもしれません。

## Tips : スキルの知識はどのように作られたのか

ドキュメント検索でAWSの認証情報を渡すのは過剰権限だと述べましたが、MCPを使わない場合は、スキルの知識からAWSの公式情報を参照する形になります。

ここで気になるのが「スキルはどのように作られたのか」という点です。結論から言うと、これは**おそらくAWS内部の人間によって作られた**ものでした。公式ドキュメント（一次情報）とスキルを自動的に同期する仕組みは観測できず、外部からは**人手で作成・更新されている**と判断できました。

### 判断根拠

こう判断した根拠は以下の通りです。

* 文体・構造: 「MUST NOT」「セキュリティ考慮」「hard-to-debug」など、ガードレール的・主観的な記述が多数。公式 docs のリライトではなく、エージェント向けに整形されている（参考：[https://github.com/aws/agent-toolkit-for-aws/tree/main/skills）](https://github.com/aws/agent-toolkit-for-aws/tree/main/skills%EF%BC%89)
* CI/CD: `.github/workflows/build.yml` は lint・validate・gitleaks のみで、コンテンツ生成スクリプトは存在しない
* `tools/validate.py` も構造チェック（kebab-case 名、YAML frontmatter）にとどまる
* `CONTRIBUTING.md` で「外部コード貢献は受け付けていない」とされ、クローズドな執筆体制
* README に「skills that have undergone thorough end-to-end evaluations」とあり、手動キュレーション + 評価テスト前提

### 同期プロセス（推定）

```
[AWS内部]                [GitHub]                [ユーザー側]
公式docs改訂              upstream main           ローカルキャッシュ
   │                         │                        │
   │ (人手で読んで反映)       │ (plugin install/update)│
   ▼                         ▼                        ▼
skills/*.md  ──git push──→  release tag  ─────────→  ~/.claude/plugins/cache/
                          (version bump)
```

* 自動同期は無い
* ユーザー側は `/plugin update` 等を明示的に実行しない限りローカルが古いまま
* AWS が新機能をリリース → docs 改訂 → スキル反映 → リリース → ユーザーが更新、というチェーンの**各段階に人手のタイムラグ**

### リスク

スキルの知識は公式ではあるものの、あくまで**二次情報**です。今後年数が経過すると、AWSサービスのアップデートに対してスキルの鮮度が落ちていくリスクがあります。

また、AWSの公式ドキュメントとスキルのドキュメントが二重管理になっている、という課題もあります。とはいえ、ドキュメントが細かい手段や仕様の断片的な知識の集合体であるのに対し、スキルは原理原則を包括して圧縮した内容です。鮮度の問題さえ解決すれば、利用する側にとっても一定のメリットがあるといえるでしょう。

## まとめ

本記事ではAgent Toolkit for AWSについて、ドキュメント検索やAWSリソースへの問い合わせ・作成といった例を通じて、どの程度のことができるのかを見てきました。

現状は、乱立した公式MCP群へのアンチテーゼとして、何でもできる単一のAWS MCPにとりあえず押し込めた、という過渡期の印象が強いです。また、ドキュメント検索とAWSリソース操作を同一の認証情報・同一のMCPで行うべきかという責務分離の議論もまだ設計に落とし込まれておらず、「もっと良い形があるのではないか」という疑問も残ります。

なお本稿では触れませんでしたが、[AWS MCPからの操作をIAMで禁じる方法はすでに公開されています](https://docs.aws.amazon.com/agent-toolkit/latest/userguide/security_iam_id-based-policy-examples.html)。本番ワークロードでMCPを使う場合は、この設定がおそらく必須になるでしょう。過剰権限が気になる場合は、ぜひ活用してみてください。
