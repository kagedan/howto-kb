---
id: "2026-04-30-openai-agents-sdkを使ってマルチエージェントシステムを作ってみた-01"
title: "OpenAI Agents SDKを使ってマルチエージェントシステムを作ってみた"
url: "https://zenn.dev/titosemi/articles/f6b906d40bee8a"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "API", "AI-agent", "zenn"]
date_published: "2026-04-30"
date_collected: "2026-05-01"
summary_by: "auto-rss"
---

## はじめに

最近、AIエージェントという言葉をよく聞くようになりましたが、実際にコードで書いてみると「思ったより簡単だった」というのが正直な感想です。

今回、僕はOpenAIが公式に提供している **OpenAI Agents SDK** を使って、シンプルなエージェントから始まり、カスタムツール、さらにはマルチエージェントのハンドオフまでを実際に動かしてみました。その手順と実行結果をまとめます。

公式ドキュメント:

<https://developers.openai.com/api/docs/guides/agents>

---

## OpenAI Agents SDKとは？

OpenAI Agents SDKは、OpenAIが提供するエージェント構築のためのPython/TypeScript用SDKです（バージョン: 0.14.8）。

単純なチャットボットとの違いは「ツール呼び出し」と「エージェント間の連携（ハンドオフ）」を宣言的に書けることです。具体的には次のことが簡単にできます。

* `Agent` クラスでエージェントの役割・モデルを定義する
* `@function_tool` デコレータでPython関数をツールとして登録する
* `handoffs` でエージェントが別のエージェントに処理を委譲できるようにする
* `Runner.run()` で非同期にエージェントを実行する

---

## 環境構築

```
pip install openai-agents
export OPENAI_API_KEY=sk-...
```

たったこれだけです。依存関係も少なく、すぐに始められます。

---

## シナリオ1：シンプルなエージェント

まずは基本から。`Agent` を定義して `Runner.run()` で動かします。

```
import asyncio
from agents import Agent, Runner

agent = Agent(
    name="travel_advisor",
    instructions="あなたは日本の観光地に詳しい旅行アドバイザーです。質問に対して簡潔に日本語で答えてください。",
    model="gpt-4o-mini",
)

async def main():
    result = await Runner.run(agent, "京都でおすすめの観光スポットを3つ教えてください。")
    print(result.final_output)

asyncio.run(main())
```

**実行結果:**

```
もちろんです！京都でおすすめの観光スポットは以下の3つです。

1. **金閣寺（鹿苑寺）** - 美しい金色の外観が特徴で、庭園も楽しめます。
2. **清水寺** - 京都のシンボル的存在で、のびやかな舞台からの眺望が素晴らしいです。
3. **嵐山** - 自然豊かなエリアで、竹林や渡月橋の美しい景色を楽しめます。
```

ポイントは `result.final_output` にテキスト結果が入り、`result.history` に会話履歴が入ることです。次のターンではこのhistoryを引き継いで会話を継続できます。

---

## シナリオ2：カスタム関数ツールを使ったエージェント

`@function_tool` デコレータを付けるだけで、Pythonの関数をエージェントが呼び出せるツールに変換できます。ここでは天気情報と移動時間を返すツールを作りました（今回はダミーデータですが、実際のAPIと差し替えるだけで使えます）。

```
from agents import Agent, Runner, function_tool

@function_tool
def get_weather(city: str) -> str:
    """指定した都市の天気情報を返す"""
    weather_data = {
        "東京": "晴れ、気温25°C、湿度60%",
        "大阪": "曇り、気温23°C、湿度65%",
    }
    return weather_data.get(city, f"{city}の天気データが見つかりませんでした。")

@function_tool
def get_travel_time(from_city: str, to_city: str) -> str:
    """2都市間の移動時間を返す"""
    return "新幹線で約2時間30分"

agent = Agent(
    name="travel_planner",
    instructions="旅行プランニングのアシスタントです。天気情報と移動時間ツールを使って相談に乗ってください。日本語で回答してください。",
    tools=[get_weather, get_travel_time],
    model="gpt-4o-mini",
)

async def main():
    result = await Runner.run(
        agent,
        "東京から大阪に旅行を考えています。今の天気と移動時間を教えてください。"
    )
    print(result.final_output)

asyncio.run(main())
```

**実行結果:**

```
現在の天気は以下の通りです。

- **東京**: 晴れ、気温25°C、湿度60%
- **大阪**: 曇り、気温23°C、湿度65%

移動時間は新幹線で約**2時間30分**です。
何か他に知りたいことはありますか？
```

エージェントが `get_weather("東京")`、`get_weather("大阪")`、`get_travel_time("東京", "大阪")` を自動的に呼び出して、結果を統合して回答してくれました。開発者はツールの実装に集中するだけでよく、ツールを何回・どの順番で呼ぶかはモデルが判断してくれます。

