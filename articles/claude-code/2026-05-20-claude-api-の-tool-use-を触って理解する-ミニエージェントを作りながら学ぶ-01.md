---
id: "2026-05-20-claude-api-の-tool-use-を触って理解する-ミニエージェントを作りながら学ぶ-01"
title: "Claude API の Tool Use を触って理解する — ミニエージェントを作りながら学ぶ"
url: "https://zenn.dev/shino_i/articles/38a3c0c8a87525"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "Python", "zenn"]
date_published: "2026-05-20"
date_collected: "2026-05-21"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude API には **Tool Use** という、Claude が自律的に外部の関数（ツール）を呼び出せる機能があります。Claude Code をはじめとする最近のエージェント型 AI アプリケーションの心臓部となっている仕組みです。

この記事では、Tool Use を理解するためにミニエージェントを Python で作って実際に動かして体験してみました。

* ツール定義の書き方
* エージェントループの仕組み
* Claude と実装の責任分界

完成すると、次のようなターミナルアプリで Claude と対話できます。

```
👤 User: 東京の現在の気温を華氏に変換して

🤖 Claude: 東京の現在の天気情報を取得します！

🔧 Tool Call: get_weather({"city": "Tokyo"})
✅ Result:
{
  "city": "Tokyo",
  "temp_c": 22,
  "condition": "晴れ時々曇り",
  "humidity": 55
}

🤖 Claude: 東京の気温は **22°C** ですね。これを華氏に変換します！（公式: °F = °C × 9/5 + 32）

🔧 Tool Call: calculate({"expression": "22 * 9/5 + 32"})
✅ Result:
{
  "expression": "22 * 9/5 + 32",
  "result": "71.6"
}

🤖 Claude: 結果をまとめると：

| 項目 | 値 |
|------|-----|
| 🌡️ 摂氏 | 22°C |
| 🌡️ 華氏 | **71.6°F** |
| 天気 | 晴れ時々曇り ☀️🌤️ |
| 湿度 | 55% |

東京の現在の気温は **22°C（71.6°F）** です！過ごしやすい気温ですね😊
```

質問1つから Claude が「東京の気温を取得 → 単位変換」を自分で組み立てて実行している様子が見て取れます。※デモ環境であるため、東京の天気情報と気温は用意していたデータを利用しています。

---

ざっくり言うと、Claude API に **「使えるツールの一覧」** をスキーマで渡しておくと、Claude が必要に応じて

> 「`get_weather` を `{"city": "Tokyo"}` で呼んでください」

と返してくる、という機能です。実際にツールを実行するのは **こちら側（ローカル）の責任** で、その結果を会話履歴に追加して再度 Claude に渡すと、Claude が結果を踏まえて続きを考えてくれます。

つまり Claude 自身は外部システムに直接アクセスする力を持たず、**「判断は Claude、実行はローカル」** の分業構造で外部世界と接続するわけです。

---

## プロジェクト構成

最終的に以下のような構成になりました。

```
project/
├── main.py                     # エントリーポイント (REPL)
├── agent.py                    # エージェントループ
├── tools/
│   ├── __init__.py             # ツールレジストリ
│   ├── weather.py              # get_weather
│   ├── calculator.py           # calculate
│   ├── time_service.py         # get_current_time
│   └── knowledge_base.py       # search_knowledge_base
└── utils/
    ├── __init__.py
    └── console.py              # ANSI カラーコード
```

各ツールは「定義 (`DEFINITION`)」と「実装 (`execute`)」の2つを持つモジュールとして独立させ、`tools/__init__.py` で集約します。新しいツールを追加したくなったら、`tools/` にファイルを1つ追加するだけで済む構造です。

---

## セットアップ

### 1. パッケージインストール

```
pip install anthropic tzdata
```

Windows で `zoneinfo` を使う場合に `tzdata` を入れないと `Asia/Tokyo` などのタイムゾーンを解決できず、後述の `get_current_time` ツールが失敗したため、パッケージをインストールしました。

### 2. API キーを環境変数に設定

PowerShell の場合、永続化するには以下を実行します。

```
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "sk-ant-...", "User")
```

ターミナルを再起動すると有効になります。今回は個人での開発且つデモ環境ということもあり、コード管理に紛れ込ませてしまう事故の恐れがある`.env` ファイルの利用ではなく、上記の方法を採用しました。

---

## ① ツール定義 — Claude に「能力」を教える

Claude に渡すツール定義は、シンプルな JSON スキーマです。例として `get_weather` の定義を見てみます。

```
# tools/weather.py
DEFINITION = {
    "name": "get_weather",
    "description": "指定された都市の現在の天気情報を取得します。",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "都市名(例: Tokyo, New York, London)",
            }
        },
        "required": ["city"],
    },
}
```

