---
id: "2026-06-05-craft-agents-oss入門-ゼロコンフィグaiエージェントデスクトップの全貌-01"
title: "Craft Agents OSS入門 — ゼロコンフィグAIエージェントデスクトップの全貌"
url: "https://qiita.com/kai_kou/items/0e580e86ab9c3ec2291c"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "LLM", "OpenAI"]
date_published: "2026-06-05"
date_collected: "2026-06-06"
summary_by: "auto-rss"
query: ""
---

![Craft Agents OSSのデスクトップUIイメージ（マルチセッションインボックス・ドキュメント中心インターフェース・マルチプロバイダー接続）](https://raw.githubusercontent.com/kai-kou/zenn-blog-automation/main/images/craft-agents-oss-desktop-guide/01-hero.png)

## はじめに

2026年2月3日に [Craft Docs](https://www.craft.do/) チームが公開した **Craft Agents OSS** が、2026年5月に GitHub Trending 入りし改めて注目を集めています。

Craft Agents OSS は、AIエージェントとのやり取りを「チャット画面」から「ドキュメント中心のデスクトップ環境」へと再定義するオープンソースプロジェクトです。Apache 2.0 ライセンスで公開されており、自由に利用・改変・商用利用が可能です。

### この記事で学べること

- Craft Agents OSSの概要・アーキテクチャ
- 主要機能（マルチセッション、3段階権限モード、MCP連携等）
- インストールとセットアップ手順
- 対応LLMプロバイダーの種類と接続方法
- Claude Code との共通点・相違点

### 対象読者

- AIエージェントを日常業務に組み込みたいエンジニア
- Claude Code や Cursor を使っているが、GUI環境も試したい方
- オープンソースのエージェントフレームワークを評価中の方

### 前提条件

- macOS / Linux / Windows のいずれか
- Anthropic API キーまたは Claude Max/Pro サブスクリプション（推奨）
- Bun ランタイム（ソースビルドの場合のみ）

---

## TL;DR

- Craft Agents OSSは **Electron + React + Claude Agent SDK** 製のオープンソースAIエージェントデスクトップアプリ（Apache 2.0）
- Anthropic、Google AI Studio、ChatGPT Plus、GitHub Copilot、Ollama など **マルチプロバイダー** 対応
- **ゼロコンフィグ統合**: 「Linear を追加して」と伝えるだけで API 接続・認証・設定を自動完了
- **3段階権限モード**（Explore / Ask to Edit / Execute）でエージェントの自律度を柔軟に制御
- v0.9.0（2026-04-30 リリース）が最新版。macOS/Linux/Windows インストーラーあり

---

## Craft Agents OSS とは

### 開発背景

Craft Agents は、[Craft Docs](https://www.craft.do/) チームが「自分たちが毎日使うツール」として内部開発したものです。公式ブログには次のように記されています。

> "A better, more opinionated way of working with the most powerful AI agents. Document-centric workflows, zero-config integrations, and a beautiful UI."
> — [Introducing Craft Agents](https://www.craft.do/blog/introducing-craft-agents)（Craft Docs, 2026）

従来のAIエージェント作業環境（ターミナル、設定ファイル、OAuth の手動設定）が抱える摩擦を解消し、エージェントが実際にどう動くかに最適化されたインターフェースを提供することを目的としています。

### リポジトリ情報

| 項目 | 詳細 |
|------|------|
| GitHub | [lukilabs/craft-agents-oss](https://github.com/lukilabs/craft-agents-oss) |
| ライセンス | Apache 2.0 |
| 最新バージョン | v0.9.0（2026-04-30） |
| 公式ドキュメント | [agents.craft.do](https://agents.craft.do/docs/getting-started/introduction) |

---

## 主要機能

![Craft Agents OSSの4つの主要機能（マルチセッション・権限モード・MCP連携・マルチプロバイダー）](https://raw.githubusercontent.com/kai-kou/zenn-blog-automation/main/images/craft-agents-oss-desktop-guide/02-features-overview.png)

### 1. マルチセッションインボックス

Craft Agents のセッション管理は、**メール + タスクマネージャー** を組み合わせたような UI になっています。

- 複数のタスクを並行して管理（インボックス式）
- セッションごとに名前・フラグ・ステータス（Todo → In Progress → Needs Review → Done）を設定
- 会話履歴・添付ファイル・ツールの実行ログを永続保存
- バックグラウンドでタスクを実行しながら別のセッションに切り替え可能

### 2. 3段階権限モード

エージェントの自律度をタスクごとに制御できる3つのモードがあります。

| モード | 動作 | 用途 |
|--------|------|------|
| **Explore** | 読み取り専用（変更なし） | 調査・情報収集 |
| **Ask to Edit** | 変更前に承認を求める | コードレビュー、ドキュメント編集 |
| **Execute** | 自律実行（中断なし） | 繰り返しタスク、自動化 |

### 3. ゼロコンフィグ統合

最も特徴的な機能の一つが、設定ファイルを書かずにサービスを連携できる **ゼロコンフィグ統合** です。

エージェントに「GitHub を追加して」と伝えると、エージェントが自律的に API ドキュメントを読み込み、認証情報を設定します。対応サービスの例：

- **MCP サーバー**: GitHub, Linear, Craft ドキュメント（32+ツール）
- **REST API**: Google, Slack, Microsoft 各サービス
- **ローカルファイル**: Obsidian ノート、コードリポジトリ

### 4. VS Code スタイルのマルチファイル diff

エージェントがファイルを変更する際、VS Code と同様のマルチファイル diff ビューで変更内容を確認できます。変更を承認・拒否・一部のみ適用といった細かい制御が可能です。

### 5. イベント駆動オートメーション

ラベル付け、スケジュール、ツール使用などのイベントをトリガーとして、自動でエージェントを起動するオートメーション機能があります。

---

## アーキテクチャ

![Craft Agents OSSのアーキテクチャ（Desktop App・CLI Client・Headless Server・Core・外部LLMプロバイダー接続）](https://raw.githubusercontent.com/kai-kou/zenn-blog-automation/main/images/craft-agents-oss-desktop-guide/03-architecture-diagram.png)

### モノレポ構成

Craft Agents OSS はモノレポ構成で、複数のコンポーネントから成ります。

| コンポーネント | 説明 |
|--------------|------|
| **Desktop App** | Electron + React + shadcn/ui 製メインアプリ |
| **CLI クライアント** | ターミナル・スクリプトからの利用用 |
| **Headless サーバー** | リモートデプロイ用（Docker 対応） |
| **Core パッケージ** | 共有型定義・ビジネスロジック |

### 技術スタック

| 技術 | 用途 |
|------|------|
| Electron | デスクトップアプリ基盤 |
| React + shadcn/ui + Tailwind CSS v4 | UI フレームワーク |
| Bun | ランタイム・パッケージマネージャー |
| esbuild / Vite | ビルドツール |
| Claude Agent SDK | AIエージェント基盤（プライマリ） |
| AES-256-GCM | 認証情報の暗号化保存 |

### Claude Code との関係

Craft Agents は Claude Agent SDK をベースに構築されており、Claude Code と同じモデル・コアツール（Read, Write, Edit, Bash, Glob, Grep）・MCP サポートを共有しています。

**主な相違点:**

| 観点 | Claude Code | Craft Agents |
|------|-------------|-------------|
| インターフェース | CLI（ターミナル） | GUI（デスクトップアプリ） |
| セッション管理 | 単一セッション | マルチセッションインボックス |
| 対応プロバイダー | Anthropic のみ | マルチプロバイダー |
| 権限制御 | approve/reject | 3段階モード |
| REST API 連携 | MCP 経由 | MCP + ネイティブ REST |

---

## 対応 LLM プロバイダー

Craft Agents はマルチプロバイダーに対応しており、プロジェクトやコストに応じて使い分けられます。

### ネイティブ対応（直接接続）

| プロバイダー | 認証方法 |
|------------|---------|
| Anthropic | API キー or Claude Max/Pro OAuth |
| Google AI Studio | API キー |
| ChatGPT Plus/Pro | Codex OAuth |
| GitHub Copilot | OAuth |

### カスタムエンドポイント経由

OpenAI / Anthropic 互換の API であれば接続可能です。

- OpenRouter
- Vercel AI Gateway
- Ollama（ローカル LLM）
- その他 OpenAI/Anthropic 互換サービス

---

## インストールとセットアップ

### クイックインストール（推奨）

**macOS / Linux:**

```bash
curl -fsSL https://agents.craft.do/install-app.sh | bash
```

**Windows（PowerShell）:**

```powershell
irm https://agents.craft.do/install-app.ps1 | iex
```

### ソースからビルド

Bun ランタイムが必要です。

```bash
git clone https://github.com/lukilabs/craft-agents-oss.git
cd craft-agents-oss
bun install
bun run electron:start
```

開発モードで起動する場合:

```bash
cp .env.example .env
# .env を編集して API キーを設定
bun run electron:dev
```

### 初期設定の流れ

1. **API 接続の選択**: Anthropic API キーまたは Claude Max OAuth を設定
2. **ワークスペースの作成**: プロジェクトごとに独立した環境を構成
3. **ソースの接続**（任意）: MCP サーバーや REST API を接続
4. **権限モードの設定**: 用途に応じて Explore / Ask to Edit / Execute を選択

---

## 実践的なユースケース

### ユースケース1: マルチツールワークフロー自動化

Linear でイシューを管理し、GitHub にプルリクエストを作成し、Slack にレポートを投稿する一連の作業をエージェントに委託できます。

セッション内で一度サービスを接続すれば、後続のセッションでも設定が引き継がれます。

### ユースケース2: ドキュメント中心のコードレビュー

Ask to Edit モードでエージェントにコードレビューを依頼すると、エージェントが変更案を提示し、差分ビューで確認・承認できます。承認フローが自然に組み込まれているため、意図しない変更を防げます。

### ユースケース3: Craft ドキュメントとの連携

Craft ドキュメントに格納されたナレッジを活用して、議事録の要約・週次レポートの自動生成・仕様書からのコード生成などが可能です。

---

## 注意点


> **AES-256-GCM による認証情報の暗号化**: 保存された API キーは AES-256-GCM で暗号化されます。ただし、セキュリティ要件が高い環境では、API キーの管理方針をチームで事前に確認することを推奨します。



> **商標について**: "Craft" および "Craft Agents" は Craft Docs Ltd の商標です。Apache 2.0 ライセンスのソースコード自体は自由に利用できますが、商標に関するルールは [TRADEMARK.md](https://github.com/lukilabs/craft-agents-oss/blob/main/TRADEMARK.md) を確認してください。


---

## まとめ

Craft Agents OSS は、AIエージェントとの作業をターミナル・設定ファイルから解放し、**ドキュメント中心の直感的なデスクトップ環境** で管理できるオープンソースツールです。

公開情報をもとに整理すると、主なポイントは以下の通りです。

- **ゼロコンフィグ統合**: サービス追加の摩擦をなくし、エージェントが自律的に接続設定を完了
- **マルチプロバイダー対応**: Anthropic だけでなく Google, OpenAI, Ollama など柔軟に切り替え可能
- **3段階権限モード**: タスクの種類に応じてエージェントの自律度を制御
- **Claude Agent SDK ベース**: Claude Code と共通のコアを持ち、MCP エコシステムを活用可能

v0.9.0 はデスクトップアプリとしての成熟度を高めており、実用レベルに達しています。オープンソースのため、組織の要件に合わせた拡張・カスタマイズも可能です。

---

## 参考リンク

- [lukilabs/craft-agents-oss](https://github.com/lukilabs/craft-agents-oss) — GitHub リポジトリ（Apache 2.0）
- [Craft Agents 公式ドキュメント](https://agents.craft.do/docs/getting-started/introduction) — Getting Started
- [Introducing Craft Agents](https://www.craft.do/blog/introducing-craft-agents) — 公式ブログ発表（Craft Docs）
- [v0.9.0 Release Notes](https://github.com/lukilabs/craft-agents-oss/releases/tag/v0.9.0) — リリースノート（GitHub）
