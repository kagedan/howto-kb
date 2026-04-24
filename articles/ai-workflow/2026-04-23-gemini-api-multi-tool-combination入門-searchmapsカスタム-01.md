---
id: "2026-04-23-gemini-api-multi-tool-combination入門-searchmapsカスタム-01"
title: "Gemini API Multi-Tool Combination入門 — Search・Maps・カスタム関数を1コールで組み合わせる"
url: "https://zenn.dev/kai_kou/articles/197-gemini-api-multi-tool-combination-guide"
source: "zenn"
category: "ai-workflow"
tags: ["API", "LLM", "Gemini", "Python", "zenn"]
date_published: "2026-04-23"
date_collected: "2026-04-24"
summary_by: "auto-rss"
query: ""
---

## はじめに

AIエージェント開発における長年の課題のひとつが、**複数のツールを連携させるオーケストレーション**の複雑さです。Google SearchでWebを検索し、Google Mapsで位置情報を取得し、さらに独自のビジネスロジックを組み合わせる場合、従来は複数のAPIコールと複雑なフロー制御が必要でした。

2026年4月、Google DeepMindはGemini APIに**Multi-Tool Combination（マルチツール組み合わせ）機能**を追加しました。これにより、組み込みツール（Google Search・Google Maps）とカスタム関数宣言を**1つのAPIコールで同時に指定**し、Geminiが自律的に適切なツールを選択・実行できるようになりました。

### この記事で解説すること

* Multi-Tool Combinationの仕組みとアーキテクチャ
* Context Circulation（コンテキスト循環）による多ターン推論
* Parallel Tool Execution（並列ツール実行）の実装
* Python実装例と`include_server_side_tool_invocations`フラグの使い方
* 対応モデルと料金の考え方

### 前提条件

