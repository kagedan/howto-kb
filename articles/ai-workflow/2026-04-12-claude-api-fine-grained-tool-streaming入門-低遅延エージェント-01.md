---
id: "2026-04-12-claude-api-fine-grained-tool-streaming入門-低遅延エージェント-01"
title: "Claude API Fine-Grained Tool Streaming入門 — 低遅延エージェントをPythonで実装する"
url: "https://qiita.com/kai_kou/items/8e1d151031acc1851445"
source: "qiita"
category: "ai-workflow"
tags: ["API", "Python", "qiita"]
date_published: "2026-04-12"
date_collected: "2026-04-13"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude API でツールを使ったエージェントを構築すると、ツール呼び出しの**パラメータが大きいほど応答開始までの時間が長くなる**という問題に直面します。

これは従来、Claude がパラメータを完全に生成してからクライアントへ送信する「バッファリング」が行われていたためです。ファイル書き込みツールに渡す長いテキストや、検索クエリが完成するまで待機が発生していました。

**Fine-Grained Tool Streaming** は、このバッファリングを取り除き、ツールパラメータを**生成しながら即座にストリーミング**する機能です。2026年2月5日に全モデル・全プラットフォームで正式リリース（GA）となり、ベータヘッダーなしで利用できます。

### この記事で学べること

* Fine-Grained Tool Streaming の仕組みと有効化方法
* `eager_input_streaming` パラメータの使い方
* `input_json_delta` イベントを使った Python/TypeScript 実装
* 不完全な JSON や `max_tokens` 到達時の例外処理
* 活用が有効なユースケースと注意点

### 対象読者

* Claude API でツール使用エージェントを構築しているエンジニア
* ストリーミングレイテンシを改善したい方
* Python または TypeScript で Claude を使っている方

### 前提環境

* Python 3.10 以上（または Node.js 20 以上）
* `anthropic` SDK（最新版推奨）
* Claude API キー（`ANTHROPIC_API_KEY`）

---

## TL;DR

* `eager_input_streaming: true` をツール定義に追加するだけで有効化
* ベータヘッダー不要（2026年2月5日 GA）
* 公式ドキュメントの例: **15秒 → 3秒**のレイテンシ削減
* 全プラットフォーム対応（Claude API / Amazon Bedrock / Google Vertex AI / Microsoft Foundry）
* パラメータが不完全な JSON になる可能性があるため、エラーハンドリングが必要

---

## Fine-Grained Tool Streamingとは

### 従来の動作（バッファリングあり）

通常のストリーミングでは、Claude が `tool_use` ブロックのパラメータを生成する際、**完全な JSON として有効になるまでバッファリング**してからクライアントへ送信します。

```
[15秒の待機]
Chunk 1: '{"'
Chunk 2: 'query": "Ty'
Chunk 3: 'peScri'
Chunk 4: 'pt 5.0 5.1 5.2 5.3'
Chunk 5: ' new f'
Chunk 6: 'eatur'
...
```

長い文字列配列や大きなオブジェクトをパラメータとして渡す場合、クライアントは**パラメータ全体が完成するまでデータを受け取れません**。

### Fine-Grained Streamingの動作（バッファリングなし）

Fine-Grained Tool Streaming を有効にすると、**JSON バリデーションなしで生成と同時にパラメータを送信**します。

```
[3秒で最初のチャンク]
Chunk 1: '{"query": "TypeScript 5.0 5.1 5.2 5.3'
Chunk 2: ' new features comparison'
```

* バッファリング解消により**最初のデータ到着が大幅に高速化**（公式例: 15秒→3秒、約5倍の削減）
* チャンクが長くなり、単語途中の分割（word breaks）が減少
* ツール処理の**パイプライン化**（データが届き次第次の処理を開始可能）

---

## 有効化方法

### ツール定義に `eager_input_streaming` を追加

Fine-Grained Tool Streaming は、**ツール定義ごと**に有効化します。有効にしたいツールの定義に `eager_input_streaming: true` を追加し、リクエストでストリーミングを有効にするだけです。

```
import anthropic

client = anthropic.Anthropic()

with client.messages.stream(
    model="claude-opus-4-6",
    max_tokens=65536,
    tools=[
        {
            "name": "make_file",
            "description": "テキストをファイルに書き込む",
            "eager_input_streaming": True,  # ← これだけ追加
            "input_schema": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "書き込み先ファイル名"
                    },
                    "lines_of_text": {
                        "type": "array",
                        "description": "書き込むテキスト行の配列"
                    }
                },
                "required": ["filename", "lines_of_text"]
            },
        }
    ],
    messages=[
        {
            "role": "user",
            "content": "長い詩を書いて poem.txt というファイルに保存してください"
        }
    ],
) as stream:
    for event in stream:
        pass
    final_message = stream.get_final_message()

print(final_message.usage)
```

> `eager_input_streaming` は**ユーザー定義ツール**にのみ設定できます。Anthropic が提供するビルトインツール（web\_search、code\_execution など）には設定不要で、これらはデフォルトで最適化されています。

