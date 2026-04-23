---
id: "2026-04-11-claude-managed-agents入門-インフラ不要でaiエージェントを本番運用する-01"
title: "Claude Managed Agents入門 — インフラ不要でAIエージェントを本番運用する"
url: "https://qiita.com/kai_kou/items/69bef4fccad0163dca1e"
source: "qiita"
category: "ai-workflow"
tags: ["API", "AI-agent", "qiita"]
date_published: "2026-04-11"
date_collected: "2026-04-12"
summary_by: "auto-rss"
---

## はじめに

2026年4月8日、Anthropicは[Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview)をパブリックベータとして公開しました。これは、AIエージェントをAnthropicのマネージドインフラ上で動かすためのフルマネージドエージェントハーネスです。

自前でエージェントループを実装し、サンドボックスを用意し、ツール実行レイヤーを構築する必要がなくなりました。エージェントが実行するコンテナ、ファイルシステム、ツール群をAnthropicが管理します。

### この記事で学べること

* Claude Managed Agentsの4つのコアコンセプト（Agent/Environment/Session/Events）
* Messages APIとの使い分け
* Pythonを使ったエージェントの作成・環境構築・セッション開始・ストリーミングの実装手順
* 8種類の組み込みツールの概要と設定方法
* 環境のパッケージ設定・ネットワーク制御の方法
* 料金とレート制限の詳細

### 対象読者

* AIエージェントを本番環境に組み込みたいエンジニア
* エージェントの自前実装（ループ管理・サンドボックス）を避けたい方
* Anthropic APIを使ったアプリ開発者

### 前提条件

* Anthropic APIキー
* Python 3.9+
* `pip install anthropic` でSDKインストール済み

---

## TL;DR

* **Claude Managed Agents** = Anthropic管理インフラ上で動くフルマネージドAIエージェント基盤（2026-04-08 公開ベータ）
* 全APIリクエストに `managed-agents-2026-04-01` betaヘッダーが必要（SDKは自動付与）
* コアコンセプト: **Agent**（モデル定義）・**Environment**（コンテナ設定）・**Session**（実行インスタンス）・**Events**（通信単位）
* 組み込みツール8種: `bash` / `read` / `write` / `edit` / `glob` / `grep` / `web_fetch` / `web_search`
* 料金: **$0.08/セッション時間** + 通常APIトークン料金

---

## Claude Managed Agentsとは

Claude Managed Agentsは、AnthropicがホストするAIエージェント実行基盤です。

従来のMessages APIを使ったエージェント実装では、以下を自前で用意する必要がありました:

* **エージェントループ**: ツール呼び出し → 結果受取 → 再プロンプト の繰り返し処理
* **サンドボックス環境**: コード実行やファイル操作のための安全な分離環境
* **ツール実行レイヤー**: Bash・ファイル操作・Web検索等の実装
* **セッション管理**: 長時間実行タスクの状態保持とコンテキスト管理

Claude Managed Agentsはこれらをすべてマネージドサービスとして提供します。

### 4つのコアコンセプト

| コンセプト | 説明 |
| --- | --- |
| **Agent** | モデル・システムプロンプト・ツール・MCPサーバー・スキルの定義セット |
| **Environment** | コンテナのテンプレート設定（パッケージ・ネットワーク制御） |
| **Session** | AgentとEnvironmentを参照して起動する実行インスタンス（タスク実行単位） |
| **Events** | アプリケーションとエージェントの間で交わされるメッセージ（ユーザー入力・ツール結果・ステータス） |

AgentとEnvironmentは一度作成してIDを保存しておけば、複数のSessionで使い回せます。各Sessionは独立したコンテナインスタンスを持ち、ファイルシステムは共有されません。

### Messages API との使い分け

|  | Messages API | Claude Managed Agents |
| --- | --- | --- |
| **最適なケース** | カスタムループ・細かい制御 | 長時間タスク・非同期処理 |
| **実行環境** | 自前で用意 | Anthropicがホスト |
| **エージェントループ** | 自前実装 | マネージド |
| **ツール実行** | 自前実装 | 組み込み（8種） |
| **インフラ負荷** | 高い | 低い |

---

## セットアップ

### SDKのインストール

```
pip install anthropic
export ANTHROPIC_API_KEY="your-api-key-here"
```

### ant CLI（オプション）

ターミナルから直接エージェントやセッションを操作できるCLIも提供されています。

```
# macOS (Homebrew)
brew install anthropics/tap/ant
xattr -d com.apple.quarantine "$(brew --prefix)/bin/ant"

# Linux/WSL
VERSION=1.0.0
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m | sed -e 's/x86_64/amd64/' -e 's/aarch64/arm64/')
curl -fsSL "https://github.com/anthropics/anthropic-cli/releases/download/v${VERSION}/ant_${VERSION}_${OS}_${ARCH}.tar.gz" \
  | sudo tar -xz -C /usr/local/bin ant

ant --version
```

