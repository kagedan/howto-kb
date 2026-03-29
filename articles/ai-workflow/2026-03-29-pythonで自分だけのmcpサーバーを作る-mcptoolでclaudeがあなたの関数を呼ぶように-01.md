---
id: "2026-03-29-pythonで自分だけのmcpサーバーを作る-mcptoolでclaudeがあなたの関数を呼ぶように-01"
title: "Pythonで自分だけのMCPサーバーを作る ─ @mcp.tool()でClaudeがあなたの関数を呼ぶようになるまで"
url: "https://qiita.com/AI-SKILL-LAB/items/48992f453c48b87fd6a7"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "API", "Python", "qiita"]
date_published: "2026-03-29"
date_collected: "2026-03-29"
summary_by: "auto-rss"
---

# Pythonで自分だけのMCPサーバーを作る ─ @mcp.tool()でClaudeがあなたの関数を呼ぶようになるまで

なんか、これって地味に革命的だと思うんです。

自分で書いたPythonの関数を、ClaudeやCursorが「あ、これ使えばいいじゃん」って自動で選んで呼んでくれる時代になりました。その仕組みを支えているのが **MCP（Model Context Protocol）** というプロトコルです。

正直に言いましょう。MCPって名前は聞いたことがある、でも何をするものかよくわからない...という人、かなり多いと思います。最初そういう感じでした。

この記事では、MCPの概念を理解するところから始めて、Pythonで実際にMCPサーバーを作って、ClaudeがあなたのPython関数を呼ぶところまでをハンズオンで解説します。

**この記事で学べること:**

- MCPの仕組みを直感的に理解できる（コンセントの比喩で）
- `@mcp.tool()` デコレータで最初のMCPサーバーを作れる
- 外部API呼び出し・ファイル操作・データ処理の実践Toolを実
