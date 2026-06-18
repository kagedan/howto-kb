---
id: "2026-06-17-agentsmdにsopをシンボリックリンクしdesignmdでフロントを分離する-01"
title: "AGENTS.mdにSOPをシンボリックリンクし、DESIGN.mdでフロントを分離する"
url: "https://zenn.dev/zapabob/articles/agents-md-sop-design-symlink"
source: "zenn"
category: "claude-code"
tags: ["CLAUDE-md", "MCP", "AI-agent", "OpenAI", "Python", "TypeScript"]
date_published: "2026-06-17"
date_collected: "2026-06-18"
summary_by: "auto-rss"
query: ""
---

Codex を複数リポジトリで使うと、ルールが散らばります。プロジェクトごとに test コマンドが違う。フロントのデザイン規約は別ファイルにある。個人の文体や MCP 方針はマシン全体で共通にしたい。

この記事では、**PC 全体の `~/.codex/AGENTS.md`** と **リポジトリの `AGENTS.md`** を分け、後者から **SOP（標準作業手順）** と **DESIGN.md（フロント設計）** をシンボリックリンクで参照する構成を紹介します。

本書 [OpenAI Codex実践設計入門](https://zenn.dev/zapabob/books/openai-codex-design-book) の第3章を補う、実務向けのレイアウトです。

## 3層のドキュメント

| 層 | パス | 役割 |
| --- | --- | --- |
| グローバル | `~/.codex/AGENTS.md` | 全プロジェクト共通の原則（工学規律、スキル方針、個人ワークフロー） |
| リポジトリ | `./AGENTS.md` | この repo の Commands / Rules / Done |
| 参照ドキュメント | `docs/sop/*.md`, `docs/design/DESIGN.md` | 言語別 SOP・UI 規約（リンクまたは symlink） |

Codex CLI はリポジトリルートの `AGENTS.md` を `project_doc_fallback_filenames` で自動読み込みします。グローバル設定は `CODEX_HOME`（通常 `~/.codex`）側が適用されます。

詳細は [examples/global-vs-project.md](https://github.com/zapabob/codex-zenn-starter/blob/main/examples/global-vs-project.md) も参照してください。

## グローバル AGENTS.md に書くこと

マシン全体の `~/.codex/AGENTS.md` には、**リポジトリにコミットしない** 内容を置きます。

* 遵守すべき上位原則（例: 明示的な要件・検証可能な完了条件・秘密情報の非コミット）
* 文体やレビュー方針（チーム repo には載せない個人設定）
* スキル / MCP の利用優先順位
* 「SOP と DESIGN.md を必ず参照せよ」という **メタ規則**

先頭 1 行で上位原則を宣言するパターンがあります。

```
# ~/.codex/AGENTS.md（概念例・個人設定）

AGENTS.md / CLAUDE.md は SOP、MILSPEC 由来の規律、ソフトウェア工学のベストプラクティスに従うこと。

## Global rules
- 要件は曖昧語（「いい感じ」「適当」）を使わず、検証コマンドで閉じる。
- リポジトリの `docs/sop/` と `docs/design/DESIGN.md` を UI 作業前に読む。
- secrets・トークン・個人パスをコミットしない。
```

## MILSPEC 風の規律をソフトウェア工学に落とす

軍用規格（MILSPEC）をそのままソフトウェアに適用するのではなく、**エージェント向けに転用しやすい要素** だけを取り込みます。

| 考え方 | AGENTS.md / SOP での書き方 |
| --- | --- |
| 要求の明示 | Rules に禁止・許可を列挙（曖昧語を使わない） |
| 追跡可能性 | Done に「どのコマンドが通れば完了か」を書く |
| 検証 | Commands に test / lint / typecheck を固定 |
| 変更管理 | SOP にブランチ・PR・レビュー手順を 1 ページにまとめる |
| インタフェース分離 | フロントは DESIGN.md、バックエンドは SOP の言語別章 |

これは ISO/IEC 12207 やチームの Definition of Done と親和性があります。AGENTS.md は **エージェントが毎回読む要約**、SOP は **人間も読む詳細手順** と役割分担します。

## リポジトリ構成（推奨）

```
your-repo/
├── AGENTS.md                 # ルートに必須（Codex が読む入口）
├── docs/
│   ├── sop/
│   │   ├── engineering.md    # 共通（PR、レビュー、セキュリティ）
│   │   ├── python.md         # 言語別
│   │   ├── typescript.md
│   │   └── rust.md
│   └── design/
│       └── DESIGN.md         # UI・コンポーネント・トークン
├── src/
└── ...
```

### AGENTS.md（リポジトリ入口）

ルートの `AGENTS.md` は **短く** 保ち、詳細は SOP / DESIGN へ誘導します（32 KiB 上限を意識）。

```
# AGENTS.md

## Project
Next.js SaaS. See docs/design/DESIGN.md for UI.

## Commands
- Install: `npm ci`
- Test: `npm test`
- Lint: `npm run lint`
- Preview: `npm run dev`

## Rules
- Follow docs/sop/engineering.md for all changes.
- UI work: read docs/design/DESIGN.md before editing components.
- Python scripts: docs/sop/python.md
- Do not commit `.env` or secrets.

## Done
- `npm test` and `npm run lint` pass.
- UI changes match DESIGN.md tokens and layout rules.
```

## シンボリックリンクの使い方

Codex はリポジトリ内のファイルを読みに行けます。SOP を **別ファイルで管理しつつ、入口を一本化** する方法が 2 つあります。

### 方法 A: AGENTS.md は実体、SOP は Rules で参照（推奨）

* メンテが簡単で Windows / Linux 両方で確実
* 上記の「Rules でパスを明示」がこれ

### 方法 B: AGENTS.md を SOP 実体へ symlink

単一ファイルにまとめたい場合、ルート `AGENTS.md` を `docs/sop/AGENTS.full.md` へリンクします。

**Windows（管理者または Developer Mode）:**

```
# 既存 AGENTS.md を退避してから
New-Item -ItemType SymbolicLink `
  -Path AGENTS.md `
  -Target docs\sop\AGENTS.full.md
```

**Linux / macOS:**

```
ln -sf docs/sop/AGENTS.full.md AGENTS.md
```

## 言語別 SOP の例

`docs/sop/python.md`:

```
# Python SOP

## Toolchain
- Package manager: uv
- Test: pytest
- Lint: ruff

## Rules
- Type hints on public functions.
- No bare `except:`.
- Run `uv run pytest` before marking Done.
```

`docs/sop/typescript.md`:

```
# TypeScript SOP

## Toolchain
- Package manager: npm
- Test: vitest / jest（プロジェクトに合わせる）
- Lint: eslint

## Rules
- Strict TypeScript; no `any` without comment.
- Prefer existing components from docs/design/DESIGN.md.
```

エージェントは AGENTS.md の Rules 経由で該当 SOP を開きます。プロンプトに毎回「TypeScript では…」と書く必要が減ります。

## DESIGN.md（フロントエンド）

UI 規約は AGENTS.md と混ぜず **`docs/design/DESIGN.md`** に分離します。

```
# DESIGN.md

## Stack
- Next.js App Router, Tailwind CSS, shadcn/ui

## Tokens
- Primary: `hsl(222 47% 11%)`
- Radius: `0.5rem` default
- Font: system-ui, "Noto Sans JP" for Japanese

## Layout
- Max content width: 72rem
- Mobile-first; breakpoints follow Tailwind defaults

## Components
- Use `Button` from `@/components/ui/button`
- No inline styles for spacing; use Tailwind utilities

## Accessibility
- Interactive elements need focus ring
- Images require `alt` text
```

バックエンドのみの repo では DESIGN.md は不要です。モノレポなら `apps/web/docs/design/DESIGN.md` のようにアプリ単位で置きます。

## Codex 設定との組み合わせ

```
# .codex/config.toml（リポジトリまたは ~/.codex）
project_doc_fallback_filenames = ["AGENTS.md"]
project_doc_max_bytes = 32768
approval_policy = "on-request"
sandbox_mode = "workspace-write"
```

グローバルとリポジトリの両方に AGENTS.md がある場合、**リポジトリの Commands / Done が優先** され、グローバルは横断的な Rules を補います。矛盾させないよう、グローバルには「repo の AGENTS.md を上書きしない」旨を書いておくと安全です。

## チェックリスト

## テンプレート

[codex-zenn-starter](https://github.com/zapabob/codex-zenn-starter) の `examples/` に以下を追加しています。

| ファイル | 用途 |
| --- | --- |
| `examples/docs/sop/engineering.md` | 共通 SOP |
| `examples/docs/design/DESIGN.md` | フロント設計例 |
| `examples/AGENTS.md.with-sop-design.md` | SOP / DESIGN 参照付き AGENTS.md |

## おわりに

AGENTS.md はプロンプトの置き場ではなく、**検証可能な開発契約** です。SOP で手順を、DESIGN.md で見た目を分離し、グローバル AGENTS.md でマシン横断の規律を載せると、Codex の作業は再現しやすくなります。

次の一歩は、今のリポジトリに `docs/sop/engineering.md` を 1 枚だけ追加し、AGENTS.md の Rules から参照することです。
