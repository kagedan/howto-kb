---
id: "2026-03-22-実践claude-codeの能力を120引き出すaiハーネスエンジニアリングclaudemdhook-01"
title: "【実践】Claude Codeの能力を120%引き出す「AIハーネスエンジニアリング」──CLAUDE.md・Hooks・Rules設定ガイ"
url: "https://zenn.dev/yoshihiko555/articles/b2fd663ab14416"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "AI-agent", "zenn"]
date_published: "2026-03-22"
date_collected: "2026-03-23"
summary_by: "auto-rss"
---

Claude Codeの真価は、プロンプトの書き方ではなく「環境設計」で決まる。CLAUDE.md、Hooks、Rules、Agent Routingを体系的に設計することで、AIコーディングアシスタントは単なるチャットボットから、プロジェクトの文脈を理解し自律的に動く開発パートナーへと変わる。

この記事では、Claude Codeの設定機構を「ハーネスエンジニアリング」として体系化し、各レイヤーの設計方法から、自作のオーケストレーションシステム「ai-orchestra」による統合管理まで、実践的に解説する。

---

## プロンプトから「環境構築」へ──ハーネスエンジニアリングとは

### プロンプトエンジニアリングとの違い

プロンプトエンジニアリングは「何を聞くか」の技術である。質問の仕方、few-shotの工夫、Chain-of-Thoughtの誘導——これらはすべて**1回のやりとり**を最適化するアプローチだ。

ハーネスエンジニアリングは「AIが常に最適な状態で働ける環境を設計する」技術である。ここでいう「ハーネス」とは、Claude Codeを制御する設定群（CLAUDE.md、Hooks、Rules、Settings）の総称だ。テストハーネスがテスト実行環境を整備するように、AIハーネスはAIの実行環境を整備する。

| 比較軸 | プロンプトエンジニアリング | ハーネスエンジニアリング |
| --- | --- | --- |
| 最適化対象 | 1回の対話 | 全セッション |
| 持続性 | その場限り | プロジェクトに永続化 |
| 共有性 | 個人の知見 | チーム全体に適用可能 |
| 制御の強さ | ソフト（LLMが解釈） | ハード（プログラムで強制）も可 |
| スケーラビリティ | 対話ごとに再入力 | 一度設計すれば自動適用 |

### なぜ「ハーネス」が必要か

Claude Codeの使い方を「毎回プロンプトで指示する」段階から脱却すべき3つの理由がある。

**1. コンテキストの一貫性**

プロジェクトの規約、ディレクトリ構造、命名規則——これらを毎回プロンプトで伝えるのは非効率である。CLAUDE.mdに一度書けば、全セッションで自動的にコンテキストとして読み込まれる。

**2. ガードレールの決定性**

「テストを必ず書いて」というプロンプトはLLMが無視する可能性がある。一方、PreToolUseフックでテスト未実行の実装を検知してブロックすれば、ルール違反を**プログラムで**防げる。

**3. チームスケール**

個人のプロンプト技術はチームに共有しにくい。ハーネス（`.claude/`配下のファイル群）はgitで管理し、チーム全員に同じ開発体験を提供できる。

---

## CLAUDE.mdの設計──プロジェクトの文脈をAIにインストールする

CLAUDE.mdはClaude Codeが**セッション開始時に自動で読み込む**設定ファイルである。LLM向けの「意味的な指示」を書く場所であり、ハーネスの土台となるレイヤーだ。

### 3つの階層

Claude Codeは以下の順でCLAUDE.mdを読み込み、すべてをコンテキストに含める。

```
~/.claude/CLAUDE.md              ← グローバル（全プロジェクト共通）
.claude/CLAUDE.md                ← プロジェクトルート（チーム共有）
src/backend/.claude/CLAUDE.md    ← サブディレクトリ（領域固有）
```

**グローバル**には言語設定やコミュニケーションの好みなど、プロジェクトに依存しない個人設定を書く。

```
# ~/.claude/CLAUDE.md

## Communication
- 文章は簡潔に。ただし重要な理由や前提は箇条書きで補足してください。
- 不明点が多い場合は、すぐに大きな変更をせず前提の確認から始めてください。

## General coding policy
- 既存の仕様や振る舞いを壊さないことを最優先してください。
- 大きな変更より、小さく安全なステップでの修正を優先してください。
```

**プロジェクトルート**にはリポジトリ固有の文脈を書く。ディレクトリ構造、ワークフロー、使用中のスキル一覧など。

