---
id: "2026-07-08-aws-finops-agentで始める継続的なコスト監視-01"
title: "AWS FinOps Agentで始める継続的なコスト監視"
url: "https://zenn.dev/nttdata_tech/articles/52ea31c75ff74c"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "zenn"]
date_published: "2026-07-08"
date_collected: "2026-07-09"
summary_by: "auto-rss"
query: ""
---

## 1. はじめに

AWS（Amazon Web Services）のコスト管理では、Cost Explorer、Cost Anomaly Detection、Cost Optimization Hub、Compute Optimizerなど、目的に応じたさまざまなサービスが提供されています。

また、最近ではAmazon Qを利用して、AWSマネジメントコンソール上から自然言語でコストに関する質問を行うこともできるようになってきました。そのため、「Cost ExplorerやAmazon Qがある中で、AWS FinOps Agentは何が違うのか？」と感じる方もいるのではないでしょうか。

AWS FinOps Agentは、2026年6月にプレビューとして発表された、FinOps担当者やエンジニアリングチーム向けのエージェントです。コストに関する問い合わせ、最適化機会の発見、コスト異常の調査、定期的なFinOpsワークフローの実行などを支援します。

本記事では、AWS FinOps Agentの概要、Cost ExplorerやAmazon Qとの違い、セットアップ手順、実際に想定されるユースケースについて整理します。特に、単発のコスト確認だけでなく、定期レポートや異常検知後の調査、Slack/Jira連携など、FinOps業務を継続的に回す観点でどのように活用できるかを見ていきます。

なお、AWS FinOps Agentは本記事執筆時点ではプレビュー機能のため、今後仕様が変更される可能性があります。最新情報は公式ドキュメントもあわせて確認してください。

## 2. AWS FinOps Agentとは

AWS FinOps Agent は、AWSコストの問い合わせ、異常調査、最適化機会の発見、レポート生成を支援するフロンティアエージェントです。チャットからコスト質問を行えるだけでなく、コスト異常の根本原因調査、最適化レコメンドの抽出、HTML/PDF/PPT形式のレポート生成、JiraやSlack連携まで扱える点が特徴です。

