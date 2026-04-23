---
id: "2026-04-15-claude-managed-agents-完全解説-brainhands分離アーキテクチャと実装入-01"
title: "Claude Managed Agents 完全解説 — Brain/Hands分離アーキテクチャと実装入門"
url: "https://zenn.dev/zenchaine/articles/claude-managed-agents-production-ai-2026"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "zenn"]
date_published: "2026-04-15"
date_collected: "2026-04-16"
summary_by: "auto-rss"
query: ""
---

## Claude Managed Agents とは何ですか？

Claude Managed Agents は、Anthropic が 2026年4月8日にパブリックベータとしてリリースした **AI エージェントのフルマネージド実行基盤** です。サンドボックス実行、セッション管理、認証情報管理、ツール統合をすべて API として提供し、エージェント開発を大幅に高速化します。

従来、AI エージェントを本番環境で動かすにはコンテナ管理、状態永続化、認証管理など数ヶ月分のインフラ構築が必要でした。Managed Agents はこれをまるごと引き受けます。

## Brain/Hands 分離アーキテクチャはどう動くのか？

Managed Agents の最大の技術的特徴は、推論（Brain）と実行（Hands）の完全な分離です。

### 3 コンポーネント構成

| コンポーネント | 役割 | 特性 |
| --- | --- | --- |
| **Session** | 追記専用イベントログ | 永続状態。切断復帰可能 |
| **Harness** | エージェントループ | ステートレス。水平スケール |
| **Sandbox** | コード実行コンテナ | 使い捨て。オンデマンド |

ポイントは、推論がコンテナのプロビジョニングを待たずに開始できることです。Anthropic のエンジニアリングブログによれば、この設計で p50 TTFT が約 60% 短縮、p95 は 90% 以上短縮されています。

### ツール実行の抽象化

```
execute(name, input) -> string
```

このシンプルなインターフェースにより、Harness はツールの実装詳細を知らず、Sandbox は推論を知りません。疎結合がスケーラビリティを実現しています。

## 最速で試すには？ — TypeScript クイックスタート

### 前提

* Anthropic API キー
* Node.js 18+

### SDK インストール

```
npm install @anthropic-ai/sdk
```

### Agent → Session → Event の 3 ステップ

```
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

// 1. Agent 作成（再利用可能な設定バンドル）
const agent = await client.beta.agents.create({
  model: "claude-sonnet-4-6",
  name: "code-reviewer",
  system: "Review code for security and performance issues.",
  tools: [{ type: "agent_toolset_20260401" }],
});

// 2. Session 開始（Agent + Environment の実行インスタンス）
const session = await client.beta.sessions.create({
  agent_id: agent.id,
});

// 3. Event 送信 + SSE ストリーミング受信
const stream = await client.beta.sessions.events.create(session.id, {
  event: {
    type: "user.message",
    content: [{ type: "text", text: "Analyze the project structure." }],
  },
  stream: true,
});

for await (const event of stream) {
  if (event.type === "text_delta") {
    process.stdout.write(event.delta);
  }
}
// 注: SDK は "managed-agents-2026-04-01" ベータヘッダーを自動付与する
```

### CLI（ant）で対話的に確認

```
brew install anthropics/tap/ant
ant agent run --agent-id $AGENT_ID
```

## 料金はいくらかかるのか？

2 軸の課金です。

**トークンコスト（従来 API と同一）:**

| モデル | 入力 | 出力 |
| --- | --- | --- |
| Claude Sonnet 4.6 | $3/MTok | $15/MTok |
| Claude Opus 4.6 | $5/MTok | $25/MTok |

**セッションランタイム: $0.08/時間**

`running` ステータスの間のみ課金。アイドル時間は対象外です。

**実コスト例:** Claude Opus 4.6 で 1 時間、50K 入力 + 15K 出力 → **合計 $0.705**。BuildFastWithAI のレビューでは、4〜6 時間のセッションで $1.50〜$3.50 が典型的とされています。

