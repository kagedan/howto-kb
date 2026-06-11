---
id: "2026-06-10-llmエージェントをlangchainなしで実装するopenai-tools-apiと手動ループの基-01"
title: "LLMエージェントをLangChainなしで実装する：OpenAI tools APIと手動ループの基本"
url: "https://zenn.dev/libercraft/articles/20260610-agent-sdk-no-framework"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "LLM", "OpenAI", "GPT", "Python"]
date_published: "2026-06-10"
date_collected: "2026-06-11"
summary_by: "auto-rss"
query: ""
---

**LLMエージェントをフレームワークなしで実装するとは、OpenAI tools APIとPythonのwhile-loopを直接使い、「LLMがツールを選び・コードが実行し・結果をLLMに返す」ループを手書きで動かすことです。**

LangChainのようなフレームワークは便利ですが、内部で何が起きているかを知らないまま使うと、動いている理由もわからなければ壊れた理由もわかりません。フレームワークが抽象化している層の正体を理解することが、設計力とトラブル対応力を上げる最短ルートです。

「LangChainを外したら、何もできなくなった」

これは、AIエージェントをある程度触った人が必ず通る壁です。LangChainのチェーンを組んで、エージェントを動かして、デモは動かせている。でも「内部で何が起きているか」は言語化できない。少し変わった要件が来ると、どこをいじればいいかわからなくて手が止まる。

この状態は、フレームワークを「外から使っているだけ」の状態です。中身を知らずに使っているので、動いている理由もわからなければ、壊れた理由もわからない。

この記事の目的は、その状態から抜け出すことです。

OpenAI tools APIを直接使い、while-loopを手で書き、エージェントが「なぜそう動くか」を構造ごと理解します。LangChainやLangGraphが抽象化している層の正体は何か。それを把握した上でフレームワークを使えるようになることが目標です。フレームワークを捨てることが目標ではありません。

---

エージェントの動作原理を一言で表すと、**「LLMがツールを選び、コードが実行し、結果をLLMに返す」の繰り返し**です。

LLMは本来、テキストを生成する機能しか持ちません。しかし tools API を使うと、LLMは「このツールをこの引数で呼んでほしい」という指示をテキストとして返せます。実際にツールを実行するのはPythonコードです。LLMは「何を」「どんな引数で」呼ぶかを決めるだけで、実行は委ねます。

この往復が繰り返されるのがエージェントループの正体です。

LLMが `tool_calls` を返す限りループは続きます。`tool_calls` が `None`（または空）になったとき、LLMが「もうツールは不要」と判断したということです。これがループの終了条件です。

`tool_choice` はLLMのツール利用方針を制御するパラメータです。

| 値 | 意味 |
| --- | --- |
| `"auto"` | LLMが判断。ツールを使うかどうかを自動で決める（デフォルト） |
| `"required"` | 必ずツールを1つ以上呼ばせる |
| `"none"` | ツールを使わず、テキスト応答のみ返す |
| `{"type": "function", "function": {"name": "xxx"}}` | 特定のツールを強制的に呼ばせる |

通常のエージェントループでは `"auto"` を使います。LLMが自律的に判断し、必要なくなった時点で `tool_calls` が `None` になり、それがループの終了トリガーになります。

`"required"` は「最初の1ステップで必ずツールを使わせたい」場面で有効です。ルーティングや初期分類をツールに委ねるパターンで使います。

LLMがツール呼び出しを要求したとき、レスポンスの `message.tool_calls` に以下の構造が入ります。

```
# OpenAI APIからのレスポンス（tool_callsがある場合）
response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
    tool_choice="auto",
)

message = response.choices[0].message

# message.tool_calls の構造
# [
#   ChatCompletionMessageToolCall(
#     id='call_abc123',
#     type='function',
#     function=Function(
#       name='search_web',
#       arguments='{"query": "Python 3.13 新機能"}'
#     )
#   )
# ]
```

`arguments` はJSON文字列として返ってきます。`json.loads()` でdictに変換してからツール関数に渡します。この点はよく見落とされます。`arguments` はdictではなく文字列です。

