---
id: "2026-03-30-複数案件を掛け持ちするエンジニアのための-gh-claude-code-アカウント切り替え術-01"
title: "複数案件を掛け持ちするエンジニアのための gh / Claude Code アカウント切り替え術"
url: "https://zenn.dev/busaiku0084/articles/20260330-dc3vcb5l"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-03-30"
date_collected: "2026-03-31"
summary_by: "auto-rss"
---

はじめに
複数の案件を掛け持ちしていると、GitHubアカウントやClaude Codeの認証を切り替える場面が頻繁にやってきます。個人のOSSと業務用リポジトリで別アカウントを使っていたり、案件ごとにClaude Codeの組織アカウントが異なっていたりすると、切り替え忘れによるミスが起きがちです。
「間違ったアカウントでコミットしてしまった」「別の組織のClaude Codeでコードを読ませてしまった」といった経験がある方もいるのではないでしょうか。
この記事では、GitHub CLI（gh）の auth switch とClaude Codeの auth コマンドを使って、アカ...
