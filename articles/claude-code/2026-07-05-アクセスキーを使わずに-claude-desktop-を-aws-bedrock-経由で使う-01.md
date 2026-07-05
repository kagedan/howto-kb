---
id: "2026-07-05-アクセスキーを使わずに-claude-desktop-を-aws-bedrock-経由で使う-01"
title: "アクセスキーを使わずに Claude Desktop を AWS Bedrock 経由で使う"
url: "https://zenn.dev/takaha4k/articles/claude-desktop-bedrock-no-access-key"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-07-05"
date_collected: "2026-07-06"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Desktop アプリは AWS Bedrock をバックエンドにして動かせます。今回これを設定するにあたって、次の 2 点で困りました。

* Claude Code と違って、Claude Desktop から Bedrock を使うには「開発者モードを有効化」→「サードパーティ推論を設定」という設定手順を踏む必要がある。この手順はヘルプメニューにあって見つけにくく、ピンポイントで解説している記事も見当たらなかった
* これまでは IAM ユーザーのアクセスキーを `~/.aws/credentials` に置いて使っていたが、クレデンシャルはファイルに置いた瞬間から漏洩リスクを抱え続ける。この機会にアクセスキーを一切発行しない構成に切り替えたかった

この記事では、この 2 点を踏まえて、IAM ユーザーを使いつつアクセスキーは発行しない方法で、Claude Desktop から Bedrock 経由で Claude を使うまでの手順を整理します。

## 想定読者

* AWS は日常的に触っているが、Claude Desktop から Bedrock を使うのは初めて
* IAM ユーザーのアクセスキーを増やしたくない
* Bedrock の Model Access（モデルアクセス）の有効化でハマった経験がある

## 全体像

今回の構成はこのようになります。

* 認証: IAM ユーザー + `aws login`（AWS CLI v2）でアクセスキーなしの一時クレデンシャルを取得
* 推論: AWS Bedrock 経由で Claude モデルを呼び出す
* クライアント: Claude Desktop の Developer Mode から Bedrock を接続先として設定

## 1. IAM ユーザーに必要な権限

Claude Desktop から Bedrock で推論するだけなら、IAM ユーザーに必要な権限は次の 2 つです。

* `bedrock:InvokeModel`
* `bedrock:InvokeModelWithResponseStream`

IAM ユーザーにアタッチするポリシーの例です。

bedrock-claude-desktop-policy.json

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "BedrockInvoke",
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": [
        "arn:aws:bedrock:*::foundation-model/*",
        "arn:aws:bedrock:*:*:inference-profile/*"
      ]
    }
  ]
}
```

## 2. `aws login` でアクセスキーなしの認証情報を用意する

ここが今回のポイントです。アクセスキーを発行する代わりに、AWS CLI v2 の `aws login` コマンドを使います。

`aws login` はローカル開発向けの機能で、ブラウザで開いている AWS Management コンソールのログインセッションを使って、CLI 用の一時クレデンシャルとリフレッシュトークンを取得します。アクセスキーを `~/.aws/credentials` に保存する必要がありません。

ターミナル

```
aws login --profile <プロファイル名>
```

実行するとブラウザが開き、コンソールにログイン済みの IAM ユーザーとしてセッションが確立されます。成功すると `~/.aws/config` の対象プロファイルに以下が自動で追記されます。

~/.aws/config

```
[profile <プロファイル名>]
region = us-east-1
login_session = arn:aws:iam::<account-id>:user/<iam-user-name>
```

設定できたら、以下のコマンドで動作確認します。

ターミナル

```
aws sts get-caller-identity --profile <プロファイル名>
```

対象の IAM ユーザーとして認証できていれば OK です。

## 3. Bedrock で Model Access を有効化する

Bedrock はモデルごとに、アカウント内で最初に使うときの利用申請（Model Access の有効化）が必要です。これをやっていないと、後述の接続テストで失敗します。コンソール画面または CLI コマンドで利用申請ができます。

### コンソールから有効化する

1. AWS Management コンソールで Bedrock の画面を開く
2. 左メニューの「Model access」から、使いたい Claude モデル（例: Claude Sonnet 5、Claude Opus 4.8 など）へのアクセスをリクエストする
3. Anthropic モデルは AWS Marketplace 経由の利用規約への同意が求められるので、画面の指示に従って進める

### CLI から有効化する （推奨）

コンソールを使わず CLI でも有効化できます。有効化を実行する IAM ユーザー（または管理者）には、`bedrock:GetUseCaseForModelAccess` / `bedrock:PutUseCaseForModelAccess` と `aws-marketplace:Subscribe` / `aws-marketplace:ViewSubscriptions` の権限が必要です。

ターミナル

```
# 1. 利用同意のオファー情報を取得
aws bedrock list-foundation-model-agreement-offers --model-id <ModelId>