## セキュリティモデルはどうなっている？

本番利用で気になるセキュリティ設計を整理します。

* **認証情報**: Sandbox 外の専用 Vault に保管。MCP ツール呼び出しは専用プロキシ経由
* **リポジトリアクセス**: トークンは Sandbox 初期化時にのみ注入。生成コードからアクセス不可
* **スコープ管理**: Agent 単位でアクセス可能なツール・データソースを明示的に定義
* **トレーシング**: Claude Console で全実行ログを可視化

## Managed Agents と Agent SDK の使い分け

Anthropic は Managed Agents と並行して **Claude Agent SDK**（Python / TypeScript ライブラリ）も提供しています。同じ Claude モデル・MCP を共有しますが、責任範囲が異なります。

* **Agent SDK**: Claude Code を支えるエージェントループ・ツール実行・コンテキスト管理を `import` して自社アプリに組み込める。デプロイ・スケーリング・監視は自前
* **Managed Agents**: ランタイム・サンドボックス・スケーリング・安全性を Anthropic がフル管理

| 観点 | Agent SDK | Managed Agents |
| --- | --- | --- |
| 運用責任 | 自前 | Anthropic |
| 柔軟性 | 高い | ミドル |
| 開発体験 | ローカルでタイトなループ | 長時間ジョブが得意 |
| 向くケース | 自社インフラに深く統合／開発中のイテレーション | 素早い本番投入／非同期ジョブ |

両者とも同じモデル・MCP なので、**SDK で試作 → Managed Agents で本番展開** といった移行も現実的です。「運用チーム体制」と「本番までの時間軸」で判断するのが分かりやすいでしょう。

## 競合との違いはどこにあるのか？

以下の比較は [Composio のブログ記事](https://composio.dev/content/claude-agents-sdk-vs-openai-agents-sdk-vs-google-adk) を参考にしています。

| 観点 | Claude Managed Agents | OpenAI Agents SDK | Google ADK |
| --- | --- | --- | --- |
| インフラ | Anthropic フル管理 | 自前管理 | Vertex AI Agent Engine |
| OS アクセス | Bash, ファイルシステム, Web | なし | なし |
| モデル | Claude のみ | 100+ LLM | Gemini 最適化 |
| SDK | 7 言語 | 2 言語 | 4 言語 |
| 差別化 | OS アクセス深度 + MCP | モデル自由度 + 音声 | A2A + ガバナンス |

**選定基準:** 安全性・監査性を重視し、開発者向けエージェントやファイル操作自動化が主用途なら Managed Agents。マルチモデルや音声対応が必要なら OpenAI SDK。GCP 統合やエンタープライズガバナンスが優先なら Google ADK、というのが現時点での判断軸です。

## エンタープライズ導入事例

ベータ公開と同時に発表された事例です。

* **Notion**: マルチエージェント連携で数十タスクを並列実行
* **Rakuten**: 各部門に専門エージェントを約 1 週間でデプロイ
* **Sentry**: デバッグ → PR 作成を一気通貫で自動化
* **Asana**: 「AI Teammates」としてプロジェクト内でタスクを引き受け

Anthropic の内部ベンチマークでは、構造化ファイル生成タスクの成功率が標準プロンプティングループ比で最大 10 ポイント向上しています。

## 注意すべき制約

Hacker News のディスカッションやレビュー記事から、現時点の主な懸念点を整理します。

* **ベンダーロックイン**: Claude Platform 専用。Bedrock / Vertex AI からは利用不可
* **マルチモデル非対応**: 異なる LLM を組み合わせたワークフローは構築できない
* **パブリックベータ**: 本番 SLA は未提供。可用性の実績は発展途上
* **レート制限**: 作成系 60 req/min、読み取り系 600 req/min

## 参考ソース

---

この記事で紹介した内容の詳細な解説は、ZenChAIne の記事で公開しています。
