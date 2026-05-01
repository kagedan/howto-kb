---
id: "2026-04-30-claude-managed-agents入門-3層アーキテクチャとpython実装ガイド-01"
title: "Claude Managed Agents入門 — 3層アーキテクチャとPython実装ガイド"
url: "https://qiita.com/kai_kou/items/f93f9e95c357edaa51b6"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "qiita"]
date_published: "2026-04-30"
date_collected: "2026-05-01"
summary_by: "auto-rss"
---

<!-- IMAGE_SLOT: hero | Claude Managed Agentsのアーキテクチャ全体図。左側に「Agent（Brain）」ブロック、中央に「Harness（Orchestration Loop）」ブロック、右側に「Sandbox（Cloud Container）」ブロックを配置。三者が矢印で繋がり、下部に「Session（Append-only Event Log）」が横断する形で描かれる。背景は白、Blue/Slate/Emerald配色、フラットデザイン。英語ラベルのみ。 -->

## はじめに

2026年4月8日、Anthropicは**Claude Managed Agents**をパブリックベータとして公開しました。

これまでClaude APIでAIエージェントを構築する場合、開発者自身がエージェントループ・ツール実行基盤・実行サンドボックスをゼロから実装する必要がありました。Claude Managed Agentsはそれらを**マネージドインフラとして提供**し、開発者がエージェントのロジックとシステムプロンプトの設計に集中できる環境を整えます。

### この記事で学べること

- Claude Managed Agentsの3層アーキテクチャ（Session / Harness / Sandbox）
- Messages APIとの使い分け
- Pythonを使ったクイックスタート（Agent作成→Session起動→ストリーミング）
- 料金体系と注意点

### 対象読者

- Anthropic APIでAIエージェントを開発しているエンジニア
- 長時間・非同期なエージェントタスクを本番環境に投入したい方
- エージェントインフラの自前実装に課題を感じている方

### 前提条件

- Anthropic Consoleアカウント・APIキー
- Python 3.10以上

## TL;DR

- Claude Managed Agentsは**Agent / Environment / Session / Events**の4コンセプトで構成される
- 内部アーキテクチャは**Session（イベントログ）/ Harness（オーケストレーション）/ Sandbox（コンテナ）**に分離されており、信頼性と再起動時のゼロデータロスを実現
- 料金は**標準トークン料金 + $0.08/セッション時間**[^pricing]
- 現在パブリックベータ、ベータヘッダー `managed-agents-2026-04-01` が必要

