---
id: "2026-03-16-claude-code-actionでgithub-issue駆動ai開発-01"
title: "Claude Code ActionでGitHub Issue駆動AI開発"
url: "https://zenn.dev/kanahiro/articles/98dce92b922a9e"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-03-16"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

## はじめに

Issueを起点とした以下のようなフローを手に馴染ませていたところでした（手元のマシンで動かす前提）。

1. GitHub Issueでビジネス要求を記述
2. Claude CodeでIssueを読んで、Plan
3. 納得いくまでPlanを叩く
4. 実装

意外と悪くないなと思っていたのですが、「これをやるなら最早GitHub上でClaude Codeが動けばそれで良いじゃん」と気づいてしまったので、やってみた記事です。

## `anthropics/claude-code-action`

<https://github.com/anthropics/claude-code-action>

最初は任意のモデルを使えるような何かをスクラッチで書くのも面白いかなと思ったのですが、Claude Code Actionがあって、それがMAXプランの範囲で利用出来ることを知ったので、それを使うのが最短と判断しました。

導入手順は簡単で、`/install-github-app`を実行するだけでよいです。

<https://code.claude.com/docs/ja/github-actions>

この手順で環境構築するだけ…ならこの記事を書く必要がなかったのですが、若干気を付けるべきポイントがありました。

### プリセットだと、Pull-requestの自動作成はできない

これがドキュメントからは非自明な罠で、デフォルトだと何故かPull-requestを作成する権限が塞がれている模様です。プルリクエストの雛形まで作られた状態のアンカーリンクは貼り付けてくれるのですが…。

これを迂回するには、GitHub MCPを利用するのがどうやら良さそうです（調べて見つかる、自動でPRを作らせているパターンは全てMCP利用だった）。そんなわけで下記のworkflowを使っています。

```
name: Claude Code

on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
  pull_request_review:
    types: [submitted]
  issues:
    types: [labeled]

jobs:
  claude:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
      issues: write
      id-token: write
      actions: read
    steps:
      - name: Checkout repository
        uses: actions/checkout@v6
        with:
          fetch-depth: 1

      - name: Run Claude Code
        id: claude
        uses: anthropics/claude-code-action@v1
        with:
          claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
          trigger_phrase: "@claude"
          show_full_output: true
          claude_args: |
            --append-system-prompt "実装を依頼された場合、コード変更後に必ず Pull Request を作成してください。PR本文には Closes #<Issue番号> を含めてください。GitHub操作にはghコマンドではなくMCPツール(mcp__github__*)を使ってください。"
            --model claude-opus-4-6
            --allowed-tools "mcp__github__create_pull_request,mcp__github__get_pull_request,mcp__github__list_pull_requests,mcp__github__create_issue,mcp__github__get_issue,mcp__github__list_issues,mcp__github__add_issue_comment,mcp__github__create_branch,mcp__github__push_files,mcp__github__search_code,mcp__github__get_file_contents,mcp__github__create_or_update_file"
          additional_permissions: |
            actions: read
```

このほかにも、デフォルトでは許可されていないツール・コマンドを使えなくて困る場合は緩めましょう。

## GitHub Issueを起点とした開発フロー

以下は筆者のポートフォリオサイトを事例とした開発フローの紹介です。

1. GitHubでIssueを書く
2. `@claude`にplanさせる  
   ![](https://static.zenn.studio/user-upload/f6c1df4db857-20260316.png)  
   a. ラベルを使って起動も試したけど、余計な仕組み入れないでコメント書いた方がシンプルそうだった
3. Planをレビューする  
   a. Issue上で`@claude`に返信して、気に入るまで何度でも修正させる
4. `@claude`にimplementを指示する
5. 自動作成されたPRをレビューしてマージする  
   ![](https://static.zenn.studio/user-upload/652d8aba28b4-20260316.png)  
   a. 自動テストだいじ（この例では、Cloudflare WorkersのPRプレビュー、VRTレポートを自動で作成したりもしている）

## 感想

* GitHub Actionsがそれぞれ独立したマシンなので、並列実行のための何か（git worktreeだとか）に頭を使わなくて良くていい
* スマホから指示出せてたのしい。スマホからでも差分の妥当性を判断できるような環境整備は必要（自動テスト、プレビュー…）。特殊なツールや設定が無くても違和感なくスマホから指示できてよい（これが幸せなことかどうかは別として…）。
* 手元で検証したくなったらpullしてくれば続きから開始できる。
* チーム開発のベスプラはわからない…。MAX Planはユーザーに紐つくから、それを使ってチーム開発は微妙な感じ（規約的にもグレー？）。
