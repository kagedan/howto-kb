---
id: "2026-04-20-aiエージェントはなぜ人間と協働するのかhuman-in-the-loopで理解する意思決定の最終制-01"
title: "AIエージェントはなぜ人間と協働するのか｜Human-In-The-Loopで理解する意思決定の最終制御"
url: "https://zenn.dev/startspace/articles/bd01942b140647"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-20"
date_collected: "2026-04-21"
summary_by: "auto-rss"
query: ""
---

# 導入｜なぜAIエージェントは「人間と協働する」のか

今までの連載の中で、AIエージェントの「行動」「実行」「ループ」「記憶」について見てきました。

ここまで整理してくると、こう思う方も多いのではないでしょうか。

> 「もうAIエージェントだけで業務は回るのではないか？」

実際、2025年はAIエージェント元年とも言われており、自律的に動くシステムは現実的なものになりつつあります。

しかし一方で、実務の現場を見るとどうでしょうか。

AIエージェントが導入されていても、最終的には人間が確認しているケースがほとんどです。

ではなぜ、ここまで技術が進んでいるにも関わらず、業務は完全に自動化されていないのでしょうか？

それは、多くの業務において人間の意思決定が必要なポイントが存在するためです。

ではなぜ人の意思決定が必要になるのか。そしてそれをどのように設計すべきなのか。

この記事では、Human-In-The-Loopという観点からその構造を整理していきます。

# よくある誤解｜AIエージェントは完全自動化できる

それではよくある誤解について確認していきます。

ここまでAIエージェントの構造を見てくると、次のように考えたくなります。

* LLMの推論能力が高くなれば、人間はいらない
* Agentがあれば業務はすべて任せられる

一見すると正しそうに見えますが、これは本質的には誤りです。

確かにAIエージェントによって、多くの業務は自動化できます。実際に「人手を介さずに動くシステム」を作ること自体は可能です。

しかし、ここで一つ重要な問いがあります。

> もしAIが誤った判断をした場合、その責任は誰が取るのでしょうか？

例えば、LLMがハルシネーションを起こし、誤った情報をもとに処理を実行した場合。

それは実装者の責任なのか、運用者の責任なのか。  
あるいはLLMを提供している事業者の責任なのか。

この責任の所在は非常に曖昧であり、少なくともAI自身が責任を負うことはありません。

ここが重要なポイントです。

AIは「判断」はできますが、その結果に対して責任を持つことはできません。

だからこそ、実務のシステムでは最終的な意思決定を人間が担う構造が必要になります。

完全自動化が可能かどうかではなく、どこまでをAIに任せ、どこからを人間が担うのか。

これを設計することが、AIエージェントにおいて本質的な課題になります。

# 本質｜Human-In-The-Loopとは「意思決定の最終制御」である

では今回の主題であるHuman-In-The-Loopとは何でしょうか。

結論から言うと、AIの出力に対して人間が介在する仕組みです。

ただし、ここで重要なのは単に「人が関与する」という話ではありません。

Human-In-The-Loopの本質は、意思決定の最終制御を人間が担うことにあります。

AIエージェントは自律的に動作し、判断し、行動することができます。  
しかし、その結果に対する責任を持つことはできません。

だからこそ、

* AIが判断し
* AIが行動し
* 最終的な意思決定を人間が担う

という構造を取る必要があります。

これにより何が実現できるかというと、AIの利便性を活かしつつ、リスクをコントロールできるようになります。

例えば、AIが誤った判断をしたとしても、最終的な実行を人間が制御することで、システム全体としての安全性を担保することができます。

つまりHuman-In-The-Loopとは、AIに任せるのではなく、「制御しながら使う」ための設計です。

# なぜ人間が必要なのか｜AIが苦手な領域

では、これだけ高性能なAIが存在するにも関わらず、なぜ人間が必要になるのでしょうか。

結論から言うと、AIは「計算」はできても「判断の責任」を扱えないためです。

ここでは、その背景となる代表的な領域を整理します。

## 不確実性の判断

まずは不確実性です。

GPTやClaude、GeminiといったLLMは非常に優秀ですが、あくまで「与えられた情報の中で最適な推論を行う」モデルです。

そのため、

* 情報が不足している
* 情報がそもそも存在しない
* 正解が一意に定まらない

といった状況では、必ずしも正しい判断ができるとは限りません。

