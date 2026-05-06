---
id: "2026-05-05-gemini-api-docs-mcp入門-agent-skillsでcoding-agentの精度-01"
title: "Gemini API Docs MCP入門 — Agent SkillsでCoding Agentの精度を96.3%に向上させる"
url: "https://zenn.dev/kai_kou/articles/206-gemini-api-docs-mcp-agent-skills-guide"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "zenn"]
date_published: "2026-05-05"
date_collected: "2026-05-06"
summary_by: "auto-rss"
---

## はじめに

Claude CodeやCursorなどのCoding Agentは、学習データのカットオフ以降に更新されたAPIの仕様を把握できていません。Gemini APIの最新モデル名・メソッド・パラメータを誤って生成し、実行時にエラーが出るケースは開発現場でよく見られます。

2026年4月1日、Googleはこの問題を解決する2つの開発者向けツールを公開しました。

* **Gemini API Docs MCP**: 公式ドキュメントへのリアルタイムアクセスをMCPで提供するサーバー
* **Agent Skills**: 最新のSDKパターン・モデル名・ベストプラクティスをCoding Agentに注入するスキルセット

Googleの評価では、この2つを組み合わせることで**正解率96.3%・トークン数63%削減**を達成したとされています。

本記事では、これらのツールのセットアップ手順と各ツールとの統合方法を解説します。

### この記事で学べること

* Gemini API Docs MCPの仕組みと接続方法
* 3種類のAgent Skillsと選び方
* Claude Code・Cursor・Gemini CLIへの設定手順
* 設定後の動作確認方法

### 前提環境

* Node.js v20以上（`npx` コマンドが使用可能）
* Claude Code、Cursor、Gemini CLIのいずれか

---

## TL;DR

* `npx add-mcp "https://gemini-api-docs-mcp.dev"` でMCPサーバーを接続
* `npx skills add google-gemini/gemini-skills --skill gemini-api-dev --global` でスキルを追加
* 2つを併用すると、正解率96.3%・トークン数63%削減を達成

---

## 課題: Coding Agentが古い知識で誤ったコードを書く

Coding Agentは学習データに依存しているため、以下のような問題が生じます。

* **廃止予定モデルを参照**: `gemini-2.0-flash` など廃止予定（2026年6月1日）のモデル名を提案する
* **変更されたAPIを使用**: 旧メソッドや削除されたパラメータを含むコードを生成する
* **古いSDKパターン**: 推奨されなくなったインポートパスや初期化方法を使う

特にGemini APIは2026年に入ってモデルラインアップが大きく変化しており、トレーニングデータが古いエージェントは正しいコードを生成しにくい状況にあります。

---

## Gemini API Docs MCPとは

Gemini API Docs MCPは、Gemini APIの公式ドキュメントへのリアルタイムアクセスを提供するMCPサーバーです。

Googleは `https://gemini-api-docs-mcp.dev` に公開MCPサーバーをホストしており、Coding Agentはこのサーバーを通じて最新のAPIリファレンス・SDK情報・モデル一覧を取得できます。

### 主な機能

| 機能 | 説明 |
| --- | --- |
| `search_documentation` | 自然言語クエリでGemini APIドキュメントを検索 |
| リアルタイム更新 | トレーニングデータに依存せず常に最新の仕様を参照 |
| SDK情報 | Python・JavaScript・Go SDK全対応 |
| モデル情報 | 現在利用可能なモデル一覧と推奨設定 |

Coding Agentはコードを生成する際に `search_documentation` ツールを自動的に呼び出し、最新のAPIドキュメントに基づいたコードを生成します。

---

## Agent Skillsとは

Agent Skillsは、Coding Agentに最新のSDKパターンとベストプラクティスを直接注入するスキルファイルです。MCPサーバーが動的なドキュメント検索を担うのに対し、Agent Skillsは静的なガイドラインとして動作します。

Googleは `google-gemini/gemini-skills` として4種類のスキルを提供しています。

### 1. `gemini-api-dev`（基本スキル）

一般的なGemini API開発向けの基本スキルです。

* 現在推奨されているモデルへのルーティング
* マルチモーダルプロンプティングのパターン
* 認証・APIキー管理のベストプラクティス

**推奨シーン**: Gemini APIを初めて使う開発・一般的なテキスト生成・画像解析

### 2. `vertex-ai-api-dev`（Vertex AI向け）

Google Cloud Vertex AI経由でGeminiモデルを使う開発向けスキルです。

* Vertex AI SDK固有の初期化・認証パターン
* エンタープライズ向けのリージョン設定
* Google Cloudとの統合パターン

**推奨シーン**: Google Cloudプロジェクトを使う企業内開発・Vertex AIのAPIを直接利用する場合

### 3. `gemini-live-api-dev`（リアルタイム会話）

WebSocketを使ったリアルタイム会話アプリ向けスキルです。

* WebSocket接続の確立と管理
* ストリーミング音声・映像の送受信
* Voice Activity Detection（VAD）の設定
* セッション管理とエラーハンドリング

**推奨シーン**: 音声チャットボット・リアルタイム翻訳・ライブコーダーへの統合

### 4. `gemini-interactions-api`（マルチターン・エージェント開発）

テキスト生成・マルチターンチャット・ストリーミング・バックグラウンド実行を含む汎用インターフェース向けスキルです。

