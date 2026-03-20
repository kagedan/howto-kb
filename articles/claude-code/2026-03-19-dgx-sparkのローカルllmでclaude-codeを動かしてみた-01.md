---
id: "2026-03-19-dgx-sparkのローカルllmでclaude-codeを動かしてみた-01"
title: "DGX SparkのローカルLLMでClaude Codeを動かしてみた"
url: "https://zenn.dev/caists/articles/ed05fa15da72ee"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "LLM", "zenn"]
date_published: "2026-03-19"
date_collected: "2026-03-20"
summary_by: "auto-rss"
---

DGX Sparkが手元にあるなら、ローカルLLMでClaude Codeを動かせないだろうか？
そう思って試してみたら、意外とちゃんと動いた。ファイルの読み書き、コマンド実行、コード探索といった基本的なコーディング作業が、Anthropic APIなしでローカル完結でできるようになり、Webアプリを約1時間で自律的に構築するところまで到達した。
この記事では、そのために作った「Claude Local Proxy」の仕組みと、小型モデルをClaude Codeで実用するために必要だった工夫をまとめておく。
ソースコードはGitHubで公開している。
https://github.com...
