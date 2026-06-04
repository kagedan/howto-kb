---
id: "2026-06-03-langgraphを学んでみたら株価を自動チェックするaiアプリが作れた話-01"
title: "LangGraphを学んでみたら、株価を自動チェックするAIアプリが作れた話"
url: "https://zenn.dev/ise_ai_enabler/articles/f5853b8e06f039"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "LLM", "Python", "JavaScript", "zenn"]
date_published: "2026-06-03"
date_collected: "2026-06-04"
summary_by: "auto-rss"
query: ""
---

## はじめに

仕事でチャットボット開発に関わる機会があり、LangGraphという名前をよく耳にするようになりました。  
業務で使う可能性もあったので、「どうせなら今のうちに触っておこう」と思い立ち、  
学習を始めました。結果として、株価を自動取得して動向を分析するアプリまで作ることができたので、学んだことをまとめます。

## 環境

| 項目 | 内容 |
| --- | --- |
| LangGraph | 最新版（2025年時点） |
| LangChain | LangGraph依存バージョン |
| Python | 3.11系 |
| UI | Gradio |
| デバッグ | LangSmith |
| ブラウザ操作 | Playwright |
| 検索 | SERP API |
| メモリ | MemorySaver / SQLite |

## LangGraphって何？

まず最初に混乱したのが「LangGraphって結局どれのこと？」という点でした。  
その前に、そもそも LangGraph が何者なのかを整理しておきます。

LangGraph は、AIエージェントのワークフローを「グラフ構造」で設計するPythonフレームワークです。

「エージェント」というのは、単に質問に答えるだけでなく、  
ツールを使ったり、結果を評価したり、必要なら再試行したりと、  
自律的にタスクをこなすAIのことです。

通常のLLM（大規模言語モデル）の呼び出しは「入力 → 出力」の一方通行ですが、  
LangGraphを使うと処理の流れを分岐させたり、ループさせたり、複数の処理を組み合わせたりできます。  
状態（State）を中心に処理を設計するのが特徴で、「何のデータを持ちながら、どう処理を進めるか」を  
コードで明示的に定義できる点が強みです。

LangChainというライブラリをベースに作られており、  
LangChainが提供する各種ツールやLLMのラッパーとも組み合わせて使えます。

また、LangGraph という名前には3つの構成要素があります。

| 名前 | 役割 |
| --- | --- |
| LangGraph | ロジックを書くフレームワーク本体 |
| LangGraph Studio | ビジュアルで設計できるUI |
| LangGraph Platform | デプロイ・運用のホスティング基盤 |

この記事では主にフレームワーク本体の話をします。

## 中核の4概念：State・Node・Edge・Graph

LangGraphを理解するうえで、最初に押さえておくべき概念が4つあります。  
最初はとっつきにくかったのですが、一つひとつは実はシンプルです。

### State（状態）

アプリ全体で共有される「データの箱」です。  
すべてのノードがこの状態を受け取り、新しい状態を返します。

```
class State(BaseModel):
    messages: Annotated[list, add_messages]
```

ここで登場する add\_messages は Reducer と呼ばれるもので、  
複数のノードが同時にデータを更新しても安全に統合するための関数です。  
「上書き」ではなく「追加」にすることで、会話履歴が消えずに積み上がっていきます。

### Node（ノード）

Stateを受け取って、新しいStateを返すPython関数です。  
LLMの呼び出しも、API呼び出しも、すべてノードとして定義します。

```
  def my_node(state):
      # 何か処理する
      return {"messages": [response]}
```

### Edge（エッジ）

「次にどのノードに進むか」を決めるロジックです。  
単純に次のノードへ進む場合と、条件によって分岐する場合があります。

### Graph（グラフ）

ノードとエッジをまとめた「処理フロー全体」です。  
定義してからコンパイルして実行する、という2段階の構造になっています。

```
result = graph.invoke(initial_state)
```

# CrewAIと何が違うの？

以前 CrewAI も触ったことがあるので、その違いが気になっていました。  
一言で言うとこうです。

▎ CrewAI：「誰がやるか」を設計する（人間的なモデル）  
▎ LangGraph：「どう動くか」を設計する（プログラム的なモデル）

