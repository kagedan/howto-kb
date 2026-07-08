---
id: "2026-07-08-claude-api-が-overloaded-error-429-で落ちる-anthropic-s-01"
title: "Claude API が overloaded_error / 429 で落ちる — Anthropic SDK の自動リトライだけでは足りない理由と指数バックオフ+ジッターの実装手順【2026】"
url: "https://qiita.com/yureki_lab/items/cbd573de10db20193ab9"
source: "qiita"
category: "ai-workflow"
tags: ["API", "Python", "qiita"]
date_published: "2026-07-08"
date_collected: "2026-07-09"
summary_by: "auto-rss"
query: ""
---

## はじめに / 対象と前提

Claude API(Anthropic Python SDK)でそこそこの量のリクエストを投げていると、ある日突然こういうのに出くわす。

```
anthropic.InternalServerError: Error code: 529 - {'type': 'error', 'error': {'type': 'overloaded_error', 'message': 'Overloaded'}}
anthropic.RateLimitError: Error code: 429 - {'type': 'error', 'error': {'type': 'rate_limit_error', ...}}
```

単発のスクリプトなら「もう一回叩けば通る」で済む。でも無人で長時間回すバッチや自律エージェントだと、この 1 回で処理系全体が止まる。翌朝ログを見たら夜中の 2 時で死んでいた、というのを何度かやった。

この記事は「そこで落とさないためのリトライ設計」を、実装コードと一緒にまとめる。

- 想定読者:Claude API を Python から叩いていて、たまに 429 / 529 で落ちて困っている人
- 前提:`anthropic` SDK を触ったことがある(`messages.create` を呼べる)
- 環境:Python 3.13 / `anthropic` 0.40 系 / モデルは `claude-sonnet-4-6`

## TL;DR

- SDK は **すでにリトライしている**(`max_retries` 既定 2、429/5xx/接続エラーが対象、`Retry-After` ヘッダも尊重)。まず既定値を上げるだけで大半は片付く。
- それでも足りないのは **(1) 長時間ジョブでリトライ回数が不足** **(2) streaming が途中で切れると SDK は自動再開しない** の 2 ケースだけ。
- 自前で書くなら **リトライ対象を絞る + `Retry-After` 優先 + full jitter** の 3 点を外さない。

## まず SDK の既定リトライを知る

自前で何か書く前に、SDK が何をやってくれているかを押さえる。ここを知らずに自作すると、たいてい二重リトライで自爆する(後述)。

`anthropic` SDK は `max_retries`(既定 2)まで、以下を自動リトライする。

- 408 / 409 / 429 / 5xx(529 含む)
- 接続エラー・タイムアウト
- レスポンスに `Retry-After` / `retry-after-ms` があればその秒数を尊重、無ければ指数バックオフ + ジッター

つまり「たまの 529」程度なら、既定値を上げるだけで十分なことが多い。

```python
from anthropic import Anthropic

# クライアント全体の既定を上げる
client = Anthropic(max_retries=5, timeout=60.0)

# 特定リクエストだけ厚くしたいとき
resp = client.with_options(max_retries=8).messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "ping"}],
)
```

**まずここを試す。** これで解決するなら、リトライ処理を自作する必要はない。

## それでも自前でリトライを書く場面

SDK 任せで足りないのは主に 2 つ。

1. **無人ジョブでリトライ回数・待ち時間をアプリ側で制御したい**。既定 2 回ではピーク時に足りない、ログを残したい、閾値を超えたらアラートを飛ばしたい、など。
2. **streaming が途中で切れたとき**。`messages.stream` の途中で接続が切れると、SDK は「途中から再開」してくれない。丸ごとやり直しになる。

non-streaming のラッパはこんな形になる。

```python
import random, time
import anthropic

# リトライして意味があるものだけ拾う
RETRYABLE = (
    anthropic.RateLimitError,       # 429
    anthropic.InternalServerError,  # 5xx(529 = overloaded_error 含む)
    anthropic.APIConnectionError,   # 接続断・タイムアウト
)

def _retry_after(err) -> float | None:
    resp = getattr(err, "response", None)  # 接続エラーは response を持たない
    if resp is None:
        return None
    val = resp.headers.get("retry-after")
    try:
        return float(val) if val is not None else None
    except ValueError:
        return None

def create_with_retry(client, *, max_attempts=6, cap=60.0, **kwargs):
    for attempt in range(max_attempts):
        try:
            return client.messages.create(**kwargs)
        except RETRYABLE as e:
            if attempt == max_attempts - 1:
                raise
            wait = _retry_after(e)
            if wait is None:
                # full jitter: 0〜(2^n) 秒の一様乱数、cap で頭打ち
                wait = random.uniform(0, min(cap, 2 ** attempt))
            print(f"[retry] {type(e).__name__} attempt={attempt+1} sleep={wait:.1f}s")
            time.sleep(wait)
```

