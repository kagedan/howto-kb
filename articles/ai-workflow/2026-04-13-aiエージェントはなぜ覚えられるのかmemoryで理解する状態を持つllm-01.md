---
id: "2026-04-13-aiエージェントはなぜ覚えられるのかmemoryで理解する状態を持つllm-01"
title: "AIエージェントはなぜ覚えられるのか｜Memoryで理解する状態を持つLLM"
url: "https://zenn.dev/startspace/articles/3c6fb5e7d0b169"
source: "zenn"
category: "ai-workflow"
tags: ["LLM", "zenn"]
date_published: "2026-04-13"
date_collected: "2026-04-14"
summary_by: "auto-rss"
---

# 導入｜なぜAIエージェントは「覚えていられる」のか

ChatGPTが会話を忘れてしまい、困った経験がある方も多いと思います。

基本的にLLMは会話の情報を保存する仕組みを持っておらず、処理が終わると状態はリセットされます。

しかしAIエージェントは、

* 実行した過去の結果を利用できる
* 業務の進捗を覚えながら処理を進められる

といった振る舞いができます。

このようにAIエージェントは過去の情報をもとに判断を積み重ね、行動を繰り返すことができるのです。

ではここで一つ疑問が生まれます。

AIエージェントは、どこに「記憶」を持っているのでしょうか？

# よくある誤解｜LLMが記憶しているわけではない

AIエージェントの話をすると、よく次のような誤解が生まれます。

* AIエージェントは実行するたびに学習している
* ChatGPTはユーザーごとに記憶して成長している
* 会話を続けるとディープラーニングによって賢くなる

しかし実際はそうではありません。

LLMは基本的に毎回リセットされる仕組みになっています。

つまり、会話の履歴や実行結果そのものをLLMが内部に保存しているわけではありません。

では、AIエージェントが利用している

といった情報はどこにあるのでしょうか。

その答えが、今回のテーマであるMemory（記憶）です。

# 本質｜AIエージェントは「状態」を持つ

AIエージェントの本質は、状態（State）を持つLLMであることです。

これまでの記事では、

* Function Callingによって「行動」が実行できる
* Control Flowによって「処理を繰り返すループ」が構成される

という仕組みを整理してきました。

そして今回のテーマがMemory（状態）です。

AIエージェントは、次のような構造で動作します。

```
AIエージェント = State + Think + Act + Observe
```

現在の状態（State）をもとにLLMが思考（Think）を行い、必要な処理をFunction Callingなどで実行（Act）します。

そして、その結果を観測（Observe）し、新しい状態として更新していきます。

この流れは次のように表現できます。

```
State
↓
Think
↓
Act
↓
Observe（State更新）
```

つまりAIエージェントは、状態を更新し続けながら判断と行動を繰り返す構造になっているのです。

# AIエージェントのMemoryの種類

AIエージェントにおけるMemoryは、大きく次の3種類に分けられます。

* Short-Term Memory（短期記憶）
* Long-Term Memory（長期記憶）
* State Memory（状態記憶）

それぞれ役割が異なり、組み合わせて利用されます。

## Short-Term Memory（短期記憶）

短期記憶は、現在の状況を理解するための記憶です。

例えば次のような情報が含まれます。

LLMはこの情報をコンテキストとして読み取り、次に何をするべきかを判断します。

## Long-Term Memory（長期記憶）

長期記憶は、過去の知識を利用するための記憶です。

代表的な例がRAG（Retrieval Augmented Generation）です。

ベクトルDBなどに知識を保存しておき、必要なタイミングで検索してLLMに渡します。

Long-Term MemoryはRAGなどで利用される知識ベースに近いものです。

## State Memory（状態記憶）

AIエージェントで特に重要になるのがState Memoryです。

これは現在のタスクの状態を保持するための記憶です。

例えば次のような情報です。

* 作業の進捗
* タスクの状態
* 処理の結果
* ユーザーの状態

以前の記事で在庫管理エージェントのサンプルを作りましたが、その際には次のようなStateを保持していました。

```
@dataclass
class InventoryState:
    item_id: str
    stock: int = 0
    reorder_threshold: int = 10
    last_order_result: str | None = None
    done: bool = False
```

このStateには次のような情報が含まれています。

* 在庫の種類
* 現在の在庫数
* 注文する閾値
* 前回処理の結果
* 処理完了フラグ

このように状態を保持することで、AIエージェントは

* 現在の状況を理解し
* 次に行うべき行動を判断し
* 処理を継続する

ことができるようになります。

※本記事では、タスクの進捗や状態を保持する記憶を「State Memory」と呼んでいます。

# MemoryがあることでAIエージェントはどう変わるのか

もしMemoryがない場合、状態が保持されないため、LLMは単発で呼び出されるだけの存在になります。

