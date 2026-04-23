---
id: "2026-03-23-ragの次は検索ではなく行動であるsemantic-kernelで理解するaiエージェントの設計思想-01"
title: "RAGの次は検索ではなく行動である｜Semantic Kernelで理解するAIエージェントの設計思想"
url: "https://zenn.dev/startspace/articles/402e14cb2993e4"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-03-23"
date_collected: "2026-03-24"
summary_by: "auto-rss"
---

# 導入｜RAGの先で、私は何に行き着いたのか

RAGの精度改善には、まだ多くの余地があります。

Chunking、検索戦略、Rerank、評価...やれることはまだあるし、一般的に、Chunkingや検索戦略、Rerankなどの改善が行われています。

しかし、ある地点で違和感にぶつかります。

それは、「これで、本当に業務は終わるのか？」という問いです。

RAGによって、社内ナレッジの検索は劇的に速くなりました。チャットボットに組み込めば、問い合わせ対応も自動化できます。

確かに効率化はできています。

しかしそれは、人の仕事を置き換えているのではなく、人の仕事を少し楽にしているだけに過ぎませんでした。

ホワイトカラーの業務は、「正しい情報を得ること」で終わるわけではありません。

判断し、処理し、実行することで、初めて仕事が終わります。

RAGは、正しい答えにたどり着くための優れた技術でした。

しかしそれは、仕事を終わらせる技術ではありませんでした。

# RAGの限界｜それは「検索最適化」という構造にある

RAGは非常に強力な技術ですが、その構造自体に限界があります。

それは、「1クエリ → 1レスポンス」という静的な処理構造に閉じていることです。

RAGは、ユーザーの質問をEmbeddingし、ベクトルDBで関連情報を検索し、それをプロンプトに組み込んで回答を生成します。

この一連の流れは、あくまで単発のクエリ処理です。

そこには、

* 状態を保持する仕組み
* タスクを分解する仕組み
* 何度も思考を繰り返すループ構造

が存在しません。

つまり、RAGは「一度考えて答える」ことはできますが、「考え続けてタスクを完了する」ことができません。

function callingを組み込むことで外部処理は可能になりますが、それも単発の拡張に留まり、継続的な意思決定や実行には至りません。

RAGは、LLMに不足している知識を補完するための技術です。

しかしそれは、タスクを処理するための構造にはなっていませんでした。

# AIエージェントとは何か｜ループする知能という設計

従来の生成AIアプリケーションでは、プロンプト、外部ツール、簡易的な状態管理を組み合わせることで機能を実現してきました。

しかしAIエージェントは、それらを単発で組み合わせるのではなく、「ループする構造」そのものを持つという点で本質的に異なります。

AIエージェントは、ある目的に対して、

* 状態を保持し（State）
* 思考し（Think）
* 行動し（Act）
* 結果を観測し（Observe）

この一連の流れを繰り返します。

つまり、1回の推論で完結するのではなく、目的が達成されるまで、継続的に思考と実行を回し続ける構造になっています。

この「ループ構造」の有無こそが、RAGのような単発のクエリ処理と、AIエージェントのようなタスク処理を分ける決定的な違いです。

# RAGとAIエージェントの違い｜部品とシステム

RAGとAIエージェントは、競合する技術ではありません。

役割が異なる、別レイヤーの技術です。

RAGは、必要な知識を取得し、LLMに渡すための仕組みです。

つまり、「RAG = 知識取得モジュール」です。

一方でAIエージェントは、

* 目的を理解し
* 何をするべきかを判断し
* 必要なツールを選択し
* 実行し
* 結果をもとに次の行動を決める

という一連の流れを持つシステムです。

つまり、「AIエージェント = 意思決定システム」です。

この違いを一言で表すと、RAGは「部品」であり、AIエージェントは「システム」です。

重要なのはここからです。

LLMの性能向上や外部検索（Tavilyなど）によって、一般的なタスクであればRAGなしでも対応できる場面は増えています。

