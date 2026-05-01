---
id: "2026-04-30-mcp-filesystemがserver-disconnectedで動かなくなった-bitlock-01"
title: "MCP FilesystemがServer disconnectedで動かなくなった → BitLocker解除が原因だったかも"
url: "https://zenn.dev/snow_rabbit/articles/31a8ae16ce42e6"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "zenn"]
date_published: "2026-04-30"
date_collected: "2026-05-01"
summary_by: "auto-rss"
---

はじめに
ローカルMCPサーバーのFileSystemツールが突然エラーを吐くようになりました。
再インストールで直ったあと、「そういえばあのタイミングで何かやったっけ？」と振り返ったところ、
Windows UpdateによるBitLocker回復キーの要求 → BitLocker無効化 という操作をしていたことに気づきました。
!
直接的な因果関係は確認できていませんが、同じ状況に遭遇する人がいるかもしれないと思い、注意喚起として共有します。

 発生した事象（事実ベース）

ある日からローカルMCPサーバーのFileSystemツールが Server disconnected...