* テキスト生成とマルチターンチャット
* ストリーミングレスポンスの実装
* 関数呼び出し（Function Calling）の正しいパターン
* バックグラウンド実行とセッション管理

**推奨シーン**: AIエージェント構築・ストリーミングチャットボット・ツール呼び出し実装

---

## セットアップ手順

### Step 1: MCP サーバーの接続

以下のコマンドを実行してCoding AgentにMCPサーバーを接続します。

```
npx add-mcp "https://gemini-api-docs-mcp.dev"
```

このコマンドは、使用しているCoding Agentの設定ファイルを自動的に検出し、`https://gemini-api-docs-mcp.dev` をMCPサーバーとして登録します。Claude Code（`.claude/settings.json`）・Cursor（`.cursor/mcp.json`）・Gemini CLI（`~/.gemini/settings.json`）に対応しています。

### Step 2: Agent Skillsのインストール

**skills.sh経由（推奨）:**

開発用途に応じて必要なスキルをインストールします。

```
# 基本スキル（ほとんどのGemini API開発に対応）
npx skills add google-gemini/gemini-skills --skill gemini-api-dev --global

# Google Cloud / Vertex AI経由でGeminiを使う場合
npx skills add google-gemini/gemini-skills --skill vertex-ai-api-dev --global

# リアルタイム会話アプリ開発を行う場合は追加
npx skills add google-gemini/gemini-skills --skill gemini-live-api-dev --global

# エージェント開発（Interactions API）を行う場合は追加
npx skills add google-gemini/gemini-skills --skill gemini-interactions-api --global
```

`--global` フラグを付けると全プロジェクトに適用されます。特定プロジェクトのみに適用する場合はフラグを外してください。

**Context7経由:**

```
npx ctx7 skills install /google-gemini/gemini-skills gemini-api-dev
npx ctx7 skills install /google-gemini/gemini-skills gemini-live-api-dev
npx ctx7 skills install /google-gemini/gemini-skills gemini-interactions-api
```

---

## 動作確認

セットアップ後は以下の手順で正しく設定されているか確認します。

### MCP接続の確認

Coding Agentに以下のような質問を投げかけます。

```
Gemini APIのcontext cachingはどのように使いますか？
```

MCPが正しく機能している場合、エージェントは `search_documentation` ツールを呼び出し、`cacheContent` などの具体的なメソッド名とその使い方を公式ドキュメントに基づいて回答します。

### ツール別の確認コマンド

| ツール | MCP確認 | Skills確認 |
| --- | --- | --- |
| Claude Code | `/mcp` | `/skills` |
| Cursor | Settings > Features > MCP | Settings > Rules |
| Gemini CLI | `gemini mcp list` | `gemini skills list` |
| GitHub Copilot | `@gemini /mcp` | `@gemini /skills` |

---

## ツール別の設定詳細

各ツールでの設定確認方法と注意点を整理します。

### Claude Code

Claude Codeでは、`npx add-mcp` コマンドがClaude CodeのMCP設定ファイルを自動的に更新し、`gemini-api-docs-mcp.dev` サーバーを追加します。設定後、`/mcp` コマンドでMCPサーバーの接続状態とツール一覧を確認できます。

### Cursor

Cursorでは `Settings > Features > MCP` からサーバーの接続状態を確認します。Agent Skillsは `Settings > Rules` に自動的に追記されます。設定変更後はIDEを完全に再起動してください。

### Gemini CLI

Gemini CLIでは `gemini mcp list` でMCPサーバー一覧を、`gemini skills list` でインストール済みスキルを確認できます。

---

## トラブルシューティング

### エージェントがスキルを無視する

ターミナルベースのエージェント（Claude Code）は起動時にスキルをインデックスします。スキルのインストール後はエージェントを再起動してください。IDEベースのツール（Cursor）では、IDEを完全に終了してから再起動します。

### グローバルとローカルの競合

`--global` でインストールしたスキルとプロジェクトローカルのスキルが競合する場合は、プロジェクトルートで `--global` フラグなしで再インストールします。

```
# プロジェクトルートで実行
npx skills add google-gemini/gemini-skills --skill gemini-api-dev
```

---

## ベンチマーク: 2つを組み合わせた効果

Googleが公表した評価結果によると、MCPとSkillsを組み合わせることで以下の効果が得られています。

| 指標 | 結果 |
| --- | --- |
| 正解率 | **96.3%**（評価セット） |
| トークン数削減 | **63%削減**（vanilla promptingとの比較） |

MCPが動的なドキュメント検索を担い、Skillsが静的なガイドラインを提供することで、両者の相乗効果が得られています。公式ブログでは「combining MCP and Skills leads to a 96.3% pass rate on our eval set, with 63% fewer tokens per correct answer compared to vanilla prompting」と述べられています。

---

## まとめ

Gemini API Docs MCPとAgent Skillsは、Coding AgentがGemini APIの最新仕様を正確に参照できるようにするための2つの補完的なツールです。

* **Gemini API Docs MCP**: `search_documentation` ツールで常に最新のドキュメントを参照
* **Agent Skills**: 3種類のスキルで開発パターンとモデル情報をエージェントに直接注入
* **2つの組み合わせ**: 正解率96.3%・トークン63%削減という評価結果

セットアップは2つのコマンドで完了し、Claude Code・Cursor・Gemini CLI・GitHub Copilotに対応しています。Gemini APIを扱うプロジェクトでは導入を検討してみてください。

## 参考リンク