### 対応プラットフォーム

| プラットフォーム | 対応状況 |
| --- | --- |
| Claude API（direct） | GA |
| Amazon Bedrock | GA |
| Google Cloud Vertex AI | GA |
| Microsoft Foundry | GA |

どのプラットフォームでも**ベータヘッダー不要**で利用できます。

---

## ストリーミングイベントの処理

Fine-Grained Tool Streaming を使う場合、ツールパラメータは以下のイベントシーケンスで届きます。

### イベントシーケンス

1. **`content_block_start`** (`type: "tool_use"`)

   * `input: {}` という空オブジェクトが含まれる（プレースホルダー）
   * これは実際の値ではない
2. **`content_block_delta`** (`type: "input_json_delta"`) × 複数

   * `delta.partial_json` に部分的な JSON 文字列が含まれる
   * これらを**文字列として連結**する
3. **`content_block_stop`**

   * 連結した文字列を `json.loads()` でパース

> `content_block_start` の `input: {}` は**プレースホルダー**であり、実際のパラメータではありません。本当の値は `input_json_delta` イベントで届きます。

### Python実装: イベント手動処理

```
import json
import anthropic

client = anthropic.Anthropic()

tool_inputs: dict[int, str] = {}  # index -> 蓄積中の JSON 文字列

with client.messages.stream(
    model="claude-opus-4-6",
    max_tokens=1024,
    tools=[
        {
            "name": "get_weather",
            "description": "都市の現在の天気を取得する",
            "eager_input_streaming": True,
            "input_schema": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "都市名"}
                },
                "required": ["city"],
            },
        }
    ],
    messages=[{"role": "user", "content": "パリの天気を教えてください"}],
) as stream:
    for event in stream:
        if (
            event.type == "content_block_start"
            and event.content_block.type == "tool_use"
        ):
            # tool_use ブロック開始: 蓄積バッファを初期化
            tool_inputs[event.index] = ""

        elif (
            event.type == "content_block_delta"
            and event.delta.type == "input_json_delta"
        ):
            # パラメータのフラグメントを蓄積
            tool_inputs[event.index] += event.delta.partial_json
            # ここでリアルタイム処理も可能（例: プログレスインジケーター更新）

        elif event.type == "content_block_stop" and event.index in tool_inputs:
            # ブロック完了: JSON をパース
            try:
                parsed = json.loads(tool_inputs[event.index])
                print(f"ツール入力: {parsed}")
            except json.JSONDecodeError as e:
                print(f"JSON パース失敗: {e}")
                # 不完全な JSON の場合（max_tokens 到達など）の処理
                print(f"生データ: {tool_inputs[event.index]}")
```

### TypeScript実装

```
import Anthropic from "@anthropic-ai/sdk";

const anthropic = new Anthropic();

const toolInputs: Record<number, string> = {};

const stream = anthropic.messages.stream({
  model: "claude-opus-4-6",
  max_tokens: 1024,
  tools: [
    {
      name: "get_weather",
      description: "都市の現在の天気を取得する",
      eager_input_streaming: true,
      input_schema: {
        type: "object",
        properties: {
          city: { type: "string", description: "都市名" }
        },
        required: ["city"]
      }
    }
  ],
  messages: [{ role: "user", content: "パリの天気を教えてください" }]
});

for await (const event of stream) {
  if (event.type === "content_block_start" && event.content_block.type === "tool_use") {
    toolInputs[event.index] = "";
  } else if (event.type === "content_block_delta" && event.delta.type === "input_json_delta") {
    toolInputs[event.index] += event.delta.partial_json;
  } else if (event.type === "content_block_stop" && event.index in toolInputs) {
    try {
      const parsed = JSON.parse(toolInputs[event.index]);
      console.log("ツール入力:", parsed);
    } catch (e) {
      console.error("JSON パース失敗:", e);
    }
  }
}
```

### SDK ヘルパーを使う場合

手動でイベントを処理する必要がない場合、SDK のヘルパーメソッドを使うと簡潔に書けます。

```
# Python SDK: get_final_message() が蓄積を自動処理
with client.messages.stream(
    model="claude-opus-4-6",
    max_tokens=1024,
    tools=[...],  # eager_input_streaming: True を含む
    messages=[...],
) as stream:
    # イベント処理なしでも get_final_message() で完成した入力を取得可能
    final = stream.get_final_message()

for block in final.content:
    if block.type == "tool_use":
        print(f"ツール: {block.name}")
        print(f"入力: {block.input}")
```

> **手動イベント処理 vs SDK ヘルパー**の使い分け：
>
> * **手動処理**: パラメータ到着中にリアルタイムでUIを更新したい場合や、部分データで下流処理を先行させたい場合
> * **SDK ヘルパー**: ツールを実行できれば良く、中間状態は不要な場合（推奨）

---

## 注意点と例外処理

