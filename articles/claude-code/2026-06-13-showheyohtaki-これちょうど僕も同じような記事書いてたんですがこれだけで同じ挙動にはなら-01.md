---
id: "2026-06-13-showheyohtaki-これちょうど僕も同じような記事書いてたんですがこれだけで同じ挙動にはなら-01"
title: "@showheyohtaki: これちょうど僕も同じような記事書いてたんですが、これだけで同じ挙動にはならないと思います🤔 ①AGENTS.mdからC"
url: "https://x.com/showheyohtaki/status/2065696423778394508"
source: "x"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "AI-agent", "x"]
date_published: "2026-06-13"
date_collected: "2026-06-14"
summary_by: "auto-x"
query: "Claude Code hooks 使い方 OR subagents 設定 OR Claude Code スケジュール"
---

これちょうど僕も同じような記事書いてたんですが、これだけで同じ挙動にはならないと思います🤔

①AGENTS.mdからCLAUDE.mdを読ませるだけでは、肝心の skills / commands / agents / hooks などの挙動が再現できず、Claude Code側と同じになりません。これをやるにはCodex側の skills / hooks / subagents などに移行・確認が必要です。

②あとCodexにはClaude のように「@ファイル名」でimportできる機構がないので、正本にするならAGENTS.mdの方がいいです。Claude公式にも「AGENTS.md を使っているリポジトリでは CLAUDE.md に AGENTS.md と書けば両方で同じ指示を読める」とAGENTS.mdを正本にするように案内しています。

Codex、Cursor、その他大半のコーティングエージェントで「最初に読む設定ファイル名」としてスタンダードになってるのも「AGENTS.md」の方なので、こっちをベースにした方が汎用的な環境になりますよ！
