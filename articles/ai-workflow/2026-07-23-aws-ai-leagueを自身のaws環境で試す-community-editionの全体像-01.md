---
id: "2026-07-23-aws-ai-leagueを自身のaws環境で試す-community-editionの全体像-01"
title: "AWS AI Leagueを自身のAWS環境で試す ─ Community Editionの全体像"
url: "https://zenn.dev/nttdata_tech/articles/402acac4a19180"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "API", "AI-agent", "Python", "zenn"]
date_published: "2026-07-23"
date_collected: "2026-07-24"
summary_by: "auto-rss"
query: ""
---

## 1. はじめに

以前、以下の記事でAWS AI Leagueについて紹介しました。

<https://zenn.dev/nttdata_tech/articles/a907eb00cbbe4b>

AWS AI Leagueは、競技形式で生成AIの技術を学ぶプログラムです。主に、次の2つのテーマが用意されています。

* Amazon SageMaker AIを利用したモデルのファインチューニング
* Amazon Bedrock AgentCoreを利用したAgentic AI

Agentic AIチャレンジでは、AIエージェントがマップ上を移動し、コインの取得や質問への回答などを行いながら、宝箱への到達を目指します。ゲーム形式で楽しみながらAIエージェントについて学べる一方、イベントの時間内にエージェント、ツール、Memory、Guardrailsなどを理解し、改善するのは簡単ではありません。

そこで、AWS AI/ML Communityから、AWS AI Leagueの練習環境を自分のAWSアカウントに構築できるオープンソースプロジェクトが公開されました。

本記事では、**AWS AI League Community Edition**の全体像を紹介します。

AWS AI League Community Editionは、AWS AI Leagueで扱われる技術を、イベント開催時以外にも練習するためのオープンソースです。以下のGitHubリポジトリで公開されています。

<https://github.com/aws-ai-community/ai-league-community-edition>

Community Editionを自分のAWSアカウントへデプロイすると、ブラウザからマップやAIエージェントを設定し、ゲーム形式でエージェントを実行できます。

2026年6月に公開された紹介記事では、主にAgentic AIチャレンジの練習環境として紹介されていました。その後も開発が進み、現行版にはファインチューニングを支援する機能も追加されています。

Community Editionでは、大きく分けて次の2つを試せます。

### 3.1 Agentic AI

Agentic AIでは、マップ上を移動するAIエージェントを構築・実行できます。

主な機能は以下です。

| 機能 | 概要 |
| --- | --- |
| Map Builder | カスタムダンジョンマップを作成する |
| Agent Builder | Supervisor、Sub-agent、ツールなどを設定する |
| Gameplay | エージェントをマップ上で実行する |
| Leaderboard | マップごとのスコアを確認する |

初期構成では、Supervisor Agentが経路探索用のSub-agentへ処理を委譲し、Sub-agentがAgentCore Gateway経由でLambdaツールを呼び出します。

最初からすべてを作る必要はなく、用意された構成をベースに、プロンプトやモデル、ツールなどを変更できます。

なお、Community Editionとは別に、過去のAI Leagueで使用されたマップやチャレンジ定義も公開されています。  
<https://github.com/aws-ai-community/ai-league-competition-data>

リポジトリには、主に次のデータが含まれています。

* マップ定義やチャレンジ定義を含むJSON
* マップを可視化した画像
* スコアリングパラメータ
* 大会やマップの概要を記載したREADME

これらのデータをCommunity Editionへ読み込むことで、過去大会で使用されたマップを使ったエージェントの実行や評価を試すことができます。ただし、公式大会環境そのものを再現するものではなく、過去大会のマップや設定を使って、自分のエージェントを検証するためのデータです。

### 3.2 ファインチューニング

現行版には、ファインチューニングを支援する画面とサンプルデータも用意されています。主な流れは以下です。

1. サンプルの学習データを取得する
2. SageMaker AIでモデルを学習する
3. 完了した学習ジョブをCommunity Editionへ登録する
4. Bedrock Custom Model Importを利用してデプロイする
5. Agent Builderでデプロイ済みモデルを選択する

なお、Community Editionでは、Tool CallとFaithfulnessを対象とした学習データやReward Functionが提供されています。それぞれのReward Functionを利用してモデルの出力を評価しながら、SageMaker AIでファインチューニングを試すことができます。

## 4. システム構成

Community Editionは、Amazon Bedrock AgentCoreを中心としたAgentic AIの実行環境に加えて、マップやゲーム情報を管理するWebアプリケーション、SageMaker AIを利用したファインチューニング機能など、複数のAWSサービスを組み合わせて構築されています。

以下は、GitHub READMEに記載されているアーキテクチャを、本記事向けに簡略化したものです。

