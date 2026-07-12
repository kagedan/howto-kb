---
id: "2026-07-12-claude-codeで始めるloop-engineering-01"
title: "Claude Codeで始めるLoop Engineering"
url: "https://zenn.dev/laiken/articles/20260712-claude-codeloop-engineering"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "prompt-engineering", "AI-agent", "zenn"]
date_published: "2026-07-12"
date_collected: "2026-07-13"
summary_by: "auto-rss"
query: ""
---

#### AIが書きました🤖

この記事は、AIが書いたものを人間が確認してから投稿しています。

Claude Codeを使って「loopを設計する」とは、具体的に何を、どのようなコマンドやファイルで実装することなのでしょうか？

# Loop Engineering

## プロンプトする人から、ループを設計する人へ

Claude Codeを単発の実装支援として使う段階から、発見、実行、検証、記録を反復する運用システムとして使う段階へ。

ここで設計するのは「次に何を聞くか」ではなく、「どの条件で、何を実行し、何をもって止めるか」です。

* 対象: Claude Code
* 用途: 実装、CI対応、PR保守、定期トリアージ
* 設計単位: 1つの検証可能な成果

## Executive Summary

**Prompt Engineering**は、一回の出力を改善します。

**Loop Engineering**は、継続的に成果を出す仕組みを改善します。

ループの基本構造は、次のとおりです。

```
Discover
  ↓
Decide
  ↓
Execute
  ↓
Verify
  ↓
Escalate
  ↓
Remember
  └────────→ 次のDiscoverへ
```

| 段階 | 役割 |
| --- | --- |
| Discover | CI、Issue、PR、ログから次の仕事を見つける |
| Decide | 対象外を除き、1件の小さな作業に絞る |
| Execute | 計画し、実装し、変更を限定する |
| Verify | テスト、ビルド、Lint、レビューで確認する |
| Escalate | 自動で閉じられない問題を人のトリアージへ送る |
| Remember | 結果と次の作業を会話の外に残す |

## 最初に押さえるべき3つの原則

### 1. 目的ではなく、停止条件を書く

「認証を直す」ではなく、次のように書きます。

> 対象テストが成功し、Lintが通り、変更範囲が制約内にある。

良いループは、AIが何をしたかではなく、どの条件を満たしたら停止するかで決まります。

### 2. 作る人と確認する人を分ける

実装者の自己評価だけに依存しません。

検証用の別エージェント、Stop hook、または人のレビューを置きます。

### 3. 会話を状態管理に使わない

会話は永続的な状態管理には向きません。

完了、失敗、保留、次の一手は、Markdownやチケットに残します。

# ループを構成する「5つ＋記憶」

Addy Osmaniの整理を、Claude Codeで実装できる部品に変換すると、次のようになります。

| 要素 | 役割 | Claude Codeでの実装例 |
| --- | --- | --- |
| Automation | いつ、何を再実行するか | `/loop`、Routines、Desktop scheduled tasks、GitHub Actions |
| Worktree | 並列作業を隔離する | Git worktree、subagentの`isolation: worktree` |
| Skills | 繰り返す手順を固定する | `.claude/skills/<skill-name>/SKILL.md` |
| Connectors | 実際の作業環境へ接続する | MCP、GitHub、DB、Slackなど |
| Subagents | 実装、調査、レビューを役割分担する | `.claude/agents/*.md` |
| Memory | 会話の外へ状態を残す | Markdown、Issue、Linearなど |

## 最小ファイル構成

```
repo/
├── CLAUDE.md
├── .claude/
│   ├── loop.md
│   ├── skills/
│   │   └── release-check/
│   │       └── SKILL.md
│   └── agents/
│       ├── fixer.md
│       └── code-reviewer.md
├── ops/
│   └── agent-state.md
└── .github/
    └── workflows/
        └── nightly-triage.yml
```

このうち、Claude Codeが規約や設定として読む対象は、主に次のファイルです。

* `CLAUDE.md`
* `.claude/loop.md`
* `.claude/skills/`
* `.claude/agents/`

`ops/agent-state.md`は、ループの状態を残すためにプロジェクト側で設けるファイルです。

