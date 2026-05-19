---
id: "2026-05-18-claude-codeのvscode拡張をbedrock経由で使うまでの全手順まとめ-01"
title: "Claude CodeのVSCode拡張をBedrock経由で使うまでの全手順まとめ"
url: "https://qiita.com/nyhigo/items/11286cc4f2743665c6a9"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "VSCode", "qiita"]
date_published: "2026-05-18"
date_collected: "2026-05-19"
summary_by: "auto-rss"
query: ""
---

## はじめに
本記事では、Claude CodeのVSCode拡張をAWS Bedrock経由で利用できるようになるまでの手順を解説します。  

以下のような方を対象としています。

- Claude CodeをVSCodeで利用したい方
- Bedrock経由でセキュアに利用したい方
- 環境構築でつまずきたくない方


## 全体像（アーキテクチャ）

今回構築する構成は以下の通りです。

```text
VSCode（Claude Code拡張）
        ↓
ローカル環境（AWS認証情報）
        ↓
AWS Bedrock
        ↓
Claude（Anthropicモデル）
```

### ポイント

- Claude APIを直接使用せず、Bedrockを経由します
- IAMによるアクセス制御が可能です



## 前提条件

事前に以下を満たしておく必要があります。

- AWSアカウントを保有している
- Bedrockが有効化されている
- Claudeモデルにアクセス可能である
- AWS CLIがインストール済みである
- AWS CLIの認証設定が完了している



## Claude Code VSCode拡張とは

Claude Codeは、AnthropicのClaudeモデルを活用したコーディング支援ツールです。

主に以下の機能を提供します。

- コード生成
- リファクタリング
- コードレビュー補助
- ペアプログラミング支援



## 環境構築手順

## 1. Bedrock側の設定

### 1.1 モデルアクセス確認

AWSコンソールで以下を確認します。

- Bedrock → Model access
- Claudeモデルが「Available」になっていること

### 1.2 リージョン確認

Claudeが利用可能なリージョンであることを確認します。

例：
- us-east-1
- us-west-2



## 2. IAM（権限）設定

Bedrockを利用するための権限を付与します。

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
```



## 3. AWS CLI設定

### 3.1 通常設定

```bash
aws configure
```

### 3.2 SSOを利用する場合

```bash
aws configure sso
```

### 3.3 プロファイル確認

```bash
aws configure list-profiles
```


## 4. VSCode拡張の導入

1. VSCodeを起動します  
2. 拡張機能から「Claude Code」を検索します  
3. インストールします  




## 5. VSCode側の設定

### 5.1 settings.json に環境変数を追記する
Claude Code拡張をBedrock経由で動作させるために、VSCodeの `settings.json` に以下を追記します。

#### 設定手順
1. VSCodeのコマンドパレットを開きます（Windows/Linux: `Ctrl+Shift+P`、macOS: `Cmd+Shift+P`）
2. `Preferences: Open User Settings (JSON)` を選択します
3. 開いた `settings.json` に以下を追記します

```json
{
  "claudeCode.environmentVariables": [
    {
      "name": "CLAUDE_CODE_USE_BEDROCK",
      "value": "1"
    },
    {
      "name": "AWS_PROFILE",
      "value": "default"
    },
    {
      "name": "AWS_REGION",
      "value": "us-west-2"
    },
    {
      "name": "ANTHROPIC_MODEL",
      "value": "global.anthropic.claude-sonnet-4-6"
    }
  ]
}
```

#### 設定項目の意味
- `CLAUDE_CODE_USE_BEDROCK`: Bedrock経由での利用を有効化します（`1` で有効）
- `AWS_PROFILE`: 利用するAWS CLIプロファイル名を指定します
- `AWS_REGION`: Bedrockを利用するリージョンを指定します
- `ANTHROPIC_MODEL`: Bedrock上で呼び出すモデルIDを指定します




## 6. 接続確認

VSCode上でClaudeに対してプロンプトを送信し、レスポンスが返ることを確認します。



## なぜBedrock経由で使うのか

Bedrockを利用する主なメリットは以下の通りです。

- IAMによるアクセス制御が可能
- 組織単位でのガバナンスを効かせられる



## まとめ

本記事では、Claude CodeのVSCode拡張をBedrock経由で利用する手順を解説しました。

### ポイント

- Bedrockのモデルアクセス確認が重要
- リージョンとIAM権限に注意
- VSCodeとAWSプロファイルの整合性を取る

Bedrock経由で利用することで、セキュアかつ統制された形でClaudeを活用できます。