例えば、社内のマニュアルや規約、暗黙知のような情報は、外部のLLMだけでは扱えないケースも多く存在します。

RAGによって知識を補完することは可能ですが、

* 必要な情報がtop-kに含まれる保証はない
* そもそも検索対象に存在しない情報もある

といった制約があります。

また、正解が複数存在する場合、どの選択肢を採用するかは「その場の判断」に依存します。

このような不確実性を含む領域では、最終的な判断を人間が担う必要があります。

## リスク判断

次にリスクです。

AIエージェントは自律的に処理を実行できるため、決済やデータ更新といった重要な業務にも適用することができます。

しかし、

* 大金が動く処理
* 法令遵守が求められる処理
* セキュリティに関わる処理

において誤りが発生した場合、その影響は非常に大きくなります。

例えば、AIが誤った判断を行い不正な処理を実行した場合、それを「AIのせい」として説明できるでしょうか。

実際の経営判断としては、そうはなりません。

また、最近ではエージェントに権限を持たせる設計も増えており、どこまでの権限を委譲するかという問題も重要になっています。

AIに任せられる範囲は、「技術」ではなく「リスク」で決まります。

## 文脈・責任の判断

最後に責任と文脈です。

業務における意思決定は、単なる正解選択ではなく、

* 組織としてどう判断するか
* 誰が責任を持つのか
* どのリスクを許容するのか

といった文脈の中で行われます。

そしてこれらは、現時点ではAIが扱える領域ではありません。

特に企業規模が大きくなるほど、

といった要素が重要になり、単純な自動化では対応できなくなります。

---

これらを踏まえると、AIは「判断を補助する存在」であり、「判断を代替する存在ではない」という構造が見えてきます。

だからこそ、AIエージェントにおいては、人間の意思決定を前提とした設計が必要になるのです。

# Human-In-The-Loopの設計パターン

Human-In-The-Loopは単に人間を介在させるのではなく、どこに人間を入れるかを設計することが重要です。

ここでは代表的なパターンを整理します。

## 承認フロー型（Approval）

AIが処理を行い、その結果を人間が確認・承認した上で実行するパターンです。

例：

* メール送信前の文章作成 → 人間が確認 → 送信
* 発注内容の生成 → 人間が承認 → 実行

このパターンは、実行そのものにリスクがある場合に適しています。

「実行してよいか」を人間が判断する構造です。

## 分岐判断型（Decision Gate）

一定の条件に応じて、人間にエスカレーションするパターンです。

例：

* 金額が一定以上の場合のみ承認フローに乗せる
* 信頼度スコアが低い場合に人間に判断を委ねる

このパターンは、すべてを人間に任せるとコストが高すぎる場合に有効です。

「通常は自動化しつつ、例外だけ人に任せる」構造です。

## レビュー型（Review）

処理の実行後に、人間が成果物を確認するパターンです。

例：

* レポート生成後に人間がレビュー
* 実行ログを確認し問題があれば再実行

このパターンは、リアルタイム性よりも品質が重要な場合に適しています。

「まず動かし、後から担保する」構造です。

## 設計の本質

これらをまとめると、

* Approval：実行前に止める
* Decision Gate：条件で止める
* Review：実行後に確認する

という違いになります。

重要なのは、すべてに人間を介在させることではありません。

「どこに人間の判断価値があるか」を見極めることです。

# 実装イメージ｜Human-In-The-Loopを組み込む

以前は、在庫不足を検知した際にAIエージェントがそのまま発注まで実行していました。  
今回はそこを変更し、AIは発注提案までを行い、実際の発注は人間が承認したときのみ実行する形にしています。

ポイントは、AIの役割を「自動実行」から「判断補助」に変えていることです。

このように、AIが判断し、人間が最終実行を制御する構造にすることで、Human-In-The-Loopを最小構成で表現できます。

最初Human-in-the-loopの実装

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
    proposed_order_quantity: int = 0
    approval_required: bool = False
    approved: bool = False
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
        return json.dumps(
            {"item_id": item_id, "stock": stock},
            ensure_ascii=False,
        )

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