# How to: 最小の検証ループを作る

## Step 1. 成果を1つに絞り、測定できる完了条件に変える

曖昧なTo Doを、そのままエージェントに渡しません。

良いループは「何をするか」より「何が確認できたら終わりか」で決まります。

完了条件には、次の要素を含めます。

* 実行するコマンド
* 期待する結果
* 変更範囲の制約
* 反復回数や時間の上限

```
/goal npm test exits 0, npm run lint exits 0,
only files under src/auth and tests/auth are changed,
and stop after 12 turns
```

## Step 2. 変わりにくいルールを`CLAUDE.md`に置く

毎回必要な前提だけを、プロジェクトの常設コンテキストにします。

まず、プロジェクトのルートで`/init`を実行し、生成された`CLAUDE.md`を短く育てます。

ビルド、テスト、リポジトリ固有の制約だけを残します。

```
# CLAUDE.md

## Commands

- Test: npm test
- Lint: npm run lint
- Typecheck: npm run typecheck

## Workflow

- For changes across multiple files, create a plan before editing.
- Run the narrowest relevant test first.
- Do not push, merge, deploy, or delete without explicit user approval.

## Repository rules

- Keep auth changes within src/auth and tests/auth unless the plan explains why.
- Update docs when public behavior changes.
```

`CLAUDE.md`は、長いプロンプトを保存する場所ではありません。

頻繁に変わらず、プロジェクト全体に適用されるルールだけを置きます。

## Step 3. 反復する手順をSkillにする

毎回説明している手順は、Skillにします。

Skillは次の場所に置きます。

```
.claude/skills/<skill-name>/SKILL.md
```

ディレクトリ名がコマンド名になるため、次の例は`/release-check`で実行できます。

```
---
name: release-check
description: Inspect a release PR and report actionable failures.
disable-model-invocation: true
allowed-tools: Read Grep Glob Bash
---

1. Inspect the current PR and recent CI runs.
2. Run the relevant test and lint commands.
3. Classify findings as:
   - fix now
   - needs human decision
   - no action
4. Write a concise update to ops/agent-state.md.
5. Never push, merge, deploy, or delete.
```

デプロイ、送信、削除など、副作用がある手順には`disable-model-invocation: true`を付けます。

これにより、ClaudeがそのSkillを自動実行することを防ぎます。

## Step 4. 実装者とレビュー担当を分ける

「自分で書いたコードを、自分で採点する」構造を避けます。

Claude Codeのカスタムサブエージェントは、MarkdownとYAML front matterで定義します。

レビュー担当には編集権限を付けず、差分、テスト、リスクだけを評価させます。

```
---
name: code-reviewer
description: Review changed code for correctness, security, and test evidence.
tools: Read, Grep, Glob, Bash
model: inherit
---

You are a strict reviewer.

1. Run git diff and inspect only changed files.
2. Check that the stated acceptance criteria have evidence.
3. Identify root-cause risks, security issues, and missing tests.
4. Return findings in this format:
   - Critical
   - Must fix
   - Nice to have
   - Evidence reviewed

Do not edit files. Do not approve based on claims alone.
```

実装用のサブエージェントは`Edit`を持てます。

並列で変更させる場合は、forkしたサブエージェントに`isolation: worktree`を設定し、作業ディレクトリを分離します。

## Step 5. 状態をMarkdownに残す

セッションの記憶ではなく、リポジトリの記録に次の仕事を渡します。

```
# ops/agent-state.md

## Last run

- 2026-06-20 09:00 JST
- Trigger: nightly triage
- Result: CI failure reproduced in tests/auth/session.test.ts

## Completed

- [x] Reproduced failure
- [x] Added regression test
- [x] Fixed token refresh path
- [x] npm test and npm run lint passed

## Needs human decision

- [ ] Confirm whether the session timeout should remain 30 minutes.

## Next run

- Check review comments on PR #123.
- Do not create another PR for this issue.
```

状態ファイルには、次の情報を残します。

* 何を試したか
* 何が通ったか
* 何を人に渡すか
* 次に何をするか

ファイル名は任意です。

重要なのは、状態を会話の外に置くことです。

