---
id: "2026-04-14-claude-managed-agents入門-セルフホスト不要でaiエージェントを動かすapiガイ-01"
title: "Claude Managed Agents入門 — セルフホスト不要でAIエージェントを動かすAPIガイド"
url: "https://qiita.com/kai_kou/items/9aa2ca4787306e4dc162"
source: "qiita"
category: "ai-workflow"
tags: ["API", "AI-agent", "qiita"]
date_published: "2026-04-14"
date_collected: "2026-04-15"
summary_by: "auto-rss"
---

## はじめに

2026年4月8日、Anthropicは **Claude Managed Agents** をパブリックベータとして公開しました。これはClaudeを自律型AIエージェントとして動かすための、フルマネージドなエージェントハーネスです。

従来のMessages APIでは、エージェントループ・ツール実行・サンドボックスの構築をすべて自前で実装する必要がありました。Claude Managed Agentsを使うと、Anthropicがインフラを管理し、開発者は「エージェントに何をさせるか」の定義だけに集中できます。

### この記事で解説すること

* Claude Managed Agentsの4つのコア概念
* Pythonを使ったクイックスタート（Agent → Environment → Session の作成）
* 組み込みツール（bash, web\_search等）の設定方法
* カスタムツールの定義方法
* ant CLIによるYAML管理
* 料金体系

### 対象読者

* AnthropicのAPIを使ってAIエージェントを構築したい開発者
* エージェントのインフラ管理を省力化したい方
* Claude Managed Agentsの全体像を把握したい方

### 前提条件

