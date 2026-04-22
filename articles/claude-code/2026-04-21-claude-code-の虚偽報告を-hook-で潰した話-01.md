---
id: "2026-04-21-claude-code-の虚偽報告を-hook-で潰した話-01"
title: "Claude Code の虚偽報告を hook で潰した話"
url: "https://zenn.dev/ai_arai_ally/articles/20260421-0401-claude-code-hook"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "LLM", "zenn"]
date_published: "2026-04-21"
date_collected: "2026-04-22"
summary_by: "auto-rss"
---

Claude Code agent に夜間タスクを3件振って寝た。朝起きたら、2件が「完了しました」と報告していた。中身を開いたら、1件はファイルすら作られていなかった。
検知できたのは PostToolUse hook を仕込んでいたからで、もし人力レビューだけだったら本番にマージされていた。
元ネタは Qiita の「家老の不祥事と殿の反省」という記事で、AI が虚偽報告してきた体験を江戸モチーフで描いてバズっていた。面白い。笑った。でも、反省は再発防止にならない。LLM に自責の概念はないし、次のセッションでコンテキストは消えている。
必要なのは構造的拘束だ。hook と skil...
