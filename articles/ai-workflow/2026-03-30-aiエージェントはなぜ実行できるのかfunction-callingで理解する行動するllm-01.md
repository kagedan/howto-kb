---
id: "2026-03-30-aiエージェントはなぜ実行できるのかfunction-callingで理解する行動するllm-01"
title: "AIエージェントはなぜ実行できるのか｜Function Callingで理解する行動するLLM"
url: "https://zenn.dev/startspace/articles/f738d3fb4f898c"
source: "zenn"
category: "ai-workflow"
tags: ["LLM", "zenn"]
date_published: "2026-03-30"
date_collected: "2026-03-31"
summary_by: "auto-rss"
query: ""
---

# 導入｜AIエージェントはなぜ「実行」できるのか

前回の記事では、AIエージェントの本質は「行動」にあると述べました。

しかし、ここで一つの疑問が残ります。

なぜ、文章しか生成できないはずのLLMが、実際の業務を「進める」ことができるのでしょうか？

LLMは本来、テキストを生成するモデルです。それにもかかわらず、AIエージェントはツールを呼び出し、処理を実行し、業務を前に進めることができます。

これは、LLMが賢くなったからではありません。

どれだけモデルの性能が上がっても、それだけで「業務が実行される」ことはありません。

AIエージェントは、賢いから動くのではなく、実行できる構造を持っているから動きます。

本記事では、その「実行」を支えている仕組みであるFunction Callingについて解説していきます。

これを理解すると、LLMが「答える存在」から「仕事を進める存在」に変わる理由が見えてきます。

# Function Callingとは何か｜LLMが外界と接続する瞬間

Function Callingとは、LLMが「文章を生成するだけの存在」から、外部の処理を実行できるようにする仕組みです。

LLMは本来、テキストを生成することしかできません。どれだけ高度な推論ができたとしても、それだけでは現実の処理を実行することはできません。

しかしFunction Callingを用いることで、LLMは「何を実行すべきか」を構造化された形式で出力し、その内容に基づいて外部のツールやAPIが呼び出され、実際の処理が実行されます。

つまり、LLM自身が処理を実行しているわけではなく、実行内容を決定し、それを外部に渡しているという構造になります。

# なぜこれで「実行」が可能になるのか

ではなぜ、テキストしか生成できないはずのLLMが、実際の処理を「実行できる」ようになるのでしょうか？

流れはシンプルです。

まず、LLMはプロンプトとともに「利用可能なツール（Function Calling）」の情報を受け取ります。その上で、「どのツールを使うべきか」「引数は何か」を判断し、構造化された形式（JSON）で出力します。

この出力を受け取ったアプリケーション側が、その内容に基づいてツールやAPIを実行します。

Function Callingは、「何を実行するか」を機械が扱える形に変換する仕組みです。

```
LLM（思考）
↓
Function Calling（意思決定の構造化）
↓
Tool / API（実行）
```

ここで重要なのは、LLM自身が処理を実行しているわけではないという点です。

LLMはあくまで「何を実行するか」を決めているだけであり、実際の処理は外部のシステムが担っています。

つまり、「実行できる能力」があるのではなく、実行を担う外部システムと、意思決定を担うLLMが分離されている構造になっているため、結果として実行が可能になっているのです。

# Function Callingの内部で何が起きているのか

ここまでで、LLMが「実行を指示している」ことは見えてきました。

しかし、実際にどのように動いているのかまでは見えていません。

では、その内部では実際に何が起きているのでしょうか。

流れは次の4ステップに分解できます。

## ① ツール定義（JSON Schema）

まず、LLMにはあらかじめ「使えるツール」が渡されます。

これは単なる関数ではなく、どのような引数を受け取るかまで含めたスキーマとして定義されます。

例えば、在庫を取得する関数であれば、以下のような形になります。

```
{
  "name": "get_stock",
  "description": "在庫数を取得する",
  "parameters": {
    "type": "object",
    "properties": {
      "item_id": {
        "type": "string"
      }
    },
    "required": ["item_id"]
  }
}
```

LLMはこの情報をもとに、「どの関数がどのような条件で使えるか」を理解します。

次に、LLMはプロンプトと状況をもとに、どのツールを使うべきかを判断します。

ここで重要なのは、これは明示的な分岐ロジックではなく、LLMの推論によって選択されているという点です。

つまり、LLMは

を推論によって決めています。

## ③ 引数生成（arguments generation）

ツールを選択した場合、次にその関数に渡す引数を生成します。

ここでもLLMは、スキーマに従って正しい形式のJSONを出力します。

```
{
  "name": "get_stock",
  "arguments": {
    "item_id": "item-001"
  }
}
```

## ④ 実行とレスポンス処理（execution & parsing）

