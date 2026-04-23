---
id: "2026-03-25-deploy-to-awsの一言でaiがawsインフラ構築からデプロイまで完了する時代が来た-01"
title: "「Deploy to AWS」の一言でAIがAWSインフラ構築からデプロイまで完了する時代が来た"
url: "https://qiita.com/miruky/items/74af8cae780f50f1a7f8"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "AI-agent", "qiita"]
date_published: "2026-03-25"
date_collected: "2026-03-26"
summary_by: "auto-rss"
---

## はじめに

こんばんは、mirukyです。

2026年2月17日、AWSが**Agent Plugins for AWS**を公開しました。Claude CodeやCursorに「Deploy this app to AWS」と一言伝えるだけで、AIエージェントが**アーキテクチャ設計 → コスト見積もり → IaCコード生成 → デプロイ実行**まで自動で行ってくれるという、衝撃的なツールです。

初回リリースの`deploy-on-aws`プラグインに続き、サーバーレスやAmplify等の追加プラグインも順次公開。さらに2026年3月にはMicrosoftも**Azure Skills Plugin**を公開し、AWS・Azure両クラウドで「AIにインフラ構築を任せる時代」が本格的に始まりました。

本記事では、Agent Plugins for AWSの仕組み・使い方・注意点をコンパクトにまとめます。

