---
id: "2026-06-30-amazon-bedrock経由のcoworkでgmail連携するためにgmail-mcpを導入して-01"
title: "Amazon Bedrock経由のCoworkでGmail連携するために、Gmail MCPを導入してみた"
url: "https://zenn.dev/uemuragame5683/articles/2f93f3faafce43"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "cowork", "zenn"]
date_published: "2026-06-30"
date_collected: "2026-07-01"
summary_by: "auto-rss"
query: ""
---

## はじめに

社内では Amazon Bedrock 経由の Cowork を利用して Claude を活用しています。  
Claude.ai では Gmail や GitHub などのコネクタを GUI から追加することで、  
各サービスと簡単に連携できます。

Amazon Bedrock経由のCowork では、現時点ではコネクタ機能を利用できません。そのため、Google Workspace（Gmail）と連携したい場合は、  
MCPを利用して接続環境を構築する必要があります。

今回は、会社でも同様の要望が出ていたため、まずは自宅環境で Google Workspace の Gmail を MCP 経由で接続し、Claude Code と Cowork の両方から利用できる環境を構築しました。

そこで、本記事では実際に動作するところまでの手順をまとめます。  
最終的には次のような操作ができるようになりました。

・最新メールの取得  
・メール内容の要約

!

補足  
今回は「2. OAuth認証情報を配置」〜「8. 動作確認」までの作業は、Claude Code を活用しながら進めました。  
Claude Code に手順を指示し、エラーが発生した場合はログを共有しながら修正内容を提案してもらい、実際に動作を確認しながら環境を構築しています。

本記事では、最終的に動作した手順をまとめていますが、環境によって設定が異なる場合があります。その際は、Claude Code などのAIにログを共有しながら調整すると、スムーズに構築できると思います。

## 環境

・macOS  
・Claude Code  
・Cowork（AWS Bedrock）  
・Node.js / npm  
・Gmail MCP Server

## やりたかったこと

Amazon Bedrock 経由の Cowork では Google Workspace コネクタを利用できないため、MCP を利用して Gmail と連携できる環境を構築したいと考えました。

最終的にはClaudeに

> 最新のメールを3件見せて

や

> ○○さんからのメールを検索して

と話しかけるだけで Gmail を操作できることを目標にしました。

## 手順

### 1. Google Cloud Console の設定

まず Google Cloud Console で設定を行います。  
<https://console.cloud.google.com/>

#### ・プロジェクトを作成（または既存プロジェクトを利用）

画面上部のプロジェクト選択から、新しいプロジェクトを作成します。  
既に利用するプロジェクトがある場合は、そのまま利用しても問題ありません。

