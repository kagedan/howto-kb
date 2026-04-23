---
id: "2026-03-19-adk-ついにグラフ構造ワークフローが来たadk-20-αで導入されたworkflow-runtim-01"
title: "[ADK] ついにグラフ構造ワークフローが来た！ADK 2.0 αで導入されたWorkflow RuntimeとTask APIを最速で触る"
url: "https://zenn.dev/soundtricker/articles/24af4acb2c4514"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "zenn"]
date_published: "2026-03-19"
date_collected: "2026-03-20"
summary_by: "auto-rss"
---

![](https://static.zenn.studio/user-upload/184404d488be-20260319.png)

こんにちは、サントリーこと大橋です。

前回の記事から少し間が空いてしまいました。2025年末以降、公私共にバタバタしておりADKのキャッチアップ記事が書けていなかったことをお詫びします。ゴメンネ

さて、昨日(2026/03/18)に開催された Google Agent Development Kit (ADK) の Community Call にて、ついに **ADK v2.0** の Early Release (Alpha版) が発表されました！

これまでの ADK の良さを引き継ぎつつ、よりAIワークフローが書きやすくなる機能が追加されています。今回はこのアルファ版を実際に触りながら、何が変わったのか、どのような新機能が追加されたのかを書いていきます。

### 対象

* ADK を触ったことがある方
* これから AI エージェントをコードベースで開発したい方
* LangGraph 等の Graph ベースのフレームワークを触っており、ADK の進化が気になる方

---

## ADK の課題: ワークフロー制御の煩雑さ

これまで ADK で複数のエージェントを組み合わせた「ワークフロー」を構築しようとすると、主に以下の 4 つの方法がありました。

1. **プロンプト(Instruction)による制御**: LLM に「次はこのエージェントを呼んで」と指示する。
2. **Workflow Agent**: `SequentialAgent`, `ParallelAgent`, `LoopAgent` などを組み合わせる。
3. **BaseAgent の継承**: 独自ロジックを Python コードでゴリゴリ書く。
4. **Callback による制御**: 特定のタイミングで処理を割り込ませる。

しかし、これらにはそれぞれデメリットがありました。

* **不確実性**: プロンプトベースは LLM の機嫌に左右され、決定論的なフローが作りにくい。(「確実にやる」ではなく、確率的になる 「ではホゲホゲAgentに依頼します」と言いながらやらないことがある)ツライ
* **柔軟性の欠如**: `SequentialAgent` 等は単純な並びには強いが、「条件による分岐（ルーティング）」をそれ単体で表現できない。ツライ
* **実装コスト**: 小さなルーティングのためだけに `BaseAgent` を継承してクラスを作るのは、ボイラープレートコードが増えて面倒。ツライ
* **可読性**: Callback による制御は本来の用途とは異なるため、コードがスパゲッティ化しやすい。ツライ

世の中の AI エージェントフレームワーク（特に **LangGraph** など）を見ると、処理を「ノード」と「エッジ」で表現する **グラフ構造** を採用することで、これらの課題を解決しています。ADK 2.0 では、まさにこの「グラフ構造の制御」をネイティブに取り込んだ形になります。

---

## What's new in ADK v2

ADK 2.0 Alpha の目玉は、大きく分けて以下の 2つです。

### 1. Workflow Runtime (Graph-based Engine)

これまでの `Workflow Agent` が進化し、**決定論的な グラフ実行エンジン**となりました。  
ルーティング（条件分岐）、ファンアウト/ファンイン、ループ、リトライ、ステート管理、Human-in-the-Loop などを、ノードとエッジの定義だけで記述できるようになります。

### 2. Task API (Structured Delegation)

サブエージェントに対するタスクの「移譲（Delegation）」をより構造化するための新しい API モードです。  
これまでの `transfer_to_agent` は比較的ルーズな移譲でしたが、Task API では明確な **Input/Output Schema** を持たせることができ、複数ターンのタスク実行や、タスクエージェントをワークフローの一つのノードとして扱うことが容易になります。

リポジトリに v2 ブランチがあるのでコードはそこから閲覧できます。

<https://github.com/google/adk-python/tree/release/v2.0.0-alpha.1>

---

## 実際に触ってみる

さっそく、新しくなった ADK を動かしてみましょう。

### 1. ADK v2 のインストール

まず、今回のADK v2 を試すためのプロジェクトを作成します。

```
mkdir adk-v2-demo
cd adk-v2-demo
```

個人的にツールのバージョン管理には `mise` を利用しているので `mise` を利用して `python` や `uv` を整備します。

```
# miseのセットアップと uvのセットアップ
mise use python@3.12
mise use uv@latest
uv python pin 3.12
uv init --app .
```

次に`uv` でADK v2をインストールします。　  
ADK v2 はアルファ版のため、明示的なバージョン指定が必要です。

```
# ADK v2.0 Alpha1をインストール
uv add "google-adk==2.0.0a1"
```

これでADK v2 を利用する準備は完了です。

### 2. Workflow Runtime を利用したルーティング

公式サンプルのルーティング処理を日本語化して見てみましょう。  
入力内容が「質問」か「声明」か「その他」かを判断して、適切なエージェントに振り分けるフローです。

まず`adk create`を利用してAgentを作成します。

```
uv run adk create workflow_route

Choose a model for the root agent:
1. gemini-2.5-flash
2. Other models (fill later)
Choose model (1, 2): 2

Please see below guide to configure other models:
https://google.github.io/adk-docs/agents/models

Agent created in /path/to/adk-v2-demo/workflow_route:
- .env
- __init__.py
- agent.py
```

次に作成されたAgentを修正します。

workflow\_route/agent.py

```
from typing import Literal
from google.adk import Agent, Event, Workflow
from pydantic import BaseModel

# 1. データの構造を定義
class InputCategory(BaseModel):
    category: Literal["question", "statement", "other"]

# 2. 前処理ノード（関数でも書ける！）
def process_input(node_input: str):
    return Event(state={"input": node_input})

# 3. 分類を行うAgent
classify_input = Agent(
    name="classify_input",
    instruction="入力された内容を 'question', 'statement', 'other' のいずれかに分類してください: {input}",
    output_schema=InputCategory,
    output_key="category",
)

# 4. ルーティングロジック
def route_on_category(category: InputCategory):
    yield Event(route=category.category)

# 5. 各処理Agent
answer_question = Agent(name="answer_question", instruction="質問に回答してください: {input}")
comment_on_statement = Agent(name="comment_on_statement", instruction="声明に対してコメントしてください: {input}")

def handle_other():
    yield Event(message="すみません、質問か声明以外は受け付けられません。")

# 6. Workflowの定義（ここがv2の新機能）
root_agent = Workflow(
    name="root_workflow",
    edges=[
        # STARTから順に実行されるパイプラインをリスト形式で定義
        ("START", process_input, classify_input, route_on_category),
        (
            route_on_category,
            {
                "question": answer_question,
                "statement": comment_on_statement,
                "other": handle_other,
            },
        ),
    ],
)
```

!

この `edges` 定義において、`("START", process_input, classify_input, route_on_category)` のようにタプル形式でノードを連結できるのは ADK 2.0 特有の非常に強力なシンタックスです。これは「順番に実行されるパイプライン」を意味しており、グラフ構造を意識しすぎることなく、直感的にフローを記述できるようになっています。

次に`.env`を修正します。いい感じで値を設定してください。

workflow\_route/.env

```
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=DUMMY
```

では`adk web`を利用してAgentを動かしてみましょう。

画面を開いてみると、これまでの`adk web`にいくつか機能が追加されているのが分かります。  
例えば今回の修正で`adk web` に `Agent Structure Graph` を表示する機能が追加されました。

![](https://static.zenn.studio/user-upload/e00238abb49f-20260319.png)

ではAgentに質問してみましょう。

![](https://static.zenn.studio/user-upload/80715a902a36-20260319.png)

次に「宣言」をしてみましょう。

![](https://static.zenn.studio/user-upload/16a841a110db-20260319.png)

最後に「質問」でも「宣言」でもない、挨拶をしてみます。

![](https://static.zenn.studio/user-upload/a4ecf7d5a931-20260319.png)

それぞれどのAgentが回答しているかはチャットウィンドウ左端の◯をマウスオーバーすると表示されます。

![](https://static.zenn.studio/user-upload/12c6d1737fd6-20260319.png)

ちゃんとそれぞれの `edge` にルーティングできていますね。

#### v1 との比較

以前の ADK でこれと同じことをやろうとすると、`BaseAgent` を継承したクラスの中で `if category == "question": ...` のようにコードを書くか、LLM の `transfer_to_agent` に頼る必要がありました。  
v2 では `edges` の定義として **「A の後に B を実行する」「結果が X なら C へ、Y なら D へ行く」** という構造がコードから切り離されて可視化されているのが分かります。

#### LangGraph との比較

グラフ構造ワークフローのフレームワークといえば **LangGraph** が有名ですが、ADK v2 はより「ADK らしさ」を保ったまま進化しています。  
例えば、LangGraph でいう `State` の定義と更新が、ADK では `Event(state=...)` や Pydantic モデルをそのまま渡すことで、より直感的かつ型安全に扱えるようになっています。複雑な StateGraph クラスを構築する手間がなく、エージェント開発の延長線上で自然にグラフを組めるのが大きなメリットだと感じました。

### 3. Task API による構造化された移譲

次にTask APIです。  
Task API を使うと、特定の Agent を「構造化されたタスク実行者」として定義できます。

Workflowと同じ様に`adk create`を利用してagentを作成します。

```
uv run adk create task_api

Choose a model for the root agent:
1. gemini-2.5-flash
2. Other models (fill later)
Choose model (1, 2): 2

Please see below guide to configure other models:
https://google.github.io/adk-docs/agents/models

Agent created in /path/to/adk-v2-demo/task_api:
- .env
- __init__.py
- agent.py
```

次に作成されたAgentを修正します。

task\_api/agent.py

```
from google.adk import Agent, Event, Workflow
from google.adk.workflow import DEFAULT_ROUTE
from pydantic import BaseModel, Field

# 1. 出力スキーマの定義
class PatientIdentity(BaseModel):
    """受付エージェントの出力スキーマ"""
    name: str = Field(description="患者のフルネーム")
    phone_number: str = Field(description="患者の電話番号")

# 2. Taskモードのエージェント
# mode="task" を指定すると、スキーマが埋まるまでユーザーと多ターン対話を続けます
intake_agent = Agent(
    name="intake_agent",
    mode="task",
    output_schema=PatientIdentity,
    instruction="""
あなたは医療機関の受付アシスタントです。
ユーザーからフルネームと電話番号を聞き出して、PatientIdentityを完成させてください。
情報を捏造しないでください。両方の情報が得られたら、タスクを完了してください。
""",
)

# 3. 注文を検索するノード（通常のPython関数）
def find_orders(node_input: PatientIdentity):
    """
    名前が "サントリー" の場合のみ注文が見つかったと仮定するモック処理。
    見つからない場合は 'retry' ルートへ、見つかった場合は 'DEFAULT_ROUTE' へ。
    """
    if node_input.name.lower() != "サントリー":
        yield Event(
            message=f"{node_input.name} 様の記録が見つかりませんでした。もう一度お伺いします。",
            route="retry",
        )
    else:
        # 見つかった注文を状態（state）に保存
        yield Event(state={"orders": ["血液検査 (CBC)", "脂質パネル検査", "肥満度検査"]})

# 4. 準備指示を生成するエージェント（デフォルトのSingle Turnモード）
# Workflow内では、前のノードからの出力を受け取ったり、stateの値を参照したりできます
generate_instruction = Agent(
    name="generate_instruction",
    instruction="""
以下の検査項目に基づいて、患者向けの簡潔な受診準備指示（絶食の必要性など）を作成してください。
{orders}
""",
)

# 5. 最終的な回答を組み立てる関数ノード
def send_message(orders: list[str], node_input: str):
    orders_str = "\n- ".join(orders)
    yield Event(message=f"""
良いお知らせです！以下の注文が見つかりました：
- {orders_str}

受診にあたっては、以下の指示に従ってください：

{node_input}
""")

# 6. Workflowの定義
root_agent = Workflow(
    name="task_in_workflow",
    edges=[
        # STARTから受付エージェントへ、その後検索処理へ
        ("START", intake_agent, find_orders),
        (
            find_orders,
            {
                # 失敗時は受付に戻る、成功時は指示生成へ
                "retry": intake_agent, 
                DEFAULT_ROUTE: generate_instruction
            },
        ),
        # 指示生成が終わったらメッセージ送信へ
        (generate_instruction, send_message),
    ],
)
```

次に `.env` を修正します。

task\_api/.env

```
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=DUMMY
```

では実際に`adk web`を利用して動かしてみましょう。

まず最初にユーザーが質問すると`intake_agent`が返答をしています。  
その後、ユーザーがフルネームと電話番号を伝えるまでは`intake_agent`が処理を担当しています。

![](https://static.zenn.studio/user-upload/e9d7aa2171c2-20260319.png)

`intake_agent`はユーザーがフルネームと電話番号を聞いて`PatientIdentity`のデータが埋まると、  
`finish_task`ツールを呼び出し、処理の終了を宣言します。  
ここで登場する `finish_task` は、Task APIで自動で付与される専用ツールです。LLMが `output_schema` に定義した情報を全て収集したと判断した際、自律的にこのツールを呼び出してワークフローを次へ進めます。開発者が『情報が揃ったか？』というバリデーションコードを書く必要がないのが、このAPIの真骨頂です。

![](https://static.zenn.studio/user-upload/81ae9c9942a9-20260319.png)  
するとWorkflow Runtime(今回は `task_in_workflow`というワークフロー)は、  
次のedgeである`find_orders`を呼び出します。

![](https://static.zenn.studio/user-upload/33b97a50f2e7-20260319.png)

`find_orders`では`intake_agent`の結果(=`node_input`)である`PatientIdentity`を利用して、  
名前から注文を検索します。

検索結果が見つからない場合は `Event(route='retry')`を設定して再度`intake_agent`へ処理を戻します。  
成功している場合は、`route`は未設定にして`DEFAULT_ROUTE`(分岐条件に当てはまらなかった場合のデフォルト)に遷移するようにし、次の`generate_instruction`へ処理を流します。  
`generate_instruction`では注文から検査の注意点を作成します。

![](https://static.zenn.studio/user-upload/e2f340e41ad4-20260319.png)

そして最後にメッセージをフォーマットするための`send_message`を呼び出します。

![](https://static.zenn.studio/user-upload/478076e0586f-20260319.png)

一見するとなかなか面倒そうなフローに見えますが、Workflowを利用すると以下の部分でうまくルーティングを表しているのがわかります。

```
root_agent = Workflow(
    name="task_in_workflow",
    edges=[
        # STARTから受付エージェントへ、その後検索処理へ
        ("START", intake_agent, find_orders),
        (
            find_orders,
            {
                # 失敗時は受付に戻る、成功時は指示生成へ
                "retry": intake_agent, 
                DEFAULT_ROUTE: generate_instruction
            },
        ),
        # 指示生成が終わったらメッセージ送信へ
        (generate_instruction, send_message),
    ],
)
```

![](https://static.zenn.studio/user-upload/17b0fa4e45ea-20260319.png)

また今回のTask APIでは `intake_agent`が `task`モード `generate_instruction` が `single_turn`モードで動いています。  
`task`モードを利用することで、**今までCallbackなどのコードを用いて情報の充足状況を確認していましたが、その部分が不要になりました。**  
これにより `intake_agent`は名前と電話番号がわかるまで、つまり`PatientIdentity`のデータが埋まるまで、マルチターンでユーザーに問い合わせを続けています。  
それに対して`generate_instruction`では単発のタスクとして指示作成のみを行っています。

これまでの `transfer_to_agent` との違いは、**「会話の流れでなんとなく移譲する」** のではなく、**「特定のインターフェース（Task）を持ったユニットとして、明確に仕事を依頼する」** という点にあります。

特に `mode="task"` を使うことで、エージェントは「必要な情報が揃うまでユーザーと勝手に喋っておいてね、終わったら結果を構造化データで返してね」という制御が可能になります。これにより、メインのワークフローロジックを汚さずに、複雑なマルチエージェントのやり取りをグラフの一つのノードとしてカプセル化できるわけです。  
今までこれをやろうと思うと一つのAgentでは表現することができませんでした。

---

## まとめ

今回は速報として、ADK 2.0 Alpha の新機能について紹介しました。

* **Workflow Runtime**: Graph ベースのエンジン導入により、複雑なルーティングが劇的に書きやすくなった。
* **Task API**: エージェント間の移譲が構造化され、システムとしての堅牢性が向上した。

まだアルファ版のため、API の変更や追加機能があるとは思いますが、ADK v2ではこれまでの「コードファースト」な良さを活かしつつ、LangGraph のような柔軟な制御を手に入れました。  
今後もADK v2を追っていきたいと思います。

---

## お知らせ/宣伝

ADK 開発者が集う日本語の Discord コミュニティがあります。ADK に関する情報交換や議論に興味がある方は、ぜひご参加ください！

<https://discord.gg/BKpGRzjtqZ>
