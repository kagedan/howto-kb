---
id: "2026-07-12-claude-api-の-count-tokens-で事前にトークン数を見積もる実装-システムプロン-01"
title: "Claude API の count_tokens で事前にトークン数を見積もる実装 — システムプロンプト・tool定義を含めた計算と料金試算の3つのハマりどころ【2026】"
url: "https://qiita.com/yureki_lab/items/4c2de4f0b6174b9dcbab"
source: "qiita"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "Python", "qiita"]
date_published: "2026-07-12"
date_collected: "2026-07-13"
summary_by: "auto-rss"
query: ""
---

## はじめに / 対象と前提

Claude API(Anthropic Python SDK)を業務に組み込んでいて、「このリクエスト、送る前に何トークンになるか知りたい」と思ったことがある人向けの記事です。

想定読者:

- Python で Claude API を呼び出す実装をしている
- 長いシステムプロンプトや複数の tool 定義を持つエージェントを運用していて、コストや `max_tokens` 超過が気になっている
- `count_tokens` という名前は知っているが、実際に手を動かしたことはない

前提環境:

- Python 3.13
- `anthropic` SDK(pip 最新版)
- モデルは `claude-sonnet-4-6` を例に使う

## TL;DR

- `client.messages.count_tokens()` に、実際に送るのと同じ `messages` / `system` / `tools` を渡すだけで、課金前にトークン数が分かる
- **system prompt・tools の `input_schema`・画像もすべて加算対象**。テキストだけ数えて安心すると実際の請求とズレる
- `cache_control` を付けたリクエストでも `count_tokens` は「キャッシュが効いた場合の割引後の数値」を返さない。素の入力トークン数として扱われる点に注意
- 見積もり値 × 単価で、実行前に USD 概算を出す関数を書いておくと便利

## 手順 / 動かし方

### 1. 最小構成で叩いてみる

```python
import anthropic

client = anthropic.Anthropic()

result = client.messages.count_tokens(
    model="claude-sonnet-4-6",
    messages=[
        {"role": "user", "content": "この記事の要約を3行で書いて"}
    ],
)

print(result)
# => MessageTokensCount(input_tokens=15)
```

`count_tokens` は課金対象の API 呼び出しではなく、専用のカウント用エンドポイントを叩く。実際に生成はしないので `output_tokens` は返ってこない(出力トークン数は生成してみないと分からないため、これは仕様)。

### 2. system prompt / tools を含めて見積もる

自分が普段運用しているエージェントは、system prompt が長く tool 定義も複数あることが多い。これらもまとめて見積もるのが本題。

```python
tools = [
    {
        "name": "search_docs",
        "description": "社内ドキュメントを全文検索する",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "top_k": {"type": "integer", "default": 5},
            },
            "required": ["query"],
        },
    }
]

system_prompt = "あなたは社内ドキュメント検索アシスタントです。..."  # 実際はもっと長い

result = client.messages.count_tokens(
    model="claude-sonnet-4-6",
    system=system_prompt,
    tools=tools,
    messages=[
        {"role": "user", "content": "経費精算のルールを教えて"}
    ],
)

print(result.input_tokens)
```

自分の環境で試したところ、tool 定義 1 個(shallow な schema)でも数十〜百トークン単位で加算された。tool を 5 個も 10 個も持つエージェントだと、system prompt よりも tools 側のトークン消費が大きくなるケースもあったので、「system prompt だけ最適化して満足していた」時期は見積もりが甘かったと分かった。

### 3. 見積もり値から USD を概算する

