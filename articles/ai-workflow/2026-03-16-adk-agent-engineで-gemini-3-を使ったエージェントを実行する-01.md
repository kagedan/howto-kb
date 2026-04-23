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

## 結論

方法は2つ。

### 1. `adk deploy agent_engine` コマンド

`--env_file` 引数に、`GOOGLE_CLOUD_LOCATION=global` を含む `.env` ファイルへのパスを入れる。

```
uv run adk deploy agent_engine \
        --project=$PROJECT_ID \
        --region=$LOCATION_ID \
        --env_file=$ENV_FILE \    # ← `.env` ファイルへのパス
        --display_name="Greeting Agent" \
        sample_agent
```

### 2. pythonスクリプト

`agent_engines.create` のパラメータに以下を加える。

```
remote_agent = agent_engines.create(
    agent_engine=root_agent,
    display_name="Greeting Agent",
    requirements=[...],
    env_vars = {
        "GOOGLE_CLOUD_LOCATION": "global",  # ← globalリージョンの設定
    },
)
```

### サンプルコード

<https://github.com/Koichi73/adk-gemini-3-in-agent-engine>

## 何が起きてる？

* geminiの3系は現在(2026年3月16日)時点で `global` リージョンでしか使えない
* Agent Engineのデプロイの際、`global` リージョンを指定できない
* なので、Agent EngineにデプロイしたADKのエージェントをそのまま動かすと、モデル名が無いと404エラーが発生する

## デプロイした様子

**エージェント**:

```
from google.adk.agents.llm_agent import Agent

MODEL = "gemini-3-flash-preview"

root_agent = Agent(
    model=MODEL,
    name='root_agent',
    description="greeting",
    instruction="Please greet me cheerfully.",
)
```

**Agent Engineのプレイグラウンド**:  
![AgentEngine](https://static.zenn.studio/user-upload/deployed-images/d9ac4464ba3291a7364f2811.png?sha=8a7c248b51aeda9dfdbdcd7a0fcba9a56ac8704d)
