---
id: "2026-03-16-プロンプトインジェクション一発で機密ファイルが飛ぶclaude-codeのhooksで防壁を作った話-01"
title: "プロンプトインジェクション一発で機密ファイルが飛ぶ——Claude Codeのhooksで防壁を作った話"
url: "https://zenn.dev/hoshimurayuto/articles/credential-guard"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-03-16"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

Zennのはじめての記事です。よろしくの程を。

 TL;DR
Claude Codeのツール呼び出しを検査して、機密情報を読ませない・送信させないプラグインを作った。
https://github.com/HoshimuraYuto/credential-guard
# マーケットプレースを追加
/plugin marketplace add HoshimuraYuto/credential-guard

# インストール
/plugin install credential-guard@credential-guard
!
Claude Codeのプラグインなのでコマンド2つで導入で...
