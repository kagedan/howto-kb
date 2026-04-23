---
id: "2026-04-20-nvidia-nemo-agent-toolkit入門-mcpa2a対応マルチエージェントをpyth-01"
title: "NVIDIA NeMo Agent Toolkit入門 — MCP・A2A対応マルチエージェントをPythonで実装する"
url: "https://zenn.dev/kai_kou/articles/195-nvidia-nemo-agent-toolkit-mcp-a2a-guide"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "AI-agent", "Python", "zenn"]
date_published: "2026-04-20"
date_collected: "2026-04-21"
summary_by: "auto-rss"
query: ""
---

## はじめに

2026年3月16日のGTC 2026において、NVIDIAは**NVIDIA Agent Toolkit**（オープンエージェント開発プラットフォーム）を発表しました。その中核を担う**NVIDIA NeMo™ Agent Toolkit**は、マルチエージェントシステムを構築するためのオープンソースPython SDKです（Apache-2.0ライセンス）。

NeMo Agent Toolkitの特徴は以下の通りです。

* **フレームワーク非依存**: LangChain・LlamaIndex・CrewAI・Google ADKなど主要フレームワークすべてと統合可能
* **MCP対応**: Model Context Protocolのクライアント・サーバー両方をネイティブサポート
* **A2Aプロトコル対応**: Agent-to-Agentプロトコルによるエージェント間通信
* **NIM統合**: NVIDIA Inference Microservices経由でNemotron 3などの最適化済みモデルを利用可能

既存記事「[NVIDIA Nemotron 3 Super入門](%E8%A8%98%E4%BA%8B062)」がモデル単体を解説したのに対し、本記事は**Toolkitフレームワーク**としての使い方に焦点を当てます。

### この記事で学べること

* NeMo Agent Toolkitのアーキテクチャ全体像
* Pythonによるシングルエージェント・マルチエージェントの実装
* MCPサーバーとの連携パターン
* A2Aプロトコルを使ったエージェント間通信

### 対象読者

* AIエージェントシステムの設計・実装に取り組むエンジニア
* LangChainやCrewAIなど既存フレームワークをより堅牢な基盤に移行したい方
* MCPやA2Aプロトコルを実際のシステムに組み込みたい方

### 前提条件

* Python 3.11以上（nvidia-nat 1.5.0 の対応バージョン）
* pip / uv などのパッケージ管理ツール
* NVIDIA NIM APIキー（build.nvidia.com で取得可能）

---

## TL;DR

* NeMo Agent Toolkitは**エンタープライズ向けマルチエージェントOSS**（GTC 2026発表、Apache-2.0ライセンス）
* MCPサーバーをツールとして接続し、A2Aプロトコルで複数エージェントを連携させる
* NIM経由でNemotron 3 Superなどの最適化済みモデルが利用可能
* NVIDIA OpenShellと組み合わせることで、エージェントの権限をコード外で制御できる

---

NeMo Agent Toolkitは以下の5つのコンポーネントで構成されています。

| コンポーネント | 役割 |
| --- | --- |
| **NeMo Agent Toolkit** | マルチエージェントオーケストレーションSDK（本記事の主役） |
| **NIM Microservices** | Nemotronモデルの推論サービス（OpenAI互換API） |
| **AI-Q Blueprint** | エンタープライズRAGエージェントの参照実装 |
| **NVIDIA OpenShell** | エージェントのセキュリティポリシー実行環境（アルファ版） |
| **cuOpt** | GPU加速最適化ライブラリ（配送最適化など） |

本記事では**NeMo Agent Toolkit**を中心に、NIMとNVIDIA OpenShellの連携まで解説します。

---

## セットアップ

### インストール

```
pip install nvidia-nat
# または uv を使う場合
uv pip install nvidia-nat
```

**LangChain統合を使う場合:**

```
pip install "nvidia-nat[langchain]"
```

NIMのAPIキーを環境変数に設定します。

