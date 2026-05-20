---
id: "2026-05-19-claude-code-の-claude-設定を育てた話-01"
title: "Claude Code の .claude 設定を育てた話"
url: "https://zenn.dev/cutlet_of_pork/articles/db6a3837e1eaee"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "prompt-engineering", "API", "AI-agent"]
date_published: "2026-05-19"
date_collected: "2026-05-20"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Code を使い始めて数ヶ月、気づけば `~/.claude/` ディレクトリが **53個のスキル・12個のエージェント・15個以上の環境別ルール** を持つ「自律開発インフラ」になっていた。

この記事では、筆者が実際に運用している `.claude` 設定の全体像と、設計思想・ハマりどころを共有する。同じように「Claude Code をもっと使いこなしたい」という人の参考になれば幸いだ。

---

## 全体構成

```
~/.claude/
├── CLAUDE.md                 # コア原則（200行以内に厳守）
├── rules/                    # ルール集（自動読み込み）
│   ├── _core/                # 全セッション必須ルール（5ファイル）
│   ├── workflows/            # タスクタイプ別ワークフロー（13ファイル）
│   ├── tools/                # ツール使用ガイド（9ファイル）
│   ├── environments/         # 環境固有ルール（15ファイル）
│   └── team/                 # エージェントチーム運用（1ファイル）
├── skills/                   # スラッシュコマンド（53個）
├── agents/                   # カスタムエージェント定義（12個）
├── scripts/                  # Hookスクリプト
└── settings.json             # Claude Code 設定
```

---

## 設計の根本思想：「トークンは生鮮食品」

すべての設定の根底にある原則はひとつ。

**Claudeのトークンは「判断と編集」にのみ使う。調査・分析・検索は外部委任する。**

| 作業 | ツール |
| --- | --- |
| 1〜2ファイルの読み取り | **Claude 直接**（Read/Edit） |
| 300行超のファイル構造把握 | **Serena** `get_symbols_overview` |
| 50KB超のコードベース分析 | **Gemini CLI** `@構文` |
| Web検索 | **Gemini CLI**（WebSearch/WebFetch は禁止） |
| git commit/push | **Gemini CLI**（コミットメッセージ生成含む） |
| ライブラリAPIドキュメント | **Context7** |

これを「ハイブリッド委任原則」と呼んでいる。最初は「Serena/Gemini CLI に全部委任」としていたが、1〜2ファイルの単純操作に Serena を呼ぶのは逆にオーバーヘッドと気づき、現在の形に落ち着いた。

---

## CLAUDE.md の書き方：200行の壁

CLAUDE.md が長くなると、Claude は下のルールを無視し始める（Instruction Overload）。Anthropic 推奨は **400トークン程度**。

筆者の解決策は「ポインタ駆動 CLAUDE.md」：

```
## コア原則

**ABSOLUTE: Claudeのトークン節約はすべてのルールに優先する絶対原則。**
詳細: `~/.claude/rules/_core/token-efficiency.md`

## ツール委任原則
完全なタスク別ツールマトリクス: `~/.claude/rules/tools/mcp-servers.md`
```

CLAUDE.md はポインタのみ。詳細は `rules/` ディレクトリに分割して格納する。これにより、CLAUDE.md 自体のトークン消費を最小化しつつ、必要な情報は必要なときに参照できる構造になっている。

---

## rules/ ディレクトリ：知識を分類して管理

### \_core/（全セッション必須）

```
_core/
├── language.md         # 日本語・簡潔・会話的に
├── token-efficiency.md # トークン節約（絶対原則）
├── output-format.md    # マークダウン制限・LaTeX禁止
├── session-start.md    # セッション開始時の必須ワークフロー
└── system-prompting.md # CoT推論・構造化出力ルール
```

`session-start.md` が特に重要で、セッション開始時に以下を順番通り実行するよう定義している：

1. Serena でプロジェクトをアクティベート
2. claude-mem で過去の作業記録を検索
3. ライブラリ関連なら Context7 でドキュメント確認

### environments/（環境固有の落とし穴集）

Windows 環境で Claude Code を使う上での罠を丁寧に文書化したもの。

**windows-powershell.md** の教訓たち：

```
# ❌ Write ツールで ps1 を全文上書き → 1行化してParse Error
# ✅ Edit ツールで差分編集のみ

# ❌ Join-Path の3引数（PowerShell v5 では不可）
Join-Path $env:USERPROFILE '.claude' 'tmp'

# ✅ 文字列結合
"$env:USERPROFILE/.claude/tmp"
```

**pywinauto-winforms.md** では WinForms GUI 自動化の落とし穴を記録：

```
# ❌ UIA Invoke → COMError -2146233083
win.child_window(title='登録').click()

# ✅ 物理マウスクリック
win.child_window(title='登録').click_input()
```

こういった「実際にハマった罠」を都度 rules/ に追記し、次の Claude セッションで同じミスをしないようにしている。

---

## settings.json：自動化の核心

