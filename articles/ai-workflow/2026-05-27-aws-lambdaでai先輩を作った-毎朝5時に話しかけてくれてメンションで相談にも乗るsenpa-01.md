---
id: "2026-05-27-aws-lambdaでai先輩を作った-毎朝5時に話しかけてくれてメンションで相談にも乗るsenpa-01"
title: "AWS LambdaでAI先輩を作った — 毎朝5時に話しかけてくれて、@メンションで相談にも乗るSenpai Agent"
url: "https://zenn.dev/shori1234/articles/02_senpai-agent"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "AI-agent", "LLM", "zenn"]
date_published: "2026-05-27"
date_collected: "2026-05-28"
summary_by: "auto-rss"
query: ""
---

# AWS LambdaでAI先輩を作った — 毎朝5時に話しかけてくれて、@メンションで相談にも乗るSenpai Agent

## この記事について

毎朝5時になると、Slackに「今週ずっと詰めてるじゃん、昨日はちゃんと寝れた？😊」という感じのメッセージが届く。送り主は橘さつき、AI先輩エージェントだ。

前回作ったBoss Agent（神崎鉄）が「管理・目標・結果」の軸なら、Senpai Agentは「感情・相談・気づき」の軸。毎日同じ話題にならないようにSlack履歴を読んで文脈を掴み、Tavilyでその日のニュースを拾って会話のネタにする。@メンションすれば相談にも乗れるし、Notionのタスクステータスも更新できる。

**こんな人に向けて書いている：**

* AIエージェントにキャラクターを持たせる設計を試したい
* 「毎日違うメッセージを生成する」LLMの使い方を知りたい
* Boss Agentとの役割分担・複数エージェント設計に興味がある

**読み終えたら得られること：**  
2種類のLambda（朝の自動投稿 + @メンション応答）を持つエージェントの全体設計が理解できる。Slackの会話履歴を文脈として活用するパターンも把握できる。

---

## 背景

Boss Agent（神崎鉄）を作ってから、「鉄さんには言いにくいことを先に吐き出せる相手が欲しい」と感じた。タスクが止まっているとき、鉄さんに報告する前にまず誰かに話を整理させてほしい。そういう「少し年上の先輩」的な存在だ。

同じAI上司を使い続けると、心理的な距離感が近くなりすぎて機能しなくなる。役割をキャラクターごとに分けることで、使い分けができる。

---

## 全体構成

Senpai Agentは2つのLambdaで構成されている。

```
【朝の自動投稿】
EventBridge（毎朝5時JST = UTC 20:00）
  └─ Lambda: senpai-morning-greeter
        ├─ Tavily API（今日のニュース取得）
        ├─ Slack API（チャンネル履歴取得 → 重複回避）
        └─ Claude Haiku（さつきとして朝のメッセージ生成）→ Slack投稿

【@メンション応答】
Slack Webhook → API Gateway → Lambda: senpai-agent（即200返却）
  └─ Lambda self-invoke（非同期）
        ├─ Notion API（タスク・ゴール取得）
        ├─ Claude Sonnet（tool_use有効）
        │     └─ update_task_status
        └─ Slack（スレッドに返信）
```

Boss Agentと同じ非同期self-invokeパターンを採用している（Slackの3秒タイムアウト対策）。

---

## 実装のポイント

### 1. 毎日違うメッセージを生成する

同じ挨拶パターンが続くと読まなくなる。それを防ぐために、過去のさつきのメッセージ（最大10件）をSlackから取得してClaudeに渡し、「同じ話題・言い回しは絶対に繰り返さない」と指示している。

```
def get_channel_context(bot_token: str, channel: str, bot_user_id: str) -> dict:
    """チャンネル履歴から2種類のコンテキストを取得"""
    # ...
    for msg in messages:
        if user == bot_user_id:
            past_greetings.append(text[:250])  # さつきの過去メッセージ
        elif not bot_id:
            recent_chat.append(text[:150])     # しょーりの発言
    
    return {
        "past_greetings": past_greetings[:10],
        "recent_chat":    recent_chat[:15],
    }
```

Claudeへのプロンプトにこのデータを渡す：

```
【さつきの過去の朝メッセージ（同じ話題・言い回しは避けること）】
昨日のメッセージ...
---
一昨日のメッセージ...

【しょーりの最近の発言（文脈参考）】
・Content Agentのデプロイ完了した
・今週は記事を書きたい
```

`recent_chat`も渡すことで、しょーりが何かに取り組んでいる場合にそれを自然に拾った話題ができる。