* Python 3.10以上
* `google-genai` パッケージ（`pip install --upgrade google-genai`）
* Gemini API キー（[Google AI Studio](https://aistudio.google.com/)で取得）

## TL;DR

* Gemini APIがGoogle Search・Maps・カスタム関数を**1コール**で組み合わせ可能に
* `include_server_side_tool_invocations: true` フラグで有効化
* **Context Circulation**でツール結果が後続ステップに引き継がれる
* **Parallel Tool Execution**で独立した関数を同時実行しレイテンシを削減
* 対応モデル: `gemini-3-flash-preview`・`gemini-3.1-pro-preview`

---

### 従来のアプローチの課題

従来のエージェント開発では、複数のツールを組み合わせる場合、開発者が以下を手動で実装する必要がありました:

1. LLMにツールの選択を問い合わせる
2. 選択されたツールを個別に実行する
3. 結果をコンテキストに追加してLLMに再送信する
4. 次のツール選択を繰り返す

この「思考→行動→観察」のループを何度も繰り返すことで、レイテンシが増大し、コードも複雑になりがちでした。

### 新機能: 1コールでのツール組み合わせ

Multi-Tool Combinationでは、Geminiが**サーバーサイドで組み込みツール（Search・Maps）を自律実行**しながら、必要に応じてカスタム関数の呼び出しも要求します。

```
[従来]
User → Gemini → (Search) → Gemini → (Maps) → Gemini → (カスタム関数) → 回答
                 ↑3回のAPIコール

[Multi-Tool Combination]
User → Gemini → 回答
        ↑サーバーサイドで自動実行
```

---

## 主要機能の解説

### 1. Context Circulation（コンテキスト循環）

Context Circulationは、組み込みツールの実行結果（`toolCall`・`toolResponse`）を**後続の推論ステップに引き継ぐ**機能です。

公式ドキュメントによると:

> "Tool context circulation makes it possible to preserve and expose the context of built-in tools and share it with custom tools in the same call from turn to turn."  
> — [Gemini API ドキュメント](https://ai.google.dev/gemini-api/docs/tool-combination)

**実用例**: Gemini が Google Search で「北米最北端の都市」を検索し、その結果（アラスカ州ウトキアグビク）をコンテキストとして保持したまま、カスタムの天気情報取得関数を呼び出します。この際、検索結果のコンテキストが自動的に引き継がれるため、開発者が手動でデータを受け渡す必要がありません。

互いに依存しない複数の関数を**同時並行で実行**する機能です。Geminiが並列化可能と判断した場合、1つのレスポンスに複数の`functionCall`が含まれます。

各関数呼び出しには一意の`id`が付与されます。開発者は:

1. Geminiのレスポンスから複数のfunctionCallを取得
2. 外部APIへの呼び出しを並行実行
3. 結果を`id`で紐付けてGeminiに一括返却

この仕組みにより、APIラウンドトリップを削減しレイテンシを大幅に改善できます。

Multi-Tool Combinationを有効化するための必須フラグです。

```
config=types.GenerateContentConfig(
    tools=[...],
    tool_config=types.ToolConfig(
        include_server_side_tool_invocations=True
    )
)
```

---

## Python実装例

### セットアップ

```
pip install --upgrade google-genai
```

```
import os
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL = "gemini-3-flash-preview"
```

### 基本例: Google Search + カスタム関数

以下の例では、Google Searchで最新情報を検索しつつ、カスタムの`get_local_time`関数を組み合わせています。

```
def get_local_time(city: str) -> dict:
    """指定都市の現地時刻を取得する（実際はAPIを呼び出す）"""
    # 本番環境では外部API（worldtimeapi.org等）を呼び出す
    time_zones = {
        "Tokyo": "JST+9",
        "New York": "EST-5",
        "London": "GMT+0",
    }
    return {"city": city, "timezone": time_zones.get(city, "UTC"), "status": "ok"}

# ツール設定
tools = [
    types.Tool(
        google_search=types.GoogleSearch(),  # 組み込みツール: Google Search
        function_declarations=[
            types.FunctionDeclaration(
                name="get_local_time",
                description="指定した都市の現地時刻とタイムゾーンを取得します",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "city": types.Schema(
                            type=types.Type.STRING,
                            description="都市名（英語）",
                        )
                    },
                    required=["city"],
                ),
            )
        ],
    )
]

# APIコール（コンテキスト循環を有効化）
config = types.GenerateContentConfig(
    tools=tools,
    tool_config=types.ToolConfig(
        include_server_side_tool_invocations=True
    ),
)

response = client.models.generate_content(
    model=MODEL,
    contents="東京の最新AIニュースを調べて、現在の東京時間も教えてください。",
    config=config,
)

# functionCallが含まれる場合は実行して結果を返す
for part in response.candidates[0].content.parts:
    if part.function_call:
        fc = part.function_call
        if fc.name == "get_local_time":
            result = get_local_time(**fc.args)
            # 結果をGeminiに返す
            follow_up = client.models.generate_content(
                model=MODEL,
                contents=[
                    types.Content(
                        role="user",
                        parts=[types.Part(text="東京の最新AIニュースを調べて、現在の東京時間も教えてください。")]
                    ),
                    response.candidates[0].content,
                    types.Content(
                        role="user",
                        parts=[
                            types.Part(
                                function_response=types.FunctionResponse(
                                    id=fc.id,
                                    name=fc.name,
                                    response=result,
                                )
                            )
                        ]
                    ),
                ],
                config=config,
            )
            print(follow_up.text)
```

### 並列ツール実行例: 複数都市を同時処理

```
import asyncio

async def fetch_city_info(city: str) -> dict:
    """都市情報を非同期で取得"""
    await asyncio.sleep(0.1)  # 実際はAPIコール
    return {"city": city, "population": "dummy_data", "status": "ok"}

async def process_parallel_function_calls(response):
    """Geminiから返された並列functionCallを処理"""
    function_calls = [
        part.function_call
        for part in response.candidates[0].content.parts
        if part.function_call
    ]
    
    if not function_calls:
        print(response.text)
        return
    
    # 全functionCallを並列実行
    tasks = [fetch_city_info(fc.args["city"]) for fc in function_calls]
    results = await asyncio.gather(*tasks)
    
    # 結果をidで紐付けて一括返却
    function_responses = [
        types.Part(
            function_response=types.FunctionResponse(
                id=fc.id,  # 必須: 元のidと一致させる
                name=fc.name,
                response=result,
            )
        )
        for fc, result in zip(function_calls, results)
    ]
    
    return function_responses

# 並列実行の確認
multi_city_response = client.models.generate_content(
    model=MODEL,
    contents="東京・ロンドン・ニューヨークの人口を同時に教えてください。",
    config=config,
)

responses = asyncio.run(process_parallel_function_calls(multi_city_response))
print(f"並列実行した関数数: {len(responses)}")
```

---

## Google Maps組み込みとの連携

Google Mapsの組み込みツールを使うと、Geminiが**リアルタイムの位置情報・店舗情報・経路**を自律的に取得できます。

```
# Google Search + Google Maps + カスタム関数の3ツール組み合わせ
tools_with_maps = [
    types.Tool(
        google_search=types.GoogleSearch(),
        google_maps=types.GoogleMaps(),  # Maps組み込みツール
        function_declarations=[
            types.FunctionDeclaration(
                name="book_venue",
                description="指定した場所のイベント会場を予約します",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "venue_name": types.Schema(type=types.Type.STRING),
                        "date": types.Schema(type=types.Type.STRING),
                        "capacity": types.Schema(type=types.Type.INTEGER),
                    },
                    required=["venue_name", "date"],
                ),
            )
        ],
    )
]

response = client.models.generate_content(
    model=MODEL,
    contents="東京・渋谷周辺で50人規模のテックイベント向け会場を探して、来週金曜日に予約してください。",
    config=types.GenerateContentConfig(
        tools=tools_with_maps,
        tool_config=types.ToolConfig(
            include_server_side_tool_invocations=True
        ),
    ),
)
```

このコードでは、Geminiが:

1. **Google Search**でイベント会場の情報を検索
2. **Google Maps**で渋谷周辺の実際の場所・評価を取得
3. 適切な会場が見つかれば、**`book_venue`カスタム関数**を呼び出して予約

という3段階のオーケストレーションを自律的に実行します。

---

## 対応モデルと料金

### 対応Geminiモデル（2026年4月時点）

| モデルID | 特徴 | 入力料金 | 出力料金 |
| --- | --- | --- | --- |
| `gemini-3-flash-preview` | 高速・高コスパ、エージェントワークフロー向け | $0.50/1Mトークン | $3.00/1Mトークン |
| `gemini-3.1-pro-preview` | 高度な推論・複雑なタスク向け | $2.00/1Mトークン | $12.00/1Mトークン |

出典: [Gemini API Pricing](https://ai.google.dev/gemini-api/docs/pricing)（2026年4月時点）

### コスト最適化のヒント

Multi-Tool Combinationを使うとコンテキスト循環によりトークン消費が増える可能性があります。以下の対策が有効です:

* **Context Caching**: 繰り返し利用するプロンプトやコンテキストをキャッシュ（最大90%コスト削減）
* **Batch API**: 非同期処理可能なタスクに活用（50%コスト削減）
* **Flex Inference**: リアルタイム性が不要な場合に活用

---

## 注意点

---

## まとめ

Gemini API Multi-Tool Combinationにより、エージェント開発のオーケストレーション複雑性が大幅に軽減されました。

* **1コールで完結**: Google Search・Maps・カスタム関数を単一APIコールで指定
* **Context Circulation**: ツール結果が自動的に後続ステップに引き継がれる
* **Parallel Execution**: 独立した関数を同時実行しレイテンシを削減
* **エージェント開発の民主化**: 複雑なオーケストレーションコードが不要に

`include_server_side_tool_invocations`フラグを有効にするだけで利用でき、対応モデル（`gemini-3-flash-preview`・`gemini-3-1-pro-preview`）はすでにGoogle AI Studio経由で利用可能です。位置情報サービス・リサーチエージェント・カスタマーサポートなど、複数のデータソースを組み合わせるアプリケーションで特に力を発揮します。

## 参考リンク
