---
id: "2026-05-18-aws-lambdaでclaude-code-agent-sdk利用時のタイムアウト解決方法-01"
title: "AWS LambdaでClaude Code Agent SDK利用時のタイムアウト解決方法"
url: "https://zenn.dev/metalmental/articles/20260518_anthropic-timeout"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "zenn"]
date_published: "2026-05-18"
date_collected: "2026-05-19"
summary_by: "auto-rss"
query: ""
---

## 背景

Strands Agentsやめて、ClaudeのAgent SDKをLambdaで利用しようとしたらtimeoutが発生して動作しなかった

## 結論

![timeout](https://static.zenn.studio/user-upload/deployed-images/5f7046beabc19f8e5a509ac8.png?sha=1900d72fb34804848582eced933e74ff4b1ce042)

Lambdaの環境変数にキー: `HOME`、値: `/tmp` を設定すると解決しました

Claude Platform on AWSでも同様でした

## 余談

現場でもそうですが、エラーログが出力されていない場合がとてもしんどいです...w
