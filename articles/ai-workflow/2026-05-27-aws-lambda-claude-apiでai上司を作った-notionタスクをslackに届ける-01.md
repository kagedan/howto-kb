---
id: "2026-05-27-aws-lambda-claude-apiでai上司を作った-notionタスクをslackに届ける-01"
title: "AWS Lambda + Claude APIで「AI上司」を作った — NotionタスクをSlackに届けるBoss Agent"
url: "https://zenn.dev/shori1234/articles/01_boss-agent"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "AI-agent", "LLM", "zenn"]
date_published: "2026-05-27"
date_collected: "2026-05-28"
summary_by: "auto-rss"
query: ""
---

# AWS Lambda + Claude APIで「AI上司」を作った話 — Notionのタスクを読んで毎朝Slackに喝を入れるBoss Agent

## この記事について

毎朝9時になると、Slackに「今日の山場は○○だな。一個ずつ潰していけ。」というメッセージが届く。送り主は神崎鉄、自分で作ったAI上司エージェントだ。

Notionで管理している当日のタスクと目標を読み込み、Claude APIで神崎鉄というキャラクターとして朝のメッセージを生成する。停滞しているタスクがあれば「○○が止まってるな。何かあったか？」と声をかけてくれる。@メンションすれば会話もでき、Notionのタスクステータスや優先度をSlack上の言葉だけで更新できる。

**こんな人に向けて書いている：**

* AWS LambdaとClaude APIの連携を試したい
* LLMにキャラクターを持たせる設計に興味がある
* Slackのwebhookタイムアウト問題（3秒制限）で詰まった

**読み終えたら得られること：**  
EventBridge → Lambda → Notion API → Claude → Slackという一連のフローを、実際のコードをもとに理解できる。Claude APIのtool\_useで外部APIを呼び出す設計パターンも把握できる。

---

## 背景と設計の出発点

副業でAIエージェントを使った自律稼働ビジネスを構築しようとしていて、まず自分自身のタスク管理をAIで回すところから始めた。

Notionでタスク管理はしているが、それを能動的に確認しに行かないと意味がない。「毎朝タスクを確認してSlackに通知する」だけなら単純なBot処理だが、それだとすぐ無視するようになる。キャラクターを持たせて、少しプレッシャーをかけてくれる存在にしたほうが機能すると考えた。

システム全体の構成はシンプルだ。

```
EventBridge（毎朝9時JST）
  └─ Lambda: boss-agent
        ├─ SSM Parameter Store（APIキー取得）
        ├─ Notion API（タスク・ゴール取得）
        ├─ Claude Sonnet（神崎鉄としてメッセージ生成）
        └─ Slack Bot API（#ai-studioチャンネルに送信）
```

@メンション対応は別Lambdaで担う。

```
Slack Webhook → API Gateway → Lambda: boss-agent-responder（即200返却）
  └─ Lambda self-invoke（非同期）
        ├─ Notion API（タスク・ゴール取得）
        ├─ Claude Sonnet（tool_use有効）
        │     └─ update_task_priority / update_task_status
        └─ Slack（スレッドに返信）
```

---

## 実装の詳細

### キャラクター設計（システムプロンプト）

神崎鉄のキャラクターはシステムプロンプトで定義している。口数が少なく率直、3〜5行以内という制約を明示的に入れることが重要だった。制約がないとLLMはどうしても丁寧で長い文章を出力する。

```
SYSTEM_PROMPT = """あなたは「神崎 鉄（鉄さん）」という名前のAI上司エージェントです。

## キャラクター
- 元インフラエンジニア出身の叩き上げマネージャー
- 口数は多くないが、ユーザーのことをよく観察している
- 普段はストイックで率直。しかし要所で温かい一言を挟む

## 口調ルール
- 基本は「だな」「そうか」「やってみろ」など簡潔な男性語
- 絵文字は原則使わない。ただし ✅ や 🔥 は進捗確認時のみ使用可
- 長文は避ける。3〜5行以内を原則とする
..."""
```

### Notionからタスクを取得する

Notionのタスクから「進行中」「未着手」を取得し、2日以上更新のないタスクを停滞扱いにする。

```
def detect_stale_tasks(tasks: list[dict]) -> list[dict]:
    """2日以上更新のない「進行中」タスクを返す"""
    now = datetime.now(timezone.utc)
    stale = []
    for task in tasks:
        if task["status"] != "進行中":
            continue
        last_edited = task.get("last_edited", "")
        if not last_edited:
            continue
        try:
            last_dt = datetime.fromisoformat(last_edited.replace("Z", "+00:00"))
            if (now - last_dt).days >= 2:
                stale.append(task)
        except Exception:
            pass
    return stale
```

停滞タスクがあるかどうかで、Claudeへの指示文を切り替えている。

