---
id: "2026-06-09-lineがai秘書になった話claude-notion-googleを繋いで毎朝8時に予定を送ってく-01"
title: "LINEがAI秘書になった話。Claude × Notion × Googleを繋いで、毎朝8時に予定を送ってくれる仕組みを作った"
url: "https://zenn.dev/dmiiiiii1116/articles/1e00592cec212f"
source: "zenn"
category: "ai-workflow"
tags: ["API", "Python", "zenn"]
date_published: "2026-06-09"
date_collected: "2026-06-10"
summary_by: "auto-rss"
query: ""
---

## 作ったきっかけ

「今日の予定なんだっけ」と思うたびにカレンダーアプリを開く。メールも確認する。Notionのタスクも見る。

これが毎朝地味にめんどくさかった。

どうせLINEは毎日開くんだから、LINEの中で全部終わればいいじゃないか。そう思って作り始めたのが、このAI秘書です。

---

## 今こういう使い方をしている

朝起きたらLINEに通知が来ている。「今日の予定」「未完タスク」「重要メール」のサマリーが届いている。

外出先で「〇〇さんへの返信下書き作って」とLINEに送ると、Gmailの下書きが完成している。

「来週月曜15時にMTG入れて」と送ると、Google Calendarに予定が追加されている。

全部LINEの中で完結する。カレンダーアプリもGmailも開かない。

これが思ったより快適だった。

---

## 構成

```
LINEアプリ
  ↓
LINE Messaging API
  ↓
https://secretary.your-domain.com/line/webhook
  ↓
ConoHa VPS / Ubuntu / Nginx / HTTPS
  ↓
FastAPI + Uvicorn + systemd
  ↓
Claude API
  ├─ Google Calendar API
  ├─ Gmail API
  └─ Notion API
```

ローカルPCではなく、ConoHa VPSで24時間動かしています。PCを閉じても、サーバーは動き続けます。

---

## 技術的に面白かったところ

### Claudeがルーターになってる

このシステムの中心はClaude APIです。

「今日の予定は？」と送るとCalendarを叩く。「メール来てる？」と送るとGmailを叩く。「タスク追加して」と送るとNotionを叩く。

どのAPIを呼ぶかの判断をClaudeがやっています。自分でルーティングロジックを書かなくていいので、コードがシンプルになりました。

```
# secretary.py（抜粋・イメージ）
tools = [calendar_tool, gmail_tool, notion_tool]
response = claude.messages.create(
    model="claude-sonnet-4-6",
    tools=tools,
    messages=conversation_history
)
```

### Googleトークンの自己修復

最初に詰まったのがGoogle OAuth周りです。

アクセストークンには期限があります。期限が切れるとGmailもCalendarも動かなくなる。でも再認証はブラウザ操作が必要なので完全自動化できない。

対策として、トークン失効を検知したらLINEに通知して復旧手順を案内する仕組みを入れました。

```
def handle_google_error(e):
    if "Token has been expired" in str(e):
        # .reauth_requiredファイルを作成
        open("google_token.json.reauth_required", "w").close()
        # LINEに案内を送る
        send_line_message("Googleの再認証が必要です。手順を送ります...")
```

完全自動とはいかないけど、「突然動かなくなって気づかない」状態は回避できました。

### systemdで常時稼働

ConoHaに移してから、systemdサービスとして登録しています。

```
[Service]
Type=simple
ExecStart=/opt/line-ai-secretary/.venv/bin/uvicorn assistant_bot.app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5
```

`Restart=always` にしておくと、エラーで落ちても自動で再起動します。

---

## 詰まったポイント

* **ngrokからVPS移行のタイミング**: ローカルで動いてからVPSに移すのが一番スムーズだった。順番が大事。
* **Google OAuthのスコープ設定**: CalendarとGmailで必要なスコープが違う。両方まとめて最初に設定しておくべきだった。
* **LINE\_USER\_IDの取得**: Push通知（朝晩レポート）を送るためにはユーザーIDが必要。最初に確認しておかないと後で詰まる。

---

## 実際に使ってみた感想

毎朝8時にLINEが届く生活になって2週間くらいです。

思ったより「ちゃんと使ってる」感があります。朝のサマリーを見てから一日が始まる感じ。カレンダーアプリを別で開くことがほぼなくなりました。

「自分が欲しいから作った」ものが実際に使えてるのは、単純に気持ちいいです。

---

*Python 3.10+ / FastAPI / Claude API / LINE Messaging API / Google OAuth 2.0 / Notion API / ConoHa VPS*
