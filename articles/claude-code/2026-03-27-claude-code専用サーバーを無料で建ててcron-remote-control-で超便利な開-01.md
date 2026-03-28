---
id: "2026-03-27-claude-code専用サーバーを無料で建ててcron-remote-control-で超便利な開-01"
title: "# Claude Code専用サーバーを無料で建てて、cron + remote-control で超便利な開発環境を作る方法"
url: "https://zenn.dev/momozaki/articles/62d027e36657d6"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-03-27"
date_collected: "2026-03-28"
summary_by: "auto-rss"
---

使うサービス：Oracle Cloud Free Tier
Oracleの「Always Free」枠が異次元に太っ腹。



スペック
内容




CPU
Ampere A1（ARM）× 4コア


メモリ

24GB（永久無料）


ストレージ
200GB


料金
永久無料





 Step 1：インスタンス作成

Oracle Cloud に無料登録
Compute &gt; Create Instance
Shape: VM.Standard.A1.Flex / OS: Ubuntu 22.04
OCPU: 4 / Memory: 24GB（スライダー最大）



 ...
