---
id: "2026-04-09-anthropic-が発表した-claude-マネージドエージェント-エージェント基盤をフルマネージ-01"
title: "Anthropic が発表した Claude マネージドエージェント — エージェント基盤をフルマネージドで運用する新 API - Qiita"
url: "https://qiita.com/imk1t/items/48821dc85d8ec5cc93f8"
source: "qiita"
category: "ai-workflow"
tags: ["API", "qiita"]
date_published: "2026-04-09"
date_collected: "2026-04-09"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude でちゃんとした「自律エージェント」を本番で動かそうとすると、いつも同じ壁にぶつかります。Messages API の上にエージェントループを書き、ツール呼び出しを捌き、サンドボックス付きの実行環境を用意し、セッションの会話履歴とファイルシステムを永続化し、長時間タスクのチェックポイントを作り、スケーリングとモニタリングを整える — ここまでやってようやくユーザーに提供できる状態になります。多くのチームがこの「ハーネス部分」で時間を溶かしてきました。

Anthropic はこのハーネスをマネージドサービスとして提供する **Claude Managed Agents** を public beta として公開しました。beta ヘッダー `managed-agents-2026-04-01` を付けるだけで、`/v1/agents`・`/v1/environments`・`/v1/sessions` という 3 つのリソースを介して、エージェントループ・組み込みツール・サンドボックス・セッション永続化がすべて API ネイティブで使えるようになります。

この記事では、以下の内容を 2026 年 4 月時点の公式ドキュメントに基づいて解説します。

* Claude Managed Agents が解決する課題と全体像
* `agent` / `environment` / `session` という主要概念の関係
* Python SDK による最小の Quickstart
* Messages API や Agent SDK との使い分け
* 拡張ポイント（カスタムツール、MCP、マルチエージェント、メモリ）
* 料金モデルと現時点での制限

本記事の内容は 2026 年 4 月時点の情報です。Claude Managed Agents は public beta として提供されており、beta ヘッダー `managed-agents-2026-04-01` が必須です。今後の更新で API や料金が変更される可能性があります。

## Claude マネージドエージェントとは

Claude Managed Agents は、一言でいえば **「Claude のエージェントループとツール実行環境を Anthropic がホストしてくれる API」** です。

従来、エージェントを本番投入するには以下のすべてを自前で組み上げる必要がありました。

* エージェントループ（Claude に考えさせて、ツールを呼び、結果をフィードバックする無限ループ）
* 安全なサンドボックス（任意のコードを実行できる環境の隔離）
* 認証・認可（エージェントが外部リソースに触れるときの権限管理）
* セッションの永続化（会話履歴だけでなく、読み書きしたファイルの状態も含めた復元）
* 長時間実行のためのチェックポイント
* ツールオーケストレーションとコンテキスト管理

Managed Agents はこれらすべてを API の内側に押し込めます。開発者側は「どんなエージェントか (agent)」と「どんな実行コンテナで動かすか (environment)」を定義し、会話のライフサイクル (session) を API 経由で回すだけで済みます。

### 現時点での提供形態

| 項目 | 内容 |
| --- | --- |
| **ステータス** | Public beta |
| **beta ヘッダー** | `anthropic-beta: managed-agents-2026-04-01` |
| **SDK 対応** | Python / TypeScript（`beta` 名前空間） |
| **リサーチプレビュー** | マルチエージェント (`multiagent`) / メモリ (`memory`) / 成果物検証 (`outcomes`) は別途アクセス申請が必要 |

## アーキテクチャと主要概念

Managed Agents は 4 つのリソースの組み合わせで動きます。

| 概念 | エンドポイント | 役割 |
| --- | --- | --- |
| **Agent** | `/v1/agents` | モデル・システムプロンプト・ツール・MCP サーバーを束ねた「エージェント定義」。バージョン管理される |
| **Environment** | `/v1/environments` | 実行コンテナの設定（クラウド / ネットワーク / マウントリソース） |
| **Session** | `/v1/sessions` | Agent × Environment の実行インスタンス。会話履歴とコンテナの状態が永続化される |
| **Event** | `/v1/sessions/{id}/events` | セッション中にやり取りされるユーザーメッセージ・エージェントの応答・ツール使用の単位 |

