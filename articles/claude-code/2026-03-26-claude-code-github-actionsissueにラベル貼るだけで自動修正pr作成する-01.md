---
id: "2026-03-26-claude-code-github-actionsissueにラベル貼るだけで自動修正pr作成する-01"
title: "【Claude Code × GitHub Actions】Issueにラベル貼るだけで自動修正＆PR作成する仕組みを作ってみた"
url: "https://zenn.dev/solvio/articles/63842f1417883a"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-03-26"
date_collected: "2026-03-27"
summary_by: "auto-rss"
---

## はじめに

普段の開発において、GitHub Issueを起票してから実際に修正に着手するまで地味に時間がかかってしまった経験はないでしょうか？

**Claude Code**をGitHub Actionsと組み合わせることで、Issueに`auto-fix`ラベルを付与するだけでコードの自動修正からPR作成までを一気通貫で行う仕組みを構築することが可能です。

本記事では、実際のシステム構築とその際の注意点を記載いたします。

## この記事のGoal

* **Claude CodeをCI上で自律的に動作させる方法がわかること**
* **git worktreeを活用した安全な自動修正の仕組みが構築できること**
* **ラベルベースのステータス管理による運用フローが理解できること**

IssueベースのバグFixフローをできるだけ自動化したい方の参考になりますと幸いです。

## 対象読者

* Claude Codeを日常的に使用している方
* GitHub Actionsを活用した開発自動化に興味がある方
* Issue起票から修正までのリードタイムを短縮したい方

## アーキテクチャの概要

今回構築する仕組みの全体像です。

### 処理フロー

全体の流れとしては、**Issueにラベルを貼る → GitHub Actionsが発火 → Claude Codeがworktree上でコード修正 → PR作成**というシンプルな構成です。

### ラベルによるステータス管理

この仕組みでは、ラベルを使ってIssueの修正状況を可視化しています。

| ラベル | 意味 |
| --- | --- |
| `auto-fix` | 自動修正をリクエスト（トリガー） |
| `auto-fix-in-progress` | Claude Codeが修正中 |
| `auto-fix-done` | 修正完了・PR作成済み |
| `auto-fix-failed` | 修正に失敗 |

チームメンバーがIssue一覧を見るだけで、どのIssueが自動修正中か、完了したか、失敗したかが一目でわかります。

## なぜこの仕組みを作ったのか

普段の開発でこんな場面がよくありました。

* バグが見つかったのでIssueを起票したが、他の作業中で着手できない
* 軽微な修正なのに Issue → ブランチ作成 → 修正 → コミット → PR作成 の手順が地味に手間
* 夜中にバグ報告が来て、翌朝まで放置してしまう

これらの課題に対して、**「Issueの内容をそのままClaude Codeに渡して自動で修正させれば良いのでは？」** と思い至ったことが今回のきっかけです。

また、今回の仕組みでは**セルフホステッドランナー**を使用しているため、GitHub Actionsの実行時間に対する課金が発生しません。Claude Codeによる自動修正は処理時間が長くなりがちですが、セルフホステッドランナーであればActions側のコストはゼロで、**かかるのはClaude CodeのAPI利用料（サブスク料金）のみ**です。コスト面を気にせずガンガン自動修正を回せるのは大きなメリットだと感じています。

## システム実装

### 今回のディレクトリ構成

```
プロジェクトルート
├── .github/
│   └── workflows/
│       └── auto-fix-issue.yml    # GitHub Actionsワークフロー
├── scripts/
│   └── auto-fix-issue.mjs        # 自動修正スクリプト
├── CLAUDE.md                      # Claude Code用の設定ファイル
└── package.json
```

auto-fix-issue.yml（全文）

