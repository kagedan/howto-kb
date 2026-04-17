---
id: "2026-04-16-claude-opus-46-の-1m-コンテキストで-170-ファイルの-terraform-リポ-01"
title: "Claude Opus 4.6 の 1M コンテキストで 170 ファイルの Terraform リポジトリを読ませてみた"
url: "https://zenn.dev/geneg/articles/claude-opus-4-6-1m-terraform"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "zenn"]
date_published: "2026-04-16"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

はじめに
Claude Opus 4.6 の 1M トークン（100万トークン）コンテキスト が使えるようになってから、大規模リポジトリの扱いがガラッと変わりました。
これまで Claude Code で大きな Terraform リポジトリを扱うときは、

「関連ファイルだけ絞って読ませる」
「Agent tool で分割探索させる」
「要点だけまとめた memory を持たせる」

といった工夫が必要でした。1M コンテキストはこの前提を一度リセットします。
この記事では、170 ファイル以上ある実プロジェクトの Terraform を実際に 1M コンテキストで扱ってみた体験を...