```python
# 2026年時点の claude-sonnet-4-6 の目安単価(要:最新の公式料金ページで確認)
INPUT_PRICE_PER_MTOK = 3.0   # USD / 1M tokens
OUTPUT_PRICE_PER_MTOK = 15.0  # USD / 1M tokens

def estimate_cost(input_tokens: int, expected_output_tokens: int) -> float:
    input_cost = input_tokens / 1_000_000 * INPUT_PRICE_PER_MTOK
    output_cost = expected_output_tokens / 1_000_000 * OUTPUT_PRICE_PER_MTOK
    return round(input_cost + output_cost, 6)

result = client.messages.count_tokens(
    model="claude-sonnet-4-6",
    system=system_prompt,
    tools=tools,
    messages=[{"role": "user", "content": "経費精算のルールを教えて"}],
)
print(estimate_cost(result.input_tokens, expected_output_tokens=500))
```

出力トークンは生成してみないと確定しないので、`expected_output_tokens` は自分のユースケースの経験則(過去ログの平均値など)を入れる。バッチ処理で「1回あたりの上限予算」を決めているなら、この関数を実行前チェックに組み込んで、閾値を超えたら送信をスキップする、という使い方をしている。

## ハマりどころ

### 1. `cache_control` を付けても数値が変わらない

```
symptom: prompt caching を有効化しているのに、count_tokens の結果が
         毎回同じ input_tokens を返す。「キャッシュ分は安くなっているはず」と
         思ってこの数値でコスト計算すると、実際の請求より高く見積もってしまう
```

原因:`count_tokens` は「このリクエストを送ったら入力として何トークン消費するか」の**素の入力トークン数**を返すだけで、キャッシュヒット時の割引後の金額計算はしてくれない。キャッシュのヒット率・割引は実際にリクエストを送った後のレスポンスの `usage.cache_read_input_tokens` を見るしかない。

回避策:`count_tokens` は「上限に収まるか」「大まかな規模感」を見るためのものと割り切り、キャッシュ込みの正確なコストは本番リクエストの `usage` フィールドを集計して把握する。

### 2. モデル名の指定ミスで見積もりがズレる

```
symptom: count_tokens に古いモデル名(例: 廃止済みのエイリアス)を
         渡してもエラーにならず、微妙に違う数値が返ってくることがあった
```

原因:モデルによってトークナイザーが異なる場合がある。実際にリクエストするモデル名と `count_tokens` に渡すモデル名が食い違っていると、見積もりと実測がズレる。

回避策:`count_tokens` に渡す `model` パラメータは、実際に `messages.create` で使う変数と共通化する(定数を分けない・ハードコードを二重に書かない)。

```python
MODEL_NAME = "claude-sonnet-4-6"

# 見積もり
client.messages.count_tokens(model=MODEL_NAME, ...)
# 本番リクエスト
client.messages.create(model=MODEL_NAME, ...)
```

### 3. tools の `input_schema` を最小化しないと想定以上に膨らむ

```
symptom: tool を5個登録しているエージェントで、
         system prompt を削っても入力トークンがほとんど減らなかった
```

原因:`input_schema` に `description` を各プロパティに丁寧に書いていたり、`enum` の選択肢を大量に列挙していたりすると、tools 側だけで数百〜千トークン単位になっていた。

回避策:`count_tokens` に `tools` だけ渡した結果と `tools=[]` で渡した結果を比較して、tools 側の消費量を切り分ける。

```python
with_tools = client.messages.count_tokens(
    model=MODEL_NAME, tools=tools, messages=messages
).input_tokens
without_tools = client.messages.count_tokens(
    model=MODEL_NAME, tools=[], messages=messages
).input_tokens
print(f"tools分: {with_tools - without_tools} tokens")
```

これで「tools が原因で膨らんでいる」のか「system prompt が原因」なのかを定量的に切り分けられる。

## まとめ

- `count_tokens` は課金なしでトークン数を確認できる専用エンドポイント。system prompt / tools / 画像もすべて加算対象
- キャッシュの割引は反映されない。キャッシュ込みコストは実行後の `usage` から集計する
- モデル名は本番リクエストと共通の定数で管理し、見積もりと実測のズレを防ぐ
- `tools=[]` との差分を取れば、tool 定義がどれだけトークンを食っているか切り分けられる
- バッチ処理の実行前チェックに組み込んでおくと、想定外のコスト超過を未然に防げる