```
name: Auto Claude Code Fix

on:
  issues:
    types: [labeled]

# 同一Issueの同時実行を防止(新しい実行が優先)
concurrency:
  group: auto-fix-${{ github.event.issue.number }}

jobs:
  claude-code-runner:
    runs-on: self-hosted

    # "auto-fix" ラベルが付いた時だけ発動
    if: github.event.label.name == 'auto-fix'

    timeout-minutes: 30

    permissions:
      contents: write
      pull-requests: write
      issues: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run auto-fix script
        env:
          ISSUE_NUMBER: ${{ github.event.issue.number }}
          ISSUE_TITLE: ${{ github.event.issue.title }}
          ISSUE_BODY: ${{ github.event.issue.body }}
        run: pnpm auto-fix-issue

      # スクリプト内でコメント処理しているが、予期せぬクラッシュ時のフォールバック
      - name: Notify failure on unexpected crash
        if: failure()
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh issue comment ${{ github.event.issue.number }} --body "## 自動修正が予期せず中断されました

          ワークフローの実行ログを確認してください。
          [ログを確認する](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }})"

          gh issue edit ${{ github.event.issue.number }} --remove-label "auto-fix-in-progress" || true
          gh issue edit ${{ github.event.issue.number }} --add-label "auto-fix-failed" || true
```

auto-fix-issue.mjs（全文）

```
#!/usr/bin/env node
/**
 * Issue 自動修正スクリプト (Claude Code + git worktree 版)
 */

import { execFileSync, execSync } from 'node:child_process';
import { resolve } from 'node:path';

// --- 環境変数の取得 ---
function requireEnv(name) {
  const value = process.env[name];
  if (!value) {
    console.error(`エラー: 環境変数 ${name} が設定されていません`);
    process.exit(1);
  }
  return value;
}

// --- Issue 操作 (gh CLI) ---
function runGhCommand(args) {
  try {
    execFileSync('gh', args, { stdio: 'inherit', env: process.env });
  } catch (error) {
    console.error(`gh コマンド失敗 (${args.join(' ')}): ${error.message}`);
  }
}

function commentOnIssue(issueNumber, body) {
  runGhCommand(['issue', 'comment', issueNumber, '--body', body]);
}

function addLabel(issueNumber, label) {
  runGhCommand(['issue', 'edit', issueNumber, '--add-label', label]);
}

function removeLabel(issueNumber, label) {
  runGhCommand(['issue', 'edit', issueNumber, '--remove-label', label]);
}

// --- メイン処理 ---
function main() {
  const issueNumber = requireEnv('ISSUE_NUMBER');
  const issueTitle = requireEnv('ISSUE_TITLE');
  const issueBody = process.env.ISSUE_BODY ?? '';

  const branchName = `auto-fix-${issueNumber}`;
  // 現在のディレクトリ直下に一時的な worktree フォルダを作成
  const worktreeDir = `.worktree-${branchName}`;

  commentOnIssue(
    issueNumber,
    '## 自動修正を開始しました\nClaude Code エージェントが専用の作業領域(worktree)でコードを修正し、PRを作成します。'
  );
  removeLabel(issueNumber, 'auto-fix');
  addLabel(issueNumber, 'auto-fix-in-progress');

  console.log(`\n${'='.repeat(60)}`);
  console.log(`[Step 1] 作業用 Worktree の準備: ${worktreeDir}`);
  console.log('='.repeat(60));

  try {
    // 過去の残骸があれば削除しておく
    execSync(`git worktree remove -f ${worktreeDir}`, { stdio: 'ignore' });
  } catch {
    // 無視
  }

  try {
    // main ブランチから新しいブランチを作成し、worktree として展開
    // (-B を使うことで既存ブランチがあっても上書き/リセットします)
    execSync(`git worktree add -B ${branchName} ${worktreeDir} main`, { stdio: 'inherit' });
  } catch (error) {
    console.error(`Worktreeの作成に失敗しました: ${error.message}`);
    process.exit(1);
  }

  // --- Claude に与える一連の作業指示 ---
  const prompt = `
あなたは自律型のAIソフトウェアエンジニアです。
以下のGitHub Issueを解決するための作業をすべてあなたに任せます。

## Issue #${issueNumber}: ${issueTitle}
${issueBody}

