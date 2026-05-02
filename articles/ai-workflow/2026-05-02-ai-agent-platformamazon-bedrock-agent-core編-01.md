---
id: "2026-05-02-ai-agent-platformamazon-bedrock-agent-core編-01"
title: "AI Agent Platform（Amazon Bedrock Agent Core編）"
url: "https://zenn.dev/cozy07/articles/4275fd95352ab1"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "prompt-engineering", "API", "AI-agent", "LLM", "OpenAI"]
date_published: "2026-05-02"
date_collected: "2026-05-02"
summary_by: "auto-rss"
query: ""
---

## はじめに

こんにちは🙌  
AI Agentの企業導入は、PoCで試す段階から、実業務に組み込む段階へ進みつつあります。

そこで重要になるのが、AI Agentの実行環境です。エージェントはLLMを呼び出すだけではなく、外部ツールを使い、ユーザーやシステムの権限を扱い、会話履歴や業務文脈を保持し、実行過程を監視・評価する必要があります。  
各クラウドベンダーもAI Agent Platformと呼べるサービス群を整備し始めています。

本記事では、Amazon Bedrock AgentCoreを実際に試しながら、どのような特徴を持つサービスなのかを整理します。

他クラウドでの AI Agent Platform も同様に記事を書いているので、ぜひご覧ください。（数日中に公開予定...）

## ゴール

* Amazon Bedrock AgentCoreの全体像を理解する
* Runtime、Memory、Gateway、Identity、Observability、Evaluationsの役割を把握する
* ワークショップを通じて、PoCのエージェントを本番運用に近づける流れを確認する
* 他クラウドのAI Agent Platformとの立ち位置をざっくり比較する

## AI Agent Platform

AI Agent Platformとは、厳密に標準化された用語ではありませんが、AIエージェントを本番運用するための runtime、orchestration、integration、認証、メモリ、監視、評価、ガバナンスをまとめた実行・運用基盤として使われることが増えています。

AWS Prescriptive Guidanceでも、AI Agent Platformは、本番レベルのエージェントシステムを実行し、拡張し、管理するための基盤として説明されています。  
ここでいうPlatformは、エージェントを作るためのフレームワークそのものではありません。エージェントが安全に動き、外部ツールや業務システムと連携し、組織として運用・管理できるようにするための実行基盤に近いものです。

AI Agent Platform をエンタープライズスケールなインフラへ発展させるには、ガバナンス、スケーラビリティ、ビジネスとの整合性を持って、エージェントを業務ワークフローに組み込む必要があります。

## クラウドサービスでの比較

各クラウドベンダーが提供する AI Agent Platform 相当のサービスを、公開情報ベースで整理したものです。サービス名や対応機能は変化が速いため、厳密な機能比較というより、設計思想の違いを見るための比較として扱います。

| 特性 | Amazon Bedrock AgentCore | Azure AI Agent Service (Foundry) | Gemini Enterprise Agent Platform |
| --- | --- | --- | --- |
| 主な設計思想 | モジュール化とOSSフレームワークの柔軟性 | M365統合と強力なエンタープライズ統制 | マルチモーダル推論とフルスタック垂直統合 |
| ランタイム形式 | Firecracker MicroVMによるサーバーレス隔離 | マネージドコンテナおよびサーバーレス関数 | 低レイテンシのAgent Runtime（サーバーレス） |
| 主要プロトコル | HTTP, MCP, A2A, AG-UI | Assistants API, Llama Stack, MCP | MCP, A2A (Agent2Agent) |
| 開発手法 | コードファースト (Python, Java, JS, .NET) | コードファースト (.NET, Python) | ノーコード(Studio) & プロコード(ADK) |
| エコシステム統合 | AWS全域 (S3, Lambda, IAM) | M365, Fabric, Teams, Logic Apps | Workspace (Gmail, Drive), BigQuery |

## Amazon Bedrock AgentCore

AIエージェントの構築・デプロイ・運用を安全かつ大規模に行うためのフルマネージドなプラットフォームとなっています。

