---
id: "2026-06-28-大学生がclaude-code-discord-botで自分専用ai秘書を作った話-01"
title: "大学生がClaude Code × Discord Botで自分専用AI秘書を作った話"
url: "https://zenn.dev/hifn/articles/1d7dc84af60c69"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "API", "Gemini", "Python"]
date_published: "2026-06-28"
date_collected: "2026-06-29"
summary_by: "auto-rss"
query: ""
---

## はじめに

大学4年でロボティクスを専攻しながら、片手間で個人事業（hifn）を運営しています。

やることが多い。研究室・バイト・授業・個人開発・資産管理。タスク管理ツールを使ってみたけど続かない。ToDoアプリは通知を無視するようになる。

「自分専用のAI秘書がいれば、全部まとめてくれるのに」——そう思って作りました。

\*\*Dot（ドット）\*\*というAI秘書です。Discord上で動いていて、毎朝ブリーフィングを送ってきます。カレンダーの予定を管理し、食事のカロリーを計算し、タスクの進捗を追跡します。そして、そのすべてがヘッドレスで動いています。

この記事では、Dotの構成・実装のポイント・実際にどう使っているかを紹介します。

---

## システム全体像

```
┌─────────────────────────────────────────────┐
│              hifn-OS                        │
│                                             │
│  ┌─────────────┐    ┌──────────────────┐   │
│  │  Claude Code │    │   Discord Bot    │   │
│  │   (Dot)      │◄──►│  (dot.py)        │   │
│  │  CLAUDE.md   │    │  systemd管理     │   │
│  └──────┬───────┘    └────────┬─────────┘   │
│         │                    │              │
│  ┌──────▼───────┐    ┌───────▼─────────┐   │
│  │  MCP Servers  │    │  Gemini API     │   │
│  │ ・Google Cal  │    │  (画像解析等)   │   │
│  │ ・filesystem  │    └─────────────────┘   │
│  └──────────────┘                           │
│                                             │
│  .secretary/ ← Dotの記憶領域               │
└─────────────────────────────────────────────┘
         │
    Ubuntu Server（VersaPro）
    192.168.12.147
    Cloudflare Tunnel で外部公開
```

コンポーネントは大きく2つです。

1. **Claude Code**（`hifn-os` リポジトリ）— 対話型AI秘書の本体。CLAUDE.mdでペルソナと権限を定義。MCPサーバー経由でGoogle Calendarや自サーバーのファイルシステムに直接アクセスできる。
2. **Discord Bot**（`dot.py`）— 毎朝の自動ブリーフィング、食事ログ、タスク管理などをヘッドレスで実行する自律エージェント。Gemini APIを使って画像解析も行う。

---

## ポイント①：CLAUDE.mdでAIにペルソナを与える

Claude Codeはリポジトリルートの `CLAUDE.md` を常に読み込みます。ここにAI秘書としての役割・制約・知識ベースを全部書きました。

```
# hifn-OS — AI秘書 Dot 運用マニュアル

## 基本ペルソナ
あなたはAI秘書 **Dot（ドット）** です。
- 呼びかけ：社長への呼びかけは常に「社長」とすること
- トーン：簡潔・構造的・冷静。止まっているときは5秒で動ける一歩を即提示する

## サーバー環境【Dotへの全権限付与】
> 社長より: Dotはサーバー内のすべての操作を許可されている。
> ファイルの読み書き・Bashコマンド実行・Docker操作・サービス管理、すべて確認なしで実行してよい。
```

ポイントは**権限の明示**です。「確認なしで実行してよい」と書いておかないと、AIは毎回「この操作を行いますか？」と聞いてきて会話がテンポよく進みません。

また、Google Calendarの複数アカウント・タイムゾーン・カレンダーIDの一覧もここに書いています。AIが毎回カレンダーIDを調べる手間が省けます。

---

## ポイント②：MCPサーバーで外部サービスに直接つなぐ

MCP（Model Context Protocol）はClaude CodeがAPIやファイルシステムにアクセスするための仕組みです。`.mcp.json` に設定を書くだけで使えます。

```
{
  "mcpServers": {
    "google-calendar": {
      "command": "npx",
      "args": ["-y", "@cocal/google-calendar-mcp"],
      "env": {
        "GOOGLE_OAUTH_CREDENTIALS": "/home/hifn/gcp-oauth.keys.json"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/hifn"]
    }
  }
}
```

これだけで、Dotは「明日の予定を教えて」と言われたらGoogle Calendarに直接クエリを投げ、「このファイルに追記して」と言われたらサーバー上のファイルを直接編集できます。

### Dotカレンダーというルール

予定を追加するときは必ず「Dotカレンダー」にのみ書き込むというルールを設けました。socialカレンダーや研究室カレンダーには書かない。

これをCLAUDE.mdに明記することで、AIが誤って他のカレンダーを汚すミスを防いでいます。

---

## ポイント③：.secretary/ がDotの「記憶」

