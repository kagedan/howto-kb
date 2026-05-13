---
id: "2026-05-12-context-engineeringとは何かプロンプトの次に来るllmへの情報設計という技術202-01"
title: "Context Engineeringとは何か？──プロンプトの次に来る、LLMへの情報設計という技術【2026】"
url: "https://zenn.dev/karaagedesu/articles/a7d58f2f197aa3"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "prompt-engineering", "API", "LLM", "OpenAI", "zenn"]
date_published: "2026-05-12"
date_collected: "2026-05-13"
summary_by: "auto-rss"
query: ""
---

## はじめに

「プロンプトをどれだけ工夫しても、精度が頭打ちになる」「コンテキストウィンドウが広くなったからと大量のドキュメントを詰め込んだら、むしろ重要な指示を無視された」

こういった壁に直面しているなら、必要なのはプロンプトの改善ではなく、**Context Engineering（コンテキストエンジニアリング）** という視点の転換かもしれません。

2025年6月、ShopifyのCEO Tobi Lutkeがこんな言葉を残しました。

> 「Context engineeringはprompt engineeringよりも、このコアスキルを正確に表している」

これを受けてAndrej Karpathy（元OpenAI共同創業者、元TeslaのAIディレクター）も定義を加えました。

> 「あらゆる産業レベルのLLMアプリにおいて、Context Engineeringとは、最適な次のアクションを得るために、コンテキストウィンドウに適切な情報を精巧に詰め込むアートとサイエンスだ」

Anthropicも公式ブログでContext EngineeringをPrompt Engineeringの「自然な進化」と位置付けており、2026年現在は**AIエージェント開発における実務標準**として定着しつつあります。

本記事では、Context Engineeringの概念から実践テクニックまでをまとめます。

---

## Prompt EngineeringとContext Engineeringの違い

一言でいうと、

* **Prompt Engineering**：「LLMに何をさせるか（What）」という指示の最適化
* **Context Engineering**：「LLMが何を知っている状態でタスクを行うか（Where & How）」という情報供給の設計

です。

プロンプトエンジニアリングは「より良い指示文を書く技術」です。対して、Context Engineeringは、LLMに渡すシステムプロンプト・会話履歴・RAGで取得した文書・ツール呼び出し結果・メモリなど、**コンテキストウィンドウ全体を設計する技術**です。

```
プロンプトエンジニアリング
  ユーザー → [指示文] → LLM → 回答

Context Engineering
  ユーザー → [システムプロンプト
              + 会話履歴（圧縮済み）
              + RAG取得文書（選別済み）
              + ツール呼び出し結果
              + 外部メモリからの関連情報
              + ユーザーの指示] → LLM → 回答
```

プロンプトが「単一の静的なテキスト文字列」であるのに対し、コンテキストは「動的に構造化された情報コンポーネントの集合」です。

:::

Context Engineeringは、プロンプトエンジニアリングの否定ではなく拡張です。Few-shot・Chain-of-Thought・RAG・MCPは、すべてContext Engineeringの構成要素と捉えることができます。

:::

---

## なぜ今重要なのか：Context Rotの問題

コンテキストウィンドウが広がったからといって、「全部詰め込めばいい」は間違いです。

**Context Rot（コンテキスト腐食）** と呼ばれる現象があります。コンテキスト内のトークン数が増えるにつれて、モデルが情報を正確に想起・活用する能力が逓減していくという問題です。

原因はTransformerアーキテクチャのSelf-Attentionにあります。計算量はトークン数のn²に比例するため、コンテキストが長くなるほど重要な情報が埋もれやすくなります。

> 「最小の高シグナルなトークン集合を見つけ、期待される結果の可能性を最大化する。」

これがContext Engineeringの本質的な目標です。情報は多ければいいのではなく、**ノイズを減らしシグナルを最大化する**設計が求められます。

---

## コンテキストウィンドウの構造

LLMが受け取るコンテキストは、大きく以下の要素で構成されます。

```
┌─────────────────────────────┐
│ System Prompt               │ ← 役割・制約・指示
├─────────────────────────────┤
│ Memory（外部メモリ）         │ ← 過去セッションの記憶
├─────────────────────────────┤
│ Retrieved Context（RAG）    │ ← 検索で取得した関連情報
├─────────────────────────────┤
│ Tool Results                │ ← API・DB呼び出し結果
├─────────────────────────────┤
│ Conversation History        │ ← 会話履歴（圧縮済み）
├─────────────────────────────┤
│ User Input                  │ ← 今回のユーザーの入力
└─────────────────────────────┘
```

Context Engineeringとは、この各レイヤーをどう設計・最適化するかを考える技術です。

---

## 4つの戦略フレームワーク

コンテキストを管理する戦略は4つに分類できます。

### 1. Write（書き出す）

処理中の中間結果や状態を、コンテキストウィンドウの外（ファイル・DB・メモリストア）に書き出す戦略です。

エージェントが長時間タスクを遂行するとき、すべての中間情報をコンテキストに保持し続けるとすぐにウィンドウが溢れます。重要な状態だけを構造化して外部に保存し、必要なときに読み込む設計が有効です。

```
# LangGraphのチェックポイントがこの典型例
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
# 処理の中間状態が自動的に保存・復元される
```

### 2. Select（選択して戻す）

必要なときに必要な情報だけをコンテキストに注入する戦略です。RAGがその代表例です。