CrewAIはエージェントをチームメンバーとして定義する感覚に近く、  
LangGraphは関数とデータフローを組み合わせる感覚です。

デバッグのしやすさという点ではLangGraphに軍配が上がります。  
CrewAIではYAMLの書き方ひとつでエラーが出たり、原因がわからないまま詰まることがありました。  
LangGraphは状態（State）が常に明示的なので、どこで何が起きているか追いやすかったです。

チェックポイントで会話履歴を保持する

LangGraphはデフォルトでは会話をまたいだ記憶を持ちません。  
最初に「名前を覚えてくれない」という現象で少し詰まりました。

解決策は チェックポイント の利用です。

```
  from langgraph.checkpoint.sqlite import SqliteSaver

  memory = SqliteSaver("memory.db")
  graph = builder.compile(checkpointer=memory)
```

# thread\_idで会話を識別する

{"thread\_id": "user\_001"}}

```
result = graph.invoke(state, config=config)
```

thread\_id はユーザーを識別するキーのようなもので、  
これを指定することで会話をまたいだ状態の保持が実現できます。  
SQLiteを使えばカーネル再起動後も記憶が残り、一気に実用的になりました。

Toolを追加して現実世界とつなぐ

LangGraph単体はただの処理フローですが、ツールを追加することで外の世界と接続できます。

```
  from langchain.agents import Tool

  search_tool = Tool(
      name="search",
      func=serper.run,
      description="Web検索を行う"
  )

  llm_with_tools = llm.bind_tools([search_tool])
```

bind\_tools でLLMにツールの存在を教えることで、  
LLMが「このツールを使うべき」と判断した場合に自動で呼び出してくれます。

今回は以下のツールを組み合わせました。

* SERP API：Web検索
* Playwright：ブラウザ操作（JavaScriptが必要なページにも対応）
* Push通知：結果をスマートフォンへ送信
* Python REPL：コード実行

# 実際に作ったもの：株価チェックアプリ

これらの要素を組み合わせて、株価を自動取得して動向を分析するアプリを作りました。

* 指定した銘柄の最新株価をWeb上から取得
* 価格推移をもとに動向を分析
* 結果をプッシュ通知で受け取る

毎回ブラウザを開いて確認していた作業が自動化され、  
チェックにかかる時間が大幅に減りました。  
さらに、単純な価格取得だけでなく「利益が出やすいタイミング」の判断もエージェントに任せられる点は、  
自分で作っておきながら驚きました。

### WorkerとEvaluatorのループ（発展）

より精度の高い出力を得たい場合は、WorkerとEvaluatorを分けるパターンが有効です。

```
  Worker（作業する）
    ↓
  Evaluator（評価する）
    ↓ NGなら
  Worker（やり直す）
```

EvaluatorにはLLMの構造化出力を使い、成功したかどうかをプログラムで判定できるようにします。

```
  class EvaluatorOutput(BaseModel):
      feedback: str
      success_criteria_met: bool
      user_input_needed: bool
```

この構造にすることで、AIが自分の出力を自己評価しながら改善を繰り返す仕組みが作れます。

### ハマったところ

想定通りに動かないことが多かったというのが正直な感想です。  
特に最初のうちは、状態管理の設計が理解できておらず、  
「なぜ会話が途切れるのか」「なぜツールが呼ばれないのか」で詰まりました。

解決策はシンプルで、実際に手を動かし続けることでした。  
LangSmithのログを見ながら「どの処理でどの値が渡っているか」を確認することで、  
少しずつ中身が見えてきました。LangSmithは導入して本当によかったです。

# まとめ

* LangGraphはState・Node・Edge・Graphの4概念を理解すれば、あとはそれを組み合わせるだけ
* 状態管理はデフォルトで自動にはならない。チェックポイントを使って自分で設計する必要がある
* ツールを組み合わせることで「AIが現実世界を操作するアプリ」が作れる

詰まることも多いですが、一つひとつの仕組みが明示的なので  
「なぜそう動くのか」が理解しやすい点がLangGraphの好きなところです。  
業務でLangGraphを触ることになった方や、これから始めようか迷っている方の参考になれば幸いです！

# 参考

---
