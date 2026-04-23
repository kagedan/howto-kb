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

[claude-code-action](https://github.com/anthropics/claude-code-action/tree/main) を使って Pull Request のコードレビューを自動化しているときに、

* 期待する表示：レビューコメントの投稿者が Claude（claude[bot]）
* 実際の表示：投稿者が GitHub Actions（‎⁠github-actions[bot]⁠）

という状態になってしまいました。

![](https://static.zenn.studio/user-upload/3c02a8781b2a-20260403.png)

調査した結果、原因は ‎⁠`github_token`⁠ 入力パラメータの指定でした。‎⁠github\_token⁠ を削除するだけで解決できた。

![](https://static.zenn.studio/user-upload/1bc4ab9060db-20260403.png)

公式ドキュメントにもある通り、このパラメータは**カスタム GitHub App を使う場合だけ**必要で、通常の利用では不要です。

![](https://static.zenn.studio/user-upload/029504b8b944-20260403.png)

今回の修正差分

![](https://static.zenn.studio/user-upload/67892a697973-20260403.png)

解決方法は ‎⁠github\_token⁠ を削除するだけで、とてもシンプルですが、ハマると気付きにくいポイントだと思います。  
同じように「Claude でレビューさせているはずなのに、GitHub Actions がコメントしているように見える」と感じた方の参考になれば幸いです。
