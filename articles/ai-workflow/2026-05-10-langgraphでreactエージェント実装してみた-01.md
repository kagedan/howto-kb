---
id: "2026-05-10-langgraphでreactエージェント実装してみた-01"
title: "LangGraphでReActエージェント実装してみた"
url: "https://zenn.dev/mori373/articles/20260508-react-agent"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "AI-agent", "LLM", "Gemini", "Python"]
date_published: "2026-05-10"
date_collected: "2026-05-11"
summary_by: "auto-rss"
query: ""
---

# はじめに

こんにちは！現在大学院でAI研究を行っているmori-373([@mm03](https://x.com/mm_mc04318))です。  
最近は、LangGraphを使ったAIエージェントの勉強などを精力的に行っております。

今回は、AIエージェントの設計パターンで最も基本的なものの一つであるReActエージェントをLangGraphで実装してみました！

また、実装はnotebookで行い、以下のリポジトリにアップしています。  
<https://github.com/mori-318/ai-agent-design-pattern>

# 基礎知識

## ReActとは？

ReActとは、簡単にいうとReasoning（推論）とActing（行動）を交互に繰り返すエージェントパターンで、調べた限りでは、2022年に発表された[REACT: SYNERGIZING REASONING AND ACTING IN LANGUAGE MODELS](https://arxiv.org/pdf/2210.03629)という論文で提案されたものとなっています。

LLMが自律的に必要な行動を行い、その結果をもとにさらに行動するのか、タスク完了とするのかなどを判断します。

## LangGraphとは

LangGraphとは、LangChainエコシステムの中で開発されたAIエージェントフレームワークです。  
複数のAIやツールを「グラフ構造」で繋げて作成することで簡単にAIエージェントを実装することができます。

# LangGraphでのReAct実装

## 前準備

あらかじめ、`.env`ファイルを作成して以下を設定します。  
Tavilyは、Web検索機能を提供しているサービスで、以下からログインして、APIキーを取得できます。（無料枠があり、本記事の実行ぐらいは全然大丈夫です！）  
<https://app.tavily.com/home>

```
GEMINI_API_KEY=""
TAVILY_API_KEY=""
```

## ReAct.ipynbの実装

**== 必要なモジュールのインポート ==**

```
from IPython.display import display, Image

from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph, MessagesState

# .envを読み込む
load_dotenv()
```

**== 検索ツールの実装 ==**  
tavilyを使用して、AIが使用する検索ツールを実装します。

```
tavily_search = TavilySearchResults(max_results=3)

@tool
def web_search(search_query: str) -> list[str]:
    """クエリの内容に応じて、web検索を行う関数

    Args:
        search_query: ユーザーからの検索クエリ
    Returns:
        検索結果のリスト
    """
    results = tavily_search.invoke(search_query)

    # 結果を整形
    results_formatted = []
    for result in results:
        title = result.get("title", "No Title")
        content = result.get("content", "No Content")
        results_formatted.append(f"タイトル：{title}\n\nコンテンツ：{content}")

    return results_formatted

tools = [web_search]
tools_by_name = {tool.name: tool for tool in tools}
```

**== モデルの準備 ==**  
今回は、Gemini 2.5 Flash Liteを使います。  
また、`bind_tools`でLLMが検索ツールを呼び出せるようにします。

```
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)
llm_with_tools = llm.bind_tools(tools)
```

**== ノードの実装 ==**  
次に、ReActの流れに対応するノードを実装します。

* `node_call_llm`: LLMを呼び出す
* `node_route`: ツール実行に進むか終了するかを判断する
* `node_tools`: 実際にツールを呼び出し、結果を`ToolMessage`で返す

```
system_prompt = """
あなたは、ユーザーの旅行予定をもとに、観光計画を立案するAIエージェントです。
Web検索機能を使用しながら、ユーザーの質問に答えてください。

## 注意点
- 単一のweb検索結果のみで判断せず、いろいろな視点で情報を集めてください。
"""

def node_call_llm(state: MessagesState):
    """LLMを呼び出すノード"""
    # 最初の呼び出しの場合は、system promptを追加する
    if len(state["messages"]) == 1:
        messages = [
            SystemMessage(content=system_prompt),
            state["messages"][-1],
        ]
    else:
        messages = state["messages"]

    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def node_route(state: MessagesState):
    """次のノードをルーティングするノード"""
    if len(state["messages"]) > 6:
        return END

    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "tools"

    return END

def node_tools(state: MessagesState):
    """ツール呼び出しを実行するノード"""
    last_message = state["messages"][-1]

    tool_messages = []
    for tool_call in getattr(last_message, "tool_calls", []):
        tool_name = tool_call.get("name")
        tool = tools_by_name.get(tool_name)
        if tool is None:
            continue

        args = tool_call.get("args", {}) or {}
        tool_result = tool.invoke(args)

        tool_messages.append(
            ToolMessage(
                content=str(tool_result),
                name=tool_name,
                tool_call_id=tool_call["id"],
            )
        )

    return {"messages": tool_messages}
```

**== グラフの構築 ==**  
ノードを定義したら、LangGraphで接続してReActエージェントグラフを構築します。

```
builder = StateGraph(MessagesState)

builder.add_node("call_llm", node_call_llm)
builder.add_node("tools", node_tools)

builder.add_edge(START, "call_llm")
builder.add_conditional_edges(
    "call_llm",
    node_route,
    {"tools": "tools", END: END},
)
builder.add_edge("tools", "call_llm")

react_agent = builder.compile()

display(Image(react_agent.get_graph().draw_mermaid_png()))
```

このセルを実行すると、以下の画像が表示されます。  
この図では、call\_llmがReasoningを担当しており、ここでtoolsを実行（Acting）するか、現在の状態でユーザーの質問に回答するかを判断します。  
toolsでは、call\_llmに渡された検索クエリをもとに検索を行い、その結果をcall\_llmに返します。  
![作成したReActエージェントグラフ](https://static.zenn.studio/user-upload/deployed-images/1da3a54bb01679b534c3df3d.png?sha=5bb3398735ade763364174429ac3e26d17505f8e)

**== エージェントの実行 ==**  
ユーザー入力を与えてエージェントを実行します。

```
messages = [HumanMessage(content="4月頭の奄美大島の三泊旅行に行きます。ご飯、自然などを味わえる1日ごとの旅行計画を作ってください！")]
response = react_agent.invoke({"messages": messages})
```

**== エージェントの回答を表示 ==**  
エージェントの回答を表示します。  
`pretty_print`というメソッドが組み込まれており、これを実行すると、見やすい形でエージェントの回答を表示してくれます。

```
response["messages"][-1].pretty_print()
```

表示結果は以下のようになりました！  
いい感じに旅行計画を作成してくれてますね〜

AIの回答

```
================================== Ai Message ==================================

4月頭の奄美大島旅行、楽しみですね！温暖な気候で自然を満喫できるベストシーズンです。以下に、おすすめのご飯、自然、そしてそれらを味わえる1日ごとの旅行計画をご提案します。

**奄美大島の4月について**

*   **気候:** 平均気温は約20〜23℃で、日中は半袖でも過ごせる暖かさですが、朝晩は肌寒く感じることもあります。薄手の羽織りものやストールがあると便利です。
*   **服装:** Tシャツ、長袖の羽織り、スニーカーが基本。雨具（折りたたみ傘や撥水ジャケット）も忘れずに。日差しが強くなるので、帽子、サングラス、日焼け止めも必須です。
*   **海:** 海開きは3月ですが、4月は水温が21℃前後になるため、ウェットスーツを着用すればシュノーケリングやダイビングが楽しめます。

**おすすめのご飯**

*   **鶏飯（けいはん）:** 奄美のソウルフード。ご飯に具材を乗せ、鶏がらスープをかけていただきます。
*   **油そうめん:** そうめん（またはうどん）に煮干し、人参、ニラなどを入れたあっさりとした一品。
*   **島料理:** 新鮮な魚介類を使った刺身や、豚の角煮、ヤギ汁（挑戦する価値あり！）、もずく天ぷらなど。
*   **黒糖焼酎:** 奄美ならではのお酒。様々な種類の蔵元があるので、飲み比べてみるのも楽しいでしょう。
*   **海鮮料理:** 新鮮な魚介類が豊富。特に「あまみの魚たち」や「島の居酒屋むちゃかな」などがおすすめです。
*   **郷土料理:** 「喜多八」や「鳥しん」などで、奄美の伝統的な味を堪能できます。

**おすすめの自然・アクティビティ**

*   **マングローブ:** 黒潮の森マングローブパークでのカヌー体験は、神秘的な自然を感じられます。
*   **滝:** フナンギョの滝、タンギョの滝、アランガチの滝など、迫力ある滝や癒される滝があります。
*   **ビーチ:** 土盛海岸、倉崎海岸、実久海岸など、美しいビーチがたくさんあります。シュノーケリングやダイビングも楽しめます。
*   **金作原原生林:** 手付かずの亜熱帯広葉樹林を散策できます（ガイドツアー推奨）。
*   **星空観賞:** 奄美の澄んだ空気の中で見る星空は格別です。

---

**【3泊4日】奄美大島満喫モデルプラン**

**1日目：奄美到着、マングローブと郷土料理に舌鼓**

*   午前：奄美空港到着後、レンタカーを借りてホテルへ移動。
*   昼食：「奄美鶏飯と島料理の鳥しん」で、まずは奄美の代表的な郷土料理「鶏飯」を堪能。
*   午後：黒潮の森マングローブパークへ。カヌーに乗って、神秘的なマングローブの世界を探検。
*   夕食：「島の居酒屋むちゃかな」で、新鮮な魚介や島野菜を使った郷土料理と黒糖焼酎を楽しむ。

**2日目：絶景ビーチと滝、そして夕日**

*   午前：美しい海が広がる土盛海岸へ。シュノーケリングや海水浴を楽しむ（ウェットスーツ推奨）。
*   昼食：海岸近くのカフェや、奄美市街に戻って「あまみの魚たち」で海鮮ランチ。
*   午後：フナンギョの滝へ。迫力ある滝と豊かな緑に癒される。
*   夕方：大浜海浜公園へ移動。東シナ海に沈む美しい夕日を鑑賞。
*   夕食：地元の食材を使った料理が楽しめるお店で、奄美の味を堪能。

**3日目：原生林探検と島の文化体験**

*   午前：金作原原生林へ（認定エコツアーガイド同行推奨）。太古の森の神秘的な雰囲気を体験。
*   昼食：金作原ツアーの近く、または奄美市街に戻って「奄美薬膳つむぎ庵」で薬膳そばなどを味わう。
*   午後：大島紬村や、草木染め体験ができる工房などを訪れ、奄美の伝統文化に触れる。
*   夕食：「居酒屋ならびや」で、豊富な種類の黒糖焼酎と共に島唄を聞きながら、島料理を楽しむ。

**4日目：最後の海と空港へ**

*   午前：ホテル近くのビーチ（例：倉崎海岸）で、最後の海を満喫。
*   昼食：空港へ向かう途中で、気になるお店に立ち寄るか、空港内のレストランで軽食。
*   午後：奄美空港から帰路へ。

**その他のおすすめ**

*   **イベント:** 4月には様々なイベントが開催されている可能性があります。事前に奄美市のイベント情報をチェックしてみてください。
*   **ドライブ:** レンタカーを借りて、海岸線をドライブするだけでも気持ちが良いです。途中で見つけた絶景スポットに立ち寄るのもおすすめです。

このプランはあくまで一例です。興味のある場所や体験に合わせて、自由にアレンジしてくださいね。素敵な奄美大島旅行になりますように！
```

**== エージェントの処理の流れを表示 ==**  
LangGraphでは、エージェントの出力にそれまでのメッセージが全て含まれています。これをfor文で1つずつ表示してみます。

```
for message in response["messages"]:
    message.pretty_print()
```

処理の流れ

```
================================== Ai Message ==================================

4月頭の奄美大島旅行、楽しみですね！温暖な気候で自然を満喫できるベストシーズンです。以下に、おすすめのご飯、自然、そしてそれらを味わえる1日ごとの旅行計画をご提案します。

**奄美大島の4月について**

*   **気候:** 平均気温は約20〜23℃で、日中は半袖でも過ごせる暖かさですが、朝晩は肌寒く感じることもあります。薄手の羽織りものやストールがあると便利です。
*   **服装:** Tシャツ、長袖の羽織り、スニーカーが基本。雨具（折りたたみ傘や撥水ジャケット）も忘れずに。日差しが強くなるので、帽子、サングラス、日焼け止めも必須です。
*   **海:** 海開きは3月ですが、4月は水温が21℃前後になるため、ウェットスーツを着用すればシュノーケリングやダイビングが楽しめます。

**おすすめのご飯**

*   **鶏飯（けいはん）:** 奄美のソウルフード。ご飯に具材を乗せ、鶏がらスープをかけていただきます。
*   **油そうめん:** そうめん（またはうどん）に煮干し、人参、ニラなどを入れたあっさりとした一品。
*   **島料理:** 新鮮な魚介類を使った刺身や、豚の角煮、ヤギ汁（挑戦する価値あり！）、もずく天ぷらなど。
*   **黒糖焼酎:** 奄美ならではのお酒。様々な種類の蔵元があるので、飲み比べてみるのも楽しいでしょう。
*   **海鮮料理:** 新鮮な魚介類が豊富。特に「あまみの魚たち」や「島の居酒屋むちゃかな」などがおすすめです。
*   **郷土料理:** 「喜多八」や「鳥しん」などで、奄美の伝統的な味を堪能できます。

**おすすめの自然・アクティビティ**

*   **マングローブ:** 黒潮の森マングローブパークでのカヌー体験は、神秘的な自然を感じられます。
*   **滝:** フナンギョの滝、タンギョの滝、アランガチの滝など、迫力ある滝や癒される滝があります。
*   **ビーチ:** 土盛海岸、倉崎海岸、実久海岸など、美しいビーチがたくさんあります。シュノーケリングやダイビングも楽しめます。
*   **金作原原生林:** 手付かずの亜熱帯広葉樹林を散策できます（ガイドツアー推奨）。
*   **星空観賞:** 奄美の澄んだ空気の中で見る星空は格別です。

---

**【3泊4日】奄美大島満喫モデルプラン**

**1日目：奄美到着、マングローブと郷土料理に舌鼓**

*   午前：奄美空港到着後、レンタカーを借りてホテルへ移動。
*   昼食：「奄美鶏飯と島料理の鳥しん」で、まずは奄美の代表的な郷土料理「鶏飯」を堪能。
*   午後：黒潮の森マングローブパークへ。カヌーに乗って、神秘的なマングローブの世界を探検。
*   夕食：「島の居酒屋むちゃかな」で、新鮮な魚介や島野菜を使った郷土料理と黒糖焼酎を楽しむ。

**2日目：絶景ビーチと滝、そして夕日**

*   午前：美しい海が広がる土盛海岸へ。シュノーケリングや海水浴を楽しむ（ウェットスーツ推奨）。
*   昼食：海岸近くのカフェや、奄美市街に戻って「あまみの魚たち」で海鮮ランチ。
*   午後：フナンギョの滝へ。迫力ある滝と豊かな緑に癒される。
*   夕方：大浜海浜公園へ移動。東シナ海に沈む美しい夕日を鑑賞。
*   夕食：地元の食材を使った料理が楽しめるお店で、奄美の味を堪能。

**3日目：原生林探検と島の文化体験**

*   午前：金作原原生林へ（認定エコツアーガイド同行推奨）。太古の森の神秘的な雰囲気を体験。
*   昼食：金作原ツアーの近く、または奄美市街に戻って「奄美薬膳つむぎ庵」で薬膳そばなどを味わう。
*   午後：大島紬村や、草木染め体験ができる工房などを訪れ、奄美の伝統文化に触れる。
*   夕食：「居酒屋ならびや」で、豊富な種類の黒糖焼酎と共に島唄を聞きながら、島料理を楽しむ。

**4日目：最後の海と空港へ**

*   午前：ホテル近くのビーチ（例：倉崎海岸）で、最後の海を満喫。
*   昼食：空港へ向かう途中で、気になるお店に立ち寄るか、空港内のレストランで軽食。
*   午後：奄美空港から帰路へ。

**その他のおすすめ**

*   **イベント:** 4月には様々なイベントが開催されている可能性があります。事前に奄美市のイベント情報をチェックしてみてください。
*   **ドライブ:** レンタカーを借りて、海岸線をドライブするだけでも気持ちが良いです。途中で見つけた絶景スポットに立ち寄るのもおすすめです。

このプランはあくまで一例です。興味のある場所や体験に合わせて、自由にアレンジしてくださいね。素敵な奄美大島旅行になりますように！
```

おすすめの料理や観光スポットをしっかり検索していることが分かりますね！

# まとめ

今回は、AIエージェントの基本的なパターンであるReActをLangGraphを用いて実装してみました！  
やはり、LangGraphを用いることで、直感的に簡単に実装できますね。  
今後、他の実装パターンもいろいろ試してみて記事にするので、お楽しみに！
