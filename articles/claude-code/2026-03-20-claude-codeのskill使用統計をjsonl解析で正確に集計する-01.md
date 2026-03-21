---
id: "2026-03-20-claude-codeのskill使用統計をjsonl解析で正確に集計する-01"
title: "Claude CodeのSkill使用統計をJSONL解析で正確に集計する"
url: "https://zenn.dev/rinomiya_sumoru/articles/claudecode-skill-usage-tracking"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-03-20"
date_collected: "2026-03-22"
summary_by: "auto-rss"
---

はじめに
Claude Code に登録した Skill が増えてきたとき、「どのSkillを一番使っているんだろう？」と気になりました。
スモルには現在、zenn-article・note-article・add-task・idea-scout など10本近くのSkillが登録されています。育てていくうちに「どれが実際に役立っているか」「使われていないSkillは整理すべきか」を判断したくなりました。でも感覚だけでは正確にわからない。そこで、Skillの使用統計を自動収集する仕組みを作ることにしました。

 まず hooks を試みた
Claude Code の settings...
