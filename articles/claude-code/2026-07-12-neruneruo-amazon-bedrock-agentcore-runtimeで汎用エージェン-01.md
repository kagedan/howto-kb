---
id: "2026-07-12-neruneruo-amazon-bedrock-agentcore-runtimeで汎用エージェン-01"
title: "@neruneruo: Amazon Bedrock AgentCore Runtimeで汎用エージェントを運用しているときにSkillsでsc"
url: "https://x.com/neruneruo/status/2076293093729706449"
source: "x"
category: "claude-code"
tags: ["API", "AI-agent", "x"]
date_published: "2026-07-12"
date_collected: "2026-07-13"
summary_by: "auto-x"
query: "Claude Code CLAUDE.md 書き方 OR コンテキスト管理 OR Handover"
---

Amazon Bedrock AgentCore Runtimeで汎用エージェントを運用しているときにSkillsでscriptを動かそうとすると依存関係管理が大変だからCodeInterpreterに逃がしたい。でも、Write Files Toolsはファイルコンテンツを渡さないといけないからコンテキストを消費してしまう。これを回避するには(1/2)

Amazon Bedrock AgentCoreのRuntimeとCodeInterpreterにAmazon S3のPut/GetObjectの権限を付与して、S3 API経由でファイルパスで渡せばコンテキスト消費しない。Skillsのscriptをこの方法で渡して、コマンド実行をCodeIntepreter上で行えば、依存関係でエージェントを太らせることなく対応可能！(2/2)
