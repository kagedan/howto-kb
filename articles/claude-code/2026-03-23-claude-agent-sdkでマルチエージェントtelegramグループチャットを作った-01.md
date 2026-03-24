---
id: "2026-03-23-claude-agent-sdkでマルチエージェントtelegramグループチャットを作った-01"
title: "Claude Agent SDKでマルチエージェントTelegramグループチャットを作った"
url: "https://zenn.dev/acropapa330/articles/zenn_multi_agent_telegram"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "zenn"]
date_published: "2026-03-23"
date_collected: "2026-03-24"
summary_by: "auto-rss"
---

はじめに
「Claude Code のエージェントに1つずつ Telegram Bot を割り当てて、グループチャットで議論させたら面白くない？」
そんなアイデアから作り始めたら、意外とハマりどころが多くて面白かったので記事にしました。
実際にこんな感じでエージェント同士が @メンション でバトンを渡し合いながら議論します：

テキストで表すとこんな流れです：
ユーザー: フィジカルAIは今後社会にどう実装されると思う？

🔍 Researcher: CES2026でも注目のフィジカルAI、製造・物流・医療・自動運転の
               4領域が先行しそうです。@Acro...