400 / 401 / 403 / 422 系(`BadRequestError` など)は `RETRYABLE` に入れていない。リクエスト自体が間違っているので、何回投げても通らない。ここを混ぜないのが最初のポイント。

## streaming の途中切断はまるごとやり直す

ストリーミングは途中で切れると SDK が自動再開しないので、アプリ側で包む。部分出力は捨てて丸ごと再試行する。

```python
def stream_text_with_retry(client, *, max_attempts=6, cap=60.0, **kwargs):
    for attempt in range(max_attempts):
        try:
            parts = []
            with client.messages.stream(**kwargs) as stream:
                for text in stream.text_stream:
                    parts.append(text)
            return "".join(parts)
        except (anthropic.APIConnectionError, anthropic.InternalServerError) as e:
            if attempt == max_attempts - 1:
                raise
            wait = random.uniform(0, min(cap, 2 ** attempt))
            print(f"[stream-retry] {type(e).__name__} attempt={attempt+1} sleep={wait:.1f}s")
            time.sleep(wait)
```

長い生成の途中で切れると、それまでのトークンは丸ごと無駄になる。streaming で長文を吐かせるほど、この「まるごとやり直し」コストは効いてくる。`max_tokens` を欲張りすぎないのも、地味だが効く回避策。

## ハマりどころ

- **SDK が既にリトライしていることを知らずに二重に包む** → 実効リトライ回数が `自前 × SDK既定` で跳ね上がり、429 が余計に増える。自前で回すなら SDK 側は `max_retries=0` にして一本化する。
  ```python
  client = Anthropic(max_retries=0)  # リトライ制御を自前に寄せる
  ```
- **429 と 529 を同じものだと思う** → 429 は「あなたのレート超過」、529(overloaded_error)は「Anthropic 側が混雑」。前者は同時実行数やレート上限の問題、後者はこちらに非がない。SDK 上はクラスも分かれる(429=`RateLimitError` / 529=`InternalServerError`)。ステータスコードで切り分けたいときは `except anthropic.APIStatusError as e: e.status_code` を見る。
- **`Retry-After` を無視して固定 sleep** → レート制限がまだ明けていないのに叩き直して、また 429。ヘッダがあれば必ず優先する。
- **ジッター無しの `2 ** n`** → 複数ワーカーが同じ秒数で一斉に復帰して雪崩れる(thundering herd)。復帰タイミングをばらす full jitter を入れる。同時実行が多いほど効く。
- **接続エラーで `response` を触って `AttributeError`** → `APIConnectionError` は HTTP レスポンスを持たない。`getattr(err, "response", None)` で守る。

## 動作確認

意図的に 529 を起こすのは難しいので、まずはログで「リトライが効いているか」を見えるようにするのが早い。上の `print` を入れておくと、混雑時にこう出る。

```
[retry] InternalServerError attempt=1 sleep=1.4s
[retry] RateLimitError attempt=2 sleep=0.7s
（3回目で成功、返り値が返る）
```

リトライが 1〜2 回で吸収できていれば OK。逆に、毎回 `max_attempts` 上限まで張り付くようなら、それはリトライで直る話ではない。レート上限の見直し(同時実行数を下げる / プランを上げる)が必要なサインなので、そこはコードでなく運用側で直す。

## 背景 — 自律システムでは「落ちない」が最優先

自分が組んでいる完全自律実装システム(24 時間、無人で実装タスクを回す仕組み)では、1 晩で数百〜数千回 Claude API を叩く。ここで 1 回の overloaded を握りつぶせないと、翌朝まで処理が止まって丸々 1 日ロスする。

だから「賢く書く」より前に「落ちないように書く」ほうが優先度が高い。派手さはないが、リトライ設計は無人運用の生命線になる。

抑えるポイントは 1 つだけで、**リトライで直るエラー(429 / 5xx / 接続断)と、直らないエラー(400 / 401 / 422)を最初にきっぱり分ける**こと。ここを混ぜると、直らないエラーを延々リトライして時間とトークンを溶かす。

## まとめ

- まず `max_retries` を上げる。SDK が 429 / 5xx / 接続エラーを `Retry-After` 尊重で自動リトライしてくれる。
- 自前で書くのは「長時間ジョブの制御」と「streaming の途中切断」の 2 ケースだけ。
- 自前で書くときは、リトライ対象を絞る(429/5xx/接続断だけ)/ `Retry-After` 優先 / full jitter、の 3 点を外さない。
- 自前で回すなら SDK 側は `max_retries=0` にして、二重リトライを避ける。
