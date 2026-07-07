---
id: "2026-07-07-claude-api-で毎回きちんと-json-を返させる-tool-use-による構造化出力とたま-01"
title: "Claude API で毎回きちんと JSON を返させる — Tool Use による構造化出力と『たまに壊れる JSON』を根絶する実装手順【2026】"
url: "https://qiita.com/yureki_lab/items/efa3caa0d009a8f6c35f"
source: "qiita"
category: "ai-workflow"
tags: ["API", "Python", "qiita"]
date_published: "2026-07-07"
date_collected: "2026-07-08"
summary_by: "auto-rss"
query: ""
---

Claude に「JSON で返して」とプロンプトで頼むと、9割はうまくいくのに、たまに前置きの文章が混ざったり末尾が切れたりして `json.loads` が落ちる。本番のバッチでこれをやられると地味に痛い。この記事は、その「たまに壊れる」を **Tool Use（関数呼び出し）** で構造的に潰す手順をまとめたもの。

## 対象と前提

- 想定読者: Claude API で分類・抽出・要約などの結果を **プログラムから使う** 人
- 前提環境: Python 3.13 / `anthropic`（公式 Python SDK、本記事は 2026年7月時点の最新）/ モデルは `claude-sonnet-4-6`
- `ANTHROPIC_API_KEY` は環境変数に設定済みとする
- プロンプトで「JSON だけ返して」と指示する方式を一度は試して、たまに壊れて困っている人向け

## TL;DR

- `messages.create` に **tools** を渡し、欲しい構造を「ツールの入力スキーマ」として定義する
- `tool_choice` で **そのツールを必ず呼ばせる**。これで前置きテキストの混入が消える
- 返ってくる `tool_use` ブロックの `.input` は **すでに dict**。`json.loads` すら要らない
- 壊れる最後の原因 `max_tokens` 途中打ち切りは `stop_reason` で検知して弾く

## 手順 / 動かし方

### 1. 欲しい構造を「ツール」として定義する

プロンプトで「こう返して」とお願いする代わりに、JSON Schema で構造を宣言する。

```python
import anthropic

client = anthropic.Anthropic()  # ANTHROPIC_API_KEY を自動で読む

extract_tool = {
    "name": "save_review",
    "description": "レビュー文から評価情報を構造化して保存する",
    "input_schema": {
        "type": "object",
        "properties": {
            "sentiment": {
                "type": "string",
                "enum": ["positive", "negative", "neutral"],
                "description": "全体の感情",
            },
            "score": {"type": "integer", "minimum": 1, "maximum": 5},
            "keywords": {
                "type": "array",
                "items": {"type": "string"},
                "description": "評価の根拠になった語",
            },
        },
        "required": ["sentiment", "score", "keywords"],
    },
}
```

### 2. tool_choice でそのツールを強制する

ここが肝。`tool_choice` を指定しないと、モデルは「ツールを使うかどうか」から判断してしまい、普通の文章で返してくることがある。

```python
resp = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    tools=[extract_tool],
    tool_choice={"type": "tool", "name": "save_review"},  # 必ず呼ばせる
    messages=[{
        "role": "user",
        "content": "このレビューを解析して: 「動作は速いが UI が古い。星3くらい」",
    }],
)
```

### 3. tool_use ブロックから取り出す

`tool_choice` で強制した場合、`resp.content` の中に `tool_use` ブロックが入る。その `.input` はパース済みの dict なので、そのまま使える。

```python
def extract_tool_input(resp, tool_name):
    if resp.stop_reason == "max_tokens":
        raise RuntimeError("max_tokens で途中打ち切り。JSON が壊れている可能性大")
    for block in resp.content:
        if block.type == "tool_use" and block.name == tool_name:
            return block.input  # ← すでに dict。json.loads 不要
    raise RuntimeError("tool_use ブロックが見つからない")

data = extract_tool_input(resp, "save_review")
print(data)
# {'sentiment': 'neutral', 'score': 3, 'keywords': ['速い', 'UIが古い']}
```

これで「前置きが混ざる」「コードブロックのフェンスで囲まれる」といった定番の崩れは構造的に発生しなくなる。

## ハマりどころ

### ① tool_choice を省くと結局テキストで返る

`tools` を渡しただけで安心すると、モデルが「今回はツール要らないか」と判断して普通の文章を返す確率が残る。**確実に構造化したいなら `tool_choice={"type":"tool","name":...}` で名指し強制** が必須。`{"type":"auto"}` は任意呼び出しなので構造化用途には向かない。

### ② input_schema が緩いとキーが欠ける

`required` を書かないと、モデルは「埋めやすいキーだけ」返してくることがある。必須キーは必ず `required` に入れる。`enum` や `minimum/maximum` も、書いておくと出力の揺れがかなり減る。スキーマは「お願い」ではなく「制約」だと思って厳しめに書く。

### ③ max_tokens 途中打ち切りで JSON が壊れる

配列を長く吐かせるケースで `max_tokens` に到達すると、途中で生成が止まって不完全な構造になる。SDK は例外を投げず、`resp.stop_reason == "max_tokens"` として **正常っぽく返してくる** のが罠。上のコードのように `stop_reason` を必ず見て、途中打ち切りなら弾く（または `max_tokens` を上げて再試行）。

### ④ dict を信じすぎない → Pydantic で二重に締める

スキーマで縛っても「enum 外の値が来ない」ことまでは 100% 保証されない。受け取り側でもう一枚バリデーションを噛ませておくと、壊れたデータが後段に流れない。

```python
from typing import Literal
from pydantic import BaseModel, conint

class Review(BaseModel):
    sentiment: Literal["positive", "negative", "neutral"]
    score: conint(ge=1, le=5)
    keywords: list[str]

review = Review.model_validate(data)  # 型が違えば ValidationError で即落ちる
```

## 背景・補足

なぜプロンプトで「JSON だけ返して」より Tool Use が安定するのか。前者はモデルの「指示追従の気分」に依存するのに対し、Tool Use はツール呼び出し（関数呼び出し）という別レイヤーの仕組みに乗るため、出力が構造化されることが前提になる。同じ「JSON が欲しい」でも、お願いベースか仕組みベースかで再現性が変わる、というのが体感的な違い。

なお `input_schema` の JSON Schema は全機能が使えるわけではなく、`type` / `enum` / `required` / `properties` あたりの基本が中心。凝った条件分岐（`oneOf` など）は素直に効かないこともあるので、複雑な制約は Pydantic 側に寄せるのが結局ラク。

## まとめ

- 「JSON で返して」とお願いする方式は、たまに壊れて本番で刺さる
- **tools でスキーマ定義 → tool_choice で強制 → tool_use の .input を取る** が構造化出力の基本形
- `.input` はパース済み dict。`json.loads` は不要
- 最後の穴は `max_tokens` 途中打ち切り。`stop_reason` で必ず検知する
- 仕上げに Pydantic で二重チェックすると、壊れたデータが後段に流れない
