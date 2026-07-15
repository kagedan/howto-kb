---
id: "2026-07-15-openai-agents-sdk入門-サンドボックスとハーネスで長期タスクをpythonで実装する-01"
title: "OpenAI Agents SDK入門 — サンドボックスとハーネスで長期タスクをPythonで実装する"
url: "https://zenn.dev/kai_kou/articles/246-openai-agents-sdk-sandbox-harness-guide"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "OpenAI", "GPT", "Python", "TypeScript"]
date_published: "2026-07-15"
date_collected: "2026-07-16"
summary_by: "auto-rss"
query: ""
---

## はじめに

OpenAIは2026年4月15日、Agents SDKに重要なアップデートを発表しました。今回のアップデートの柱は2つです。**ハーネス（制御プレーン）とサンドボックス（実行プレーン）の明確な分離**、そして **ネイティブなサンドボックス実行のサポート** です。

これにより、ファイル操作・コマンド実行・長期タスク管理を伴う本格的なAIエージェントを、最小限の独自インフラで構築できるようになりました。

### この記事で学べること

* ハーネスとサンドボックスの役割分担と設計思想
* `SandboxAgent` の基本的な使い方（Pythonコード付き）
* `Manifest` によるワークスペースの宣言的定義
* `Capabilities`（Shell, Filesystem, Memory など）の活用
* 対応サンドボックスプロバイダー一覧と選択指針
* RunState・session\_state・snapshot による状態管理

### 対象読者

* OpenAI Agents SDK を使ってエージェントを構築しているエンジニア
* ファイル操作や長期タスクに対応したAIエージェントを設計したい方
* エージェントの安全な実行環境（サンドボックス）に関心がある方

### 前提環境

* Python 3.10 以上（公式ドキュメントで要確認）
* `openai-agents` パッケージ（最新版）
* OpenAI API キー

## TL;DR

* Agents SDK にネイティブのサンドボックス実行機能が追加（Python 先行、TypeScript は近日対応）
* **ハーネス**（制御プレーン）がエージェントループ・ツールルーティング・状態管理を担当
* **サンドボックス**（実行プレーン）がファイル操作・コマンド実行・パッケージインストールを担当
* `SandboxAgent`・`Manifest`・`Capabilities` の3要素でエージェント環境を宣言的に定義
* E2B・Modal・Cloudflare など7つのホスト型プロバイダーをプラグイン方式で切り替え可能

## 背景：なぜ「ハーネス＋サンドボックス」なのか

従来のAIエージェントは、ファイル操作・コード実行・長期タスクを実装しようとすると、開発者が独自の実行環境をゼロから組み立てる必要がありました。これにより、以下の問題が生じていました。

* **安全性**: コードが任意のホスト環境を変更できてしまう
* **再現性**: 環境のセットアップが複雑で、プロバイダー間での移植性がない
* **状態管理**: タスクの中断・再開・スナップショットを独自実装する必要がある

今回のアップデートはこれらを解決するために、制御と実行を明確に分離したアーキテクチャを導入しています。

### ハーネスとサンドボックスの役割

| 層 | 役割 | 主な責務 |
| --- | --- | --- |
| **ハーネス（制御プレーン）** | エージェントの「指揮官」 | エージェントループ、モデル呼び出し、ツールルーティング、ハンドオフ、承認、トレーシング、RunState管理 |
| **サンドボックス（実行プレーン）** | エージェントの「作業場」 | ファイルシステム、シェル、依存パッケージ、マウントストレージ、ポート公開、スナップショット |

公式ドキュメントによると、この分離には重要な意図があります。ハーネスは信頼できるインフラ上で動作し、サンドボックスは限定された資格情報とスコープされたマウントで実行されます。これにより、機密性の高い制御操作はハーネス側に保持しつつ、プロバイダー固有の実行はサンドボックスに任せる設計が実現します。

## SandboxAgent の基本実装

### インストールと準備

```
pip install openai-agents --upgrade
```

### 最小構成のサンドボックスエージェント

以下は公式ドキュメントで紹介されている基本的な実装パターンです。

