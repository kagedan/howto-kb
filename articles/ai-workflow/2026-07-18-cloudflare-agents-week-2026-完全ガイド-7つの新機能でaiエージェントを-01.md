---
id: "2026-07-18-cloudflare-agents-week-2026-完全ガイド-7つの新機能でaiエージェントを-01"
title: "Cloudflare Agents Week 2026 完全ガイド — 7つの新機能でAIエージェントを本番運用する"
url: "https://zenn.dev/kai_kou/articles/248-cloudflare-agents-week-2026-infra-guide"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "API", "AI-agent", "LLM", "OpenAI", "Python"]
date_published: "2026-07-18"
date_collected: "2026-07-19"
summary_by: "auto-rss"
query: ""
---

## はじめに

2026年4月13〜17日、Cloudflareは **Agents Week 2026** を開催し、AIエージェントの本番運用を支えるインフラを一気に公開しました。

単なる機能追加ではなく、「AIエージェントがコンテナの100倍速でコードを実行し、Gitで成果物を管理し、ブラウザを操作し、記憶を持つ」環境を丸ごと揃えた週でした。

この記事では、発表された7つの主要機能を技術的な観点で整理し、実際にどう使うかを解説します。

### この記事で学べること

* Dynamic Workersの仕組みとコンテナとの性能差
* Sandboxes GAとArtifactsでエージェントの作業環境を構築する方法
* Agent Memoryで会話を越えた記憶を持たせる方法
* Browser Runでエージェントにブラウザを使わせる方法
* AI Gateway・Cloudflare Mesh・Project Thinkの概要

### 対象読者

* AIエージェントを本番に持っていこうとしている開発者
* コンテナの起動コストやコールドスタートに悩んでいる方
* Cloudflare Workersの活用幅を広げたい方

## TL;DR

* **Dynamic Workers**: V8アイソレートで AI生成コードを実行。コンテナの100倍速、10〜100倍メモリ効率
* **Sandboxes GA**: 永続的なLinux環境。複雑なビルド・テストを安全に実行
* **Agent Memory**: Durable Objects + Vectorize で4種類の永続記憶を管理（プライベートβ）
* **Artifacts**: エージェント向けGit互換バージョン管理。1GB無料、$0.50/GB（プライベートβ）
* **Browser Run**: CDP対応ブラウザ自動化。同時接続数4倍（30→120）に拡張
* **AI Gateway**: 12以上のプロバイダーへの統合推論レイヤー。自動フェイルオーバー
* **Project Think**: エージェントSDKの次世代基盤。永続セッション・サブエージェント・ファイバー

---

## 1. Dynamic Workers — コンテナの100倍速でAI生成コードを実行

### 何が新しいのか

AIエージェントがコードを生成・実行するとき、従来はDockerコンテナを立ち上げていました。起動に数秒かかり、メモリも数百MBを消費します。

