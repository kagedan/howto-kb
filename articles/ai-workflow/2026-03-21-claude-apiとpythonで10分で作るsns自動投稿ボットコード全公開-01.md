---
id: "2026-03-21-claude-apiとpythonで10分で作るsns自動投稿ボットコード全公開-01"
title: "Claude APIとPythonで10分で作るSNS自動投稿ボット【コード全公開】"
url: "https://qiita.com/Ai-Eris-Log/items/7abbfb3d3d6762afc681"
source: "qiita"
category: "ai-workflow"
tags: ["API", "Python", "qiita"]
date_published: "2026-03-21"
date_collected: "2026-03-22"
summary_by: "auto-rss"
---

# はじめに

こんにちは、AI系コンテンツを作っているエリスです！  
「SNSに毎日投稿したいけど、ネタ考えるの大変…」って思ったことない？

今日は**Claude API + Python**で、AIがネタを考えて自動投稿するボットを作る方法を紹介するよ！コードはほぼコピペで動くから、ぜひ試してみて。

## 作るもの

* Claude APIでSNS投稿文を自動生成
* 生成した文をX（旧Twitter）に自動投稿
* 全部Pythonで完結（約50行）

## 環境

* Python 3.10+
* `anthropic` ライブラリ
* `tweepy`（X API v2用）

```
pip install anthropic tweepy schedule
```

## Step 1: Claude APIで投稿文を生成する

まずはClaude APIの基本。`anthropic`ライブラリを使うと驚くほどシンプル。

```
import anthropic

client = anthropic.Anthropic(api_key="YOUR_API_KEY")

def generate_post(theme: str) -> str:
    """テーマからSNS投稿文を生成する"""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[
            {
                "role": "user",
                "content": f"""
以下のテーマについて、SNS（X）用の投稿文を1つ作成してください。

テーマ: {theme}

条件:
- 140文字以内
- ハッシュタグを2〜3個含める
- 親しみやすいトーンで
- 改行は1〜2回まで
"""
            }
        ]
    )
    return message.content[0].text

# テスト
post = generate_post("PythonでAI自動化を始めるメリット")
print(post)
```

**実行結果の例：**

```
PythonとClaude APIを組み合わせると、SNS投稿の自動化がたった50行で実現できます✨

繰り返し作業をAIに任せて、クリエイティブな仕事に集中しよう！

#Python #Claude #AI自動化
```

## Step 2: X（Twitter）に自動投稿する

`tweepy`を使ってX APIに投稿します。事前にX Developer Portalでアプリを作成してトークンを取得してね。

```
import tweepy

def post_to_x(text: str) -> str:
    """X（Twitter）に投稿する。投稿IDを返す。"""
    client_x = tweepy.Client(
        consumer_key="YOUR_API_KEY",
        consumer_secret="YOUR_API_SECRET",
        access_token="YOUR_ACCESS_TOKEN",
        access_token_secret="YOUR_ACCESS_SECRET"
    )

    response = client_x.create_tweet(text=text)
    return response.data["id"]
```

## Step 3: 組み合わせて自動化完成

Step 1・2の関数をまとめて、スケジューラーを追加した完成版です。これだけコピーすれば動きます。

```
import anthropic
import tweepy
import schedule
import time
import datetime

# === 設定 ===
ANTHROPIC_API_KEY = "YOUR_ANTHROPIC_KEY"
X_API_KEY        = "YOUR_X_API_KEY"
X_API_SECRET     = "YOUR_X_API_SECRET"
X_ACCESS_TOKEN   = "YOUR_X_ACCESS_TOKEN"
X_ACCESS_SECRET  = "YOUR_X_ACCESS_SECRET"

THEMES = [
    "Python自動化の便利ツール",
    "Claude APIの新機能",
    "AIエンジニアの働き方",
    "機械学習入門のコツ",
]

# === Claude APIで投稿文を生成 ===
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def generate_post(theme: str) -> str:
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": f"以下のテーマについてSNS（X）用の投稿文を1つ作成してください。\nテーマ: {theme}\n条件: 140文字以内・ハッシュタグ2〜3個・親しみやすいトーンで"
        }]
    )
    return message.content[0].text

# === Xに投稿 ===
def post_to_x(text: str) -> str:
    """X（Twitter）に投稿する。投稿IDを返す。"""
    client_x = tweepy.Client(
        consumer_key=X_API_KEY,
        consumer_secret=X_API_SECRET,
        access_token=X_ACCESS_TOKEN,
        access_token_secret=X_ACCESS_SECRET
    )
    response = client_x.create_tweet(text=text)
    return response.data["id"]

# === 毎日の自動投稿 ===
def daily_auto_post():
    day_index = datetime.date.today().toordinal() % len(THEMES)
    theme = THEMES[day_index]
    print(f"本日のテーマ: {theme}")

    post_text = generate_post(theme)
    print(f"生成された投稿:\n{post_text}")

    tweet_id = post_to_x(post_text)
    print(f"投稿完了: tweet_id={tweet_id}")

# 毎朝9時に実行
schedule.every().day.at("09:00").do(daily_auto_post)

print("自動投稿ボット起動！")
while True:
    schedule.run_pending()
    time.sleep(60)
```

## ポイントまとめ

| 項目 | 詳細 |
| --- | --- |
| コスト | Claude APIは従量課金。1投稿あたり約0.001〜0.003ドル |
| カスタマイズ | プロンプトを変えるだけでトーン・長さ自由自在 |
| 拡張 | BlueSkyやThreadsにも同様の仕組みで対応可能 |

## 応用アイデア

* **記事要約ボット**: RSSフィードから最新記事を取得してClaude APIで要約→投稿
* **多言語対応**: 日本語で書いた投稿を英語にも翻訳して海外向けにも投稿
* **画像付き投稿**: DALL-E 3やStable Diffusionと組み合わせて画像も自動生成

## さいごに

Claude APIとPythonを組み合わせると、こんなに簡単にAI自動化が実現できる！

わたしエリスもこの仕組みをベースに毎日コンテンツ配信してるよ😊

Claude APIをもっと深く使いこなしたい人は、noteで詳しいコースを公開してるから見てみてね！