[^pricing]: [Claude Managed Agents pricing](https://platform.claude.com/docs/en/about-claude/pricing#claude-managed-agents-pricing)（Anthropic公式ドキュメント）

---

## Claude Managed Agentsとは

Claude Managed Agentsは、Claudeを**自律エージェントとして動作させるためのマネージドインフラ**です。

従来のMessages APIとの比較を下表に示します（[公式ドキュメント](https://platform.claude.com/docs/en/managed-agents/overview)より）。

| | Messages API | Claude Managed Agents |
|---|---|---|
| **特徴** | モデルへの直接プロンプトアクセス | 設定可能なエージェントハーネス＋マネージドインフラ |
| **最適なケース** | カスタムエージェントループ・細粒度の制御 | 長時間タスク・非同期処理 |
| **エージェントループ** | 自前実装が必要 | 組み込み済み |
| **サンドボックス** | 自前構築が必要 | クラウドコンテナを自動プロビジョニング |
| **状態管理** | 自前実装が必要 | セッション単位の永続化 |

Managed Agentsが特に威力を発揮するのは、以下のようなワークロードです。

- 数分〜数時間にわたって複数ツールを呼び出し続けるタスク
- セキュアなコンテナ内でのコード実行が必要なタスク
- インフラ構築コストを最小化したいプロダクション環境

---

## 4つのコアコンセプト

Claude Managed Agentsは4つのコンセプトを中心に設計されています。

<!-- IMAGE_SLOT: concept | Claude Managed Agentsの4コンセプト図。上段に「Agent（Model + System Prompt + Tools + MCP）」ブロック、「Environment（Cloud Container Config）」ブロック。下段に「Session（Running Instance）」ブロック、「Events（User/Tool/Status Messages）」ブロック。矢印でフローを示す。白背景、フラットデザイン、英語ラベル。 -->

| コンセプト | 説明 |
|-----------|------|
| **Agent** | モデル・システムプロンプト・ツール・MCPサーバー・スキルの定義体。一度作成してIDで再利用可能 |
| **Environment** | エージェントが実行されるコンテナのテンプレート。プリインストールパッケージ・ネットワークアクセスルールなどを設定 |
| **Session** | AgentとEnvironmentを参照する実行インスタンス。特定のタスクを実行し出力を生成する単位 |
| **Events** | アプリケーションとエージェントの間でやり取りされるメッセージ（ユーザーターン・ツール結果・ステータス更新） |

---

## 3層アーキテクチャの設計思想

Anthropicの[エンジニアリングブログ](https://www.anthropic.com/engineering/managed-agents)では、Managed Agentsの設計を**「ブレイン・ハンズ・セッションの分離」**と表現しています。

以前は密結合だった3つのコンポーネントを独立した抽象化レイヤーとして切り出すことで、耐障害性と拡張性を実現しています。

### Session — 追記専用イベントログ

**Session**はエージェントが実行した全履歴を格納する**追記専用（Append-only）のイベントログ**です。

ハーネスがクラッシュしても、`wake(sessionId)` でイベントログを取得して処理を再開できます。Claude のコンテキストウィンドウの外側に状態を永続化することで、**ゼロデータロスの再起動**を実現しています。

### Harness — ステートレスなオーケストレーションループ

**Harness**はClaudeを呼び出し、ツールコールをルーティングする**ステートレスなループ**です。

ステートレス設計により、ハーネス自体の再起動コストを最小化。プロンプトキャッシング・コンテキスト圧縮などのパフォーマンス最適化が組み込まれており、**time-to-first-tokenをp50で約60%、p95で90%以上削減**[^perf]しています。

[^perf]: [Scaling Managed Agents: Decoupling the brain from the hands](https://www.anthropic.com/engineering/managed-agents)（Anthropic Engineering Blog）

### Sandbox — 分離されたクラウドコンテナ

**Sandbox**はコードや各種ツールが実際に実行される**分離コンテナ**です。

コンテナはツールコール時にオンデマンドでプロビジョニングされます。コンテナに障害が発生してもハーネスが再試行を処理するため、データ損失は発生しません。また、**認証トークン・シークレットはSandboxに渡されない**セキュリティ設計になっています。

---

## クイックスタート: Python実装

以下の手順でClaude Managed Agentsの最初のセッションを構築できます。


> 現在パブリックベータです。全エンドポイントにベータヘッダー `managed-agents-2026-04-01` が必要ですが、SDKを使用する場合は自動設定されます。


### インストール

```bash
pip install anthropic
export ANTHROPIC_API_KEY="your-api-key-here"
```

### Step 1: Agentの作成

モデル・システムプロンプト・ツールを定義したAgentを作成します。`agent_toolset_20260401` を指定すると、Bash・ファイル操作・Webサーチなどの全組み込みツールが有効になります。

```python
from anthropic import Anthropic

client = Anthropic()

agent = client.beta.agents.create(
    name="Coding Assistant",
    model="claude-opus-4-7",
    system="You are a helpful coding assistant. Write clean, well-documented code.",
    tools=[
        {"type": "agent_toolset_20260401"},
    ],
)

print(f"Agent ID: {agent.id}")
```

作成したAgentは `agent.id` で参照でき、複数のSessionで再利用可能です。

### Step 2: Environmentの作成

Agentが実行されるコンテナ設定を定義します。

```python
environment = client.beta.environments.create(
    name="quickstart-env",
    config={
        "type": "cloud",
        "networking": {"type": "unrestricted"},
    },
)

print(f"Environment ID: {environment.id}")
```

`networking.type` は `unrestricted`（アウトバウンド無制限）または `egress-only` などで制御できます。

### Step 3: Sessionの開始

AgentとEnvironmentを参照してSessionを作成します。

```python
session = client.beta.sessions.create(
    agent=agent.id,
    environment_id=environment.id,
    title="My first session",
)

print(f"Session ID: {session.id}")
```

### Step 4: メッセージ送信とSSEストリーミング

ストリームを開き、ユーザーメッセージを送信してイベントを受信します。

```python
with client.beta.sessions.events.stream(session.id) as stream:
    # ストリームオープン後にメッセージを送信
    client.beta.sessions.events.send(
        session.id,
        events=[
            {
                "type": "user.message",
                "content": [
                    {
                        "type": "text",
                        "text": "Create a Python script that generates the first 20 Fibonacci numbers and saves them to fibonacci.txt",
                    },
                ],
            },
        ],
    )

    # リアルタイムにイベントを処理
    for event in stream:
        match event.type:
            case "agent.message":
                for block in event.content:
                    print(block.text, end="", flush=True)
            case "agent.tool_use":
                print(f"\n[Using tool: {event.name}]")
            case "session.status_idle":
                print("\n\nAgent finished.")
                break
```

実行すると、Claudeはコードを書き、コンテナ内でBashを実行してファイルを生成し、結果を検証するまで自律的に動作します。

```text
I'll create a Python script that generates the first 20 Fibonacci numbers.
[Using tool: write]
[Using tool: bash]
The script ran successfully. Let me verify the output file.
[Using tool: bash]
fibonacci.txt contains the first 20 Fibonacci numbers (0 through 4181).

Agent finished.
```

---

## 組み込みツール

`agent_toolset_20260401` を有効にすると以下のツールがClaude Managed Agentsで利用可能になります（[公式ドキュメント](https://platform.claude.com/docs/en/managed-agents/tools)）。

| ツール | 説明 |
|-------|------|
| **Bash** | コンテナ内でシェルコマンドを実行 |
| **File operations** | ファイルの読み書き・編集・glob・grep |
| **Web search** | Webを検索して結果を取得 |
| **Web fetch** | URLからコンテンツを取得 |
| **MCP servers** | 外部ツールプロバイダーに接続 |

---

## 料金体系

Claude Managed Agentsの料金は2要素から構成されます[^pricing]。

| 課金要素 | 料金 |
|---------|------|
| モデル推論（入力/出力トークン） | 通常のClaude API料金と同一 |
| セッション実行時間 | **$0.08/セッション時間**（ミリ秒単位で計測） |

実行時間の課金はSessionのステータスが `running` の間のみ発生します。`idle`・`terminated` 状態では課金されません。

たとえば、アクティブな実行が90秒の場合:

```
$0.08 × (90 / 3600) ≈ $0.002
```

---

## レート制限

| 操作 | 上限 |
|------|------|
| 作成系エンドポイント（Agent・Session・Environment等の作成） | 300リクエスト/分 |
| 読み取り系エンドポイント（取得・一覧・ストリーミング等） | 600リクエスト/分 |

組織レベルの支出上限・ティアベースのレート制限も適用されます。

---

## Messages APIとの使い分け指針

| 条件 | 推奨 |
|------|------|
| エージェントループを独自に制御したい | Messages API |
| 細粒度のコンテキスト管理が必要 | Messages API |
| タスクが数分〜数時間かかる | **Managed Agents** |
| コードの実行・ファイル操作が必要 | **Managed Agents** |
| インフラ構築コストを最小化したい | **Managed Agents** |
| セッション間で状態を永続化したい | **Managed Agents** |

---

## 注意点

- **パブリックベータ**: APIの仕様変更の可能性があります。ベータヘッダー `managed-agents-2026-04-01` は必須です
- **Outcomes/Multi-agentはリサーチプレビュー**: 利用には[別途申請](https://claude.com/form/claude-managed-agents)が必要です
- **ブランディング制約**: 製品への組み込み時に「Claude Code」「Claude Cowork」として表示することは禁止されています（[ガイドライン](https://platform.claude.com/docs/en/managed-agents/overview#branding-guidelines)）

---

## まとめ

- Claude Managed Agentsは**Agent / Environment / Session / Events**の4コンセプトで構成されるマネージドエージェントインフラ
- 内部は**Session（イベントログ）/ Harness（ステートレスループ）/ Sandbox（コンテナ）**の3層に分離されており、耐障害性と再起動時のゼロデータロスを実現
- Pythonでは `client.beta.agents.create()` → `client.beta.environments.create()` → `client.beta.sessions.create()` → SSEストリーミングの4ステップで動作する
- 料金は**$0.08/セッション時間 + 通常のトークン料金**

長時間・自律的なエージェントタスクの本番化において、自前でエージェントループとサンドボックスを実装するコストを大幅に削減できる選択肢として検討する価値があります。

## 参考リンク

- [Claude Managed Agents overview](https://platform.claude.com/docs/en/managed-agents/overview) — 公式ドキュメント（概要・コアコンセプト）
- [Quickstart](https://platform.claude.com/docs/en/managed-agents/quickstart) — 公式クイックスタートガイド
- [Scaling Managed Agents: Decoupling the brain from the hands](https://www.anthropic.com/engineering/managed-agents) — Anthropicエンジニアリングブログ（アーキテクチャ設計解説）
- [Anthropic Introduces Managed Agents to Simplify AI Agent Deployment](https://www.infoq.com/news/2026/04/anthropic-managed-agents/) — InfoQ