しかし、特定の業務に特化した処理を行う場合、ドメイン知識を正確に渡す仕組みは依然として不可欠です。

その役割を担うのがRAGです。

つまりRAGは不要になるのではなく、AIエージェントの中に組み込まれる知識取得レイヤーへと進化します。

これが、RAGとAIエージェントの関係性の本質です。

# Semantic Kernelとは何か｜Agentを成立させる設計フレーム

Semantic Kernelとは、AIエージェントを構築するための軽量なオープンソースSDKであり、C#、Python、Javaといった言語で統一的に扱うことができます。

重要なのは、Semantic Kernelが単なるツールではなく、AIエージェントを成立させるための設計フレームを提供している点です。

Semantic Kernelは主に以下のコンポーネントで構成されます。

これらは、前章で説明したエージェントの構造と対応しています。

AIエージェントは、

* 状態を持ち（State）
* 思考し（Think）
* 行動し（Act）
* それをループさせる（Loop）

という構造を持っていました。

Semantic Kernelではこれを以下のように実現します。

* Planner：何をするべきかを決定する（Think）
* Plugin：実際の処理を実行する（Act）
* Memory：状態や履歴を保持する（State）

※従来はPlannerというコンポーネントが存在し、  
タスクの分解や実行計画を担っていました。

現在は、LLMによるFunction Callingによって、  
同様の役割が実現されています。

このように、エージェントの各責務が明確に分離されています。

つまりSemantic Kernelは、「思考・行動・記憶」を分離し、それらをループさせるための設計フレームです。

これにより、単発の推論ではなく、継続的にタスクを処理するAIエージェントを実装できるようになります。

# 理論的にどのように適用できるのか｜業務はループ構造に分解できる

例えば継続的な判断と実行が必要な業務を考えてみます。

この業務は、以下のような流れで構成されます。

* 在庫状況を確認する
* 発注の判断を行う
* 発注を実行する
* 在庫状況を更新する

一見シンプルに見えますが、この処理は一度で終わるものではなく、継続的に繰り返されるループ構造になっています。

これをAIエージェントの構造に対応させると、次のようになります。

* 在庫状況を確認する → 状態取得（State）
* 発注の判断を行う → 思考・意思決定（Think）
* 発注を実行する → 行動（Act）
* 在庫状況を更新する → 観測（Observe）

そして、この一連の流れを繰り返すことで、業務が継続的に回り続けます。

Semantic Kernelを用いる場合、この構造は以下のように実現されます。

* Plugin：在庫確認や発注処理といった具体的な業務処理（Act）
* Planner（またはLLMの判断）：発注が必要かどうかを決定する（Think）
* Memory：在庫状況や履歴を保持する（State）

そしてこれらを組み合わせ、目的が達成されるまでループさせることで、業務を自動化します。

つまり、業務とは単発の処理ではなく、「状態をもとに判断し、実行し、再評価する」というループ構造そのものです。

AIエージェントは、この構造をそのまま実装できるため、業務の自動化に適したアーキテクチャであると言えます。

# 最小構成のエージェント｜構造だけ見せる

ここまでで、AIエージェントの構造は見えてきたと思います。

では実際に、「この構造はどう実装されるのか」を最小構成の例で見ていきます。

ここでの目的は一つです。

「あ、これ作れるじゃん」と思えることです。

## 構造をもう一度整理する

今回扱うのは、在庫管理のシンプルな業務です。

* 在庫を確認する
* 閾値を下回っていれば発注する
* 結果を状態に反映する

これをエージェントの構造に対応させると、次のようになります。

* 状態（State）：在庫数
* 判断（Think）：発注するかどうか
* 行動（Act）：発注処理
* 観測（Observe）：結果の反映

そして、この一連の流れをループさせます。

## 疑似コードで見るエージェント

まずは、細かい実装を抜きにして構造だけを見ると、エージェントは次のように表現できます。

```
while not done:
    stock = get_stock(item_id) # Observe

    if stock < threshold: # Think
        place_order(item_id, 20) # Act

    update_state() # State
```

