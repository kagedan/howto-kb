---
id: "2026-04-03-claude-code-v2189のfullscreen-renderingモードno-flicke-01"
title: "Claude Code v2.1.89のFullscreen renderingモード（NO_FLICKER）"
url: "https://zenn.dev/firstloop_tech/articles/6c6cb8d4e77bd6"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-03"
date_collected: "2026-04-04"
summary_by: "auto-rss"
---

こんにちは、ファーストループテクノロジーの彦坂です。
2026年4月1日リリースのClaude Code v2.1.89で、ターミナルのちらつきを抑えるFullscreen renderingモードが追加されました。環境変数 CLAUDE_CODE_NO_FLICKER=1 で有効になります。現時点ではResearch previewの扱いです。

 背景
筆者の環境では、SSH経由やスマホからTermiusで接続し、tmux上でClaude Codeを使用しています。この構成では、長時間のセッションでログが蓄積してくるとターミナル描画のちらつきが顕著になっていました。
対策として、DE...
