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

はじめに
普段の開発において、GitHub Issueを起票してから実際に修正に着手するまで地味に時間がかかってしまった経験はないでしょうか？
Claude CodeをGitHub Actionsと組み合わせることで、Issueにauto-fixラベルを付与するだけでコードの自動修正からPR作成までを一気通貫で行う仕組みを構築することが可能です。
本記事では、実際のシステム構築とその際の注意点を記載いたします。

 この記事のGoal

Claude CodeをCI上で自律的に動作させる方法がわかること
git worktreeを活用した安全な自動修正の仕組みが構築できること
ラベル...