### 不完全なJSONへの対処

Fine-Grained Tool Streaming では**バリデーションなしでパラメータを送信**するため、何らかの理由でストリームが途中で終わると不完全な JSON が届く場合があります。

特に **`stop_reason: "max_tokens"`** に達した場合、パラメータが途中で切れる可能性があります。

```
import json
import anthropic

def process_tool_input(raw_json: str, stop_reason: str) -> dict | None:
    """ツール入力を安全にパースする"""
    try:
        return json.loads(raw_json)
    except json.JSONDecodeError:
        if stop_reason == "max_tokens":
            # max_tokens 到達による不完全な JSON
            print("警告: max_tokens に達したためパラメータが不完全です")
            # エラーレスポンスとしてモデルに返す場合
            return {"INVALID_JSON": raw_json}
        else:
            # その他の予期しない不完全 JSON
            raise

# 使用例
with client.messages.stream(
    model="claude-opus-4-6",
    max_tokens=512,  # 意図的に小さい値でテスト
    tools=[{
        "name": "write_content",
        "description": "長いコンテンツを書き込む",
        "eager_input_streaming": True,
        "input_schema": {
            "type": "object",
            "properties": {
                "content": {"type": "string"}
            },
            "required": ["content"]
        }
    }],
    messages=[{"role": "user", "content": "非常に長い記事を書いてください"}],
) as stream:
    tool_inputs = {}
    final_message = None

    for event in stream:
        if event.type == "content_block_start" and event.content_block.type == "tool_use":
            tool_inputs[event.index] = ""
        elif event.type == "content_block_delta" and event.delta.type == "input_json_delta":
            tool_inputs[event.index] += event.delta.partial_json
        elif event.type == "message_stop":
            pass

    final_message = stream.get_final_message()
    stop_reason = final_message.stop_reason

    for i, raw_json in tool_inputs.items():
        result = process_tool_input(raw_json, stop_reason)
        if result:
            print(f"パース結果 [index={i}]: {result}")
```

### 不完全なJSONをモデルに返す場合

モデルにエラーを通知しつつ次のターンへ進める場合は、不完全な JSON を `INVALID_JSON` キーでラップして返します。

```
# tool_result として返すフォーマット
error_response = {
    "type": "tool_result",
    "tool_use_id": tool_use_id,
    "content": json.dumps({"INVALID_JSON": raw_json}),  # ラップして返す
    "is_error": True
}
```

> `INVALID_JSON` でラップする際、`raw_json` 内のエスケープ文字を適切に処理してください。`json.dumps()` を使うことで自動的にエスケープされます。

---

## 活用ユースケース

### 特に効果的なケース

| ユースケース | 効果 | 例 |
| --- | --- | --- |
| ファイル書き込みツール | 長いコンテンツをリアルタイム表示 | コード生成→即時編集 |
| 長い文字列配列パラメータ | バッファリング解消 | レポート章立て生成 |
| 検索クエリ生成 | クエリ確定前に処理開始 | 並列検索パイプライン |
| ストリーミングUI | プログレス表示 | チャットボットのタイピング表示 |

### 向いていないケース

* パラメータが短い場合（数十文字以下）→ バッファリングとの差が小さい
* JSON バリデーションが必須な場合 → SDK ヘルパーで最終結果のみ使用する方が安全
* パラメータが完全に揃ってから処理を開始したい場合 → SDK ヘルパー（`get_final_message()`）を推奨

---

## cURLでの確認

ツール定義の動作確認や検証には cURL も使用できます。

```
curl https://api.anthropic.com/v1/messages \
  -H "content-type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-opus-4-6",
    "max_tokens": 65536,
    "tools": [
      {
        "name": "make_file",
        "description": "テキストをファイルに書き込む",
        "eager_input_streaming": true,
        "input_schema": {
          "type": "object",
          "properties": {
            "filename": {"type": "string"},
            "lines_of_text": {"type": "array"}
          },
          "required": ["filename", "lines_of_text"]
        }
      }
    ],
    "messages": [
      {"role": "user", "content": "長い詩を書いて poem.txt に保存してください"}
    ],
    "stream": true
  }'
```

`stream: true` を指定することでサーバー送信イベント（SSE）形式でレスポンスが届き、`input_json_delta` イベントが確認できます。

---

## まとめ

Fine-Grained Tool Streaming は、Claude API でツールを使ったエージェントを構築する際の**レイテンシ改善**において最もシンプルで効果的な手段の1つです。

* **`eager_input_streaming: true`** をツール定義に追加するだけで有効化
* ベータヘッダー不要でGAに移行済み（全プラットフォーム対応）
* 大きなパラメータを持つツールで顕著な効果（公式例: 15秒 → 3秒）
* `input_json_delta` イベントを蓄積してパース、または SDK ヘルパーで簡略化

エージェントの応答速度がユーザー体験に直結する場合、まず `eager_input_streaming` を試すことを推奨します。

---

## 参考リンク