## 作業環境について
あなたはすでにIssue解決のために作成された専用の作業ディレクトリ（git worktree）におり、\`${branchName}\` ブランチにチェックアウトされています。
ブランチの作成や切り替えは不要です。そのまま現在のディレクトリで作業を開始してください。

## 作業手順
以下のステップを順番にターミナルコマンドを実行して進めてください。

1. **Gitの準備**:
   - ユーザー名 'github-actions[bot]'、メールアドレス 'github-actions[bot]@users.noreply.github.com' でローカル設定を行ってください (\`git config\`)。

2. **コードの修正**:
   - Issueの内容を読んでプロジェクトのコードを修正してください。
   - \`CLAUDE.md\`のコーディングガイドラインに厳密に従ってください。
   - バグ修正の場合は、修正内容・理由・背景をコード内のコメントとして明記してください。

3. **品質レビューとLint**:
   - 自身の修正差分 (\`git diff\`) を確認し、問題がないかセルフレビューしてください。
   - プロジェクトのLintコマンド (\`pnpm check:fix\` 等) を実行してエラーを解消してください。

4. **コミットとプッシュ**:
   - 修正したファイルをステージングし、\`fix: ${issueTitle} (closes #${issueNumber})\` というメッセージでコミットしてください。
   - \`origin ${branchName}\` にプッシュしてください (\`git push -u origin ${branchName}\`)。

5. **PRの作成**:
   - \`gh\` コマンドを使用してPull Requestを作成してください。
   - 対話プロンプトで止まらないように、以下のようにオプションをすべて指定して実行してください。
     \`gh pr create --title "fix: ${issueTitle} (#${issueNumber})" --body "Closes #${issueNumber}\n\nClaude Codeによって自動生成された修正です。" --base main --head ${branchName}\`

すべての手順が正常に完了したら、作業終了を宣言して終了してください。
`;

  console.log(`\n${'='.repeat(60)}`);
  console.log('[Step 2] Claude Code による自動修正の実行');
  console.log('='.repeat(60));

  try {
    // Claude Codeエージェントの起動
    // ★ cwd オプションを使って、作成した worktree 内でプロセスを起動する
    execFileSync('claude', ['-p', prompt, '--dangerously-skip-permissions'], {
      stdio: 'inherit',
      env: process.env,
      cwd: resolve(worktreeDir),
    });

    removeLabel(issueNumber, 'auto-fix-in-progress');
    addLabel(issueNumber, 'auto-fix-done');
    commentOnIssue(
      issueNumber,
      '## 自動修正が完了しました\nClaude Code が修正を完了し、PRを作成しました。'
    );
    console.log('\n✅ 全プロセスの実行が完了しました。');
  } catch (error) {
    console.error(`\n❌ Claude Codeの実行中にエラーが発生しました: ${error.message}`);
    removeLabel(issueNumber, 'auto-fix-in-progress');
    addLabel(issueNumber, 'auto-fix-failed');
    commentOnIssue(issueNumber, '## 自動修正に失敗しました\nアクションのログを確認してください。');
  } finally {
    // ★ 成功しても失敗しても、最後に必ず worktree を掃除する
    console.log(`\n${'='.repeat(60)}`);
    console.log('[Step 3] Worktree の後片付け');
    console.log('='.repeat(60));
    try {
      execSync(`git worktree remove -f ${worktreeDir}`, { stdio: 'inherit' });
      console.log('🧹 Worktree を削除しました。');
    } catch (e) {
      console.warn(`Worktreeの削除に失敗しましたが、処理は続行します: ${e.message}`);
    }
  }
}

main();
```

以降のセクションで各ファイルの処理内容を詳しく解説していきます。

### GitHub Actions ワークフロー

`.github/workflows/auto-fix-issue.yml`に配置するワークフローファイルです。

```
name: Auto Claude Code Fix

on:
  issues:
    types: [labeled]

# 同一Issueの同時実行を防止(新しい実行が優先)
concurrency:
  group: auto-fix-${{ github.event.issue.number }}

jobs:
  claude-code-runner:
    runs-on: self-hosted

    # "auto-fix" ラベルが付いた時だけ発動
    if: github.event.label.name == 'auto-fix'

    timeout-minutes: 30

    permissions:
      contents: write
      pull-requests: write
      issues: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run auto-fix script
        env:
          ISSUE_NUMBER: ${{ github.event.issue.number }}
          ISSUE_TITLE: ${{ github.event.issue.title }}
          ISSUE_BODY: ${{ github.event.issue.body }}
        run: pnpm auto-fix-issue