```
# .claude/CLAUDE.md

## プロジェクト概要
このリポジトリは個人のデジタルガーデンです。

## ディレクトリ構造
digital-garden/
├── content/articles/   # ブログ記事（published/ drafts/ archive/）
├── content/notes/      # 学習ノート
└── reviews/            # 振り返り（weekly/ monthly/ yearly/）

## コンテンツの成長フロー
brainstorm → ideas → notes → articles
（ブレスト  → 思いつき → 学習・整理 → 公開記事）
```

### 効果的なCLAUDE.mdの書き方

**含めるべき情報:**

* プロジェクトの概要（1-2文）
* ディレクトリ構造（主要なもののみ）
* 命名規則・コーディング規約
* テスト実行コマンド
* ワークフロー（データの流れ、デプロイ手順）
* 使用中のスキル一覧

**含めるべきでない情報:**

* 実装の詳細（コードを読めばわかること）
* 一時的な情報（今の作業内容）
* 巨大なリスト（コンテキストウィンドウを圧迫する）

コンテキストウィンドウの消費を意識し、「Claude Codeがこの情報を持っていないと正しい判断ができない」ものだけを書くのが原則である。

---

## Settings階層とRulesシステムによるAIの挙動制御

### settings.jsonの3階層

Claude Codeの機能設定は`settings.json`で管理する。CLAUDE.mdがLLM向けの「意味的な指示」であるのに対し、settings.jsonは**プログラムレベルの設定**である。

```
~/.claude/settings.json                ← ユーザー設定（全プロジェクト共通）
.claude/settings.json                  ← プロジェクト設定（git管理、チーム共有）
.claude/settings.local.json            ← ローカル設定（gitignore、個人上書き）
```

各階層はマージされ、下位の設定が上位を上書きする。

```
// .claude/settings.json（チーム共有）
{
  "permissions": {
    "allow": ["Bash(npm run test)", "Bash(npm run lint)"],
    "deny": ["Bash(rm -rf)"]
  }
}
```

```
// .claude/settings.local.json（個人、gitignore対象）
{
  "hooks": {
    "SessionStart": [
      {
        "type": "command",
        "command": "python3 $AI_ORCHESTRA_DIR/scripts/sync-orchestra.py"
      }
    ]
  }
}
```

チームで共有すべき権限設定は`settings.json`に、個人のフック設定や環境依存の設定は`settings.local.json`に配置する。`.local.json`は`.gitignore`に追加する。

### .claude/rules/によるルールのモジュール分割

`.claude/rules/`ディレクトリに`.md`ファイルを配置すると、Claude Codeが自動で読み込む。CLAUDE.mdに全ルールを書くとファイルが肥大化するため、関心事ごとにファイルを分割するのが有効である。

```
.claude/rules/
├── coding-principles.md          # コード品質ルール
├── config-loading.md             # 設定ファイルの読み込み手順
├── agent-routing-policy.md       # エージェントルーティングポリシー
├── codex-delegation.md           # Codex CLI委譲ルール
├── gemini-delegation.md          # Gemini CLI委譲ルール
├── skill-review-policy.md        # レビューポリシー
├── task-memory-usage.md          # タスク状態管理ルール
└── context-sharing.md            # コンテキスト共有ルール
```

各ルールファイルは独立したドキュメントとして完結させる。例えば`coding-principles.md`には以下のような内容を書く。

```
# Code Quality Policy

## シンプルさ優先
- 読みやすいコードを複雑なコードより選ぶ
- 過度な抽象化を避ける

## Early Return
ネストを浅く保つために Early Return を使う。
ネスト深度は2以下を目標とする。

## 型ヒント必須
すべての関数に型アノテーションを付ける。
```

ルールにはYAMLフロントマターで`paths:`を指定でき、特定のディレクトリでのみ有効にすることも可能だ。

```
---
paths:
  - "src/backend/**"
---
# Backend Rules
バックエンド固有のルールをここに書く。
```

### CLAUDE.md vs Rules: 使い分け

|  | CLAUDE.md | .claude/rules/ |
| --- | --- | --- |
| 用途 | プロジェクト概要、ワークフロー | コーディング規約、ポリシー |
| スコープ | 常にすべて読み込み | パス制限可能 |
| 更新頻度 | 低い（構造変更時） | 中程度（ルール追加・修正） |
| 推奨サイズ | 簡潔に（200行以内） | ファイルごとに分割 |

---

## Hooksシステム──Claude Codeのワークフローを自動化・拡張する

HooksはClaude Codeの最も強力なハーネス機構である。CLAUDE.mdやRulesがLLMへの「お願い」（Soft Rule）であるのに対し、Hooksはプログラムで**確実に実行される**（Hard Rule）。

### Soft Rule vs Hard Rule

