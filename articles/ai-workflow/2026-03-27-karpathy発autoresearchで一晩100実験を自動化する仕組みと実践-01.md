---
id: "2026-03-27-karpathy発autoresearchで一晩100実験を自動化する仕組みと実践-01"
title: "Karpathy発AutoResearchで一晩100実験を自動化する仕組みと実践"
url: "https://zenn.dev/0h_n0/articles/28e8fe4721f315"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-03-27"
date_collected: "2026-03-28"
summary_by: "auto-rss"
---

Karpathy発AutoResearchで一晩100実験を自動化する仕組みと実践

 この記事でわかること

AutoResearchの3ファイルアーキテクチャ（prepare.py / train.py / program.md）の設計思想と役割
5分固定予算の実験ループで一晩100回以上のML実験を自律実行する仕組み
SkyPilotによるマルチGPU並列化で910実験/8時間を実現した拡張手法
AutoKernelなど派生プロジェクトに見る「AutoResearchパターン」の汎用的な適用方法
Goodhart's Lawやスケール制約など、自律実験ループ運用時の落とし穴と対...