---

## ツールをどう定義するか：PydanticからOpenAI形式への変換

tools APIに渡すツール定義は、JSON Schemaで書く必要があります。手書きも可能ですが、Pydanticを使ってPythonクラスで定義してからOpenAI形式に変換する方法が保守性の面で優れています。

### 悪い例：スキーマを手書きする

```
# 悪い例：JSON Schemaを直接手書き
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Web検索を実行する",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "検索クエリ"},
                    "max_results": {"type": "integer", "description": "最大件数"},
                },
                "required": ["query"],
            }
        }
    }
]
```

手書きの問題は、パラメータが増えるたびにJSONを直接編集する必要があること、型の誤りがランタイムまで気づかないこと、そして関数シグネチャとスキーマが乖離しやすいことです。

### 良い例：Pydanticでスキーマを定義してから変換する

```
from pydantic import BaseModel, Field
import json

# Pydanticでツールの入力スキーマを定義する
class SearchWebInput(BaseModel):
    query: str = Field(..., description="検索クエリ文字列")
    max_results: int = Field(default=5, description="取得する最大件数（1〜20）")

class GetWeatherInput(BaseModel):
    location: str = Field(..., description="都市名（例：Tokyo, Osaka）")
    unit: str = Field(default="celsius", description="温度の単位（celsius / fahrenheit）")

# Pydantic → OpenAI tools形式に変換するヘルパー
def pydantic_to_openai_tool(
    name: str,
    description: str,
    model: type[BaseModel],
    strict: bool = True,
) -> dict:
    schema = model.model_json_schema()
    # Pydantic v2 のスキーマから $defs を除去して整形する
    schema.pop("title", None)
    if strict:
        schema["additionalProperties"] = False
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "strict": strict,
            "parameters": schema,
        }
    }

# ツール定義リストを生成する
tools = [
    pydantic_to_openai_tool(
        name="search_web",
        description="Web検索を実行して最新情報を取得する",
        model=SearchWebInput,
    ),
    pydantic_to_openai_tool(
        name="get_weather",
        description="指定した都市の現在の天気情報を取得する",
        model=GetWeatherInput,
    ),
]
```

このアプローチの利点は3つです。関数シグネチャとスキーマが同じクラスから生成されるので乖離しない。Pydanticのバリデーションが引数の型を保証する。`strict=True` を指定することでLLMの引数がスキーマに完全準拠することを強制できる（`additionalProperties: False` が必要）。

`strict: True` は本番実装では推奨です。LLMが定義外のフィールドを勝手に追加するリスクを排除できます。

---

## エージェントループを手で書く：完全動作コード

ループの骨格は単純です。LLMに送る → `tool_calls` があれば実行してmessagesに追加 → `tool_calls` がなければ終了。この3ステップを繰り返すだけです。

### messagesリストに追加する順序

ポイントが2つあります。

* LLMのtool\_calls応答そのもの（`assistant` role）を先にmessagesに追加する
* 各ツールの実行結果を `tool_call_id` とセットで `tool` roleで追加する

この順序を守らないとAPIエラーになります。「assistantがツール呼び出しを要求した」という記録の後に「その結果」を置く、という会話の論理的な順序に従っています。

### 完全な実装コード