```

#### ポイント

* **トリガー**: `issues`の`labeled`イベントを使用し、`auto-fix`ラベルが付与されたときだけジョブが実行されるように`if`条件で制御しています
* **セルフホステッドランナー**: Claude Code CLIの実行にはAPIキーなどの環境設定が必要なため、`self-hosted`ランナーを使用しています。また、**セルフホステッドランナーはGitHub Actionsの実行時間に対する課金が発生しません。** Claude Codeの処理は数分〜数十分かかることもあるため、GitHub-hostedランナーを使用すると実行時間分の課金が積み重なってしまいます。

また、スクリプトが予期せずクラッシュした場合のフォールバック処理も用意しています。

```
      # スクリプト内でコメント処理しているが、予期せぬクラッシュ時のフォールバック
      - name: Notify failure on unexpected crash
        if: failure()
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh issue comment ${{ github.event.issue.number }} --body "## 自動修正が予期せず中断されました

          ワークフローの実行ログを確認してください。
          [ログを確認する](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }})"

          gh issue edit ${{ github.event.issue.number }} --remove-label "auto-fix-in-progress" || true
          gh issue edit ${{ github.event.issue.number }} --add-label "auto-fix-failed" || true
```

これにより、万が一の場合でもIssueにコメントで通知され、ラベルも`auto-fix-failed`に更新されます。

### 自動修正スクリプト

次に、実際にClaude Codeを起動してIssueを修正するNode.jsスクリプトです。  
処理は大きく分けて以下の3ステップで構成されています。

1. **Worktreeの準備**: 安全な作業領域を作成
2. **Claude Codeの実行**: Issue内容をプロンプトとして渡して修正を実行
3. **Worktreeの後片付け**: 作業領域を削除

#### ユーティリティ関数

```
#!/usr/bin/env node
/**
 * Issue 自動修正スクリプト (Claude Code + git worktree 版)
 */

import { execFileSync, execSync } from 'node:child_process';
import { resolve } from 'node:path';

// --- 環境変数の取得 ---
function requireEnv(name) {
  const value = process.env[name];
  if (!value) {
    console.error(`エラー: 環境変数 ${name} が設定されていません`);
    process.exit(1);
  }
  return value;
}

// --- Issue 操作 (gh CLI) ---
function runGhCommand(args) {
  try {
    execFileSync('gh', args, { stdio: 'inherit', env: process.env });
  } catch (error) {
    console.error(`gh コマンド失敗 (${args.join(' ')}): ${error.message}`);
  }
}

function commentOnIssue(issueNumber, body) {
  runGhCommand(['issue', 'comment', issueNumber, '--body', body]);
}

function addLabel(issueNumber, label) {
  runGhCommand(['issue', 'edit', issueNumber, '--add-label', label]);
}