```
Soft Rule（CLAUDE.md / Rules）
  → LLMが解釈して従う。無視される可能性がある。
  → 例: 「テストを必ず書いてください」

Hard Rule（Hooks）
  → プログラムが機械的に実行する。回避不可能。
  → 例: PreToolUse hookでテスト未実行を検知し、exit code 2でブロック
```

この区別を理解することが、ハーネス設計の核心である。

### 6種のイベントタイプ

| イベント | 発火タイミング | 主な用途 |
| --- | --- | --- |
| `SessionStart` | セッション開始時 | 設定の同期、状態の読み込み |
| `SessionEnd` | セッション終了時 | クリーンアップ、ログ出力 |
| `UserPromptSubmit` | ユーザーがプロンプトを送信した後 | コンテキスト注入、ルーティング提案 |
| `PreToolUse` | ツール実行前 | ブロック判定、承認フロー |
| `PostToolUse` | ツール実行後 | 結果キャプチャ、自動整形 |
| `SubagentStart` / `SubagentStop` | サブエージェントのライフサイクル | モニタリング、リソース管理 |

### Hookの設定方法

`settings.json`（または`settings.local.json`）にフック定義を追加する。

```
{
  "hooks": {
    "PreToolUse": [
      {
        "type": "command",
        "command": "python3 ./hooks/check-codex-before-write.py",
        "matcher": "Edit|Write"
      }
    ],
    "PostToolUse": [
      {
        "type": "command",
        "command": "python3 ./hooks/lint-on-save.py",
        "matcher": "Edit"
      }
    ]
  }
}
```

`matcher`はツール名の正規表現で、特定のツール使用時のみフックを発火させる。

PreToolUseフックがexit code `2`を返すと、Claude Codeはそのツール呼び出しをブロックする。これがHard Ruleの正体である。

```
#!/usr/bin/env python3
"""check-codex-before-write.py
core/ 配下のファイル変更前にCodexへの相談を提案する。
"""
import sys
import json

input_data = json.loads(sys.stdin.read())
tool_name = input_data.get("tool_name", "")
tool_input = input_data.get("tool_input", {})

file_path = tool_input.get("file_path", "")

# core/ 配下のファイル変更は Codex に相談すべき
if "core/" in file_path:
    print("[Codex Suggestion] core/ の変更を検出しました。")
    print("Codex に設計相談してから編集してください。")
    # exit code 2 = ツール実行をブロック
    sys.exit(2)
```

### UserPromptSubmit: コンテキスト注入とルーティング

UserPromptSubmitフックはプロンプト送信後に発火し、stdoutに出力したテキストがClaude Codeのコンテキストに追加される。エージェントルーティングの提案や、外部CLIへの委譲指示に利用できる。

```
#!/usr/bin/env python3
"""agent-router.py
ユーザーのプロンプトを分析し、最適なエージェントを提案する。
"""
import sys
import json

input_data = json.loads(sys.stdin.read())
prompt = input_data.get("prompt", "")

# キーワードベースの簡易ルーティング
if any(kw in prompt for kw in ["Python", "FastAPI", "Django"]):
    print("[Agent Routing] 'Python' → `backend-python-dev` (tool: codex):")
    print('Task(subagent_type="backend-python-dev", prompt="...")')
```

### 実践的なHook構成例

以下は筆者が実際に使用しているHook構成（一部抜粋）である。

| フック | イベント | 目的 |
| --- | --- | --- |
| `sync-orchestra.py` | SessionStart | パッケージの自動同期 |
| `load-task-state.py` | SessionStart | Plans.mdからタスク状態を読み込み |
| `agent-router.py` | UserPromptSubmit | エージェントルーティング提案 |
| `check-codex-before-write.py` | PreToolUse(Edit|Write) | 重要ファイル変更前のCodex相談提案 |
| `suggest-gemini-research.py` | PreToolUse(WebSearch|WebFetch) | Geminiリサーチへの委譲提案 |
| `inject-shared-context.py` | PreToolUse(Agent|Task) | サブエージェントへのコンテキスト注入 |
| `capture-task-result.py` | PostToolUse(Agent|Task) | サブエージェント結果のキャプチャ |
| `lint-on-save.py` | PostToolUse(Edit) | 保存時の自動lint |

---

## Agent Routing──専門エージェントをタスクに最適配置する

Claude Codeのサブエージェント機能を活用すると、タスクの種類に応じて専門エージェントに作業を委譲できる。ハーネスエンジニアリングでは、この委譲先を**設定ファイルで一元管理**する。

エージェントの実行ツール（Codex CLI / Gemini CLI / Claude直接処理）を1つのYAMLファイルで管理する。

