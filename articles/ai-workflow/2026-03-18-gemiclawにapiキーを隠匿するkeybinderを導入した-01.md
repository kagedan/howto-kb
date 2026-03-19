---
id: "2026-03-18-gemiclawにapiキーを隠匿するkeybinderを導入した-01"
title: "gemiclawにAPIキーを隠匿するkeybinderを導入した。"
url: "https://zenn.dev/nishina__n/articles/2fd0f90086841b"
source: "zenn"
category: "ai-workflow"
tags: ["API", "zenn"]
date_published: "2026-03-18"
date_collected: "2026-03-19"
summary_by: "auto-rss"
---

現在開発している軽量・セキュアなAIエージェントのgemiclawにAIエージェントからAPIキーが見えないようにするkeybinderを構想・作成した。
リポジトリ：https://github.com/Nishina-N/gemiclaw

 AIエージェントのリスク
AIエージェント利用時のセキュリティリスクには以下のようなものがあると思う。

プロンプトインジェクション
外部から取得したコンテンツ（Webページ、Discordメッセージ等）に悪意ある指令が埋め込まれ、エージェントがそれに従って意図しない行動をとる。
機密情報の漏洩
APIキー、トークン、個人情報などをエージェント...
