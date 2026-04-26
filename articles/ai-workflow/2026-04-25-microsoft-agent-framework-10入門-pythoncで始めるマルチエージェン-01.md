---
id: "2026-04-25-microsoft-agent-framework-10入門-pythoncで始めるマルチエージェン-01"
title: "Microsoft Agent Framework 1.0入門 — Python/C#で始めるマルチエージェント本番開発"
url: "https://zenn.dev/kai_kou/articles/199-microsoft-agent-framework-v1-python-guide"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "API", "AI-agent", "LLM", "zenn"]
date_published: "2026-04-25"
date_collected: "2026-04-26"
summary_by: "auto-rss"
---

## はじめに

2026年4月3日、Microsoftは **Agent Framework 1.0** の正式リリースを発表しました。これはSemantic KernelとAutoGenという2つの人気OSSフレームワークを統合した後継プロジェクトであり、PythonおよびC#/.NETの両方で安定APIが提供される、プロダクション対応のマルチエージェント開発基盤です。

<!-- IMAGE\_SLOT: hero  
description: Microsoft Agent Framework 1.0のアーキテクチャ概念図。左に"Semantic Kernel"と"AutoGen"のレガシーブロック、中央に"Agent Framework 1.0"への統合矢印、右にAgents/Workflows/MCPの3コンポーネントを示す。白背景、フラットデザイン、Blue(#3B82F6)とSlate(#475569)。  
aspect\_ratio: 16:9  
-->

### この記事で学べること

* Microsoft Agent Framework 1.0の概要と背景
* PythonおよびC#でのエージェント作成手順
* マルチエージェントオーケストレーションパターン
* Semantic KernelおよびAutoGenからの移行方針

### 対象読者

* Semantic KernelまたはAutoGenを使用中のエンジニア
* プロダクション向けAIエージェントシステムを構築したい方
* PythonまたはC#でAIエージェントを開発したい方

### 前提条件

* Python 3.10以上 または .NET 8以上
* Azure OpenAI / OpenAI / Anthropic等のAPIキーいずれか

---

## TL;DR

* Semantic KernelとAutoGenが統合した後継フレームワーク「Microsoft Agent Framework 1.0」が正式リリース
* Python/C#共に`pip install agent-framework` / `dotnet add package Microsoft.Agents.AI.Foundry` で利用可能
* sequential・concurrent・handoff・group chatなど複数のマルチエージェントパターンを内蔵
* MCP（Model Context Protocol）対応によりツール拡張が容易
* Azure OpenAI・OpenAI・Anthropic・Google Gemini・Amazon Bedrockなど主要LLMプロバイダーをサポート

---

## 背景：なぜAgent Framework 1.0が生まれたか

<!-- IMAGE\_SLOT: concept  
description: Semantic KernelとAutoGenが"Microsoft Agent Framework 1.0"に統合される様子を示した概念図。フロー図で左から"Semantic Kernel（Enterprise Features）"と"AutoGen（Agent Patterns）"が矢印で中央の"Agent Framework 1.0"ボックスに合流し、右に"Production-Ready Agents"が続く。白背景、Emerald(#10B981)のアクセント使用。  
aspect\_ratio: 16:9  
-->

MicrosoftはAIエージェント開発において、2つの主要OSSプロジェクトを運営してきました。

| フレームワーク | 特徴 | 課題 |
| --- | --- | --- |
| Semantic Kernel | エンタープライズ機能、型安全、テレメトリ | エージェント抽象が複雑 |
| AutoGen | シンプルなエージェントパターン | エンタープライズ機能が不十分 |

2025年10月にMicrosoftはこの2つを統合した「Microsoft Agent Framework」を発表。2026年2月にRC（Release Candidate）に到達し、2026年4月3日にv1.0正式版としてリリースされました。

公式ブログでは次のように説明されています：

> Agent Framework combines AutoGen's simple abstractions for single- and multi-agent patterns with Semantic Kernel's enterprise-grade features such as session-based state management, type safety, filters, telemetry, and extensive model and embedding support.  
> — [Microsoft Agent Framework Version 1.0](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/)（2026-04-03）

---

## インストール

### Python

```
pip install agent-framework
```

Azure AI Foundry との統合が必要な場合：

```
pip install agent-framework-foundry
```

### C#/.NET

Azure AI Foundry 統合を含む場合：

```
dotnet add package Microsoft.Agents.AI.Foundry
```

コア抽象のみを使用する場合：

```
dotnet add package Microsoft.Agents.AI
```

---

## 基本的なエージェントの作成

### Python（Azure OpenAI）

```
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential

credential = AzureCliCredential()
client = FoundryChatClient(
    project_endpoint="https://your-foundry-service.services.ai.azure.com/api/projects/your-foundry-project",
    model="gpt-5.4-mini",
    credential=credential,
)

agent = client.as_agent(
    name="HelloAgent",
    instructions="You are a friendly assistant. Keep your answers brief.",
)

# 非ストリーミング（レスポンス一括取得）
result = await agent.run("What is the largest city in France?")
print(f"Agent: {result}")
```

### Python（Anthropic Claude）

Agent Framework 1.0はAnthropicを含む複数プロバイダーをファーストパーティでサポートします。Anthropic統合を使用するには追加パッケージが必要です。

```
pip install agent-framework-anthropic
```

```
from agent_framework.anthropic import AnthropicClient

agent = AnthropicClient(
    model="claude-sonnet-4-6",
    api_key="YOUR_API_KEY"
).as_agent(
    name="ClaudeAgent",
    instructions="You are a helpful assistant.",
)

result = await agent.run("Explain MCP in one sentence.")
print(result)
```

### C#/.NET

```
using Azure.AI.Projects;
using Azure.Identity;
using Microsoft.Agents.AI;

AIAgent agent = new AIProjectClient(
        new Uri("https://your-foundry-service.services.ai.azure.com/api/projects/your-foundry-project"),
        new AzureCliCredential())
    .AsAIAgent(
        model: "gpt-5.4-mini",
        instructions: "You are a friendly assistant. Keep your answers brief.");

Console.WriteLine(await agent.RunAsync("What is the largest city in France?"));
```

---

## サポートするLLMプロバイダー

v1.0では以下のプロバイダーへのコネクタが提供されます（[公式プロバイダー一覧](https://learn.microsoft.com/en-us/agent-framework/agents/providers/)）：

| プロバイダー | モデル例 |
| --- | --- |
| Microsoft Foundry / Azure OpenAI | gpt-5.4-mini, gpt-5.4 |
| OpenAI | gpt-5.4, gpt-5.4-mini |
| Anthropic | claude-sonnet-4-6, claude-opus-4-6 |
| Amazon Bedrock | 各種Claudeモデル |
| Ollama | Llama 4, Gemma 4等のローカルモデル |

---

## マルチエージェントオーケストレーション

<!-- IMAGE\_SLOT: workflow  
description: マルチエージェントオーケストレーションの4パターンを示すフロー図。左から右に: 1) Sequential（直列）, 2) Concurrent（並列）, 3) Handoff（引き継ぎ）, 4) Group Chat（会話）。各パターンをボックスとフロー矢印で視覚化。白背景、Blue(#3B82F6)メイン。  
aspect\_ratio: 16:9  
-->

Agent Framework 1.0では以下のマルチエージェントパターンが安定版として提供されます。

### 利用可能なオーケストレーションパターン

| パターン | 概要 | ユースケース |
| --- | --- | --- |
| **Sequential** | エージェントが直列に処理 | コンテンツ生成→レビュー |
| **Concurrent** | エージェントが並列に処理 | 複数データソースの同時収集 |
| **Handoff** | 条件に基づきエージェントを引き継ぎ | カスタマーサポートのルーティング |
| **Group Chat** | 複数エージェントが議論し合意 | 設計レビュー、意思決定支援 |
| **Magentic-One** | Microsoft Research発の自律型パターン | 複雑なタスクの完全自動化 |

### Sequentialパターンの実装例（Python）

```
import os
from agent_framework.foundry import FoundryChatClient
from agent_framework.orchestrations import SequentialBuilder
from azure.identity import AzureCliCredential

# エージェントを作成
chat_client = FoundryChatClient(
    project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
    model=os.environ["FOUNDRY_MODEL"],
    credential=AzureCliCredential(),
)

# ライター → レビュアーの直列ワークフロー
writer = chat_client.as_agent(
    name="writer",
    instructions="You are a technical writer. Write a concise blog post about the given topic.",
)
reviewer = chat_client.as_agent(
    name="reviewer",
    instructions="You are an editor. Review the draft and improve clarity and structure.",
)

# SequentialBuilder でワークフローを構築
workflow = SequentialBuilder(participants=[writer, reviewer]).build()

# 実行してイベントを受信
async for event in workflow.run("Write about MCP protocol for developers.", stream=True):
    if event.type == "output":
        for msg in event.data:
            print(f"[{msg.author_name or msg.role}]: {msg.text}")
```

---

## MCP（Model Context Protocol）統合

Agent Framework 1.0はMCPをネイティブサポートしており、MCPサーバーをツールとしてエージェントから動的に呼び出せます。接続方式に応じて3種類のツールクラスが用意されています。

| クラス | 接続方式 | 用途例 |
| --- | --- | --- |
| `MCPStdioTool` | ローカルプロセス（stdio） | ローカルMCPサーバー |
| `MCPStreamableHTTPTool` | HTTP/SSE | リモートMCPサーバー |
| `MCPWebsocketTool` | WebSocket | リアルタイムデータ連携 |

### HTTP MCP サーバーへの接続例

```
import asyncio
from agent_framework import Agent, MCPStreamableHTTPTool
from agent_framework.foundry import FoundryChatClient
from azure.identity.aio import AzureCliCredential

async def main():
    async with AzureCliCredential() as credential:
        client = FoundryChatClient(credential=credential)
        async with (
            MCPStreamableHTTPTool(
                name="Microsoft Learn MCP",
                url="https://learn.microsoft.com/api/mcp",
            ) as mcp_server,
            Agent(
                client=client,
                name="DocsAgent",
                instructions="You help with Microsoft documentation questions.",
            ) as agent,
        ):
            result = await agent.run(
                "How to create an Azure storage account using az cli?",
                tools=mcp_server
            )
            print(result)

asyncio.run(main())
```

### ローカル MCP サーバーへの接続例

```
from agent_framework import Agent, MCPStdioTool
from agent_framework.openai import OpenAIChatClient

async with (
    MCPStdioTool(
        name="calculator",
        command="uvx",
        args=["mcp-server-calculator"]
    ) as mcp_server,
    Agent(
        client=OpenAIChatClient(),
        name="MathAgent",
        instructions="You are a math assistant.",
    ) as agent,
):
    result = await agent.run("What is 15 * 23 + 45?", tools=mcp_server)
    print(result)
```

公式ドキュメントによると、MCPサポートにより「エージェントがMCP準拠サーバーで公開された外部ツールを動的に検出・呼び出し」できます。

---

## Semantic Kernel・AutoGenからの移行

### Semantic Kernelからの移行

Semantic Kernelでは複雑なKernel初期化が必要でしたが、Agent Frameworkではエージェントを数行で直接インスタンス化できます。

**移行前（Semantic Kernel）：**

```
# Semantic Kernelの旧スタイル（参考）
kernel = sk.Kernel()
kernel.add_chat_service("azure_chat", AzureChatCompletion(...))
kernel.add_plugin(MyPlugin(), plugin_name="myplugin")
# ... 複雑なセットアップが必要
```

**移行後（Agent Framework 1.0）：**

```
from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient

agent = Agent(
    client=FoundryChatClient(
        project_endpoint="...",
        model="gpt-5.4-mini",
        credential=AzureCliCredential()
    ),
    name="MyAgent",
    instructions="...",
    tools=[my_tool_function],  # ツールを直接登録
)
```

### AutoGenからの移行

AutoGenのエージェント抽象はAgent Frameworkの`Agent`クラスに対応します。マルチエージェントのグループチャットパターンはそのままサポートされています。

詳細な移行手順は公式の移行ガイドを参照してください：

---

## エージェント vs ワークフロー：使い分け

Agent Frameworkでは用途に応じてAgentとWorkflowを使い分けます。

| 用途 | 推奨アプローチ |
| --- | --- |
| オープンエンドな対話や自律的なツール使用 | **Agent** |
| 明確なステップ数とフロー制御が必要な処理 | **Workflow** |
| 関数で十分に実装できる処理 | 関数（Agentは不要） |

---

## まとめ

Microsoft Agent Framework 1.0は、Semantic KernelとAutoGenの長所を統合した本番対応のエージェント開発基盤です。

* **安定API**: v1.0として長期サポート（LTS）を公約
* **マルチプロバイダー**: Azure OpenAI・Anthropic・Google Gemini等に対応
* **豊富なオーケストレーション**: Sequential・Concurrent・Handoff・Group Chat・Magentic-One
* **MCP統合**: 外部ツールをMCP経由で動的に利用可能
* **移行ガイド**: Semantic Kernel・AutoGenユーザー向けの詳細な移行資料を提供

既存のSemantic KernelまたはAutoGenプロジェクトをお持ちの場合は、公式移行ガイドを参照しながら段階的に移行することが推奨されます。

---

## 参考リンク