![](https://static.zenn.studio/user-upload/1d4626ac005d-20260705.png)

## 3. Cost Explorer / Amazon Q / FinOps Agent

AWS FinOps AgentはCost Explorerなどを内部的に活用しながら、質問回答、異常調査、最適化推奨、レポート生成を行います。Amazon QがAWSマネジメントコンソール上で手軽に聞けるのに対して、AWS FinOps Agentはタスク、スケジュール実行、イベントトリガー実行などを通じて、FinOps業務そのものを継続的に回すための仕組みを提供している点が特徴です。

たとえば、「先月のコスト増加要因を教えて」とその場で質問するだけでなく、「毎週月曜日に前週のコスト傾向をまとめる」、「Cost Anomaly Detectionで異常が検出されたら原因を調査する」、「調査結果をSlackに通知する」、「必要に応じてJiraチケットを作成する」といった運用フローまでエージェントに任せることができます。

つまり、Cost Explorerがコストを“見る”ためのサービス、Amazon Qがコストについて“聞く”ための体験だとすると、AWS FinOps Agentはコスト調査や最適化のアクションを“業務として実行する”ためのエージェントと捉えることができます。

| 観点 | Cost Explorer | Amazon Qのコスト機能 | AWS FinOps Agent |
| --- | --- | --- | --- |
| 主な使い方 | コスト・使用量の可視化、分析 | 自然言語でのコスト質問、見積もり、分析支援 | FinOps業務の実行・自動化 |
| 向いている場面 | 数値を正確に確認したい | すぐ質問して概要を掴みたい | 調査、レポート、通知、チケット化まで回したい |
| 強み | 信頼できる一次画面 | コンソール上で手軽に聞ける | タスク、スケジュール、イベントトリガー、成果物管理 |
| 実務での位置づけ | 分析画面 | アドホック相談役 | 継続運用のエージェント |

## 4. AWS FinOps Agentの主なユースケース

### 4.1　コスト関連の問い合わせ

データソース：  
・ AWS Cost Explorer  
・ AWS Cost Anomaly Detection  
・ AWS Cost Optimization Hub  
・ AWS Compute Optimizer

### 4.2　コストの異常調査

データソース：  
・ AWS Cost Explorer  
・ AWS CloudTrail

### 4.3　推奨コスト最適化問い合わせ

データソース：  
・ AWS Compute Optimizer

### 4.4　コスト最適化レポート作成

対応ファイル：  
・ HTML  
・ PDF  
・ PPT

## 5. WebアプリケーションUI

AWSマネジメントコンソールとは独立したWebアプリケーションUIを提供し、エージェントとの対話やコスト調査の指示や分析結果を確認することができます。

| メニュー | 説明 |
| --- | --- |
| Chat | コストに関する質問や指示を自然言語で行う |
| Tasks | レポート生成や異常調査など、時間のかかる処理をバックグラウンド実行 |
| Automations | 定期実行やイベントトリガー実行を管理 |
| Artifacts | HTML / PDF / PPT などの生成レポートを確認・ダウンロード |
| Context files | 組織固有のアカウント情報やルールをアップロード |

![](https://static.zenn.studio/user-upload/79d6138b0d3e-20260705.png)

## 6. セットアップ手順

### 6.1 US East(N. Virginia)でAWS FinOps Agentを開く

![](https://static.zenn.studio/user-upload/b9036c22768b-20260705.png)

![](https://static.zenn.studio/user-upload/4518f6943c84-20260705.png)

### 6.2 Agentの作成 / ロールの設定

![](https://static.zenn.studio/user-upload/2a5486e1e186-20260705.png)

![](https://static.zenn.studio/user-upload/4ebd4f54f8c1-20260705.png)

![](https://static.zenn.studio/user-upload/ae490dddb439-20260705.png)

![](https://static.zenn.studio/user-upload/4c69d2b68a98-20260705.png)

![](https://static.zenn.studio/user-upload/90886bf6ffab-20260705.png)

### 6.3 Webアプリケーションを開く

![](https://static.zenn.studio/user-upload/0a542aa5ce1d-20260705.png)

![](https://static.zenn.studio/user-upload/e0f6da6b43f2-20260705.png)

## 7. 様々なユースケースでの活用

### 7.1 コスト関連の問い合わせ

まずは単純にコストに関する問い合わせをチャットから実施できます。例えば、「2026年5月のコストはいくらでしたか？また、前月と比較して増減が大きかったサービスを教えてください。」といったようなことをチャットに入力することで回答を得ることが可能です。

### 7.2 コストの異常調査

例えば、「過去7日間のコスト異常を調査してください。CloudTrailと連携して、異常の背景にあるAPI呼び出しやIAMプリンシパルを特定してください。結果を要約してください。」のように指示をすることでコストの異常調査を実施することができます。

### 7.3 コスト最適化レポート作成

例えば、「経営層向けに、今月のAWSコスト傾向と削減機会をPowerPoint形式でまとめてください。」のように指示するとPowerPoint形式で資料をまとめてくれます。以下のような資料を作成できます。  
![](https://static.zenn.studio/user-upload/4061213071dd-20260705.png)

### 7.4 定期実行とSlack / Jira 連携

例えば、「毎週月曜日の午前9時に、前週のAWSコストサマリを作成してください。サービス別の増減、異常、削減候補をまとめ、Slackの#cost-alertsに投稿してください。」のように指示することで、定期的にレポーティングを実施してくれるようになります。なお、FinOps Agentのタスクには、オンデマンド、スケジュール、イベントベースの3種類があります。

## 8. 利用上の考慮点

利用上の主な考慮点を以下に整理します。

| # | クォータ（アカウント&リージョン毎） | クォータ | 上限緩和申請可能? |
| --- | --- | --- | --- |
| 1 | リージョン & アカウント毎のエージェント数 | 1 | Yes |
| 2 | エージェント毎のアーティファクトストレージ | 100 MB | Yes |
| 3 | アップロード毎のコンテキストファイルサイズ | 10 MB | Yes |
| 4 | エージェント毎のコンテキストファイルストレージサイズ | 100 MB | Yes |
| 5 | アカウント毎の Jira 統合数 | 1 | No |
| 6 | アカウント毎の Slack 統合数 | 1 | No |
| 7 | エージェント毎の Jira 接続数 | 2 | No |
| 8 | エージェント毎の Slack 接続数 | 2 | No |

## 9. まとめ

AWS FinOps Agentは、Cost ExplorerやCompute Optimizerなどの既存サービスを置き換えるものではなく、それらの情報を活用しながらFinOps業務をエージェントとして実行・自動化するためのサービスと捉えると分かりやすいです。

Cost Explorerはコストや使用量を正確に確認するための分析画面、Amazon QはAWSマネジメントコンソール上で手軽にコストについて質問できるアシスタントとして便利です。一方で、AWS FinOps Agentは、チャットでの問い合わせに加えて、タスク実行、スケジュール実行、イベントトリガー実行、レポート生成、Slack/Jira連携などを通じて、継続的なFinOps運用に踏み込める点が特徴です。

特に、以下のような用途ではAWS FinOps Agentの価値が出やすいと感じました。

* 毎週・毎月のコストサマリを自動生成したい
* Cost Anomaly Detectionの検知結果をもとに、原因調査まで自動化したい
* Compute OptimizerやCost Optimization Hubの推奨を整理し、アクションにつなげたい
* 経営層や関係者向けに、HTML / PDF / PowerPoint形式のレポートを作成したい
* Slack通知やJiraチケット作成まで含めて、FinOpsの運用フローを整備したい

プレビュー時点では、日本語での出力やクォータ制限など考慮すべき点もありますが、FinOps担当者が手作業で行っていた調査・集計・報告・連携の一部をエージェントに任せられる可能性を感じました。

まずは、読み取り中心のコスト問い合わせや週次レポートの自動生成から試し、慣れてきたらコスト異常検知をトリガーとした調査やSlack/Jira連携に広げていくのがよさそうです。