LLMは基本的に一度の入力に対して一度の出力を返すだけの関数のようなものであり、前回の処理結果や現在の進捗を自分で覚えているわけではありません。

そのため、後続の処理をつなげようとすると、

といった一連の流れを、すべてプログラム側で手動で制御する必要があります。

しかしMemoryを持つことで、AIエージェントは現在の状態（State）を保持しながら処理を進めることができるようになります。

つまり、

* 今の在庫はいくつか
* すでに発注を行ったか
* 業務は完了しているか

といった現在の状況を記憶した状態で次の判断を行えるようになります。

さらに、Semantic KernelのようなAIエージェントフレームワークでは、Plugin（Function Calling）などを組み合わせることで、ツールの実行と状態更新を繰り返しながら処理を進めることができます。

その結果、LLMは単なる「質問に答える存在」ではなく、状態を見ながら次の行動を決める存在として動作するようになります。

つまりMemoryがあることで、AIエージェントは次のようなループ構造を持つことになります。

```
状況確認（State）
↓
判断（Think）
↓
行動（Act）
↓
結果取得（Observe）
↓
状態更新（State Update）
↓
再判断
```

このように、Memoryによって状態を保持できるようになることで、AIエージェントは単発の応答システムから、継続的に業務を進めるシステムへと変わるのです。

# 実装イメージ｜Stateを持つAIエージェント

ここまでで、AIエージェントは

```
State + Think + Act + Observe
```

という構造で動作することを説明してきました。

では実際に、Stateを持ったAIエージェントはどのように実装されるのでしょうか。

以下はSemantic Kernelを使った最小構成のサンプルです。  
在庫管理エージェントを例に、Stateを保持しながら処理を進める構造を簡略化して示しています。

※コードは動作確認用のサンプルで、Jupyter Notebook上で実行しています。

最小のStateを持ったAIエージェント

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

load_dotenv()

@dataclass
class InventoryState:
    item_id: str
    stock: int = 0
    done: bool = False

class InventoryPlugin:
    def __init__(self):
        self._db = {"item-001": 6}

    @kernel_function(name="get_stock", description="商品の在庫数を取得する")
    def get_stock(self, item_id: str) -> str:
        stock = self._db.get(item_id, 0)
        return json.dumps({"item_id": item_id, "stock": stock}, ensure_ascii=False)

    @kernel_function(name="place_order", description="商品を20個発注する")
    def place_order(self, item_id: str) -> str:
        self._db[item_id] = self._db.get(item_id, 0) + 20
        return json.dumps(
            {"item_id": item_id, "new_stock": self._db[item_id]},
            ensure_ascii=False,
        )

async def main():
    kernel = Kernel()

    kernel.add_service(
        AzureChatCompletion(
            service_id="azure-chat",
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            deployment_name=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        )
    )

    kernel.add_plugin(InventoryPlugin(), plugin_name="inventory")

    settings = AzureChatPromptExecutionSettings()
    settings.function_choice_behavior = FunctionChoiceBehavior.Auto(
        filters={"included_plugins": ["inventory"]}
    )

    chat_completion = kernel.get_service(type=ChatCompletionClientBase)

    state = InventoryState(item_id="item-001")

    while not state.done:
        history = ChatHistory()
        history.add_user_message(
            f"""
あなたは在庫管理エージェントです。

次を実行してください。
- inventory.get_stock で在庫を確認する
- 在庫が10未満なら inventory.place_order で20個発注する
- 最後に JSON のみで返す

現在の state:
- item_id: {state.item_id}
- stock: {state.stock}

出力形式:
{{
  "stock": 数値,
  "done": true,
  "summary": "実行結果"
}}
"""
        )

        result = await chat_completion.get_chat_message_content(
            chat_history=history,
            settings=settings,
            kernel=kernel,
        )

        parsed = json.loads(str(result))

        state.stock = parsed["stock"]
        state.done = parsed["done"]

        print("state:", state)
        print("result:", parsed)

await main()
```

このサンプルでは、InventoryStateというデータクラスを定義し、

といった情報をStateとして保持しています。

エージェントはこのStateを参照しながら、

1. 在庫数を確認する
2. 必要であれば発注する
3. 実行結果を受けてStateを更新する

という処理を繰り返します。

つまりAIエージェントは、

```
State → Think → Act → Observe → State更新
```

というループを回しながら、状態を更新し続けることでタスクを進めていく構造になっています。

# まとめ

ここまでAIエージェントの構造について整理してきました。

AIエージェントは次の3つの要素で構成されています。

* Memory（State）
* Control Flow（Loop）
* Function Calling（Act）

Memoryによって状態を保持し、Control Flowによって処理を繰り返し、Function Callingによって実際の行動を実行します。

つまりAIエージェントは、状態を更新しながら判断と行動を繰り返す構造になっています。

そして、この構造の上に業務フローを設計することで、実務で動くAIエージェントを設計できるようになります。
