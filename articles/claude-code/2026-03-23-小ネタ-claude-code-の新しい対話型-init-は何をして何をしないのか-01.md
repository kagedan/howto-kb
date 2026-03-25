---
id: "2026-03-23-小ネタ-claude-code-の新しい対話型-init-は何をして何をしないのか-01"
title: "[小ネタ] Claude Code の新しい対話型 `/init` は何をして何をしないのか"
url: "https://zenn.dev/foxtail88/articles/claude-new-init"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "zenn"]
date_published: "2026-03-23"
date_collected: "2026-03-25"
summary_by: "auto-rss"
---

はじめに
CLAUDE_CODE_NEW_INIT=1 と環境変数を設定することで、Claude Code が対話的にCLAUDE.mdを作成してくれるという情報をXで拝見しました。

たしかに公式ドキュメントの環境変数一覧にもデビューしています。
https://code.claude.com/docs/en/env-vars#:~:text=CLAUDE_CODE_NEW_INIT

Set to true to make /init run an interactive setup flow. The flow asks which files to generate, inc...
