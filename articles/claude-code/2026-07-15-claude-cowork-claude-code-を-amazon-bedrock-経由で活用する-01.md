---
id: "2026-07-15-claude-cowork-claude-code-を-amazon-bedrock-経由で活用する-01"
title: "Claude Cowork / Claude Code を Amazon Bedrock 経由で活用する理由"
url: "https://zenn.dev/nttdata_tech/articles/d2c044e4384fea"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "LLM", "cowork", "zenn"]
date_published: "2026-07-15"
date_collected: "2026-07-16"
summary_by: "auto-rss"
query: ""
---

## 1. はじめに

Claude Cowork や Claude Code は、調査、ファイル操作、データ分析、資料作成、コーディング、テスト、レビューといった作業を Claude に委任できる AI エージェント体験を提供します。

一方で、企業で利用する場合に重要なのは「何ができるか」だけではありません。プロンプト、ソースコード、生成物、監査ログ、コストなどをどう管理するかが重要になります。

本記事では、**Claude Cowork や Claude Code を Amazon Bedrock 経由で利用する理由を、AWS（Amazon Web Services）のセキュリティ、認証、監査、請求、全社展開の観点から整理**します。

なお、本記事では詳細な手順紹介ではなく、「なぜ Amazon Bedrock 経由で使うのか」と「どの接続方式を選ぶべきか」を中心にまとめます。

## 2. Claude Cowork / Claude Code とは

Claude Cowork と Claude Code は、どちらも Claude に作業を委任するためのエージェント体験ですが、主な利用シーンが異なります。

| 項目 | Claude Cowork | Claude Code |
| --- | --- | --- |
| 主な対象 | 業務ユーザー、企画、プロジェクトマネージャー、アナリスト、開発者 | 開発者、DevOps、Platform Engineer |
| 主な用途 | 調査、分析、ファイル整理、資料作成、レポート生成 | コード調査、実装、テスト、レビュー、リファクタリング |
| 実行イメージ | Desktop から業務タスクを依頼 | CLI / IDE / Desktop から開発タスクを依頼 |
| 扱うデータ | ドキュメント、Excel、CSV、PDF、画像、業務資料 | ソースコード、テスト、設定ファイル、ドキュメント |
| 出力例 | Markdown、Excel、PowerPoint、整理済みファイル | コード差分、テスト結果、README、PR説明文 |

ざっくり言えば、Claude Cowork は「業務作業を任せる」ためのもの、Claude Code は「開発作業を任せる」ためのものです。  
企業での展開を考えると、Claude Cowork は非エンジニアを含む業務ユーザーへの AI エージェント展開、Claude Code は開発者の生産性向上という位置づけになります。

## 3. なぜ Amazon Bedrock 経由で活用するのか

Claude Cowork / Claude Code を利用するだけであれば、単に「便利な AI エージェントを使える」という話になります。

しかし、企業で利用する場合はそれだけでは不十分です。Claude Cowork は業務資料、ローカルファイル、レポート作成などを扱い、Claude Code はソースコード、設定ファイル、開発環境に近い領域を扱います。つまり、通常のチャット型 AI よりも、業務データや開発資産に近い場所で利用されるツールです。

そのため、「何ができるか」だけでなく、どの管理境界で利用するかが重要になります。

Claude Cowork / Claude Code を Amazon Bedrock 経由で利用する**主なメリットは、以下の4点**です。

| 観点 | メリット |
| --- | --- |
| **コスト** | 従量課金で利用できるため、使った分だけ支払う形にできます。固定のシートライセンスではないため、利用頻度が高いユーザーだけでなく、月に数回利用するようなライトユーザーにも展開しやすくなります。 |
| **セキュリティ・ガバナンス / データ管理** | Amazon Bedrock では、プロンプト、ファイル、ツール入出力、モデル応答は、基盤モデルの改善目的で利用されず、モデルプロバイダーにも共有されません。なお、トークン数やエラーコードなどの集計テレメトリは送信される場合がありますが、設定で無効化可能です。また、CloudTrail による監査ログ、リージョン選択によるデータレジデンシーなど、AWS のセキュリティ・ガバナンス機能を活用しやすくなります。加えて、要件に応じて Amazon Bedrock Guardrails や LLM Gateway などを組み合わせることで、入出力制御やポリシー適用を設計しやすくなります。 |
| **請求・契約管理** | Claude の利用料を AWS 請求に統合できます。個人の立替精算や新たなベンダー契約を増やさず、既存の AWS アカウント、請求管理、予算管理の仕組みに乗せやすい点がメリットです。 |
| **スケール** | Amazon Bedrock 経由であれば、サブスクリプションプランのようなユーザー数上限に縛られにくく、必要なユーザーへ段階的に展開できます。Application Inference Profiles やコスト配分タグを活用することで、プロジェクト単位・チーム単位でのコスト可視化もしやすくなります。 |