特別なことはしていません。

状態を見て、判断して、行動して、更新する。このループを回しているだけです。

これがAIエージェントの最小構成です。

## 実行すると何が起きるか

実際に動かすと、内部では次のような流れになります。

```
=== LOOP 1 START ===
CURRENT STATE: stock=0

[PLUGIN] get_stock called
→ stock = 6

[PLUGIN] place_order called
→ +20

LLM RESULT: 
{
    "stock": 26,
    "ordered": true
}
```

ここで重要なのは3点です。

* LLMが「発注するかどうか」を判断している
* 必要に応じてツール（Plugin）を呼び出している
* 結果が状態として更新されている

つまり、先ほどの疑似コードのループが、そのまま実行されています。

## Semantic Kernelでの実装

上記の構造を、Semantic Kernelで実装すると以下のようになります。

Semantic Kernelでの実装例

```
import os
import json
from dataclasses import dataclass
from dotenv import load_dotenv

from semantic_kernel import Kernel
from semantic_kernel.contents import ChatHistory
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)
from semantic_kernel.functions import kernel_function

# 環境変数読み込み
load_dotenv()

# 状態
@dataclass
class InventoryState:
    item_id: str
    stock: int = 0
    reorder_threshold: int = 10
    last_order_result: str | None = None
    done: bool = False

# Tool / Plugin
class InventoryPlugin:
    def __init__(self):
        self._db = {"item-001": 6}

    @kernel_function(
        name="get_stock",
        description="指定した商品の現在在庫数を取得する"
    )
    def get_stock(self, item_id: str) -> str:
        print(f"[PLUGIN] get_stock called: item_id={item_id}")
        stock = self._db.get(item_id, 0)
        return json.dumps({"item_id": item_id, "stock": stock}, ensure_ascii=False)

    @kernel_function(
        name="place_order",
        description="指定した商品の発注を実行する。quantity個だけ在庫を増やす"
    )
    def place_order(self, item_id: str, quantity: int) -> str:
        print(f"[PLUGIN] place_order called: item_id={item_id}, quantity={quantity}")
        self._db[item_id] = self._db.get(item_id, 0) + quantity
        return json.dumps(
            {
                "item_id": item_id,
                "ordered_quantity": quantity,
                "new_stock": self._db[item_id],
            },
            ensure_ascii=False,
        )

# エージェントループ
async def main():
    kernel = Kernel()

    # モデル設定
    kernel.add_service(
        AzureChatCompletion(
            service_id="azure-chat",
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            deployment_name=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        )
    )

    # Plugin 登録
    kernel.add_plugin(InventoryPlugin(), plugin_name="inventory")

    state = InventoryState(item_id="item-001")

    # Azure用 settings を使う
    settings = AzureChatPromptExecutionSettings()
    settings.function_choice_behavior = FunctionChoiceBehavior.Auto(
        filters={"included_plugins": ["inventory"]}
    )

    # Chat completion service を取得
    chat_completion = kernel.get_service(type=ChatCompletionClientBase)

    loop_count = 0
    max_loops = 3

    while not state.done and loop_count < max_loops:
        loop_count += 1

        print(f"\n=== LOOP {loop_count} START ===")
        print("CURRENT STATE:", state)

        history = ChatHistory()
        history.add_user_message(
            f"""
あなたは在庫管理エージェントです。
次の業務を実行してください。

目的:
- inventory.get_stock を使って在庫を確認する
- 在庫が reorder_threshold を下回っていれば inventory.place_order を使って 20 個発注する
- 最後に結果を JSON のみで返す

現在の状態:
- item_id: {state.item_id}
- stock: {state.stock}
- reorder_threshold: {state.reorder_threshold}
- last_order_result: {state.last_order_result}

出力形式:
{{
  "stock": 数値,
  "should_order": true/false,
  "ordered": true/false,
  "done": true/false,
  "summary": "説明"
}}

注意:
- 必要なら必ずツールを呼び出してください
- JSON以外は返さないでください
"""
        )

        try:
            result = await chat_completion.get_chat_message_content(
                chat_history=history,
                settings=settings,
                kernel=kernel,
            )

            text = str(result)
            print("LLM RESULT:", text)

            # JSON parse
            parsed = json.loads(text)

            state.stock = int(parsed["stock"])
            state.done = bool(parsed["done"])

            if parsed.get("ordered"):
                state.last_order_result = parsed.get("summary", "ordered")

            print("UPDATED STATE:", state)

        except Exception as e:
            print("=== outer exception ===")
            print(type(e).__name__, e)

            if e.__cause__:
                print("=== cause ===")
                print(type(e.__cause__).__name__, e.__cause__)

            if e.__context__:
                print("=== context ===")
                print(type(e.__context__).__name__, e.__context__)

            raise

# 実行
await main()
```

