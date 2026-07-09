---
id: "2026-07-09-claude-の-extended-thinking思考予算を-anthropic-python-s-01"
title: "Claude の extended thinking(思考予算)を Anthropic Python SDK で使う — thinking ブロックの取り出しと tool use 併用時の3つのハマりどころ【2026】"
url: "https://qiita.com/yureki_lab/items/7249c2412cd102e253ab"
source: "qiita"
category: "ai-workflow"
tags: ["API", "Python", "qiita"]
date_published: "2026-07-09"
date_collected: "2026-07-10"
summary_by: "auto-rss"
query: ""
---

## はじめに / 対象と前提

Claude の **extended thinking(拡張思考 / 思考予算)** を Anthropic 公式 Python SDK から使うときの実装手順と、実際に動かして踏んだハマりどころをまとめる。「有効化のフラグ自体はすぐ見つかるのに、レスポンスの取り出し方と、tool use と組み合わせた瞬間に 400 が返ってきて詰まる」——そこを再現可能な粒度で書く。

- **想定読者**: Anthropic API を Python から叩いたことがあり、`messages.create` は使えるが extended thinking はまだ、という人
- **前提環境**: Python 3.13 / `anthropic` Python SDK 0.69 系 / モデルは `claude-sonnet-4-6`
- 認証は `ANTHROPIC_API_KEY` を環境変数に入れてある前提

## TL;DR

- `thinking={"type": "enabled", "budget_tokens": N}` を渡すだけで有効化できる。ただし **`budget_tokens` は 1024 以上かつ `max_tokens` 未満** でないと 400。
- レスポンスは `text` ブロックだけではなく **`thinking` ブロックが先頭に混ざる**。`b.type` で振り分けて取り出す。
- **tool use と併用する場合、直前ターンの `thinking` ブロックを署名付きでそのまま次リクエストに戻さないと 400 になる**。ここが最大の罠。

## 手順 / 動かし方

### 1. 最小の呼び出し

```python
import anthropic

client = anthropic.Anthropic()

resp = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=16000,
    thinking={"type": "enabled", "budget_tokens": 10000},
    messages=[{"role": "user", "content": "整数を素因数分解する関数を設計して。まず方針を検討してから答えて。"}],
)

for block in resp.content:
    print(block.type)
# -> thinking
# -> text
```

`resp.content` は配列で、**思考が `thinking` ブロック、最終回答が `text` ブロック**として別々に入ってくる。`resp.content[0].text` のように決め打ちで取ると、思考ブロックを掴んで `AttributeError` になる。

### 2. thinking と回答を分離して取り出す

```python
thinking = "".join(b.thinking for b in resp.content if b.type == "thinking")
answer   = "".join(b.text     for b in resp.content if b.type == "text")

print("=== 思考 ===\n", thinking[:200], "...")
print("=== 回答 ===\n", answer)
```

`type` で振り分けるのがポイント。`thinking` ブロックには本文 `.thinking` のほかに **`.signature`(改ざん検知用の署名)** が付いている。これは後述の tool use で必須になる。

### 3. streaming で思考をリアルタイム表示

思考は長いと数秒〜十数秒かかるので、CLI ツールに組み込むなら streaming で流したい。

```python
with client.messages.stream(
    model="claude-sonnet-4-6",
    max_tokens=16000,
    thinking={"type": "enabled", "budget_tokens": 10000},
    messages=[{"role": "user", "content": "..."}],
) as stream:
    for event in stream:
        if event.type == "content_block_delta":
            if event.delta.type == "thinking_delta":
                print(event.delta.thinking, end="", flush=True)
            elif event.delta.type == "text_delta":
                print(event.delta.text, end="", flush=True)
```

`content_block_delta` の中で `delta.type` が `thinking_delta` か `text_delta` かを見て出し分ける。思考ブロックの終わりには `signature_delta` も飛んでくるが、`stream.get_final_message()` を使えば署名は自動で組み立ててくれるので、自前で連結する必要はない。

## ハマりどころ

### ① `budget_tokens` の下限と上限で 400

```
BadRequestError: `thinking.budget_tokens` must be less than `max_tokens`
```

- **`budget_tokens` は 1024 が下限**。それ未満だと弾かれる。
- **`budget_tokens < max_tokens` が必須**。思考も出力トークンを消費するので、`max_tokens` は「思考予算 + 最終回答ぶん」を見込んで大きめに取る。上の例で `max_tokens=16000, budget=10000` にしているのは、回答に 6000 残す意図。

### ② tool use 併用時、thinking を戻さないと 400

一番ハマったのがこれ。tool use のループで、モデルが `tool_use` を返す → こちらが `tool_result` を返す、という往復をするとき、**assistant ターンの `thinking` ブロックを削って `tool_use` だけ戻すと 400 になる**。

```
BadRequestError: messages: final assistant content block must be ... thinking block is required
```

正しくは、モデルが返した `resp.content`(thinking も tool_use も含む配列)を **丸ごと** assistant メッセージとして積み、その後に `tool_result` を足す。

```python
messages.append({"role": "assistant", "content": resp.content})  # thinking を消さない
messages.append({
    "role": "user",
    "content": [{
        "type": "tool_result",
        "tool_use_id": tool_use_block.id,
        "content": str(result),
    }],
})
```

`thinking` ブロックには `.signature` が入っており、API 側はこの署名で「その思考が本物か」を検証する。だから **署名ごとそのまま戻す**必要がある。要約したり別テキストに差し替えたりするとアウト。

### ③ `redacted_thinking` と temperature

- ごく稀に思考が暗号化された **`redacted_thinking` ブロック**(`.data` を持つ)で返ることがある。中身は読めないが、②と同じくマルチターンでは **そのまま戻す**。デコードしようとしない。
- extended thinking を有効にしているときは **`temperature` を 1 以外にすると 400**(思考中はサンプリング変更不可)。既定のまま触らないのが無難。

## 背景・補足

思考ブロックの署名を戻させる仕組みは、「モデルが自分の推論を捏造・改変されないため」の整合性チェックだと理解しておくと腑に落ちる。だから署名を落とせない。tool use を挟むエージェント的なループを組むときほど、この「content を丸ごと積む」実装に寄せておくと事故が減る。

なお、tool use の途中でも思考を挟ませたい(ツール結果を見て考え直させたい)場合は、ベータヘッダ `interleaved-thinking-2025-05-14` を `client.beta.messages.create(..., betas=[...])` で付ける。付けないと、思考は基本的にターン先頭に一度だけ入る挙動になる。

## 動作確認

- ①: `budget_tokens=512` にして `BadRequestError` を確認 → 1024 以上に上げて解消。
- ②: tool use ループで `thinking` を削って 400 を再現 → `resp.content` を丸ごと積む方式に直して解消。`usage.output_tokens` に思考ぶんも乗るのでコスト増は実測しておく。
- ③: `temperature=0.2` を足して 400 を確認 → 削除して解消。

## まとめ

- 有効化は `thinking={"type":"enabled","budget_tokens":N}` の 1 行。ただし **1024 ≤ budget < max_tokens** を守る。
- レスポンスは `type` で `thinking` / `text` を振り分けて取り出す。決め打ちインデックスは禁物。
- **tool use 併用時は `thinking` ブロックを署名ごと丸ごと戻す**。これを外すと 400 で必ず詰まる。
- `redacted_thinking` はそのまま戻す、思考中は `temperature` を触らない。
