---
id: "2026-04-22-claude-code-の-precompact-hook-で幻覚編集を封じた話-01"
title: "Claude Code の PreCompact hook で『幻覚編集』を封じた話"
url: "https://zenn.dev/ai_arai_ally/articles/20260421-1601-claude-code-precompact-hook"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "zenn"]
date_published: "2026-04-22"
date_collected: "2026-04-23"
summary_by: "auto-rss"
---

3時間かけて積み上げたリファクタが、たった一言で吹き飛んだ。
「src/utils/retry.ts を編集しました」——そのファイルは、存在しない。
ls しても、git status しても、どこにもない。でも Claude Code は確信を持って「編集した」と言う。
正直に言うと、最初は自分が寝ぼけてるのかと思った。でも違った。これは context compaction が走った直後に起きる、構造的な幻覚だ。
今日はその幻覚を、v2.1.83 で追加された PreCompact hook と CLAUDE.md への防御指示、そして git チェックポイントの3段構えで封じた話...
