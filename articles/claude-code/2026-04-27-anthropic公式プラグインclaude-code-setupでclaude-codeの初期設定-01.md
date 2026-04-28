---
id: "2026-04-27-anthropic公式プラグインclaude-code-setupでclaude-codeの初期設定-01"
title: "Anthropic公式プラグイン「claude-code-setup」でClaude Codeの初期設定を効率化する"
url: "https://zenn.dev/shirochan/articles/1a9c4b51f4ef7b"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "OpenAI", "Python"]
date_published: "2026-04-27"
date_collected: "2026-04-28"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Codeには、フック・スキル・MCPサーバーといった拡張機能が豊富に用意されています。しかし何から始めればいいか分からず、デフォルト設定のまま使い続けているケースは少なくありません。`claude-code-setup` は、そのギャップを埋めるためにAnthropicが公式に提供しているプラグインです。

## このプラグインが何をするか

`claude-code-setup` はコードベースを解析し、そのプロジェクトに適したClaude Codeの自動化設定を提案します。**ファイルの書き換えは一切行いません**。あくまで「何を設定すべきか」を教えてくれるだけで、実際に設定するのは開発者自身です。

提案のカテゴリは以下の5つ（SKILL.mdの定義に基づく）:

| カテゴリ | 概要 | 例 |
| --- | --- | --- |
| **Hooks** | ツールイベントに連動する自動処理 | 保存時のフォーマット、機密ファイルへの書き込み防止 |
| **MCP Servers** | 外部ツールとの統合 | context7（ドキュメント検索）、Playwright（ブラウザ操作）、DBアクセス |
| **Skills** | 再利用可能なワークフローのパッケージ | PR作成、テスト実行、コード説明 |
| **Subagents** | 並列で動く専門レビュアー | セキュリティ、パフォーマンス、アクセシビリティチェック |
| **Plugins** | 複数のSkillをまとめたバンドル | チーム共有向けのコレクション |

各カテゴリにつき、上位1〜2件に絞って提案する設計になっています。一度に大量の提案を返して混乱させないよう、意図的に絞り込まれています。

> **補足**: READMEには「Slash Commands」がカテゴリとして列挙されていますが、実装の仕様書であるSKILL.mdでは「Plugins」が5番目のカテゴリとして定義されています。上記の表はSKILL.mdに基づいています。

## 内部の動作

プラグインが持つスキル `claude-automation-recommender` は3フェーズで動作します。

**フェーズ1: コードベースの読み取り**  
`Read` / `Glob` / `Grep` / `Bash` ツールを使い、`package.json`、ディレクトリ構造、既存の設定ファイルを確認します。使用言語・フレームワーク・テスト構成・外部連携を把握します。

**フェーズ2: 提案の生成**  
検出した情報を既知のパターンに照合します。たとえば:

* Prettierの設定を検出 → `PostToolUse` フックで自動フォーマットを提案
* Reactを検出 → Playwright MCPサーバーを提案
* PostgreSQLを検出 → DB接続MCPサーバーを提案

**フェーズ3: レポートの出力**  
各カテゴリの推奨設定を、その理由・インストール手順・実装方法とあわせて出力します。

## インストール方法

Anthropic公式マーケットプレイス（`claude-plugins-official`）はClaude Codeの起動時から利用可能な状態になっています。追加の設定は不要です。

インストールはClaude Code内でコマンドを1行実行するだけです:

```
/plugin install claude-code-setup@claude-plugins-official
```

インストール後、プラグインをその場で有効化するには:

インストール済みプラグインの確認や管理は `/plugin` コマンドから行えます。

## 使い方

インストール後は自然言語で呼び出します。以下はどれも機能します:

```
recommend automations for this project
help me set up Claude Code
what hooks should I use?
```

Claude Codeがプロジェクトを解析し、設定候補のリストを返してくれます。

---

## 実際の使用例

以下に公開しているサンプルプロジェクトで試してみました。  
<https://github.com/shirochan/chatbot-created-by-claude-code>

### 実践例

```
❯ claude codeのセットアップを手伝って下さい。

⏺ Skill(claude-code-setup:claude-automation-recommender)
  ⎿  Successfully loaded skill

⏺ コードベースを分析して、最適な自動化設定を提案します。

  Listed 3 directories (ctrl+o to expand)
```

### 結果

```
  実装の優先順位

  ┌────────┬────────────────────────────────────┬────────────────────────────────────────────────────┐
  │ 優先度 │                項目                │                        理由                        │
  ├────────┼────────────────────────────────────┼────────────────────────────────────────────────────┤
  │ ★★★    │ .env ブロック Hook                 │ API キー漏洩防止                                   │
  ├────────┼────────────────────────────────────┼────────────────────────────────────────────────────┤
  │ ★★★    │ context7 MCP                       │ LangChain/Anthropic ドキュメントが頻繁に更新される │
  ├────────┼────────────────────────────────────┼────────────────────────────────────────────────────┤
  │ ★★     │ security-reviewer サブエージェント │ ファイルアップロード・DB処理のリスク               │
  ├────────┼────────────────────────────────────┼────────────────────────────────────────────────────┤
  │ ★★     │ gen-test スキル                    │ 充実したテストスイートの維持                       │
  ├────────┼────────────────────────────────────┼────────────────────────────────────────────────────┤
  │ ★      │ GitHub MCP                         │ PR/Issue 管理の効率化                              │
  └────────┴────────────────────────────────────┴────────────────────────────────────────────────────┘

  ---
  どれか特定の項目を実際に設定しますか？「.env ブロックと context7 を設定して」のように伝えてください。
```

あくまで提案なので、そのまま採用するかどうかは開発者が判断します。

全文はこちらから確認できます。

分析が完了しました。推奨内容をまとめます。