## Step 6. 時間で回すものと、完了するまで回すものを分ける

同じ自動化でも、実行間隔と停止条件は別に設計します。

`/loop`は、開いているClaude Codeセッション中の短期ポーリングに向いています。

`/goal`は、証拠を伴う完了条件が満たされるまで、同一セッションを進めるために使います。

```
# 今開いているセッションで、10分ごとにPRを確認する
/loop 10m /release-check

# 条件を満たすまで修正と検証を続ける
/goal npm test exits 0 and npm run lint exits 0,
then summarize the exact commands and outputs
```

# 実務で使える最小ループ

最初の対象としては、機能開発全体ではなく、CI失敗またはPR保守が適しています。

入力と検証の境界が明確で、AIに任せる範囲を限定しやすいためです。

## PR health loop

```
定期実行
  ↓
PR、CI失敗、レビューコメントを収集
  ↓
release-check Skillが状態を分類
  ↓
修正可能な小さい問題だけworktreeで修正
  ↓
別のcode-reviewerが差分と証拠を検証
  ↓
人がPRを確認
  ↓
判断が必要なものは状態ファイルへ残す
```

具体的には、次の流れです。

1. 定期実行が、現在のPR、CI失敗、未解決レビューコメントを収集する。
2. `/release-check`が、証拠付きで状態ファイルを更新する。
3. 小さく再現可能な不具合だけを、隔離されたworktreeで修正する。
4. 実装者とは別の`code-reviewer`が、変更とテスト証拠を確認する。
5. テストが成功し、レビューでCriticalがなければ、人がPRを確認する。
6. 判断が必要なものは`Needs human decision`に残し、自動マージはしない。

## ループ設計チェックリスト

開始条件の例は、次のとおりです。

* CIが失敗した
* レビューコメントが追加された
* 指定ラベルのIssueが存在する

# アンチパターン

## 検証なき反復

「完了しました」という自己申告を、成功条件にしてはいけません。

テスト、ビルド、Lint、スクリーンショット比較など、外部から確認できるシグナルを置きます。

## 会話だけで進捗管理する

長いセッションに依存すると、コンテキスト圧迫と再開不能の原因になります。

状態は、ファイルまたはタスク管理ツールに残します。

## 自動処理を過信する

無監督でmergeやdeployまで進めるべきではありません。

ループの目的は、人の判断を消すことではありません。

人が判断すべき地点まで、安全に作業を運ぶことです。

# 導入順序

## 最初の1週間

`CLAUDE.md`と、1つの検証可能な`/goal`を作ります。

## 次の1週間

繰り返している手順を1つだけSkillにします。

同時に、状態ファイルを追加します。

## その後

読み取り専用のレビュー用subagentを追加します。

## 安定後

worktreeと外部スケジューラを導入します。

次の指標を観測します。

* 実行頻度
* 失敗率
* 手戻り
* 人へのエスカレーション数
* トークン消費
* 完了までの反復回数

# まとめ

Claude Codeでloopを設計するとは、単に同じプロンプトを繰り返すことではありません。

具体的には、次の要素を設計することです。

1. 何をきっかけに開始するか
2. どの作業を対象にするか
3. 何を自動実行するか
4. どの証拠で成功を判定するか
5. どの条件で停止するか
6. どの判断を人に渡すか
7. 次回のために何を記録するか

Claude Codeでは、それぞれを次の機能に対応させられます。

| 設計対象 | Claude Codeでの実装 |
| --- | --- |
| 常設ルール | `CLAUDE.md` |
| 反復手順 | Skills |
| 実装と検証の分離 | Subagents |
| 短期的な定期実行 | `/loop` |
| 完了条件付きの反復 | `/goal` |
| 並列作業の隔離 | Git worktree |
| 外部サービスとの接続 | MCP |
| セッションをまたぐ状態 | Markdown、Issue、タスク管理 |
| 継続的な自動実行 | Routines、Desktop scheduled tasks、GitHub Actions |

Loop Engineeringの中心は、AIに長時間働かせることではありません。

小さな仕事を、安全に発見し、限定された権限で実行し、証拠を使って検証し、必要な判断だけを人へ渡すことです。

# 参考資料
