---
id: "2026-03-25-スマホからmacを操作claude-dispatchを使ってみた-01"
title: "スマホからMacを操作！Claude Dispatchを使ってみた"
url: "https://qiita.com/wozisagi/items/dce4fbe55bcb1fa3b850"
source: "qiita"
category: "cowork"
tags: ["cowork", "qiita"]
date_published: "2026-03-25"
date_collected: "2026-03-26"
summary_by: "auto-rss"
---

## はじめに

2026年3月23日、Anthropicが **Claude Dispatch** をリリースしました。
「スマートフォンからClaudeに指示を出すと、自宅のMacが勝手に作業してくれる」という機能です。Claudeのリリースを確認したときに、OpenClawみたいでセットアップも簡単そうと思ったので実際にやってみました。

## 環境

| 項目 | バージョン・内容 |
|------|----------------|
| OS（デスクトップ） | macOS |
| OS（モバイル） | iOS |
| 利用サービス | Claude Cowork（Claude Pro プラン） |
| 確認時点 | 2026年3月23日 |

:::note warn
Claude Dispatch は **Claude Pro（$20/月）以上のプランが必要**です。無料プランでは利用できません。
:::

## Claude Dispatch とは

まず軽く概要を整理します。

Claude Dispatch は、Anthropicの **Claude Cowork