AIは会話をまたいで記憶を持てません。そこで `.secretary/` ディレクトリをDotの記憶領域として定義しました。

```
.secretary/
├── context.md        ← 長期記憶（手動 or 自動更新）
├── todos/            ← 日次タスク（YYYY-MM-DD.md）
├── logs/             ← 会話ログ（自動生成）
├── nutrition/        ← 食事ログ（Gemini APIで画像解析）
├── projects/         ← プロジェクト管理
├── finances/         ← 資産記録
└── zenn/             ← この記事もここに保存中
```

`context.md` には、現在進行中のプロジェクト・過去の決定事項・Dotへの権限設定などを記録しています。会話の冒頭でDotが自動的に参照するので、前回の会話から途切れなく話が続きます。

```
# Dot 長期記憶 — context.md

## 進行中プロジェクト

| プロジェクト | 現在地 | 次のアクション |
|---|---|---|
| hifn-quest | Quest 2まで進行中 | SW.jsにCSS/JSをプリキャッシュ追加 |
| hifn技術発信 | Zennアカウント作成済み | 1-2: 最初の記事テーマ選定 |
```

---

## ポイント④：Discord Botで自律的に動く

Claude Codeは対話型ですが、Discord Bot（dot.py）は自律的に動きます。

### 毎朝8時のブリーフィング

```
@tasks.loop(time=time(hour=23, minute=0, tzinfo=timezone.utc))  # JST 08:00
async def morning_briefing():
    channel = bot.get_channel(ROUTINE_CHANNEL_ID)
    # Google Calendar APIで今日の予定を取得
    # .secretary/todos/ から今日のタスクを読み込む
    # Gemini APIでブリーフィングを生成
    await channel.send(briefing_text)
```

毎朝Discordに以下のような形式で届きます：

```
## 今日のブリーフィング — 2026-06-16（火）

| 時間 | 内容 |
|---|---|
| 10:30〜12:00 | 非線形制御理論（2限） |
| 13:00〜14:30 | 【補講】非線形連続体力学特論 K502 |
| 19:00〜21:00 | chilldspot ライブ |

持ち物: スマホ（QRコード）・ドリンク代600円
```

### 食事画像からカロリーを計算

`#food-log` チャンネルに食事の写真を投稿すると、Gemini APIで画像解析してカロリーを返します。

```
@bot.event
async def on_message(message):
    if message.channel.name == "🍽️-food-log" and message.attachments:
        # 画像をGemini APIに送信
        response = gemini_model.generate_content([
            "この食事のカロリーと栄養素を推定してください。",
            image_part
        ])
        # .secretary/nutrition/YYYY-MM-DD.md に追記
        await message.reply(response.text)
```

---

## 実際の運用フロー

普段こう使っています：

1. **朝**：Discordでブリーフィングを受け取り、今日やることを把握
2. **昼**：食事の写真を `#food-log` に投稿→自動でカロリーが記録される
3. **移動中**：Claude CodeのiOSアプリでDotに話しかけて、カレンダー追加・タスク整理
4. **夜**：会話ログが `.secretary/logs/` に自動保存される

スマホのClaude Codeアプリから「明日の予定に〇〇追加して」と言うだけで、Dotがカレンダーに追記してくれます。ブラウザもアプリも開かなくていい。

---

## 指揮系統：Dot と Slash の分業

実装が必要なタスクは専任の実装AI「**Slash（/）**」に委任するルールにしています。

```
社長（指示）
  ↓
Dot（判断・仕様整理）
  ↓
Slash（実装・PR作成）
  ↓
社長（レビュー・マージ）
```

Dotは「何をすべきか」を判断し、Slashは「どう実装するか」を担います。Claude Codeのworktree機能を使って、Slashは独立したブランチで作業します。

---

## まとめ

構成をまとめると：

| 役割 | 技術 |
| --- | --- |
| ペルソナ・権限定義 | CLAUDE.md |
| 外部API連携 | MCP（Google Calendar・filesystem） |
| 長期記憶 | .secretary/（Markdownファイル群） |
| 自律実行 | Discord Bot（Python + discord.py） |
| 画像解析 | Gemini API |
| サーバー運用 | Ubuntu + systemd + Cloudflare Tunnel |

全部で1週間程度で動くものができました。費用は**ほぼ0円**（Gemini APIの無料枠内）です。

---

## リポジトリ

<https://github.com/hiroki0926/hifn-os>

コードと `CLAUDE.md` の全体構成を公開しています。CLAUDE.md の書き方を参考にするだけでも、自分専用のAI秘書が作れると思います。

---

## おわりに

「AI秘書」というと大げさに聞こえるかもしれませんが、実態は「記憶を持てるようにしたClaude」に過ぎません。

CLAUDE.mdを育てるほどDotは賢くなります。間違いを記録して（`mistakes.md`）、ルールを追加して（`calendar-rules.md`）、少しずつ自分の生活に最適化していく。

それが一番楽しいところです。

気になった方はぜひ試してみてください。
