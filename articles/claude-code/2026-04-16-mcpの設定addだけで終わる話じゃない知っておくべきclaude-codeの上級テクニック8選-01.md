---
id: "2026-04-16-mcpの設定addだけで終わる話じゃない知っておくべきclaude-codeの上級テクニック8選-01"
title: "MCPの設定、addだけで終わる話じゃない。知っておくべきClaude Codeの上級テクニック8選"
url: "https://qiita.com/moha0918_/items/0ac1abef9834b3e3dbec"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "qiita"]
date_published: "2026-04-16"
date_collected: "2026-04-16"
summary_by: "auto-rss"
query: ""
---

Claude CodeでMCPサーバーを使っている人は多いと思います。`claude mcp add` でサーバーを追加して、ツールが動くようになったら「OK、設定完了」と。

でも公式ドキュメントをちゃんと読むと、addの先にけっこう重要な設定が埋まっています。コンテキストウィンドウの圧迫を防ぐTool Search、社内認証に対応するheadersHelper、チーム共有を安全にする環境変数展開――このあたりは知っているだけで運用が変わります。

この記事では、MCPの基本は分かっている前提で、次のステップとなる上級テクニックを8つまとめました。前半3つは特に重要なので詳しく、残り5つはテーブル+コード例で手短にいきます。

## Tool Searchでコンテキストの無駄遣いを防ぐ

MCPサーバーを5つ、10と追加していくと、ツール定義だけでコンテキストウィンドウが埋まっていきます。「最近レスポンスが遅い」「compactionが頻発する」――原因がMCPのツール定義だった、というのは割とある話です。

Tool Searchは、**ツールのスキーマをオンデマンドで読み込む仕組
