---
id: "2026-04-18-claude-code-obsidian-vault-で作る何でも相談プロジェクト-フォルダ構成cl-01"
title: "Claude Code × Obsidian Vault で作る「何でも相談」プロジェクト ― フォルダ構成・CLAUDE.md・MCP設定まで全公開"
url: "https://qiita.com/htani0817/items/0cb5e8f91fa64fb9ba8c"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "qiita"]
date_published: "2026-04-18"
date_collected: "2026-04-19"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Code を使い始めて少し経つと、多くの人が同じ問題にぶつかります。

- Claude が生成した `.md` がプロジェクトルート直下に散乱する
- 「あの調査メモどこ行った？」が週1で起きる
- Mac と Windows を行き来するたびにパス問題でつまずく

この記事では、私が実際に運用している「何でも相談-pj」という Claude Code 専用プロジェクトの中身を、**フォルダ構成・`CLAUDE.md`・`.claude/settings.json`・`.mcp.json` まで全部公開**します。Obsidian の Vault をプロジェクトに内包することで、Claude Code の成果物を自動で整理し、さらに後から Obsidian のグラフビューで知識を俯瞰できる、という構成です。

対象読者：Claude Code を使い始めた〜中級者。Obsidian は未経験でも OK。

## プロジェクト全体像

まず設計の軸になっている3つの原則を先に書きます。この3つが全ての構成判断を支えています。

1. **成果物は全部 O