# 2. (初回のみ) Use Case フォームを提出
aws bedrock put-use-case-for-model-access --form-data <Base64EncodedFormData>

# 3. オファーに同意してモデルを有効化（利用同意のオファー情報からトークン取得）
aws bedrock create-foundation-model-agreement --model-id <ModelId> --offer-token <OfferToken>

# 4. 有効化状態を確認
aws bedrock get-foundation-model-availability --model-id <ModelId>
```

Use Case フォームはアカウント単位で一度提出すれば以降は不要なので、既に別の Anthropic モデルを有効化済みのアカウントでは手順 2 は省略されます。また、手順 3 の実行直後は `agreementAvailability` が `PENDING` のままのことがあり、`AVAILABLE` になるまで数分待つ必要があります。

## 4. Claude Desktop 側の設定

IAM ユーザー・認証情報・Model Access の準備ができたら、Claude Desktop 側を設定します。

### 4-1. Developer Mode を有効化する

メニューの「ヘルプ」→「トラブルシューティング」→「開発者モードを有効にする」を選びます。

![](https://static.zenn.studio/user-upload/deployed-images/79d08b3df8871aab59fea882.png?sha=93046673fc7a547d66f9d2f8648c94093354c38a)

### 4-2. Third-Party Inference を設定する

Developer Mode を有効化すると、メニューバーに「開発」が追加されます。「開発」→「サードパーティ推論を設定...」を選びます。

![](https://static.zenn.studio/user-upload/deployed-images/fc41065ddff2ddf8fc51ada7.png?sha=6fc8a87de80ad696e32db5b4338d076670d53165)

開いた画面の Provider で「Amazon Bedrock」を選択し、以下を入力します。

| 項目 | 内容 |
| --- | --- |
| AWS リージョン | Bedrock ランタイムのリージョン（例: `us-east-1`） |
| AWS プロファイル名 | `aws login` で設定したプロファイル名 |
| AWS の設定ディレクトリ | 通常は `~/.aws`（デフォルトのままで OK） |
| AWS CLI のパス | `aws` コマンドの絶対パス（例: `/usr/local/bin/aws`） |
| 認証情報の種類 | 「クラウドベンダープロファイル」を選択 |

入力後、「接続テスト」を実行し、`AWS profile` 経由で推論が成功することを確認します。

### 4-3. モデルを追加する

「モデル」セクションのモデルリストに、使いたいモデル ID を追加します。

```
us.anthropic.claude-sonnet-5
```

表示名を入れておくと、モデル選択画面で見分けやすくなります。入力例は以下のとおりです。

![](https://static.zenn.studio/user-upload/deployed-images/dd56e214a01294f51da7af0c.png?sha=a2f0f835cf903b2e9a70d3a4540a22e8cd9f9335)

## ハマりやすい点

* **モデルアクセスの有効化漏れ**: 使いたいモデルへのアクセスを有効化していないと、接続テストやモデル呼び出しがエラーになる
* **リージョンとモデルの対応**: モデルの提供状況はリージョンごとに異なるため、選んだリージョンで対象モデルが提供されているか事前に確認する
* **有効化操作とIAMユーザーの権限の混同**: `aws-marketplace:Subscribe` 系の権限は Model Access を有効化する操作にのみ必要で、有効化済みのモデルを推論に使う IAM ユーザーには不要
* **プロファイル名の衝突**: 他のツールやプロジェクトで同名の AWS プロファイルを使っていると、意図しない認証情報で接続してしまうことがある。Claude Desktop 専用のプロファイル名を切っておくと事故を防げる

## まとめ

* IAM ユーザーのアクセスキーを発行せず、`aws login` で一時クレデンシャルを取得すれば、Claude Desktop から Bedrock を安全に使える
* 推論に使う IAM ユーザーが必要とする権限は `bedrock:InvokeModel` / `InvokeModelWithResponseStream` のみ
* Bedrock 側で使いたいモデルの Model Access を有効化しておかないと、Claude Desktop 側の接続テストで失敗する。この有効化は 1 回限りの操作で、`aws-marketplace:Subscribe` などの権限が必要
* Claude Desktop の設定は「開発者モードを有効化」→「サードパーティ推論を設定」→ Bedrock の接続情報を入力、という流れで完結する
