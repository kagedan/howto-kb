---
id: "2026-04-19-claude-apiのfine-grained-tool-streamingで低遅延エージェントをp-01"
title: "Claude APIのFine-Grained Tool Streamingで低遅延エージェントをPythonで実装する"
url: "https://zenn.dev/bluecat/articles/34684b37d96212"
source: "zenn"
category: "ai-workflow"
tags: ["API", "Python", "zenn"]
date_published: "2026-04-19"
date_collected: "2026-04-20"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude APIのツール使用（tool\_use）はAIエージェント開発の中核機能ですが、従来の実装ではツールの引数（input）が**すべて生成されてから**クライアントに届いていました。検索クエリの生成やコード生成ツールでは、長い引数が完全に揃うまで何秒も待つ必要があり、ユーザー体験を損なう原因になっていました。

2026年2月5日にGA（一般利用可能）となった**Fine-Grained Tool Streaming**を使うと、ツールの引数をリアルタイムでストリーミング受信できます。ベータヘッダー不要、全モデル・全プラットフォームで利用可能です。

本記事では、Fine-Grained Tool Streamingの仕組みから実装パターン、マルチツールエージェントへの応用まで、動作するコードで解説します。

---

従来のtool\_use（非ストリーミング）とFine-Grained Tool Streamingの違いを整理します。

| 項目 | 従来（バッファリング） | Fine-Grained Streaming |
| --- | --- | --- |
| 引数の届き方 | 完成後にまとめて | 生成と同時にデルタで |
| 遅延 | 引数長に比例して増大 | 最初の文字が即座に届く |
| ベータヘッダー | 不要 | 不要（2026/2/5 GA） |
| 有効化方法 | — | ツール定義に `eager_input_streaming: True` を追加 |
| デルタ形式 | — | 部分的なJSON文字列 |

**ユースケース**：

* 検索クエリをリアルタイム表示（「どんなキーワードで検索するか」がすぐわかる）
* コード生成ツールで途中経過を表示
* 長い引数を持つツール（ドキュメント生成など）の進捗表示

---

## 基本実装：ストリーミングでツール引数を受け取る

### セットアップ

```
pip install anthropic
export ANTHROPIC_API_KEY="your-api-key"
```

### シンプルなストリーミング受信

```
import anthropic
import json

client = anthropic.Anthropic()

# Fine-Grained Streamingを有効にしたツール定義
tools = [
    {
        "name": "web_search",
        "description": "指定したクエリでWeb検索を実行し、関連する情報を取得する",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "検索クエリ（詳細なほど精度が高い）"
                },
                "max_results": {
                    "type": "integer",
                    "description": "取得する最大件数（デフォルト5）",
                    "default": 5
                }
            },
            "required": ["query"]
        },
        # ★ Fine-Grained Streamingを有効化するキー
        "eager_input_streaming": True
    }
]

def stream_with_fine_grained_tools(user_message: str):
    """Fine-Grained Tool Streamingを使ってメッセージを送信し、
    ツール引数をリアルタイムで表示する"""

    input_buffer = {}  # ツールIDごとに引数の断片を蓄積

    with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        tools=tools,
        messages=[{"role": "user", "content": user_message}]
    ) as stream:
        for event in stream:
            event_type = event.type

            # テキストのストリーミング
            if event_type == "content_block_delta":
                delta = event.delta
                if delta.type == "text_delta":
                    print(delta.text, end="", flush=True)

                # ★ ツール引数のデルタ（Fine-Grained Streamingの核心）
                elif delta.type == "input_json_delta":
                    tool_use_id = event.index
                    if tool_use_id not in input_buffer:
                        input_buffer[tool_use_id] = ""
                    input_buffer[tool_use_id] += delta.partial_json
                    # デルタをリアルタイム表示
                    print(f"\r[tool_input]: {input_buffer[tool_use_id]}", end="", flush=True)

            # ツールブロックの開始
            elif event_type == "content_block_start":
                if hasattr(event.content_block, "type") and event.content_block.type == "tool_use":
                    print(f"\n\n🔧 ツール呼び出し開始: {event.content_block.name}")
                    print("引数をストリーミング受信中: ", end="")

            # ツールブロックの完了
            elif event_type == "content_block_stop":
                idx = event.index
                if idx in input_buffer:
                    final_input = json.loads(input_buffer[idx])
                    print(f"\n✅ 引数確定: {json.dumps(final_input, ensure_ascii=False, indent=2)}")

    return stream.get_final_message()

# 実行例
if __name__ == "__main__":
    message = stream_with_fine_grained_tools(
        "2026年の日本のAI政策について、最新の政府発表を調べてください"
    )
    print(f"\n\n停止理由: {message.stop_reason}")
```

