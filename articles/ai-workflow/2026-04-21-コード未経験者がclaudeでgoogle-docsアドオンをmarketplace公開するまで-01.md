---
id: "2026-04-21-コード未経験者がclaudeでgoogle-docsアドオンをmarketplace公開するまで-01"
title: "コード未経験者がClaudeでGoogle DocsアドオンをMarketplace公開するまで"
url: "https://qiita.com/TateGaki/items/770a64b8fb490816a50f"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-04-21"
date_collected: "2026-04-21"
summary_by: "auto-rss"
query: ""
---

<aside>
📌

**この記事について**

- 対象：非エンジニア／AIで個人開発をやってみたい人／GAS開発者
- 読了時間：約10分
- 作ったもの：Google Docsの縦書きアドオン「TateGaki」
</aside>

## はじめに

2026年2月まで、私はコードを一行も書いたことがありませんでした。

そんな私が、Claude（Anthropic社のAI）との対話だけでGoogle Docsの縦書きアドオン「TateGaki」を開発し、Google Workspace Marketplaceの審査を通過して公開するに至りました。

この記事は、**非エンジニアがAIを相棒にアドオンを作った実装記録**です。GAS（Google Apps Script）の制約、Marketplace審査のハマりどころ、そして「バイブコーディング」での開発プロセスをまとめています。

- **作ったもの**：[TateGaki - 縦書きエディタ](https://workspace.google.com/marketplace/app/tategaki_%E7%B8%A6%E6
