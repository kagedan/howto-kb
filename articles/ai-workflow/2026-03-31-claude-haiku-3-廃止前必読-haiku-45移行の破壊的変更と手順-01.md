---
id: "2026-03-31-claude-haiku-3-廃止前必読-haiku-45移行の破壊的変更と手順-01"
title: "Claude Haiku 3 廃止前必読 — Haiku 4.5移行の破壊的変更と手順"
url: "https://qiita.com/kai_kou/items/34443f80a44c787b0b00"
source: "qiita"
category: "ai-workflow"
tags: ["API", "Python", "qiita"]
date_published: "2026-03-31"
date_collected: "2026-04-01"
summary_by: "auto-rss"
---

## はじめに

Anthropicは2026年4月19日をもって、**Claude Haiku 3**（`claude-3-haiku-20240307`）のAPIサービスを終了します。  
廃止まで残り約3週間。この日を過ぎると、同モデルへのAPIリクエストはすべてエラーになります。

この記事では、公式ドキュメントをもとに以下を解説します:

* Haiku 3廃止の背景と影響範囲
* **移行先: Claude Haiku 4.5** の新機能と性能向上
* 破壊的変更の一覧と対応方法
* Pythonコードの移行サンプル
* 料金・レートリミットの変化

### この記事の対象読者

* Anthropic APIで `claude-3-haiku-20240307` を使用しているエンジニア
* Claude Haiku 4.5への移行を検討しているチーム
* Anthropicモデルの移行ポリシーを把握したい方

---

## TL;DR

* `claude-3-haiku-20240307` は **2026-04-19 に廃止**（以降リクエストが失敗）
* 移行先は `claude-haiku-4-5-20251001`
* **破壊的変更**: `temperature` と `top_p` の同時指定が不可、ツールタイプ識別子の変更など
* Haiku 4.5 はSWE-bench 73.3%・Computer Use 50.7%と大幅に性能向上
* 価格は $1/$5 per 1M tokens（Haiku 3.5比 +25%、ただし性能は大幅改善）

---

## Claude Haiku 3 廃止の背景

