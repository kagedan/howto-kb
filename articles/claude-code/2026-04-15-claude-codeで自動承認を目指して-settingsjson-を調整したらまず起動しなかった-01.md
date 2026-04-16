---
id: "2026-04-15-claude-codeで自動承認を目指して-settingsjson-を調整したらまず起動しなかった-01"
title: "Claude Codeで「自動承認」を目指して settings.json を調整したら、まず起動しなかった話"
url: "https://zenn.dev/aliyell/articles/9cdc77fd1a7b24"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-15"
date_collected: "2026-04-16"
summary_by: "auto-rss"
query: ""
---

Claude Code を使っていると、毎回の permission 確認が少しずつ重く感じてきます。
そこで今回は、できるだけ自動で進めつつ、安全性は落としすぎない構成を目指して、settings.json をいろいろ調整してみました。
やりたかったのは単純で、Bash コマンドを毎回手で承認しなくても進む状態を作ることです。
ただ、やってみると最初にぶつかったのは「起動しない」という問題でした。そこから sandbox、bypassPermissions、claude doctor、deny ルールを順番に見直していくことで、ようやく「どこを自動化し、どこを明示的に止めるべきか」が見...