---

## クイックスタート: 5ステップで最初のエージェントを動かす

公式ドキュメントの[クイックスタート](https://platform.claude.com/docs/en/managed-agents/quickstart)を参考に、Pythonで動かす手順を解説します。

### ステップ1: Agentを作成する

Agentにはモデル・システムプロンプト・使用するツールを定義します。

```
from anthropic import Anthropic

client = Anthropic()

agent = client.beta.agents.create(
    name="Coding Assistant",
    model="claude-sonnet-4-6",
    system="You are a helpful coding assistant. Write clean, well-documented code.",
    tools=[
        {"type": "agent_toolset_20260401"},
    ],
)

print(f"Agent ID: {agent.id}, version: {agent.version}")
```

`agent_toolset_20260401` を指定すると、Bash・ファイル操作・Web検索を含む[組み込みツール8種](#%E7%B5%84%E3%81%BF%E8%BE%BC%E3%81%BF%E3%83%84%E3%83%BC%E3%83%AB%E4%B8%80%E8%A6%A7)がすべて有効になります。返却された `agent.id` を保存してください。

> すべてのManaged AgentsエンドポイントはPythonクライアントからも `client.beta.agents` 以下でアクセスします。SDKは `managed-agents-2026-04-01` betaヘッダーを自動的に付与するため、手動設定は不要です。

### ステップ2: Environmentを作成する

Environmentはエージェントが実行されるコンテナのテンプレートです。

```
environment = client.beta.environments.create(
    name="quickstart-env",
    config={
        "type": "cloud",
        "networking": {"type": "unrestricted"},
    },
)

print(f"Environment ID: {environment.id}")
```

`unrestricted` ネットワーキングを指定すると、コンテナから外部への全接続が許可されます（一般的な安全ブロックリストを除く）。本番環境では `limited` を推奨します（後述）。

### ステップ3: Sessionを開始する

AgentとEnvironmentのIDを参照してセッションを作成します。

```
session = client.beta.sessions.create(
    agent=agent.id,
    environment_id=environment.id,
    title="Quickstart session",
)

print(f"Session ID: {session.id}")
```

`title` は任意のラベルで、管理のためのメモとして使えます。

### ステップ4: メッセージを送信してストリーミング受信する

ストリームを開き、ユーザーイベントを送信して、エージェントの応答をリアルタイムに受け取ります。

```
with client.beta.sessions.events.stream(session.id) as stream:
    # ストリームオープン後にユーザーメッセージを送信
    client.beta.sessions.events.send(
        session.id,
        events=[
            {
                "type": "user.message",
                "content": [
                    {
                        "type": "text",
                        "text": "フィボナッチ数列の最初の20個を生成してfibonacci.txtに保存するPythonスクリプトを作成してください",
                    },
                ],
            },
        ],
    )

    # イベントをリアルタイムに処理
    for event in stream:
        match event.type:
            case "agent.message":
                for block in event.content:
                    print(block.text, end="", flush=True)
            case "agent.tool_use":
                print(f"\n[ツール実行: {event.name}]")
            case "session.status_idle":
                print("\n\nエージェントがタスクを完了しました。")
                break
```

エージェントはPythonスクリプトを作成し、コンテナ内で実行して出力ファイルを確認するまで、自律的にツールを使い続けます。

```
フィボナッチ数列を生成するPythonスクリプトを作成します。
[ツール実行: write]
[ツール実行: bash]
スクリプトが正常に実行されました。出力ファイルを確認します。
[ツール実行: bash]
fibonacci.txtにフィボナッチ数列の最初の20個（0〜4181）が保存されています。

エージェントがタスクを完了しました。
```

### ステップ5: セッションの仕組みを理解する

ユーザーイベントを送信すると、バックグラウンドで以下が進行します:

1. **コンテナプロビジョニング**: Environment設定に基づきクラウドコンテナを起動
2. **エージェントループ実行**: メッセージを解析し、どのツールを使うかを判断
3. **ツール実行**: ファイル書き込み・Bashコマンド等をコンテナ内で実行
4. **イベントストリーミング**: 進行中の応答・ツール使用をServer-Sent Events（SSE）でリアルタイム送信
5. **アイドル**: `session.status_idle` イベントを発行してタスク完了を通知

---

## 組み込みツール一覧

`agent_toolset_20260401` で有効になるツールの一覧です。

| ツール名 | 説明 |
| --- | --- |
| `bash` | コンテナ内でシェルコマンドを実行 |
| `read` | ローカルファイルシステムからファイルを読み取り |
| `write` | ローカルファイルシステムにファイルを書き込み |
| `edit` | ファイル内の文字列を置換（差分編集） |
| `glob` | globパターンで高速ファイル検索 |
| `grep` | 正規表現でファイル内テキストを検索 |
| `web_fetch` | URLからコンテンツを取得 |
| `web_search` | Webを検索して情報を取得 |

### 特定のツールを無効化する

```
agent = client.beta.agents.create(
    name="Restricted Agent",
    model="claude-sonnet-4-6",
    tools=[
        {
            "type": "agent_toolset_20260401",
            "configs": [
                {"name": "web_fetch", "enabled": False},
                {"name": "web_search", "enabled": False},
            ],
        },
    ],
)
```

### 特定のツールだけを有効化する

`default_config.enabled` を `False` にすることで、明示的に許可したツールだけを使わせることができます。

```
agent = client.beta.agents.create(
    name="File-only Agent",
    model="claude-sonnet-4-6",
    tools=[
        {
            "type": "agent_toolset_20260401",
            "default_config": {"enabled": False},
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

## 環境の詳細設定

### パッケージのプリインストール

Environment作成時に `packages` フィールドで依存ライブラリを指定しておくと、セッション開始前にコンテナへ自動インストールされます。

```
environment = client.beta.environments.create(
    name="data-analysis",
    config={
        "type": "cloud",
        "packages": {
            "pip": ["pandas", "numpy", "scikit-learn"],
            "npm": ["express"],
            "apt": ["ffmpeg"],
        },
        "networking": {"type": "unrestricted"},
    },
)
```

対応パッケージマネージャーは以下のとおりです（アルファベット順に実行）:

| フィールド | パッケージマネージャー |
| --- | --- |
| `apt` | システムパッケージ (apt-get) |
| `cargo` | Rust (cargo) |
| `gem` | Ruby (gem) |
| `go` | Goモジュール |
| `npm` | Node.js (npm) |
| `pip` | Python (pip) |

### ネットワーク制御

本番環境では `limited` モードで最小限のアクセスのみ許可することが[公式ドキュメントで推奨](https://platform.claude.com/docs/en/managed-agents/environments)されています。

```
environment = client.beta.environments.create(
    name="production-env",
    config={
        "type": "cloud",
        "networking": {
            "type": "limited",
            "allowed_hosts": ["api.example.com"],
            "allow_mcp_servers": True,      # MCPサーバーへのアクセスを許可
            "allow_package_managers": True,  # PyPI/npmへのアクセスを許可
        },
    },
)
```

| モード | 説明 |
| --- | --- |
| `unrestricted`（デフォルト） | 安全ブロックリストを除く全アウトバウンド接続を許可 |
| `limited` | `allowed_hosts` で指定したホストのみ許可 |

---

## 料金とレート制限

### 料金

公式の[料金ページ](https://platform.claude.com/docs/en/about-claude/pricing)によると:

| 課金項目 | 単価 |
| --- | --- |
| セッション実行時間 | **$0.08 / セッション時間** |
| トークン（入力・出力） | 通常のAPIトークン料金 |

セッション時間の課金はエージェントがアクティブに動いている時間に対して発生します。

### レート制限

| 操作 | 上限 |
| --- | --- |
| 作成系エンドポイント（agents/sessions/environments等の作成） | 60リクエスト / 分 |
| 読み取り系エンドポイント（取得・一覧・ストリーム等） | 600リクエスト / 分 |

組織レベルのスペンド制限・階層別レート制限も適用されます。

---

## Research Preview機能

現在、以下の機能がResearch Previewとして[アクセス申請](https://claude.com/form/claude-managed-agents)で利用可能です:

| 機能 | 概要 |
| --- | --- |
| **Outcomes** | エージェントが達成すべき成果を定義し、自動評価を行う |
| **Multi-agent** | 複数のエージェントが協調するマルチエージェントワークフロー |
| **Memory** | セッションをまたいだ長期記憶の保持 |

---

## まとめ

Claude Managed Agentsを使うと、エージェントループ・サンドボックス・ツール実行レイヤーの自前実装が不要になります。

### 得られた知見

* **Agent / Environment / Session / Events** の4コンセプトを理解すれば、すぐに動かせる
* `agent_toolset_20260401` で8種のツールが一括有効化でき、個別の有効/無効制御も可能
* 環境はパッケージのプリインストールとネットワーク制御をサポート（本番は `limited` モード推奨）
* `session.status_idle` イベントでエージェントの完了を検知する

### Messages APIとの使い分け指針

* **Minutes/Hours単位の長時間タスク** → Managed Agents
* **カスタムロジック・細かい制御が必要** → Messages API
* **コードの自律実行・ファイル生成が必要** → Managed Agents

### 次のステップ

---

## 参考リンク