Anthropicは2026年2月19日、`claude-3-haiku-20240307` の廃止を正式アナウンスしました。  
廃止日: **2026年4月19日〜20日**（公式ページにより表記が1日ずれる場合があります。最新情報は[公式ドキュメント](https://platform.claude.com/docs/en/about-claude/model-deprecations)を参照してください）。

[Anthropicのモデル廃止ポリシー](https://platform.claude.com/docs/en/about-claude/model-deprecations)では、公開モデルについては**廃止の少なくとも60日前**に通知を行うと定められており、今回の通知はこのポリシーに準拠しています。

### 廃止後に何が起きるか

廃止日以降、`claude-3-haiku-20240307` を指定したAPIリクエストは**エラーレスポンスを返します**。  
既存の本番環境への影響を避けるため、早急な移行対応が必要です。

> 廃止モデルを使っているかどうかは、Anthropic Consoleの**APIアクセス監査機能**で確認できます。

---

## 移行先: Claude Haiku 4.5

Anthropicが推奨する移行先は [Claude Haiku 4.5](https://www.anthropic.com/news/claude-haiku-4-5)（`claude-haiku-4-5-20251001`）です。

### 主要スペック

| 項目 | Claude Haiku 3 | Claude Haiku 4.5 |
| --- | --- | --- |
| モデルID | `claude-3-haiku-20240307` | `claude-haiku-4-5-20251001` |
| コンテキスト窓 | 200K tokens | 200K tokens |
| 最大出力トークン | 4K tokens | **64K tokens** |
| SWE-bench Verified | — | **73.3%** |
| Computer Use (OSWorld) | — | **50.7%** |
| Extended Thinking | 非対応 | **対応** |
| Computer Use | 非対応 | **対応** |
| Context Awareness | 非対応 | **対応** |
| 入力料金 | $0.25/1M | **$1.00/1M** |
| 出力料金 | $1.25/1M | **$5.00/1M** |

価格は約4倍ですが、性能・機能は大幅に向上しています。

### 性能ハイライト

**コーディング性能**: SWE-bench Verified で **73.3%** を達成。Claude Sonnet 4.5（77.2%）とわずか5ポイント差の性能を3分の1のコストで実現します[1](#fn-1)。

**Computer Use**: OSWorldベンチマークで **50.7%** を達成。Sonnet 4（42.2%）を上回る性能をより低コストで提供します[1](#fn-1)。

**Extended Thinking**: HaikuモデルとしてはじめてExtended Thinkingに対応。複雑なコーディング・推論タスクでの精度が向上します。

**Context Awareness**: モデルが自身のコンテキスト消費量をリアルタイムで把握し、長い会話セッションで自動的に優先度の低い情報を圧縮するなど、タスク継続性が向上します。

---

## 破壊的変更（Breaking Changes）

Claude Haiku 3系から移行する際は、以下の破壊的変更に対応する必要があります。

### 1. モデルID変更（必須）

```
# 変更前
model = "claude-3-haiku-20240307"

# 変更後
model = "claude-haiku-4-5-20251001"
```

### 2. `temperature` と `top_p` の同時指定が不可（必須）

Haiku 4.5 では、`temperature` と `top_p` を同時に指定することが**エラー**になります。

```
# 変更前（Haiku 3では許容されていた）
response = client.messages.create(
    model="claude-3-haiku-20240307",
    temperature=0.7,
    top_p=0.9,  # 同時指定していた場合
    ...
)

# 変更後: どちらか一方のみ指定する
response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    temperature=0.7,  # temperature のみ指定
    ...
)
```

どちらを選ぶかは用途次第ですが、多くの場合 `temperature` のみで問題ありません。

### 3. 新しい refusal stop reason への対応（必須）

Claude 4.5 では、`stop_reason` に `"refusal"` が追加されています。  
この値を処理しないと、予期しない動作になる可能性があります。

```
response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    ...
)

# 変更前（"end_turn" と "max_tokens" のみ処理していた場合）
if response.stop_reason == "end_turn":
    pass
elif response.stop_reason == "max_tokens":
    pass

# 変更後: "refusal" を追加
if response.stop_reason == "end_turn":
    pass
elif response.stop_reason == "max_tokens":
    pass
elif response.stop_reason == "refusal":
    # モデルが応答を拒否した場合の処理
    print("モデルが応答を拒否しました")
```

### 4. ツールタイプ識別子の変更（ツール使用時）

`text_editor` ツールなどのタイプ識別子が更新されています。  
ツールを使用している場合は、[公式マイグレーションガイド](https://platform.claude.com/docs/en/about-claude/models/migrating-to-claude-4)で最新のツールタイプ識別子を確認してください。

### 5. Extended output beta ヘッダーの廃止

過去に使用していた `output-128k-2025-02-19` ベータヘッダーは Claude 4.5 では**非サポート**です。  
Haiku 4.5 では標準で64Kトークンの出力が可能なため、このヘッダーは不要です。

```
# 変更前（ベータヘッダーを使用していた場合）
response = client.messages.create(
    model="claude-3-haiku-20240307",
    extra_headers={"output-128k-2025-02-19": "true"},  # 削除する
    ...
)

# 変更後: ヘッダー不要
response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=64000,  # 標準で最大64K
    ...
)
```

---

## 移行の全体手順

### Step 1: 現在の使用状況を確認する

Anthropic Console の **APIアクセス監査機能** を使用し、`claude-3-haiku-20240307` を使用しているシステムをすべて特定します。

```
# Bashでもモデル使用状況を検索できます
grep -r "claude-3-haiku-20240307" ./src --include="*.py"
```

### Step 2: 開発環境で移行テストを実施

```
import anthropic

client = anthropic.Anthropic()

# 移行後の基本的なリクエスト
response = client.messages.create(
    model="claude-haiku-4-5-20251001",  # モデルID変更
    max_tokens=1024,
    temperature=0.7,  # top_p との同時指定は不可
    messages=[
        {"role": "user", "content": "こんにちは。簡単に自己紹介してください。"}
    ]
)

# stop_reason の "refusal" を追加処理
print(f"stop_reason: {response.stop_reason}")
print(response.content[0].text)
```

### Step 3: Extended Thinking の活用（オプション）

複雑な処理には Extended Thinking を有効化することを推奨します。

```
response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000  # 思考に使うトークン予算
    },
    messages=[
        {"role": "user", "content": "この関数のバグを特定して修正してください: ..."}
    ]
)

# thinking ブロックと text ブロックが返ってくる
for block in response.content:
    if block.type == "thinking":
        print("思考:", block.thinking)
    elif block.type == "text":
        print("回答:", block.text)
```

> **注意**: Extended Thinking はプロンプトキャッシュの効率に影響します。キャッシュを多用している場合は[Extended Thinkingのドキュメント](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)を確認してください。

### Step 4: 本番環境に反映

テストが完了したら、本番環境のモデルIDを更新します。  
Claude Haiku 4.5 は Amazon Bedrock・Google Cloud Vertex AI でも同様に利用可能です。

---

## レートリミットの変化

Claude Haiku 4.5 は Haiku 3 と**別のレートリミット**が設定されています。  
現在のTierにおけるレートリミットは[Anthropicの公式ドキュメント](https://platform.claude.com/docs/en/about-claude/models/overview)を参照してください。

高負荷なシステムでは、移行時に一時的にレートリミットに達する可能性があります。  
リクエスト量が多い場合は、Anthropicサポートへ事前に相談することを推奨します。

---

## コスト試算

価格は上昇しますが、Extended Thinkingやキャッシュを活用することでコストを最適化できます。

| 施策 | 削減率 |
| --- | --- |
| プロンプトキャッシュ | 最大90% |
| バッチ処理（Message Batches API） | 50% |
| Extended Thinkingで再試行を削減 | ユースケースによる |

バッチ処理を活用すれば、Haiku 4.5 の実質コストは **$0.50/$2.50 per 1M tokens** まで削減可能です[1](#fn-1)。

---

## まとめ

* **Claude Haiku 3 廃止日は 2026年4月19〜20日** — この日以降リクエストが失敗する
* 移行先は `claude-haiku-4-5-20251001` で、SWE-bench 73.3%・Computer Use 50.7%と大幅な性能向上
* **破壊的変更の主要な対応点**: モデルID更新・`temperature`/`top_p`の同時指定を解消・新しい`stop_reason`の処理追加
* Extended Thinking・Context Awarenessなど、新機能の活用でエージェント系ユースケースも強化

廃止まで残りわずかです。公式の[Migration Guide](https://platform.claude.com/docs/en/about-claude/models/migrating-to-claude-4)と[Model Deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations)ページも併せて確認し、早めに対応を進めましょう。

---

## 参考リンク