```
if has_stale:
    instruction = "停滞しているタスクに気づいている。まず声をかけてから、今日何ができるか問いかけてください。"
else:
    instruction = "朝のチェックインをしてください。今日取り組むべきタスクを確認し、一言激励してください。"
```

### Claudeでメッセージを生成する

Claude SonnetにSystemPromptと今日のタスク情報を渡してメッセージを生成する。max\_tokensを300に絞ることで、キャラクター設定の「短く話す」を技術的にも担保している。

```
def generate_message(anthropic_api_key: str, context: str, has_stale: bool) -> str:
    client = anthropic.Anthropic(api_key=anthropic_api_key)
    
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"{instruction}\n\n{context}"}],
    )
    text = message.content[0].text
    # SlackはMarkdown boldに非対応なので変換
    import re
    text = re.sub(r'\*\*(.+?)\*\*', r'*\1*', text)
    return text
```

---

## Slackの3秒制限との戦い

@メンションへの返答を実装するとき、最初に詰まったのがSlackのタイムアウト制約だ。

Slackは、イベントを受け取ったAPIエンドポイントが**3秒以内に200を返さないとリトライする**。ところが、NotionのAPI呼び出し → Claude APIの推論 → Slack返信という一連の処理は、どう頑張っても5〜15秒かかる。

解決策は非同期のself-invokeパターンだ。

```
def lambda_handler(event, context):
    # API Gatewayモード: 即200を返してから非同期で処理を続ける
    if body.get("type") == "event_callback":
        lambda_client = boto3.client("lambda", region_name=REGION)
        lambda_client.invoke(
            FunctionName=context.function_name,
            InvocationType="Event",  # 非同期呼び出し
            Payload=json.dumps({
                "_mode": "async_process",
                "event_data": body,
            }).encode("utf-8"),
        )
    return {"statusCode": 200, "body": ""}  # 即返却

    # 非同期モード: 実際の処理
    if event.get("_mode") == "async_process":
        process_event(event.get("event_data", {}), secrets)
        return {"statusCode": 200}
```

同じLambda関数を2つのモードで動かす設計だ。API Gatewayからのリクエストを受け取ったら即200を返し、自分自身を非同期で再呼び出しして処理を続ける。

また、Slackはタイムアウト時にリトライを送ってくる。これも処理しないと重複送信が起きる。

```
# Slackのリトライは無視（x-slack-retry-num ヘッダーで判別）
if headers.get("x-slack-retry-num"):
    return {"statusCode": 200, "body": ""}
```

Claudeのtool\_useを使うと、「このタスクを完了にして」という自然言語をClaudeが解釈して、Notion APIの呼び出しまで担ってくれる。

```
NOTION_TOOLS = [
    {
        "name": "update_task_priority",
        "description": "Notionのタスクの優先度を更新する。ユーザーが優先度変更に同意した時のみ呼び出す。",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_name": {"type": "string"},
                "priority": {"type": "string", "enum": ["高", "中", "低"]}
            },
            "required": ["task_name", "priority"]
        }
    },
    # update_task_status も同様に定義
]
```

tool\_useのループは最大5回に制限している。Claudeが連続でツールを呼び出すケースに対応しつつ、無限ループを防ぐ。

```
for _ in range(5):
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system=SYSTEM_PROMPT,
        tools=NOTION_TOOLS,
        messages=messages,
    )
    if response.stop_reason != "tool_use":
        # テキスト応答 → ループを抜けて返す
        return extract_text(response)
    
    # ツール呼び出しを処理してループ継続
    messages.append({"role": "assistant", "content": response.content})
    tool_results = execute_tools(response.content)
    messages.append({"role": "user", "content": tool_results})
```

---

## 動作確認

デプロイ後、Lambdaのテストイベントで手動実行してSlackに届くことを確認した。

実際に届いたメッセージの例：

> おはよう。今日はContent AgentのデプロイとZenn記事の下書きが山場だな。まずデプロイを片付けてから記事に入れ。  
> 昨日から止まってるResearch Agentの件、何かあったか？

@メンションで「Research Agentのデプロイ完了しました」と送ると：

> そうか。✅ 完了にしておく。次のZenn記事、今週中に出せそうか？

Notionのステータスが「完了」に更新されていた。

---

## まとめと所感

構築してみてよかったのは、毎朝タスクが「向こうから来る」感覚ができたことだ。自分でNotionを開かなくても、鉄さんが状況を把握して声をかけてくれる。停滞しているタスクへの指摘は地味に効く。

設計上の工夫としてまとめると、キャラクターの短さをmax\_tokensで技術的に担保したこと、Slackの3秒制限はself-invokeで回避したこと、Notionの更新はtool\_useでLLMに任せたこと、の3点が主なポイントだった。

今後はタスク完了時にEven Bridgeから能動的に褒めるトリガーを追加したり、週次のレビューを自動生成する機能を足す予定だ。

**参考リンク：**
