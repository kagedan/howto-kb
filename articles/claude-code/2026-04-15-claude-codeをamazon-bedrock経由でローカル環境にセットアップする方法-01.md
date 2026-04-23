---
id: "2026-04-15-claude-codeをamazon-bedrock経由でローカル環境にセットアップする方法-01"
title: "Claude CodeをAmazon Bedrock経由でローカル環境にセットアップする方法"
url: "https://zenn.dev/runyan_tang/articles/db0b5b336d765e"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "zenn"]
date_published: "2026-04-15"
date_collected: "2026-04-16"
summary_by: "auto-rss"
query: ""
---

ターミナル型AIアシスタント「Claude Code」を、Anthropicの直接APIではなく**AWSのAmazon Bedrock経由**で利用するための手順をまとめました。

すでにAWS環境を利用していて、Bedrock経由でセキュアにClaudeを使いたいエンジニアの方におすすめです。

### 0. 事前準備（前提条件）

設定を進める前に、以下の環境が整っているか確認してください。

* **AWSアカウント**: Bedrockへのアクセスが有効になっていること。
* **モデルアクセス**: Bedrock上で目的のClaudeモデル（例：Claude Sonnet 4.6）の利用申請が完了していること。
* **AWS CLI**: インストール済みで、`aws configure` などで認証情報が設定されていること（別の認証メカニズムがない場合）。
* **IAM権限**: Bedrockのモデルを呼び出せる適切な権限が付与されていること。

---

### 1. AWS側での確認（Bedrockコンソール）

まずはAWSのマネジメントコンソールから、モデルが利用できる状態か確認し、モデル名（ID）を把握します。

1. **[Amazon Bedrock コンソール](console.aws.amazon.com/bedrock/)** を開きます。
2. 左側のメニューから **「プレイグラウンド（テキストなど）」** を選択します。  
   ![](https://static.zenn.studio/user-upload/39fc64170257-20260415.png)
3. **「モデルの選択」** をクリックし、カテゴリから「Anthropic」を選び、利用したいモデルを選択します。  
   *(※ここでは例として `JP Anthropic Claude Sonnet 4.6` を選択したものとして進めます)*  
   ![](https://static.zenn.studio/user-upload/49225b7ef1cf-20260415.png)
4. **「プレイグラウンドを開く」** をクリックし、モデルが正常に動作するか（アクセス権があるか）を確認しておきましょう。  
   ![](https://static.zenn.studio/user-upload/f6613311fbba-20260415.png)

---

### 2. ローカル環境へClaude Codeをインストール

次に、手元のPC（ローカル環境）にClaude Code本体をインストールします。お使いの環境に合わせて、以下のいずれかのコマンドをターミナルで実行してください。

**▼ curlを使ってインストールする場合**

```
curl -fsSL https://claude.ai/install.sh | bash
```

**▼ Homebrewを使ってインストールする場合（macOS）**

```
brew install --cask claude-code
```

---

### 3. 環境変数の設定

Claude CodeがデフォルトのAnthropic APIではなく、**AWS Bedrockを向くように**環境変数を設定します。  
お使いのシェル（`bash` または `zsh`）に合わせて、設定ファイルに追記してください。

> **💡 注意:** `<プロファイル名>` の部分は、ご自身の `~/.aws/credentials` に設定しているAWSプロファイル名（`default` など）に書き換えてください。

**▼ bashを利用している場合（`~/.bashrc`）**

```
echo 'export CLAUDE_CODE_USE_BEDROCK=1' >> ~/.bashrc
echo 'export AWS_REGION=ap-northeast-1' >> ~/.bashrc
echo 'export AWS_PROFILE=<プロファイル名>' >> ~/.bashrc
# 先ほどBedrockコンソールで確認したモデルIDを指定
echo 'export ANTHROPIC_MODEL=jp.anthropic.claude-sonnet-4-6' >> ~/.bashrc

# 設定を即時反映
source ~/.bashrc
```

**▼ zshを利用している場合（`~/.zshrc`）**

```
echo 'export CLAUDE_CODE_USE_BEDROCK=1' >> ~/.zshrc
echo 'export AWS_REGION=ap-northeast-1' >> ~/.zshrc
echo 'export AWS_PROFILE=<プロファイル名>' >> ~/.zshrc
# 先ほどBedrockコンソールで確認したモデルIDを指定
echo 'export ANTHROPIC_MODEL=jp.anthropic.claude-sonnet-4-6' >> ~/.zshrc

# 設定を即時反映
source ~/.zshrc
```

---

### 4. Claude Codeの起動

設定は以上で完了です！  
ターミナルを開き、作業したいプロジェクトのディレクトリで以下のコマンドを実行してください。

![](https://static.zenn.studio/user-upload/287680b9cb44-20260415.png)

これで、Bedrock経由でClaude Codeが立ち上がり、ターミナル上で直接コード生成や対話ができるようになります。快適なAIコーディング体験をお楽しみください！

> 参考：<https://code.claude.com/docs/ja/amazon-bedrock>