ポイントは **Agent と Session が分離されている** ことです。1 つの Agent 定義から複数の Session を生やせるため、同じ「コーディングアシスタント」を複数のユーザーに同時提供するようなマルチテナント設計がそのまま API で表現できます。

### セッションのステータス

Session は実行中に次のステータスを遷移します。

| ステータス | 意味 |
| --- | --- |
| `rescheduling` | コンテナの準備中 |
| `running` | エージェントが動作中（課金対象） |
| `idle` | ユーザーの入力待ち（課金されない） |
| `terminated` | 終了済み |

セッションは一時停止してから後で再開できるため、返ってきたときに「エージェントが前回読んだファイル」「前回の分析結果」「前回の決定」をそのまま引き継げます。

## Quickstart: Python SDK で最初のエージェントを動かす

ここからは実際に動かす手順です。公式の Quickstart に沿って、組み込みツールセットだけで動くコーディングアシスタントを作ります。

### 事前準備

最新の Anthropic Python SDK をインストールし、API キーを環境変数に設定します。

```
pip install -U anthropic
export ANTHROPIC_API_KEY="sk-ant-..."
```

Managed Agents は beta リソースなので、SDK では `client.beta.*` 名前空間を経由します。beta ヘッダー (`managed-agents-2026-04-01`) は SDK が自動で付与してくれます。

### 1. エージェントを作成する

エージェントにはモデル・システムプロンプト・ツールセットを渡します。ここでは **`agent_toolset_20260401`** という組み込みツールセットを指定するだけで、`bash` / `read` / `write` / `edit` / `glob` / `grep` / `web_fetch` / `web_search` の 8 種類のツールが一度に有効になります。

```
from anthropic import Anthropic

client = Anthropic()

agent = client.beta.agents.create(
    name="Coding Assistant",
    model="claude-sonnet-4-6",
    system="あなたは親切なコーディングアシスタントです。きれいでコメント付きのコードを書いてください。",
    tools=[
        {"type": "agent_toolset_20260401"},
    ],
)

print(f"Agent ID: {agent.id}, version: {agent.version}")
```

返ってくる `agent.id` は `agent_011CZkYpogX7uDKUyvBTophP` のようなプレフィックス付き ID です。エージェントはバージョニングされており、システムプロンプトやツールを更新すると新しいバージョンが作られます。

### 2. Environment を作成する

Environment は Claude が実際にコードを実行するコンテナの設定です。ここでは最小設定として「クラウド上で動く・ネットワーク制限なし」の環境を作ります。

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

### 3. Session を作成してストリーミングする

Agent と Environment が揃ったら Session を開き、ユーザーメッセージを `events.send` で送り込みつつ、`events.stream` でサーバーから流れてくるイベントを購読します。

```
session = client.beta.sessions.create(
    agent=agent.id,
    environment_id=environment.id,
    title="Quickstart session",
)

print(f"Session ID: {session.id}")

with client.beta.sessions.events.stream(session.id) as stream:
    # ストリームを開いた後にユーザーメッセージを送る
    client.beta.sessions.events.send(
        session.id,
        events=[
            {
                "type": "user.message",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "フィボナッチ数列の最初の 20 項を生成して "
                            "fibonacci.txt に保存する Python スクリプトを作成してください。"
                        ),
                    },
                ],
            },
        ],
    )

    for event in stream:
        match event.type:
            case "agent.message":
                for block in event.content:
                    print(block.text, end="")
            case "agent.tool_use":
                print(f"\n[Using tool: {event.name}]")
            case "session.status_idle":
                print("\n\nAgent finished.")
                break
```

ポイントは 3 つあります。