Claude はこの「description」を読んで「ユーザーの質問にこのツールが使えるか？」を判断することから **`description` の質** が重要になります。説明が曖昧だと使ってもらえなかったり、誤った場面で呼ばれたりするので、人間に説明するつもりで書きます。

---

## ② ツール実装 — ローカル関数

`get_weather` の実装側は、単純な辞書ルックアップです（実際の天気情報を取得する API を叩いても OKですが、今回はTool Useを触って理解することが目的であるため、あらかじめ決まった値を呼び出すようにしています）。

```
# tools/weather.py
_WEATHER_DB = {
    "tokyo": {"temp_c": 22, "condition": "晴れ時々曇り", "humidity": 55},
    "new york": {"temp_c": 18, "condition": "曇り", "humidity": 60},
    # ...
}

def execute(city: str) -> dict:
    data = _WEATHER_DB.get(city.lower(), {"temp_c": 20, "condition": "晴れ", "humidity": 50})
    return {"city": city, **data}
```

Claude はこの中身を**一切知りません**。固定辞書だろうが本物の API だろうが、返ってくる JSON の形さえ守れば差し替えても動きます。これが Tool Use の柔軟性の源です。

---

## ③ ツールレジストリ — 一元管理

ツールが増えても呼び出し側がぐちゃつかないように、`tools/__init__.py` でまとめます。

```
# tools/__init__.py
from . import calculator, knowledge_base, time_service, weather

DEFINITIONS = [
    weather.DEFINITION,
    calculator.DEFINITION,
    time_service.DEFINITION,
    knowledge_base.DEFINITION,
]

_HANDLERS = {
    "get_weather": lambda inp: weather.execute(inp["city"]),
    "calculate": lambda inp: calculator.execute(inp["expression"]),
    "get_current_time": lambda inp: time_service.execute(inp["timezone"]),
    "search_knowledge_base": lambda inp: knowledge_base.execute(inp["query"]),
}

def execute(name: str, tool_input: dict) -> dict:
    handler = _HANDLERS.get(name)
    if handler is None:
        return {"error": f"未知のツール: {name}"}
    return handler(tool_input)
```

`DEFINITIONS` は Claude に渡すスキーマ一覧、`execute()` は Claude から要求された名前でディスパッチする実行関数です。

---

最重要パートです。`agent.py` で Claude API と対話します。

```
# agent.py
import json
from anthropic import Anthropic
from tools import DEFINITIONS, execute as execute_tool

_client = Anthropic()
MODEL = "claude-sonnet-4-6"

def run(user_message: str, max_iterations: int = 10) -> None:
    messages = [{"role": "user", "content": user_message}]

    for _ in range(max_iterations):
        # ① Claude にリクエスト
        response = _client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system="あなたは Tool Use のデモ用エージェントです。...",
            tools=DEFINITIONS,
            messages=messages,
        )

        # 応答を会話履歴に追加
        messages.append({"role": "assistant", "content": response.content})

        # ② tool_use ブロックを抽出
        tool_use_blocks = [b for b in response.content if b.type == "tool_use"]

        # ③ 終了判定
        if response.stop_reason != "tool_use":
            break

        # ④ ローカルでツール実行
        tool_results = []
        for tu in tool_use_blocks:
            result = execute_tool(tu.name, tu.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tu.id,
                "content": json.dumps(result, ensure_ascii=False),
            })

        # ⑤ 結果を会話履歴に追加して次のループへ
        messages.append({"role": "user", "content": tool_results})
```

### ループ構造のポイント

| 番号 | 役割 |
| --- | --- |
| ① | `tools=DEFINITIONS` を渡すことで Claude にツール一覧を知らせる |
| ② | レスポンスから `tool_use` 型のブロックを取り出す |
| ③ | **`stop_reason != "tool_use"` ならループ終了**（Claude が「もう十分」と判断） |
| ④ | ローカルでツールを実行 |
| ⑤ | 結果を `user` ロールの `tool_result` として送り返す |

ここでよく勘違いするのが⑤の **ロール** です。ツール結果は `tool` ではなく **`user`** ロールで送るのが Claude API の決まりです。

---

## ⑤ アーキテクチャ全体像

```
┌───────────────────────────────────────────────────────────────┐
│                    ローカル環境 (Your PC)                      │
│                                                               │
│   👤 ユーザー ──▶ main.py ──▶ agent.py ◀──▶ tools/             │
│                              │                                │
└──────────────────────────────┼────────────────────────────────┘
                               │ HTTPS (anthropic SDK)
                               ▼
┌───────────────────────────────────────────────────────────────┐
│              ☁️ Anthropic Cloud (Claude API)                  │
│              🤖 claude-sonnet-4-6                             │
│              「どのツールを使うか」を判断する役                   │
└───────────────────────────────────────────────────────────────┘
```

