---
id: "2026-03-28-claude-codeで使うmarkdownファイルの種類と配置ガイド-01"
title: "Claude Codeで使うMarkdownファイルの種類と配置ガイド"
url: "https://zenn.dev/hageoyaji/articles/4258167f3c54c5"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "zenn"]
date_published: "2026-03-28"
date_collected: "2026-03-29"
summary_by: "auto-rss"
---

Claude Codeでは、用途の異なるMarkdownファイルを適切に配置することで、AIの振る舞いを制御できます。しかし種類が多く、正しく整理できないまま中途半端な環境を作ってしまっていました。
本記事では、どのファイルに何を書くべきか、どこに置くべきか、どのようなルートで呼び出されるかをサンプル付きで整理しました。

 ディレクトリ構成の全体像
my-project/
├── CLAUDE.md                          # プロジェクト全体の方針・構成
├── CLAUDE.local.md                    # 個人設定（.gitig...