```
import json
import openai
from pydantic import BaseModel, Field

client = openai.OpenAI()  # OPENAI_API_KEY を環境変数に設定しておく

# ---- 入力スキーマ定義 ----

class SearchWebInput(BaseModel):
    query: str = Field(..., description="検索クエリ文字列")

class GetWeatherInput(BaseModel):
    location: str = Field(..., description="都市名（例：Tokyo, Osaka）")
    unit: str = Field(default="celsius", description="温度の単位（celsius / fahrenheit）")

class CalculateInput(BaseModel):
    expression: str = Field(..., description="計算式（例：'2 ** 10 + 3 * 7'）")

# ---- スキーマ変換ヘルパー ----

def pydantic_to_openai_tool(
    name: str,
    description: str,
    model: type[BaseModel],
    strict: bool = True,
) -> dict:
    schema = model.model_json_schema()
    schema.pop("title", None)
    if strict:
        schema["additionalProperties"] = False
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "strict": strict,
            "parameters": schema,
        }
    }

tools = [
    pydantic_to_openai_tool("search_web", "Web検索で最新情報を取得する", SearchWebInput),
    pydantic_to_openai_tool("get_weather", "指定都市の天気情報を取得する", GetWeatherInput),
    pydantic_to_openai_tool("calculate", "数式を評価して結果を返す", CalculateInput),
]

# ---- モック実装（本番では実際のAPIに置き換える）----

def search_web(query: str) -> str:
    return json.dumps({
        "results": [
            {"title": f"「{query}」に関する記事1", "snippet": "概要テキスト（モック）"},
            {"title": f"「{query}」に関する記事2", "snippet": "概要テキスト（モック）"},
        ]
    }, ensure_ascii=False)

def get_weather(location: str, unit: str = "celsius") -> str:
    return json.dumps({
        "location": location,
        "temperature": 22,
        "unit": unit,
        "condition": "晴れ",
        "humidity": 55,
    }, ensure_ascii=False)

def calculate(expression: str) -> str:
    try:
        # eval を使う場合はサンドボックス化が必要。本番では asteval 等を使うこと
        result = eval(expression, {"__builtins__": {}}, {})
        return json.dumps({"result": result, "expression": expression})
    except Exception as e:
        return json.dumps({"error": str(e), "expression": expression})

# ---- ツール実行のディスパッチャ ----

TOOL_REGISTRY = {
    "search_web": search_web,
    "get_weather": get_weather,
    "calculate": calculate,
}

def execute_tool(tool_call) -> str:
    """tool_callオブジェクトを受け取り、対応する関数を実行して結果を返す"""
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)  # argumentsはJSON文字列

    func = TOOL_REGISTRY.get(name)
    if func is None:
        return json.dumps({"error": f"未知のツール: {name}"})

    return func(**args)

# ---- エージェントループ ----

def run_agent(user_message: str, max_iterations: int = 10) -> str:
    """
    エージェントループを実行して最終応答を返す。

    Args:
        user_message: ユーザーの質問文
        max_iterations: 無限ループを防ぐための上限回数

    Returns:
        LLMの最終テキスト応答
    """
    messages = [
        {
            "role": "system",
            "content": (
                "あなたは有能なアシスタントです。"
                "必要に応じてツールを使い、正確な情報に基づいて回答してください。"
                "ツールの結果が得られたら、それを踏まえて丁寧に回答してください。"
            ),
        },
        {"role": "user", "content": user_message},
    ]

    for iteration in range(max_iterations):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        message = response.choices[0].message

        # LLMの応答を必ずmessagesに追加する（tool_callsあり・なし両方）
        messages.append(message)

        # tool_callsがなければループ終了
        if not message.tool_calls:
            return message.content or ""

        # tool_callsがある場合：各ツールを実行してresultを追加
        for tool_call in message.tool_calls:
            result = execute_tool(tool_call)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,  # tool_call_idは必須
                "content": result,
            })

    # max_iterations に達した場合
    return f"最大試行回数（{max_iterations}回）に達しました。処理を中断します。"

# ---- 実行例 ----
if __name__ == "__main__":
    answer = run_agent(
        "東京の今日の天気を教えてください。"
        "また、2の10乗と3の7乗を計算してどちらが大きいか教えてください。"
    )
    print(answer)
```

### ループの各ステップで何が起きているか

| ステップ | 処理の内容 | messagesへの変化 |
| --- | --- | --- |
| LLM呼び出し | tools付きでchat.completionsを呼ぶ | — |
| tool\_callsあり | assistantのmessageをそのまま追加 | assistantメッセージが追加される |
| ツール実行 | execute\_tool()を呼び、結果を取得 | tool roleのメッセージが追加される |
| tool\_callsなし | ループを抜けて最終応答を返す | — |

