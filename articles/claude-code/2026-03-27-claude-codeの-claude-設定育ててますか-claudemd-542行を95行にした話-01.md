---
id: "2026-03-27-claude-codeの-claude-設定育ててますか-claudemd-542行を95行にした話-01"
title: "Claude Codeの `.claude/` 設定、育ててますか？ — CLAUDE.md 542行を95行にした話と、自己診断スキルの作り方"
url: "https://qiita.com/kiyotaman/items/487f16cb54e018bf52eb"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "AI-agent", "qiita"]
date_published: "2026-03-27"
date_collected: "2026-03-28"
summary_by: "auto-rss"
---

## はじめに

Claude Codeを本格的に使い込んでいくと、`.claude/` ディレクトリが育っていく。rules、commands、agents、hooks。気がつけば充実した開発環境が出来上がる。

先日、以下の記事を書いたが、

しかし、ある日ふと気づく。**CLAUDE.md が542行ある。そしてその大半が、`.claude/rules/` や `.claude/commands/` に書いたことの繰り返しだ。**

この記事では、開発時にClaude Code設定を全面的に見直した実体験をもとに、`.claude/` ディレクトリの「育て方」と「メンテナンスの仕組み化」について書く。

## CLAUDE.md が肥大化する構造的な理由

### 最初は便利だった

CLAUDE.mdは最初、プロジェクト固有の知識をClaude Codeに伝える唯一の場所だった。コーディング規約、テストの実行方法、ブランチ戦略、エラー時の対処法……。全部ここに書いた。

### `.claude/` の機能が充実してきた

Claude Codeの進化に伴い、`.claude/` ディレクトリに専用の仕組みが増えた：

| 機能 | ファイル | 役割 |
| --- | --- | --- |
| **Rules** | `.claude/rules/*.md` | パスベースで自動ロードされるコーディング規約 |
| **Commands** | `.claude/commands/*.md` | `/test` `/quality` 等のスラッシュコマンド |
| **Agents** | `.claude/agents/*.md` | 特化型エージェント定義 |
| **Hooks** | `settings.json` | ファイル保存時のauto-format、secret検出、SQL injection防止 |
| **Permissions** | `settings.json` | コマンド実行の許可/拒否 |

これらは強力だ。`rules/backend.md` は `backend/**` のファイルを編集する時だけ自動でロードされる。hooksはClaude Codeが書き込むたびに自動で走る。CLAUDE.mdに全部書く必要はなくなった。

### でもCLAUDE.mdは減らない

**問題はここだ。** `.claude/` に機能を追加しても、CLAUDE.mdから対応する記述を消さない。結果、同じ情報が2箇所に存在する。

私たちのプロジェクトでは、こうなっていた：

| CLAUDE.mdのセクション | 行数 | 本来の提供元 |
| --- | --- | --- |
| Kagura Memory Cloud活用ガイド | ~110行 | `kagura_memory_usage_guide` ツール |
| コーディング規約 | ~25行 | `.claude/rules/backend.md` 等（自動ロード） |
| メモリ管理ベストプラクティス | ~60行 | ツール自体のガイド |
| エラー発生時の標準フロー | ~25行 | `.claude/commands/` で対応済み |
| 技術スタック詳細 | ~30行 | README.md / コードから判別可能 |
| 開発環境セットアップ | ~25行 | README.mdと重複 |

**542行のうち、CLAUDE.md固有の価値を持つ情報は100行未満だった。**

## 実際にやったこと

### CLAUDE.md: 542行 → 95行

残したのは、**他のどこにも書かれていない情報だけ**：

```
# Kagura Memory Cloud - Development Guide

## Overview（5行）
## Memory-First Development（10行）
  - recall before implementing, remember after
  - coding rules auto-loaded from .claude/rules/
## Development Workflow（10行）
  - Issue → branch → implement → PR
## Branch Strategy & Naming（15行）
## Commit Messages（15行）
## Quality Commands（15行）
## PR Rules（5行）
## References（10行）
```

重要なポイント：

