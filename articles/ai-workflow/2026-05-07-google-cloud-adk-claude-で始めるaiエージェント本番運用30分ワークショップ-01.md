---
id: "2026-05-07-google-cloud-adk-claude-で始めるaiエージェント本番運用30分ワークショップ-01"
title: "Google Cloud ADK + Claude で始めるAIエージェント本番運用【30分ワークショップ】"
url: "https://qiita.com/bokuno_log/items/df16dd49cf71f48516fc"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "AI-agent", "LLM", "qiita"]
date_published: "2026-05-07"
date_collected: "2026-05-08"
summary_by: "auto-rss"
---

> この記事は @angeldot_ さんによる X ポストの動画（約30分）を日本語でまとめたものです。
> 登壇者: Ivan Nardini（Google Cloud Developer Relations Engineer, AI/ML）/ Anthropic 主催イベントにて収録
> オリジナル YouTube: [Building AI agents with Claude in Google Cloud's Vertex AI | Code w/ Claude](https://www.youtube.com/watch?v=TUysIAtxyrQ)

元ツイート: https://x.com/angeldot_/status/2052104456846622957?s=20

## はじめに

AIエージェントの開発はできた。でも本番に出せない——そんな壁を Google Cloud の Ivan Nardini が 30 分で突破する方法を実演したワークショップです。

ADK・MCP・Vertex AI Agent Engine・A2A Protocol の4本柱を使い、Claude を脳みそにしたマルチエージェントシステムを構築・デプロイするまでを一気通貫で解説しています。

---

## AIエージェントを本番化できない3つの理由

![Building AI agents - Powerful, but complex](https://raw.githubusercontent.com/bokuno-studio/zenn-content/main/images/google-cloud-adk-claude-vertex-agent-00-01-30.jpg)

エージェントのプロトタイプはできたのに、本番化で詰まるのはなぜか。3つの根本的な原因があります。

| 課題 | 内容 |
|------|------|
| **断片化したエコシステム** | フレームワークが乱立し、何を使えばいいか不明確 |
| **統合の難しさ** | 異なるフレームワーク同士のエージェント間通信が困難 |
| **運用・ガバナンスの欠如** | モニタリング・ロギング・スケーリングをすべて自前実装する必要がある |

この3つを解決するために Google Cloud が用意したのが **Agentic Stack** です。

## Google Cloud Agentic Stack の全体像

![Our agentic stack](https://raw.githubusercontent.com/bokuno-studio/zenn-content/main/images/google-cloud-adk-claude-vertex-agent-00-04-30.jpg)

| レイヤー | 役割 |
|---------|------|
| **Agent Development Kit (ADK)** | OSS のコードファーストなエージェント開発フレームワーク |
| **Model Context Protocol (MCP)** | LLM へのコンテキスト提供を標準化するオープンプロトコル |
| **Vertex AI Agent Engine** | エージェントを本番スケールでデプロイ・管理するマネージドプラットフォーム |
| **Agent2Agent (A2A) Protocol** | 異なるフレームワーク間のエージェント通信を実現するオープン標準 |

---

## Demo 1: 最初のエージェントを3ファイルで作る

![ADK でのエージェント実装](https://raw.githubusercontent.com/bokuno-studio/zenn-content/main/images/google-cloud-adk-claude-vertex-agent-00-11-45.jpg)

```python
from google.adk.agents import LlmAgent
from google.adk.models.anthropic_llm import Claude
from google.adk.models.registry import LLMRegistry

root_agent = LlmAgent(
    name="birthday_planner",
    model="claude-3-7-sonnet@20250219",
    description="誕生日パーティーの計画を手伝うエージェント",
    instruction="ゲストリストの作成、会場の提案、スケジュール調整を行う..."
)
```

必要なのは `agent.py`・`.env`・`requirements.txt` の3ファイルだけ。起動は1コマンド。

```bash
adk run birthday_planner    # CLI で対話
adk web                     # ブラウザ UI で対話＋デバッグ
```

---

## Demo 2: MCPでマルチエージェント化する

![MCP を使ったカレンダーエージェントのコード](https://raw.githubusercontent.com/bokuno-studio/zenn-content/main/images/google-cloud-adk-claude-vertex-agent-00-16-20.jpg)

構成：BirthdayPlannerAgent / CalendarServiceAgent（MCP経由） / EventOrganizerAgent（オーケストレーター）

MCP サーバーの接続は2行：

```python
mcp_tools, exit_stack = await MCPToolset.from_server(
    connection_params=SseServerParams(url=MCP_CALENDAR_SERVER_URL)
)
agent = LlmAgent(name="CalendarServiceAgent", model="claude-3-7-sonnet@20250219", tools=mcp_tools, ...)
```

---

## Demo 3: Vertex AI Agent Engine にデプロイする

![Vertex AI Agent Engine アーキテクチャ](https://raw.githubusercontent.com/bokuno-studio/zenn-content/main/images/google-cloud-adk-claude-vertex-agent-00-21-00.jpg)

```python
agent_engines.create(
    agent=root_agent,
    requirements=["google-cloud-aiplatform[adk]"]
)
```

自動で使えるようになるもの：Cloud Trace / Logging / Monitoring による Observability・セッション管理・Vertex AI Evaluation Service 連携。LangGraph・LangChain・CrewAI でも動作。

---

## ボーナス: A2A Protocol

- **Agent Card**: エージェントのデジタル名刺
- **Agent Skills**: 機能の記述

HTTP / JSON-RPC ベースのオープン標準。異なるフレームワーク間のエージェント協調を実現します。

---

## まとめ

| ポイント | 内容 |
|---------|------|
| ADK は3ファイル・1コマンド | 開発フローがシンプル |
| MCP 統合は2行 | 既存エコシステムをそのまま活用 |
| Agent Engine でゼロ運用デプロイ | Observability・スケーリング自動 |
| A2A でフレームワーク間の壁を超える | Claude・Gemini・LangChain が共存 |
