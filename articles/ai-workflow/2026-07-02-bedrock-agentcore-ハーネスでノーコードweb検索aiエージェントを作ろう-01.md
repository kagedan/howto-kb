---
id: "2026-07-02-bedrock-agentcore-ハーネスでノーコードweb検索aiエージェントを作ろう-01"
title: "Bedrock AgentCore ハーネスでノーコードWeb検索AIエージェントを作ろう"
url: "https://zenn.dev/sdb_blog/articles/bedrock-agentcore-harness"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "API", "AI-agent", "LLM", "zenn"]
date_published: "2026-07-02"
date_collected: "2026-07-03"
summary_by: "auto-rss"
query: ""
---

# はじめに

こんにちは！SDBの土井です！

先日2026年6月のAWS Summit New York Cityで、Amazon Bedrock AgentCore に関する新機能がいくつか発表されましたね。🎉  
特に、AgentCore ハーネスのGAは、フルノーコードでAIエージェントの作成・デプロイができ、  
開発のハードルを下げてくれた素晴らしい機能だと感じています。

<https://aws.amazon.com/jp/blogs/machine-learning/amazon-bedrock-agentcore-harness-is-now-generally-available-go-from-idea-to-production-grade-agent-in-minutes/>

さらに、us-east-1リージョン限定ですが、エージェントにWeb検索機能を組み込める機能の発表もありました。

<https://aws.amazon.com/jp/blogs/aws/announcing-web-search-on-amazon-bedrock-agentcore-ground-your-ai-agents-in-current-accurate-web-knowledge/>

本記事では、Web検索に対応したAIエージェントの開発を通して、その手軽さを体験してみようと思います。

# 手順

Agentcoreのリソースは、もちろんコンソール画面からの作成や設定も可能なのですが、本記事では `agentcore cli`を使って作成・デプロイをしていきます。  
記事執筆時2026-06-29の最新バージョンは `v0.21.1` でした。

<https://github.com/aws/agentcore-cli#installation>

```
npm install -g @aws/agentcore
```

## 1. プロジェクトを作成する

まず、`agentcore create` コマンドを実行して、新規のプロジェクトを作成しましょう。  
コマンドを実行すると、カレントディレクトリ配下にプロジェクトが作成されます。  
手順としては、まずWeb検索ツールのGatewayを作成した後にハーネスを作成するため、  
プロジェクト作成時のエージェントの初期セットアップは `--no-agent` オプションによりスキップしておきます。

```
agentcore create --name harness --no-agent
```

コマンドが正常に実行されると、以下のようなプロジェクトが作成されます。

```
harness/
├── AGENTS.md
├── README.md
└── agentcore/
    ├── .env.local          # API keys (gitignored)
    ├── agentcore.json      # Resource specifications
    ├── aws-targets.json    # Deployment targets
    └── cdk/                # CDK infrastructure
```

## 2. Web検索ツール（Gateway）を作成する

次に、作成したプロジェクトのディレクトリに移動し、Web検索ツールをAgentcore Gateway のターゲットとして追加します。

```
agentcore add gateway --name gateway
```

```
ENABLE_GATED_FEATURES=1 agentcore add web-search --gateway gateway --name gateway-target
```

ここまできたら一度AWS環境にデプロイしましょう。  
※ 記事執筆時点では、Web検索ツールが対応しているリージョンは `us-east-1` のみとなります。

## 3. ハーネスを作成する

Web検索ツールのGatewayが作成できたら、次にハーネスを追加しデプロイしていきます。  
まず最初に、`agentcore status` コマンドで先ほどAWS環境にデプロイしたGatewayのARNを確認しておきます。

```
agentcore status --json | jq .deployedState.targets.default.resources.mcp.gateways.gateway.gatewayArn
```

次にハーネスを追加します。既に作成済みのGatewayと紐付けてハーネスを作成します。

```
agentcore add harness \
  --name harness \
  --tools agentcore_gateway \
  --gateway-arn arn:aws:bedrock-agentcore:us-east-1:123456789012:gateway/harness-gateway-xxxxxxxxxx \
  --model-provider lite_llm \
  --model-id amazon.nova-pro-v1:0
```

ハーネスの設定ができたら再度デプロイします。

# 動作確認

デプロイしたハーネスにプロンプトを投げて、Web検索が効いているかを確認します。  
確認はAWSのコンソール画面のハーネスプレイグラウンドから確認ができます。

まず、「天気とは何か」という言葉の意味をエージェントに聞いてみます。

![](https://static.zenn.studio/user-upload/deployed-images/3b908aae99a19fd1911e8302.png?sha=bb7c4cc0033335efaefd825e9d5f3ab221a829f6)

言葉の意味などのモデルが学習済みの知識はWeb検索をせずとも答えられるため、 Web検索ツールは呼ばれませんでした。

次に、「明日の東京の天気」をエージェントに聞いてみます。

![](https://static.zenn.studio/user-upload/deployed-images/75509115396789b447557824.png?sha=77d013fec718c1994ffd5929f9ab6ac900222183)

「明日の東京の天気」は、**モデルの学習データには存在しない最新情報** です。  
そのためエージェントはWeb検索ツールを呼び出して、検索結果をもとに回答しています。

動作を試したところ、AIエージェントがWebを検索する必要があるかどうかを判断し、適切な回答ができていることが確認できました！

# まとめ

本記事では、AgentcoreハーネスとWeb検索ツールを実際に構築して、その挙動を確認しました。  
フルノーコードでサクッとAIエージェントが作成でき、その便利さを体感できました。  
Web検索ツールはまだ us-east-1リージョンのみで限定的ですが、東京リージョンにもくることを期待しています。

# 参考リンク

<https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-get-started.html>
