---
id: "2026-03-22-claude-code-cursor-のaiコンテキスト生成を自動化するcliツールを作った-01"
title: "Claude Code / Cursor のAIコンテキスト生成を自動化するCLIツールを作った"
url: "https://zenn.dev/s4kura/articles/orbit-ai-context-cli"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "zenn"]
date_published: "2026-03-22"
date_collected: "2026-03-23"
summary_by: "auto-rss"
---

はじめに
Claude Code や Cursor を使って開発していると、「なんでこのAI、プロジェクトの構造わかってないんだろう」と思う瞬間がある。Next.js のプロジェクトなのに Express 前提のコードを提案してきたり、既にある共通関数を無視して同じ処理を一から書き始めたり。AIは賢いけど、目の前のプロジェクトについては何も知らない状態でスタートする。
そこで重要になるのが CLAUDE.md や .cursorrules といったコンテキストファイルだ。プロジェクトの技術スタック、ディレクトリ構成、コーディング規約などを書いておくと、AIがそれを参照してくれる。Cl...