この流れを把握しておくと、エラーが出たときに「LLMへの入力（messages）」「LLMの出力（tool\_calls）」「ツールの実行結果」のどこが問題かを即座に特定できます。デバッグ時は `print(messages)` の1行でmessagesの全体像を確認できるのが、SDK直接実装の強みです。

---

## 複数ツールの組み合わせ：検索・計算・ファイル操作

上のコードは3つのツール（search\_web・get\_weather・calculate）を持っています。LLMは1回のレスポンスで複数のtool\_callsを返すことがあります。これが**並列ツール呼び出し**です。

```
# 「東京と大阪の天気を両方教えて」と聞いたとき
# LLMは1度のレスポンスで2つのtool_callsを返す場合がある

# message.tool_calls = [
#   ChatCompletionMessageToolCall(
#     id='call_abc',
#     function=Function(name='get_weather', arguments='{"location": "Tokyo"}')
#   ),
#   ChatCompletionMessageToolCall(
#     id='call_def',
#     function=Function(name='get_weather', arguments='{"location": "Osaka"}')
#   ),
# ]
```

ループの中の `for tool_call in message.tool_calls:` は、この並列ツール呼び出しも自然に処理します。全てのtool\_callを実行し、全ての結果をmessagesに追加してからLLMに再送信します。

### ファイル読み書きツールを追加する例

```
import os

class ReadFileInput(BaseModel):
    file_path: str = Field(..., description="読み込むファイルのパス")

class WriteFileInput(BaseModel):
    file_path: str = Field(..., description="書き込むファイルのパス")
    content: str = Field(..., description="書き込む内容")

def read_file(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return json.dumps({
            "file_path": file_path,
            "content": content,
            "size_bytes": len(content.encode("utf-8")),
        }, ensure_ascii=False)
    except FileNotFoundError:
        return json.dumps({"error": f"ファイルが見つかりません: {file_path}"})
    except Exception as e:
        return json.dumps({"error": str(e)})

def write_file(file_path: str, content: str) -> str:
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return json.dumps({
            "file_path": file_path,
            "bytes_written": len(content.encode("utf-8")),
            "status": "success",
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})

# ツール定義とレジストリに追加する
tools.extend([
    pydantic_to_openai_tool("read_file", "ファイルを読み込んで内容を返す", ReadFileInput),
    pydantic_to_openai_tool("write_file", "指定パスにファイルを書き込む", WriteFileInput),
])

TOOL_REGISTRY["read_file"] = read_file
TOOL_REGISTRY["write_file"] = write_file
```

ツールを追加するときはPydanticクラスを定義してスキーマ変換し、レジストリに関数を登録する。この2ステップだけです。ループのコード自体を変更する必要はありません。

---

## 終了条件の設計：エージェントを安全に止める

手動ループで最も重要な設計判断が「いつ止めるか」です。止め方を誤ると、無限ループで APIコストが爆発します。

### 悪い例：終了条件が1つしかない

```
# 悪い例：tool_callsがNoneになるのを無限に待つ
while True:
    response = client.chat.completions.create(...)
    message = response.choices[0].message
    messages.append(message)

    if not message.tool_calls:
        return message.content

    for tool_call in message.tool_calls:
        result = execute_tool(tool_call)
        messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": result})

# 問題：ツールがエラーを返し続けるとLLMがループし続ける
# 問題：LLMがバグでtool_callsを返し続けると無限ループになる
```

### 良い例：複数の終了条件を組み合わせる

```
def run_agent_safe(user_message: str) -> str:
    messages = [
        {"role": "system", "content": "あなたは有能なアシスタントです。"},
        {"role": "user", "content": user_message},
    ]

    max_iterations = 10       # 絶対的な上限回数
    tool_call_count = 0       # ツール呼び出しの累計回数
    max_tool_calls = 20       # ツール呼び出し数の上限

    for iteration in range(max_iterations):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        message = response.choices[0].message
        messages.append(message)

        # 終了条件1：ツール呼び出しなし（正常終了）
        if not message.tool_calls:
            return message.content or ""

        # 終了条件2：ツール呼び出し数が上限に達した
        tool_call_count += len(message.tool_calls)
        if tool_call_count >= max_tool_calls:
            return f"ツール呼び出し上限（{max_tool_calls}回）に達しました。"

        for tool_call in message.tool_calls:
            result = execute_tool(tool_call)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })

    # 終了条件3：イテレーション上限（フォールバック）
    return f"最大反復回数（{max_iterations}回）に達しました。"
```