```
from agents import Runner
from agents.run import RunConfig
from agents.sandbox import Manifest, SandboxAgent, SandboxRunConfig
from agents.sandbox.capabilities import Shell
from agents.sandbox.entries import File
from agents.sandbox.sandboxes.unix_local import UnixLocalSandboxClient

# ワークスペースの初期状態を定義
manifest = Manifest(
    entries={
        "account_brief.md": File(content=b"# Account Brief\n\n- Client: Acme Corp\n- ARR: $120K"),
    }
)

# サンドボックス対応エージェントを定義
agent = SandboxAgent(
    name="Renewal Packet Analyst",
    model="gpt-5.4",
    instructions="Review the workspace before answering.",
    default_manifest=manifest,
    capabilities=[Shell()],
)

# ローカルサンドボックスで実行
result = await Runner.run(
    agent,
    "Summarize the renewal blockers.",
    run_config=RunConfig(
        sandbox=SandboxRunConfig(client=UnixLocalSandboxClient()),
        workflow_name="Unix-local sandbox review",
    ),
)
print(result.final_output)
```

`SandboxAgent` は通常の `Agent` と同じく `instructions`・`tools`・`handoffs`・`model` の設定を保持しつつ、サンドボックス固有の実行境界を追加します。ローカル開発時は `UnixLocalSandboxClient`、本番環境ではホスト型プロバイダーのクライアントに差し替えるだけで動作します。

## Manifest によるワークスペース定義

`Manifest` はサンドボックス内の初期ワークスペースを宣言的に定義するオブジェクトです。対応するエントリータイプは以下のとおりです。

| エントリータイプ | 説明 |
| --- | --- |
| `File` | バイト列として渡す小さなファイル |
| `Dir` | ディレクトリ構造 |
| `LocalFile` | ホストのファイルをサンドボックスにマウント |
| `LocalDir` | ホストのディレクトリをサンドボックスにマウント |
| `GitRepo` | GitリポジトリをWorkspaceにフェッチ |
| `S3Mount` / `GCSMount` / `R2Mount` / `AzureBlobMount` | クラウドストレージのマウント |

```
from agents.sandbox.entries import File, LocalDir, GitRepo

manifest = Manifest(
    entries={
        # インラインファイル
        "config.yaml": File(content=b"model: gpt-5.4\nmax_steps: 50"),
        # ホストのディレクトリをマウント
        "src": LocalDir(src="/home/user/myproject/src"),
        # Gitリポジトリ
        "data": GitRepo(url="https://github.com/org/dataset.git", ref="main"),
    },
    env={"OPENAI_API_KEY": "$OPENAI_API_KEY"},
)
```

注意事項として、Manifestのパスはワークスペース相対であり、`..` によるバウンダリ脱出は許可されていません。

## Capabilities（エージェント機能）

`Capabilities` はサンドボックス内でエージェントが使用できる機能のセットです。デフォルトでは `Filesystem()`・`Shell()`・`Compaction()` の3つが有効になっています。

| Capability | 用途 |
| --- | --- |
| `Shell` | コマンド実行・インタラクティブ入力 |
| `Filesystem` | `apply_patch` によるファイル編集・`view_image` による画像参照 |
| `Skills` | スキルの発見とマテリアライズ（AGENTS.mdベース） |
| `Memory` | クロスラン学習の永続化 |
| `Compaction` | 長期ワークフローでのコンテキスト削減 |

### Memory Capability の活用

`Memory()` を有効にすると、エージェントは実行をまたいで学習内容を保持できます。`MEMORY.md`・`memory_summary.md` などのファイルが自動生成され、ユーザーの好みやプロジェクト固有の知識が蓄積されます。

```
from agents.sandbox.capabilities import Filesystem, Memory, Shell

agent = SandboxAgent(
    name="Project Reviewer",
    model="gpt-5.4",
    instructions="Review code changes and apply lessons from previous reviews.",
    capabilities=[Memory(), Filesystem(), Shell()],
)
```

## サンドボックスプロバイダー