```
  Claude Code 自動化セットアップ推奨

  コードベースプロフィール

  - 言語: Python 3.11+
  - フレームワーク: Streamlit + LangChain
  - 主要ライブラリ: LangChain (OpenAI / Anthropic / Google), Pillow, pdfplumber, SQLite
  - テスト: pytest (5ファイル / 充実したテストスイート)
  - 現状: hooks最小限, スキル・MCPなし

  ---
  🔌 MCP サーバー

  1. context7 — ライブラリドキュメント自動検索

  LangChain / Anthropic SDK / OpenAI SDK など更新頻度の高いパッケージを多数使用しているため、最新ドキュメントをその場で参照できると作業効率が上がります。

  claude mcp add context7 -- npx -y @upstash/context7-mcp

  2. GitHub MCP — PR・Issue管理

  claude mcp add github -- npx -y @modelcontextprotocol/server-github
  # 環境変数が必要: GITHUB_TOKEN

  ---
  ⚡ Hooks

  1. .env ファイルの編集をブロック

  API キーを含む .env を誤って編集・コミットするリスクを防ぎます。

  .claude/settings.json を作成:

  {
    "hooks": {
      "PreToolUse": [
        {
          "matcher": "Edit|Write",
          "hooks": [
            {
              "type": "command",
              "command": "python3 -c \"import sys, json; data=json.load(sys.stdin); path=data.get('tool_input',{}).get('file_path',''); sys.exit(1 if '.env' in path and not path.endswith('.example') else 0)\"",
              "blocking": true
            }
          ]
        }
      ]
    }
  }

  2. ファイル編集後に自動テスト実行

  src/ や tests/ の変更後に関連テストを走らせます。

  {
    "hooks": {
      "PostToolUse": [
        {
          "matcher": "Edit|Write",
          "hooks": [
            {
              "type": "command",
              "command": "bash -c \"path=$(echo $CLAUDE_TOOL_INPUT | python3 -c 'import sys,json; print(json.load(sys.stdin).get(\\\"file_path\\\",\\\"\\\"))' 2>/dev/null); [[ $path == *src/* || $path == *tests/*]] && uv run pytest tests/ -q --tb=short 2>&1 | tail -20 || true\""
            }
          ]
        }
      ]
    }
  }

  ---
  🤖 サブエージェント

  security-reviewer

  API キー管理・ファイルアップロード処理・SQLite 履歴など、セキュリティに敏感なコードが多いため、レビュー時に役立ちます。

  .claude/agents/security-reviewer.md を作成:

  ---
  name: security-reviewer
  description: API key handling, file upload processing, and SQLite security review
  ---

  このプロジェクトのセキュリティレビューを実施してください。特に以下を確認します:
  - API キーの取り扱いと漏洩リスク
  - ファイルアップロード処理のバリデーション (src/utils/file_processing.py)
  - SQLite チャット履歴のインジェクションリスク (src/utils/database.py)
  - ユーザー入力のサニタイズ (bleach の適切な使用)

  問題点とその修正方法をリストアップしてください。

  ---
  🎯 スキル

  gen-test — テスト自動生成

  新機能追加時にテストの雛形を生成します。.claude/skills/gen-test/SKILL.md:

  ---
  name: gen-test
  description: Generate pytest tests for a given source file in this project
  disable-model-invocation: false
  ---

  引数で指定されたソースファイル($ARGUMENTS)に対して、既存の tests/ ディレクトリのスタイル(pytest + pytest-mock)に合わせたテストを生成してください。conftest.py のフィクスチャも参考にしてください。

  使い方: /gen-test src/utils/file_processing.py

  ---
  実装の優先順位

  ┌────────┬────────────────────────────────────┬────────────────────────────────────────────────────┐
  │ 優先度 │                項目                │                        理由                        │
  ├────────┼────────────────────────────────────┼────────────────────────────────────────────────────┤
  │ ★★★    │ .env ブロック Hook                 │ API キー漏洩防止                                   │
  ├────────┼────────────────────────────────────┼────────────────────────────────────────────────────┤
  │ ★★★    │ context7 MCP                       │ LangChain/Anthropic ドキュメントが頻繁に更新される │
  ├────────┼────────────────────────────────────┼────────────────────────────────────────────────────┤
  │ ★★     │ security-reviewer サブエージェント │ ファイルアップロード・DB処理のリスク               │
  ├────────┼────────────────────────────────────┼────────────────────────────────────────────────────┤
  │ ★★     │ gen-test スキル                    │ 充実したテストスイートの維持                       │
  ├────────┼────────────────────────────────────┼────────────────────────────────────────────────────┤
  │ ★      │ GitHub MCP                         │ PR/Issue 管理の効率化                              │
  └────────┴────────────────────────────────────┴────────────────────────────────────────────────────┘

  ---
  どれか特定の項目を実際に設定しますか？「.env ブロックと context7 を設定して」のように伝えてください。
```

## 注意点

* 提案の質はコードベースの状態に依存します。`package.json` や設定ファイルが整備されているほど精度が上がります。
* 提案された設定を実際に適用するのは手作業になります。自動で設定を書き込む機能はありません。
* スキルが参照するリファレンスファイル（hooks-patterns.md、mcp-servers.md など）はプラグイン内にバンドルされており、Anthropicが管理しています。

## まとめ

`claude-code-setup` は「Claude Codeの拡張機能を何から入れれば良いか分からない」という状況に対して、コードベースを根拠にした提案を返してくれます。大がかりな導入コストはなく、コマンド1行でインストールして自然言語で呼び出すだけです。

Claude Codeを使い始めたばかりの方にも、すでに使い込んでいるが拡張設定が後回しになっている方にも、試してみる価値はあります。

---

**参考リンク**
