---
id: "2026-05-24-aws-mcp-server-でaiエージェントと人間の-iam-権限を分離してみた-01"
title: "AWS MCP Server でAIエージェントと人間の IAM 権限を分離してみた"
url: "https://zenn.dev/acntechjp/articles/feb79f5abbe462"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "LLM", "zenn"]
date_published: "2026-05-24"
date_collected: "2026-05-25"
summary_by: "auto-rss"
query: ""
---

## 導入

### 背景

* 2026 年 5 月 6 日、AWS MCP Server が一般提供（GA）を開始しました。
* AWS MCP Server を利用することで、Claude Code 等の AI エージェントから、既存の IAM 認証情報を用いて AWS サービスへ直接アクセスできるようになりました。
* 一方で「エージェントに AWS へのアクセスを許可する = 人間と同等の権限を与える」という状況は、セキュリティ上のリスクになりえます。エージェントが意図せず重要リソースを変更・削除するようなシナリオは避けたいはずです。
* GA に伴い IAM コンテキストキー `aws:ViaAWSMCPService` / `aws:CalledViaAWSMCP` が導入されました。これにより、「人による操作」と「AI エージェント経由の操作」を IAM ポリシーレベルで明確に分離できるようになりました。

### 本記事の目的

* AWS MCP Server が IAM リクエストにどのように関与するかを、認可フローの観点から整理します。
* 2 つの IAM コンテキストキー（`aws:ViaAWSMCPService` / `aws:CalledViaAWSMCP`）の違いと使い分けを解説します。
* これらのコンテキストキーを IAM ポリシーに設定することで、**人による直接操作と AI エージェント経由の操作とで付与権限を明確に分離**できることをハンズオンで確認します。
* 同時に、**CloudTrail ログ上でも両者を区別して確認**できることを確認します。

### 対象読者

* AWS MCP Server の利用を検討しているエンジニア・セキュリティ担当者
* AWS IAM の基本知識（ポリシー構造、コンテキストキーの概念）を前提とします。

---

## AWS MCP Server の概要

AWS MCP Server は、AWS が提供するマネージド MCP サーバーです。AI エージェントはこの MCP サーバーを利用することで、AWS API オペレーションを実行したり、最新の AWS ドキュメント情報を取得したりできます。なお、ドキュメントの取得に認証は不要です。

GA により、IAM コンテキストキーをサポートするようになりました。これにより、標準の IAM ポリシーできめ細かなアクセス制御を表現できます。

---

## 課題：エージェントに与える権限をどう絞るか

AWS MCP Server はユーザーの既存の IAM ポリシーに基づいて動作します。つまり、`AdministratorAccess` を持つ開発者が AWS MCP Server を使えば、エージェントも同等の操作が可能です。

これは以下のような問題につながりえます。

* エージェントが誤って本番リソースを変更・削除する
* 想定外の高コストリソースが作成される
* CloudTrail 上で「人の直接操作」と「エージェント経由の操作」が区別できない

この問題を解決するのが、すべての AWS マネージド MCP サーバー経由リクエストに自動付与される 2 つの IAM コンテキストキーです。

---

## 2 つの IAM コンテキストキー

AWS MCP Server は、S3・Lambda などの AWS サービスへリクエストを転送する際に、以下の 2 つのグローバルコンテキストキーを自動的に付与します。

| コンテキストキー | 型 | 値 | 用途 |
| --- | --- | --- | --- |
| `aws:ViaAWSMCPService` | Boolean | `true` / `false` | AWS マネージド MCP サーバー経由かどうかの判定 |
| `aws:CalledViaAWSMCP` | String（単一値） | MCP サーバーのサービスプリンシパル名 | 特定の MCP サーバーを指定した制御 |

### `aws:ViaAWSMCPService` — すべての MCP 経由リクエストを対象にする

Boolean キーです。AWS マネージド MCP サーバーのいずれかを経由したリクエストに対して `true` がセットされます。MCP 経由かどうかという粒度で一律に制御したい場合に使用します。

### `aws:CalledViaAWSMCP` — 特定の MCP サーバーに絞る

String キーです。リクエストを転送した MCP サーバーのサービスプリンシパル名を保持します。複数の AWS マネージド MCP サーバーを使い分ける環境で、サーバーごとに異なるアクセス制御を実装したい場合に活用できます。

> **ポイント**：きめ細かな制御が必要な場合は、`aws:ViaAWSMCPService`（一括制御）と `aws:CalledViaAWSMCP`（サーバー個別制御）を組み合わせて設計することを推奨します。

---

## ハンズオン

コンテキストキーによる権限制御と CloudTrail ログでの操作区別を実際に確認します。

### 前提条件

* AWS CLI がインストール・設定済みであること
* Claude Code がインストール済みであること
* `uv` がインストール済みであること（AWS MCP Server のプロキシ起動に使用）

### 検証環境の構成

今回は以下の構成でハンズオンを行います。

* IAM ユーザーに S3 への全操作を許可するポリシーをアタッチ
* ただし、AWS MCP Server 経由（`aws:ViaAWSMCPService: true`）の場合は S3 の変更系操作（`s3:CreateBucket` 等）を Deny
* CLI 直接操作では S3 バケット作成が可能だが、Claude Code + MCP 経由では参照のみ可能なことを確認

### Step 1：IAM ユーザーとポリシーの作成

#### 1-1. MCP 経由の S3 変更系操作を Deny するポリシーの作成

`aws:ViaAWSMCPService` を条件に、S3 の書き込み系操作をすべて Deny します。

