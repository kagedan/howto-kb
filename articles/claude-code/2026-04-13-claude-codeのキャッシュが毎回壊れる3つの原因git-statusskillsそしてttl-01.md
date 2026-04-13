---
id: "2026-04-13-claude-codeのキャッシュが毎回壊れる3つの原因git-statusskillsそしてttl-01"
title: "Claude Codeのキャッシュが毎回壊れる3つの原因——git status、skills、そしてTTLサイレント変更"
url: "https://qiita.com/yurukusa/items/e8a8af7356cacd4fb371"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "qiita"]
date_published: "2026-04-13"
date_collected: "2026-04-13"
summary_by: "auto-rss"
query: ""
---

<!-- FC完了: ①#47098/#47107実在確認済み(session69) ②CLAUDE_CODE_DISABLE_GIT_INSTRUCTIONS=#47107報告者が言及 ③Token Checkup/Security Checkup URL 200OK確認済み ④#47108=16%消費実在確認済み ⑤#46829=Cache TTL 1h→5m(WebSearch確認4/13) ⑥#42338=--continue/resume キャッシュ無効化(WebSearch確認4/13) -->

Claude Codeのプロンプトキャッシュが壊れると、トークン消費が数倍に跳ね上がる。

「昨日まで普通に使えていたのに、今日は5時間制限の16%が一瞬で消えた」——[#47108](https://github.com/anthropics/claude-code/issues/47108)の報告だ。原因はキャッシュの仕組みにある。

## プロンプトキャッシュとは

Claude Codeは毎ターン、システムプロンプト（CLAUDE.md、skills、設定情報）をAPIに
