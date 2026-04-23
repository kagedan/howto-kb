---
id: "2026-04-03-claude-の-batch-api-で処理費用を半額にした話-01"
title: "Claude の Batch API で処理費用を半額にした話"
url: "https://zenn.dev/ztmyo/articles/claude-batch-api-cost-saving"
source: "zenn"
category: "ai-workflow"
tags: ["API", "zenn"]
date_published: "2026-04-03"
date_collected: "2026-04-04"
summary_by: "auto-rss"
---

# Claude の Batch API で処理費用を半額にした話

Claude API の **Message Batches API** を使うと、通常料金の**50%オフ**でリクエストを処理できます。即時レスポンスが不要なバッチ処理には最適です。

本記事では、実際に Batch API を使って処理費用を半額にした方法を、コード付きで解説します。

## Batch API とは

通常の `messages.create()` は即座にレスポンスが返りますが、Batch API は**非同期**です。リクエストを一括送信し、数分〜数時間後に結果を取得します。

| 項目 | 通常 API | Batch API |
| --- | --- | --- |
| レスポンス | 即時 | 非同期（最大24時間） |
| 料金 | 通常 | **50%オフ** |
| 最大リクエスト数 | 1件ずつ | 10,000件/バッチ |
| ユースケース | チャット、リアルタイム | データ処理、分析、生成 |

## 基本的な使い方

### Step 1: バッチを送信する

```
import anthropic

client = anthropic.Anthropic()

def submit_batch(prompts: list[str]) -> str:
    """バッチリクエストを送信してバッチIDを返す"""
    requests = [
        {
            "custom_id": f"req-{i:04d}",
            "params": {
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}],
            },
        }
        for i, prompt in enumerate(prompts)
    ]

    batch = client.messages.batches.create(requests=requests)

    print(f"バッチ送信完了!")
    print(f"  ID: {batch.id}")
    print(f"  リクエスト数: {len(requests)}")
    print(f"  ステータス: {batch.processing_status}")

    return batch.id
```

### Step 2: 完了を待つ

```
import time

def wait_for_batch(batch_id: str, poll_interval: int = 30) -> None:
    """バッチの完了を待つ"""
    while True:
        batch = client.messages.batches.retrieve(batch_id)
        status = batch.processing_status
        counts = batch.request_counts

        print(
            f"[{status}] 処理済: {counts.succeeded}, "
            f"エラー: {counts.errored}, "
            f"残り: {counts.processing}"
        )

        if status == "ended":
            print("バッチ完了!")
            return

        time.sleep(poll_interval)
```

### Step 3: 結果を取得する

```
def get_results(batch_id: str) -> list[dict]:
    """バッチの結果を取得する"""
    results = []

    for result in client.messages.batches.results(batch_id):
        if result.result.type == "succeeded":
            msg = result.result.message
            results.append({
                "id": result.custom_id,
                "text": msg.content[0].text,
                "input_tokens": msg.usage.input_tokens,
                "output_tokens": msg.usage.output_tokens,
            })
        else:
            results.append({
                "id": result.custom_id,
                "error": str(result.result),
            })

    return results
```

## 実践例: 100件のレビューを一括分析

```
# 100件の商品レビューを感情分析する例
reviews = [
    "この商品は素晴らしいです。品質が良く、配送も早かった。",
    "期待外れでした。サイズが合わず返品しました。",
    # ... 100件
]

prompts = [
    f"以下のレビューの感情を positive/negative/neutral で分類してください。\n\nレビュー: {review}\n\n結果（1語のみ）:"
    for review in reviews
]

# 送信
batch_id = submit_batch(prompts)

# 待機
wait_for_batch(batch_id)

# 結果取得
results = get_results(batch_id)

# 集計
sentiments = [r["text"].strip().lower() for r in results if "text" in r]
print(f"Positive: {sentiments.count('positive')}")
print(f"Negative: {sentiments.count('negative')}")
print(f"Neutral: {sentiments.count('neutral')}")
```

## コスト比較

100件のレビュー分析（平均: 入力200トークン、出力10トークン）:

| 方式 | 入力コスト | 出力コスト | **合計** |
| --- | --- | --- | --- |
| 通常 API (Sonnet) | $0.060 | $0.015 | **$0.075** |
| Batch API (Sonnet) | $0.030 | $0.0075 | **$0.0375** |

**50%削減！** 月に10,000件処理するなら $3.75 の節約になります。

## 注意点

1. **24時間以内に処理される**（通常は数分〜数時間）
2. **リアルタイム性が必要なケースには不向き**
3. バッチあたり最大10,000リクエスト
4. 結果は29日間保存される

## どんなケースで使うべきか

✅ **向いているケース:**

* 夜間のデータ処理パイプライン
* 大量のドキュメント要約
* テストデータの生成
* 定期的なレポート作成
* データマイニング・分類

❌ **向いていないケース:**

* チャットボット
* リアルタイムの応答が必要なAPI
* ユーザーが即座に結果を見たいUI

## まとめ

Batch API は「即時性が不要 → 50%オフ」という非常にシンプルなトレードオフです。バッチ処理のパイプラインがあるなら、使わない理由はありません。

---