実行すると、`query` フィールドの値が文字ごとに届く様子が確認できます。

---

## 実践パターン：ツール実行を含む完全なエージェントループ

実際のエージェントはツール引数を受け取った後、ツールを実行して結果をモデルに返す必要があります。Fine-Grained Streamingと組み合わせた完全な実装例を示します。

```
import anthropic
import json
from typing import Any

client = anthropic.Anthropic()

# ダミーのツール実装（実際はAPIや処理を実装する）
def execute_tool(tool_name: str, tool_input: dict) -> Any:
    """ツールを実行してモック結果を返す"""
    if tool_name == "web_search":
        query = tool_input.get("query", "")
        return {
            "results": [
                {"title": f"[検索結果1] {query} に関する記事", "url": "https://example.com/1"},
                {"title": f"[検索結果2] {query} 最新情報", "url": "https://example.com/2"},
            ],
            "total": 2
        }
    elif tool_name == "calculate":
        expr = tool_input.get("expression", "0")
        try:
            result = eval(expr, {"__builtins__": {}})
            return {"result": result, "expression": expr}
        except Exception as e:
            return {"error": str(e)}
    return {"error": "Unknown tool"}

tools = [
    {
        "name": "web_search",
        "description": "Web検索を実行する",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "検索クエリ"}
            },
            "required": ["query"]
        },
        "eager_input_streaming": True
    },
    {
        "name": "calculate",
        "description": "数式を計算する",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "計算式（例: '3.14 * 10 ** 2'）"}
            },
            "required": ["expression"]
        },
        "eager_input_streaming": True  # 計算式もリアルタイムで確認できる
    }
]

def run_agent_loop(user_message: str, max_turns: int = 5):
    """Fine-Grained Tool Streamingを使った完全なエージェントループ"""

    messages = [{"role": "user", "content": user_message}]
    turn = 0

    while turn < max_turns:
        turn += 1
        print(f"\n--- ターン {turn} ---")

        tool_calls = []
        input_buffers = {}

        with client.messages.stream(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            tools=tools,
            messages=messages
        ) as stream:
            for event in stream:
                if event.type == "content_block_start":
                    cb = event.content_block
                    if cb.type == "tool_use":
                        print(f"\n🔧 {cb.name}（ID: {cb.id}）")
                        print("  引数: ", end="", flush=True)
                        tool_calls.append({
                            "type": "tool_use",
                            "id": cb.id,
                            "name": cb.name,
                            "input": {}
                        })
                        input_buffers[cb.id] = {"index": event.index, "raw": ""}

                elif event.type == "content_block_delta":
                    delta = event.delta
                    if delta.type == "text_delta":
                        print(delta.text, end="", flush=True)
                    elif delta.type == "input_json_delta":
                        # どのツール呼び出しに対応するデルタか特定する
                        for tc in reversed(tool_calls):
                            if tc["id"] in input_buffers:
                                buf_info = input_buffers[tc["id"]]
                                if buf_info["index"] == event.index:
                                    buf_info["raw"] += delta.partial_json
                                    print(delta.partial_json, end="", flush=True)
                                    break

                elif event.type == "content_block_stop":
                    # 引数を確定
                    for tc in tool_calls:
                        if tc["id"] in input_buffers:
                            buf = input_buffers[tc["id"]]
                            if buf["raw"]:
                                tc["input"] = json.loads(buf["raw"])
                                print(f"  → 確定: {tc['input']}")

            final_message = stream.get_final_message()

        # アシスタントメッセージを追加
        messages.append({"role": "assistant", "content": final_message.content})

        # ツール呼び出しがなければ終了
        if final_message.stop_reason != "tool_use":
            print("\n✅ エージェント完了")
            break

        # ツールを実行して結果を追加
        tool_results = []
        for tc in tool_calls:
            result = execute_tool(tc["name"], tc["input"])
            print(f"\n📊 {tc['name']} 結果: {json.dumps(result, ensure_ascii=False)}")
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tc["id"],
                "content": json.dumps(result, ensure_ascii=False)
            })

        messages.append({"role": "user", "content": tool_results})

    return messages

# 実行例
if __name__ == "__main__":
    result = run_agent_loop("円の面積の公式で、半径が15cmの場合の面積を計算してください")
```

