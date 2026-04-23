---
id: "2026-04-10-claude-managed-agentsのアーキテクチャと既存エージェント実行環境との技術比較-01"
title: "Claude Managed Agentsのアーキテクチャと既存エージェント実行環境との技術比較"
url: "https://qiita.com/tatematsu-k/items/dce3ce5252e24c4585bd"
source: "qiita"
category: "ai-workflow"
tags: ["API", "AI-agent", "qiita"]
date_published: "2026-04-10"
date_collected: "2026-04-10"
summary_by: "auto-rss"
query: ""
---

## TL;DR

* Claude Managed Agentsは2026年4月8日にパブリックベータとして公開された、エージェント実行基盤のマネージドサービス
* 既存のフレームワーク（LangGraph、CrewAI、Dify等）とは異なり、**モデル＋ハーネス（制御ループ）＋サンドボックス＋セッション永続化がAPI一つで提供される垂直統合アーキテクチャ**
* 内部アーキテクチャはSession / Harness / Sandboxの3コンポーネントに分離されており、エンジニアリングブログで設計が公開されている
* 課金モデルはアクティブ実行時間のみの従量課金（$0.08/時間、アイドル無料）

## はじめに

この記事では、AIエージェントの実行環境を5つのカテゴリに分類し、それぞれのアーキテクチャ・組み込み機能・課金モデルを技術的な観点で比較する。

対象読者はAIエージェントの本番運用を検討しているエンジニア。各実行環境の公式ドキュメントおよびエンジニアリングブログに基づく事実ベースの比較とする。

## エージェント実行環境の分類

AIエージェントの実行には、LLM（モデル）の他に以下のインフラが必要となる。

* **エージェントループ**: モデル呼び出し → ツールコール解析 → 実行 → 結果フィードバックの制御ループ
* **サンドボックス**: コード実行の隔離（ファイルシステム、ネットワーク、プロセス）
* **永続化**: セッション状態の保存、チェックポイント
* **クレデンシャル管理**: 秘密情報の安全な注入と分離
* **エラー回復**: 障害時の自動リトライ

2026年4月時点で、これらを提供する実行環境は大きく5つに分類できる。

| カテゴリ | 代表例 | エージェントループ | サンドボックス | 永続化 | モデル |
| --- | --- | --- | --- | --- | --- |
| (A) 自前構築 | Python + 自作ループ | 自前実装 | 自前実装 | 自前実装 | 任意 |
| (B) コード型FW | LangGraph / CrewAI | FW提供 | 自前実装 | 一部FW提供 | 任意 |
| (C) ローコード型FW | Dify / Langflow | GUI提供 | 一部提供 | WF単位 | 任意 |
| (D) クラウドホスティング | LangGraph Cloud | FW提供 | プラットフォーム提供 | 提供 | 任意 |
| (E) マネージド基盤 | Managed Agents | 組み込み | 組み込み | 組み込み | Claude固定 |

## 各実行環境の技術的特徴

### (A) 自前構築

```
# 最小限のエージェントループの例
while True:
    response = client.messages.create(model="claude-sonnet-4-20250514", ...)
    if response.stop_reason == "tool_use":
        result = execute_tool(response.content)
        # 結果をフィードバックして再度呼び出し
    else:
        break
```

エージェントループ、ツール実行、エラー回復をすべて自前で実装する。自由度は最大だが、本番に必要なサンドボックス、チェックポイント、クレデンシャル分離もすべて自前で設計・実装する必要がある。

### (B) LangGraph / CrewAI