```
# .claude/config/agent-routing/cli-tools.yaml

codex:
  enabled: true
  model: gpt-5.3-codex
  sandbox:
    analysis: read-only
    implementation: workspace-write
  flags: --full-auto

gemini:
  enabled: true
  model: gemini-3.1-pro-preview

# エージェントルーティング
agents:
  # レビュー系 → Claude直接処理（コンテキスト内で完結）
  code-reviewer:
    tool: claude-direct
  security-reviewer:
    tool: claude-direct
  architecture-reviewer:
    tool: claude-direct

  # 実装系 → Codex CLI（深い推論 + ファイル操作）
  backend-python-dev:
    tool: codex
    sandbox: workspace-write
  frontend-dev:
    tool: codex
    sandbox: workspace-write

  # リサーチ系 → Gemini CLI（大規模検索 + マルチモーダル）
  researcher:
    tool: gemini

  # 自動選択（タスク内容に応じて切り替え）
  general-purpose:
    tool: auto
```

### 4つのルーティングモード

| モード | 動作 | 適した場面 |
| --- | --- | --- |
| `codex` | OpenAI Codex CLIで実行 | 実装、デバッグ、設計判断 |
| `gemini` | Google Gemini CLIで実行 | リサーチ、ドキュメント分析、マルチモーダル |
| `claude-direct` | Claude Code自身で処理 | レビュー、コンテキスト内で完結する作業 |
| `auto` | タスク内容に応じて自動選択 | 汎用エージェント |

### ローカル上書き

プロジェクト固有のモデルや設定は`.local.yaml`で上書きする。ベースファイルはai-orchestraから自動同期されるため、直接編集しない。

```
# .claude/config/agent-routing/cli-tools.local.yaml
codex:
  model: gpt-5.4-mini  # このプロジェクトだけ軽量モデルで実行
```

上書きルール: `.local.yaml`に定義されたキーだけがベースを上書きし、未定義のキーはベースの値を継承する。

---

## 実践例: ai-orchestraによるハーネス統合管理

ここまで個別に紹介してきたCLAUDE.md、Rules、Hooks、Agent Routingは、プロジェクトが大きくなるにつれ管理が煩雑になる。「コード品質ルール」を10プロジェクトで共有したい場合、手動コピーでは破綻する。

