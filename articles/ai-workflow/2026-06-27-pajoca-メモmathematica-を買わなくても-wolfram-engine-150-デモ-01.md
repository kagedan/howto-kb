---
id: "2026-06-27-pajoca-メモmathematica-を買わなくても-wolfram-engine-150-デモ-01"
title: "@Pajoca_: メモ：Mathematica を買わなくても Wolfram Engine 15.0 (デモ目的なら無料) をダウンロー"
url: "https://x.com/Pajoca_/status/2070865760436867404"
source: "x"
category: "ai-workflow"
tags: ["MCP", "GPT", "x"]
date_published: "2026-06-27"
date_collected: "2026-06-28"
summary_by: "auto-x"
query: "MCP server 設定 OR MCP 活用事例 OR MCP 連携"
---

メモ：Mathematica を買わなくても Wolfram Engine 15.0 (デモ目的なら無料) をダウンロードすれば Codex と連携可能。チャット画面で指示すれば Codex が書き上げたコードがエンジンに投げられ実行され、計算結果をそのまま利用できる。(MCP サーバーとして連携)
Mathematicaノートブックも生成できた

Wolframアカウントは必要だけど無料
https://t.co/f2M27MtKX3
↑手順。作業はChatGPTと相談推奨

注意点としてライセンスの制限で Wolfram Engine の同時起動数に制限があるみたいで、PowerShellでエンジンを立ち上げたままだと Codex側から Wolfram Local MCP が見えない問題が発生しました。(閉じた)