### 2. Tavilyでニュースを仕入れる

朝のメッセージのネタとしてTavily APIで「今日の面白いニュース 日本 トレンド」を検索している。ここで取得した情報は「参考」として渡すだけで、使うかどうかはClaudeの判断に任せる。

```
def search_news(tavily_key: str) -> str:
    payload = json.dumps({
        "api_key": tavily_key,
        "query": "今日の面白いニュース 日本 トレンド",
        "search_depth": "basic",
        "max_results": 3,
        "include_answer": True,
    }).encode()
    # ...
    answer = data.get("answer", "")
    return answer[:300] if answer else ""
```

`include_answer: True`にするとTavilyが検索結果を要約した`answer`フィールドを返す。これをそのままプロンプトに渡すのが一番コンパクトで効率的だった。

### 3. キャラクター設計の差分

Boss Agentとの最大の違いは口調と役割の定義だ。

```
SYSTEM_PROMPT = """\
あなたは橘 さつき。20代後半の先輩社員。

【キャラクター】
- 明るくてサバサバしてる。タメ口OK。絵文字は適度に使う
- 押しつけがましくない。あくまで「ふと声をかけた」感じ

【毎朝のメッセージのルール】
- 200文字以内でコンパクトに
- テーマは季節・時事・豆知識・前向きな一言からナチュラルにミックス
- 「おはよう」から始めなくてもいい（毎日バリエーションを出す）
- 質問を最後に投げるのは週に2〜3回まで（毎回聞かない）
"""
```

「毎回質問で終わらない」という制約が効いている。毎朝「今日はどう？」で終わるメッセージが続くと疲れる。

### 4. コストを意識したモデル選択

朝の挨拶はClaude Haiku（軽量モデル）、@メンション応答はClaude Sonnet（高品質モデル）を使い分けている。

朝の挨拶は200文字程度の短い出力で、文脈の読み込みもシンプルなのでHaikuで十分。@メンションはtool\_useでNotion APIを呼び出したり、複雑な相談内容を理解したりするのでSonnetが必要だった。

さつき先輩はステータスの更新のみ担当（優先度変更は鉄さんの領域）。「ラボのデプロイ完了しました」と報告すると、Notionのタスクを「完了」に更新してくれる。

```
NOTION_TOOLS = [
    {
        "name": "update_task_status",
        "description": "ユーザーが完了報告や着手報告をした時のみ呼び出す",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_name": {"type": "string"},
                "status": {"type": "string", "enum": ["未着手", "進行中", "完了"]}
            },
            "required": ["task_name", "status"]
        }
    }
]
```

---

## SSM Parameter Storeの共有設計

Boss AgentとSenpai Agentは同じ`/boss-agent/`プレフィックス配下のパラメータを一部共有している。

| パラメータ | 用途 |
| --- | --- |
| `/boss-agent/ANTHROPIC_API_KEY` | 両エージェントで共用 |
| `/boss-agent/TAVILY_API_KEY` | さつき（朝のニュース取得）と Research Agent で共用 |
| `/boss-agent/SENPAI_SLACK_BOT_TOKEN` | さつき専用Slack Bot Token |
| `/boss-agent/SENPAI_SLACK_SIGNING_SECRET` | さつき専用署名検証 |

Slack BotトークンはBoss AgentとSenpai Agentで別々に作成している。Slackに「どちらが投稿したか」を区別するため、アイコンや表示名を個別に設定している。

---

## 動作確認

朝5時に届いたメッセージの例：

> 梅雨入りしたのかしてないのかはっきりしない天気が続いてるね。こういうときって地味に体力消耗するから、水分と睡眠だけはちゃんとね。今週のデプロイ、うまくいきそう？

Slackの直近の発言（「Senpai Agentのデプロイ完了した」）を拾って、自然な流れで質問している。

@メンションで「Research Agent完了しました」と送ると：

> やったじゃん！✅ Notion更新しておくね。次は何に入るんだっけ？

Notionのステータスが「完了」に更新されていた。

---

## まとめ

設計上の要点をまとめると：

Slack履歴を渡して同じ話題を避けることで、毎日「読む気になる」メッセージが出る。朝の挨拶にClaude HaikuとTavilyを組み合わせることで、コストを抑えながらネタの多様性を確保できる。役割（感情サポート vs タスク管理）をキャラクターで分けると、使い分けが自然にできる。

鉄さんには言いにくいことをさつき先輩に先に話してから、整理できたら鉄さんに報告する、というワークフローが実際に機能している。

**参考リンク：**