### 主要設定

```
{
  "model": "claude-sonnet-4-6",
  "effortLevel": "medium",
  "alwaysThinkingEnabled": false,
  "language": "japanese",
  "cleanupPeriodDays": 365,
  "env": {
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "80",
    "CLAUDE_CODE_AUTO_COMPACT_WINDOW": "400000",
    "CLAUDE_CODE_MAX_OUTPUT_TOKENS": "64000"
  }
}
```

`effortLevel: "medium"` は Pro プランでの推奨値。`high` 以上は数回で5時間ローリング上限に達するリスクがある。

`CLAUDE_CODE_AUTO_COMPACT_WINDOW: "400000"` は Context Rot 対策。1Mトークンモデルでも300〜400k付近からパフォーマンス劣化が始まるため、早めの自動コンパクトを設定している。

### Hooks 設定：システムレベルの品質担保

Hooks は CLAUDE.md のプロンプト指示と異なり、**強制力を持つ**。

```
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "powershell ... serena-auto-prime.ps1 -EventSource startup"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "bash ~/.claude/scripts/unc-path-check.sh" },
          { "type": "command", "command": "bash ~/.claude/scripts/block-main-push.sh" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          { "type": "command", "command": "bash ~/.claude/scripts/auto-format.sh" }
        ]
      },
      {
        "matcher": "",
        "hooks": [
          { "type": "command", "command": "bash ~/.claude/scripts/context-monitor.sh" }
        ]
      }
    ],
    "PostCompact": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command", "command": "bash -c 'cat ~/.claude/CLAUDE.md'" }
        ]
      }
    ]
  }
}
```

各 Hook の役割：

| Hook | スクリプト | 目的 |
| --- | --- | --- |
| SessionStart | `serena-auto-prime.ps1` | Serena の自動起動・プロジェクト選択 |
| PreToolUse(Bash) | `unc-path-check.sh` | UNCパス直接使用の検出・警告 |
| PreToolUse(Bash) | `block-main-push.sh` | main/master への force push をブロック |
| PostToolUse(Write/Edit) | `auto-format.sh` | Ruff/ESLint の自動実行 |
| PostToolUse(全て) | `context-monitor.sh` | コンテキスト使用率の監視 |
| PostCompact | inline | CLAUDE.md を自動再注入（圧縮後の指示消失を防ぐ） |
| Stop | `on-stop.sh` | セッション終了時の状態保存 |

---

## skills/：53個のスラッシュコマンド

スキルはユーザーが `/skill-name` と入力することで呼び出せるワークフローの塊。  
起動時は「名前と概要（約100トークン）」のみ読み込まれ、使うときだけ全文がロードされる遅延読み込み方式。

### 代表的なスキル

**`/bp-research`** — ベストプラクティス自動調査  
Gemini CLI を使って Zenn・Qiita・Reddit・HN を並列検索し、発見した知見を rules/ に自動反映してから git push まで行う。30日スロットリングつき。

**`/mem-checkpoint`** — セッション記録の保存  
重要な作業完了時に claude-mem へ観測を記録する。後のセッションで「前回どこまでやったか」をすぐ把握できるようになった。

**`/commit-push-pr`** — git ワークフロー一発完了  
Gemini CLI でコミットメッセージを自動生成し、確認後にコミット・プッシュ・PR 作成まで完結させる。

**`/ask-gemini`** — Gemini CLI への委任  
コードベースが 100KB を超える場合や、web 検索・diff レビューが必要な場合に Gemini CLI に処理を委任する。

**`/session-yolo-confirm`** — YOLO モード切り替え  
確認プロンプトなしで全操作を自動承認するモードへの切り替え。

### スキル設計の鉄則

`description` フィールドを正確に書くことが最重要。Claude はここだけを見てスキルを選択する：

```
---
name: commit-push-pr
description: |
  git commit・push・PR作成を一括実行するスキル。
  ユーザーが「コミットして」「プッシュして」「PRを作成して」と言った時に使用。
  Gemini CLIでコミットメッセージを自動生成する。
---
```

---

## agents/：12個のカスタムエージェント

サブエージェントとして呼び出せる特化型エージェント群。

| エージェント | 役割 |
| --- | --- |
| `tech-lead` | タスク分解・委任のオーケストレーター |
| `code-architect` | 設計レビュー（新機能追加前） |
| `build-validator` | ビルド・テスト・Lint の品質検証 |
| `code-simplifier` | 重複削除・可読性向上 |
| `security-auditor` | OWASP Top10 準拠の静的解析 |
| `test-writer` | TDD ベースのテスト作成 |
| `verify-app` | E2E 動作確認 |
| `gemini-researcher` | Web 検索・50KB超のコード分析 |
| `ui-designer` | AI Slop 排除・デザインシステム |
| `tech-debt-auditor` | 技術負債の特定・優先順位付け |
| `pdf-form-layout` | PDF フォーム座標自動分析 |
| `pdf-ocr-fixer` | PDF OCR 失敗の自律修正 |