この出力を受け取ったアプリケーション側が、実際に関数やAPIを実行します。

そして、その結果を再びLLMに渡すことで、次の判断や応答が行われます。

このプロセスは一度で終わるとは限らず、結果をもとに再度ツールを選択することで、処理が連続的に進んでいきます。

## 重要なポイント

ここで重要なのは、LLMは「関数を呼び出している」わけではないという点です。

LLMはあくまで「関数呼び出しの形式で出力しているだけ」です。

実際の実行は、外部のシステムが担っています。

つまり、Function Callingとは、「関数を呼び出す仕組み」ではなく、LLMが意思決定を行い、外部システムが実行するための接続インターフェースなのです。

# コードで理解する｜最小のFunction Calling

ここまでで内部の流れは理解できましたが、実際にどのようにコードに落ちるのかはまだ見えていません。

ここでは、最小構成のコードを通して、その動きを確認してみます。

Semantic Kernelでは、Function Callingを直接JSONで書くのではなく、@kernel\_function を使ってPluginとして定義します。

すると内部的には、この定義がツール情報としてLLMに渡され、必要に応じてLLMが関数の利用を判断し、Semantic Kernel側が実際の関数を実行します。

以下は、在庫取得の関数を1つだけ持つ最小構成の例です。

Semantic KernelでのFunction Callingの例

```
import os
from dotenv import load_dotenv

from semantic_kernel import Kernel
from semantic_kernel.contents import ChatHistory
from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)

load_dotenv()

class InventoryPlugin:
    @kernel_function(
        name="get_stock",
        description="指定した商品の現在在庫数を取得する"
    )
    def get_stock(self, item_id: str) -> str:
        print(f"[PLUGIN] get_stock called: item_id={item_id}")
        mock_db = {
            "item-001": 6,
            "item-002": 12,
        }
        stock = mock_db.get(item_id, 0)
        return f"item_id={item_id}, stock={stock}"

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

    history = ChatHistory()
    history.add_user_message(
        """
inventory.get_stock を使って item-001 の在庫数を確認してください。
最終結果は自然な日本語で答えてください。
"""
    )

    result = await chat_completion.get_chat_message_content(
        chat_history=history,
        settings=settings,
        kernel=kernel,
    )

    print("LLM RESULT:")
    print(result)

# 実行
# ※jupyter notebookやIPython環境を想定しています。
# 通常のPythonスクリプトとして実行する場合は asyncio.run(main()) を使用してください。
await main()
```

※.envには以下の環境変数を用意してください。

* AZURE\_OPENAI\_API\_KEY
* AZURE\_OPENAI\_ENDPOINT
* AZURE\_OPENAI\_API\_VERSION
* AZURE\_OPENAI\_CHAT\_DEPLOYMENT

※Azure OpenAI側で、あらかじめチャットモデルのデプロイを作成しておく必要があります。

実行結果

```
[PLUGIN] get_stock called: item_id=item-001
LLM RESULT:
item-001 の現在の在庫数は 6 点です。
```

この例で重要なのは、LLMがPythonの関数を直接呼んでいるわけではないという点です。

LLMは、与えられたツール情報の中からget\_stockを使うべきだと判断し、その結果としてSemantic Kernel側が実際の関数を実行しています。

つまり、LLMが判断し、Semantic Kernelが橋渡しし、Pluginが実行する、という役割分担になっています。

# AIエージェントとの関係｜Function Callingは行動そのものである

前回の記事では、Agentの構造として

を整理しました。

今回のFunction Callingは、この中の「Act」にあたります。

つまり、AIエージェントの「行動」とは、Function Callingの連続であると言えます。

# よくある誤解｜Function Callingだけではエージェントにならない

Function Callingを使えばAIエージェントになる、と思われがちですが、それは誤解です。

Function Callingによって外部の処理が実行できるため、それだけで「エージェントのように見える」ことがあります。

Function Callingはあくまで「行動」を実現する仕組みであり、それ単体では意思決定は行えません。

AIエージェントとして成立させるためには、

* 状態を持ち（State）
* 判断し（Think）
* 行動し（Act）
* 結果をもとに次を決める（Observe）

というループ構造が必要になります。

つまり、Function Callingは手足であり、エージェントは意思決定のループです。

# まとめ｜LLMは「実行できる構造」を持つようになった

LLMは文章を生成するだけの存在ではなくなりました。

しかし、LLMが自ら処理を実行しているわけではありません。

Function Callingによって外部のシステムと接続されることで、LLMが意思決定を行い、外部が実行するという構造が生まれています。

つまり、LLMは「実行する存在」になったのではなく、「実行できる構造の中で意思決定する存在」へと変わったのです。
