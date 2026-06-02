---
id: "2026-06-01-claude-code-dynamic-workflows-を技術的に整理する-01"
title: "Claude Code Dynamic Workflows を技術的に整理する"
url: "https://qiita.com/OctoPool/items/da04f57a1d33d61153b1"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "JavaScript", "qiita"]
date_published: "2026-06-01"
date_collected: "2026-06-02"
summary_by: "auto-rss"
query: ""
---

## この記事でわかること

- Dynamic Workflows がどういう仕組みで動くか
- 何が得意で、何が苦手か（コスト面含む）
- 使いはじめるときの注意点


## 前提・環境

- 対象: Claude Code（CLI / Desktop / VS Code拡張）
- 必要プラン: Max / Team / Enterprise
- ステータス: Research Preview（2026年5月28日〜）
- 情報源: Anthropic公式発表、Claude Code公式ドキュメント


## Dynamic Workflows とは

2026年5月28日、Anthropic が Claude Opus 4.8 のリリースと同時に **Dynamic Workflows** を Research Preview として公開した。

一言で言うと、**Claude が自分でオーケストレーションスクリプトを書き、数十〜数百のサブエージェントを並列で走らせる仕組み**だ。

従来の Claude Code は、複雑なタスクを1つのセッション（コンテキストウィンドウ）の中で処理していた。タスクが大きくなるほどコンテキストが圧迫され、長時間の作業はミスが増えやすかった。

Dynamic Workflows はこの制約を根本から変える。オーケストレーションの計画をモデルのコンテキストウィンドウの外に出し、**JavaScript スクリプト**として書き出す。そのスクリプトをランタイムが実行し、各サブエージェントが独立して並列処理する。


## 仕組みを整理する

```
あなた → Claude Code（Orchestrator）
              ↓
         JSスクリプトを生成
              ↓
    ┌────────────────────────────┐
    │  Subagent A  Subagent B   │
    │  Subagent C  Subagent D   │
    │  ...（最大1,000体）        │
    └────────────────────────────┘
              ↓
         結果を検証・統合
         （別のエージェントが
           adversarialにレビュー）
              ↓
         最終結果をあなたへ
```

ポイントは以下の3点:

1. **計画をスクリプト化する**: コンテキストの外に出すことで、巨大タスクでも計画がぶれない
2. **並列実行**: 独立したサブエージェントが同時に動くため、大量の作業を短時間でこなせる
3. **adversarial レビュー**: 別エージェントが結果を壊そうとすることで品質を担保する。進捗は継続保存されるため、中断しても再開できる



## 何が得意か

公式が挙げているユースケースは大きく3つ:

**コードベース監査（Codebase Audit）**
サービス全体のセキュリティ・パフォーマンスレビューを独立した複数の視点で行い、結果を統合する。

**大規模マイグレーション（Large Migration）**
フレームワーク移行やAPI廃止対応を数千ファイル規模で実施。既存のテストスイートを合格基準として使える。

**クリティカルな検証（Critical Verification）**
複数のエージェントが独立して問題を解き、adversarial なエージェントが結果を検証してから納品する。

公開されている中で最も印象的な事例は、Jarred Sumner による **Bun ランタイムの Zig→Rust ポート**だ。約75万行の Rust コードを生成し、元のテストスイートの99.8%を通過。11日で完了している。


## 何が苦手か / 注意すること

**コストが高い**
通常の Claude Code セッションに比べ、トークン消費が大幅に増える。最大1,000のサブエージェントが同時に動くため、スコープを絞らずに使うとコストが爆発する。公式も「小さいタスクからはじめることを推奨」と明記している。

**Research Preview**
まだ本番品質ではない。実運用での挙動は都度確認が必要。

**プラン制限**
Max / Team / Enterprise のみ。Free / Pro プランでは使えない。


## 使いはじめ方

### 手動でワークフローを作成する

Claude Code に対して、具体的なタスクを伝えてワークフローの作成を依頼する:

```
このリポジトリ全体のセキュリティ監査を
Dynamic Workflow で実施してほしい
```

### Ultracode モードを使う

Claude Code の effort メニューから `ultracode` を有効にすると、Claude がワークフローを使うべきかどうかを自動判断する。effort が `xhigh` に設定され、必要に応じてオーケストレーションが起動する。

```
/effort → ultracode を選択
```

### 最初の実行前に確認ダイアログが出る

ワークフロー実行前には確認が求められる。特に大規模タスクは事前にスコープを明確にしておくことを推奨する。



## まとめ

Dynamic Workflows は「エージェントが自分でエージェントを書いて動かす」アーキテクチャの実用化だ。コンテキストウィンドウの制約を外に出し、並列+adversarialレビューで品質を担保する設計は興味深い。

現時点では Research Preview であり、コストも高い。使うなら、まず小さいスコープで試して感触をつかむのが無難だろう。大規模マイグレーションや監査など、「人間が週単位で取り組む作業」を対象にした機能として位置づけると整理しやすい。


## 参考

- [Introducing dynamic workflows in Claude Code](https://claude.com/blog/introducing-dynamic-workflows-in-claude-code) — Anthropic公式ブログ
- [Orchestrate subagents at scale with dynamic workflows](https://code.claude.com/docs/en/workflows) — Claude Code公式ドキュメント
- [Introducing Claude Opus 4.8](https://www.anthropic.com/news/claude-opus-4-8) — Anthropic公式発表
- [Claude Code Dynamic Workflows: Scripts Replace Context Windows](https://www.techtimes.com/articles/317363/20260529/claude-code-dynamic-workflows-scripts-replace-context-windows-ultracode-automates-orchestration.htm) — TechTimes