* **main.py** は REPL の入出力だけ担当
* **agent.py** が Claude API との対話とループを制御
* **tools/** は純粋な関数群（Claude を一切意識しない）

---

## 複数ツールの組み合わせになる質問をしてみる

```
cd C:\work\claude\tool_use\project
python main.py
```

質問と結果:

```
👤 User: Pyrhon と Rustの特徴を教えて、ついでにLondonの天気も

🤖 Claude: 3つの情報を同時に取得しますね！

🔧 Tool Call: search_knowledge_base({"query": "Python プログラミング言語の特徴"})
🔧 Tool Call: search_knowledge_base({"query": "Rust プログラミング言語の特徴"})
🔧 Tool Call: get_weather({"city": "London"})
✅ Result:
{
  "query": "Python プログラミング言語の特徴",
  "hits": [
    {
      "title": "Python",
      "body": "Python は読みやすさを重視した汎用プログラミング言語。データサイエンス、機械学習、Web 開発、自動化スクリプトなど幅広く使われる。"
    }
  ]
}

✅ Result:
{
  "query": "Rust プログラミング言語の特徴",
  "hits": [
    {
      "title": "Rust",
      "body": "Rust は安全性とパフォーマンスを両立するシステムプログラミング言語。所有権システムによりメモリ安全性を保証する。"
    }
  ]
}

✅ Result:
{
  "city": "London",
  "temp_c": 12,
  "condition": "小雨",
  "humidity": 78
}

🤖 Claude: まとめてお伝えします！

---

## 🐍 Python の特徴
- **読みやすさ重視**のシンプルな文法で初心者にも人気
- **幅広い用途**に対応：データサイエンス・機械学習・Web開発・自動化スクリプトなど
- 豊富なライブラリエコシステムが強み

---

## 🦀 Rust の特徴
- **安全性とパフォーマンスを両立**するシステムプログラミング言語
- 独自の**所有権システム**によってメモリ安全性をコンパイル時に保証
- C/C++ の代替として注目されており、低レイヤー開発に最適

---

## 🌦️ ロンドンの現在の天気
| 項目 | 情報 |
|------|------|
| 🌡️ 気温 | 12°C |
| 🌧️ 天気 | 小雨 |
| 💧 湿度 | 78% |

ロンドンらしいお天気ですね！☔

---

ご不明な点や詳しく知りたいことがあれば、お気軽にどうぞ！
```

Claude は **`search_knowledge_base` を2回 + `get_weather` を1回** 呼んで、結果をまとめて回答してくれます。複数ツールの組み合わせを Claude 自身が組み立てているのが面白いポイントです。

---

## 今回開発してみてのつまずきポイント

### Windows で `zoneinfo` がタイムゾーンを認識しない

```
{"error": "無効なタイムゾーン: 'No time zone found with key Asia/Tokyo'"}
```

これは Windows に IANA タイムゾーンデータベースが入っていないために起こっているようです。

で解決しました。

### `ModuleNotFoundError: No module named 'anthropic'`

を忘れずに。

---

ここまで作って気づくのは、Claude API の Tool Use が提供しているのは以下 **3つだけ** だということです。

1. ツールのスキーマ（名前・説明・引数）を Claude に渡せる
2. Claude が「このツールを、この引数で呼びたい」と返してくる
3. 開発者が実行結果を会話に戻すと、続きを考えてくれる

**`get_weather` も `calculate` も Claude の機能ではなく、こちらが定義したただのローカル関数です**。Claude が知っているのは名前と説明文だけ。

この境界線さえ理解すれば、

* 社内 DB の検索ツール
* メール送信ツール
* ファイル操作ツール
* 外部 API ラッパー

など、どんな業務ツールでも Claude に「使い分けて」もらえます。Claude Code 自身も、ファイル読み書き・コマンド実行・Web 検索といった「ツール」を組み合わせて動いている、同じ仕組みのアプリケーションです。

---

## まとめ

* Tool Use は **「Claude が判断 / ローカルが実行」** の分業構造
* ツール定義は JSON スキーマ、実装は普通の関数
* `stop_reason == "tool_use"` の間ループを回すだけのシンプルな構造
* ツール結果は **`user` ロール** で送り返すのを忘れずに

Tool Use を理解すると、Claude を単なるチャットボットではなく **「自律的に動くエージェントの頭脳」** として組み込めるようになります。Claude API開発の第一歩として、ぜひ手元で動かしてみてください。

---

## 参考
