---
id: "2026-06-11-gen-techcamp-ついに来たiphonemacアプリからclaudeが直接呼べるように-ap-01"
title: "@GEN_TECHCAMP: 【ついに来た】iPhone/MacアプリからClaudeが直接呼べるように📱 Appleの開発者向けAI基盤「Found"
url: "https://x.com/GEN_TECHCAMP/status/2064872188533215520"
source: "x"
category: "ai-workflow"
tags: ["API", "x"]
date_published: "2026-06-11"
date_collected: "2026-06-11"
summary_by: "auto-x"
query: "Claude プロンプト 書き方 OR Claude 業務効率化 実例"
---

【ついに来た】iPhone/MacアプリからClaudeが直接呼べるように📱
Appleの開発者向けAI基盤「Foundation Models」が、Claudeに対応しました。

iPhoneやMacのアプリに、Claudeを組み込みやすくなった、という話です。

🔀 何がうれしいのか
これまでアプリに搭載できるのはApple端末内のAIが中心でした。今回からは、Apple標準のAIと同じ書き方のまま、呼び先をClaudeに差し替えるだけで使えるようになります。

⚖️ 使い分けがキモ
・軽い処理 → 端末内AI（高速・オフライン・プライベート）
・重い処理 → Claude（長い文章、高度な推論、Web検索やコード実行）
このスイッチをアプリ側が選べるのがポイントです。

🔒 経路はアプリから直接Claudeへ
Appleは間に入らず、プロンプトや応答を見ません。課金はAnthropic側に通常のAPI料金で発生します。

🛠 現状の注意点
対応はiOS 27/macOS 27など、いずれもベータ。正式版前に仕様が変わる可能性があります。

これからのアプリは「軽い処理は端末内、重い処理はクラウドのAI」を自然に行き来する形が当たり前になっていきそうです🚀


--- 引用元 @ClaudeDevs ---
New for Apple developers: Foundation Models support for Claude lets developers use Apple's Foundation Models framework to call Claude for multi-step reasoning, code generation, and longer context. https://t.co/7EbHlWBBSe

Typed outputs from Apple's Foundation Models framework drop straight into your Claude request, so you're sending structured data rather than raw user text. Responses stream back into the same SwiftUI view.

Read more in the docs:
https://t.co/2jbbef73kv
