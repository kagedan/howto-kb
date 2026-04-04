---
id: "2026-04-03-claude-codeのskill作成中に見かけた-user-invocableを調べてみた-01"
title: "🔍Claude CodeのSkill作成中に見かけた user-invocableを調べてみた"
url: "https://zenn.dev/dely_jp/articles/76842757cce7b6"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-03"
date_collected: "2026-04-04"
summary_by: "auto-rss"
---

こんにちは、クラシルiOSエンジニアのkeiです。
皆さん、Skillを作るときに生成されたSKILL.mdの中身をちゃんとチェックしていますか？ 私はほぼAIに任せきりで、「動いたからヨシ！」で済ませがちでした。
でも先日、たまたまヘッダー設定を眺めていたら知らない設定を見つけて、「これ何だろう」と調べたら意外と面白かったので共有します。

 きっかけ
クラシルのiOSアプリで、Applovin SDKの更新作業がありました。更新の手順やチェックリストがそこそこあるので、それをClaude CodeのSkillとしてまとめるPRを出していたときのことです。
SKILL.mdのヘッダー設...