async def request_human_approval(state: InventoryState) -> bool:
    """
    Human-In-The-Loop の最小例として、
    発注提案に対して人間が承認するかを受け取る。
    """
    print("\n=== HUMAN APPROVAL REQUIRED ===")
    print(
        f"商品 {state.item_id} の在庫は {state.stock} 個です。"
        f"{state.proposed_order_quantity} 個の発注を提案します。"
    )

    user_input = input("発注を承認しますか？ (yes / no): ").strip().lower()
    return user_input == "yes"

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

    # Plugin は1回だけ作って使い回す
    plugin = InventoryPlugin()
    kernel.add_plugin(plugin, plugin_name="inventory")

    state = InventoryState(item_id="item-001")

    settings = AzureChatPromptExecutionSettings()
    settings.function_choice_behavior = FunctionChoiceBehavior.Auto(
        filters={"included_plugins": ["inventory"]}
    )

    chat_completion = kernel.get_service(type=ChatCompletionClientBase)

    loop_count = 0
    max_loops = 3

    while not state.done and loop_count < max_loops:
        loop_count += 1

        print(f"\n=== LOOP {loop_count} START ===")
        print("CURRENT STATE:", state)

        # 承認待ちの場合はLLMではなく人間に判断を委ねる
        if state.approval_required and not state.approved:
            approved = await request_human_approval(state)

            if approved:
                state.approved = True
                print("[HUMAN] 発注を承認しました。")

                # 同じ plugin インスタンスを使って発注する
                result = plugin.place_order(
                    item_id=state.item_id,
                    quantity=state.proposed_order_quantity,
                )
                parsed_result = json.loads(result)

                state.stock = int(parsed_result["new_stock"])
                state.last_order_result = f"{parsed_result['ordered_quantity']}個を発注"
                state.done = True

            else:
                print("[HUMAN] 発注を却下しました。")
                state.last_order_result = "発注は承認されませんでした"
                state.done = True

            print("UPDATED STATE:", state)
            continue

        history = ChatHistory()
        history.add_user_message(
            f"""
あなたは在庫管理エージェントです。
次の業務を実行してください。

目的:
- inventory.get_stock を使って在庫を確認する
- 在庫が reorder_threshold を下回っていれば、すぐに発注するのではなく、
  人間に承認を求める提案を作成する
- 発注提案が必要な場合は approval_required=true とし、
  proposed_order_quantity=20 を設定する
- 最後に結果を JSON のみで返す

現在の状態:
- item_id: {state.item_id}
- stock: {state.stock}
- reorder_threshold: {state.reorder_threshold}
- proposed_order_quantity: {state.proposed_order_quantity}
- approval_required: {state.approval_required}
- approved: {state.approved}
- last_order_result: {state.last_order_result}

出力形式:
{{
  "stock": 数値,
  "should_order": true/false,
  "approval_required": true/false,
  "proposed_order_quantity": 数値,
  "done": true/false,
  "summary": "説明"
}}

注意:
- 在庫確認には必要なら必ずツールを呼び出してください
- 在庫不足でも勝手に発注はしないでください
- 発注が必要なら「人間の承認が必要」と返してください
- 承認が必要な場合は done=false にしてください
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

            parsed = json.loads(text)

            state.stock = int(parsed["stock"])
            state.approval_required = bool(parsed["approval_required"])
            state.proposed_order_quantity = int(parsed["proposed_order_quantity"])

            # 承認待ちなら未完了に固定する
            if state.approval_required and not state.approved:
                state.done = False
                state.last_order_result = None
            else:
                state.done = bool(parsed["done"])
                state.last_order_result = parsed.get("summary", "no action")

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

# jupyter notebookで実行
await main()
```

出力結果

noの場合

```
=== LOOP 1 START ===
CURRENT STATE: InventoryState(item_id='item-001', stock=0, reorder_threshold=10, proposed_order_quantity=0, approval_required=False, approved=False, last_order_result=None, done=False)
[PLUGIN] get_stock called: item_id=item-001
LLM RESULT: {
  "stock": 6,
  "should_order": true,
  "approval_required": true,
  "proposed_order_quantity": 20,
  "done": false,
  "summary": "在庫6が発注点10を下回っているため、20個の発注提案を作成します。人間の承認が必要です。"
}
UPDATED STATE: InventoryState(item_id='item-001', stock=6, reorder_threshold=10, proposed_order_quantity=20, approval_required=True, approved=False, last_order_result=None, done=False)

=== LOOP 2 START ===
CURRENT STATE: InventoryState(item_id='item-001', stock=6, reorder_threshold=10, proposed_order_quantity=20, approval_required=True, approved=False, last_order_result=None, done=False)

=== HUMAN APPROVAL REQUIRED ===
商品 item-001 の在庫は 6 個です。20 個の発注を提案します。
発注を承認しますか？ (yes / no):  no
[HUMAN] 発注を却下しました。
UPDATED STATE: InventoryState(item_id='item-001', stock=6, reorder_threshold=10, proposed_order_quantity=20, approval_required=True, approved=False, last_order_result='発注は承認されませんでした', done=True)
```

yesの場合

```
=== LOOP 1 START ===
CURRENT STATE: InventoryState(item_id='item-001', stock=0, reorder_threshold=10, proposed_order_quantity=0, approval_required=False, approved=False, last_order_result=None, done=False)
[PLUGIN] get_stock called: item_id=item-001
LLM RESULT: {
  "stock": 6,
  "should_order": true,
  "approval_required": true,
  "proposed_order_quantity": 20,
  "done": false,
  "summary": "在庫6は再発注しきい値10を下回っています。20個の発注を提案します。人間の承認が必要です。"
}
UPDATED STATE: InventoryState(item_id='item-001', stock=6, reorder_threshold=10, proposed_order_quantity=20, approval_required=True, approved=False, last_order_result=None, done=False)

=== LOOP 2 START ===
CURRENT STATE: InventoryState(item_id='item-001', stock=6, reorder_threshold=10, proposed_order_quantity=20, approval_required=True, approved=False, last_order_result=None, done=False)

=== HUMAN APPROVAL REQUIRED ===
商品 item-001 の在庫は 6 個です。20 個の発注を提案します。
発注を承認しますか？ (yes / no):  yes
[HUMAN] 発注を承認しました。
[PLUGIN] place_order called: item_id=item-001, quantity=20
UPDATED STATE: InventoryState(item_id='item-001', stock=26, reorder_threshold=10, proposed_order_quantity=20, approval_required=True, approved=True, last_order_result='20個を発注', done=True)
```

# 実務での設計指針｜どこに人間を入れるべきか

では実務において、AIエージェントに人間をどこに介在させるべきでしょうか。

結論から言うと、「判断の価値が高い箇所」に限定して入れるべきです。

すべてに人間を介在させてしまうと、単なる手作業に戻ってしまいます。そのため、どこに入れるかの設計が重要になります。

ここでは代表的な判断観点を整理します。

## リスクが高い箇所

まずはリスクです。

* 対顧客のコミュニケーション
* 外部へのデータ送信
* 誤りが直接的な損害に繋がる処理

こういった領域では、誤った判断がそのままビジネスリスクになります。

そのため、実行前の承認フローを設けるなど、人間の介在を前提とした設計が必要になります。

## 正解が一意に定まらない箇所

次に、不確実性の高い領域です。

* 法務判断
* 社内ルールの解釈
* ケースバイケースの判断

これらは単純なロジックでは扱えず、状況に応じた意思決定が求められます。

そのため、AIに任せきるのではなく、人間の判断を前提にする必要があります。

## ビジネスインパクトが大きい箇所

最後にインパクトです。

* 高額な決済
* 重要なデータ更新
* 経営に影響する意思決定

こういった処理は、頻度が低くても影響が非常に大きいため、人間の確認や承認を積極的に入れるべき領域です。

## 設計の本質

ここまでをまとめると、

これらのいずれかに該当する箇所に、Human-In-The-Loopを設計するのが基本になります。

ただし重要なのは、すべてに人間を入れないことです。

人間によるレビューはコストがかかるため、適切に絞り込む必要があります。

AIに任せるかではなく、「どこで人間が介入すべきか」を設計することが本質です。

# まとめ｜AIエージェントは「人間と協働するシステム」である

ここまで、AIエージェントにおける人間の関与について整理してきました。

AIエージェントは自律的に動作し、判断し、行動することができます。  
しかしその一方で、完全自律には大きなハードルがあり、すべてを任せることは現実的ではありません。

そのため実務では、人間の意思決定を前提とした設計が必要になります。

本記事で見てきた通り、AIエージェントは

* Memory（状態）
* Control Flow（ループ）
* Function Calling（行動）
* Human-In-The-Loop（最終制御）

といった要素を組み合わせることで、単なる自動化ではなく、制御されたシステムとして成立します。

重要なのは、AIを止めることではなく、AIの出力をそのまま実行させない構造を設計することです。

AIエージェントは「完全自動化のシステム」ではなく、人間と協働しながら意思決定を行うシステムなのです。