この課題を解決するために筆者が構築したのが[ai-orchestra](https://github.com/yoshihiko555/ai-orchestra)である。

### パッケージシステム

ai-orchestraはハーネスの構成要素を**パッケージ**として管理する。各パッケージは`manifest.json`で内容を定義する。

```
{
  "name": "core",
  "version": "0.4.0",
  "description": "全パッケージ共通の基盤ライブラリ",
  "depends": [],
  "hooks": {
    "SessionStart": ["load-task-state.py"],
    "SessionEnd": ["cleanup-session-context.py"],
    "PreToolUse": [
      { "file": "check-plan-gate.py", "matcher": "Agent|Task" },
      { "file": "inject-shared-context.py", "matcher": "Agent|Task" }
    ],
    "PostToolUse": [
      { "file": "capture-task-result.py", "matcher": "Agent|Task" },
      { "file": "update-working-context.py", "matcher": "Edit" }
    ]
  },
  "skills": ["skills/startproject", "skills/checkpointing", "skills/task-state"],
  "agents": [],
  "rules": ["rules/coding-principles.md", "rules/config-loading.md"],
  "config": ["config/task-memory.yaml"]
}
```

現在10パッケージを運用している。

| パッケージ | 役割 |
| --- | --- |
| `core` | 基盤（状態管理、コンテキスト共有、品質ルール） |
| `agent-routing` | 28エージェント定義 + ルーティングエンジン |
| `quality-gates` | コードレビュー、TDD、リリースチェック |
| `codex-suggestions` | Codex CLIへの委譲提案 |
| `gemini-suggestions` | Gemini CLIへの委譲提案 |
| `cli-logging` | CLI呼び出しログ |
| `route-audit` | ルーティング監査・KPIレポート |
| `issue-workflow` | GitHub Issue開発フロー |
| `cocoindex` | MCPサーバー自動プロビジョニング |
| `tmux-monitor` | サブエージェント監視（tmux表示） |

### 自動同期の仕組み

SessionStart Hookで`sync-orchestra.py`が起動し、ai-orchestraの最新状態をプロジェクトの`.claude/`に差分コピーする。

```
ai-orchestra/packages/ (ソース)
    ↓ SessionStart hook: sync-orchestra.py
.claude/ (プロジェクト)
    ├── agents/     ← 28エージェント定義
    ├── skills/     ← 全スキル
    ├── rules/      ← 全ルール
    └── config/     ← 設定ファイル（.local.yamlは保護）
```

同期の特徴:

* **差分コピー**: mtimeベースで変更されたファイルのみ同期（無変更時は約70ms）
* **ローカル保護**: `*.local.yaml`や`*.local.json`は同期の対象外（プロジェクト固有設定を保護）
* **Hook直接参照**: HookスクリプトはコピーせずAI\_ORCHESTRA\_DIRからのパス参照（常に最新版が実行される）
* **Facetビルド**: 同期時にFacetシステムによるSKILL.md / ルールの自動生成も実行

### Facetシステム──DRYなスキル・ルール管理

同じルールを複数のスキルに手動コピーすると、1箇所を修正するたびに全ファイルを更新する必要がある。Facetシステムはこの問題を解決する。

この仕組みはnrsさんの記事「[Faceted Prompting ── 肥大化したプロンプトを5つの関心で分解する](https://zenn.dev/nrs/articles/5d19b4c8a39ecb)」に着想を得ている。同記事ではモノリシックなプロンプトをPersona・Policy・Instruction・Knowledge・Output Contractの5つの関心に分離するアーキテクチャを提案しており、ai-orchestraではこの考え方をClaude Codeのスキル・ルール管理に応用した。

3種類の部品を組み合わせてスキルやルールを自動生成する仕組みである。

```
facets/
├── policies/           ← 共有Policy（複数スキル・ルールで再利用）
│   ├── cli-language.md      # 外部CLIとの言語プロトコル
│   ├── code-quality.md      # コード品質の共通ルール
│   ├── dialog-rules.md      # 対話ルール
│   └── factual-writing.md   # 事実に基づいた記述ルール
│
├── output-contracts/   ← 共有Output Contract（出力形式の標準化）
│   ├── tiered-review.md     # Critical/High/Medium/Lowの4段階レビュー形式
│   ├── compare-report.md    # 比較レポート形式
│   └── deep-dive-report.md  # 詳細分析レポート形式
│
├── instructions/       ← スキル・ルール固有のInstruction
│   ├── review.md
│   ├── startproject.md
│   └── ... (25個以上)
│
└── compositions/       ← 組み立て定義YAML
    ├── review.yaml
    └── startproject.yaml
```

Composition YAMLでどの部品を組み合わせるかを定義する。

```
# compositions/review.yaml
target: skill
name: review
policies:
  - cli-language
output_contracts:
  - tiered-review
instruction: review
```

`facet build`を実行すると、Policy + Output Contract + Instructionが結合されたSKILL.mdが自動生成される。Policyを1箇所修正すれば、参照する全スキルに反映される。

### セットアップ

新しいプロジェクトにai-orchestraを導入するには以下のコマンドを実行する。

```
# インストール
uv tool install orchex

# プロジェクトへのセットアップ（全パッケージ）
orchex setup all --project /path/to/project

# 最低限のパッケージのみ
orchex setup essential --project /path/to/project
```

以降はClaude Code起動時にSessionStart Hookが自動同期を行うため、明示的な操作は不要となる。

---

## まとめ──ハーネス設計のステップバイステップ

AIハーネスエンジニアリングは「プロンプトを毎回書く」から「環境を一度設計する」へのパラダイムシフトである。

段階的に導入する場合は、以下の順序を推奨する。

**Step 1: CLAUDE.mdを書く**

プロジェクト概要、ディレクトリ構造、テストコマンドをCLAUDE.mdに書く。これだけでClaude Codeの出力品質は大幅に向上する。

**Step 2: Rulesを分割する**

コーディング規約やワークフローのルールを`.claude/rules/`に分割する。CLAUDE.mdを簡潔に保ちつつ、詳細なルールを独立管理できる。

**Step 3: Hooksで自動化する**

繰り返し行う確認作業をHooksで自動化する。SessionStartでの環境初期化、PreToolUseでのガードレール、PostToolUseでの自動整形などから始めるとよい。

**Step 4: Agent Routingを設計する**

サブエージェントとCLIツール（Codex / Gemini）のルーティングを設定ファイルで一元管理する。タスクの種類に応じた最適なツール選択を自動化する。

**Step 5: パッケージ化して再利用する**

複数プロジェクトで同じハーネスを使う場合は、ai-orchestraのようなオーケストレーションシステムで統合管理する。

ハーネスの設計に正解は1つではない。自身のプロジェクトとワークフローに合わせて、少しずつ育てていくものである。この記事が、Claude Codeの真の能力を引き出すための出発点になれば幸いだ。

---

**関連記事:**
