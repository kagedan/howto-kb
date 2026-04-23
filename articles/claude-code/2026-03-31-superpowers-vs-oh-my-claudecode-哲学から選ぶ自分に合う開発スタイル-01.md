---
id: "2026-03-31-superpowers-vs-oh-my-claudecode-哲学から選ぶ自分に合う開発スタイル-01"
title: "superpowers vs oh-my-claudecode — 哲学から選ぶ、自分に合う開発スタイル"
url: "https://zenn.dev/dk_/articles/26f88c8ae89864"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-03-31"
date_collected: "2026-04-01"
summary_by: "auto-rss"
---

## はじめに

Claude Codeのプラグインエコシステムが急速に充実してきています。その中でも特に注目を集めているのが **superpowers**（obra/superpowers）と **oh-my-claudecode**（Yeachan-Heo/oh-my-claudecode）の2つです。

どちらもClaude Codeの能力を大幅に拡張するプラグインですが、**目指している方向が異なります**。単なる機能比較ではなく、両者の「哲学」から理解することで、自分の開発スタイルに本当に合うほうを選べるようになります。

この記事では、備忘録としてClaude Codeをすでに使っている状態を想定し両者を多角的に比較します。

---

## 2つのプラグインの概要

### superpowers（obra/superpowers）

<https://github.com/obra/superpowers>

> "A complete software development workflow for your coding agents"

Jesse Vincent（obra）氏が作成。**スキルベースの開発メソドロジー**に特化したプラグインです。

* ⭐ GitHub Stars: 約120k
* 言語: Shell / JavaScript
* 対応エージェント: Claude Code、Cursor、Codex、OpenCode、Gemini CLI（マルチプラットフォーム）

### oh-my-claudecode（Yeachan-Heo/oh-my-claudecode）

<https://github.com/yeachan-heo/oh-my-claudecode>

> "A weapon, not a tool"

クオンツトレーダーのYeachan Heo氏が作成。**マルチエージェントオーケストレーション**に特化したプラグインです。

* ⭐ GitHub Stars: 約1.8k（急成長中）
* 言語: TypeScript
* 対応エージェント: Claude Code（メイン）+ Gemini CLI / Codex をワーカーとして活用

---

## 哲学・コンセプトの違い

ここが最大の差異です。

### superpowers：「プロセスの体系化」

superpowersの核心は「**エージェントに正しい開発プロセスを踏ませること**」です。

SKILL.mdというMarkdownファイルで「スキル」を定義し、エージェントが特定の状況を検知すると自動でそのスキルを参照・実行します。スキルは「いつ使うか（`when_to_use`）」が定義されており、明示的な呼び出しなしに動きます。

```
# SKILL.mdのフロントマター例
name: Root Cause Tracing
description: Systematically trace bugs backward through call stack
when_to_use: Bug appears deep in call stack but you need to find where it originates
```

強調されているのは：

* **TDD（テスト駆動開発）**: RED→GREEN→REFACTORサイクルを強制
* **YAGNI**: 必要なものだけ実装する
* **DRY**: 重複を排除する
* **Systematic over ad-hoc**: アドホックな対処より体系的なプロセスを

「エージェントに好き勝手やらせない」という発想です。

### oh-my-claudecode：「エージェントの火力を最大化する」

OMCのコンセプトは「**道具ではなく武器**」です。とにかくエージェントの自律実行能力と並列処理を極限まで高めることに主眼を置いています。

Claude Codeをオーケストレーター（指揮者）とし、Gemini CLIやCodexをtmuxペインで起動してワーカーとして動かす**真のマルチAIアーキテクチャ**が特徴です。

---

## 具体的なワークフローの違い

### superpowersのワークフロー

superpowersはプロジェクト開始から完了まで、以下のフローを自動で踏みます。

```
1. brainstorming
   └─ ゴールを対話的に引き出し、要件を明確化

2. using-git-worktrees
   └─ 承認後、新しいブランチで隔離されたワークスペースを作成

3. writing-plans
   └─ タスクを2〜5分単位に分解、ファイルパス・完全なコード・検証手順を含む計画を作成

4. subagent-driven-development
   └─ タスクごとにサブエージェントを起動
      → 2段階レビュー（仕様準拠チェック → コード品質チェック）

5. test-driven-development
   └─ RED→GREEN→REFACTORを強制

6. requesting-code-review
   └─ タスク間でのコードレビュー（重大な問題はブロック）

7. finishing-a-development-branch
   └─ テスト確認後、マージ/PR/廃棄の選択を提示
```

ポイントは「**エージェントに裁量を与えすぎない**」設計です。計画書は「判断力が乏しく、テストが嫌いな熱意だけある新人エンジニアでも従えるくらい明確に」書くよう指示されています。

### oh-my-claudecodeのワークフロー

OMCには複数の実行モードがあり、目的や状況に応じて使い分けます。

