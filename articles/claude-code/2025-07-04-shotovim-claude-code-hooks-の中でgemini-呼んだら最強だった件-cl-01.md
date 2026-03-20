---
id: "2025-07-04-shotovim-claude-code-hooks-の中でgemini-呼んだら最強だった件-cl-01"
title: "@shotovim: 【Claude Code Hooks の中でGemini 呼んだら最強だった件】
Claude Code の Hooks"
url: "https://x.com/shotovim/status/1940968054638493800"
source: "x"
category: "claude-code"
tags: ["claude-code", "Gemini", "x"]
date_published: "2025-07-04"
date_collected: "2026-03-20"
summary_by: "auto-x"
---

【Claude Code Hooks の中でGemini 呼んだら最強だった件】
Claude Code の Hooks で Gemini を呼ぶことで、Claude Code が生成した結果に対して、さらに追加のプロンプトを即座に適用できた。この体験めちゃくちゃいい。

今回は Hooks の Stop で新規作成や修正による差分ファイルを検知し、そのファイルに対して Gemini にタグ付けしてもらうスクリプトを実行した。これでタグ付けプロンプトが不要に。（詳しくは動画参照：左＝ターミナル実行画面、右＝Obsidian）

なぜ Gemini かというと、Claude Code Hooks の中で Claude Code 自体を再帰的に呼び出すと無限ループで処理がキャンセルされてしまうため。そのため、Hooks 内では Claude ではなく外部の Gemini を呼び出す構成にすることで、この問題を回避できる。
