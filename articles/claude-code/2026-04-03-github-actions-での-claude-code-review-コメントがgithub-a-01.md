---
id: "2026-04-03-github-actions-での-claude-code-review-コメントがgithub-a-01"
title: "GitHub Actions での Claude Code Review コメントが「GitHub Actions」になってしまう問題"
url: "https://zenn.dev/thaddeusjiang/articles/8cca91e0196eb3"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-03"
date_collected: "2026-04-04"
summary_by: "auto-rss"
---

claude-code-action を使って Pull Request のコードレビューを自動化しているときに、

期待する表示：レビューコメントの投稿者が Claude（claude[bot]）
実際の表示：投稿者が GitHub Actions（‎⁠github-actions[bot]⁠）

という状態になってしまいました。

調査した結果、原因は ‎⁠github_token⁠ 入力パラメータの指定でした。‎⁠github_token⁠ を削除するだけで解決できた。

公式ドキュメントにもある通り、このパラメータはカスタム GitHub App を使う場合だけ必要で、通常の利用...
