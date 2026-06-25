---
id: "2026-06-23-windows11antigravity-20-トークン節約術-skillでpc内検索を賢くする-01"
title: "【Windows11】Antigravity 2.0 トークン節約術 ― SKILLでPC内検索を賢くする"
url: "https://zenn.dev/sosa/books/antigravity-token-saving-skill"
source: "zenn"
category: "antigravity"
tags: ["antigravity", "Python", "zenn"]
date_published: "2026-06-23"
date_collected: "2026-06-25"
summary_by: "auto-rss"
query: ""
---

# 【Windows11】Antigravity 2.0 トークン節約術 ― SKILLでPC内検索を賢くする

Windows 11 環境の Antigravity 2.0 で、PC内のファイル検索時にトークン消費が爆発する問題を解決した実践記録です。PythonスクリプトからPowerShellの Select-String を呼び出し、2つのキーワードによる行単位のAND検索でファイルを事前に絞り込むSKILLを構築。1,095ファイル・18.5MBのObsidian Vaultに対して無料プランでトークン消費を20％以上使っていたタスクを1〜7%に抑えることに成功しました。（txtやmdファイルなど、テキストとして読み取れるファイルを検索します）
