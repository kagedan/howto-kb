---
id: "2026-04-13-claudeとcopilot-codexを組み合わせたaiコードレビューワークフローtakt-01"
title: "ClaudeとCopilot Codexを組み合わせたAIコードレビューワークフロー（takt）"
url: "https://zenn.dev/acntechjp/articles/ca8a99ee0530f0"
source: "zenn"
category: "ai-workflow"
tags: ["API", "zenn"]
date_published: "2026-04-13"
date_collected: "2026-04-14"
summary_by: "auto-rss"
---

> **この記事はAIの支援を受けて執筆しています。**

## はじめに

「Claude にコードを書かせ、Codex にレビューさせる」という構成は、異なるモデルによる外部視点が得られるとして注目されています。この組み合わせ自体はシンプルですが、実際に運用しようとすると **「どうやって2つのモデルをつなぐか」** というハーネス選びが課題になります。

いくつかのオーケストレーションツールを検討した中で、もう一つ制約がありました。手元の環境では **Codex の API を直接呼び出せず、GitHub Copilot 経由でのみ Codex が使える**状況だったのです。

この条件にマッチしたのが **[takt](https://github.com/nrslib/takt)** です。takt は Claude と Copilot を同じワークフロー内のステップに混在させられるため、今回の構成にそのまま当てはめることができました。

この記事では、takt を使ってこのワークフローを組む方法と、実際に詰まったポイントを共有します。

---

## 事前準備

### 必要なもの

| ツール | 用途 |
| --- | --- |
| Node.js 20+ | takt の動作要件 |
| Claude Code CLI | Claude ステップの実行エンジン |
| GitHub Copilot サブスクリプション | Copilot ステップの利用に必要 |
| GitHub Fine-grained PAT | takt から Copilot API を呼び出すためのトークン |

### Node.js のセットアップ

```
# nvm 経由で Node 20 をインストール
nvm install 20
nvm use 20

# takt インストール
npm install -g takt
```

### Claude Code CLI のセットアップ

takt は Claude ステップを `claude -p` サブコマンドで実行します。  
インストールと認証が済んでいることを確認してください。

### Copilot トークンの設定

takt から Copilot を呼び出すには Fine-grained PAT が必要です。  
詳細は後述の「詰まりポイント③」を参照してください。

---

## takt とは

takt は YAML でワークフローを定義し、複数の AI エージェント（Claude / Copilot / OpenAI など）を  
ステップごとに呼び出せる AI オーケストレーションツールです。

* 各ステップに「ペルソナ（役割定義）」「ポリシー（規約）」「ナレッジ（知識）」を注入できる
* ステップの遷移条件を自然言語で記述できる（例: 「レビュー結果が PASS なら次へ」）
* git worktree でタスクを分離して実行できる
* MIT ライセンス、Node.js 製

---

## ワークフロー全体像

今回構築したワークフローは 7 ステップです。

```
plan → implement → auto_check → code_review
                                    ↓ CRITICAL → fix_from_review → auto_check（最大3ループ）
                  integration_test → test_verify → report
                                       ↓ FAIL → fix_from_verify → integration_test（最大3ループ）
```

| ステップ | AIプロバイダー | モデル | 役割 |
| --- | --- | --- | --- |
| plan | Claude | Opus 4.6 | 仕様調査・タスク分解・実装計画 |
| implement | Claude | Sonnet 4.6 | コード実装 |
| auto\_check | Claude | Sonnet 4.6 | ruff / mypy / pytest |
| **code\_review** | **Copilot** | **Codex** | **汎用性・規約チェック（外部視点）** |
| fix\_from\_review | Claude | Sonnet 4.6 | CRITICAL 指摘の修正 |
| integration\_test | Claude | Sonnet 4.6 | 統合テスト・実環境確認 |
| **test\_verify** | **Copilot** | **Codex** | **テスト結果の検証（外部視点）** |
| fix\_from\_verify | Claude | Sonnet 4.6 | FAIL 指摘の修正 |
| report | Claude | Sonnet 4.6 | 結果集約・コミットメッセージ提案 |

**ポイント**: `code_review` と `test_verify` だけ Copilot（Codex）を使っています。  
実装した Claude 自身ではなく別モデルに「これは汎用的か？ハードコードはないか？」と問わせるのが狙いです。

---

## 設定ファイル

### `.takt/config.yaml`（ペルソナ別モデル設定）

```
language: ja
provider: claude
model: sonnet           # デフォルト

persona_providers:
  my-planner:
    provider: claude
    model: opus          # 計画は Opus で
  my-implementer:
    provider: claude
    model: sonnet
  my-code-reviewer:
    provider: copilot
    model: gpt-5.3-codex # レビューは Copilot Codex で
  my-test-verifier:
    provider: copilot
    model: gpt-5.3-codex
  my-reporter:
    provider: claude
    model: sonnet

provider_profiles:
  claude:
    default_permission_mode: edit
    step_permission_overrides:
      plan: readonly
      code_review: readonly
      test_verify: readonly
      report: readonly
  copilot:
    default_permission_mode: readonly

allow_git_hooks: true
auto_pr: false
base_branch: main
```

### `.takt/workflows/my-dev.yaml`（ワークフロー定義）

```
name: my-dev
initial_step: plan
max_steps: 50
interactive_mode: passthrough   # 起動時のデフォルト選択を passthrough に設定

workflow_config:
  runtime:
    prepare:
      - .takt/scripts/pre-check.sh  # 実行前の事前確認

loop_monitors:
  - cycle:
      - code_review
      - fix_from_review
    threshold: 3
    judge:
      persona: my-quality-checker
      rules:
        - condition: ループ回数が閾値を超えた
          next: ABORT

steps:
  - name: plan
    persona: my-planner
    model: claude-opus-4-5
    edit: false
    required_permission_mode: readonly
    instruction: plan
    rules:
      - condition: 計画が完成した
        next: implement
      - condition: 要件が不明確
        next: ABORT

  - name: implement
    persona: my-implementer
    model: claude-sonnet-4-5
    edit: true
    instruction: implement
    rules:
      - condition: 実装完了
        next: auto_check

  - name: auto_check
    persona: my-quality-checker
    edit: true
    instruction: auto-check
    rules:
      - condition: ruff・mypy・pytest が全て通過した
        next: code_review
      - condition: 3回の自動修正を試みたが失敗した
        next: ABORT

  - name: code_review
    persona: my-code-reviewer
    edit: false
    required_permission_mode: readonly
    instruction: code-review
    rules:
      - condition: レビュー結果が PASS
        next: integration_test
      - condition: レビュー結果に CRITICAL が含まれる
        next: fix_from_review

  # ... 以下 fix_from_review / integration_test / test_verify / report
```

---

## takt の起動モードを選ぶ

`takt` を実行すると、まず以下の 4 つのモードを選ぶメニューが表示されます。

| モード | 内容 |
| --- | --- |
| **assistant** | タスク内容についてClaudeと対話しながら指示を整理してからワークフローを開始（デフォルト） |
| **persona** | ワークフロー最初のステップのペルソナとして対話し、タスクを詰めてから実行 |
| **quiet** | 対話なし。タスク文字列をそのまま使ってすぐ実行するが、Claude が一度サマリーを生成 |
| **passthrough** | 対話なし。タスク文字列をそのまま渡して即実行（最もシンプル） |

今回は `passthrough` を使っています。  
CLI から `takt --workflow my-dev "〇〇機能を追加"` のように直接タスクを渡す運用であれば、  
AI との事前対話は不要なためです。

ワークフロー YAML に `interactive_mode: passthrough` と書くと、起動時のメニューが  
**スキップされ、自動的に passthrough モードで実行が始まります**。

```
takt --workflow my-dev "〇〇機能を追加する"
```

---

## 詰まりポイント① サンドボックスで docker が使えない

Claude Code にはサンドボックス機能（bubblewrap）があり、有効にすると  
`docker` などのシステムコマンドがブロックされます。  
takt はサブプロセスとして `claude -p` を起動するため、**ワークフロー内のステップから  
docker コマンドを直接実行しようとするとサンドボックスに阻まれます**。

### 解決策: スクリプトベースの実行

Claude に直接コマンドを構築させるのではなく、**あらかじめスクリプトを用意し、  
そのスクリプトのパスだけを許可リストに追加**するアプローチが安定します。  
許可リストに載ったスクリプト経由の実行はサンドボックスの制限を受けません。

```
// .claude/settings.json
{
  "permissions": {
    "allow": [
      "Bash(.takt/scripts/*)"
    ]
  }
}
```

インストラクションファイルでスクリプトを呼ぶよう指示:

```
<!-- .takt/facets/instructions/auto-check.md -->
以下のスクリプトで品質チェックを実行してください。

```bash
.takt/scripts/run-checks.sh
```

* "ALL CHECKS PASSED" で終了 → 次ステップへ
* 失敗した場合は指摘箇所を修正して再実行（最大3回）

```
スクリプト本体:

```bash
#!/usr/bin/env bash
# .takt/scripts/run-checks.sh
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

echo "=== lint ===" && uv run ruff check src/ tests/ --fix
echo "=== type check ===" && uv run mypy src/
echo "=== test ===" && uv run pytest --cov=myapp --cov-fail-under=80
echo "=== ALL CHECKS PASSED ==="
```

---

## 詰まりポイント② git worktree でスクリプトが消える

takt は **git worktree** を使ってタスクを別ディレクトリで実行します。  
worktree は git 管理下のファイルしか持ち込まないため、`.takt/scripts/` が  
`.gitignore` で除外されていると **worktree 内でスクリプトが見つからなくなります**。

### 解決策: scripts/ を git 管理対象にする

`.takt/.gitignore` で `*`（全除外）+ 明示的な許可という構成にしている場合、  
`scripts/` を明示的に許可する必要があります:

```
# .takt/.gitignore
*

# バージョン管理するもの
!.gitignore
!config.yaml
!workflows/
!workflows/**
!scripts/       # ← これを追加
!scripts/**     # ← これを追加
!facets/
!facets/**
```

また、スクリプト内で `docker compose ps` を使うと **worktree のディレクトリ名が  
プロジェクト名として解釈される**ため、コンテナが見つからないことがあります。  
`docker ps --format '{{.Names}}'` を使うほうが安全です:

```
# NG: worktree ディレクトリ名に依存する
docker compose ps myservice

# OK: コンテナ名で直接検索
CONTAINER=$(docker ps --format '{{.Names}}' | grep -i myservice | head -1)
```

---

## 詰まりポイント③ Copilot CLI の PAT 認証

`~/.takt/config.yaml` に `copilot_github_token` を設定する際、  
**Classic PAT（`ghp_` 始まり）は使えません**。copilot CLI v1.0.24 以降で明示的に拒否されます。

### 必要なもの: Fine-grained PAT

1. <https://github.com/settings/personal-access-tokens/new> を開く
2. **Repository access**: "No repositories" で OK
3. **Permissions** → **Copilot** → **Copilot Requests: Read** のみ選択
4. 生成されるトークン（`github_pat_` 始まり）を設定

```
# ~/.takt/config.yaml（リポジトリ外・git 管理外）
copilot_github_token: github_pat_xxxxxxxxxxxx
```

> **代替**: `gh copilot` コマンドで認証済みの場合は OAuth トークン（`gho_` 始まり）が  
> 自動的に使われるため PAT 設定は不要です。

---

## Copilot レビューに渡すインストラクション例

Codex による code\_review ステップには、汎用性チェックに特化した指示を渡しています:

```
<!-- .takt/facets/instructions/code-review.md -->
実装されたコードをレビューし、以下の観点で評価してください。

### チェック項目
1. **ハードコード検出**: パス・URL・マジックナンバーが定数・設定ファイル化されているか
2. **汎用性**: 特定のファイル名・環境に依存した書き方をしていないか
3. **型アノテーション**: Python であれば mypy strict 準拠か
4. **命名規則**: プロジェクトの規約に沿っているか

### 出力形式
- **CRITICAL**: 修正必須の問題（マージ前に対応が必要）
- **WARNING**: 改善推奨（対応は任意）
- **PASS**: 問題なし

最後に判定（CRITICAL / WARNING / PASS）を1行で明記してください。
```

---

## まとめ

| 課題 | 解決策 |
| --- | --- |
| 実装した AI 自身がレビューすると見落としが多い | Claude と Copilot（Codex）を別ステップに分ける |
| docker/uv コマンドの権限エラー | `.takt/scripts/` にスクリプトを置き `Bash(.takt/scripts/*)` だけ許可 |
| git worktree でスクリプトが消える | `.takt/.gitignore` で `scripts/` を明示的に許可 |
| Classic PAT で Copilot 認証エラー | Fine-grained PAT（Copilot Requests: Read）を使う |
| 起動モードの選択が毎回手間 | `interactive_mode: passthrough` でメニューをスキップして自動実行 |

ワークフローもそうですが、ナレッジを付与して実行させられるので  
思った解決と違うといったことが少ないように感じられました  
実行時間はネックですが、間違いがないのなら結構ありだと思います。

自動的にワークツリーでの実行になるので、複数実行などしてもよさそうですね。  
個人的にはテストがコンテナ内の動作でしかできず、複数実行だとぶつかるのでここをどうしようかと思案中です。  
はじめてTAKT触ったので間違っている部分あれば申し訳ございません。  
よきハーネスライフを！

---

## 参考