| 終了条件 | 正常か異常か | 説明 |
| --- | --- | --- |
| `tool_calls` が `None` | 正常終了 | LLMが「もうツールは不要」と判断 |
| イテレーション上限 | 異常終了（フォールバック） | ループが止まらないときの安全弁 |
| ツール呼び出し数上限 | 異常終了（フォールバック） | 1回のイテレーションで大量呼び出しへの対応 |

実務では、異常終了した場合のログ記録とアラート送信も忘れずに実装してください。「上限に達した」という事実が記録されなければ、本番環境でのコスト爆発に気づけません。

---

OpenAI tools APIで書いた概念は、そのままAnthropicにも適用できます。異なるのはJSON Schemaのキー名と、ツール結果の返し方だけです。

### 主な違い

| 項目 | OpenAI | Anthropic |
| --- | --- | --- |
| ツール定義のキー | `parameters` | `input_schema` |
| ツール呼び出しの判定 | `message.tool_calls is not None` | `response.stop_reason == "tool_use"` |
| 引数の形式 | `arguments`（JSON文字列）→ `json.loads()` 必要 | `input`（すでにdict） |
| ツール結果のrole | `"tool"`（単独メッセージ） | `"user"`（contentにtool\_resultブロックを埋め込む） |
| スキーマ厳格化 | `"strict": true` + `additionalProperties: false` | `"strict": true` |

最大の違いは「ツール結果の返し方」です。OpenAIは `role: "tool"` の独立したメッセージとして追加します。AnthropicはOpenAIと異なり、`role: "user"` のメッセージ内に `tool_result` ブロックとして埋め込む形式になります。

### Anthropic版の実装

```
import anthropic
import json

client = anthropic.Anthropic()  # ANTHROPIC_API_KEY を環境変数に設定する

# Anthropic形式のツール定義（parametersではなくinput_schema）
tools_anthropic = [
    {
        "name": "search_web",
        "description": "Web検索を実行して最新情報を取得する",
        "input_schema": {           # OpenAIは "parameters"
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "検索クエリ文字列"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_weather",
        "description": "指定した都市の現在の天気情報を取得する",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "都市名（例：Tokyo, Osaka）"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "温度の単位"
                }
            },
            "required": ["location"]
        }
    }
]

def run_agent_anthropic(user_message: str, max_iterations: int = 10) -> str:
    messages = [{"role": "user", "content": user_message}]
    # Anthropicはsystemをメッセージリストの外に渡す

    for _ in range(max_iterations):
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system="あなたは有能なアシスタントです。必要に応じてツールを使って回答してください。",
            tools=tools_anthropic,
            messages=messages,
        )

        # 終了条件：stop_reasonで判定（OpenAIはtool_calls is Noneで判定）
        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return ""

        # tool_useブロックを処理する
        # AnthropicはOpenAIと異なり、argumentsはすでにdictとして返ってくる
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = TOOL_REGISTRY.get(block.name, lambda **kw: '{"error": "unknown tool"}')(**block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

        # assistantの応答をmessagesに追加する
        messages.append({"role": "assistant", "content": response.content})

        # ツール結果はuserメッセージとして追加する（OpenAIとの最大の違い）
        messages.append({"role": "user", "content": tool_results})

    return f"最大試行回数（{max_iterations}回）に達しました。"
```

コードは違いますが、概念は同じです。LLMにmessagesとtoolsを渡す→ツール呼び出し要求を受け取る→ツールを実行する→結果をmessagesに追加して再送信→LLMが「もう不要」と判断したら終了。この構造が理解できていれば、SDKが変わっても迷いません。

---

## LangChainありvsなし：いつ素のAPIを使うべきか