---

## シナリオ3：マルチエージェント（トリアージ + ハンドオフ）

これがAgents SDKの一番面白い機能です。受付エージェントが質問の種類に応じて専門エージェントへ委譲（ハンドオフ）します。

```
from agents import Agent, Runner

# 専門エージェントを定義
tech_support_agent = Agent(
    name="tech_support",
    handoff_description="技術的な問題やプログラミングに関する質問を担当するエージェントです",
    instructions="エンジニア向け技術サポートの専門家です。日本語で技術的に正確に回答してください。",
    model="gpt-4o-mini",
)

billing_agent = Agent(
    name="billing_support",
    handoff_description="料金・請求に関する質問を担当するエージェントです",
    instructions="請求・料金に関するサポート専門家です。日本語で回答してください。",
    model="gpt-4o-mini",
)

# トリアージエージェント（振り分け役）
triage_agent = Agent(
    name="customer_support_triage",
    instructions=(
        "カスタマーサポートの受付担当です。\n"
        "- 技術的な問題 → tech_support へ引き継ぐ\n"
        "- 料金・請求の問題 → billing_support へ引き継ぐ"
    ),
    handoffs=[tech_support_agent, billing_agent],
    model="gpt-4o-mini",
)

async def main():
    questions = [
        "Pythonでリストの重複を削除する方法を教えてください。",
        "今月の請求額が先月より高いのですが、理由を教えてください。",
    ]
    for q in questions:
        result = await Runner.run(triage_agent, q)
        print(f"質問: {q}")
        print(f"担当: {result.last_agent.name}")
        print(f"回答: {result.final_output[:150]}...")
        print("---")

asyncio.run(main())
```

**実行結果:**

```
質問: Pythonでリストの重複を削除する方法を教えてください。
担当: tech_support
回答: Pythonでリストの重複を削除する方法はいくつかありますが、以下の方法が一般的です。
### 方法1: `set`を使う
`set`は重複を許さないデータ型であるため...

---
質問: 今月の請求額が先月より高いのですが、理由を教えてください。
担当: billing_support
回答: 請求額が先月より高くなった理由はいくつか考えられます。一般的には以下の要因が影響する場合があります：
1. **使用量の増加**: サービスの利用頻度や量が増えた場合。
2. **料金改定**: プランやサービスの料金が変更された場合...
```

`result.last_agent.name` で最終的にどのエージェントが回答したかを確認できるのが便利です。トリアージエージェントが適切な専門エージェントへ引き継いでいることが確認できました。

---

## ハマりポイント：エージェント名に日本語は使えない

マルチエージェントを実装するとき、エージェントの `name` に日本語を使おうとしてハマりました。

```
Tool name 'transfer_to_技術サポートエージェント' contains invalid characters
and has been transformed to 'transfer_to_____________'.
```

ハンドオフ時、SDKは `transfer_to_{name}` という関数ツールを内部的に生成します。OpenAIのFunction Callingでは、ツール名に使えるのは **英数字とアンダースコアのみ** です。日本語のエージェント名は全部 `_` に変換されてしまい、区別できなくなります。

**解決策:** `name` は英数字+アンダースコアのみにして、日本語の説明は `handoff_description` や `instructions` に書きましょう。

```
# ❌ NG
Agent(name="技術サポートエージェント", ...)

# ✅ OK
Agent(
    name="tech_support",                             # 英数字のみ
    handoff_description="技術的な質問を担当します",   # 日本語はここに
    instructions="技術サポートの専門家として...",
)
```

---

## まとめ

OpenAI Agents SDKを実際に動かしてみた感想をまとめます。

**良かった点:**

* `@function_tool` デコレータだけでツールを登録できるシンプルさ
* `handoffs` リストに渡すだけでマルチエージェントが組める手軽さ
* `result.last_agent` や `result.history` など、実行後の状態が取りやすい設計

**注意点:**

* エージェントの `name` は英数字とアンダースコアのみ使用すること
* すべての処理が非同期（`async/await`）なので、Pythonの非同期に慣れていないと戸惑うかもしれない
* ツールの関数docstringがモデルへのツール説明として使われるので、しっかり書いておく

**次のステップとして試したいこと:**

* ガードレール（入力・出力の検証）の追加
* セッション管理とマルチターン会話
* MCP（Model Context Protocol）サーバーとの連携
* ストリーミングでリアルタイム応答

エージェントフレームワークは「難しそう」と思っていましたが、OpenAI Agents SDKは思ったよりずっと直感的でした。みなさんもぜひ試してみてください！

---

## 参考リンク