## このコードの見方

この実装のポイントは3つです。

① Plugin = 行動（Act）  
→get\_stockとplace\_orderが実際の業務処理を担当している

② LLM = 判断（Think）  
→ 在庫を見て「発注するかどうか」を決めている

③ ループ = エージェントの本体  
→whileによって意思決定が継続されている

つまり、先ほどの疑似コードの構造がそのままコードになっています。

こちらのソースを実際に出力した結果がこちらになります。

ログ出力

```
=== LOOP 1 START ===
CURRENT STATE: InventoryState(item_id='item-001', stock=0, reorder_threshold=10, last_order_result=None, done=False)
[PLUGIN] get_stock called: item_id=item-001
[PLUGIN] place_order called: item_id=item-001, quantity=20
LLM RESULT: {
  "stock": 26,
  "should_order": true,
  "ordered": true,
  "done": true,
  "summary": "在庫を確認したところ 6 個でした。閾値 10 を下回っていたため 20 個を発注し、現在の在庫は 26 個になりました。"
}
UPDATED STATE: InventoryState(item_id='item-001', stock=26, reorder_threshold=10, last_order_result='在庫を確認したところ 6 個でした。閾値 10 を下回っていたため 20 個を発注し、現在の在庫は 26 個になりました。', done=True)
```

## 重要なのは「難しいことをしていない」こと

ここで重要なのは、このコードが特別なことをしているわけではないという点です。

やっていることは一貫しています。

* 状態を取得する
* 判断する
* 行動する
* 結果を反映する

このループを回しているだけです。

これがAIエージェントの本質です。

# まとめ｜RAGは終わらない、役割が進化する

RAGエンジニアからAIエージェントエンジニアにシフトしていく流れについて見てきました。

私はこれまで、RAGの精度改善に取り組んできました。

しかしその中で、「これで本当に業務は終わるのか？」という問いにぶつかりました。

RAGは、正しい情報にたどり着くための技術です。一方でAIエージェントは、その情報を使って「仕事を進め、終わらせる構造」です。

RAGは部品であり、AIエージェントはシステムです。

この関係性が、本質的な違いです。

RAGは終わるわけではありません。AIエージェントの中で、知識取得レイヤーとして役割が進化していきます。

そしてこれからは、

* 状態を持ち
* 判断し
* 行動し
* 結果をもとに次を決める

このループを設計できるかどうかが、業務改善の鍵になります。

小さな例でも構いません。

まずは一つ、自分の業務をループ構造に分解してみてください。

そこから、AIエージェントの設計は始まります。

---

※補足 Semantic Kernelと並ぶ選択肢として、Microsoft Agent Framework（プレビュー）が登場しています。  
これから新規に検討する場合は、そちらも選択肢として検討する価値があります。

---

# 関連記事

本記事では、AIエージェントの本質が「状態を持ち、判断し、行動し、結果をもとに次を決めるループ構造」にあることを整理しました。

では、その中でAIエージェントはどのように行動しているのか。その仕組みを支えているのが Function Callingです。

次の記事では、LLMが外部ツールと接続し、実際の処理を前に進められる理由を解説しています。

<https://zenn.dev/startspace/articles/f738d3fb4f898c>