重要なのは「詰め込む」ではなく「選ぶ」ことです。検索精度を上げることで、不要なノイズをコンテキストから排除できます。

```
# 関連度スコアで上位だけを取得する
retriever = vectorstore.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"score_threshold": 0.75, "k": 3}  # 閾値未満は除外
)
```

### 3. Compress（圧縮する）

コンテキストの情報量を保ちながらトークン数を削減する戦略です。

会話履歴が長くなったとき、古い履歴をそのまま保持するのではなく、LLMに要約させてから保存することでトークンを節約できます。

```
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

def compress_history(messages: list, llm) -> str:
    """会話履歴を要約して圧縮する"""
    history_text = "\n".join([
        f"{m.type}: {m.content}" for m in messages
    ])
    
    summary = llm.invoke([
        SystemMessage(content="以下の会話履歴を3〜5行で要約してください。重要な決定事項や合意点を優先してください。"),
        HumanMessage(content=history_text)
    ])
    return summary.content

# 会話が20ターンを超えたら要約する
if len(messages) > 20:
    compressed = compress_history(messages[:-5], llm)  # 直近5件は保持
    messages = [SystemMessage(content=f"これまでの要約: {compressed}")] + messages[-5:]
```

### 4. Isolate（隔離する）

処理を独立したサブコンテキストに分離する戦略です。マルチエージェントシステムで特に有効です。

複雑なタスクをサブタスクに分割し、それぞれを独立したエージェント（＝独立したコンテキスト）で処理することで、各エージェントのコンテキストをクリーンに保てます。

```
# 各エージェントが独立したコンテキストを持つ構成例（LangGraph）
from langgraph.graph import StateGraph

# リサーチエージェント（自分のコンテキストのみ持つ）
research_graph = StateGraph(ResearchState)

# ライティングエージェント（自分のコンテキストのみ持つ）
writing_graph = StateGraph(WritingState)

# 親グラフがサブグラフとして呼び出す
parent_graph.add_node("research", research_graph.compile())
parent_graph.add_node("writing", writing_graph.compile())
```

---

## 実践テクニック

### XMLタグで構造化する

Claudeをはじめ多くのLLMは、XMLタグで区切られた情報をより正確に認識します。自然言語の見出しよりも情報の境界が明確になります。

```
system_prompt = """
<role>
あなたは材料科学の専門家です。
</role>

<rules>
- 回答は必ず日本語で行う
- 根拠のない推測は避ける
- 論文・データに基づいた回答を優先する
</rules>

<output_format>
結論を最初に述べてから、根拠を説明してください。
</output_format>
"""
```

### 情報を重要度順に配置する

LLMは先頭と末尾の情報を最も注意深く処理します（Lost in the Middle問題）。最も重要な情報は先頭か末尾に置くのが基本です。

```
# 悪い例：重要な指示が真ん中に埋まる
context = f"""
{大量の背景情報}
【重要：必ずJSON形式で返すこと】  ← 埋もれやすい
{さらに情報}
"""

# 良い例：重要な指示を先頭と末尾に配置
context = f"""
【出力形式：必ずJSON形式で返すこと】

{背景情報}

{参照情報}

再確認：出力はJSON形式で返してください。
"""
```

### Prompt Cachingでコストを削減する

AnthropicのAPIにはPrompt Caching機能があり、同一のプレフィックス（システムプロンプトなど）を繰り返し送る際のコストを最大90%削減できます。

```
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": "あなたは材料科学の専門家です。以下のドキュメントを参考に回答してください。",
        },
        {
            "type": "text",
            "text": long_document,  # 繰り返し使う長いドキュメント
            "cache_control": {"type": "ephemeral"}  # ← キャッシュ指定
        }
    ],
    messages=[{"role": "user", "content": user_question}]
)
```

---

## AIエージェントにおけるContext Engineeringの重要性

単発のLLM呼び出しでは、Context Engineeringの重要性は限定的です。しかしエージェントになると話が変わります。

エージェントは複数のツールを呼び出し、複数のステップをまたいで長時間タスクを遂行します。その過程でコンテキストは膨大になりやすく、適切に管理しないと以下の問題が起きます。

* コンテキストウィンドウの超過（処理が止まる）
* 不要な情報がノイズになりエージェントが迷走する
* コストとレイテンシの増大

今回ツイートで紹介したARISの論文でも、**「エージェントの性能はモデルの重みだけでなく、何をどう記憶・検索・提示するか（ハーネス）で決まる」** と明言しています。これはまさにContext Engineeringの核心を突いた視点です。

---

## まとめ

| 項目 | 内容 |
| --- | --- |
| 何か | LLMへの情報供給全体を設計する技術 |
| Promptとの違い | 指示文の最適化 → 情報システム全体の設計 |
| 中心的な問題 | Context Rot（情報が増えるほど精度が下がる） |
| 4つの戦略 | Write / Select / Compress / Isolate |
| 主な実践手法 | XML構造化・情報配置・Prompt Caching・RAG選別・履歴圧縮 |
| 重要性が高い場面 | AIエージェント・長時間タスク・マルチエージェント |

プロンプトを磨くことに限界を感じたら、次は「LLMに渡す情報全体をどう設計するか」という視点に移行してみてください。RAG・LangGraph・MCP──これまで紹介してきた技術はすべて、Context Engineeringという大きな枠組みの中でつながっています。

**参考リンク**
