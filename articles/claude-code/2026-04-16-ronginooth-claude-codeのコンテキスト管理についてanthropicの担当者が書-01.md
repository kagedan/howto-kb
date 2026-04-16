---
id: "2026-04-16-ronginooth-claude-codeのコンテキスト管理についてanthropicの担当者が書-01"
title: "@ronginooth: Claude Codeのコンテキスト管理について、Anthropicの担当者が書いた神スレッドを見つけました。 特に印"
url: "https://x.com/ronginooth/status/2044577531677020308"
source: "x"
category: "claude-code"
tags: ["claude-code", "AI-agent", "x"]
date_published: "2026-04-16"
date_collected: "2026-04-16"
summary_by: "auto-x"
query: "Claude Code CLAUDE.md 書き方 OR コンテキスト管理 OR Handover"
---

Claude Codeのコンテキスト管理について、Anthropicの担当者が書いた神スレッドを見つけました。

特に印象的だったのが /rewind の使い方。

Claudeの出力やコード変更が「なんか違う…」と思ったとき、  
その場で「直して」と指示を追加するより、  
Escキー2回押し（または /rewind）で過去の時点に戻ってやり直す方が圧倒的に効果的。

理由はシンプル：
- 失敗した履歴を積み重ねるとコンテキストが汚れて性能が落ちる（Context Rot）
- rewindなら無駄な試行錯誤をきれいに捨てて、クリーンな状態から正しい方向で再スタートできる

「言うよりrewind」が鉄則、というアドバイスが目から鱗でした。

他にも：
- Compactと新規セッション（/clear）の使い分け
- Subagentsの活用法
- 100万トークン時代に意識すべきコンテキスト管理

Claude Codeを本気で使っている人は絶対読んでおくべきスレッドです。


--- 引用元 @trq212 ---
https://t.co/Ljzw0lmvao
