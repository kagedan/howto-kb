---
id: "2026-03-27-claude-codeでgithubのissueを自動作成pr作成自己成長させてみた-01"
title: "Claude CodeでGitHubのIssueを自動作成・PR作成・自己成長させてみた"
url: "https://zenn.dev/umamichi/articles/77db1fef83fdb7"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "OpenAI", "GPT", "zenn"]
date_published: "2026-03-27"
date_collected: "2026-03-28"
summary_by: "auto-rss"
---

毎朝6時に、勝手に仕事が始まる
朝起きてGitHubを開くと、AIが昨晩のうちにIssueを作っている。
「なるほど、こういう機能欲しかったな」と思ったらissueをつくり、ラベルを1個貼っておくだけ。あとはAIが実装してPRを作ってくれる。
しかも毎週月曜、そのAIは自分のプロンプトを書き換えて賢くなっていく。
こんな仕組みがあったら良いかもと思い、実際に作ってみました。

 何を作ったか


PdM AI: 毎朝6時にIssueを自動提案（OpenAI gpt-4o-mini）

plan-first フロー: plan-first ラベルを貼ると実装プランをコメント（Claud...
