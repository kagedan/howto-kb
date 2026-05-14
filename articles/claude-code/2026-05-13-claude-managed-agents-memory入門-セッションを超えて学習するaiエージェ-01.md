---
id: "2026-05-13-claude-managed-agents-memory入門-セッションを超えて学習するaiエージェ-01"
title: "Claude Managed Agents Memory入門 — セッションを超えて学習するAIエージェントをPythonで実装する"
url: "https://qiita.com/kai_kou/items/fd21348d945527d7631c"
source: "qiita"
category: "claude-code"
tags: ["MCP", "API", "AI-agent", "Python", "qiita"]
date_published: "2026-05-13"
date_collected: "2026-05-14"
summary_by: "auto-rss"
query: ""
---

![Claude Managed Agents Memory のアーキテクチャ全体像](https://raw.githubusercontent.com/kai-kou/zenn-blog-automation/main/images/claude-managed-agents-memory-python-guide/01-hero.png)

## はじめに

AIエージェントの課題のひとつが「記憶の揮発性」です。会話を終えると状態がリセットされ、次のセッションでは白紙からスタートになる。ユーザーの好みやプロジェクトの文脈を毎回教え直す必要があります。

Anthropicは2026年4月8日に **Claude Managed Agents**（公開ベータ）を、そして4月23日に **Memory Stores（永続メモリ）** 機能を公開ベータとして追加しました。これにより、エージェントはセッションを超えて情報を保持し、利用を重ねるほど賢くなる仕組みを実装できます。

この記事では、公式ドキュメントをもとに Claude Managed Agents の基本構成から Memory Stores を使った永続化まで、Pythonコードで解説します。

### この記事で学べること

- Claude Managed Agents の4コア概念（Agent / Environment / Session / Events）
- エージェントの作成・環境構成・セッション開始の手順
- Memory Stores によるセッション横断的な記憶の実装
- メモリの CRUD 操作とバージョン管理
- セキュリティ上の注意点（read_only vs read_write）

### 対象読者

- Python でAIエージェントを開発したい方
- セッション間で状態を保持するエージェントを構築したい方
- Claude API の利用経験があり、マネージドエージェントへの移行を検討している方

### 前提環境

- Python 3.10 以上（`match` 文を使用するため）
- Anthropic API キー（[取得ページ](https://platform.claude.com/settings/keys)）
- `pip install anthropic`（最新版）

---

## TL;DR

- Claude Managed Agents はエージェントの実行基盤をフルマネージドで提供するAPIスイート（2026-04-08 公開β）
- **Memory Stores** を使うとエージェントがセッション間で情報を保持できる（2026-04-23 公開β）
- メモリは `/mnt/memory/` にマウントされ、エージェントが通常のファイル操作で読み書きする
- すべての変更は不変バージョンとして記録され、監査・ロールバックが可能
- ベータヘッダー `managed-agents-2026-04-01` が必要（SDKは自動付与）

---

## Claude Managed Agentsとは

Claude Managed Agents は、Anthropicが提供するAIエージェント実行のための完全マネージドインフラです。従来の Messages API と異なり、エージェントループ・ツール実行・サンドボックス環境の構築が不要になります。

| | Messages API | Claude Managed Agents |
|---|---|---|
| **用途** | カスタムエージェントループ・細粒度制御 | 長時間タスク・非同期処理 |
| **インフラ** | 自前で構築 | Anthropicがフルマネージド |
| **ツール実行** | 自前実装 | Bash・ファイル操作・Web検索などビルトイン |
| **セッション永続** | なし | あり（切断に強い） |

### 4つのコア概念

![Agent・Environment・Session・Memory Storeの4要素の関係図](https://raw.githubusercontent.com/kai-kou/zenn-blog-automation/main/images/claude-managed-agents-memory-python-guide/02-concept-diagram.png)

| 概念 | 説明 |
|------|------|
| **Agent** | モデル・システムプロンプト・ツール・MCPサーバー・スキルの定義 |
| **Environment** | コンテナテンプレート（パッケージ・ネットワークアクセス） |
| **Session** | エージェントと環境の組み合わせで実行される単一タスク |
| **Events** | アプリケーションとエージェント間のメッセージ（ユーザーターン・ツール結果・ステータス更新） |

### 利用可能なビルトインツール

```
Bash           シェルコマンド実行
File operations  読み取り・書き込み・編集・glob・grep
Web search/fetch  Web検索・URLコンテンツ取得
MCP servers    外部ツールプロバイダーへの接続
```

---

## セットアップ

```bash
pip install anthropic
export ANTHROPIC_API_KEY="your-api-key-here"
```


> Claude Managed Agents のすべてのAPIリクエストには `managed-agents-2026-04-01` ベータヘッダーが必要です。Python SDKは自動的に付与するため、明示的な指定は不要です。


---

## エージェントを作成する

エージェントはモデル・システムプロンプト・ツールを定義する再利用可能な設定です。一度作成してIDで参照します。

```python
from anthropic import Anthropic

client = Anthropic()

agent = client.beta.agents.create(
    name="Coding Assistant",
    model="claude-opus-4-7",
    system="You are a helpful coding assistant. Write clean, well-documented code.",
    tools=[
        {"type": "agent_toolset_20260401"},  # ビルトインツール全種を有効化
    ],
)

print(f"Agent ID: {agent.id}, version: {agent.version}")
```

`agent_toolset_20260401` を指定すると Bash・ファイル操作・Web検索などすべてのビルトインツールが使えます。返された `agent.id` は以降のセッション作成で参照します。

---

## 環境を作成する

環境はエージェントが動作するコンテナの設定です。ネットワークアクセスやプリインストールパッケージを制御できます。

```python
environment = client.beta.environments.create(
    name="coding-env",
    config={
        "type": "cloud",
        "networking": {"type": "unrestricted"},  # 外部ネットワークアクセスを許可
    },
)

print(f"Environment ID: {environment.id}")
```

`networking.type` は `unrestricted`（無制限）または特定ドメインに制限できます。

---

## セッションを開始してメッセージを送る

```python
# セッションを作成
session = client.beta.sessions.create(
    agent=agent.id,
    environment_id=environment.id,
    title="Fibonacci generator task",
)

# ストリームを開き、メッセージを送信してレスポンスを受け取る
with client.beta.sessions.events.stream(session.id) as stream:
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

エージェントは Python スクリプトを書き、コンテナ内で実行し、出力ファイルを確認するまでを自律的に行います。

---

## Memory Stores — 永続メモリの実装

![Memory Storeのライフサイクル図](https://raw.githubusercontent.com/kai-kou/zenn-blog-automation/main/images/claude-managed-agents-memory-python-guide/03-memory-flow.png)

Memory Storeは「セッションスコープを超えて情報を保持するテキストドキュメントの集合」です。セッションのコンテナ内に `/mnt/memory/` ディレクトリとしてマウントされ、エージェントが通常のファイルツールで読み書きします。

### メモリストアを作成する

```python
store = client.beta.memory_stores.create(
    name="User Preferences",
    description="Per-user preferences and project context.",
)

print(f"Memory Store ID: {store.id}")  # memstore_01Hx...
```

`description` はエージェントに渡され、ストアの内容をエージェントが理解するために使われます。

### 初期コンテンツを投入する（オプション）

エージェントが参照するリファレンス情報をあらかじめ投入できます。

```python
client.beta.memory_stores.memories.create(
    store.id,
    path="/standards/formatting.md",
    content="All reports use GAAP formatting. Dates are ISO-8601 format.",
)
```


> 個別のメモリは 100KB（約 25K トークン）が上限です。大きな1ファイルより、用途ごとに細分化した小さなファイル群の設計が推奨されています。


### セッションにメモリストアをアタッチする

```python
session = client.beta.sessions.create(
    agent=agent.id,
    environment_id=environment.id,
    resources=[
        {
            "type": "memory_store",
            "memory_store_id": store.id,
            "access": "read_write",          # read_only も指定可能
            "instructions": "Check this store before starting any task for user preferences.",
        }
    ],
)
```

1セッションに最大 **8つ** のメモリストアをアタッチできます。`access` は `read_write`（デフォルト）または `read_only` を指定します。


> **セキュリティ上の注意:** `read_write` でアタッチしたストアに対し、エージェントが信頼できないユーザー入力や外部Webコンテンツを処理している場合、プロンプトインジェクションによってストアに悪意あるコンテンツが書き込まれる可能性があります。参照データや共有ルックアップには `read_only` の使用を推奨します。


### メモリの管理（CRUD）

```python
# 一覧取得（ディレクトリ構造を確認）
page = client.beta.memory_stores.memories.list(
    store.id,
    path_prefix="/",
    order_by="path",
    depth=2,
)
for item in page.data:
    print(item.type, item.path)

# 内容取得
retrieved = client.beta.memory_stores.memories.retrieve(
    mem.id,
    memory_store_id=store.id,
)
print(retrieved.content)

# 更新（楽観的同時実行制御）
client.beta.memory_stores.memories.update(
    memory_id=mem.id,
    memory_store_id=store.id,
    content="Updated preference: always use 2-space indentation.",
    precondition={
        "type": "content_sha256",
        "content_sha256": mem.content_sha256,  # 競合を防ぐハッシュチェック
    },
)

# 削除
client.beta.memory_stores.memories.delete(
    mem.id,
    memory_store_id=store.id,
)
```

更新時に `precondition` を渡すと楽観的同時実行制御が機能します。ハッシュが一致しない場合はエラーとなるため、最新状態を再取得してリトライします。

---

## バージョン管理と監査

メモリへのすべての変更は **不変のメモリバージョン**（`memver_...`）として記録されます。コンプライアンス要件や誤書き込みのロールバックに対応できます。

```python
# バージョン履歴を一覧取得
versions = client.beta.memory_stores.memory_versions.list(
    store.id,
    memory_id=mem.id,
)
for v in versions:
    print(f"{v.id}: {v.operation}")

# 特定バージョンの内容を確認
version = client.beta.memory_stores.memory_versions.retrieve(
    version_id,
    memory_store_id=store.id,
)
print(version.content)

# 機密情報のリダクト（監査証跡は保持）
client.beta.memory_stores.memory_versions.redact(
    version_id,
    memory_store_id=store.id,
)
```

バージョンは **30日間保持**されます（最新バージョンは期間に関わらず保持）。30日を超えて保存したい場合はAPIでエクスポートします。


> `redact` は内容を消去しますが、「誰がいつ変更したか」の監査証跡は残ります。PII削除やシークレット漏洩対応など、コンプライアンス要件のあるワークフローで活用できます。


---

## 料金

Claude Managed Agents の課金は以下の2軸です。

| 項目 | 料金 |
|------|------|
| トークン消費 | 標準 Claude API のトークン料金と同一 |
| セッションランタイム | **$0.08 / session-hour**（running 状態の時間） |
| Web検索（セッション内） | $10 / 1,000 回 |

月額固定費やエージェントライセンス費用はなく、純粋な消費課金です。セッションが `idle` 状態（何も実行していない）の時間はランタイム課金されません。

---

## ユースケース

Memory Stores が特に効果的なシナリオを示します。

| ユースケース | メモリの内容例 | アクセス |
|------------|-------------|---------|
| ユーザー別カスタマイズ | 好みの言語スタイル・出力フォーマット | read_write |
| プロジェクトコンテキスト | コーディング規約・命名規則・アーキテクチャ設計 | read_write |
| 共有リファレンス | APIドキュメント・業界標準・FAQ | read_only |
| エラーパターン学習 | 過去の失敗事例と解決策 | read_write |

[公式ブログ](https://claude.com/blog/claude-managed-agents-memory)によると、Rakutenではエージェントがセッションをまたいで学習することで初回エラー率が97%削減・レイテンシが34%改善、WisedocsではMemory Storesを活用した文書検証パイプラインで処理速度が30%向上したとされています。

---

## まとめ

- Claude Managed Agents（公開β: 2026-04-08）はエージェント実行インフラをフルマネージドで提供するAPIスイートです
- Memory Stores（公開β: 2026-04-23）により、セッションを超えた永続的な記憶が実装できます
- メモリは `/mnt/memory/` にマウントされ、エージェントが通常のファイルツールで読み書きします
- すべての変更はバージョンとして記録され、監査・ロールバック・リダクトが可能です
- 信頼できない入力を処理するストアには `read_only` アクセスを設定し、プロンプトインジェクションを防ぎましょう

## 参考リンク

- [Claude Managed Agents overview](https://platform.claude.com/docs/en/managed-agents/overview) — 公式ドキュメント（全体像）
- [Get started with Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/quickstart) — クイックスタートガイド
- [Using agent memory](https://platform.claude.com/docs/en/managed-agents/memory) — Memory Stores 詳細ドキュメント
- [Claude Managed Agents announcement](https://claude.com/blog/claude-managed-agents) — 公式アナウンスブログ
- [Claude Managed Agents Memory announcement](https://claude.com/blog/claude-managed-agents-memory) — Memory機能 公式アナウンスブログ