[Dynamic Workers](https://blog.cloudflare.com/dynamic-workers/)はV8アイソレートベースのサンドボックスで、この問題を根本から解決します。

| 指標 | コンテナ | Dynamic Workers |
| --- | --- | --- |
| 起動時間 | 数秒〜数十秒 | 数ミリ秒 |
| メモリ消費 | 数百MB | 数MB |
| 同時実行数 | 限定的 | 毎秒100万リクエスト可 |

> Zite社は Dynamic Workers を使い、LLM生成アプリケーションで「毎日数百万のリクエスト」をインスタント起動で処理しています。  
> — [Cloudflare公式ブログ](https://blog.cloudflare.com/dynamic-workers/)

### 使い方

```
// Worker内でDynamic Workerを起動する例
const dynamicWorker = await env.DYNAMIC_WORKERS.create({
  code: llmGeneratedCode,  // LLMが生成したJS/Python/WASMコード
  apis: [env.MY_API],      // サンドボックスからアクセスを許可するAPI
});

const result = await dynamicWorker.run();
```

**サポート言語**: JavaScript（最適化済み）、Python、WebAssembly

### セキュリティ設計

Cap'n Web RPCブリッジがサンドボックス境界を透過的に越えてAPI通信を行います。アウトバウンドHTTPは `globalOutbound` コールバックでインターセプトでき、認証トークンを外部コードに見せることなく注入できます。

### ヘルパーライブラリ

| パッケージ | 役割 |
| --- | --- |
| `@cloudflare/codemode` | LLM生成コードの簡易実行 |
| `@cloudflare/worker-bundler` | npmモジュールのバンドル |
| `@cloudflare/shell` | 仮想ファイルシステム（トランザクション書き込み対応） |

### 料金

* **$0.002/ユニークWorker/日**（通常のCPU時間・呼び出し料金に加算）
* **βテスト期間中は無料**（料金は変更の可能性あり）
* Workers Paid プランから利用可能

---

## 2. Sandboxes GA — 永続的なLinux環境でエージェントを動かす

### Dynamic Workersとの使い分け

Dynamic Workersは短いコードスニペットの実行に最適ですが、「リポジトリをcloneしてビルドしてテストを走らせる」ような複雑な作業には向きません。そのための環境が **Sandboxes** です。

[Sandboxes GA](https://blog.cloudflare.com/sandbox-ga/)は永続的な隔離Linuxコンテナで、シェル・ファイルシステム・バックグラウンドプロセスを備えます。

```
Sandboxesでできること例:
- git clone → pip install → pytest 実行
- フロントエンドのビルド（npm run build）
- 長時間かかるデータ処理
- ゲーム開発環境の構築
```

エージェントが人間の開発者と同じタイトなフィードバックループで作業できる環境を提供します。

---

## 3. Agent Memory — 会話を越えて記憶を持つ

### 4種類の記憶タイプ

[Agent Memory](https://blog.cloudflare.com/introducing-agent-memory/)は、AIエージェントに永続記憶を与えるマネージドサービスです。記憶は4つに分類されます。

| タイプ | 内容 | 例 |
| --- | --- | --- |
| **Facts** | 安定した知識 | 「このプロジェクトはGraphQLを使う」 |
| **Events** | 特定時刻の出来事 | デプロイ日時、意思決定の記録 |
| **Instructions** | 手順・ワークフロー | 「テスト前に必ずlintを実行する」 |
| **Tasks** | 一時的な作業項目 | 現在進行中のタスク（ベクトル検索から除外） |

Facts・Instructionsはキー付きストレージで管理され、更新時はスーパーセッションチェーンで追跡されます。

### API

```
const profile = await env.MEMORY.getProfile("my-project");

// 会話履歴から記憶を抽出・保存
await profile.ingest([
  { role: "user", content: "React + TypeScriptでプロジェクトをセットアップして" },
  { role: "assistant", content: "完了しました。Workers向けReact+TSをスキャフォールドしました" }
], { sessionId: "session-001" });

// 過去の記憶を検索・取得
const results = await profile.recall("ユーザーが好むパッケージマネージャーは？");
```

### アーキテクチャ

* **Durable Objects**: エージェントごとのスコープ分離
* **Vectorize**: セマンティック検索（コサイン類似度）
* **Workers AI**: Llama 4 Scout 17B（抽出）+ Nemotron 3 120B（合成）
* **RRF（Reciprocal Rank Fusion）**: 5チャンネル並列検索の結果をマージ

---

## 4. Artifacts — エージェント向けGit互換バージョン管理

### 概要

AIエージェントが生成したコード・設定ファイル・ドキュメントを管理するには、バージョン管理が欠かせません。[Artifacts](https://blog.cloudflare.com/artifacts-git-for-agents-beta/)はエージェントファーストで設計されたGit互換バージョン管理ストレージです。

標準のGitクライアントやCI/CDツールとそのまま連携できます。

### リポジトリ操作

```
// リポジトリを作成
const repo = await env.ARTIFACTS.create("my-agent-repo");
// → { remote: "https://xxx.artifacts.cloudflare.net/git/xxx.git", token: "..." }

// GitHub からインポート
const { remote, token } = await env.ARTIFACTS.import({
  source: { url: "https://github.com/cloudflare/workers-sdk", branch: "main" },
  target: { name: "workers-sdk" }
});
```

```
# 標準のgitコマンドでclone可能
git clone https://x:${TOKEN}@<id>.artifacts.cloudflare.net/git/<repo>.git
```

### ArtifactFS — 大規模リポジトリの高速化

数GBのリポジトリをcloneすると通常2分以上かかります。Cloudflareがオープンソース化した **ArtifactFS** はbloblessクローンでファイル内容をオンデマンド取得し、起動時間を **10〜15秒** に短縮します。

### 料金（βテスト）

| 区分 | 料金 | 無料枠 |
| --- | --- | --- |
| オペレーション | $0.15 / 1,000回 | 月10,000回 |
| ストレージ | $0.50 / GB-月 | 1GB |

---

## 5. Browser Run — エージェントにブラウザを持たせる

### 概要

[Browser Run](https://blog.cloudflare.com/browser-run-for-ai-agents/)はCloudflareのグローバルネットワーク上でブラウザ自動化を実行するサービスです。CDP（Chrome DevTools Protocol）エンドポイントを公開しており、エージェントフレームワークとネイティブに統合できます。

### 主な機能

| 機能 | 説明 |
| --- | --- |
| **Live View** | エージェントのブラウザ操作をリアルタイム確認 |
| **Human in the Loop** | ログインページなどでの人間介入後にエージェントへ制御を返す |
| **Session Recordings** | DOM変化・操作ログをJSONで記録、rrweb-playerで再生可能 |
| **CDP Endpoint** | Puppeteer/Playwright から直接接続 |
| **WebMCP** | Webサイトがエージェント向けにツールを公開する仕組み |

```
// Puppeteer経由でBrowser Runに接続
const browser = await puppeteer.connect({
  browserWSEndpoint: 'wss://api.cloudflare.com/client/v4/accounts/<ACCOUNT_ID>/browser-rendering/devtools/browser',
  headers: { 'Authorization': 'Bearer <API_TOKEN>' }
});

const page = await browser.newPage();
await page.goto('https://example.com');
```

### アップデート内容

同時接続数が **30 → 120**（4倍）に拡張されました。Quick Actions（スクリーンショット・PDF・Markdown抽出）は10req/秒に対応。

Workers Free / Paid の両プランで利用可能です。

---

## 6. AI Gateway — 12以上のプロバイダーへの統合推論レイヤー

### 概要

[AI Gateway](https://blog.cloudflare.com/ai-platform/)はエージェント向けに設計された統合推論レイヤーです。

```
エージェント → Cloudflare AI Gateway → OpenAI / Anthropic / Google / Mistral ...
                                     ↑ 12以上のプロバイダーを自動切り替え
```

### 主な機能

* **自動フェイルオーバー**: プロバイダー障害時に自動で代替プロバイダーへルーティング（コード変更不要）
* **コスト最適化**: モデルの種類・料金に応じてルーティングを調整
* **リクエストログ**: 全API呼び出しの可視化とレイテンシー分析
* **キャッシュ**: 同一プロンプトへの応答をキャッシュして料金削減

---

## 7. Cloudflare Mesh & Project Think — ネットワークとSDKの刷新

### Cloudflare Mesh

[Cloudflare Mesh](https://blog.cloudflare.com/mesh/)はAIエージェントがプライベートネットワークに安全にアクセスするゼロトラストネットワーキング基盤です。

* WorkersがVPC Bindingsを通じて企業の内部ネットワークへアクセス可能
* エージェントの「足回り」を企業ネットワーク全体に拡張

### Project Think — Agents SDKの次世代基盤

[Project Think](https://blog.cloudflare.com/project-think/)はCloudflare Agents SDKのコードネームで、`@cloudflare/think` として提供されます。

単発のプロンプト応答ではなく、長時間・マルチステップのタスクを想定した設計です。

| プリミティブ | 役割 |
| --- | --- |
| **Fibers（ファイバー）** | 軽量な並行実行単位。サブタスクを並列実行 |
| **Sub-agents** | エージェントが別のエージェントを生成・制御 |
| **Persistent Sessions** | ターン間でのステート永続化 |
| **Sandboxed Code Execution** | Dynamic Workersとの統合実行 |
| **The Execution Ladder** | タスクの優先度・スコープを管理する抽象層 |

---

## まとめ — Agents Weekが示した方向性

Cloudflare Agents Week 2026の7つのリリースは、AIエージェントのインフラを「アドホックな実験」から「本番スケールの運用」へ引き上げるための部品群です。

| 役割 | 機能 |
| --- | --- |
| コード実行 | Dynamic Workers / Sandboxes |
| 記憶 | Agent Memory |
| 成果物管理 | Artifacts |
| Web操作 | Browser Run |
| 推論 | AI Gateway |
| ネットワーク | Cloudflare Mesh |
| オーケストレーション | Project Think |

今後のポイントは **Artifacts のパブリックβ（2026年5月予定）** と **Agent Memory の一般公開** です。特にArtifactsは、エージェントが生成したコードをGitで管理するワークフローを標準化する可能性があります。

まず試すなら、Workers Paid プランで **Dynamic Workers のオープンβ** から始めるのがおすすめです。

## 参考リンク
