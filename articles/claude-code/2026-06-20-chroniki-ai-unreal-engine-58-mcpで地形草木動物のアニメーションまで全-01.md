---
id: "2026-06-20-chroniki-ai-unreal-engine-58-mcpで地形草木動物のアニメーションまで全-01"
title: "@chroniki_ai: Unreal Engine 5.8 × MCPで、地形・草木・動物のアニメーションまで全部AIが作ったマップがやばすぎる"
url: "https://x.com/chroniki_ai/status/2068460398228144589"
source: "x"
category: "claude-code"
tags: ["claude-code", "MCP", "x"]
date_published: "2026-06-20"
date_collected: "2026-06-21"
summary_by: "auto-x"
query: "MCP server 設定 OR MCP 活用事例 OR MCP 連携"
---

Unreal Engine 5.8 × MCPで、地形・草木・動物のアニメーションまで全部AIが作ったマップがやばすぎる🐾

コードも手動配置もゼロ。
「こんな感じにして」って指示しただけで、ゲームのステージが丸ごとできあがってる。
どうやってるか、手順をまとめてみた。 https://t.co/j84CgXQwRr

そもそもMCPって何？ってところから説明するね🐾

MCP（Model Context Protocol）＝ ClaudeなどのAIを外部ツールと繋ぐ標準規格のこと。
Anthropicが2024年末に公開したオープン仕様で、今やClaude Code・Cursor・Windsurfなど主要なAIツールが対応してる。

Unreal Engine 5.8では、そのMCPプラグインが公式で組み込まれた。
つまり、Unreal Editorの中にサーバーが立ち上がって、Claude CodeやCodexがエディタを直接操作できるようになってる。

❌ 従来: 手でアセットを配置・コード書きながら調整の繰り返し
⭕ 今: 「この地形に木と動物を追加して」と打つだけ

動画でやってた手順、整理するね🐾

① Unreal Engine 5.8を開いて「Edit → Plugins」でUnreal MCPを有効化
② Editor Preferences → General → Model Context Protocol から「Auto Start Server」をON
　→ これでエディタ起動のたびに自動でMCPサーバーが立ち上がる（
③ Claude Code（またはCodex）のMCP設定ファイルにUnrealのサーバーアドレスを追加

④ Claude Codeのターミナルから「地形を生成して」「木を植えて」「動物を追加してアニメーションもつけて」と指示するだけ

→ つまり、ゲーム開発の「面倒な配置作業」をまるっとAIに任せられる段階に来てる。

動画で実際に作られたもの、改めて整理すると🐾

・地形（Terrain）の自動生成
・草木（Foliage）の自動配置
・動物キャラの追加
・待機・歩行アニメーションのセットアップ

全部Claude Code（+Codex）経由のMCP指示だけで完成してる。

Before: ゲーム開発者が数日かけて手で配置・調整
After: 自然言語で指示 → AIがエディタを直接操作して完成

ゲーム開発の話だけど、「AIに外部ツールを操作させる」という考え方自体は、Claude Codeを使ってる経営者・個人事業主の方にも直結する話だと思う。

→ MCPは「Claudeに仕事をさせる窓口」。ゲーム業界はその最前線を走ってる。

Claude Code × MCP、まだ試したことない方へ🐾

Unreal MCPは実験的機能だからドキュメント整備中の部分も多いけど、「AIに外部ツールを動かしてもらう」体験としては今一番わかりやすいデモだと思う。

Claude Codeを使ってる方は、まずMCP設定の公式ドキュメントを一回見てみて。
自分が日常で使ってるツールにも繋げられるかもしれないので、保存しておいて〜🐾

📹 元動画: @givros（X）

Claude Code、自分でも触ってみたくなった人へ。無料のオープンチャットで質問もし放題、特典も配布中です🤖

👉 参加リンクはプロフィール最上部の📌固定ポストから


--- 引用元 @chroniki_ai ---
https://t.co/Lw8OAyrvub
