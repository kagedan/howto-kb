---
id: "2026-06-24-claude-tagに学ぶslack常駐エージェントの作り方2026年6月aiエージェント最新動向-01"
title: "Claude Tagに学ぶ「Slack常駐エージェント」の作り方｜2026年6月AIエージェント最新動向"
url: "https://zenn.dev/kairosai/articles/9013d71da9986d"
source: "zenn"
category: "ai-workflow"
tags: ["API", "LLM", "OpenAI", "Gemini", "GPT", "Python"]
date_published: "2026-06-24"
date_collected: "2026-06-26"
summary_by: "auto-rss"
query: ""
---

## はじめに

2026年6月、Anthropicが「Claude Tag」を発表しました。Slack上で `@Claude` とメンションするだけで、AIが組織の文脈を踏まえてタスクを実行する——いわば「Slack常駐の仮想社員」です。

本記事では、自分でも作れる「Slack常駐エージェント」の最小構成をコード付きで解説します。OpenAIのScheduled TasksやGoogleのGemini Sparkも同じ「自律エージェント」の方向を向いており、その仕組みの理解は2026年のエンジニアの必須スキルになりつつあります。

## 2026年6月のエージェント関連トピック

| 提供元 | 機能 | 特徴 |
| --- | --- | --- |
| Anthropic | Claude Tag | Slackメンションで起動する組織横断エージェント |
| OpenAI | Scheduled Tasks | ChatGPTで定期実行・監視・リマインド |
| Google | Gemini Spark | 個人専属のAIエージェント＋Daily Brief |

共通点は「ユーザーの代わりに、トリガーに応じて自律的にタスクを実行する」という設計思想です。

## 最小構成：Slackメンションで動くエージェント

Bolt for Python と Anthropic API で「メンションされたら応答するエージェント」の骨格を作ります。下記はその中核ロジックです。

```
import os
from slack_bolt import App
from anthropic import Anthropic

app = App(token=os.environ["SLACK_BOT_TOKEN"])
client = Anthropic()

@app.event("app_mention")
def handle_mention(event, say):
    text = event["text"].split(">", 1)[-1].strip()
    msg = client.messages.create(model="claude-sonnet-4-6", max_tokens=1024, messages=[{"role": "user", "content": text}])
    say(text=msg.content[0].text, thread_ts=event["ts"])
```

このコードだけで「メンション→スレッドに返信」が動きます。仮想社員らしくするには、ここに tool use（外部ツール呼び出し）や定期実行（OpenAIのScheduled Tasks相当）を足していきます。

## 実装上の注意点

権限は最小化し、トークンは必要なスコープだけに絞ること。送信・公開・削除などの不可逆操作は、AIが提案して人間が承認する設計にすること。そして、GPT-5.5が幻覚を52.5%削減したとはいえ、ツール実行前の引数検証（バリデーション）は必須です。

## まとめ

2026年6月のエージェント潮流（Claude Tag / Scheduled Tasks / Gemini Spark）は、いずれも「自律的にタスクを実行するAI」という同じ方向を向いています。その最小構成は「トリガー → LLM → tool use」というシンプルな三段構成です。各社のSaaSを待つだけでなく、仕組みを理解して自分で組める力が、これからのエンジニアの差別化ポイントになるでしょう。
