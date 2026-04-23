---
id: "2026-03-23-claude-agent-sdkでマルチエージェントtelegramグループチャットを作った-01"
title: "Claude Agent SDKでマルチエージェントTelegramグループチャットを作った"
url: "https://zenn.dev/acropapa330/articles/zenn_multi_agent_telegram"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "zenn"]
date_published: "2026-03-23"
date_collected: "2026-03-24"
summary_by: "auto-rss"
---

## はじめに

「Claude Code のエージェントに1つずつ Telegram Bot を割り当てて、グループチャットで議論させたら面白くない？」

そんなアイデアから作り始めたら、意外とハマりどころが多くて面白かったので記事にしました。

実際にこんな感じでエージェント同士が `@メンション` でバトンを渡し合いながら議論します：

![エージェント同士がメンションでバトンを渡し合う様子](https://static.zenn.studio/user-upload/deployed-images/094842eca0f52eefff1af4d4.png?sha=345947e4fc3ed56feca22be6849901c2619c9b5c)

テキストで表すとこんな流れです：

```
ユーザー: フィジカルAIは今後社会にどう実装されると思う？

🔍 Researcher: CES2026でも注目のフィジカルAI、製造・物流・医療・自動運転の
               4領域が先行しそうです。@Acropapa_engineer_bot 技術面はどう？

⚙️ Engineer: エッジAIとロボティクスの統合が鍵で、ROS2 + LLMの組み合わせが
             熱いですね。@Acropapa_critic_bot リスク面はどう見ますか？

🎯 Critic: 意思決定の説明責任が曖昧になるリスクがあります。
           規制整備が追いついていない点も懸念です。

🔍 Researcher: 【まとめ】
               ・先行領域: 製造・物流・医療・自動運転
               ・技術: ROS2 + LLMの統合が有望
               ・課題: 説明責任と規制整備が急務
```

## システム構成

```
multi_agent_chat/
├── agent_bot.py          # エージェントBot本体（全エージェント共通）
├── group_chat_manager.py # 全エージェントを一括起動・監視
├── agents/
│   ├── researcher.json   # 🔍 オーガナイザー兼リサーチャー
│   ├── engineer.json     # ⚙️ エンジニア
│   └── critic.json       # 🎯 クリティック
└── .env
```

各エージェントは `agent_bot.py` を `--config` で設定ファイルを切り替えながら**独立プロセス**として起動します。

## 設計のポイント

### Bot間通信はファイルキュー経由

最初に詰まったのがここです。**TelegramはBotからBotへのメッセージを受信できない**（無限ループ防止のための仕様）。

なので Bot 間通信は `queue_{agent_id}.json` というファイルキューで実現しました：

```
def push_to_queue(target_agent_id: str, payload: dict):
    queue_file = WORK_DIR / f"queue_{target_agent_id}.json"
    queue = []
    if queue_file.exists():
        with open(queue_file, encoding="utf-8") as f:
            queue = json.load(f)
    queue.append(payload)
    with open(queue_file, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)
```

各Botが3秒ごとにファイルをポーリングして自分宛のメッセージを処理します：

```
async def queue_watcher(bot):
    while True:
        await asyncio.sleep(3)
        messages = pop_from_queue()
        for payload in messages:
            # メッセージを処理して返答
            response = await generate_response_from_queue(payload)
            await post_response(bot, response, payload)
```

### 議論フロー制御

エージェント設定JSONに `next_agent` と `max_turns` を持たせることで、議論のリレーを制御します：

```
// researcher.json
{
  "id": "researcher",
  "next_agent": "engineer",
  "max_turns": 3
}

// engineer.json
{
  "id": "engineer",
  "next_agent": "critic"
}

// critic.json
{
  "id": "critic",
  "next_agent": "researcher"  // Researcherに戻してまとめさせる
}
```

キューに積む際に `turn` カウンターを持たせて、`turn >= max_turns` になったら Researcher がまとめを生成します：

```
if AGENT_ID == "researcher" and is_last_turn:
    flow_instruction = (
        "これは議論の最終ターンです。\n"
        "【まとめ】というプレフィックスをつけて結論を整理してください。"
    )
```

### 各エージェントの個人記憶

発言のたびにバックグラウンドで `memory_{agent_id}.json` を更新します。次回以降の会話でこの記憶をプロンプトに含めることで、「このユーザーはPythonが得意」「前回はAIトレンドを話した」といった情報を引き継げます：

```
async def update_agent_memory(latest_exchange: str):
    current_memory = load_agent_memory()
    async for message in query(
        prompt=f"現在の記憶: {current_memory}\n最新の会話: {latest_exchange}\n"
               "重要情報を200文字以内の箇条書きで更新してください。",
        options=ClaudeAgentOptions(allowed_tools=[]),
    ):
        if hasattr(message, "result") and message.result:
            save_agent_memory(message.result.strip())
```

### 共有履歴で文脈を同期

全Botが `shared_history.json` を読み書きすることで、各エージェントがグループ全体の会話の流れを把握できます。キューから返答を生成する直前に `reload_shared_history()` を呼んで最新状態を反映します。

## ハマりどころまとめ

### Telegramのgroup privacy mode

デフォルトではBotはグループの全メッセージを受信できません（コマンドのみ）。BotFatherで必ずオフにする必要があります：

```
/mybots → [Bot選択] → Bot Settings → Group Privacy → Turn off
```

### Windows cp932エンコードエラー

サブプロセス起動時に絵文字を `print()` するとクラッシュします。

```
# NG
print(f"✅ {AGENT_NAME} 起動完了")

# OK
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
print(f"[OK] {AGENT_NAME} 起動完了")
```

### サブプロセスのパイプバッファ詰まり

`group_chat_manager.py` でサブプロセスの stdout を `PIPE` で受け取って**読み出さないと**バッファが詰まってプロセスが死にます。ファイルに直接書き出すのが安全です：

```
log_file = open(log_dir / f"{agent_id}.log", "a", encoding="utf-8")
process = subprocess.Popen(cmd, stdout=log_file, stderr=log_file)
```

### Bot間の無限ループ

最初に作った版では、Researcherが発言 → Engineerが返答 → Criticが返答 → Researcherが返答... と永遠に止まりませんでした。

解決策はキューから来たメッセージへの返答では次のキューに積まないのではなく、**ターン数で制御する**こと。`turn >= max_turns` になったら Researcher がまとめを出して終了します。

## セットアップ方法

### 1. BotFatherでBotを3つ作る

```
/newbot
→ 名前・ユーザー名を設定
→ トークンをコピー
```

各BotのGroup Privacy ModeをOFFに：

```
/mybots → Bot Settings → Group Privacy → Turn off
```

### 2. グループIDを取得

Botのトークンを使ってAPIを叩くのが一番確実です：

```
https://api.telegram.org/bot{BOT_TOKEN}/getUpdates
```

グループにメッセージを送った後にアクセスすると `chat.id` が取れます。

### 3. .envを設定

```
MY_USER_ID=あなたのTelegramユーザーID
GROUP_CHAT_ID=-1001234567890
RESEARCHER_BOT_TOKEN=xxx
ENGINEER_BOT_TOKEN=xxx
CRITIC_BOT_TOKEN=xxx
```

### 4. 起動

```
python group_chat_manager.py
```

## エージェントのカスタマイズ

`agents/*.json` を編集するだけで個性を変えられます：

```
{
  "id": "researcher",
  "name": "Researcher",
  "bot_username": "your_researcher_bot",
  "role": "役割の詳細説明（ここが各エージェントの個性になる）",
  "speak_probability": 0.95,  // ユーザー発言への反応確率
  "max_silence_turns": 1,     // これ以上黙ったら強制発言
  "response_delay_sec": 1.0,  // 発言前の待機秒数
  "max_turns": 3,             // 議論の最大ターン数
  "next_agent": "engineer",   // バトンを渡す先
  "allowed_tools": ["WebSearch", "WebFetch"]
}
```

`next_agent` をチェーンすることで議論の順番を自由に変えられます。4人・5人構成にするのも簡単です。

## 応用アイデア

* **コードレビューチーム**: 実装Bot → テストBot → セキュリティBot
* **ニュース解説チーム**: 収集Bot → 要約Bot → 翻訳Bot
* **ディベート**: 賛成Bot vs 反対Bot で議論させて司会Botがまとめる
* **既存パイプラインの可視化**: バックグラウンドで動いていた処理をグループチャットで会話形式に

## おわりに

Telegramの仕様（BotはBotのメッセージを受信できない）という制約がありましたが、ファイルキューで回避できました。

Claude Agent SDKの `query()` をそのまま使えるので、WebSearchやBashなど既存のツールもそのままエージェントに持たせられるのが楽でした。

ソースコードは近日GitHubに公開予定です。

---

*この記事は実際にClaudeと一緒にライブコーディングしながら書きました。*
