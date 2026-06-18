---
id: "2026-06-18-毎朝のニュースチェックをaiに丸投げしたら30分3分になったpythonclaude-api-01"
title: "毎朝のニュースチェックをAIに丸投げしたら、30分→3分になった【Python×Claude API】"
url: "https://note.com/key_pmoai/n/nb8597310decf"
source: "note"
category: "claude-code"
tags: ["API", "Python", "note"]
date_published: "2026-06-18"
date_collected: "2026-06-18"
summary_by: "auto-rss"
query: ""
---

![](https://assets.st-note.com/img/1781742931-3UjxIMyaT5CwSbpJ1XuLhVif.png?width=1200)

---

## はじめに

毎朝、ニュースサイトを5〜6個チェックしていました。

「今日の重要ニュースを把握しておかないと」という

焦りで、気づけば30分。  
でも正直、全部ちゃんと読めているわけじゃない。

そんなとき、ふと思いました。  
**「これ、AIに任せればよくないか？」**

試してみたら、あっさり解決しました。  
毎朝の情報収集が **30分 → 3分** になりました。

今回は、その仕組みをそのまま公開します。

---

## 作るもの

**「毎朝9時にAIがニュースを要約して、Slackに送ってくれる」仕組み**

```
NHKニュース（RSS）
    ↓
Python で取得
    ↓
Claude API で要約
    ↓
Slack に自動送信
```

---

## 必要なもの

**月のランニングコスト：約200〜500円**  
（Claude API の Haiku モデルを使うため格安）

---

## 手順

### Step 1｜ライブラリをインストール

ターミナルで以下を実行してください。

```
pip install anthropic feedparser requests
```

### Step 2｜Slack の Webhook URL を取得

1. Slack のワークスペースにログイン
2. [api.slack.com/apps](https://api.slack.com/apps) にアクセス
3. 「Create New App」→「From scratch」
4. 「Incoming Webhooks」を有効化
5. 「Add New Webhook to Workspace」でチャンネルを選択
6. 表示された Webhook URL をコピー

### Step 3｜Claude API キーを取得

1. [console.anthropic.com](https://console.anthropic.com/) にアクセス
2. アカウント作成（無料）
3. 「API Keys」→「Create Key」
4. 表示されたキーをコピー（一度しか表示されないので注意）

---

## コード

`news\_summary.py` というファイルを作って、以下をコピペしてください。

```
import feedparser
import anthropic
import requests
from datetime import datetime

# ここに自分のキーを入れてください
CLAUDE_API_KEY = "sk-ant-xxxxxxxx"
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/xxxxxxxx"

def fetch_news(num_articles=5):
    """NHKニュースのRSSから最新ニュースを取得"""
    rss_url = "https://www3.nhk.or.jp/rss/news/cat0.xml"
    feed = feedparser.parse(rss_url)

    articles = []
    for entry in feed.entries[:num_articles]:
        articles.append(f"・{entry.title}")

    return "\n".join(articles)

def summarize_with_claude(news_text):
    """Claude APIでニュースを3〜5行に要約"""
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": f"""以下のニュース見出しを、ビジネスパーソン向けに3〜5行で要約してください。
重要なポイントを簡潔にまとめてください。

{news_text}"""
        }]
    )
    return message.content[0].text

def send_to_slack(summary):
    """要約をSlackに送信"""
    today = datetime.now().strftime("%Y/%m/%d")
    payload = {
        "text": f"📰 *{today} のニュース要約*\n\n{summary}"
    }
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    return response.status_code == 200

if __name__ == "__main__":
    print("ニュースを取得中...")
    news = fetch_news()

    print("Claudeで要約中...")
    summary = summarize_with_claude(news)

    print("Slackに送信中...")
    success = send_to_slack(summary)

    if success:
        print("✅ 完了！Slackを確認してください")
    else:
        print("❌ Slack送信に失敗しました")
```

### Step 4｜実行してみる

```
python news_summary.py
```

Slack にこんなメッセージが届けば成功です。

```
📰 2026/06/15 のニュース要約

本日の主なニュースは以下の通りです。
・〇〇〇〇〇〇〇〇〇〇
・〇〇〇〇〇〇〇〇〇〇
・〇〇〇〇〇〇〇〇〇〇
```

---

## 毎朝自動で動かすには

**Windows の場合：タスクスケジューラ**

1. スタートメニューで「タスクスケジューラ」を検索
2. 「基本タスクの作成」
3. トリガー：毎日・午前9時
4. 操作：`python C:\path\to\news\_summary.py`

**Mac の場合：cron**

ターミナルで `crontab -e` を開いて以下を追加：

```
0 9 * * * /usr/bin/python3 /path/to/news_summary.py
```

これで毎朝9時に自動実行されます。

---

## コストの内訳

| 項目 | 金額 |  
|------|------|  
| Claude API（Haiku）| 約5〜10円/日 |  
| 月額合計 | **約150〜300円** |

Haiku モデルは Claude の中で最も安価なモデルです。  
要約程度のタスクなら Haiku で十分な品質が出ます。

---

## やってみた感想

正直、思っていたより簡単でした。

コードは全部で50行ちょっと。  
Python をちょっと触ったことがある人なら、1〜2時間で動くはずです。

毎朝の「なんとなくニュースを眺める時間」がなくなって、  
その分を他のことに使えるようになりました。

---

## まとめ

次回は「この仕組みをさらに拡張して、業界ニュースに絞り込む方法」を書く予定です。

役に立ったら「スキ」をもらえると励みになります🙏

---

現役ITエンジニアがAI×Pythonで副業月10万を目指す記録を発信しています。  
Xアカウント（@xxxxxx）でも毎日AIネタを投稿中。
