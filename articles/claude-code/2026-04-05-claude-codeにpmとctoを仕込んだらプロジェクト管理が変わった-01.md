---
id: "2026-04-05-claude-codeにpmとctoを仕込んだらプロジェクト管理が変わった-01"
title: "Claude Codeに「PM」と「CTO」を仕込んだら、プロジェクト管理が変わった"
url: "https://qiita.com/kiyotaman/items/4a9523badbc08af35a93"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "qiita"]
date_published: "2026-04-05"
date_collected: "2026-04-06"
summary_by: "auto-rss"
---

## TL;DR

Claude Codeのカスタムスラッシュコマンドで `/pm`（プロダクトマネージャー）と `/cto`（技術責任者）を定義した。`.md` ファイル2つ置くだけ。

* `/pm` — マイルストーンの一貫性、リリース順序、イシュー優先度を分析
* `/cto` — 技術的負債、アーキテクチャリスク、ドキュメント健全性、バグ状況を診断

分析はAI、判断は人間。この分離が肝。

**関連記事**

## 背景：1人開発でもプロジェクト管理は崩れる

OSSや個人開発でありがちな状態：

```
v0.8.0 "Integration, Connectivity & Docs"
├── #18  context sync export/import
├── #19  webhook notifications
├── #46  resource MCP tools
├── #47  resource UI
├── #104 sleep admin UI        ← これ Integration か？
├── #135 docs overhaul         ← これも？
└── #152 timezone fix (bug)    ← バグが混ざってる
```

7件のイシューに一貫性がない。「色々やりました」リリースになる。

問題は **判断基準が頭の中にしかない** こと。PMがいればトリアージしてくれるが、1人開発にPMはいない。CTOもいない。技術的負債は「後でやる」に溜まり続ける。

## 解決策：判断基準をスラッシュコマンドにする

`~/.claude/commands/` に `.md` ファイルを置くと、どのリポジトリからでも使えるグローバルコマンドになる。

### `/pm` — プロダクトマネージャー

```
---
description: Product manager analysis — milestone triage, issue prioritization, release planning
arguments:
  - name: repo
    description: "Target repo (e.g., owner/repo). Defaults to current repo."
    required: false
---

Analyze the project's milestones and open issues from a product manager perspective.

## Steps

### 1. Gather current state

Run in parallel:
- `gh issue list --repo $REPO --state open --json number,title,milestone,labels,createdAt`
- `gh api repos/$REPO/milestones?state=open`
- `gh api repos/$REPO/milestones?state=closed --jq '.[] | "\(.number) \(.title)"'`

If $ARGUMENTS provides a repo, use it. Otherwise use the current repo.

### 2. Analyze each milestone

For each open milestone, evaluate:
- **Theme coherence**: Do the issues tell a single story? Or is it a grab bag?
- **Size**: Is the milestone overloaded (>6 issues) or too thin (<2)?
- **Dependencies**: Are there issues that block others across milestones?
- **Unassigned issues**: Are there open issues with no milestone?

### 3. Evaluate release ordering

Apply these PM principles in order of priority:
1. **Trust before integration** — Users must trust the core before connecting it to other systems
2. **Control before automation** — Give users visibility and manual control before adding more automation
3. **Bugs before features** — Ship fixes first, don't let them accumulate across milestones
4. **Coherent narrative per release** — Each release should have a one-sentence theme
5. **Minimize WIP** — Prefer fewer, focused milestones over many scattered ones

For technical health analysis (tech debt, refactoring, architecture), use `/cto` instead.

### 4. Present findings

- Current State (milestones, issue counts, themes)
- Issues Found (incoherence, overloaded milestones, ordering problems)
- Proposed Reorganization (table with milestone → theme → issues)
- Recommended Actions

### 5. Execute (with confirmation)

Ask the user before executing any changes.
Do NOT move issues or modify milestones without explicit approval.
```

### `/cto` — 技術責任者

```
---
description: CTO-level technical health review — tech debt, architecture, refactoring priorities
arguments:
  - name: repo
    description: "Target repo (e.g., owner/repo). Defaults to current repo."
    required: false
---

Analyze the project's technical health from a CTO perspective.

## Steps

### 1. Gather current state

Run in parallel:
- `gh issue list --repo $REPO --state open --json number,title,milestone,labels,createdAt`
- `gh issue list --repo $REPO --state open --label bug --json number,title,milestone,createdAt`
- `gh issue list --repo $REPO --state open --search "refactor OR tech-debt OR deprecat"`
- `git log --oneline -30` (if in repo)

### 2. Tech debt assessment

- **Debt accumulation**: How many refactor/tech-debt issues exist?
- **Debt distribution**: Concentrated or spread?
- **Debt age**: Oldest refactor issues — stale debt signals avoidance
- **Debt-to-feature ratio**: >30% per milestone = already behind

### 3. Architecture risk analysis

- **Breaking changes queued**: API changes, migrations, deprecations
- **Cross-cutting concerns**: Issues touching multiple modules
- **Dependency risks**: Supply chain, version pinning, CVEs

### 4. Documentation health

- **Doc-feature gap**: Features shipped without docs
- **Stale docs**: `docs:` issues older than 30 days
- **API docs**: Public APIs documented? Breaking changes communicated?
- **Onboarding path**: Could a new contributor get started from docs alone?

### 5. Bug health

- **Bug velocity**: Closed faster than opened?
- **Bug age**: Any becoming chronic?
- **Bugs without milestones**: Triage gaps

### 6. Apply CTO principles

1. **Debt compounds** — 3+ refactor issues without milestone = schedule debt sprint
2. **Breaking changes need coordination** — Group into single release with migration guides
3. **Chronic bugs erode trust** — >30 days old needs a decision: fix, wontfix, or downgrade
4. **Docs are part of the product** — Features without docs are half-shipped
5. **Architecture before features** — Cross-cutting concerns piling up = pause features
6. **Dependencies are liabilities** — Flag CVEs or incident-pinned deps

### 7. Present findings

- Technical Health Summary (overall rating, debt count, bug posture)
- Tech Debt Inventory (table: issue → area → age → milestone)
- Documentation Health
- Architecture Risks
- Recommendations

### 8. Cross-reference with PM view

If `/pm` was run, cross-reference:
- Milestones balanced between features and debt paydown?
- Release order sustainable from technical perspective?

Analysis only — do NOT execute changes without approval.
```