LangGraphやLlamaIndexなどの主要なオープンソースフレームワークに加え、Claude、Gemini、OpenAI、Llama、Novaといった多様なモデルを自由に組み合わせて利用できます。

サーバーレスな実行環境（Runtime）をはじめ、長期記憶（Memory）、API接続（Gateway）、コード実行（Code Interpreter）など、実用的なエージェント開発に必要なコンポーネントをモジュール単位で提供します。

特に2026年4月には Managed Harness がプレビューとして追加され、これまで Runtime 上で自前実装していたエージェントループを、設定ベースで扱える方向に進んでいます。

### 構成要素

![](https://static.zenn.studio/user-upload/f124355a7236-20260429.png)  
*<https://catalog.workshops.aws/agentcore-deep-dive/en-US/10-fundamentals> より*

構成要素多いので、なるべく分かりやすく短めに説明をしていきます。

#### Runtime：実行基盤

あらゆるフレームワークやモデルを動かせる、安全なサーバーレス環境。

#### Identity：認証

エージェントに「誰が何をしていいか」の権限を安全に渡す仕組み。

#### Gateway：ツール窓口

数あるツール（API等）の中から、最適なものをAIが検索・利用する入口。

#### Code Interpreter：計算機

データ分析などの複雑なコードを、隔離された安全な場所で実行。

#### Browser：Web探索

エージェントが自らブラウザを操作し、Webサイトから情報を取得。

#### Memory：記憶力

会話の流れ（短期）や、過去の経緯（長期）をしっかり覚えておく機能。

#### Observability：計測

エージェントが正しく動いているか、ダッシュボードで監視・追跡。

#### Evaluations：品質テスト

AIの回答が「正しいか」「役に立つか」を自動でスコア化。

#### Policy：違反チェック

エージェントの暴走を防ぐため、実行前にルール違反がないかチェック。

### AgentCore Harness（2026年4月発表）

これまで挙げたRuntime、Identity、Gateway、Memoryといったいくつかのパーツを、「最初から全部入り」で提供するフルマネージドな実行基盤です。  
「エージェントの設定ファイル（Config）を渡すだけで、インフラ構築なしに即座に実行環境が立ち上がる」仕組みとなっています。  
「構築」から「設定」になり、サーバーの用意や認証の配線、VPC設定などが一切不要になります。

Runtimeは、安全な使い捨て環境として、セッションごとに隔離されたmicroVMが自動生成され、その中でコード実行やブラウザ操作が安全に行われます。

さらにモデルの自由な切り替えが可能となります。インフラを変えることなく、Bedrock、OpenAI、Geminiなどのモデルを自由に選択・変更できます。

### ユースケース

AWS Prescriptive Guidanceで取り上げられているユースケース例を簡単にいくつか取り上げてみます。  
<https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-patterns/introduction.html>

![](https://static.zenn.studio/user-upload/6120fef33db0-20260501.png)  
LLMが「言葉」だけでなく「行動」を選択し、外部システムと連携するパターンです。  
LLMに利用可能なツールの定義（関数名、引数、説明）を渡すと、LLMはユーザーの意図に応じて適切なツールを選び、その実行に必要なパラメータを生成します。

#### 監視・オブザーバーエージェント (Observer and Monitoring Agents)

![](https://static.zenn.studio/user-upload/84ba83839ae5-20260501.png)  
他のエージェントやシステムの状態を「受動的に観察」し、異常検知や洞察の生成を自動で行います。  
システムログ、メトリクス、あるいは他のエージェントの会話ログを継続的にインジェスト（取り込み）します。LLMがそのコンテキストを解析し、従来のルールベースでは見逃してしまうような「文脈上の不整合」や「ポリシー違反」を特定します。

## 試してみる

こちらのワークショップ題材を用いて実際にBedrock Agent Coreを試してみます。  
<https://catalog.us-east-1.prod.workshops.aws/workshops/850fcd5c-fd1f-48d7-932c-ad9babede979/en-US>

実用的な「カスタマーサポートエージェント」の構築から運用までを体験するハンズオンです。単なる対話機能だけでなく、会話メモリ、エンタープライズAPIとのセキュアな連携、そして本番環境でのスケーラビリティや品質評価といったプロダクション導入に不可欠な高度なスキルを体系的に理解しながら進められます。

![](https://static.zenn.studio/user-upload/352352a0021f-20260429.png)

### アーキテクチャの説明

AIチャットボットを超えた、「実務で頼れるAIエージェント」の構築を体験します。  
顧客一人ひとりの情報を記憶したパーソナライズな対応から、社内データに基づいた正確な業務処理、さらにはセキュリティ制限や回答品質のモニタリングまでを実装した構成を組みます。

### Lab 1: Create the Agent Prototype

まずは、Strands Agents を使って、ローカルで動作するカスタマーサポートエージェントのプロトタイプを作成します。

![](https://static.zenn.studio/user-upload/616c9f15a63a-20260429.png)

このLabでは、Amazon Nova 2 Lite をモデルとして利用し、Strands Agents の `@tool` デコレータで定義したツールをエージェントから呼び出せるようにします。

公式サンプルでは、返品ポリシー確認、商品情報検索、Web検索、Bedrock Knowledge Baseを使った技術サポート検索の4つのツールを扱っています。

例えば、返品ポリシーを返すツールは以下のように定義します。

```
from strands.tools import tool

@tool
def get_return_policy(product_category: str) -> str:
    """
    Get return policy information for a specific product category.

    Args:
        product_category: Electronics category, such as smartphones, laptops, accessories.

    Returns:
        Formatted return policy details.
    """
    return_policies = {
        "smartphones": {
            "window": "30 days",
            "condition": "Original packaging, no physical damage, factory reset required",
            "refund_time": "5-7 business days after inspection",
        },
        "laptops": {
            "window": "30 days",
            "condition": "Original packaging, all accessories, no software modifications",
            "refund_time": "7-10 business days after inspection",
        },
        "accessories": {
            "window": "30 days",
            "condition": "Unopened packaging preferred, all components included",
            "refund_time": "3-5 business days after receipt",
        },
    }

    policy = return_policies.get(product_category.lower())

    if not policy:
        return "Standard return policy applies. Please contact support for details."

    return (
        f"Return window: {policy['window']}\n"
        f"Condition: {policy['condition']}\n"
        f"Refund timeline: {policy['refund_time']}"
    )
```

Strands Agents では、Python関数に `@tool` を付けることで、エージェントが利用できるツールとして扱えます。

次に、モデルとツールを渡して Agent を作成します。

```
from strands import Agent
from strands.models import BedrockModel

model = BedrockModel(
    model_id="amazon.nova-lite-v1:0",
    region_name="us-east-1",
)

agent = Agent(
    model=model,
    tools=[
        get_return_policy,
        get_product_info,
        web_search,
        get_technical_support,
    ],
    system_prompt=SYSTEM_PROMPT,
)

response = agent("I bought a laptop last week. Can I return it?")
print(response)
```

ここで重要なのは、ユーザーの問い合わせに対して、エージェントが必要なツールを判断して呼び出す点です。

例えば「先週買ったノートPCを返品できるか？」という質問であれば、エージェントは `get_return_policy` を使うべきだと判断し、商品カテゴリに応じた返品条件を確認して回答します。

この時点で、ツール利用エージェントとしては動作します。

ただし、まだローカルのPython関数を直接呼び出しているだけです。会話履歴の永続化、ユーザーごとの文脈保持、ツールの集中管理、認証、監視、評価といった本番運用に必要な要素はまだ含まれていません。

そのため、Lab 1 は「AIエージェントとして動く最小構成」を作る位置づけになります。

### Lab 2: Enhance your Agent with Memory

![](https://static.zenn.studio/user-upload/405f2bbcfabf-20260501.png)

Lab 2 では、AgentCore Memory を使って、エージェントに会話履歴と顧客ごとの文脈を保持させます。

Lab 1 の状態では、エージェントはその場の質問には回答できますが、過去の会話や顧客の好みを継続的に覚えておくことはできません。

例えば、顧客が以前に「ノートPCをよく購入する」「返品条件を気にしている」と話していたとしても、別セッションになるとその情報は失われます。

AgentCore Memory を追加することで、以下のようなことが可能になります。

* 会話履歴を短期メモリとして保持する
* 顧客の嗜好や行動パターンを長期メモリとして抽出する
* 複数セッションをまたいで、顧客に合わせた応答を行う

コードのイメージとしては、ユーザーIDやセッションIDをもとにメモリを取得し、エージェントの入力に会話履歴やユーザー文脈を組み込みます。

```
from bedrock_agentcore.memory import MemoryClient

memory_client = MemoryClient(region_name="us-east-1")

user_id = "customer-001"
session_id = "session-001"

conversation_history = memory_client.get_memory(
    memory_id=memory_id,
    actor_id=user_id,
    session_id=session_id,
)

agent_input = f"""
Previous conversation:
{conversation_history}

User message:
I am looking for another laptop with a better return policy.
"""

response = agent(agent_input)

memory_client.create_event(
    memory_id=memory_id,
    actor_id=user_id,
    session_id=session_id,
    messages=[
        {
            "role": "USER",
            "content": "I am looking for another laptop with a better return policy.",
        },
        {
            "role": "ASSISTANT",
            "content": str(response),
        },
    ],
)
```

このコードで見たいポイントは、エージェント本体に会話履歴を持たせるのではなく、外部のMemoryに会話情報を保存している点です。

PoCでは、Pythonプロセス内の変数やチャット履歴配列で会話を保持しても問題ありません。

しかし、実運用では以下のような要件が出てきます。

* ユーザーごとに履歴を分けたい
* セッションをまたいで履歴を使いたい
* エージェントを再起動しても履歴を残したい
* 将来的に複数エージェントから同じ記憶を参照したい

このような要件を考えると、Memory は単なる会話ログ保存ではなく、エージェントをユーザーごとにパーソナライズするための基盤だと考えると分かりやすいです。

Lab 2 によって、Lab 1 の「その場限りのエージェント」から、「顧客の文脈を覚えて対応できるエージェント」へ近づきます。

### Lab 3: Scale with Gateway and Identity

![](https://static.zenn.studio/user-upload/7d65c560e497-20260501.png)  
Lab 3 では、AgentCore Gateway と AgentCore Identity を使って、ツール連携を本番環境に近い形へ拡張します。

Lab 1 では、エージェントがローカルのPython関数を直接呼び出していました。

しかし、実業務ではツールはローカル関数ではなく、社内API、Lambda、SaaS、データベース操作など、組織内で共有されるサービスとして管理されることが多いです。

そこで AgentCore Gateway を使い、既存の Lambda 関数などをエージェントから利用できるツールとして公開します。

イメージとしては、以下のように Gateway のエンドポイントを経由して、ツール一覧の取得やツール呼び出しを行います。

```
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

gateway_url = "https://xxxxxxxx.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"

headers = {
    "Authorization": f"Bearer {access_token}",
}

async with streamablehttp_client(gateway_url, headers=headers) as (
    read_stream,
    write_stream,
    _,
):
    async with ClientSession(read_stream, write_stream) as session:
        await session.initialize()

        tools = await session.list_tools()
        print(tools)

        result = await session.call_tool(
            name="check_warranty",
            arguments={
                "customer_id": "customer-001",
                "product_id": "laptop-123",
            },
        )

        print(result)
```

ここで重要なのは、ツールをエージェントの実装から切り離している点です。

ローカル関数を直接渡す構成では、ツールの追加・更新・認証・権限管理がエージェント実装に密結合しやすくなります。

一方で Gateway を使うと、ツールは独立した管理対象になります。

* 複数のエージェントから同じツールを共有できる
* Lambdaなど既存の処理を再利用できる
* ツール呼び出しを認証付きエンドポイントとして保護できる
* 将来的にツールの追加・変更をエージェント本体から切り離せる

また、このLabでは AgentCore Identity と Amazon Cognito を組み合わせて、Gateway のエンドポイントを JWT ベースで保護します。

```
import boto3

cognito = boto3.client("cognito-idp", region_name="us-east-1")

auth_response = cognito.initiate_auth(
    ClientId=user_pool_client_id,
    AuthFlow="USER_PASSWORD_AUTH",
    AuthParameters={
        "USERNAME": username,
        "PASSWORD": password,
    },
)

access_token = auth_response["AuthenticationResult"]["AccessToken"]
```

この `access_token` を Gateway 呼び出し時の `Authorization` ヘッダーに渡すことで、認証済みユーザーだけがツールを利用できる構成になります。

Lab 3 は、PoCでありがちな「ローカル関数をLLMに渡す」構成から、「組織内の共有ツールを安全にエージェントへ公開する」構成へ移行するステップとして理解すると分かりやすいです。

### Lab 4: Deploy the Agent to production with Observability

![](https://static.zenn.studio/user-upload/cd617ed30bbc-20260501.png)  
Lab 4 では、作成したエージェントを AgentCore Runtime にデプロイします。

ここから、Jupyter Notebook 上で動くローカルエージェントではなく、実際のリクエストを受けられるマネージドな実行環境として扱えるようになります。

AgentCore Runtime を使うことで、以下のような要素を扱えます。

* サーバーレスなエージェント実行環境
* 顧客ごとのセッション分離
* セッション継続
* CloudWatch GenAI Observability によるトレースとメトリクス

コードのイメージとしては、エージェントのエントリーポイントを定義し、Runtime にデプロイします。

```
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload):
    user_message = payload["prompt"]
    user_id = payload.get("user_id")
    session_id = payload.get("session_id")

    response = agent(user_message)

    return {
        "response": str(response),
        "user_id": user_id,
        "session_id": session_id,
    }

if __name__ == "__main__":
    app.run()
```

Runtime 側へデプロイした後は、クライアントからエージェントを呼び出します。

```
import boto3
import json

client = boto3.client("bedrock-agentcore", region_name="us-east-1")

payload = {
    "prompt": "My laptop battery drains quickly. What should I do?",
    "user_id": "customer-001",
    "session_id": "session-001",
}

response = client.invoke_agent_runtime(
    agentRuntimeArn=agent_runtime_arn,
    qualifier="DEFAULT",
    payload=json.dumps(payload),
)

print(response["response"].read().decode("utf-8"))
```

ここで大事なのは、Runtime に載せることで、エージェントが「手元で動くスクリプト」から「外部アプリケーションから呼び出せる実行単位」になる点です。

個人的に重要だと感じたのは、Runtime そのものよりも Observability です。

AIエージェントは、通常のAPIと比べて以下が追いづらくなります。

* どのツールを呼び出したのか
* なぜそのツールを選択したのか
* どのステップで失敗したのか
* 応答にどれくらい時間がかかったのか
* ユーザーの入力から最終回答までに何が起きたのか

そのため、本番運用では、単にエージェントをデプロイできるだけでなく、実行過程を追跡できることが重要になります。

Lab 4 は、「動くエージェント」を「運用できるエージェント」に近づけるためのステップでした。

### Lab 5: Evaluate Agent Performance

![](https://static.zenn.studio/user-upload/604ae44f86e0-20260501.png)  
Lab 5 では、AgentCore Evaluations を使って、エージェントの応答品質を評価します。

AIエージェントは、通常の決定的なプログラムとは異なり、同じような入力でも応答やツール選択が揺れることがあります。

そのため、本番運用では「動いているか」だけでなく、「期待した品質で動いているか」を継続的に確認する必要があります。

このLabでは、以下のような観点でエージェントを評価します。

* goal success rate
* correctness
* tool selection accuracy

例えば、評価用の問い合わせデータを用意し、それに対してエージェントを実行します。

```
evaluation_dataset = [
    {
        "input": "Can I return my smartphone after 20 days?",
        "expected_tool": "get_return_policy",
        "expected_outcome": "Customer receives smartphone return policy.",
    },
    {
        "input": "My headphones are not connecting via Bluetooth.",
        "expected_tool": "get_technical_support",
        "expected_outcome": "Customer receives troubleshooting guidance.",
    },
    {
        "input": "Do you have information about laptop warranty?",
        "expected_tool": "check_warranty",
        "expected_outcome": "Customer receives warranty information.",
    },
]
```

その後、エージェントの実行結果を評価サービスに渡して、回答品質やツール選択の妥当性を確認します。

```
from bedrock_agentcore.evaluations import EvaluationClient

eval_client = EvaluationClient(region_name="us-east-1")

evaluation_job = eval_client.create_evaluation_job(
    name="customer-support-agent-evaluation",
    agent_runtime_arn=agent_runtime_arn,
    dataset=evaluation_dataset,
    evaluators=[
        "goal_success_rate",
        "correctness",
        "tool_selection_accuracy",
    ],
)

print(evaluation_job)
```

ここで特にエージェントらしい評価指標だと感じたのが、`tool_selection_accuracy` です。

通常のチャットボットであれば、最終的な回答内容だけを評価すればよいケースもあります。

しかし、ツール利用エージェントでは、回答が自然に見えても、内部的に間違ったツールを呼んでいる可能性があります。

例えば、返品ポリシーを確認すべき問い合わせに対して、Web検索だけで回答してしまうと、最新情報らしく見えても、社内ポリシーに沿っていない可能性があります。

そのため、ツール利用エージェントでは以下のような観点が重要になります。

* 正しいツールを選べたか
* 必要な情報を取得できたか
* ユーザーの目的を達成できたか
* 回答が事実に基づいているか

Lab 5 は、エージェントを「作って終わり」にせず、品質を継続的に確認するためのステップです。

### Lab 6: Build a Customer-Facing Frontend Application

![](https://static.zenn.studio/user-upload/91cfe854003e-20260501.png)  
Lab 6 では、Streamlit を使って、顧客が利用するチャットUIを作成します。

ここまでで作成した Runtime、Memory、Identity を、実際のフロントエンドから利用する形にします。

このLabでは、以下の要素を確認できます。

* Streamlit によるチャットUI
* AgentCore Runtime へのストリーミングアクセス
* Cognito によるユーザー認証
* AgentCore Memory による会話履歴の維持

フロントエンド側では、ユーザーの入力を受け取り、AgentCore Runtime のエンドポイントへ送信します。

```
import streamlit as st
import boto3
import json

runtime_client = boto3.client("bedrock-agentcore", region_name="us-east-1")

st.title("Customer Support Agent")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_message = st.chat_input("How can I help you?")

if user_message:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    with st.chat_message("user"):
        st.write(user_message)

    payload = {
        "prompt": user_message,
        "user_id": st.session_state.get("user_id", "customer-001"),
        "session_id": st.session_state.get("session_id", "session-001"),
    }

    response = runtime_client.invoke_agent_runtime(
        agentRuntimeArn=agent_runtime_arn,
        qualifier="DEFAULT",
        payload=json.dumps(payload),
    )

    assistant_message = response["response"].read().decode("utf-8")

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": assistant_message,
        }
    )

    with st.chat_message("assistant"):
        st.write(assistant_message)
```

この段階まで進めると、AgentCore は単なるエージェント実行環境ではなく、実アプリケーションに組み込むための運用基盤として見えてきます。

Lab 1 の時点では、ローカルNotebook上で動くプロトタイプでした。

そこから Lab 6 まで進めることで、以下の要素が揃います。

* エージェントの実装
* ツール呼び出し
* 会話メモリ
* 認証
* Runtimeへのデプロイ
* 監視
* 評価
* フロントエンド連携

つまり、AIエージェントを「試しに動かす」だけでなく、「ユーザーが実際に使える形」に近づけるところまで確認できました。

### AgentCore harnessを使った実装(追加実装)

先にも説明をしましたが、AgentCore Harnessは、Runtimeで自前実装していたエージェントループを、より設定ベースで扱えるようにする新しい選択肢です。  
Runtime では「オーケストレーションコードを自分で書き、Docker コンテナに載せる」構成でしたが、Harness では「モデル・システムプロンプト・ツール・メモリを設定として宣言するだけで、オーケストレーションは AWS が管理する」構成です。

![](https://static.zenn.studio/user-upload/d5294e1e7d0d-20260501.png)

#### Harness の作成

Docker ビルドは不要で、create\_harness() の API 呼び出しだけで完了します（約 30 秒）。

```
control = boto3.client("bedrock-agentcore-control", region_name="us-east-1")

control.create_harness(
    harnessName="customer_support_harness",
    executionRoleArn=execution_role_arn,
    model={"bedrockModelConfig": {"modelId": MODEL_ID}},
    systemPrompt=[{"text": SYSTEM_PROMPT}],
    tools=[
        {
            "type": "inline_function",
            "name": "get_return_policy",
            "config": {
                "inlineFunction": {
                    "description": "Get return policy for a product category.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "product_category": {"type": "string"}
                        },
                        "required": ["product_category"],
                    },
                }
            },
        },
        # get_product_info, get_technical_support も同様
    ],
    memory={
        "agentCoreMemoryConfiguration": {
            "arn": memory_arn,
            "retrievalConfig": {
                "support/customer/{actorId}/semantic/": {
                    "topK": 3,
                    "relevanceScore": 0.2,
                },
            },
        }
    },
)
```

#### Inline Function とクライアントサイド実行

inline\_function 型のツールはクライアントサイドで実行されます。エージェントがツール呼び出しを判断すると `stopReason: "tool_use"` でストリームが停止し、制御が呼び出し元に返ります。クライアントでツールを実行し、結果を会話履歴に追加して再度 `invoke_harness` を呼ぶループを実装します。

```
conversation = [{"role": "user", "content": [{"text": user_input}]}]

while True:
    response = runtime.invoke_harness(
        harnessArn=harness_arn,
        messages=conversation,
        ...
    )

    # イベントループでテキストを yield、tool_calls を収集
    ...

    if stop_reason != "tool_use":
        break

    # ツールをクライアントで実行し、会話履歴全体に追記
    conversation = conversation + [
        {"role": "assistant", "content": assistant_content},
        {"role": "user", "content": tool_result_content},
    ]
```

#### Runtime との比較

| 項目 | Runtime | Harness |
| --- | --- | --- |
| セットアップ | Docker ビルド（約 10 分） | API 呼び出し（約 30 秒） |
| オーケストレーション | 自前（任意フレームワーク） | AWS 管理（Strands のみ） |
| ツール実行 | サーバーサイド | Inline function はクライアントサイド |
| SSE | 自前実装（思考プロセスが混入しやすい） | 組み込み・クリーン |
| 実行制限 | コード内で自前実装 | maxIterations / timeoutSeconds を宣言的に設定 |

「カスタムロジックが少なく素早く立ち上げたい」なら Harness、「既存フレームワーク資産や複雑なオーケストレーションを活かしたい」なら Runtime が現実的な判断基準になると感じました。

## まとめ

各パブリッククラウドにおける AI Agent Platformサービスを整理しつつ、  
AWSの公式ワークショップに沿って、Amazon Bedrock AgentCoreを使った実装を進めることで、今出来ることと出来ないこと、サービス構成要素と特徴を一通り把握することができたのではないかと思います。

最後までお読みいただき、ありがとうございました。