出典：[Introducing Agent Plugins for AWS - AWS Blog](https://aws.amazon.com/blogs/developer/introducing-agent-plugins-for-aws/) / [Agent Plugins for AWS - GitHub](https://github.com/awslabs/agent-plugins)

## 目次

1. Agent Plugins for AWSとは
2. 構成コンポーネント
3. 利用可能なプラグイン一覧
4. deploy-on-awsプラグインの動作フロー
5. インストール方法
6. Azure Skills Pluginとの比較
7. 利用時の注意点とベストプラクティス

## 1. Agent Plugins for AWSとは

### 1-1. 概要

Agent Plugins for AWSは、**AIコーディングエージェントにAWS上での設計・デプロイ・運用のスキルを付与するオープンソースのプラグイン集**です。

| 項目 | 内容 |
| --- | --- |
| **公開日** | 2026年2月17日（AWS Developer Tools Blog） |
| **リポジトリ** | [awslabs/agent-plugins](https://github.com/awslabs/agent-plugins)（Apache-2.0ライセンス） |
| **対応ツール** | Claude Code（>=2.1.29）、Cursor（>=2.5） |
| **前提条件** | AWS CLIが適切なクレデンシャルで設定済みであること |

### 1-2. なぜ生まれたのか

従来、AIコーディングエージェントにAWSの知識を与えるには、長大なAWSガイダンスをプロンプトに貼り付ける必要がありました。これには以下の問題があります。

* **コンテキストの肥大化**：トークンを大量に消費する
* **再現性の低さ**：毎回同じ品質のガイダンスを与えられない
* **チーム間の標準化が困難**：各人が異なるプロンプトを使用

Agent Pluginsは、AWSのベストプラクティスを**再利用可能でバージョン管理されたスキル**としてパッケージ化し、これらの課題を解決します。

出典：[Introducing Agent Plugins for AWS - AWS Blog](https://aws.amazon.com/blogs/developer/introducing-agent-plugins-for-aws/)

## 2. 構成コンポーネント

### 2-1. プラグインの構成要素

Agent Pluginsは、4種類のコンポーネントで構成されています。

| コンポーネント | 役割 | 具体例 |
| --- | --- | --- |
| **Agent Skills** | ベストプラクティスやワークフローをステップバイステップで定義 | デプロイ手順、コードレビュー、アーキテクチャ設計 |
| **MCP Servers** | 外部データソースやAPIへの接続 | AWSドキュメント参照、リアルタイム料金取得、IaCベストプラクティス |
| **Hooks** | ワークフローの自動化とガードレール | SAMテンプレートのバリデーション、スキーマ変更の確認 |
| **References** | エージェントが参照するドキュメントや設定情報 | 設定デフォルト値、補足ドキュメント |

**MCPサーバとは**  
MCP（Model Context Protocol）は、AIモデルが外部サービスやデータソースに接続するためのプロトコルです。Agent Plugins for AWSでは、[AWS MCP Servers](https://github.com/awslabs/mcp)（PyPIダウンロード数3,000万以上）を活用して、リアルタイムの料金情報やドキュメントを取得します。

## 3. 利用可能なプラグイン一覧

2026年3月25日時点で、以下の6つのプラグインが利用可能です。

| プラグイン | 概要 | 状態 |
| --- | --- | --- |
| **deploy-on-aws** | AWS上へのデプロイ（設計・見積もり・IaC生成・実行） | Available |
| **aws-serverless** | Lambda、API Gateway、EventBridge、Step Functionsによるサーバーレス開発 | Available |
| **aws-amplify** | Amplify Gen 2によるフルスタックアプリ開発 | Available |
| **amazon-location-service** | 地図、ジオコーディング、ルート検索等の地理空間機能 | Available |
| **databases-on-aws** | AWSデータベースの設計・クエリ・マイグレーション支援 | 一部利用可能（Aurora DSQL） |
| **migration-to-aws** | GCPからAWSへの移行支援 | Available |

**今後さらにプラグインが追加予定**  
AWS公式ブログでは「more agent plugins for AWS are launching soon」と記載されており、今後もプラグインの追加が予定されています。リポジトリをWatchしておくと最新情報をキャッチできます。

## 4. deploy-on-awsプラグインの動作フロー

### 4-1. 5ステップの自動ワークフロー

`deploy-on-aws`プラグインは、以下の5ステップでアプリケーションのデプロイを実行します。

```
Step 1：Analyze（解析）
  ↓  コードベースをスキャン、フレームワーク・DB・依存関係を特定
  ↓
Step 2：Recommend（推奨）
  ↓  最適なAWSサービスを選定し、根拠とともに提示
  ↓
Step 3：Estimate（見積もり）
  ↓  リアルタイム料金データから月額コストを算出
  ↓
Step 4：Generate（生成）
  ↓  CDK or CloudFormationのIaCコード、Dockerfile等を生成
  ↓
Step 5：Deploy（デプロイ）
     ユーザー確認後、AWSリソースをプロビジョニング
```

### 4-2. 具体的な利用例

Express.js + PostgreSQL + Reactのフルスタックアプリを例にします。

ユーザーが以下のように指示するだけです。

```
Deploy this Express app to AWS
```

すると、AIエージェントが以下の構成を**自動で推奨**します。

| 用途 | 推奨されるAWSサービス |
| --- | --- |
| **バックエンド実行環境** | AWS App Runner（オートスケーリング・マネージドコンテナ） |
| **データベース** | Amazon RDS PostgreSQL（マネージド・自動バックアップ） |
| **フロントエンド配信** | Amazon CloudFront + S3（グローバルCDN） |
| **認証情報管理** | AWS Secrets Manager |

### 4-3. 生成されるアーティファクト

AIエージェントが自動生成するファイルは以下です。

| アーティファクト | 内容 |
| --- | --- |
| **IaCコード** | AWS CDK（TypeScript）によるインフラ定義 |
| **Dockerfile** | アプリケーション用のコンテナ定義 |
| **マイグレーションスクリプト** | データベース移行用スクリプト |
| **環境設定** | 環境変数やシークレット設定 |
| **CI/CDワークフロー** | GitHub Actionsによる自動デプロイ |

### 4-4. MCPサーバの役割

`deploy-on-aws`プラグインは3つのMCPサーバを使用してリアルタイム情報を取得します。

| MCPサーバ | 役割 |
| --- | --- |
| **AWS Knowledge** | AWSドキュメント、アーキテクチャガイダンス、ベストプラクティス |
| **AWS Pricing** | リアルタイムのサービス料金情報（見積もり用） |
| **AWS IaC** | CDK / CloudFormationのベストプラクティス |

**「個別の能力だけを呼び出す」ことも可能**  
deploy-on-awsプラグインは一連のワークフローだけでなく、個別のステップだけの実行も可能です。

* `AWS architecture for this app`：アーキテクチャ設計のみ
* `Estimate AWS cost`：コスト見積もりのみ
* `Generate infrastructure`：IaCコード生成のみ

出典：[Agent Plugins for AWS - GitHub](https://github.com/awslabs/agent-plugins)

## 5. インストール方法

### 5-1. Claude Codeの場合

```
# マーケットプレイスを追加
/plugin marketplace add awslabs/agent-plugins

# deploy-on-awsプラグインをインストール
/plugin install deploy-on-aws@agent-plugins-for-aws
```

他のプラグインも同様にインストールできます。

```
# サーバーレス開発プラグイン
/plugin install aws-serverless@agent-plugins-for-aws

# Amplifyプラグイン
/plugin install aws-amplify@agent-plugins-for-aws

# GCP→AWS移行プラグイン
/plugin install migration-to-aws@agent-plugins-for-aws
```

### 5-2. Cursorの場合

1. **Cursor Settings** を開く
2. **Plugins** に移動
3. 検索バーで `AWS` と検索
4. インストールしたいプラグインを選択し **「Add to Cursor」** をクリック
5. スコープを選択

[Cursor Marketplace](https://cursor.com/marketplace/aws)からも直接インストール可能です。

**前提条件**

* Claude Code **2.1.29以上** / Cursor **2.5以上**
* **AWS CLI**が適切なクレデンシャルで設定済みであること

AWS CLIの設定がまだの場合は、以下のコマンドで設定してください。

## 6. Azure Skills Pluginとの比較

2026年3月25日、Microsoftも同様の**Azure Skills Plugin**を公開しました。AWSとAzureの両社がほぼ同時に「AIエージェントによるインフラ自動構築」を実現したことになります。

| 比較項目 | Agent Plugins for AWS | Azure Skills Plugin |
| --- | --- | --- |
| **公開日** | 2026年2月17日 | 2026年3月25日 |
| **対応ツール** | Claude Code、Cursor | GitHub Copilot（VS Code / CLI）、Claude Code |
| **プラグイン数** | 6（deploy、serverless、amplify、location、databases、migration） | 20種類のスキルファイル |
| **MCPサーバ** | AWS Knowledge、AWS Pricing、AWS IaC 等 | Azure MCP Server（40以上のサービス接続）、Foundry MCP |
| **IaCツール** | AWS CDK / CloudFormation | Bicep |
| **移行支援** | GCPからAWSへの移行プラグインあり | ― |
| **AI特化** | ― | Foundry MCPでAIモデルカタログ・エージェント管理 |
| **リポジトリ** | [awslabs/agent-plugins](https://github.com/awslabs/agent-plugins) | [microsoft/azure-skills](https://github.com/microsoft/azure-skills) |

**クラウド2大巨頭が同じ方向に動いている**  
AWS・Azureの両社が同時期にAIエージェントプラグインをリリースしたことは、「AIエージェントがインフラ構築の入口になる」というトレンドが業界全体で加速していることを示しています。今後、Google Cloud（GCP）も同様の動きを見せる可能性が高いでしょう。

## 7. 利用時の注意点とベストプラクティス

### 7-1. セキュリティに関する重要事項

**AWS公式の注意事項**  
Agent Plugins for AWSのREADMEには以下の注意書きが明記されています。

> Generative AI can make mistakes. You should consider reviewing all output and costs generated by your chosen AI model and agentic coding assistant.

生成AIは間違いを犯す可能性があります。AIモデルが生成したすべての出力とコストを確認してください。

出典：[Agent Plugins for AWS - README](https://github.com/awslabs/agent-plugins)

### 7-2. ベストプラクティス

AWS公式ブログが推奨するベストプラクティスを表にまとめます。

| プラクティス | 内容 |
| --- | --- |
| **デプロイ前に必ずレビュー** | 生成されたIaCコードをセキュリティ・コスト・レジリエンスの観点で確認する |
| **アクセラレータとして使う** | プラグインは開発者の判断・専門知識の「代替」ではなく「加速器」 |
| **プラグインを最新に保つ** | 最新のAWSベストプラクティスを反映するため定期的に更新する |
| **最小権限の原則を遵守** | AWSクレデンシャルの設定時に必要最小限の権限のみ付与する |
| **セキュリティスキャンを実施** | 生成されたIaCコードに対してセキュリティスキャンツールを実行する |

### 7-3. 「AIに任せて終わり」にしない

Agent Plugins for AWSは非常に強力なツールですが、AIが推奨するアーキテクチャやコストが**常に最適とは限りません。** 特に以下の観点は人間が確認すべきです。

| 確認ポイント | なぜ重要か |
| --- | --- |
| **コスト最適化** | 見積もりはリアルタイム料金に基づくが、リザーブドインスタンスやSavings Plans等は考慮されない可能性がある |
| **セキュリティ設計** | セキュリティグループ、IAMポリシー、暗号化設定が適切か |
| **スケーラビリティ** | 実際のトラフィックパターンに合ったオートスケーリング設計か |
| **コンプライアンス** | 業界規制やデータ所在地の要件を満たしているか |

## おわりに

ここまでお読みいただきありがとうございます。

Agent Plugins for AWSのポイントをまとめます。

* **「Deploy to AWS」の一言**でAIがアーキテクチャ設計からデプロイまで自動実行
* **6つのプラグイン**でデプロイ・サーバーレス・Amplify・地理空間・データベース・移行をカバー
* **MCPサーバ**経由でリアルタイム料金・公式ドキュメント・IaCベストプラクティスを参照
* Claude Code と Cursor で利用可能、**Azure Skills Pluginも同時期にリリース**

AIエージェントがインフラ構築のフロントエンドになる時代が来ています。ただし、生成されたコードの**レビューとセキュリティ確認は必ず人間が行いましょう。**

ではまた、お会いしましょう。

## 参考リンク

### 公式リソース

### ドキュメント

### 関連ニュース