1. **コーディング規約への言及は「`.claude/rules/` を見て」の1行だけ**。ルールは `backend/**` 編集時に自動ロードされるので、CLAUDE.mdに書く必要がない。
2. **テストコマンドは `make test-local` の1行**。詳細は `/test` コマンドが知っている。
3. **MCP toolの使い方は「`kagura_memory_usage_guide` を呼んで」の1行**。ツール自体がガイドを持っている。

### OSS向けの整備

CLAUDE.mdだけでなく、周辺のドキュメントも整理した：

| 変更 | Before | After |
| --- | --- | --- |
| **PRテンプレート** | 日本語版(大文字)と英語版(小文字)が競合 | 英語版に統一 |
| **Issueテンプレート** | 全て日本語 | 英語化 + 簡素化 |
| **README.md** | 削除済みBilling機能を参照 | クライアント設定ガイド拡充（Claude Code/Gemini CLI/ChatGPT） |
| **PRテンプレート** | `/review-pr` (存在しないコマンド) を参照 | `/review` (実在するPRコメントトリガー) に修正 |

**全体で -708行 / +186行。** ドキュメント量を半分以下にして、情報の鮮度と正確性を上げた。

## 問題は「その後」だった

ドキュメントを整理して満足していたが、ふと思った。

**この整理の結果、`.claude/` の各ファイルが本当にコードベースの現状と合っているのか？**

CLAUDE.mdは手動で整理できる。しかし `.claude/rules/backend.md` が参照しているimportパスが、リファクタで変わっていたら？ `/quality` コマンドが個別のlintコマンドを列挙しているが、Makefileにまとめたターゲットがあることを知らなかったら？

**CLAUDE.mdの重複は目に見える腐敗だった。`.claude/` 内部の不整合は目に見えない腐敗だ。**

## `/self-maint` — Claude Codeに自己診断させる

そこで作ったのが `/self-maint` スキルだ。`.claude/` 配下の全設定をコードベースの現状と照合し、不整合を検出するスラッシュコマンド。

### 6つの監査ステップ

```
1. Rules Audit      — ルールの参照先がコードに存在するか
2. Commands Audit   — コマンドのCLI参照が動くか
3. Agents Audit     — エージェント定義がプロジェクト構造と一致するか
4. Hooks Audit      — hookスクリプトが存在し、パターンが網羅的か
5. Permissions Audit — 許可リストに過不足がないか
6. CLAUDE.md Check  — CLAUDE.mdと.claude/の一貫性
```

### 実際に見つかったfinding

整理直後に `/self-maint` を実行してみた。整理したばかりなのだから問題はないはず……と思ったら、こうだった：

| # | Severity | Issue |
| --- | --- | --- |
| 1 | Warning | `/quality` が個別コマンドを列挙。Makefileに `make lint` `make type-check` が存在するのに未使用 |
| 2 | Warning | `/test` が `python -m pytest` を直接実行。`make test-local` と二重管理 |
| 3 | Warning | `/self-review` だけが日本語。他の全commands/rules/agentsは英語化済み |
| 4 | Warning | `rules/backend.md` が「No `print()`」を禁止。しかしdocstring例示の `print()` が4ファイルに存在（実害なし） |

**整理した直後なのに4件。** つまりこれは「丁寧に作業しても見落とす」類のものだということ。

### 設計上の割り切り

`/self-maint` は**チェックリストであって、テストスイートではない**。

「何をチェックするか」をMarkdownで記述し、「どうやってチェックするか」はClaude Codeの判断に委ねている。これは意図的な設計だ。

**弱点：** 再現性がない。2回実行して結果が変わることがある。

**強み：** 文脈を理解した判断ができる。docstring内の `print()` を「これは例示で実害なし」と判断できるのは、静的解析ツールにはできない。

### 2段階フロー

```
/self-maint
  ↓
[監査: 全ファイル読み取り + grep + 照合]
  ↓
[結果テーブル表示]
  ↓
ユーザー: 「全部直して」
  ↓
[修正適用]
```

自動修正しない。`.claude/` の変更はプロジェクト全体のAI体験を変えるので、開発者が確認してから適用する。

## `.claude/` メンテナンスの原則

この作業を通じて得た教訓をまとめる。

### 原則1: 情報は1箇所に

CLAUDE.mdと `.claude/rules/` に同じことを書かない。**情報の正規の置き場所を1つ決めて、他からは参照だけする。**

