---
id: "2026-04-14-claude-message-batches-api入門-300kトークン出力ベータで大規模テキスト-01"
title: "Claude Message Batches API入門 — 300kトークン出力ベータで大規模テキスト生成を最適化する"
url: "https://zenn.dev/kai_kou/articles/192-claude-message-batches-300k-output-guide"
source: "zenn"
category: "ai-workflow"
tags: ["API", "zenn"]
date_published: "2026-04-14"
date_collected: "2026-04-15"
summary_by: "auto-rss"
---

## はじめに

Claude APIでは、2026年3月30日に**Message Batches APIの300kトークン出力ベータ**が追加されました。通常モデルの最大出力上限（Sonnet 4.6: 64k、Opus 4.6: 128k）を大幅に超える**最大30万トークンの出力**が、バッチ処理経由で利用可能になっています。

### この記事で学べること

* Claude Message Batches APIの基本的な使い方
* 300kトークン出力ベータの有効化と実装方法
* 料金構造とコスト最適化の考え方
* Haiku 3廃止（2026年4月20日）への対応方法

### 対象読者

* Claude APIを使った大量テキスト処理をPythonで実装したい方
* バッチ処理でコストを削減したい方
* 書籍・長大ドキュメント生成などのユースケースを検討している方

### 前提環境

* Python 3.10以上（match構文を使用するため）
* Anthropic Python SDK (`pip install anthropic`)
* Anthropic APIキー

---

## TL;DR

* Message Batches APIはClaude APIの通常料金より**50%オフ**でバッチ処理を実行できる
* ベータヘッダー `anthropic-beta: output-300k-2026-03-24` を付けると、Claude Opus 4.6 / Sonnet 4.6 で最大**30万トークン出力**が可能
* バッチ処理時間は最大24時間（多くの場合1時間以内）で、大規模なオフライン処理に最適
* `claude-3-haiku-20240307` は2026年4月20日に廃止予定。`claude-haiku-4-5-20251001` への移行が必要

---

## Message Batches APIとは

