---
id: "2026-06-24-github-copilot-で-foundry-claude-を利用する-01"
title: "GitHub Copilot で Foundry Claude を利用する"
url: "https://qiita.com/baku2san/items/5239399404abb1523b03"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "GPT", "qiita"]
date_published: "2026-06-24"
date_collected: "2026-06-25"
summary_by: "auto-rss"
query: ""
---

# 背景

2026/6/1 の RU to Credit 後、上限拡張をしてもらうまでに、Foundry AIで Claude Code を利用することになった。

ただ、せっかくなら、GitHub Copilot の使い勝手で使えたほうが良いねってことで、BYOKの設定をした際の備忘録

直接 settings.json を編集してもいいけど、以下理由から、GUI使ったほうが良いかな、と

- API Key を使う際にも Secret に簡単に登録できるので、設定共有が楽
- どこに設定ファイルがあるんだっけって探さなくてよい :sweat: 

# 設定

1. VS Code のモデル選択で、⚙️
   ![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/120072/25ccb55e-3752-4ce8-823f-5e5f0b2f5238.png)

2. `Add Models` から、 `custom endpoint`
   ![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/120072/c45cd621-3911-4192-a7de-18d0c7a96e38.png)

1. グループ名を入れておく
   ![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/120072/63ce9a45-792a-4bfd-9cd4-81e39ea00662.png)

1. API Key を入力
   ![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/120072/5c1a17ea-5527-47c2-9f2d-80a65209a170.png)

   :::note info
   ここから入れる事で、自動的に secret として記録されます
   :::

1. で、進めると以下のような設定ファイルに飛ぶので、デプロイしてアルモデルを適当に追加すればOK

```json: 設定例
[
  {
    "name": "Copilot",
    "vendor": "copilot",
    "settings": {
      "gpt-5.4": {
        "reasoningEffort": "xhigh"
      }
    }
  },
  {
    "name": "Azure Foundry",
    "vendor": "customendpoint",
    "apiKey": "${input:chat.lm.secret.3e64bd91}",
    "models": [
      {
        "id": "claude-opus-4-8",
        "name": "claude-opus-4-8",
        "url": "https://{name}.services.ai.azure.com/anthropic/v1/messages",
        "toolCalling": true,
        "vision": true,
        "maxInputTokens": 200000,
        "maxOutputTokens": 32000
      },
      {
        "id": "claude-sonnet-4-6",
        "name": "claude-sonnet-4-6",
        "url": "https://{name}.services.ai.azure.com/anthropic/v1/messages",
        "toolCalling": true,
        "vision": true,
        "maxInputTokens": 200000,
        "maxOutputTokens": 32000,
        "thinking": true,
        "supportsReasoningEffort": [
          "low",
          "medium",
          "high"
        ]
      },
      {
        "id": "claude-haiku-4-5",
        "name": "claude-haiku-4-5",
        "url": "https://{name}.services.ai.azure.com/anthropic/v1/messages",
        "toolCalling": true,
        "vision": true,
        "maxInputTokens": 128000,
        "maxOutputTokens": 16000
      }
    ]
  }
]
```