```
export NVIDIA_API_KEY="nvapi-xxxxxxxx"
```

NIMのAPIキーはNVIDIA Developer Portal（[build.nvidia.com](https://build.nvidia.com)）で無料取得できます。100以上のモデルへのアクセスが含まれます。

### 利用可能なモデル確認

```
from nemo_agent_toolkit import list_nim_models

models = list_nim_models()
for m in models[:5]:
    print(m.model_id, m.context_length)
# nvidia/nemotron-3-super-120b-instruct  1048576
# nvidia/nemotron-3-nano-32b-instruct    131072
# meta/llama-3.3-70b-instruct           131072
# ...
```

---

## シングルエージェントの実装

### 最小構成エージェント

```
from nemo_agent_toolkit import Agent
from nemo_agent_toolkit.models import NIMModel

# Nemotron 3 Superをバックエンドとして利用
model = NIMModel(
    model_id="nvidia/nemotron-3-super-120b-instruct",
    temperature=0.0,
    max_tokens=4096,
)

agent = Agent(
    name="research_agent",
    model=model,
    system_prompt="You are a technical research assistant. Answer in Japanese.",
)

response = agent.run("LangGraphとNeMo Agent Toolkitの違いを教えてください")
print(response.content)
```

### ツールを持つエージェント

組み込みのPython関数をツールとして登録できます。

```
from nemo_agent_toolkit import Agent, tool
from nemo_agent_toolkit.models import NIMModel

@tool(description="指定されたURLのHTMLを取得して本文を返す")
def fetch_webpage(url: str) -> str:
    import httpx
    resp = httpx.get(url, follow_redirects=True, timeout=10)
    # 簡易テキスト抽出（実運用はBeautifulSoup等を推奨）
    return resp.text[:3000]

model = NIMModel(model_id="nvidia/nemotron-3-super-120b-instruct")

agent = Agent(
    name="web_agent",
    model=model,
    tools=[fetch_webpage],
    system_prompt="ウェブ情報を取得して質問に答えてください。",
)

response = agent.run(
    "https://nvidianews.nvidia.com/news/ai-agents のページ概要を教えてください"
)
print(response.content)
```

---

## MCPサーバーとの連携

NeMo Agent ToolkitはMCPクライアントをネイティブサポートしています。既存のMCPサーバーを直接ツールとして利用できます。

### stdioタイプのMCPサーバーを接続

```
from nemo_agent_toolkit import Agent
from nemo_agent_toolkit.mcp import MCPClientStdio
from nemo_agent_toolkit.models import NIMModel

# filesystem MCPサーバーを接続（npx経由）
filesystem_mcp = MCPClientStdio(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp/workspace"],
)

model = NIMModel(model_id="nvidia/nemotron-3-super-120b-instruct")

agent = Agent(
    name="file_agent",
    model=model,
    mcp_clients=[filesystem_mcp],
    system_prompt="ファイルシステムを操作するエージェントです。",
)

# MCPサーバーが提供するツールが自動的に利用可能になる
response = agent.run("/tmp/workspace 内のPythonファイルを列挙して内容を要約してください")
print(response.content)
```

### HTTP/SSEタイプのMCPサーバーを接続

```
from nemo_agent_toolkit.mcp import MCPClientHTTP

# リモートMCPサーバー（SSEトランスポート）
remote_mcp = MCPClientHTTP(
    url="https://your-mcp-server.example.com/sse",
    headers={"Authorization": "Bearer your-token"},
)

agent = Agent(
    name="remote_agent",
    model=model,
    mcp_clients=[remote_mcp],
)
```

### 複数MCPサーバーの組み合わせ

実運用では複数のMCPサーバーを組み合わせてエージェントの能力を拡張します。

```
from nemo_agent_toolkit.mcp import MCPClientStdio, MCPClientHTTP

mcp_clients = [
    # ファイルシステム操作
    MCPClientStdio(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "/workspace"],
    ),
    # データベース操作
    MCPClientStdio(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-postgres"],
        env={"POSTGRES_URL": "postgresql://localhost/mydb"},
    ),
    # カスタムAPIサーバー
    MCPClientHTTP(url="http://localhost:8080/mcp"),
]

agent = Agent(
    name="full_stack_agent",
    model=model,
    mcp_clients=mcp_clients,
    system_prompt="ファイル・DB・カスタムAPIを組み合わせて作業します。",
)
```

---

## マルチエージェント構成（A2Aプロトコル）

NeMo Agent ToolkitはA2A（Agent-to-Agent）プロトコルをサポートしており、エージェント間の委任・協調が可能です。

### オーケストレーター＋サブエージェント構成

```
from nemo_agent_toolkit import Agent, AgentTeam
from nemo_agent_toolkit.models import NIMModel

model_large = NIMModel(model_id="nvidia/nemotron-3-super-120b-instruct")
model_small = NIMModel(model_id="nvidia/nemotron-3-nano-32b-instruct")

# サブエージェント: コード生成専門
code_agent = Agent(
    name="code_writer",
    model=model_large,
    system_prompt="Pythonコードを生成する専門家です。型ヒント・docstringを必ず付けてください。",
    expose_as_a2a=True,  # A2Aエンドポイントとして公開
)

# サブエージェント: コードレビュー専門
review_agent = Agent(
    name="code_reviewer",
    model=model_large,
    system_prompt="Pythonコードのバグ・セキュリティ問題・パフォーマンスを審査します。",
    expose_as_a2a=True,
)

# オーケストレーター: タスクを分解してサブエージェントに委任
orchestrator = Agent(
    name="orchestrator",
    model=model_small,
    system_prompt="""あなたはタスクオーケストレーターです。
    コード生成タスクは code_writer に委任し、
    レビュータスクは code_reviewer に委任してください。""",
    sub_agents=[code_agent, review_agent],
)

# AgentTeamでライフサイクルを管理
team = AgentTeam(orchestrator=orchestrator, agents=[code_agent, review_agent])

with team:
    response = team.run(
        "FastAPIでJWTトークン認証エンドポイントを実装し、セキュリティレビューもしてください"
    )
    print(response.content)
```

### A2Aリモートエージェントへの委任

別プロセス・別サーバーで動作するA2Aエージェントにも委任できます。

```
from nemo_agent_toolkit.a2a import A2ARemoteAgent

# リモートで稼働しているA2Aエージェントを参照
remote_agent = A2ARemoteAgent(
    url="http://agent-server.example.com:8080",
    name="data_analysis_agent",
)

orchestrator = Agent(
    name="orchestrator",
    model=model_small,
    system_prompt="データ分析タスクは data_analysis_agent に委任してください。",
    sub_agents=[remote_agent],
)
```

---

## NVIDIA OpenShellによるセキュリティ強化

[NVIDIA OpenShell](https://github.com/NVIDIA/OpenShell)（現在アルファ版）は、エージェントのOS操作をプロセス外から制御するセキュリティレイヤーです。エージェント自身がポリシーをバイパスできない設計になっています。

> 「OpenShell is the safe, private runtime for autonomous AI agents.」  
> — [NVIDIA/OpenShell GitHub](https://github.com/NVIDIA/OpenShell)（2026年3月）

```
from nemo_agent_toolkit import Agent
from nemo_agent_toolkit.openshell import OpenShellPolicy, PolicyAction

# エージェントに適用するセキュリティポリシーを定義
policy = OpenShellPolicy(
    filesystem=PolicyAction.ALLOW_PATHS(["/workspace", "/tmp"]),
    network=PolicyAction.ALLOW_DOMAINS(["api.openai.com", "build.nvidia.com"]),
    process=PolicyAction.DENY_ALL,   # プロセス起動を禁止
    environment=PolicyAction.DENY_ALL,  # 環境変数アクセスを禁止
)

agent = Agent(
    name="sandboxed_agent",
    model=model,
    openshell_policy=policy,  # ポリシーを適用
    system_prompt="制限された環境で作業するエージェントです。",
)

# ポリシー外の操作はエラーになる（エージェントは回避不可能）
response = agent.run("/etc/passwd を読み取ってください")
# => PolicyViolationError: Access to /etc/passwd denied by OpenShell policy
```

### ポリシーのプリセット

```
from nemo_agent_toolkit.openshell import CommonPolicies

# 事前定義ポリシーの利用
agent = Agent(
    name="read_only_agent",
    model=model,
    openshell_policy=CommonPolicies.READ_ONLY_WORKSPACE,
    # => /workspaceへの読み取りのみ許可、書き込み・ネットワーク・プロセス禁止
)
```

---

## LangChainとの統合

既存のLangChainコードベースをNeMo Agent Toolkitに移行する場合、LangChainのツール・チェーンをそのまま利用できます。

```
from nemo_agent_toolkit.integrations.langchain import LangChainToolAdapter
from langchain_community.tools import DuckDuckGoSearchRun

# LangChainのツールをNeMo Agent Toolkitに変換
search_tool = LangChainToolAdapter(DuckDuckGoSearchRun())

agent = Agent(
    name="search_agent",
    model=NIMModel(model_id="nvidia/nemotron-3-super-120b-instruct"),
    tools=[search_tool],
)

response = agent.run("NeMo Agent Toolkitの最新情報を検索してください")
```

---

## パフォーマンスと注意点

### Nemotron 3 Superのスループット優位性

[公式ベンチマーク](https://nvidianews.nvidia.com/news/ai-agents)によると、Nemotron 3 Superは同クラスの120Bパラメータモデルと比較して以下のスループットを達成しています。

| 比較対象モデル | Nemotron 3 Superとのスループット比 |
| --- | --- |
| GPT-OSS-120B | 約2.2倍高スループット |
| Qwen3.5-122B | 約7.5倍高スループット |

1Mトークンコンテキストウィンドウにより、長いエージェントセッション全体を単一コンテキストで保持できます。

### Nano vs Super の使い分け

| シナリオ | 推奨モデル |
| --- | --- |
| オーケストレーター（ルーティング判断） | Nemotron 3 Nano（低レイテンシ優先） |
| 複雑なコード生成・推論 | Nemotron 3 Super（精度優先） |
| 長文ドキュメント処理 | Nemotron 3 Super（1Mコンテキスト） |
| エッジ・リソース制約環境 | Nemotron 3 Nano（軽量） |

### MCP接続時の注意点

MCPサーバーが多数のツールを提供する場合、コンテキストウィンドウを圧迫することがあります。`tool_filter`パラメータで使用するツールを絞り込めます。

```
agent = Agent(
    name="filtered_agent",
    model=model,
    mcp_clients=[large_mcp_server],
    tool_filter=["read_file", "write_file", "list_directory"],  # 必要なツールのみ
)
```

---

## まとめ

NeMo Agent Toolkitは以下の点でエンタープライズエージェント開発に適しています。

* **フレームワーク非依存**: LangChain・LlamaIndex・CrewAI・Google ADKのどれとでも組み合わせ可能
* **MCP/A2Aネイティブ**: 標準プロトコルを直接サポートするため、エコシステムの資産を活用しやすい
* **NIM統合**: Nemotron 3 Superの1Mコンテキスト・高スループットをAPIとして利用可能
* **NVIDIA OpenShell**: エージェントに付与する権限をコードと分離して管理でき、セキュリティ監査が容易（アルファ版）

フレームワーク乱立の現状において、NeMo Agent Toolkitは「どのフレームワークを使っても動く中立な基盤」としてのポジションを狙っています。LangChain・CrewAIなど既存投資を生かしながら、MCPやA2Aプロトコルを段階的に導入できる点が実務的な強みです。

## 参考リンク
