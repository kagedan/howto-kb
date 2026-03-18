---
id: "2026-03-16-adk-agent-engineで-gemini-3-を使ったエージェントを実行する-01"
title: "[ADK] Agent Engineで Gemini 3 を使ったエージェントを実行する"
url: "https://zenn.dev/koichi73/articles/gemini-3-in-agent-engine"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "Gemini", "zenn"]
date_published: "2026-03-16"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

結論
方法は2つ。

 1. adk deploy agent_engine コマンド
--env_file 引数に、GOOGLE_CLOUD_LOCATION=global を含む .env ファイルへのパスを入れる。
uv run adk deploy agent_engine \
        --project=$PROJECT_ID \
        --region=$LOCATION_ID \
        --env_file=$ENV_FILE \    # ← `.env` ファイルへのパス
        --display_name="Greeting ...