```
CLAUDE.md   → ワークフロー、ブランチ戦略、コミット規約
rules/      → コーディング規約（パスベースで自動ロード）
commands/   → 繰り返し実行する手順（/test, /quality）
agents/     → 特化型タスク定義（code-reviewer, test-runner）
settings.json → hooks, permissions
```

### 原則2: 「壊れないもの」ほど腐る

壊れたら気づく設定（tsconfig, pyproject.toml）は自然にメンテされる。**壊れても気づかない設定（`.claude/rules/`）は放置される。**

| 設定 | 腐敗 → | 検出 |
| --- | --- | --- |
| `tsconfig.json` | ビルドエラー | CI ✅ |
| `.eslintrc` | lint警告 | CI ✅ |
| **`.claude/rules/`** | **古いパターンを提案し続ける** | **なし** ❌ |
| **`.claude/commands/`** | **壊れたコマンドを実行** | **なし** ❌ |

`/self-maint` は「なし」を「不完全だが存在する」に変える。

### 原則3: Makefileと二重管理しない

`.claude/commands/` の中で個別コマンドを列挙するのではなく、Makefileターゲットを呼ぶ。こうすれば、Makefileを更新するだけで `/quality` や `/test` の挙動も変わる。

```
# Before（二重管理）
1. cd backend && ruff check src/ tests/
2. cd backend && ruff format --check src/ tests/
3. cd backend && pyright src/

# After（Makefileに委譲）
1. make lint
2. make type-check
```

### 原則4: 定期的に `/self-maint`

* **大きなリファクタリング後** — importパスやファイル構造が変わった時
* **新しい技術追加後** — 新言語やフレームワークが入った時
* **月1回の定期メンテ** — ルーティンに組み込む

## `/self-maint` スキルの実装

コピーして `.claude/commands/self-maint.md` に置くだけで使える：

```
---
description: Audit and maintain .claude/ configuration
             (commands, agents, rules, hooks, settings)
---

Perform a full audit of the `.claude/` directory against
the current codebase state. Report all findings, then ask
which fixes to apply.

## Audit Steps

### 1. Rules Audit (.claude/rules/)
- Verify referenced imports, packages, patterns still exist
- Check if new patterns have emerged that rules don't cover
- Verify forbidden patterns are not present in the code

### 2. Commands Audit (.claude/commands/)
- Verify CLI commands work (make targets, npm scripts)
- Check MCP tools and parameters match current API
- Verify file paths and tool references are valid

### 3. Agents Audit (.claude/agents/)
- Verify file paths, test patterns, tech stack descriptions
- Check consistency with current project structure

### 4. Hooks Audit (settings.json)
- Verify hook scripts exist and are executable
- Check file pattern matchers cover current file types
- Check secret detection patterns are comprehensive

### 5. Permissions Audit (settings.json)
- Check if allowed commands reference installed tools
- Check if needed commands are missing from allowlist

### 6. CLAUDE.md Consistency Check
- Verify CLAUDE.md references match .claude/ contents
- Flag drift between documentation and configuration

## Output Format

| # | Severity | File | Issue | Proposed Fix |
|---|----------|------|-------|-------------|

After presenting findings, ask which fixes to apply.
Do not modify settings.local.json (user-specific).
```

## まとめ

Claude Codeの `.claude/` ディレクトリは強力だ。rules、commands、agents、hooks — 使いこなせばプロジェクト固有の開発体験を作れる。

しかしこれらの設定は、**コードベースと一緒に育てないと静かに腐る**。CLAUDE.mdの肥大化は目に見える症状だが、`.claude/rules/` の参照切れや `/quality` コマンドの二重管理は、気づかないまま何週間も放置される。

3つのアクション：

1. **CLAUDE.mdを見直す** — `.claude/rules/` と重複していないか？残す価値のある情報は何か？
2. **Makefileに委譲する** — コマンド定義で個別CLIを列挙しない
3. **`/self-maint` を入れる** — 73行のMarkdown。コピーして置くだけ

`.claude/` の設定が5つ以上あるなら、今日 `/self-maint` を試してみてほしい。最初は何も見つからないかもしれない。でも数ヶ月後、確実に価値を発揮する。