特に大きいのは、**セキュリティ面とコスト面**です。

セキュリティ・ガバナンス面では、**Amazon Bedrock のデータ保護モデルを活用できる点が重要**です。業務資料やソースコードを扱う AI エージェントでは、プロンプトやファイル、モデル応答の扱いを説明できることが非常に重要です。Amazon Bedrock では、**顧客コンテンツが基盤モデルの改善に利用されず、モデルプロバイダーにも共有されない**と説明されており、企業利用において説明しやすいポイントになります。  
なお、データレジデンシー要件がある場合は、利用リージョンや推論プロファイルの設定も確認する必要があります。Cross-Region Inference を利用する場合、推論プロファイルに応じて複数の AWS リージョンへリクエストがルーティングされる可能性があります。必要に応じて地理的クロスリージョン推論を選択し、どのリージョンで処理されるかを確認しておくことが重要です。

コスト面では、**従量課金で利用**できるため、全員に固定ライセンスを割り当てるのではなく、実際の利用量に応じて費用を管理できます。Claude Code を日常的に使う開発者と、Claude Cowork を月に数回だけ使う業務ユーザーでは利用頻度が異なります。Amazon Bedrock 経由であれば、こうした**利用頻度の差を踏まえた展開がしやすく**なります。また、チーム単位やプロジェクト単位でコストを把握したい場合は、Application Inference Profiles とコスト配分タグを活用できます。一方で、個人単位やリクエスト単位の詳細な分析が必要な場合は、OpenTelemetry、IAM プリンシパル情報、model invocation logging などを組み合わせて設計する必要があります。

また、AWS の既存運用に乗せやすい点も大きなメリットです。IAM / IAM Identity Center による認証、CloudTrail による監査、CloudWatch によるメトリクス確認、必要に応じた Amazon Bedrock model invocation logging、AWS Budgets や Cost Explorer によるコスト管理など、既存の AWS 運用と組み合わせて利用できます。

つまり、Claude Cowork / Claude Code を Amazon Bedrock 経由で使う価値は、単に Claude を AWS から呼び出せることではありません。

業務ユーザー向けの Claude Cowork と、開発者向けの Claude Code を、**AWS のセキュリティ、認証、監査、請求管理の枠組みに寄せながら、安全かつ柔軟に利用できる**点にあります。

## 4. 認証方式

Claude Cowork / Claude Code を Amazon Bedrock 経由で利用する場合、まず「認証方式」と「接続・インフラ方式」を分けて考えると整理しやすいです。

### 認証方式の比較

| 認証方式 | 概要 | メリット | 注意点 | 向いている用途 |
| --- | --- | --- | --- | --- |
| **Amazon Bedrock API Key / Bearer Token** | Bedrock API Key をClaude DesktopやClaude Code に設定して利用する方式 | 最も簡単に試せる。セットアップが少なく、PoCの初期検証に向いている | 共有キーになりやすく、ユーザー単位の追跡、MFA、コスト配分の観点では弱い。本番・広範展開では慎重に扱う必要がある | 個人検証、短期PoC |
| **aws login** | AWS CLIの`aws login`を利用し、AWS マネジメントコンソールの認証情報を使う方式 | API Key を避けつつ、比較的簡単に検証できる | 小規模・限定的な利用向け。組織展開ではより管理しやすい方式を検討した方がよい | Claude Code の小規模検証 |
| **IAM Identity Center SSO / Named Profile** | AWS CLIのNamed profileとIAM Identity Centerを組み合わせて利用する方式 | 短期認証情報を利用でき、開発者に馴染みやすい。Claude Code との相性がよい | AWS CLI v2やprofile設定を各端末に配布・管理する必要がある | 開発者向け、Claude Code 利用 |
| **In-app AWS sign-in** | Claude Desktop内でIAM Identity Centerにサインインする方式 | AWS CLIが不要で、非エンジニアを含む業務ユーザーにも展開しやすい | IAM Identity Centerの設定やClaude Desktop側の管理対象設定を適切に配布する必要がある | 業務ユーザー向け、Claude Cowork展開 |
| **直接の IdP 統合** | Okta、Microsoft Entra ID、Auth0、Cognito などのIdP と OIDC 連携し、一時認証情報を発行する方式 | ユーザー属性、監査、OpenTelemetry、コスト配分を細かく扱いやすい | 構築・運用の難易度が高い | 大規模・高統制な本番展開 |

