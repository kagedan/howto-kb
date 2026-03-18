---
id: "2026-03-17-codexにいつの間にか入っていたopenai-docs-skillの中身を読み解く-01"
title: "Codexにいつの間にか入っていたopenai-docs skillの中身を読み解く"
url: "https://zenn.dev/purple_matsu1/articles/20260317-codex-openai-docs-skill"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "OpenAI", "zenn"]
date_published: "2026-03-17"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

はじめに
.codex/skills/.system にいつの間にか openai-docs が入っていたので、中身を調査しました。
Claude Code には以前から /claude-api という同様の skill がありましたが、同じ考え方が Codex にも来ていたようです。その中身を読み解きながら「skill とは何をしているのか」を整理してみます。

 openai-docs skill の中身
openai-docs skill のディレクトリを開いてみると、OpenAI のドキュメント本体は一切入っていません。
じゃあ何が入っているのか。中身はこの 3 つです。

...