SDK直接実装とLangChain・LangGraphには、それぞれ向いている用途があります。どちらが優れているかではなく、目的に応じて使い分ける判断ができることが重要です。

### SDK直接実装が向いている場面

**デバッグ・学習・プロトタイプ**が主な用途です。

```
# SDK直接実装の最大の強み：messagesをそのままprintできる
def run_agent_debug(user_message: str) -> str:
    messages = [...]
    for iteration in range(10):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools,
        )
        message = response.choices[0].message
        messages.append(message)

        # 何がLLMに渡っているか、LLMが何を返したかを即座に確認できる
        print(f"\n[iteration {iteration}]")
        print(f"tool_calls: {message.tool_calls}")
        print(f"content: {message.content}")

        if not message.tool_calls:
            break
        for tool_call in message.tool_calls:
            result = execute_tool(tool_call)
            print(f"tool result ({tool_call.function.name}): {result}")
            messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": result})

    return message.content or ""
```

LangChainを使うと、エラーが「フレームワークのどのレイヤーで起きているか」がわかりにくくなります。SDK直接実装なら、print1行でmessages全体を確認でき、「LLMに何が渡っているか」「LLMが何を返したか」が一目でわかります。

### 比較表

| 観点 | SDK直接実装 | LangChain / LangGraph |
| --- | --- | --- |
| デバッグのしやすさ | 高い（print1本で全体確認） | やや難しい（抽象層の中でエラーが起きる） |
| 依存関係 | 少ない（openai/anthropicのみ） | 多い（破壊的変更が頻繁に発生） |
| 新API機能への対応 | 即座に試せる | フレームワーク対応待ちが発生する |
| 複雑なグラフ構造 | 自前実装のコストが高い | LangGraphが抽象化を提供 |
| 状態管理・チェックポイント | 自前実装が必要 | LangGraphが標準提供 |
| Human-in-the-loop | 実装が複雑になる | LangGraphが仕組みを提供 |
| 並列実行 | asyncio で対応可能 | LangGraphが宣言的に記述できる |
| チーム開発 | 抽象化がないので読みやすい | フレームワーク共通語彙がある |

### いつLangGraphに移行すべきか

以下のいずれかが必要になった時点で移行を検討します。

* 複数のエージェントが協調して動く構造が必要
* 「途中でユーザーに確認を挟む」Human-in-the-loopが必要
* 実行状態のチェックポイントと再開が必要
* エラー時の特定ノードへの再ルーティングが必要
* グラフ構造の可視化・デバッグのための標準ツールが必要

これらが不要なうちはSDK直接実装で十分です。早すぎるフレームワーク導入は、「便利なのにデバッグできない」という状態を作り出します。

### 学習順序の価値

SDK直接実装 → LangGraphへの移行、という順序に意味があります。

LangGraphが「状態管理」「グラフのエッジ」「条件分岐」として抽象化しているものが、実は自前実装では「messagesリストへの追記」と「while-loopの終了条件」であることがわかります。LangGraphのStateGraphのノードが「messagesを受け取りmessagesを返す関数」であること、条件エッジが「tool\_callsがあるかどうか」の判定であること、これらが自然に理解できます。

抽象層の中身を知っている人と知らない人では、LangGraphを使うときの設計力とトラブル対応力に大きな差が出ます。

---

## まとめ

この記事で整理した内容をまとめます。

1. **エージェントループの正体は3ステップの繰り返し**。LLMにtools付きでmessagesを送る → tool\_callsを受け取ってツールを実行する → 結果をmessagesに追加して再送信する。tool\_callsがNoneになったら終了
2. **ツール定義はPydanticで書くと保守性が上がる**。関数シグネチャとスキーマが同じクラスから生成されるので乖離しない。`strict=True` + `additionalProperties: False` で引数のスキーマ準拠を強制できる
3. **messagesへの追加順序はアーキテクチャの制約**。assistantのtool\_calls応答を先に追加し、その後にtool結果を追加する。この順序を守らないとAPIエラーになる
4. **終了条件は複数用意する**。tool\_callsがNone（正常終了）・イテレーション上限・ツール呼び出し数上限の3つを組み合わせることで、本番での無限ループとコスト爆発を防ぐ
5. **OpenAIとAnthropicは概念が同じ**。違いはスキーマキー名（`parameters` vs `input_schema`）、ツール結果の返し方（独立メッセージ vs userメッセージへの埋め込み）だけ。構造を理解していれば、SDKが変わっても迷わない
6. **SDK直接実装とLangGraphは競合ではなく順序**。まずSDKで書いて構造を掴み、複雑なグラフ構造や状態管理が必要になった時点でLangGraphに移行する

