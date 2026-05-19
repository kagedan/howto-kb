---
id: "2026-05-19-agent-toolkit-for-aws-を使ってclaude-codeからeksクラスタを作成し-01"
title: "Agent Toolkit for AWS を使ってClaude CodeからEKSクラスタを作成してみる!"
url: "https://qiita.com/daitak/items/daf289a8e75e0bd4044d"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "AI-agent", "qiita"]
date_published: "2026-05-19"
date_collected: "2026-05-19"
summary_by: "auto-rss"
query: ""
---

こんにちは、タカサオです。
今回は、2026年5月6日にリリースされたばかりのAgent Toolkit for AWSを使ってClaude CodeからEKSクラスタを作成してみたいと思います!

https://aws.amazon.com/jp/about-aws/whats-new/2026/05/agent-toolkit/

# 前提

Claude Codeは事前にインストールされている前提とします。
今回はClaude CodeをVS Codeで実行しますが、その場合はVS CodeのインストールやClaude Code拡張のインストールが別途必要になります。

また、接続先のAWSアカウントとそれに接続するためのIAM接続情報(クレデンシャル等)は自分のPCに予め設定しておく必要がありますのでご注意ください。


# セットアップ

Claude Codeのターミナルから以下のコマンドを実行して、Agent Toolkit for AWSのプラグインをインストールを行います。
私はMacのターミナルからClaude Codeを起動して以下のコマンドを実行しました。

```
/plugin marketplace add aws/agent-toolkit-for-aws
/plugin install aws-core@agent-toolkit-for-aws
/reload-plugins
```

Agent Toolkit for AWSのプラグインは以下の3つがあります。
今回はVS Codeから対話形式でEKSクラスタ作成を行いますので、```aws-core```プラグインのみをインストールしました。

* ```aws-core```： サービス選定、CDK/CloudFormation、サーバーレス、コンテナ、ストレージ、オブザーバビリティ、請求、SDK 利用、デプロイメントといった、AWSの基本的な部分をカバー

* ```aws-agents```： AIエージェントを作成するためのAmazon BedrockやAgentCore等をカバー

* ```aws-data-analytics```： データ分析のためのS3 TablesやAWS Glue、Athena等をカバー



VS Codeから```aws-core```プラグインがインストールされた事を確認できました!


![スクリーンショット 2026-05-18 6.56.22.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1905292/bd71381b-cd76-4bb8-bf37-5d9b48c8fdf6.png)

# 試しにS3バケットをClaude Codeから作成してみる

試しにS3バケットを作成してみます。
注目して欲しいところして、バケット名にアンダースコアが使えない仕様を理解して、ハイフンに変えた名前を提案してくれています。とっても頭が良いですね!

![スクリーンショット 2026-05-19 5.12.14.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1905292/b14ff651-e25c-4649-aeca-12bde0adac37.png)


![スクリーンショット 2026-05-19 5.12.54.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1905292/d36ec9ad-c527-4bee-a03a-20f44524fda1.png)


![スクリーンショット 2026-05-19 5.13.28.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1905292/c34f81d8-b443-4ead-826c-6b47e4f50762.png)

実際にバケットが作成されたかどうかをAWSコンソールを確認しました。
ちゃんと作成されています!
しっかりバージョニングも有効になっています。これは便利ですねー


![スクリーンショット 2026-05-19 5.20.04.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1905292/d7d4304b-e45f-4a74-bb23-ba0c4125d745.png)


# EKSクラスタをClaude Codeから作成してみる!

次にいよいよClaude CodeからEKSクラスタを作成してみます。

![スクリーンショット 2026-05-19 5.56.19.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1905292/ba3cbed9-73e1-47a7-9f13-17cb954374ca.png)

構築のために以下の情報を求められました。EKSクラスタ構築に必要な最小限の内容ですね。

| Claude Codeからの質問 | 私の回答 |
|:-:|:-:|
| EKS クラスター名を教えてください  |  my-eks-cluster |
| Kubernetes のバージョンはどれを使用しますか？  |  1.32（最新・推奨） |
| デプロイするリージョンはどこですか？  | ap-northeast-1（東京・推奨）  |
| ノードグループの構成を教えてください。  | t3.medium × 2ノード（推奨）  |


![スクリーンショット 2026-05-19 6.08.11.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1905292/207b9359-e4bf-4880-a153-70fc5067ed87.png)


途中でVPCはどうする?と聞かれたので、以下の様に既存のCloudformationテンプレートから作成して欲しいと指示したところ、それ通りに作成してくれました。

```
EKS クラスターに使用する VPC を選択してください。
以下のcloudformationテンプレートを使ってVPCを新規構築してください。
VPC名は「my-eks-vpc」にしてください。

https://amazon-eks.s3.us-west-2.amazonaws.com/cloudformation/2020-10-29/amazon-eks-vpc-private-subnets.yaml
```

![スクリーンショット 2026-05-19 6.08.33.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1905292/1f864b86-23f6-4cca-a20f-d3426f987d2e.png)

![スクリーンショット 2026-05-19 6.09.05.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1905292/ae0811e7-456d-48af-b735-756feed144cd.png)

VPC作成できたみたいです!

![スクリーンショット 2026-05-19 6.09.58.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1905292/bfe8c7b4-4638-4cb6-891a-4bc2859e76c9.png)

そのままの流れでEKSクラスタ作成を開始しました。

![スクリーンショット 2026-05-19 6.10.53.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1905292/b5d7aa09-39a2-4608-85ca-ebc92f0acc62.png)


クラスタ名等を事前に伝えているので、ここでは特に追加で聞かれる事も無くEKSクラスタ構築完了しました。
続いてノードグループの作成に移りました。


![スクリーンショット 2026-05-19 6.11.26.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1905292/d64a51dc-4b7c-45ec-93cb-86d91d0fef99.png)

![スクリーンショット 2026-05-19 6.11.52.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1905292/568164e2-e8e8-4470-8856-4d12c6643147.png)


![スクリーンショット 2026-05-19 6.12.59.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1905292/638297be-dad3-424c-b764-fa2fa25e9877.png)

ノードグループの作成も終って、一通りのEKSクラスタ構築が完了しました!ここまで非常にスムーズに進みました。
最後に構築したEKSクラスタ情報が表示されて一通りのタスク完了しました。


![スクリーンショット 2026-05-19 6.13.34.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1905292/6daa8b58-6213-4a56-8a04-350f3f576038.png)

![スクリーンショット 2026-05-19 6.13.54.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1905292/3fcbfd0b-9a7a-461f-b32d-accda1da38c6.png)

AWSコンソールからもEKSクラスタが構築されている事を確認できました!

![スクリーンショット 2026-05-19 6.33.11.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1905292/343600ee-6073-4318-99a5-5853ee5001f8.png)

# まとめ

今回はAgent Toolkit for AWS を使ってClaude CodeからEKSクラスタを作成してみました。
私が入力したリソース名の不備を指摘してくれたり、Cloudformationの投入も実行してくれたり、とっても便利でしたー
これはAWSリソースの操作方法が変るな!と思いました!
それではまた!
