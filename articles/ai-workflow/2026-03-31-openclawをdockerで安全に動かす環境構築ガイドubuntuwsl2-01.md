---
id: "2026-03-31-openclawをdockerで安全に動かす環境構築ガイドubuntuwsl2-01"
title: "OpenClawをDockerで安全に動かす！環境構築ガイド【Ubuntu/WSL2】"
url: "https://zenn.dev/kanpachioishi/articles/openclaw-setup"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-03-31"
date_collected: "2026-04-01"
summary_by: "auto-rss"
---

はじめに
OpenClawを知っていますか？
GitHubスター25万超、史上最速で成長しているオープンソースのAIエージェントフレームワークです。ローカルで動く自律型AIアシスタントで、WhatsApp、Discord、Slackなど23種類以上のチャネルに対応しています。
ただし、AIが自律的にファイル操作やコマンド実行を行うため、セキュリティリスクがあります。実際にワンクリックでリモートコード実行が可能な脆弱性（CVE-2026-25253）や、権限昇格によるRCE（CVE-2026-32922）など、複数の深刻なCVEが報告されています。
そこでこの記事では、Dockerでサ...