```
aws iam create-policy \
  --policy-name DenyS3MutationViaMCPPolicy \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "DenyS3MutationViaMCP",
        "Effect": "Deny",
        "Action": [
          "s3:CreateBucket",
          "s3:DeleteBucket",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:PutBucketPolicy",
          "s3:DeleteBucketPolicy",
          "s3:PutBucketAcl"
        ],
        "Resource": "*",
        "Condition": {
          "Bool": {
            "aws:ViaAWSMCPService": "true"
          }
        }
      }
    ]
  }'
```

> **ポイント**：`Deny` は `Allow` より優先されます。AWS マネージドポリシー `AmazonS3FullAccess` を変更せず、Deny ポリシーを追加するだけで MCP 経由のみを制御できます。

#### 1-2. IAM ユーザーの作成とポリシーのアタッチ

S3 への全操作許可には AWS マネージドポリシー `AmazonS3FullAccess` を使用します。

```
# IAM ユーザーの作成
aws iam create-user --user-name mcp-handson-user

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# 2 つのポリシーをアタッチ
aws iam attach-user-policy \
  --user-name mcp-handson-user \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

aws iam attach-user-policy \
  --user-name mcp-handson-user \
  --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/DenyS3MutationViaMCPPolicy

# アクセスキーの発行
aws iam create-access-key --user-name mcp-handson-user
```

発行された `AccessKeyId` と `SecretAccessKey` を控えておきます。

#### 1-3. AWS CLI プロファイルの設定

```
aws configure --profile mcp-handson
# AWS Access Key ID: <上記で取得した AccessKeyId>
# AWS Secret Access Key: <上記で取得した SecretAccessKey>
# Default region name: ap-northeast-1
# Default output format: json
```

---

### Step 2：CLI 直接操作で S3 バケット作成できることを確認

まず、CLI から直接 S3 バケットが作成できることを確認します。

```
aws s3api create-bucket \
  --profile mcp-handson \
  --bucket mcp-handson-bucket-${RANDOM} \
  --region ap-northeast-1 \
  --create-bucket-configuration LocationConstraint=ap-northeast-1
```

以下のようなレスポンスが返れば作成成功です。

```
{
    "Location": "http://mcp-handson-bucket-XXXXX.s3.amazonaws.com/"
}
```

CLI（`aws:ViaAWSMCPService` が付与されない直接操作）では、`AmazonS3FullAccess` の Allow がそのまま適用され、バケットを作成できました。

次のステップで使うため、作成したバケットは一度削除しておきます。

```
aws s3api delete-bucket \
  --profile mcp-handson \
  --bucket <作成したバケット名> \
  --region ap-northeast-1
```

---

### Step 3：Claude Code 等の AI エージェントへの AWS MCP Server の設定

Claude Code を例に、`mcp-handson` プロファイルを使用するよう AWS MCP Server を設定します。

```
claude mcp add-json aws-mcp --scope user \
  '{"command":"uvx","args":["mcp-proxy-for-aws@latest","https://aws-mcp.us-east-1.api.aws/mcp","--metadata","AWS_REGION=ap-northeast-1","--profile","mcp-handson"]}'
```

設定後、Claude Code を起動し `/mcp` コマンドで `aws-mcp` が `connected` になっていることを確認してください。

---

### Step 4：MCP 経由で S3 バケット作成が拒否されることを確認

Claude Code 上で以下のように指示します。

```
ap-northeast-1 に mcp-handson-bucket という名前の S3 バケットを作成してください。
```

Claude Code が `call_aws` ツール（`s3:CreateBucket`）を呼び出そうとすると、`IAM ユーザー mcp-handson-user に s3:CreateBucket の明示的な拒否ポリシーが設定されているため、バケットを作成できませんでした。` といったエラーが返ります。

`DenyS3MutationViaMCPPolicy` の Deny が発動し、MCP 経由での S3 バケット作成が拒否されました。

---

### Step 5：MCP 経由で S3 の参照は可能なことを確認

続いて参照系操作を試します。Claude Code 上で以下のように指示します。

`s3:ListAllMyBuckets` は Deny の対象外のため、正常にレスポンスが返ります。

```
合計 X 個の S3 バケットが存在します。主なものをカテゴリ別にまとめます：
```

---

### Step 6：CloudTrail で操作を区別して確認する

AWS マネジメントコンソールの CloudTrail「イベント履歴」から該当のイベントレコードを確認すると、MCP 経由の操作には `userAgent` フィールドに `aws-mcp` が記録されています。MCP 経由での `CreateBucket` 呼び出しが `AccessDenied` として記録されていることが確認できます。`userAgent` フィールドを見ることで、そのリクエストが AWS MCP Server 経由だったかを事後に特定できます。

---

### ハンズオンのまとめ

`aws:ViaAWSMCPService` コンテキストキーを用いた Deny ポリシーにより、同一の IAM ユーザーでも「人の直接操作」と「AI エージェント経由の操作」で付与権限を明確に分離できることが確認できました。また CloudTrail ログの `userAgent` フィールドを使うことで、両者の操作を事後に区別してクエリすることも可能です。

---

## おわりに

AWS MCP Server の GA に伴う IAM コンテキストキーの導入は、AI コーディングエージェントのセキュリティガバナンスにおける大きな前進だと感じています。従来は「エージェント用に別 IAM ロールを準備する」という運用的な対処が必要だったところを、既存のポリシーに `Condition` ブロックを追加するだけで宣言的に制御できる点が実用上の大きな進歩です。

特に `aws:ViaAWSMCPService`（一括制御）と `aws:CalledViaAWSMCP`（サーバー個別制御）を使い分けられる設計は、複数の AWS マネージド MCP サーバーが増えていく今後を見据えても拡張しやすい仕組みだと思います。

まずは Deny ポリシーで変更系操作を封じる最小構成から始め、CloudTrail ログで実際の操作を観察しながら段階的にチューニングしていくアプローチが現実的ではないでしょうか。

---

## 参考