---

## 遅延計測：Fine-Grained Streamingの効果を数値で確認する

Fine-Grained Tool Streamingの恩恵を実感するため、最初のトークンが届くまでの時間（TTFT: Time To First Token）を計測してみましょう。

```
import anthropic
import time

client = anthropic.Anthropic()

def measure_ttft(use_streaming: bool, query_complexity: str = "medium") -> float:
    """ツール引数の最初のデルタが届くまでの時間を計測する"""

    tool_def = {
        "name": "analyze_data",
        "description": "データを分析してインサイトを返す",
        "input_schema": {
            "type": "object",
            "properties": {
                "analysis_prompt": {
                    "type": "string",
                    "description": "分析の詳細な指示（500〜1000文字程度）"
                }
            },
            "required": ["analysis_prompt"]
        }
    }

    if use_streaming:
        tool_def["eager_input_streaming"] = True

    start_time = time.time()
    first_delta_time = None

    with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        tools=[tool_def],
        messages=[{
            "role": "user",
            "content": "日本のAI産業の現状と課題について詳細に分析してください"
        }]
    ) as stream:
        for event in stream:
            if (event.type == "content_block_delta"
                    and event.delta.type == "input_json_delta"
                    and first_delta_time is None):
                first_delta_time = time.time()
                break  # 最初のデルタを確認したら停止

    if first_delta_time:
        ttft = first_delta_time - start_time
        label = "Fine-Grained Streaming" if use_streaming else "通常ストリーミング"
        print(f"{label}: TTFT = {ttft:.3f}秒")
        return ttft
    return -1.0

# 比較計測
print("=== TTFT比較計測 ===")
ttft_normal = measure_ttft(use_streaming=False)
time.sleep(2)  # レートリミット回避
ttft_fgs = measure_ttft(use_streaming=True)

if ttft_normal > 0 and ttft_fgs > 0:
    improvement = (ttft_normal - ttft_fgs) / ttft_normal * 100
    print(f"\n改善率: {improvement:.1f}%")
```

実際の計測では、引数が長いツール（500文字以上のJSON）ほどFine-Grained Streamingの優位性が顕著に現れます。

---

## まとめ

Fine-Grained Tool Streamingを使うことで、ツール引数が生成されるそばからデルタを受け取れるため、以上のメリットが得られます。

* **応答性の向上**：引数全体が完成するのを待たずに処理を開始できる
* **UX改善**：「今何を考えているか」をリアルタイムで表示できる
* **デバッグのしやすさ**：ストリームを見ながら引数の生成過程を確認できる

有効化は `eager_input_streaming: True` を追加するだけ。既存のコードへの組み込みコスドは最小限です。2026年2月5日のGA以降、ベータヘッダーも不要になりました。

実装時のポイントをまとめると：

1. ツール定義に `eager_input_streaming: True` を追加する
2. `content_block_delta` イベントで `delta.type == "input_json_delta"` を処理する
3. `delta.partial_json` を蓄積して `content_block_stop` 後に `json.loads()` で解析する
4. 複数ツールがある場合は `event.index` でどのツールのデルタかを判別する

---

## 関連書籍（有料・1,000円）

本記事のテーマをより体系的に学びたい方へ、実践ガイドを公開しています。

第1・2章は無料で読めます。