* **`stream` を先に開いてから `send` を呼ぶ**: ストリームが開く前にイベントを送るとエージェントの応答を取りこぼす可能性があります
* **イベントの `type` でハンドリングする**: `agent.message` でテキスト、`agent.tool_use` でツール使用、`session.status_idle` で終了を検出します
* **`session.status_idle` を受け取るまでループを続ける**: これがユーザーの次の入力を待つ安定状態です

### 4. 実行時に流れてくるイベントのイメージ

上のスクリプトを実行すると、だいたい次のようなログが流れてきます。

```
Python でフィボナッチ数列を生成し、ファイルに保存するスクリプトを作成します。

[Using tool: write]
[Using tool: bash]

fibonacci.py を作成し、実行して fibonacci.txt に保存しました。
生成された数列は次の通りです: 0, 1, 1, 2, 3, 5, 8, 13, ...

Agent finished.
```

Claude が `write` ツールで `fibonacci.py` を書き、`bash` ツールで実行し、生成された `fibonacci.txt` を Environment のコンテナ内に残したままセッションが idle になります。このセッションを後でもう一度開けば、同じファイルシステムに続きから作業させることができます。

## Messages API / Agent SDK との使い分け

Claude には似た名前のプロダクトがいくつかあり、混乱しやすいところです。ざっくりの棲み分けは次の表の通りです。

|  | Messages API | Claude Agent SDK | **Claude Managed Agents** |
| --- | --- | --- | --- |
| 実行場所 | 自前 | 自前（ローカル / 自社インフラ） | **Anthropic がホスト** |
| エージェントループ | 自分で書く | SDK が提供 | **API に内蔵** |
| サンドボックス | 自分で用意 | 自分で用意 | **組み込み** |
| セッション永続化 | 自分で実装 | SDK のセッション機能 | **API ネイティブ** |
| 組み込みツール | なし（自前で定義） | Read / Write / Bash など一式 | `agent_toolset_20260401` として一式 |
| 向いている用途 | カスタム細粒度制御 | CI/CD・開発ワークフロー | **長時間・非同期・本番運用** |

判断の目安はシンプルです。

* **長時間走らせたい・複数ユーザー向けに運用したい・運用コストを下げたい** → Managed Agents
* **ローカル開発環境やパイプラインでエージェントを動かしたい・挙動を細かく制御したい** → Agent SDK
* **完全に自分でループを組みたい・エージェント以外の用途も含めた汎用呼び出しが主** → Messages API

Agent SDK と Managed Agents は同じ「エージェント的な考え方」を共有しており、ツールセットの名前や挙動も揃えられています。ローカルで Agent SDK を使って試作し、本番で Managed Agents に移すといった移行もしやすくなっています。

## 拡張ポイント

組み込みツールだけでも動くエージェントは作れますが、実用ではたいてい外部リソースやドメイン固有のロジックを繋ぎ込みたくなります。Managed Agents は次の 4 つの拡張ポイントを持っています。

### カスタムツール

`type: "custom"` と JSON Schema で独自ツールを定義できます。ツールの実行はアプリケーション側で行い、結果をイベントとして Session に送り返す形です。

```
agent = client.beta.agents.create(
    name="Weather Agent",
    model="claude-sonnet-4-6",
    tools=[
        {"type": "agent_toolset_20260401"},
        {
            "type": "custom",
            "name": "get_weather",
            "description": "指定した都市の現在の天気を取得します",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "都市名"},
                },
                "required": ["location"],
            },
        },
    ],
)
```

### MCP サーバー

Agent には MCP（Model Context Protocol）サーバーを差し込めます。PostgreSQL や GitHub、Slack、ファイルシステムなど、既存の MCP エコシステムにある 1 万を超えるサーバーをそのまま再利用できます。

### マルチエージェント（research preview）

`callable_agents` を指定すると、コーディネーターのエージェントから別のエージェントに仕事を委譲できます。各エージェントは独立したスレッド（＝独立した会話履歴）を持ちますが、同じコンテナのファイルシステムは共有されます。