今回の検証では、セットアップのしやすさを重視して Amazon Bedrock API Key / Bearer Token 方式を利用しました。API Key 方式は最短で Claude Cowork / Claude Code を Amazon Bedrock 経由で動かせるため、PoC には向いています。

ただし、MFA なしの永続的なアクセス、手動配布、リポジトリへの誤コミット、ユーザー単位のモニタリングやコスト配分ができない点がリスクとなりますので、本番へ展開していく上では他方式を検討していく必要があります。

なお、Amazon Bedrock API Key には短期キーと長期キーがあります。短期 API Key はコンソールセッションの有効期限、最大 12 時間まで有効となり、長期 API Key は探索用途向けであり、本番環境では短期キーを使用するようAWS のドキュメントにも記載があります。詳細は[Amazon Bedrock API キー - Amazon Bedrock](https://docs.aws.amazon.com/ja_jp/bedrock/latest/userguide/api-keys.html)を参照してください。

### 本番利用での推奨

セキュリティレベルを考えると、以下のように使い分けるのがよいと考えます。

| 利用シーン | 推奨方式 |
| --- | --- |
| 個人検証・短期 PoC | Amazon Bedrock API Key / Bearer Token |
| API Key を避けた小規模検証 | aws login |
| 開発者向けの Claude Code 展開 | IAM Identity Center SSO / Named Profile |
| 業務ユーザー向けの Claude Cowork 展開 | In-app AWS sign-in + IAM Identity Center |
| 大規模・高統制な本番展開 | 直接の IdP 統合 |
| 独自ポリシーやマルチプロバイダー制御が必要 | LLM Gateway |

開発者向けには、AWS CLI や Named profile に慣れているケースが多いため、IAM Identity Center SSO / Named Profile が現実的です。IAM Identity Center を使うことで API Key を配布せずに企業の認証情報で Amazon Bedrock へアクセスできます。

一方、Claude Cowork を業務ユーザーに展開する場合は、AWS CLI の導入や profile 設定が負担になりやすいため、In-app AWS sign-in が有力です。この方式では、Claude Desktop 内で IAM Identity Center にサインインし、Cowork セッション開始時に短期 AWS 認証情報へ交換されます。AWS CLI が不要なため、非エンジニアを含む広範展開に向いています。

さらに、開発者ごとの詳細なモニタリング、部門・チーム単位のコスト配分、包括的な監査証跡が必要な場合は、直接の IdP 統合が候補になります。本番環境での Claude Code デプロイメントには、Okta、Microsoft Entra ID、Auth0、Cognito などとの直接的な OIDC 連携が推奨されています。

前述の認証方式とは別に、LLM Gateway を使う接続パターンもあります。LLM Gateway は、利用者と Amazon Bedrock の間に中間層を置き、リクエストを Gateway 経由でルーティングする構成です。マルチプロバイダー対応、独自のコンテンツフィルタリング、プロンプトインジェクション検知、IAM だけでは表現しづらいリクエスト単位の即時ブロックなどを実装したい場合に有効です。

ただし、Gateway を導入すると、ECS / EKS、ALB、キャッシュ、データベースなどの運用が追加され、レイテンシーや障害点も増えます。そのため、AWS 公式ブログでは、マルチプロバイダー対応、カスタムミドルウェア、IAM を超えたリクエストレベルのポリシー制御が必要な場合にのみ Gateway を検討すべきと整理されています。

### 接続・インフラ面の考慮

認証方式に加えて、本番環境へ展開していく上では接続・インフラ面の検討も必要です。

| 観点 | 内容 |
| --- | --- |
| **Amazon Bedrock Public Endpoint** | 多くの組織にとってまず検討しやすい標準構成 |
| **専用 AWS アカウント** | Claude Cowork / Claude Code 用の推論、監査、コストを分離しやすい |
| **Inference Profile** | チーム単位・プロジェクト単位のコスト追跡やクロスリージョン推論に利用。個人単位の詳細な追跡には向かないため、必要に応じて OpenTelemetry や IdP 連携と組み合わせる |
| **LLM Gateway** | 独自ポリシー、即時制御、マルチプロバイダー対応が必要な場合に利用 |

Amazon Bedrock のパブリックエンドポイントは、シンプルさ、AWS マネージドの信頼性、コストアラート、制御メカニズムのバランスを提供するため、多くの組織にとって有用となります。

また、Claude Code のようなコーディングアシスタントの推論は、開発環境や本番環境のワークロードとは別の専用 AWS アカウントに集約することが推奨されています。これにより、クォータ管理、コスト可視化、CloudTrail ログの集約、本番環境の保護がしやすくなります。

## 5. セットアップ

今回は PoC として、Amazon Bedrock API Key / Bearer Token 方式で Claude Cowork / Claude Code を Amazon Bedrock 経由で利用しました。なお、本番利用では IAM Identity Center SSO や In-app AWS sign-in など、ユーザー単位で管理できる認証方式を検討するのがよいと考えます。

### Step1 Amazon Bedrock でのモデル有効化

まず、Amazon Bedrock で利用する Claude モデルを有効化します。

Amazon Bedrock コンソールから、利用したい Claude モデルのアクセスを有効化し、実際に呼び出せることを確認します。あわせて、利用するリージョンと Claude Desktop 側に設定するリージョンが一致していることも確認します。

![](https://static.zenn.studio/user-upload/0c5f84f3bef9-20260710.png)

新規の AWS アカウントではサービスクォータが低い、または 0 になっている場合もあるため、必要に応じて Quota も確認しておくとよいです。

### Step2 IAM ポリシー・IAM ユーザーの作成（長期 API Key 方式の場合）

次に、Amazon Bedrock API Key / Bearer Token 方式で利用するための IAM ポリシーと IAM ユーザーを作成します。

必要な権限として、Amazon Bedrock のモデル呼び出しに利用する `bedrock:InvokeModel`、`bedrock:InvokeModelWithResponseStream`、Bearer Token 認証に利用する `bedrock:CallWithBearerToken` などを付与します。

![](https://static.zenn.studio/user-upload/3b3e207d089f-20260711.png)

その後、作成した IAM ユーザーから Amazon Bedrock API Key を発行し、Claude Desktop 側に設定する Bearer Token として利用します。

![](https://static.zenn.studio/user-upload/77045d12b8b3-20260711.png)

![](https://static.zenn.studio/user-upload/d1b9bd7b62ac-20260711.png)

![](https://static.zenn.studio/user-upload/068e766adc36-20260711.png)

### Step3 仮想マシンプラットフォームの有効化

Windows 環境で Claude Cowork を利用する場合は、Windows の「仮想マシンプラットフォーム」を有効化します。

![](https://static.zenn.studio/user-upload/ae77dab6b395-20260710.png)

Claude Cowork は内部的にローカルの仮想環境を利用するため、Windows の機能として仮想マシンプラットフォームを有効にしておく必要があります。設定変更後は、必要に応じて端末を再起動します。

### Step4 Claude Desktop のインストールと設定

Claude Desktop をインストールし、サードパーティ推論の設定で Amazon Bedrock を指定します。

Claude Desktop を起動後、開発者モードを有効化し、「サードパーティ推論を設定」から Provider として Bedrock を選択します。その後、AWS リージョン、Bearer Token、利用するモデル ID などを設定し、接続テストを実施します。

![](https://static.zenn.studio/user-upload/de9e2fd2c0f1-20260710.png)

![](https://static.zenn.studio/user-upload/fbad5564a194-20260710.png)

![](https://static.zenn.studio/user-upload/879bcd959bdb-20260710.png)

![](https://static.zenn.studio/user-upload/c9793dba699e-20260710.png)

接続テストが成功したら、設定を適用して Claude Desktop を再起動します。これにより、Claude Desktop から Amazon Bedrock 経由で Claude モデルを利用できるようになります。

### Step5 Git for Windows の設定

Windows 環境で Claude Code を利用する場合は、Git for Windows をインストールします。

Claude Code は bash 環境を利用するため、Git Bash を含む Git for Windows が必要になります。インストール後、必要に応じて `CLAUDE_CODE_GIT_BASH_PATH` などの環境変数を設定し、Claude Code が Git Bash を参照できるようにします。

なお、この手順は Claude Code を利用する場合の追加設定です。Claude Cowork のみを試す場合は、必須ではありません。

### Step6 Claude Cowork / Claude Code の試用

最後に、Claude Cowork / Claude Code が Amazon Bedrock 経由で動作することを確認します。

![](https://static.zenn.studio/user-upload/e3005324e2ea-20260710.png)

![](https://static.zenn.studio/user-upload/23927b26328a-20260710.png)

## 6. 本番展開時に考えること

ここまで、Claude Cowork / Claude Code を Amazon Bedrock 経由で利用する理由や接続方式を整理してきました。

PoC や個人検証であれば、Amazon Bedrock API Key / Bearer Token を使うことで比較的簡単に動作確認できます。一方で、本番環境や組織展開を考える場合は、「接続できた」だけでは不十分です。

Claude Cowork は業務資料やローカルファイルを扱い、Claude Code はソースコードや開発環境に近い領域を扱います。そのため、通常のチャット型 AI よりも、認証、権限、データ境界、監査、コスト、端末管理をしっかり設計する必要があります。

本番展開時に特に考えるべき観点は以下です。

| 観点 | 考えるべきこと |
| --- | --- |
| 認証・認可 | API Key の長期共有は避け、IAM Identity Center SSO、In-app AWS sign-in、Named Profile などユーザー単位で管理できる方式を検討する |
| データ境界 | プロンプト、ファイル、ソースコード、モデル応答、ログがどこに保存・送信されるかを整理する |
| 監査・ログ | CloudTrail、CloudWatch、Bedrock model invocation logging などで何を記録するか、誰が閲覧できるかを決める。特に Amazon Bedrock model invocation logging を有効化する場合は、モデル入力・出力がログに含まれる可能性があるため、保存先、アクセス権限、保持期間を事前に設計する |
| ネットワーク | Bedrock の Public Endpoint を使うのか、Gateway / Proxy / VPC Endpoint 経由にするのかを整理する |
| MCP・ツール連携 | 許可する MCP Server、外部接続先、ローカルファイルアクセス範囲を管理する |
| コスト管理 | 利用量が増えた場合に備え、AWS Budgets、Cost Explorer、Application Inference Profiles、コスト配分タグを活用し、部門・チーム単位のコスト配賦を検討する |
| 端末管理 | Claude Desktop の配布、設定、アップデート、許可フォルダ、プロキシ設定を MDM などで管理する |
| 利用ルール | 入力してよい情報、生成物のレビュー、禁止事項、問い合わせ先を明確にする |

特に重要なのは、API Key での検証環境をそのまま本番運用に持ち込まないことです。API Key は PoC では便利ですが、ユーザー単位の追跡、MFA、退職・異動時の権限停止、コスト配分の観点では課題が出やすくなります。

そのため、本番では以下のように利用者に応じて方式を分けるのが現実的だと考えます。

| 利用シーン | 推奨方式 |
| --- | --- |
| 個人検証・短期 PoC | Amazon Bedrock API Key / Bearer Token |
| 開発者向けの Claude Code 利用 | IAM Identity Center SSO / Named Profile |
| 業務ユーザー向けの Claude Cowork 利用 | In-app AWS sign-in + IAM Identity Center |
| 大規模・高統制な展開 | 直接の IdP 統合を基本に検討 |
| 独自ポリシー、即時ブロック、マルチプロバイダー制御が必要な場合 | LLM Gateway |

Claude Cowork / Claude Code を Amazon Bedrock 経由で使う価値は、単に Claude を AWS から呼び出せることではありません。業務ユーザー向けの Cowork と、開発者向けの Claude Code を、AWS の認証、監査、ネットワーク、コスト管理の仕組みに乗せながら、安全に組織展開しやすくなる点にあります。

したがって、まずは API Key で素早く試し、その後は IAM Identity Center、ログ設計、端末管理、MCP 制御、コスト管理を整備しながら、段階的に展開していくのがよいと考えます。

## 7. まとめ

本記事では、Claude Cowork / Claude Code を Amazon Bedrock 経由で利用する理由について整理しました。

Claude Cowork / Claude Code は、業務資料の整理や分析、資料作成、コード調査、実装支援などを AI エージェントに委任できる強力なツールです。一方で、企業で利用する場合は「便利に使えるか」だけでなく、認証、データ境界、監査、コスト管理、端末管理といった観点をあわせて考える必要があります。

Amazon Bedrock 経由で利用することで、Claude のエージェント体験を AWS の認証、監査、請求、ネットワーク設計の枠組みに寄せやすくなります。

今回の検証では API Key / Bearer Token 方式を利用しましたが、本番展開では利用者や用途に応じて、IAM Identity Center SSO / Named Profile、In-app AWS sign-in、直接の IdP 統合、LLM Gateway などを検討するのがよいと考えます。

まずは小さく試しつつ、PoC で終わらせず、認証方式・ログ設計・コスト管理・利用ルールを整備しながら段階的に展開していくことが重要です。