function removeLabel(issueNumber, label) {
  runGhCommand(['issue', 'edit', issueNumber, '--remove-label', label]);
}
```

`gh` CLIを使ってIssueへのコメントやラベル操作を行うヘルパー関数群です。  
`execFileSync`を使用しているため、コマンドの実行結果がそのまま標準出力に表示されます。

#### Step 1: Worktreeの準備

```
function main() {
  const issueNumber = requireEnv('ISSUE_NUMBER');
  const issueTitle = requireEnv('ISSUE_TITLE');
  const issueBody = process.env.ISSUE_BODY ?? '';

  const branchName = `auto-fix-${issueNumber}`;
  // 現在のディレクトリ直下に一時的な worktree フォルダを作成
  const worktreeDir = `.worktree-${branchName}`;

  commentOnIssue(
    issueNumber,
    '## 自動修正を開始しました\nClaude Code エージェントが専用の作業領域(worktree)でコードを修正し、PRを作成します。'
  );
  removeLabel(issueNumber, 'auto-fix');
  addLabel(issueNumber, 'auto-fix-in-progress');

  try {
    // 過去の残骸があれば削除しておく
    execSync(`git worktree remove -f ${worktreeDir}`, { stdio: 'ignore' });
  } catch {
    // 無視
  }

  try {
    // main ブランチから新しいブランチを作成し、worktree として展開
    // (-B を使うことで既存ブランチがあっても上書き/リセットします)
    execSync(`git worktree add -B ${branchName} ${worktreeDir} main`, { stdio: 'inherit' });
  } catch (error) {
    console.error(`Worktreeの作成に失敗しました: ${error.message}`);
    process.exit(1);
  }
```

**処理の流れ**

1. **Issue通知**: Issueにコメントを投稿し、`auto-fix` → `auto-fix-in-progress`にラベルを付け替え
2. **残骸の削除**: 過去に同じIssue番号で実行した際のworktreeが残っていれば削除
3. **Worktree作成**: `git worktree add -B`でmainブランチから新しいブランチを作成し、worktreeとして展開

`git worktree`を使うことで、**メインの作業ディレクトリを汚さずに別の作業領域を作成**できます。`-B`オプションにより、既存ブランチがあっても上書きしてくれます。

#### Step 2: Claude Codeの実行

```
  // --- Claude に与える一連の作業指示 ---
  const prompt = `
あなたは自律型のAIソフトウェアエンジニアです。
以下のGitHub Issueを解決するための作業をすべてあなたに任せます。

## Issue #${issueNumber}: ${issueTitle}
${issueBody}

## 作業環境について
あなたはすでにIssue解決のために作成された専用の作業ディレクトリ（git worktree）におり、
\`${branchName}\` ブランチにチェックアウトされています。
ブランチの作成や切り替えは不要です。そのまま現在のディレクトリで作業を開始してください。

## 作業手順
以下のステップを順番にターミナルコマンドを実行して進めてください。

1. **Gitの準備**:
   - ユーザー名 'github-actions[bot]'、メールアドレス 'github-actions[bot]@users.noreply.github.com' でローカル設定を行ってください (\`git config\`)。

2. **コードの修正**:
   - Issueの内容を読んでプロジェクトのコードを修正してください。
   - \`CLAUDE.md\`のコーディングガイドラインに厳密に従ってください。
   - バグ修正の場合は、修正内容・理由・背景をコード内のコメントとして明記してください。

3. **品質レビューとLint**:
   - 自身の修正差分 (\`git diff\`) を確認し、問題がないかセルフレビューしてください。
   - プロジェクトのLintコマンド (\`pnpm check:fix\` 等) を実行してエラーを解消してください。

4. **コミットとプッシュ**:
   - 修正したファイルをステージングし、\`fix: ${issueTitle} (closes #${issueNumber})\` というメッセージでコミットしてください。
   - \`origin ${branchName}\` にプッシュしてください (\`git push -u origin ${branchName}\`)。

5. **PRの作成**:
   - \`gh\` コマンドを使用してPull Requestを作成してください。
   - 対話プロンプトで止まらないように、以下のようにオプションをすべて指定して実行してください。
     \`gh pr create --title "fix: ${issueTitle} (#${issueNumber})" --body "Closes #${issueNumber}\\n\\nClaude Codeによって自動生成された修正です。" --base main --head ${branchName}\`

すべての手順が正常に完了したら、作業終了を宣言して終了してください。
`;
```

#### Claude Codeエージェントの起動と結果処理

```
  try {
    // Claude Codeエージェントの起動
    // ★ cwd オプションを使って、作成した worktree 内でプロセスを起動する
    execFileSync('claude', ['-p', prompt, '--dangerously-skip-permissions'], {
      stdio: 'inherit',
      env: process.env,
      cwd: resolve(worktreeDir),
    });

    removeLabel(issueNumber, 'auto-fix-in-progress');
    addLabel(issueNumber, 'auto-fix-done');
    commentOnIssue(
      issueNumber,
      '## 自動修正が完了しました\nClaude Code が修正を完了し、PRを作成しました。'
    );
    console.log('\n✅ 全プロセスの実行が完了しました。');
  } catch (error) {
    console.error(`\n❌ Claude Codeの実行中にエラーが発生しました: ${error.message}`);
    removeLabel(issueNumber, 'auto-fix-in-progress');
    addLabel(issueNumber, 'auto-fix-failed');
    commentOnIssue(issueNumber, '## 自動修正に失敗しました\nアクションのログを確認してください。');
  }
```

**Claude Codeの起動オプション**

| オプション | 説明 |
| --- | --- |
| `-p` | プロンプトを直接渡して非対話モードで実行 |
| `--dangerously-skip-permissions` | 権限確認をスキップ（CI環境では対話的な確認ができないため必要） |
| `cwd` | worktreeディレクトリを作業ディレクトリとして指定 |

成功時は`auto-fix-done`、失敗時は`auto-fix-failed`のラベルを付与し、いずれの場合もIssueにコメントで結果を通知します。

#### Step 3: Worktreeの後片付け

```
  } finally {
    // ★ 成功しても失敗しても、最後に必ず worktree を掃除する
    try {
      execSync(`git worktree remove -f ${worktreeDir}`, { stdio: 'inherit' });
      console.log('🧹 Worktree を削除しました。');
    } catch (e) {
      console.warn(`Worktreeの削除に失敗しましたが、処理は続行します: ${e.message}`);
    }
  }
}