## なぜ2つに分けるのか

PMとCTOは**見ているものが違う**。

|  | `/pm` | `/cto` |
| --- | --- | --- |
| 問い | 何を・いつ出すか | 技術的に持続可能か |
| 判断軸 | ユーザー価値、テーマ一貫性 | 負債、リスク、品質 |
| 対象 | マイルストーン、イシュー順序 | コード、依存、ドキュメント |
| 衝突例 | 「機能を早く出したい」 | 「負債を先に返したい」 |

1つのスキルに混ぜると、**両方の視点が中途半端になる**。分けておいて、両方の結果を見て人間が最終判断するのが正しい設計。

実際の運用フロー:

```
/pm kagura-ai/memory-cloud    ← マイルストーン分析
/cto kagura-ai/memory-cloud   ← 技術健全性チェック

→ 両方の結果を見て、リリース計画を確定
```

## 実際に使ってみた結果

### `/pm` の分析

> v0.8.0が「Integration, Connectivity & Docs」というテーマだが、実態は寄せ集め。  
> ユーザーが今一番困っているのは「制御できない」「信頼できない」こと。  
> Integration before trust は順序が逆。

### 再編結果

```
Before:
  v0.7.0 — Bug fixes (2 issues)
  v0.8.0 — Integration & Docs (7 issues) ← 散漫
  v1.0.0 — Production Ready (5 issues)

After:
  v0.7.0 — Bug fixes (2 issues)          ← 変更なし
  v0.8.0 — Control & Trust (5 issues)    ← テーマ刷新
  v0.9.0 — Connect (4 issues)            ← 新設
  v1.0.0 — Production Ready (5 issues)   ← 変更なし
```

各マイルストーンに一文のナラティブが付く:

* v0.8.0: *「システムが裏で何をしているか、すべて見える。気に入らなければ直せる。」*
* v0.9.0: *「信頼できるコアを外の世界と繋ぐ。」*

`/pm` が提案し、人間が承認し、`gh issue edit --milestone` で実行。この流れが10分で完了した。

## 設計のポイント

### 1. 原則を明文化する

```
1. **Trust before integration** — Users must trust the core before connecting it to other systems
2. **Control before automation** — Give users visibility and manual control before adding more automation
```

これがないとLLMは「なんとなく整理」するだけになる。原則があることで、毎回同じ品質の分析が出る。人間のPMでも、疲れているときや急いでいるときは原則を忘れる。

### 2. 分析と実行を分離する

両スキルとも最後に「承認後に実行」と明記している。`gh issue edit --milestone` を勝手に実行されたら困る。

`/cto` に至っては「Analysis only — do NOT execute changes」と完全に読み取り専用にしている。技術診断の結果を見て何をするかは人間が決める。

### 3. 互いを参照する

`/pm` は「技術面は `/cto` へ」と誘導し、`/cto` は「`/pm` の結果と照合する」ステップがある。2つのスキルが対話的に使えるようになっている。

## 応用：自分の原則にカスタマイズする

プロジェクトによって重視する原則は異なる。

**SaaS事業の `/pm`:**

```
1. **Revenue impact first** — 課金機能に関わるイシューを優先
2. **Customer-reported bugs over internal** — ユーザー報告のバグを先に
3. **Security fixes skip milestones** — セキュリティ修正は即リリース
```

**大規模チームの `/cto`:**

```
1. **API contract first** — 内部実装より先にAPI契約を安定させる
2. **Observability before optimization** — 計測できないものは改善できない
3. **Migration windows** — 破壊的変更は四半期に1回のみ
```

原則をカスタマイズすることで、**プロジェクト固有の意思決定ポリシーをコード化**できる。

## まとめ

| スキル | 役割 | 置き場所 |
| --- | --- | --- |
| `/pm` | マイルストーン分析・リリース計画 | `~/.claude/commands/pm.md` |
| `/cto` | 技術健全性・負債・ドキュメント診断 | `~/.claude/commands/cto.md` |

Claude Codeのスラッシュコマンドは `.md` ファイル1つで定義できる。コードの品質チェック（`/quality`）やリリース（`/release`）だけでなく、**判断プロセス**もコマンド化できる。

「プロンプトに原則を書く」というのは一見シンプルだが、これは**意思決定ポリシーのコード化**。1人開発でも、PM目線とCTO目線の両方でプロジェクトを定期的にチェックできる。チームで共有すれば、PM/CTO不在でも一貫したトリアージと技術判断が維持される。

## 関連
