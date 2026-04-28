---
id: "2026-04-27-windows-ネイティブ版amazon-bedrock-を使用した-claude-code-の始め-01"
title: "【Windows ネイティブ版】Amazon Bedrock を使用した Claude Code の始め方"
url: "https://zenn.dev/aws_japan/articles/claude-code-bedrock-windows-native"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "zenn"]
date_published: "2026-04-27"
date_collected: "2026-04-28"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Code は、Anthropic が開発している Agentic coding のコマンドラインツールです。Claude モデルに最適化されているという特徴があり、Anthropic 自体が提唱する MCP やスキルといった仕組みを活用しつつ、幅広いコーディングタスクを処理して開発タスクを加速できます。AWS のクレデンシャルや Bedrock のモデルアクセス権限を持った状態で、環境変数を指定すると Claude Code が Bedrock のモデルを利用するように設定できます。

この記事では、Windows ネイティブ環境で Claude Code を Amazon Bedrock 経由で使用するための設定方法を紹介します。

## 前提条件

以下の環境が整っていることを前提とします。

## AWS 認証情報の設定

Claude Code を Amazon Bedrock で使用するために、まず AWS 認証情報の取得をします。

> **重要**: この記事では、Claude Code の設定に焦点を当て、手順をシンプルにするために、IAM ユーザーを使用した認証方法を説明しますが、**本来 AWS 認証情報の利用には、 IAM Identity Center の利用が推奨されています**。IAM Identity Center は、シングルサインオンを提供するサービスで、一時的な認証情報、統合されたアクセス管理など、より安全な認証機能を提供します。IAM Identity Center の設定方法については、[AWS IAM Identity Center ユーザーガイド](https://docs.aws.amazon.com/ja_jp/singlesignon/latest/userguide/what-is.html)を参照してください。

### 1. IAM ポリシーの作成

Claude Code が Bedrock を使用するために必要な権限を持つ IAM ポリシーを作成します。

1. [AWS マネジメントコンソール](https://console.aws.amazon.com/)にログインします。
2. IAM サービスに移動します。  
   ![](https://static.zenn.studio/user-upload/693567f34c6a-20251029.png)
3. 左側のメニューから「ポリシー」を選択し、「ポリシーの作成」ボタンをクリックします。  
   ![IAMポリシー設定01](https://static.zenn.studio/user-upload/deployed-images/440fc332481959a19831ef16.png?sha=ccc6834888e842e4972acf36373269b04306cc1a)
4. 「JSON」タブを選択し、以下のポリシーを入力します。  
   ![IAMポリシー設定02](https://static.zenn.studio/user-upload/deployed-images/ebed7b4bb6d640a7ee1aef31.png?sha=b7fd0ca3f3c1454f1703db5a6093e1c688f86471)

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowModelAndInferenceProfileAccess",
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream",
                "bedrock:ListInferenceProfiles"
            ],
            "Resource": "*"
        }
    ]
}
```

5. 「次へ」をクリックします。
6. ポリシー名（例：`ClaudeCodeBedrockAccess`）を入力し、「ポリシーの作成」をクリックします。  
   ![IAMポリシー設定03](https://static.zenn.studio/user-upload/deployed-images/badfa0bf0578098dcbd83700.png?sha=2265114fdbbd412a8653f8c22e06ce59c11a9128)

### 2. IAM ユーザーの作成とポリシーのアタッチ

作成したポリシーを紐づけた IAM ユーザーを作成します。

1. 左側のメニューから「ユーザー」を選択し、「ユーザーを作成」ボタンをクリックします。  
   ![](https://static.zenn.studio/user-upload/cab2a688017f-20251029.png)
2. ユーザー名を入力し、「次へ」をクリックします。  
   ![](https://static.zenn.studio/user-upload/f57189a62a20-20251029.png)
3. 「ポリシーを直接アタッチする」を選択。検索ボックスに先ほど作成したポリシー名（例：`ClaudeCodeBedrockAccess`）を入力し、表示されたポリシーのチェックボックスを選択後、「次へ」をクリックします。  
   ![IAMユーザ設定01](https://static.zenn.studio/user-upload/deployed-images/db131692da583c8b8ede19c6.png?sha=0675cbc79f1b7e3b85457d4d0a89e9ee05be7227)
4. 「ユーザーの作成」をクリックします。  
   ![IAMユーザ設定02](https://static.zenn.studio/user-upload/deployed-images/a58e6b2690a48c6bb9eef8c6.png?sha=e98d07a30bd9ca10ed06a7ec02e1211b06d3d16d)

### 3. アクセスキーの作成

1. 作成したユーザーをクリックします。  
   ![](https://static.zenn.studio/user-upload/6113f1b8cb6e-20251029.png)
2. 「セキュリティ認証情報」タブを選択し、「アクセスキーを作成」をクリックします。  
   ![](https://static.zenn.studio/user-upload/b13ea6164cd3-20251029.png)
3. 「コマンドラインインターフェイス (CLI)」を選択後、確認チェックボックスにチェックを入れ、「次へ」をクリック  
   ![](https://static.zenn.studio/user-upload/e7335e81371b-20251029.png)
4. 「アクセスキーを作成」をクリックします。  
   ![](https://static.zenn.studio/user-upload/f31bebbda1f6-20251029.png)
5. **アクセスキー ID** と **シークレットアクセスキー** は、後述の「AWS CLI の設定」で使用するのでコピーしておきます。  
   ![](https://static.zenn.studio/user-upload/c2c9cd03d32d-20251029.png)

> **重要**: アクセスキーとシークレットキーは、GitHub などの公開リポジトリにコミットしないでください。

## インストール方法

この記事では、Windows ネイティブ環境に直接インストールする方法を紹介します。

### 1. Git for Windows のインストール

Claude Code の実行には Git が必要です。[Git for Windows](https://git-scm.com/downloads/win) のサイトからインストーラーをダウンロードし、インストールします。

![Git for Windows ダウンロードページ](https://static.zenn.studio/user-upload/deployed-images/e0705ed8bd0aec5447985e04.png?sha=218edaca743b037d29e00108e9c20fe7f0205299)

インストーラーの設定はデフォルトのまま進めて問題ありません。

インストール後、PowerShell を開いて確認します。

バージョンが表示されれば OK です。

### 2. AWS CLI のインストール

[Windows 用の AWS CLI MSI インストーラ（64 ビット）](https://awscli.amazonaws.com/AWSCLIV2.msi)をダウンロードして実行します。

インストーラーの指示に従って進めてください。インストール完了後、**PowerShell を新しく開き直して**から確認します。

バージョンが表示されれば OK です。

### 3. Claude Code のインストール

PowerShell を開き、以下のコマンドで Claude Code をインストールします。

```
# Claude Code のインストール
irm https://claude.ai/install.ps1 | iex
```

インストール完了後、**PowerShell を新しく開き直して**からインストール確認をします。

```
# インストール確認
claude --version
```

正常に動作していれば、Claude Code のバージョンが表示されます。

### 4. AWS CLI の設定

PowerShell で以下のコマンドを実行し、認証情報を設定します。

プロンプトに従って、先ほどコピーしたアクセスキー情報を入力します。

```
AWS Access Key ID [None]: <アクセスキー ID を入力>
AWS Secret Access Key [None]: <シークレットアクセスキーを入力>
Default region name [None]: <そのまま Enter キーを押す>
Default output format [None]: <そのまま Enter キーを押す>
```

設定が完了したら、正しく設定されているか確認します。

```
# 認証情報が正しく設定されているか確認
aws sts get-caller-identity
```

正しく設定されていれば、UserId などが表示されます。

## Amazon Bedrock を利用する設定

### 1. Claude Code 設定ファイルの作成

Claude Code に Bedrock を使用することを伝えるため、`~/.claude/settings.json` に設定ファイルを作成します。  
まず、ホームディレクトリに `.claude` ディレクトリを作成します。

```
# .claude ディレクトリを作成
mkdir -Force "$env:USERPROFILE\.claude"
```

次に、`settings.json` ファイルを作成します。

```
# settings.json を作成
@'
{
    "env": {
        "AWS_REGION": "ap-northeast-1",
        "CLAUDE_CODE_USE_BEDROCK": "1",
        "ANTHROPIC_DEFAULT_OPUS_MODEL": "global.anthropic.claude-opus-4-7[1m]",
        "ANTHROPIC_DEFAULT_SONNET_MODEL": "global.anthropic.claude-sonnet-4-6[1m]",
        "ANTHROPIC_DEFAULT_HAIKU_MODEL": "global.anthropic.claude-haiku-4-5-20251001-v1:0"
    }
}
'@ | Out-File -Encoding utf8 "$env:USERPROFILE\.claude\settings.json"
```

> **ポイント**:
>
> * `AWS_REGION`: 使用する AWS リージョンを指定（例：`us-west-2`, `us-east-1`, `ap-northeast-1`）
> * `ANTHROPIC_MODEL`: 使用する Claude モデルの ID を指定
> * `CLAUDE_CODE_USE_BEDROCK`: Bedrock 経由での利用を有効化

## 動作確認

設定が正しく完了したか確認します。

### 1. Claude Code の初回起動

PowerShell でプロジェクトディレクトリに移動し、以下を実行します。

初回起動時に 3 つの設定プロンプトが表示されます。**基本的にすべてデフォルトのまま Enter キーを押して進めます**。

1. **テキストスタイルの選択**: Enter でデフォルトを選択
2. **セキュリティに関する警告**: Enter で続行
3. **ディレクトリアクセスの確認**: Enter で "Yes, proceed" を選択

これで Claude Code が起動し、プロンプト（`>`）が表示されます。

### 2. Bedrock 接続の確認

Claude Code が起動したら、簡単な質問をして Bedrock が正しく動作しているか確認します。

正常に動作していれば、Claude から応答が返ってきます。

### 3. Claude Code の終了方法

Claude Code を終了するには、以下のコマンドを入力します。

これで Claude Code が終了し、通常の PowerShell に戻ります。

## （参考） MCP サーバの追加

Claude Code に MCP (Model Context Protocol) サーバーを追加することで、様々な外部機能を利用できるようになります。ここでは、ウェブ検索機能を提供する Tavily MCP を紹介します。

### 1. Node.js のインストール

Tavily MCP サーバーの実行には Node.js が必要です。[Node.js 公式サイト](https://nodejs.org/ja)から Windows インストーラー（msi）をダウンロードし、インストールします。

インストール後、PowerShell を新しく開き直して確認します。

### 2. Tavily MCP の設定

#### 1. Tavily API キーの取得

1. [Tavily 公式サイト](https://tavily.com/)にアクセスし、アカウントを作成します。
2. ダッシュボードから API キーを取得します。
3. API キーをコピーしておきます。

#### 2. Tavily MCP の追加

プロジェクトディレクトリに移動してから、以下のコマンドを実行します。**`your_token` の部分を、取得した実際の API キーに書き換えてください**。

```
# プロジェクトディレクトリに移動（まだ移動していない場合）
cd your-awesome-project

# Tavily MCP を追加
claude mcp add -e TAVILY_API_KEY=your_token -- tavily-mcp npx -y tavily-mcp@0.1.3
```

#### 3. 動作確認

プロジェクトディレクトリで Claude Code を起動します。

Claude Code が起動したら、Tavily MCP が正しく読み込まれているか確認します。以下のコマンドを実行してください。

Tavily MCP が正しく設定されていれば、接続されている MCP サーバーの一覧に `tavily-mcp` が表示され、状態が「 connected 」になります。

> **Note**: MCP 一覧の表示から抜けるには、`Esc` キーを押してください。

次に、ウェブ検索機能をテストします。Claude Code 内で以下のように質問してみます：

Tavily MCP が正常に動作していれば、リアルタイムのウェブ検索結果を取得して、最新の AI 関連ニュースを回答してくれます。

## まとめ

この記事では、Windows ネイティブ環境で Claude Code を Amazon Bedrock 経由で使用する方法を解説しました。

AWS のクレデンシャルがセットされた環境であれば、すぐに Amazon Bedrock を使用して、Claude Code の利用を始めることができます。