main();
```

`finally`ブロックで**成功・失敗に関わらず必ずworktreeを削除**しています。これを怠るとディスクを圧迫してしまうため、必ずクリーンアップを行うようにしています。

### package.jsonへのスクリプト登録

```
{
  "scripts": {
    "auto-fix-issue": "node scripts/auto-fix-issue.mjs"
  }
}
```

## なぜセルフホステッドランナーなのか

今回の仕組みでは`self-hosted`ランナーを使用していますが、これにはコスト面で大きなメリットがあります。

### GitHub-hostedランナーとのコスト比較

| 観点 | GitHub-hosted | Self-hosted |
| --- | --- | --- |
| Actions実行時間の課金 | **あり**（Linux: $0.008/分） | **なし** |
| マシンの維持コスト | なし | あり（電気代・保守） |
| 環境のカスタマイズ | 制限あり | 自由 |
| Claude Code CLIの事前設定 | 毎回セットアップが必要 | 一度設定すれば永続 |

Claude Codeによる自動修正は、Issueの内容によっては**数分〜数十分の処理時間**がかかることがあります。GitHub-hostedランナーの場合、この実行時間がそのまま課金対象になります。

例えば1回の実行に平均15分かかると仮定すると、月に20回実行した場合：

* **GitHub-hosted**: 15分 × 20回 × $0.008/分 = **$2.4/月**（Actionsの課金のみ）
* **Self-hosted**: **$0/月**（Actionsの課金なし）

一見小さな金額に見えますが、チームで頻繁に使うようになると積み重なります。**セルフホステッドランナーであればActions側の課金を完全にゼロにでき、かかるコストはClaude CodeのAPI利用料のみ**になります。

実行時間を気にせずガンガン自動修正を回せるのは、運用面でもかなり大きなメリットです。

## git worktreeを採用した理由

今回の仕組みで`git worktree`を使用している理由について補足します。

### 通常のブランチ切り替えとの比較

| 観点 | 通常のブランチ切り替え | git worktree |
| --- | --- | --- |
| 作業ディレクトリ | 共有（1つ） | 分離（それぞれ独立） |
| 既存の作業への影響 | あり（未コミットの変更が影響） | なし |
| 並列実行 | 不可 | 可能 |
| ディスク使用量 | 少ない | やや多い（objectsは共有） |

CI環境においては、**メインの作業ディレクトリを汚さずに安全に作業を行える**ことが最大のメリットです。また、将来的に複数のIssueを同時に処理する拡張も容易になります。

## 事前準備

この仕組みを導入するにあたって、以下の準備が必要です。

### 1. セルフホステッドランナーの構築

* Claude Code CLIがインストールされていること
* Claude CodeのAPIキー（`ANTHROPIC_API_KEY`）が環境変数に設定されていること

### 2. GitHub CLIの認証

* `gh` CLIがインストール・認証済みであること
* `GITHUB_TOKEN`が利用可能であること

### 3. ラベルの作成

GitHubリポジトリに以下のラベルを事前に作成しておきます。

* `auto-fix`
* `auto-fix-in-progress`
* `auto-fix-done`
* `auto-fix-failed`

## 運用時の注意点

### 自動修正に向いているIssue

* 明確なバグ修正（エラーメッセージや再現手順が記載されているもの）
* 軽微なUI修正やtypo修正
* 単純なロジック変更

### 自動修正に向いていないIssue

* 大規模なリファクタリング
* 新機能の追加（要件が曖昧なもの）
* データベースのマイグレーションを伴う変更
* セキュリティに関わる修正

**自動で作成されたPRは必ず人間がレビューしてからマージする**ことを推奨します。あくまで修正のドラフトを自動作成してくれるツールとしての運用を念頭におく形で自分も運用しております。

## おわりに

Claude CodeとGitHub Actionsを組み合わせることで、Issueにラベルを付与するだけで自動修正からPR作成までを行う仕組みを構築することができました。

特に`git worktree`による作業領域の分離は、CI上でClaude Codeを安全に実行するための重要な要素であることが確認できました。

本記事で紹介した実装手法が、開発フローの自動化において参考になりますと幸いです。