![](https://static.zenn.studio/user-upload/673b94bb31f4-20260628.png)

#### ・Gmail API を有効化

左メニューからAPIとサービス → ライブラリを開きます。  
検索ボックスで Gmail API と検索し、「有効にする」をクリックします。

![](https://static.zenn.studio/user-upload/1df5feaf7f45-20260628.png)  
![](https://static.zenn.studio/user-upload/7180ca909302-20260630.png)

#### ・OAuth 同意画面を設定

続いて、APIとサービス → OAuth 同意画面を開きます。  
初回のみ、アプリ情報（アプリ名・メールアドレスなど）を入力します。

その後、対象 -> テストユーザー、「＋ ADD USERS」から、  
自分が利用する Gmail アドレスを追加します

![](https://static.zenn.studio/user-upload/b8e98a5cd4d2-20260630.png)

#### ・OAuth クライアント ID を作成

次に、APIとサービス → 認証情報を開き、  
「認証情報を作成」→「OAuth クライアント ID」を選択します。  
アプリケーションの種類はデスクトップアプリを選択します。  
任意の名前を付けて作成します。

![](https://static.zenn.studio/user-upload/816d0737a006-20260630.png)

#### ・OAuth認証情報をダウンロード

作成後、「JSONダウンロード」をクリックします。  
ダウンロードしたファイルは後ほど利用するため、保存しておきます。  
ダウンロードしたJSONファイルは、後ほど以下のパスへ配置します。

![](https://static.zenn.studio/user-upload/236994c79bdc-20260630.png)

```
~/.gmail-mcp/credentials.json
```

ここまで完了すると、Google Cloud 側の準備は完了です。

### 2. OAuth認証情報を配置

ダウンロードした OAuth 認証情報を配置します。

```
mkdir -p ~/.gmail-mcp
cp ~/Downloads/client_secret_xxxxx.apps.googleusercontent.com.json ~/.gmail-mcp/credentials.json
```

### 3. Node.js をインストール

今回利用する Gmail MCP Server は npm パッケージとして提供されているため、事前に Node.js をインストールしておきます。

Homebrew を利用する場合は、以下のコマンドでインストールできます。

インストール後、以下のコマンドで Node.js と npm が利用できることを確認します。

mcp-server-gmail は npx 経由で起動するため、Node.js / npm が必要になります。

### 4. ラッパースクリプトを作成

Gmail MCP Server を Claude Code や Cowork から起動できるようにするため、起動用のラッパースクリプト ~/.gmail-mcp/start.sh を作成します。  
以下のコマンドで start.sh を作成します。

```
cat <<'EOF' > ~/.gmail-mcp/start.sh
#!/bin/bash
exec npx mcp-server-gmail "$@"
EOF
```

実行権限を付与します。

```
chmod +x ~/.gmail-mcp/start.sh
```

!

start.sh では npx mcp-server-gmail を実行しています。

npx は npm パッケージをその場で実行するためのコマンドで、初回実行時に mcp-server-gmail が自動的にダウンロードされます。そのため、事前に npm install を実行する必要はありません。  
環境によってエラーが発生する場合は、エラーメッセージを Claude Code に共有しながら調整すると、スムーズに解決できると思います。

### 5. Claude Code に登録

Claude Code に Gmail MCP を登録します。

```
claude mcp add gmail -s user -- ~/.gmail-mcp/start.sh
```

### 6. Cowork に登録

Coworkでは `claude_desktop_config.json` を読み込む構成になっているため、  
この設定ファイルに Gmail MCP を追加します。

```
{
  "mcpServers": {
    "gmail": {
      "command": "/Users/user/.gmail-mcp/start.sh",
      "args": []
    }
  }
}
```

設定後、Coworkを再起動します。

### 7. OAuth認証

Claude Code や Cowork から利用する前に、一度手動で起動して OAuth 認証を完了させます。  
起動スクリプトを実行します。

ブラウザが起動するので Google アカウントで認証します。

![](https://static.zenn.studio/user-upload/20d5228d221c-20260630.png)

認証が完了すると

が生成されます。

### 8. 動作確認

接続状態を確認します。

以下のように表示されれば成功です。

```
gmail: /Users/user/.gmail-mcp/start.sh - ✔ Connected
```

Cowork から最新メールを3件見せてと入力し、  
メールが取得できればセットアップ完了です。

![](https://static.zenn.studio/user-upload/80befb3bef39-20260628.png)

## できるようになったこと

・メール取得  
・メール内容の要約

## まとめ

Claude.ai ではコネクタを利用することで簡単に Gmail と連携できますが、Amazon Bedrock 経由の Cowork では現時点でコネクタを利用できません。

そのため、Google Workspace（Gmail）と連携したい場合は MCP を利用する方法が有力な選択肢になります。

一度セットアップしてしまえば、Claude Code と Cowork の両方から自然言語で Gmail を操作できるようになり、日常業務の効率化につながりました。

今回は Gmail を対象にしましたが、  
同じような考え方で Google Drive や Google Calendar など、  
他の Google Workspace サービスとも連携できる可能性があります。

今後も検証を進めていきたいと思います。
