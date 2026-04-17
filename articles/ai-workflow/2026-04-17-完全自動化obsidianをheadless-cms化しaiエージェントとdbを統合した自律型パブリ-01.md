---
id: "2026-04-17-完全自動化obsidianをheadless-cms化しaiエージェントとdbを統合した自律型パブリ-01"
title: "# 【完全自動化】ObsidianをHeadless CMS化し、AIエージェントとDBを統合した「自律型パブリッシング・パイプライン」の構"
url: "https://zenn.dev/hideki_tamae/articles/5a0e8f92293c6d"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-17"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

はじめに
「記事を書く」という行為には、創作以外の「泥臭い作業（メタデータ作成、DB記録、フォルダ整理）」が多すぎます。
本記事では、Obsidianを「思想の源泉」とし、n8n、Claude、PostgreSQLを組み合わせて、「ファイルを置くだけで世界へ思想が放流される」自律型パブリッシング・システムを構築した全記録を共有します。

 構築したシステムの全体像
単なる「自動投稿」ではありません。
以下のプロセスを1ミリの手出しもせず完結させます。



Trigger: Obsidianの特定フォルダにMarkdownを配置（Cron実行）

Fetch: Cloudflare ...
