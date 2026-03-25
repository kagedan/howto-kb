---
id: "2026-03-23-mobile-app-factory-が50イテレーションで止まる謎を30分で解明した方法-01"
title: "Mobile App Factory が50イテレーションで止まる謎を30分で解明した方法"
url: "https://zenn.dev/anicca/articles/2026-03-09-factory-50-limit-mystery"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-03-23"
date_collected: "2026-03-25"
summary_by: "auto-rss"
---

TL;DR
Mobile App Factory が約50イテレーションで止まる現象を調査し、「max 50 制限」は存在せず、実際は「1イテレーション = 1 User Story」ルールの自動リセット挙動が原因と判明。prd.json の passes フラグは信頼性が低く、progress.txt が真の完了記録（append-mode log）であることを発見した。

 前提条件

Mobile App Factory: Claude Code (CC) ベースの iOS アプリ自動生成システム

ralph.sh: Factory の制御スクリプト

prd.json: U...
