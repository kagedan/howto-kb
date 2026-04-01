---
id: "2026-03-31-clinejection-事件に学ぶ-github-issue-投稿からのサプライチェーン攻撃を再現-01"
title: "Clinejection 事件に学ぶ - GitHub Issue 投稿からのサプライチェーン攻撃を再現してみた"
url: "https://zenn.dev/hiratsuka/articles/beb8f21adfc2e0"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-03-31"
date_collected: "2026-04-01"
summary_by: "auto-rss"
---

はじめに: Clinejection 事件
2026年2月、セキュリティエンジニア兼研究者のAdnan Khanさんが "Clinejection" と題したブログ記事を公開しました。AI コーディングツール Cline の GitHub Actions に存在した脆弱性チェーンにより、GitHub Issue を1件投稿するだけで本番環境のリリース用認証情報（VSCE_PAT、OVSX_PAT、NPM_RELEASE_TOKEN）を奪取でき、多数の開発者に影響し得るサプライチェーン攻撃に発展しうる状態でした。
詳細は上記のリンクから確認できます。
攻撃チェーンは5段階で構成されてい...