![](https://static.zenn.studio/user-upload/115668cb7c7e-20260718.png)

本構成から、Community Editionはゲーム用のWeb画面だけでなく、サーバーレスバックエンド、マルチエージェント、MCPによるツール連携、モデルのファインチューニングまでを組み合わせた学習環境であることが分かります。

### 4.1 Web画面とユーザー認証

Community EditionのWebコンテンツはAmazon S3に配置され、Amazon CloudFrontを介してブラウザへ配信されます。ユーザー認証にはAmazon Cognitoが利用されており、ログインしたユーザーごとにプロフィールやエージェント設定などを管理できます。

### 4.2 REST APIとGraphQL API

バックエンドは、大きく2つのAPIに分かれています。

| API | 主に管理する情報 |
| --- | --- |
| Amazon API GatewayによるREST API | マップ、ユーザープロフィール |
| AWS AppSyncによるGraphQL API | ゲームセッション、リーダーボード、提出履歴、エージェント設定 |

REST APIのバックエンドにはNode.jsで実装されたAWS Lambdaが、GraphQL APIのバックエンドにはPythonで実装されたAWS Lambdaが利用されています。

マップ、ユーザープロフィール、ゲームセッション、リーダーボード、提出履歴、エージェント設定などの情報は、Amazon DynamoDBに保存されます。

### 4.3 Agentic AIの実行

ゲーム実行時には、Game Runner LambdaからAmazon Bedrock AgentCore Runtimeが呼び出され、Runtime上のコンテナでSupervisor Agentが実行されます。

Supervisor Agentは、Strands Agents SDKのツール呼び出しを利用して、経路探索をPathfinder Sub-agentへ委譲します。

Pathfinder Sub-agentは、AgentCore Gatewayを介して、Pathfinder LambdaをMCP（Model Context Protocol）ツールとして呼び出します。

### 4.4 ファインチューニングとの連携

ファインチューニングでは、Amazon SageMaker StudioからSageMaker AIの学習ジョブを実行します。

Community Editionには、Tool CallとFaithfulnessを対象としたサンプルの学習データ、評価データ、Reward Functionが用意されており、Amazon S3から取得できます。

SageMaker AIで学習が完了した後は、学習ジョブをCommunity Editionへ登録します。登録されたモデルは、Bedrock Custom Model Importを利用してデプロイできます。

## 5. 利用前に確認すべきこと

Community Editionを利用する際は、以下に注意が必要です。

### 5.1 利用リージョン

本ブログ執筆時点では、バージニア北部リージョンのみ対応しています。東京リージョンではない点に注意が必要です。

### 5.2 デプロイ環境

環境構築には、主に以下が必要です。

* Node.js 22以上
* Python 3.12以上
* AWS CLI
* AWS CDK
* Docker
* 各AWSリソースを作成できるIAM権限

Community Editionをデプロイすると、Amazon Cognito、Amazon DynamoDB、AWS AppSync、AWS Lambda、Amazon CloudFront、Amazon Bedrock AgentCoreなど、複数のAWSリソースが作成されます。

また、ファインチューニングを利用する場合は、バージニア北部リージョンで、SageMaker AIのモデルカスタマイズ用サーバーレスジョブに関するクォータ引き上げが必要です。

### 5.3 概算費用

GitHubリポジトリに記載されている概算費用は以下です。

| 対象 | 概算費用 |
| --- | --- |
| 基盤の維持 | 約2ドル／月 |
| ゲームの実行 | 約0.15～0.70ドル／回 |
| ファインチューニング | 約30ドル／モデル |

実際の費用は、利用するモデル、トークン数、ゲームの実行回数、学習設定などによって変動します。特に高価格帯のモデルを利用する場合は、ゲーム1回あたりの費用が大きくなる可能性があります。検証前にAWS Budgetsなどを設定しておくと安心です。

## 6. まとめ

本記事では、AWS AI League Community Editionの概要とシステム構成、利用前に確認しておきたいポイントを紹介しました。

Community Editionを利用することで、自分のAWSアカウントに練習環境を構築し、AWS AI Leagueで扱われるAgentic AIやモデルのファインチューニングを、イベント開催時以外にも試すことができます。

Agentic AIでは、過去大会で使用されたマップを使ったチャレンジに加えて、オリジナルマップの作成、Supervisor AgentやSub-agentの設定、ツール、Memory、Guardrailsの組み込みなどを試せます。また、現行版では、SageMaker AIによるファインチューニングとBedrock Custom Model Importを利用したカスタムモデルのデプロイにも対応しています。

次回以降の記事では、自分のAWSアカウントへのデプロイ手順や、Agentic AIおよびファインチューニングの具体的な検証結果を紹介する予定です。