40〜50行のコードで「エージェントの正体」が見えてきます。次のステップはこの骨格にエラーハンドリングを追加し、ツールを本物のAPIに置き換え、必要になったタイミングでLangGraphへ移行することです。

---

## よくある質問（FAQ）

### Q. LLMエージェントとは何ですか？

**LLMエージェントとは、LLMが「ツールを何の引数で呼ぶか」を判断し、Pythonコードがそのツールを実行して結果をLLMに返すサイクルを繰り返す仕組みです。** LLM自体はテキスト生成しか行いません。OpenAI tools APIを使うと、LLMは「このツールをこの引数で呼んでほしい」という指示を返し、実際の実行はPythonコードが担います。この往復ループがエージェントの正体です。

### Q. LLMエージェントをフレームワークなしで実装するには何が必要ですか？

**`openai` ライブラリと `OPENAI_API_KEY` の環境変数設定、そしてPythonのwhile-loopを書く知識だけで始められます。** `pip install openai pydantic` でインストールし、ツールをPydanticクラスで定義してOpenAI形式に変換、あとはwhile-loopでLLMとツールを往復させるだけです。本記事の40〜50行の実装をそのまま実行することで、フレームワークなしのエージェントを今すぐ動かせます。

### Q. LangChainを使わずに実装するメリットは何ですか？

**デバッグが容易になり、エラーがどこで起きているかを即座に特定できます。** LangChainを使うとエラーがフレームワークの抽象層の中で発生するため、根本原因を追いにくくなります。SDK直接実装では `print(messages)` の1行でLLMへの入力と出力の全体像を確認でき、依存パッケージも `openai` のみで破壊的変更のリスクが最小限です。新しいAPI機能も公開直後に試せます。

### Q. エージェントのループが止まらなくなる原因は何ですか？

**ツールがエラーを返し続けるか、LLMがtool\_callsを返し続けることでループが収束しない状態が発生します。** 対策は終了条件を複数用意することです。tool\_callsがNone（正常終了）・イテレーション上限・ツール呼び出し数の上限の3つを組み合わせることで、本番での無限ループとAPIコスト爆発を防げます。本記事の `run_agent_safe` 関数がこの3つの終了条件を実装した参照実装です。

### Q. LangGraphへの移行はいつ検討すべきですか？

**複数エージェントの協調・Human-in-the-loop・実行状態のチェックポイント再開が必要になった時点で移行を検討してください。** これらが不要なうちはSDK直接実装で十分です。SDK実装を経験してからLangGraphへ移行することで、LangGraphが抽象化しているものの正体（messagesリストへの追記・while-loopの終了条件）が理解でき、設計力とトラブル対応力が大きく上がります。

---

## 著者について

**三好大悟**

株式会社リベルクラフト 代表取締役。AI・データ活用コンサルティング、受託開発（B2B）を中心に、KADOKAWA・JAXA・防衛省・ミスミなど多業種のAI導入プロジェクトを支援。Craft College（データサイエンス・AI実践スクール）を運営し、LLMエンジニアを目指す社会人の転職・スキル習得を支援している。

---

!

この記事ではフレームワークなしのエージェント実装パターンを整理しましたが、  
エージェントの内部構造を理解した上で実務応用する体験は

**Craft College Advanced**（3ヶ月・少人数コホート）で提供しています。

→ [Craft College Advanced 詳細・無料相談はこちら](https://liber-craft.co.jp/school/craft-college-ds-advanced)

無料相談は30分です。ぜひお気軽にご連絡ください。