* AnthropicのAPIキー（[Consoleで取得](https://platform.claude.com/settings/keys)）
* Python 3.9以上（コード例はPythonで記載）
* `pip install anthropic`（SDK最新版）

---

## TL;DR

* **Claude Managed Agents** = Anthropicが提供するフルマネージドエージェントハーネス（2026-04-08 パブリックベータ）
* 4つの概念: **Agent（定義）→ Environment（コンテナ）→ Session（実行）→ Events（通信）**
* 組み込みツール: bash / read / write / edit / glob / grep / web\_fetch / web\_search
* **料金**: $0.08/セッション時間 + 標準トークン料金（セッション実行中のみ課金）
* beta header `managed-agents-2026-04-01` が必須（SDKが自動設定）

---

## Claude Managed Agentsとは

[公式ドキュメント](https://platform.claude.com/docs/en/managed-agents/overview)によると、Claude Managed Agentsは次のように位置づけられています。

> Pre-built, configurable agent harness that runs in managed infrastructure. Best for long-running tasks and asynchronous work.

Messages APIと比較すると、以下のような使い分けになります。

|  | Messages API | Claude Managed Agents |
| --- | --- | --- |
| **位置づけ** | モデルへの直接アクセス | フルマネージドエージェントハーネス |
| **向いている用途** | カスタムエージェントループ・細かい制御 | 長時間タスク・非同期処理 |
| **インフラ管理** | 自前で実装 | Anthropicが管理 |
| **ツール実行** | 自前で実装 | 組み込みツールを利用 |

---

## 4つのコア概念

Claude Managed Agentsは4つのリソースで構成されています。

### 1. Agent（エージェント定義）

モデル・システムプロンプト・ツール・MCPサーバーを定義する設定オブジェクトです。一度作成すればIDで参照でき、複数のセッションで再利用できます。

### 2. Environment（実行コンテナ）

エージェントが動作するコンテナテンプレートです。インストール済みパッケージやネットワークアクセス設定を定義します。

### 3. Session（実行インスタンス）

AgentとEnvironmentを参照して起動するエージェントの実行単位です。会話履歴とファイルシステムはセッション内で永続化されます。接続が切れても状態は保持されます。

### 4. Events（メッセージ）

アプリとエージェント間でやり取りするメッセージです。ユーザーメッセージの送信、ツール結果の返送、エージェントの応答受信などがEventsとして処理されます。SSE（Server-Sent Events）でリアルタイムにストリーミングできます。

```
ユーザー → Events.send（user.message）
              ↓
          Session（エージェントループ）
              ↓
          Agent（Claude）がツールを選択
              ↓
          Environment（コンテナ）でツール実行
              ↓
          Events.stream（agent.message / agent.tool_use）
              ↓
          session.status_idle（完了通知）
```

---

## セットアップ

### SDKのインストール

```
pip install anthropic
export ANTHROPIC_API_KEY="your-api-key"
```

### ant CLIのインストール（任意）

```
# macOS（Homebrew）
brew install anthropics/tap/ant
xattr -d com.apple.quarantine "$(brew --prefix)/bin/ant"

# Linux/WSL（最新バージョンは https://github.com/anthropics/anthropic-cli/releases で確認）
VERSION=1.0.0
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m | sed -e 's/x86_64/amd64/' -e 's/aarch64/arm64/')
curl -fsSL "https://github.com/anthropics/anthropic-cli/releases/download/v${VERSION}/ant_${VERSION}_${OS}_${ARCH}.tar.gz" \
  | sudo tar -xz -C /usr/local/bin ant

# インストール確認
ant --version
```

ant CLIを使うと、YAML形式でエージェント・環境設定をバージョン管理できます。

---

## クイックスタート

### ステップ1: Agentを作成する

```
from anthropic import Anthropic

client = Anthropic()

agent = client.beta.agents.create(
    name="Coding Assistant",
    model="claude-sonnet-4-6",
    system="You are a helpful coding assistant. Write clean, well-documented code.",
    tools=[
        {"type": "agent_toolset_20260401"},  # 全組み込みツールを有効化
    ],
)

print(f"Agent ID: {agent.id}, version: {agent.version}")
```

`agent_toolset_20260401` は全組み込みツール（bash, read, write, edit, glob, grep, web\_fetch, web\_search）を一括で有効化する指定です。`agent.id` を保存しておきます。

> 全Managed Agents APIリクエストには `managed-agents-2026-04-01` betaヘッダーが必要です。Python SDKは自動的にこのヘッダーを設定するため、明示的な指定は不要です。

### ステップ2: Environmentを作成する

```
environment = client.beta.environments.create(
    name="quickstart-env",
    config={
        "type": "cloud",
        "networking": {"type": "unrestricted"},  # フルネットワークアクセス
    },
)

print(f"Environment ID: {environment.id}")
```

`networking.type` には `"unrestricted"`（全通信許可）や `"none"`（通信禁止）などを指定できます。

### ステップ3: Sessionを開始する

```
session = client.beta.sessions.create(
    agent=agent.id,
    environment_id=environment.id,
    title="Quickstart session",
)

print(f"Session ID: {session.id}")
```

### ステップ4: メッセージを送信し、ストリーミングで受信する

```
with client.beta.sessions.events.stream(session.id) as stream:
    # ストリームを開いた後にユーザーメッセージを送信
    client.beta.sessions.events.send(
        session.id,
        events=[
            {
                "type": "user.message",
                "content": [
                    {
                        "type": "text",
                        "text": "フィボナッチ数列の最初の20項を生成してfibonacci.txtに保存するPythonスクリプトを作成してください",
                    },
                ],
            },
        ],
    )

    # イベントを処理
    for event in stream:
        match event.type:
            case "agent.message":
                for block in event.content:
                    print(block.text, end="")
            case "agent.tool_use":
                print(f"\n[ツール使用: {event.name}]")
            case "session.status_idle":
                print("\n\nエージェント完了")
                break
```

実行すると、以下のような出力が得られます。

```
Pythonスクリプトを作成し、fibonacci.txtに保存します。
[ツール使用: write]
[ツール使用: bash]
スクリプトが正常に実行されました。出力ファイルを確認します。
[ツール使用: bash]
fibonacci.txtにフィボナッチ数列の最初の20項（0から4181まで）が保存されました。

エージェント完了
```

エージェントはスクリプトを書き、コンテナ内で実行し、結果ファイルの存在を確認するまで自律的に動作します。

---

## 組み込みツールの設定

`agent_toolset_20260401` に含まれる全ツールは以下のとおりです。

| ツール名 | 説明 |
| --- | --- |
| `bash` | シェルコマンドをコンテナ内で実行 |
| `read` | ローカルファイルシステムからファイルを読み取り |
| `write` | ファイルシステムへのファイル書き込み |
| `edit` | ファイル内の文字列置換 |
| `glob` | globパターンでファイルを検索 |
| `grep` | 正規表現でファイル内容を検索 |
| `web_fetch` | 指定URLのコンテンツを取得 |
| `web_search` | Web検索 |

### 特定ツールの無効化

```
agent = client.beta.agents.create(
    name="Restricted Assistant",
    model="claude-sonnet-4-6",
    tools=[
        {
            "type": "agent_toolset_20260401",
            "configs": [
                {"name": "web_fetch", "enabled": False},   # URLフェッチを禁止
                {"name": "web_search", "enabled": False},  # Web検索を禁止
            ],
        },
    ],
)
```

### 必要なツールのみ有効化

```
agent = client.beta.agents.create(
    name="File-Only Assistant",
    model="claude-sonnet-4-6",
    tools=[
        {
            "type": "agent_toolset_20260401",
            "default_config": {"enabled": False},  # まず全ツールを無効化
            "configs": [
                {"name": "bash", "enabled": True},
                {"name": "read", "enabled": True},
                {"name": "write", "enabled": True},
            ],
        },
    ],
)
```

---

## カスタムツールの追加

組み込みツールに加えて、独自のカスタムツールを定義することもできます。カスタムツールはMessages APIのクライアント実行ツールと同じ仕組みです。エージェントがツール呼び出しを要求し、アプリケーション側で実行して結果を返します。

```
agent = client.beta.agents.create(
    name="Weather Agent",
    model="claude-sonnet-4-6",
    tools=[
        {"type": "agent_toolset_20260401"},
        {
            "type": "custom",
            "name": "get_weather",
            "description": (
                "指定した都市の現在の天気情報を取得します。"
                "気温・天気・湿度を返します。"
                "天気に関する質問があるときに使用してください。"
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "都市名（例: Tokyo, New York）",
                    }
                },
                "required": ["location"],
            },
        },
    ],
)
```

カスタムツール呼び出しのイベントを処理する際は、`event.type == "agent.tool_use"` の中でツール名を確認し、`tool_result` イベントで結果を返します。

### カスタムツール設計のポイント

公式ドキュメントで推奨されているベストプラクティスをまとめます。

* **説明は詳細に書く**: ツールの説明はエージェントの性能に最も大きく影響します。何をするか・いつ使うか・各パラメータの意味を3〜4文以上で記述します
* **関連操作はまとめる**: `create_pr` / `review_pr` / `merge_pr` を別々に作るより、`action`パラメータを持つ単一ツールにまとめる方が選択精度が上がります
* **ツール名に名前空間を使う**: `db_query` / `storage_read` のようにリソース名をプレフィックスにすると、ツール選択が明確になります
* **レスポンスは必要最小限に**: UUIDやスラッグなどの意味のある識別子を返し、エージェントが次のステップを判断するために必要な情報だけを含めます

---

## ant CLIによるYAML管理

ant CLIを使うと、エージェントの設定をYAMLファイルで管理してバージョン管理できます。

```
# YAMLでエージェントを作成
ant beta:agents create <<'YAML'
name: Coding Assistant
model: claude-sonnet-4-6
system: You are a helpful coding assistant. Write clean, well-documented code.
tools:
  - type: agent_toolset_20260401
    configs:
      - name: web_fetch
        enabled: false
YAML
```

```
# YAMLで環境を作成
ant beta:environments create <<'YAML'
name: quickstart-env
config:
  type: cloud
  networking:
    type: unrestricted
YAML
```

Claude Codeとの統合も公式にサポートされており、Claude Codeセッションの中からant CLIを呼び出すことができます。

---

## 料金体系

Claude Managed Agentsの料金は2つの要素で構成されます。

### セッション実行料金

[公式価格ページ](https://platform.claude.com/docs/en/about-claude/pricing)によると、**$0.08/セッション時間**が追加されます。

* **課金対象**: セッションの `status` が `running` の間のみ
* **課金対象外**: ユーザーの応答待ち・ツール確認待ち・アイドル状態
* **課金単位**: ミリ秒単位で計算

### トークン料金

利用するClaudeモデルの標準APIレートが適用されます（Managed Agents固有の割増はありません）。

### Web検索料金

セッション内でweb\_searchツールを使用した場合、**$10/1,000回**が加算されます。

### 料金の目安

| シナリオ | 概算コスト |
| --- | --- |
| 30秒の短いタスク（Web検索なし） | $0.0007（実行料金のみ） |
| 10分のコード生成タスク | $0.013 + トークン料金 |
| 1時間のリサーチタスク（Web検索10回） | $0.08 + $0.10 + トークン料金 |

> セッションが待機状態（ユーザー入力待ち）の間は課金されません。バッチ処理や長時間タスクでも、実際の実行時間に対してのみ課金されます。

---

## レート制限

| 操作 | 上限 |
| --- | --- |
| Create系（agents, sessions, environments等） | 60 rpm |
| Read系（retrieve, list, stream等） | 600 rpm |

---

## Managed Agents vs Agent SDK

Anthropicは[Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview)（Claude Codeと同じホスティングフレームワーク）も提供しています。Claude Managed Agentsとの使い分けの目安は次のとおりです。

|  | Claude Managed Agents | Agent SDK |
| --- | --- | --- |
| **向いている用途** | プロダクション・長時間タスク | 軽量なカスタムエージェント |
| **インフラ管理** | Anthropicが管理 | 自前でホスティング |
| **カスタマイズ性** | 設定ベース | フルカスタム |
| **組み込みサンドボックス** | あり | なし |

---

## まとめ

* **Claude Managed Agents**は、Claudeをエージェントとして動かすフルマネージドハーネスです（2026-04-08 パブリックベータ）
* **Agent → Environment → Session → Events** の4リソースで構成されます
* 組み込みツール8種（bash/read/write/edit/glob/grep/web\_fetch/web\_search）に加えてカスタムツールも定義可能です
* **$0.08/セッション時間**（実行中のみ課金）+ 標準トークン料金の料金体系です
* ant CLIを使うとYAMLベースでエージェント設定をバージョン管理できます
* 全APIアカウントで利用可能（betaヘッダー `managed-agents-2026-04-01` が必要、SDKは自動設定）

エージェントループ・サンドボックス・ツール実行のインフラを自前で管理するコストを削減し、「エージェントに何をさせるか」の設計に集中できる点が最大の価値です。長時間タスク・バッチ処理・非同期ワークフローへの活用が期待されます。

## 参考リンク