開発環境と本番環境でプロバイダーを切り替えるだけで、エージェント定義を変更せずに実行環境を変更できます。

| プロバイダー | 種別 | 特徴 |
| --- | --- | --- |
| `UnixLocalSandboxClient` | ローカル | macOS/Linux 開発用 |
| `DockerSandboxClient` | ローカルコンテナ | ローカルでの隔離実行 |
| **Blaxel** | ホスト型 | — |
| **Cloudflare** | ホスト型 | エッジ実行対応 |
| **Daytona** | ホスト型 | 開発環境特化 |
| **E2B** | ホスト型 | データサイエンス・コード実行に強い |
| **Modal** | ホスト型 | GPUワークロード対応 |
| **Runloop** | ホスト型 | エンタープライズ向け |
| **Vercel** | ホスト型 | フロントエンドプレビュー連携 |

プロバイダーの差し替えは `SandboxRunConfig.client` のみ変更すれば完了します。

```
# 開発環境（ローカル）
from agents.sandbox.sandboxes.unix_local import UnixLocalSandboxClient
client = UnixLocalSandboxClient()

# 本番環境（E2B）※ pip install openai-agents[e2b] が必要
from agents.extensions.sandbox import E2BSandboxClient
client = E2BSandboxClient(api_key="your_e2b_api_key")

# RunConfigで指定するだけ
run_config = RunConfig(sandbox=SandboxRunConfig(client=client))
```

## 状態管理：RunState・session\_state・snapshot

長期タスクを中断・再開するために、Agents SDKは3つの状態概念を提供します。

```
RunState（ハーネス側）
  └─ エージェントループ全体のワークフロー継続に使用

session_state（サンドボックス側）
  └─ プロバイダーへの再接続時のシリアライズされたセッション

snapshot（サンドボックス側）
  └─ ワークスペースの内容を保存し、新しいセッションのシードとして使用
```

ランナーはセッションを以下の優先順位で解決します。

1. 明示的なセッション指定
2. 再開された RunState
3. 明示的な session\_state
4. Manifest からの新規作成

```
# 状態を保存して後で再開する例
result = await Runner.run(agent, "Start the analysis task.", run_config=run_config)

# RunState に状態が保存されている
saved_state = result.run_state

# 後で再開
resumed_result = await Runner.run(
    agent,
    "Continue with step 2.",
    run_config=RunConfig(sandbox=SandboxRunConfig(client=client, run_state=saved_state)),
)
```

## サンドボックスを使うべきケース

公式ドキュメントが推奨するサンドボックスの適用場面をまとめます。

**サンドボックスを使うべき場合:**

* エージェントの回答が単なる推論でなく、ワークスペースの実作業に依存する
* 大量のドキュメントディレクトリが必要
* 後から参照するためのファイル生成が必要
* コマンド・パッケージ・スクリプトの実行が必要
* アーティファクト生成（Markdown、CSV、スクリーンショット等）
* ポート公開サービスやプレビューが必要
* 人間によるレビュー中断を挟んだ、再開可能なステートフルな作業

**サンドボックス不要の場合:**

* 簡潔なモデルレスポンスのみ必要なタスク
* 永続的なワークスペースを必要としない推論タスク

## まとめ

OpenAI Agents SDKの今回のアップデートで、長期タスク対応エージェントの実装パターンが大きく変わりました。

* **ハーネスとサンドボックスの分離** により、制御ロジックと実行環境が明確に分かれ、安全かつポータブルな構成が可能になった
* `SandboxAgent`・`Manifest`・`Capabilities` の3要素でワークスペースを宣言的に定義できる
* ローカル開発からE2B・Modal等のホスト型プロバイダーへの移行が `client` の差し替えのみで完了する
* `Memory()` Capability により、エージェントが実行をまたいで学習・成長できる

現在はPython SDKのみでの提供ですが、TypeScriptサポートも近日公開予定とされています。ファイル操作・コード実行・長期タスクを伴うエージェントを構築する場合、このアーキテクチャパターンを参考に設計を見直す価値があります。

## 参考リンク