[Message Batches API](https://platform.claude.com/docs/en/build-with-claude/batch-processing) は、Claudeへの多数のリクエストをまとめて非同期処理するためのAPIです。

### 通常のMessages APIとの比較

| 項目 | Messages API（同期） | Message Batches API（非同期） |
| --- | --- | --- |
| レスポンス | リアルタイム | 非同期（処理完了後に取得） |
| 料金 | 通常価格 | **50%オフ** |
| 最大出力 | Opus: 128k / Sonnet: 64k | 最大300kトークン（ベータ） |
| 向いている処理 | インタラクティブ | バッチ・オフライン処理 |

### 主な仕様

* **バッチサイズ上限**: 1バッチあたり最大100,000リクエスト、または256 MB（どちらか先に到達した方）
* **処理ウィンドウ**: 最大24時間（多くの場合1時間以内に完了）
* **結果の保持期間**: 作成から29日間ダウンロード可能
* **スコープ**: バッチはWorkspaceスコープ。同一ワークスペース内の全APIキーから参照可能

---

## 基本的な使い方

### バッチの作成

まず、複数のリクエストをまとめてバッチを作成します。

```
import anthropic
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request

client = anthropic.Anthropic()

message_batch = client.messages.batches.create(
    requests=[
        Request(
            custom_id="request-001",
            params=MessageCreateParamsNonStreaming(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": "Pythonでクイックソートを実装してください。"
                }],
            ),
        ),
        Request(
            custom_id="request-002",
            params=MessageCreateParamsNonStreaming(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": "JavaScriptでバブルソートを実装してください。"
                }],
            ),
        ),
    ]
)

print(f"Batch ID: {message_batch.id}")
print(f"Status: {message_batch.processing_status}")
```

各リクエストに `custom_id` を設定することで、後から結果を識別できます。

### 処理状況のポーリング

バッチの処理が完了するまで定期的に状態を確認します。

```
import time
import anthropic

client = anthropic.Anthropic()
BATCH_ID = "msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d"  # 作成時のIDに置き換える

while True:
    message_batch = client.messages.batches.retrieve(BATCH_ID)
    
    if message_batch.processing_status == "ended":
        print("バッチ処理完了")
        break
    
    print(f"ステータス: {message_batch.processing_status} — 待機中...")
    time.sleep(60)  # 1分おきにチェック
```

`processing_status` が `"ended"` になったら結果が取得可能です。

### 結果の取得

```
import anthropic

client = anthropic.Anthropic()

for result in client.messages.batches.results(BATCH_ID):
    match result.result.type:
        case "succeeded":
            content = result.result.message.content[0].text
            print(f"[{result.custom_id}] 成功:\n{content[:100]}...")
        case "errored":
            error_type = result.result.error.type
            if error_type == "invalid_request":
                print(f"[{result.custom_id}] リクエストエラー: {result.result.error}")
            else:
                print(f"[{result.custom_id}] サーバーエラー")
        case "expired":
            print(f"[{result.custom_id}] 24時間以内に処理されず期限切れ")
```

結果は`.jsonl`形式でストリーミング取得されます。**入力順とは異なる順で返る場合があるため、`custom_id` で識別**してください。

---

## 300kトークン出力ベータの使い方

2026年3月30日に追加された`output-300k-2026-03-24`ベータを使うと、標準上限（Opus: 128k / Sonnet: 64k）を超えた**最大30万トークン**の出力が可能になります。

### 対応モデル

| モデル | API ID | 通常最大出力 | ベータ時最大出力 |
| --- | --- | --- | --- |
| Claude Opus 4.6 | `claude-opus-4-6` | 128,000 | **300,000** |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | 64,000 | **300,000** |

### 実装方法

300kトークン出力ベータを使う場合は、`client.beta.messages.batches.create` を使用し、`betas` パラメータにヘッダー名を指定します。

```
import anthropic
from anthropic.types.beta.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.beta.messages.batch_create_params import Request

client = anthropic.Anthropic()

message_batch = client.beta.messages.batches.create(
    betas=["output-300k-2026-03-24"],  # ベータヘッダーの指定
    requests=[
        Request(
            custom_id="long-form-001",
            params=MessageCreateParamsNonStreaming(
                model="claude-opus-4-6",
                max_tokens=300_000,  # 最大30万トークンを指定
                messages=[
                    {
                        "role": "user",
                        "content": (
                            "分散システム設計の包括的なガイドを作成してください。"
                            "CAP定理、一貫性モデル、ネットワーク分断への対処法、"
                            "Raft・Paxosコンセンサスアルゴリズム、"
                            "マイクロサービスとモノリスの選択基準、"
                            "可観測性の実装まで詳細に解説してください。"
                        ),
                    }
                ],
            ),
        ),
    ],
)

print(f"Batch ID: {message_batch.id}")
```

通常のBatches APIと異なり、`client.beta.messages.batches` を使用し、インポート元も `anthropic.types.beta.*` に変わる点に注意してください。

### cURLでの利用

```
curl https://api.anthropic.com/v1/messages/batches \
     --header "x-api-key: $ANTHROPIC_API_KEY" \
     --header "anthropic-version: 2023-06-01" \
     --header "anthropic-beta: output-300k-2026-03-24" \
     --header "content-type: application/json" \
     --data '{
         "requests": [{
             "custom_id": "long-form-001",
             "params": {
                 "model": "claude-opus-4-6",
                 "max_tokens": 300000,
                 "messages": [{
                     "role": "user",
                     "content": "..."
                 }]
             }
         }]
     }'
```

### 300kトークン生成時の注意点

[公式ドキュメント](https://platform.claude.com/docs/en/build-with-claude/batch-processing)によると:

> "A single 300k-token generation can take over an hour to complete, so plan your batch submissions with the 24-hour processing window in mind."

1回の300kトークン生成には1時間以上かかる場合があります。バッチの処理ウィンドウ（最大24時間）を念頭においた設計が必要です。

**300kトークン出力の主なユースケース:**

* 書籍・長大な技術ドキュメントの一括生成
* 大規模な構造化データ抽出
* 長いコードスキャフォールドの生成
* 長い推論チェーンが必要なタスク

---

## 料金とコスト最適化

### バッチ料金（通常の50%オフ）

[公式の料金ページ](https://platform.claude.com/docs/en/about-claude/pricing)より。バッチAPIは通常APIの50%オフが適用されます。

| モデル | バッチ入力料金 | バッチ出力料金 |
| --- | --- | --- |
| Claude Opus 4.6 | $2.50 / MTok | $12.50 / MTok |
| Claude Sonnet 4.6 | $1.50 / MTok | $7.50 / MTok |
| Claude Haiku 4.5 | $0.50 / MTok | $2.50 / MTok |
| Claude Haiku 3.5 | $0.40 / MTok | $2.00 / MTok |

※ MTok = 100万トークン

### コスト試算例

300kトークン出力を1件生成する場合（Opus 4.6バッチ）:

* 入力 2,000トークン: $2.50 / 1,000,000 × 2,000 = **$0.005**
* 出力 300,000トークン: $12.50 / 1,000,000 × 300,000 = **$3.75**
* 合計: 約 **$3.76**（同期APIなら約 **$7.52**）

### プロンプトキャッシュとの組み合わせ

バッチ割引とプロンプトキャッシュ割引は\*\*スタック（重複適用）\*\*できます。

システムプロンプトが長い場合は、[自動キャッシュ](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)（2026年2月GA）を活用することでさらなるコスト削減が可能です。

---

## Claude Haiku 3廃止への対応（2026年4月20日）

バッチ処理でHaiku 3を使用している場合、**2026年4月20日**に廃止されます。

### 移行方法

```
# 変更前（廃止予定）
model = "claude-3-haiku-20240307"

# 変更後（推奨）
model = "claude-haiku-4-5-20251001"
```

[Claude Haiku 4.5](https://platform.claude.com/docs/en/about-claude/models/overview) は200kコンテキスト、64k出力に対応し、Haiku 3から大幅に性能が向上しています。バッチ料金は $0.50 / $2.50 (MTok) です。

---

## まとめ

* **Message Batches API** は通常の50%オフで非同期バッチ処理が可能
* **300kトークン出力ベータ** (`output-300k-2026-03-24`) を使うとOpus 4.6 / Sonnet 4.6 で書籍長の出力が1リクエストで生成できる
* 実装は `client.beta.messages.batches.create` に `betas=["output-300k-2026-03-24"]` を指定するだけ
* 300kトークン生成は1時間以上かかる場合があり、24時間処理ウィンドウを前提に設計する
* **Haiku 3ユーザーは4月20日までに `claude-haiku-4-5-20251001` へ移行**が必要

大量のドキュメント生成や長大なコード生成など、レイテンシを問わない処理ではBatches APIを活用することでAPIコストを大幅に削減できます。

## 参考リンク