### 実際の使い方

```
# PR 前フルチェック（並列実行）
Agent(subagent_type="security-auditor") + Agent(subagent_type="build-validator")

# TDD サイクル
test-writer（失敗テスト作成）→ 実装 → build-validator（パス確認）

# 大規模リファクタリング（必ず worktree 隔離）
Agent(isolation: "worktree", subagent_type="tech-lead", prompt="...")
```

#### CRITICAL: ファイル削除事故防止

`isolation: "worktree"` なしで tech-lead に大規模変更を委任すると、エージェントが「不要と判断したファイル」を削除する事故が起きる（実際に発生した）。

```
# ✅ 安全なパターン
Agent(
  isolation="worktree",
  mode="auto",
  prompt="...既存ファイルを削除しないこと..."
)
```

---

## MCP サーバー構成

```
mcpServers:
├── serena            # コードベース操作（OSS・使用上限なし）
├── context7          # ライブラリドキュメント参照
├── playwright        # ブラウザ自動操作
├── github            # Issue/PR 管理
├── sqlite            # データベース操作
├── sequential-thinking  # 複雑問題の段階的推論
├── chrome-devtools   # ネットワーク監視・JS実行
└── fetch             # 既知URLのコンテンツ取得
```

Serena はオープンソースのコードベース操作 MCP。使用上限がないため積極的に活用できる。  
ファイル横断パターン検索・シンボルリネーム・メソッド全体の書き換えは Serena に任せる。

---

## 2層メモリシステム

### auto memory（環境固有）

`~/.claude/projects/<CWDエンコード>/memory/MEMORY.md` に自動注入される。セッション横断の作業記録・環境固有の落とし穴を管理。

### Serena memories（プロジェクト固有）

アーキテクチャ決定・バグ根本原因などを `write_memory` でプロジェクトに紐づけて保存。

### claude-mem（観測履歴）

claude-mem MCP プラグインを使い、タスク経緯・デバッグ過程・意思決定を時系列で記録。3層ワークフローで段階的に情報取得：

```
Layer 1: search（軽量インデックス）
Layer 2: timeline（時系列コンテキスト）
Layer 3: get_observations（完全詳細）
```

---

## 運用していて良かったこと

### 1. セルフ修正ルール

ユーザーから行動を修正された場合、即座に `~/.claude/rules/` の該当ファイルを更新することで、同じミスの繰り返しを防ぐ。Claude Code を「育てる」感覚に近い。

### 2. Gemini CLI との役割分担

Claude は実装・編集専門、Gemini は調査・分析専門と役割を明確に分けることで、Claude のコンテキストをコードの「判断と編集」に集中させられる。

```
# Web検索は全てGemini CLIへ（--skip-trustはBash自動化で必須）
gemini --skip-trust -p "質問" -o text 2>/dev/null
```

### 3. /rewind の活用

Claude が間違ったアプローチを取った場合、修正するより **rewind** が正解。

```
# ❌ 「それはダメ、代わりにXを試して」→ 失敗した試みがコンテキストに残り汚染
# ✅ ダブルEsc または /rewind → 失敗を完全除去してから再プロンプト
```

---

## ハマりどころと解決策

### PowerShell の ps1 ファイル問題

Write ツールで ps1 ファイルを全文上書きすると改行が `\r\n` リテラルになって1行化する。常に Edit ツールで差分編集する。

### Gemini CLI の `--skip-trust` 必須

Claude Code の Bash ツールから Gemini CLI を呼ぶ場合は `--skip-trust` が必須。省略すると exit 55 で失敗する。これをスキル・ルールに徹底反映するのに半日かかった。

### Context Rot（コンテキスト腐敗）

1M トークンモデルでも 300〜400k 付近からモデルパフォーマンスが劣化する。`CLAUDE_CODE_AUTO_COMPACT_WINDOW=400000` を設定し、早めの自動コンパクトで対処している。

### エージェントへのファイル削除事故

前述の通り、`isolation: "worktree"` なしで大規模変更をエージェントに委任すると予期せぬファイル削除が発生する。必ず worktree 隔離を使い、指示に「既存ファイルを削除しないこと」を明示する。

---

## まとめ

Claude Code の `.claude` 設定を本気で育てると、こうなる：

* **CLAUDE.md** はポインタのみ（200行以内）
* **rules/** に環境固有の落とし穴を蓄積（実際にハマった罠のみ記録）
* **skills/** でよく使うワークフローをスラッシュコマンド化（53個）
* **agents/** で特化型エージェントチームを編成（12個）
* **Hooks** でシステムレベルの品質担保（フォーマット・ブロック・監視）
* **トークン節約** を絶対原則に、Gemini CLI・Serena・Context7 と役割分担

「AIに全部やらせる」より「AIの強みを引き出す設計をする」の方が圧倒的に効果的だった。

設定は GitHub で管理しており、複数端末で `git pull` するだけで同期できる体制にしている。

---

## 参考
