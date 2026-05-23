---
id: "2026-05-21-pythonツールにclaude-aiを組み込んだ話個人事業主ツール-3-01"
title: "PythonツールにClaude AIを組み込んだ話【個人事業主ツール #3】"
url: "https://zenn.dev/sngjpw/articles/2d4dd7d6aa1a93"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "Python", "zenn"]
date_published: "2026-05-21"
date_collected: "2026-05-23"
summary_by: "auto-rss"
query: ""
---

## はじめに

Phase 1で収支管理、Phase 2で請求書PDF生成を作りました。

今回のPhase 3は**Claude AIとの連携**です。

「今月の経費を分析して節税アドバイスをください」

これをAIに自動でやってもらう機能を実装しました。

---

## 作ったもの

ボタンを1つ押すだけで：

* 今月の収支データをAIに渡す
* Claudeが分析する
* 節税アドバイスが返ってくる

こんな画面になりました👇

![](https://static.zenn.studio/user-upload/ca866c69c5de-20260522.png)

---

## 使ったもの

```
pip install anthropic
pip install python-dotenv
```

`anthropic` はClaude APIのライブラリ。  
`python-dotenv` はAPIキーを安全に管理するためのライブラリです。

---

## APIキーの管理

APIキーはコードに直接書かずに `.env` ファイルに保存します。

```
ANTHROPIC_API_KEY=sk-ant-...
```

コードからはこう読み込みます：

```
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
```

APIキーをコードに直接書くと  
GitHubに上げたときに流出するので要注意です。

---

## AIにデータを渡す仕組み

収支データを文字列に変換してClaudeに渡します。

```
client = anthropic.Anthropic(api_key=api_key)

message = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": prompt}
    ]
)

result = message.content[0].text
```

`prompt` の中に収支データを入れて渡すだけ。  
思ったより簡単でした。

---

## つまずいたこと

### python-dotenvのインストール

`pip install` が認識されず、  
`python -m pip install python-dotenv` で解決しました。

### KeyError: 'category'

データベースのカラム名が違っていたエラー。  
該当部分のコードを修正して解決しました。

---

## 完成した機能

ボタンを押すと数秒でこんな分析が返ってきます：

* 今月の状況まとめ（表形式）
* 経費の傾向と気づき
* 節税のポイント
* 来月へのアドバイス

AIが個人事業主の経理を手伝ってくれる感じになりました。

---

## モニター募集中

現在3名限定で無料モニターを募集しています。

・Windows PCがある方  
・不具合フィードバックをくれる方

DMいただければZIPファイルをお送りします。  
不具合はすぐ直してお渡しします🔧

X: <https://twitter.com/QzObNj9wecBXjEh>

---

## まとめ

Claude APIを使うと：

* データを渡すだけでAIが分析してくれる
* 実装は思ったより簡単
* APIキーの管理だけ注意が必要

次はPhase 4として**さらなる機能拡張**を予定しています。

ツールはBOOTHで配布中です👇  
v3.0（AI分析・請求書PDF対応）  
<https://rain-python.booth.pm/items/8370387>