```
orchestrator = client.beta.agents.create(
    name="Engineering Lead",
    model="claude-sonnet-4-6",
    system="あなたはエンジニアリングリードです。コードレビューは reviewer、テスト作成は test_writer に委譲してください。",
    tools=[{"type": "agent_toolset_20260401"}],
    callable_agents=[
        {"type": "agent", "id": reviewer.id, "version": reviewer.version},
        {"type": "agent", "id": test_writer.id, "version": test_writer.version},
    ],
)
```

現時点では **委譲は 1 階層のみ**（サブエージェントがさらに別のエージェントを呼ぶことはできない）という制約があります。

### メモリツール（research preview）

セッションをまたいで知識を永続化したい場合は、メモリツール (`memory_20250818`) を使います。`view` / `create` / `str_replace` / `insert` / `delete` / `rename` といったコマンドで、クライアント側のストレージに記憶ファイルを管理する設計です。

マルチエージェントとメモリツール（および成果物検証の `outcomes`）は research preview 扱いで、個別にアクセス申請が必要です。本番運用に組み込む前にドキュメントで最新の提供状況を確認してください。

## 料金の考え方

Managed Agents の課金には 2 つの軸があります。

1. **トークン料金** — 使用したモデルの標準レートがそのまま適用されます
2. **セッション実行時間** — セッションが `running` ステータスの間、$0.08 / 時間 が課金されます

ポイントは、セッションが `idle`（ユーザーの入力待ち）の間は実行時間課金が発生しないことです。長時間開きっぱなしにしてもコストが線形に膨らむわけではありません。

### 料金計算の例

Claude Opus 4.6 を 1 時間使って 5 万入力トークン / 1.5 万出力トークンを消費したセッションの例です。

| 項目 | 計算 | 料金 |
| --- | --- | --- |
| 入力トークン | 50,000 × $5 / 1M | $0.250 |
| 出力トークン | 15,000 × $25 / 1M | $0.375 |
| セッション実行時間 | 1.0 時間 × $0.08 | $0.080 |
| **合計** |  | **$0.705** |

Messages API で使える Batch API 割引・Fast mode 割増・Data residency 係数・Long context プレミアムは、Managed Agents には **適用されません**。Web 検索ツールなどの従量課金は別途発生します。

## 現時点での制限

| 項目 | 内容 |
| --- | --- |
| ステータス | Public beta（ヘッダー `managed-agents-2026-04-01` 必須） |
| 作成系レート制限 | 60 req/min（組織単位） |
| 読み取り系レート制限 | 600 req/min（組織単位） |
| サブエージェント委譲 | 1 階層まで |
| research preview 機能 | multiagent / memory / outcomes は個別にアクセス申請が必要 |

本番投入を検討する場合は、自組織のトラフィック想定に対してこのレート制限で足りるかを事前に確認しておくのが安全です。

## まとめ

* **Claude Managed Agents** は Anthropic がホストするエージェント基盤で、エージェントループ・サンドボックス・セッション永続化を API ネイティブで提供する
* `agent`（定義）・`environment`（実行コンテナ）・`session`（実行インスタンス）・`event`（やり取りの単位）の 4 リソースで構成される
* Python SDK では `client.beta.agents` / `client.beta.environments` / `client.beta.sessions.events.stream` を使うだけで、最小構成のエージェントがすぐに動く
* 組み込みツール `agent_toolset_20260401` に加え、カスタムツール・MCP サーバー・マルチエージェント・メモリツールで拡張できる
* 料金はトークン料金 + セッション実行時間 $0.08 / 時間。`idle` 時間は課金されないため、ユーザー入力待ちが多いワークロードとは相性が良い
* まだ public beta であり、レート制限と research preview 機能の制約を踏まえた設計が必要

「エージェントのハーネス部分」に割いていた開発リソースを Anthropic に移譲できるのが Managed Agents の最大の価値です。これまで Messages API の上に自前で組んでいたチームは、一度 Quickstart を動かしてみて、置き換え可能な領域を見極めてみる価値があります。

## 参考