| モード | 説明 | キーワード例 |
| --- | --- | --- |
| **autopilot** | アイデアから動くコードまで完全自律実行 | `autopilot: タスク管理アプリを作って` |
| **ralph** | 完成まで自己ループし続ける（ボルダーは止まらない） | `ralph: 認証システムをリファクタリング` |
| **ultrawork** | 最大並列実行、積極的なエージェント委任 | `ulw エラーを全部直して` |
| **team** | Claude Code native teamsでN個のエージェントが協調 | `team 5:executor 全エラーを修正` |
| **deep-interview** | ソクラテス式の要件ヒアリング | `/deep-interview "タスク管理アプリを作りたい"` |
| **ralplan** | 合意形成しながらの反復計画 | `ralplan この機能` |

さらに、マルチAI連携が特徴的です：

```
# Claude（オーケストレーター）が指示を出し、各ワーカーが並行で動く
omc team 2:codex "セキュリティレビューをして"
omc team 2:gemini "UIレビューをして（1Mトークンコンテキストで）"
```

---

## スキル・エージェントの仕組みの深掘り

### superpowersのスキル設計

superpowersのスキルは「**Markdownで書かれたドキュメント＝実行可能な指示書**」です。

```
skills/
├── debugging/
│   ├── systematic-debugging/SKILL.md
│   └── root-cause-tracing/SKILL.md
├── testing/
│   └── test-driven-development/SKILL.md
├── collaboration/
│   ├── brainstorming/SKILL.md
│   ├── writing-plans/SKILL.md
│   └── subagent-driven-development/SKILL.md
└── meta/
    └── writing-skills/SKILL.md  ← スキル自体の書き方スキル
```

重要なのは **`writing-skills`** というスキルの存在です。「スキルを作るためのスキル」が組み込まれており、エージェント自身が新しいスキルを追加・改善していけるようになっています。

コミュニティ面では `superpowers-skills` リポジトリがあり、PRを通じてスキルを共有できます。また `superpowers-marketplace` でサードパーティのスキルセットもインストール可能です。

### oh-my-claudecodeのエージェント設計

OMCの19エージェントはドメイン別に分類されています。

**Build & Analysis系**

* `explore`（探索）/ `analyst`（分析）/ `planner`（計画）
* `architect`（設計）/ `debugger`（デバッグ）/ `executor`（実行）
* `code-simplifier`（コード簡略化）

**Review系**

* `security-reviewer` / `code-reviewer` / `critic`

**ドメインスペシャリスト**

* `designer` / `test-engineer` / `document-specialist`
* `tracer` / `scientist` / `git-master` など

さらに**モデルルーティング**が組み込まれており、タスクの複雑度によって自動でモデルが切り替わります：

* 設計・アーキテクチャ → Claude Opus
* 通常タスク → Claude Sonnet
* 簡単な参照・検索 → Claude Haiku

MCPツールも充実しており、LSP統合（ホバー情報・定義ジャンプ・型チェック）、AST Grep（構文的なコード検索・置換）、Pythonの永続的REPLなどが使えます。

---

## どちらを選ぶべきか

### superpowersが向いている人

* **開発プロセスそのものを改善したい**
  + 「エージェントが好き勝手やって結果がバラバラ」を解決したい
  + TDD・レビュー・計画といった工程を省略せずに進めたい
* **Claude Code以外も使う**（Cursor、Codex、Gemini CLIも対応）
* **スキルを自分でカスタマイズしたい**（Markdownを書けばOK）
* **シンプルに理解できる仕組みが好き**

### oh-my-claudecodeが向いている人

* **エージェントの自律実行能力を最大化したい**
  + とにかく「やっといて」でどんどん進めたい
  + 並列実行でスループットを上げたい
* **Claude + Gemini + Codexのマルチモデル構成に興味がある**
* **高度なオーケストレーション基盤をそのまま使いたい**（自前でゼロから作りたくない）
* **活発なアップデートを追いかけるのが苦じゃない**（リリース頻度が高い）

### 両方使うという選択肢

実は排他的ではありません。superpowersをベースの開発メソドロジーとして使いながら、特定の大規模タスクではOMCのralpやultraworkを使う、という組み合わせも理論上は可能です。

---

## まとめ

| 観点 | superpowers | oh-my-claudecode |
| --- | --- | --- |
| **コンセプト** | 開発プロセスの体系化 | エージェント火力の最大化 |
| **スキル定義** | Markdown（シンプル） | TypeScript（高機能） |
| **並列実行** | あり（サブエージェント） | あり（tmux + マルチAI） |
| **スキル数** | 15前後（コア） | 28スキル + 19エージェント |
| **マルチLLM** | なし（Claude等各自） | あり（Claude+Gemini+Codex） |
| **学習コスト** | 低〜中 | 中〜高 |
| **カスタマイズ性** | 高い（Markdown） | 高い（複雑） |
| **対応プラットフォーム** | 幅広い | Claude Codeメイン |
| **Stars** | 約120k | 約1.8k |

どちらが優れているかではなく、「**自分はエージェントにどう動いてほしいか**」によって答えが変わります。

* **プロセスを制御したい** → superpowers
* **火力を解放したい** → oh-my-claudecode

Claude Codeをただのコード補完ツールとして使うのではなく、開発ワークフロー全体を変えていくその方向性はどちらも同じではあるのでより自身の開発環境や目指すものに近いものを選んでは捨てていくという選択が今後も必要なのだろうなぁという思いです。

---

## 参考リンク