**LangGraph** はグラフ構造でエージェントの状態遷移を定義する。ノード（タスク）とエッジ（遷移条件）を明示的に記述するため、複雑なワークフローの可視性が高い。GitHub星数は90,000+（CrewAI: 45,900+）。最近リリースされたDeep Agents（[langchain-ai/deepagents](https://github.com/langchain-ai/deepagents)）では、プランニング、ファイルシステムバックエンド、サブエージェント生成といったハーネス機能も提供されている。

**CrewAI** は各エージェントにrole/goal/backstoryを設定し、フレームワークが協調パターンを推論する。コミュニティベンチマークではプロトタイプの構築速度がLangGraphより約40%速いとされる。

いずれもインフラ層（コンテナ隔離、永続化、セキュリティ）は自前で用意する必要がある。

### (C) Dify / Langflow

GUIでエージェントフローを構築するローコードアプローチ。

Difyは**DifySandbox**（Linux Seccompベース）でコード実行の隔離を提供している。syscallホワイトリスト + chroot + ネットワークプロキシによる多層隔離を実装しており、Python/Node.jsをサポート。ただしこれはワークフローの「コードノード」としての実行環境であり、エージェントの制御ループ自体とは別物。

### (D) LangGraph Cloud

LangGraphフレームワーク＋ホスティングインフラのセット。LangSmithによるオブザーバビリティ（トレース、メトリクス）が統合されている。チェックポイント、ストリーミングも提供。

モデル非依存設計のため、GPT / Claude / Gemini / ローカルLLMのマルチモデル構成が可能。

### (E) Claude Managed Agents

#### API

```
# エージェント作成
curl -X POST https://api.anthropic.com/v1/agents \
  -H "anthropic-beta: managed-agents-2026-04-01" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -d '{"model": "claude-sonnet-4-20250514", "tools": [{"type": "agent_toolset_20260401"}]}'

# セッション開始
curl -X POST https://api.anthropic.com/v1/sessions \
  -H "anthropic-beta: managed-agents-2026-04-01" \
  -d '{"agent_id": "agent_xxx", "messages": [{"role": "user", "content": "..."}]}'
```

ベータヘッダー `managed-agents-2026-04-01` が必要。`agent_toolset_20260401` を指定すると、以下の組み込みツールが有効になる。

#### 組み込みツール

| ツール | 機能 |
| --- | --- |
| bash | シェルコマンド実行（サンドボックス内） |
| Read / Write / Edit | ファイル操作 |
| Grep / Glob | ファイル検索 |
| Web Search / Fetch | Web検索・ブラウジング |
| MCP Server | 外部ツール接続（Model Context Protocol） |

## アーキテクチャの比較

### Managed Agentsの内部構造

Anthropicのエンジニアリングブログ「[Scaling Managed Agents: Decoupling the brain from the hands](https://www.anthropic.com/engineering/managed-agents)」で公開されたアーキテクチャは、以下の3コンポーネントに分離されている。

| コンポーネント | 役割 | 特徴 |
| --- | --- | --- |
| **Session** | 追記専用イベントログ | ハーネスの外に永続化。切断耐性あり |
| **Harness** | ステートレスな制御ループ | Claudeの呼び出し、ツールコールのルーティング |
| **Sandbox** | 隔離された実行環境 | コード実行、ファイル操作。長期クレデンシャルへのアクセスなし |

このアーキテクチャの特徴は以下の通り。

**セッションの永続化**: Sessionがハーネスの外に永続化されるため、コンテナが落ちてもセッション状態が保持される。ハーネスはステートレスなので、別のコンテナで再起動してSessionを引き継げる。

**クレデンシャル分離**: OAuthトークンはセキュアなVaultに保管され、MCPツール呼び出し時に専用プロキシ経由で注入される。サンドボックスに秘密情報が到達しない設計。

**遅延コンテナプロビジョニング**: 推論を即座に開始し、コンテナはバックグラウンドで起動する。エンジニアリングブログによると、この設計によりp50 TTFTが約60%、p95が90%以上改善。

**エフェメラルコンテナ**: `execute(name, input) → string` というインターフェースでツールコールを抽象化し、コンテナを"cattle, not pets"として扱う。コンテナ障害はツールコールエラーとしてハーネスに返され、Claudeが自動リトライする。

### Claude Code（ローカル）との関係

| 項目 | Claude Code | Managed Agents |
| --- | --- | --- |
| 実行環境 | ローカルマシン | Anthropicクラウド |
| 用途 | 開発時（対話的） | 本番（API駆動、24/7） |
| トリガー | 人間の対話 | API / イベント |
| セッション永続化 | なし（ローカルのみ） | あり（切断耐性） |
| サンドボックス | OS依存（macOS Seatbelt / Linux bubblewrap） | マネージドコンテナ |

公式ドキュメントでは「Claude Code subagents are development-time agents, Managed Agents are production-time agents」と区分されている。Managed AgentsはClaude Codeのハーネスをそのまま移植したものではなく、同じ設計思想を本番向けに再設計した基盤である。

## 課金モデルの比較

| 実行環境 | 基盤コスト | LLM料金 | 課金モデル |
| --- | --- | --- | --- |
| (A) 自前構築（VPS） | $121〜240/月（24/7） | 任意プロバイダ従量 | 固定費 |
| (B) LangGraph（セルフホスト） | (A)と同等 | 任意プロバイダ従量 | 固定費 |
| (C) Dify Cloud Pro | $59/workspace/月 | 任意プロバイダ従量 | 固定費＋従量 |
| (D) LangGraph Cloud + LangSmith | $39/seat/月 + $0.001/ノード実行 | 任意プロバイダ従量 | 固定費＋従量 |
| (E) Managed Agents | $0.08/アクティブ時間 | Claudeトークン従量 | **完全従量** |

Managed Agentsの課金モデルの特徴:

* **アイドル時間は無料**: メッセージ待ち、ツール確認待ち、キュー待ちの間は課金されない
* **コンテナはエフェメラル**: 必要なときに起動、アイドル時にシャットダウン
* **無料枠**: 組織あたり1日50時間分のセッションが無料
* **Web検索**: $10 / 1,000検索（別途）

24/7稼働の場合は月$58程度（730時間 × $0.08）。イベント駆動的な利用パターンではコストが大幅に下がる。

## 制約と注意点

### ベンダーロックイン

Anthropicのインフラ、ツール体系、セッション形式に依存する。エージェントのロジックをポータブルに保ちたい場合はLangGraphなどモデル非依存のフレームワークが適している。

### モデル固定

Claude専用。マルチモデル構成（GPT + Claude混在、タスクごとのモデル使い分け）は不可。

### データの経路

すべてのツールコールと判断がAnthropicのインフラを経由する。データの外部送信が制限される環境では採用が困難。

### ベータステータス

2026年4月時点でパブリックベータ。以下の機能はresearch previewで別途アクセス申請が必要:

* マルチエージェント協調（multi-agent coordination）
* 自己評価（outcomes）
* メモリ（memory）

## 比較まとめ

| 観点 | 自前構築 | LangGraph/CrewAI | Dify/Langflow | LangGraph Cloud | Managed Agents |
| --- | --- | --- | --- | --- | --- |
| 初期構築コスト | 高 | 中 | 低 | 中 | 低 |
| 運用負荷 | 高 | 中〜高 | 中 | 低〜中 | 低 |
| モデルの自由度 | 任意 | 任意 | 任意 | 任意 | Claude固定 |
| カスタマイズ性 | 最大 | 高 | GUI範囲 | 高 | ツール定義+MCP |
| サンドボックス | 自前 | 自前 | 一部提供 | 提供 | 組み込み |
| セッション永続化 | 自前 | チェックポイント | WF単位 | 提供 | 組み込み |
| クレデンシャル分離 | 自前 | 自前 | 自前 | 自前 | 組み込み |
| 課金モデル | 固定費 | 固定費 | 固定+従量 | 固定+従量 | 完全従量 |

## 参考リンク
