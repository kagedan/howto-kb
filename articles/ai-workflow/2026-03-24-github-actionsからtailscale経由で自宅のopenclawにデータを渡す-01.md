---
id: "2026-03-24-github-actionsからtailscale経由で自宅のopenclawにデータを渡す-01"
title: "GitHub ActionsからTailscale経由で自宅のOpenClawにデータを渡す"
url: "https://zenn.dev/pepabo/articles/f1499dac52c93c"
source: "zenn"
category: "ai-workflow"
tags: ["API", "LLM", "zenn"]
date_published: "2026-03-24"
date_collected: "2026-03-25"
summary_by: "auto-rss"
---

はじめに
自宅のRaspberry Pi 4BでOpenClawを動かしています。OpenClawはLLMを使ったAIエージェント基盤で、Webhook APIも用意されているので外部からプロンプトを渡すこともできます。
一方、tailscale/github-actionを使えばGitHub Actionsのランナーを自宅のTailnetに参加させられることを知り、この2つを組み合わせたら面白そうだと感じていました。
私の場合は、GitHub Actionsで定期的にWebサイトをスクレイピングするgit scrapingを運用しています。そこで、収集データの差分をTailscal...
