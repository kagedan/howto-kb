---
id: "2026-03-24-claude-code-jujutsu-worktreecreate-hookで並行セッションを自動-01"
title: "Claude Code + Jujutsu: WorktreeCreate hookで並行セッションを自動分離する"
url: "https://zenn.dev/jasagiri/articles/eb07d2d9a8acd1"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-03-24"
date_collected: "2026-03-26"
summary_by: "auto-rss"
---

Claude Codeで複数セッションを同時に走らせると、同一リポジトリ内で変更が混在する。git worktreeなら claude --worktree で自動分離できるが、Jujutsu (jj) ユーザーはそのままでは使えない。
本記事では、Claude CodeのWorktreeCreate hookを使って jj workspace に委譲し、claude --worktree をJujutsuネイティブに動かす方法を解説する。プラグインとして公開済みなので、1コマンドで導入できる。

 TL;DR
# プラグインをインストール
claude plugin instal...
