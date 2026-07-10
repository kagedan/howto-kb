---
id: "2026-07-10-claude-の-message-batches-api-で大量リクエストを半額非同期処理する実装手-01"
title: "Claude の Message Batches API で大量リクエストを半額・非同期処理する実装手順 — ポーリングと custom_id 突合の3つのハマりどころ【2026】"
url: "https://qiita.com/yureki_lab/items/319b739f6bb75720ea96"
source: "qiita"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "Python", "qiita"]
date_published: "2026-07-10"
date_collected: "2026-07-11"
summary_by: "auto-rss"
query: ""
---

Claude API を業務で使っていると、「1件ずつ叩くほどリアルタイム性は要らないが、件数が多くてコストと時間が気になる」場面がよくある。分類・要約・タグ付けをまとめて数千件回すようなバッチ処理だ。

こういうときは Message Batches API を使うと、通常の Messages API と**同じ結果を半額(50%オフ)**で処理できる。ただし同期呼び出しではなく「投げて → 待って → 結果を回収する」非同期モデルなので、初見だと結果の突合や取りこぼしでハマる。この記事では最小の動かし方と、自分が実際に踏んだ3つのハマりどころをまとめる。

## 対象と前提

- 想定読者:Claude API を Python から叩いたことがあり、大量件数をコスト最適に処理したいエンジニア
- 前提環境:Python 3.13 / `anthropic` 0.40 系 / モデルは `claude-sonnet-4-6`
- 前提知識:通常の `client.messages.create()` を呼んだことがある

## TL;DR

- `client.messages.batches.create()` に **`custom_id` 付きのリクエスト配列**を渡すと非同期バッチが走る
- `processing_status` が `ended` になるまで**ポーリング**し、`results()` で結果を回収する
- 結果は**投げた順に返らない**。`custom_id` をキーに辞書で突合するのが鉄則
- 料金は通常の半額、結果は最大24時間以内(実際はもっと早い)に揃う

## 手順 / 動かし方

### 1. バッチを投げる

各リクエストに一意の `custom_id` を付けるのがポイント。これが後で結果と入力を結びつける唯一の手がかりになる。

```python
from anthropic import Anthropic
from anthropic.types.messages.batch_create_params import Request
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming

client = Anthropic()  # ANTHROPIC_API_KEY を環境変数から読む

inputs = {
    "req-001": "Pythonのデコレータを一言で説明して",
    "req-002": "async/awaitを一言で説明して",
    # ...数千件でもOK(最大10万件 / 256MB)
}

batch = client.messages.batches.create(
    requests=[
        Request(
            custom_id=cid,
            params=MessageCreateParamsNonStreaming(
                model="claude-sonnet-4-6",
                max_tokens=256,
                messages=[{"role": "user", "content": prompt}],
            ),
        )
        for cid, prompt in inputs.items()
    ]
)
print(batch.id, batch.processing_status)  # msgbatch_xxx in_progress
```

### 2. 完了までポーリングする

`processing_status` は `in_progress` → `ended` と遷移する。`ended` は「全リクエストの処理が終わった」というだけで、個々の成否はまた別(後述)。

```python
import time

while True:
    batch = client.messages.batches.retrieve(batch.id)
    if batch.processing_status == "ended":
        break
    print("counts:", batch.request_counts)  # 進捗が見える
    time.sleep(30)  # 短すぎるとレート制限に当たるので余裕を持つ
```

### 3. 結果を custom_id で回収する

`results()` は JSONL を1行ずつ流すストリーム。`custom_id` をキーに辞書化しておくと後段で入力と突き合わせやすい。

```python
outcomes = {}
for entry in client.messages.batches.results(batch.id):
    outcomes[entry.custom_id] = entry.result

for cid, prompt in inputs.items():
    r = outcomes[cid]
    if r.type == "succeeded":
        print(cid, r.message.content[0].text[:40])
    elif r.type == "errored":
        print(cid, "ERROR", r.error.type)
    else:  # expired / canceled
        print(cid, r.type)
```

## ハマりどころ

### ① 結果は投げた順に返らない

最初、入力リストと結果を `zip()` で対応づけて盛大にズレた。バッチ内の処理順・返却順は**保証されない**。だから `custom_id` が必須で、突合は必ずこのキーで行う。`enumerate` のインデックス頼りは事故る。

### ② `results()` は「1回きりのストリーム」

`results()` の戻り値をログ出力だけして再度ループしようとしたら、2周目が空になった。これはイテレータを消費し切っているため。複数回使うなら、下のように**最初に list 化して手元へ落とす**。

```python
all_results = list(client.messages.batches.results(batch.id))
```

### ③ `ended` = 全部成功、ではない

`processing_status == "ended"` はバッチ全体が完了したという意味で、個々のリクエストが成功したかは `result.type` を見ないと分からない。`succeeded` / `errored` / `canceled` / `expired`(24時間以内に処理し切れなかった分)の4種を必ず分岐する。`errored` はモデル側の一時エラーのこともあるので、失敗分だけ集めて再バッチに回すと無駄がない。

## 背景・補足

半額になるのは「即時性を捨てる」対価だと理解すると使いどころが見える。ユーザーを待たせる同期 API と違い、バッチは裏で空いたキャパを使うから安い。逆に「今この画面のレスポンスに使う」用途には向かない。夜間にまとめて回す集計・分類・下書き生成のような、自分の手を離れて動く処理と相性がいい。無人で回すジョブに組み込むなら、②のストリーム消費と③の `expired` 検知を最初から入れておくと後で泣かずに済む。

## まとめ

- 大量・非リアルタイムな Claude 呼び出しは Message Batches API で半額にできる
- 非同期モデルなので「投げる → `ended` までポーリング → `results()` 回収」の3段構え
- 突合は必ず `custom_id`、順序は信用しない
- `results()` は使い捨てストリーム、必要なら即 list 化
- `ended` は完了であって成功ではない。`result.type` の4分岐を必ず書く
