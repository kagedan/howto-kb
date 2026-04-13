---
id: "2026-04-13-claude-code-kun-no-default-effort-level-wo-max-ni-01"
title: "Claude Codeくんのデフォルトeffort levelをmaxに固定する"
url: "https://zenn.dev/madebyjun/articles/8f7d6bb9286b95"
source: "notebooklm"
category: "claude-code"
tags: ["claude-code", "effort-level", "configuration", "notebooklm"]
date_published: "2026-04-13"
date_collected: "2026-04-13"
summary_by: "auto-nlm"
---

Claude Code v2.1.68でデフォルトの推論深度が「medium」に変更されたことによる品質低下の問題と、その解決策を解説する記事。環境変数CLAUDE_CODE_EFFORT_LEVEL=maxを.zshrcに追加する方法が最も確実で、settings.jsonの既知バグやCLIフラグの手間を回避できる。設定の優先順位は環境変数 > CLIフラグ > settings.json > モデルデフォルトの順であり、ultrathinkキーワードより環境変数のmaxの方がより高い推論レベルを提供する。
