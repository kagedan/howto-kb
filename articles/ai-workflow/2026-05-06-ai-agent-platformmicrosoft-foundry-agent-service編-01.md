---
id: "2026-05-06-ai-agent-platformmicrosoft-foundry-agent-service編-01"
title: "AI Agent Platform（Microsoft Foundry Agent Service編）"
url: "https://zenn.dev/cozy07/articles/f566129fdb59d3"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "prompt-engineering", "API", "AI-agent", "LLM", "OpenAI"]
date_published: "2026-05-06"
date_collected: "2026-05-07"
summary_by: "auto-rss"
query: ""
---

## はじめに

こんにちは🙌  
AI Agentの企業導入は、PoCで試す段階から、実業務に組み込む段階へ進みつつあります。

そこで重要になるのが、AI Agentの実行環境です。エージェントはLLMを呼び出すだけではなく、外部ツールを使い、ユーザーやシステムの権限を扱い、会話履歴や業務文脈を保持し、実行過程を監視・評価する必要があります。  
各クラウドベンダーもAI Agent Platformと呼べるサービス群を整備し始めています。

本記事では、Microsoft Foundry Agent Service を実際に試しながら、どのような特徴を持つサービスなのかを整理します。

他クラウドでの AI Agent Platform も同様に記事を書いているので、ぜひご覧ください。  
<https://zenn.dev/cozy07/articles/4275fd95352ab1>  
<https://zenn.dev/cozy07/articles/97a0f1cd463cc3>

## ゴール

* Microsoft Foundry Agent Service が、AI エージェントの開発だけでなく、実行・ツール連携・ナレッジ参照・会話状態管理・監視・ガバナンスまでを扱うプラットフォームであること
* Azure AI Foundry の SDK を使って、コードファーストにエージェントを作成する流れ
* Function Calling / File Search / Code Interpreter / Bing Grounding などの Tool を使い、エージェントが外部機能やデータを扱う流れ
* Azure AI Search、SharePoint、Microsoft Fabric、Logic Apps など Microsoft エコシステムとの連携の考え方
* エンタープライズ利用で必要になる認証、RBAC、ネットワーク、データ管理、Observability の確認観点

## Microsoft Foundry Agent Service

<https://learn.microsoft.com/ja-jp/azure/foundry/agents/overview>

### Microsoft Foundry Agent Serviceとは

![](https://static.zenn.studio/user-upload/8d1016582711-20260506.png)

Microsoft Foundry Agent Service は、Microsoft Foundry が提供する AI エージェント向けのマネージドサービスです。

エージェントを作るだけではなく、デプロイ、スケーリング、ツール連携、ナレッジ参照、メモリ、監視、ガバナンスまでを含めて扱うための基盤として位置づけられています。

公式ドキュメントでは、AI エージェントを構築、デプロイ、スケーリングするためのフルマネージドプラットフォームとして説明されています。Foundry のモデルカタログにある複数のモデルを利用でき、Foundry portal で no-code の prompt agent を作ることも、SDK / REST API からコードベースの hosted agent をデプロイすることもできます。

Microsoft Foundry Agent Service には、Prompt agents、Workflow agents、Hosted agents という複数のエージェントタイプがあります。Prompt agents は、指示文・モデル・ツールを設定として定義するエージェントです。Workflow agents は、複数ステップの自動化や分岐を扱うためのエージェントです。Hosted agents は、自分で書いたエージェントコードや Agent Framework / LangGraph などで作ったエージェントをコンテナとしてマネージド実行環境に載せる方式です。

そのため、単体のエージェント SDK というより、AI エージェントを業務アプリケーションとして運用するための実行・連携・管理基盤と考えると分かりやすいです。

### Microsoft Foundry Agent Serviceの構成要素

![](https://static.zenn.studio/user-upload/1c083f14b45b-20260506.png)

Microsoft Foundry Agent Service は、AI エージェントを作成し、実行し、業務システムと接続して運用するための機能群として整理すると分かりやすいです。

Foundry portal で no-code の Prompt agent を作ることも、SDK / REST API からコードベースの Hosted agent をデプロイすることもできます。

| 領域 | 主な構成要素 | 役割 |
| --- | --- | --- |
| Build | Prompt agents, Workflow agents, Hosted agents, Agent Framework | エージェントを作る |
| Extend | Tools, Function Calling, Code Interpreter, File Search, Web Search, MCP, OpenAPI | 外部機能やデータに接続する |
| Ground | Knowledge, Azure AI Search, SharePoint, Microsoft Fabric, Bing | データを根拠に回答する |
| Remember | Memory | セッションを跨いだ文脈を保持する |
| Observe | Tracing, Evaluation, Monitoring | 実行過程と品質を確認する |
| Govern | Microsoft Entra ID, RBAC, Managed Identity, VNet, BYO resources, Guardrails | 認証・ネットワーク・データ管理を統制する |
| Distribute | Publish, Microsoft 365 Copilot, Teams, Entra Agent Registry | 作成したエージェントを利用者に届ける |

大きく見ると、Build はエージェント作成、Extend / Ground は外部機能やデータ接続、Remember / Observe / Govern は本番運用のための領域です。

特に業務利用では、Tool を呼べることだけでなく、誰の権限でデータにアクセスするのか、会話履歴やファイルをどこに保存するのか、実行過程をどう追跡するのかが重要になります。

Microsoft 365 / Teams / SharePoint / Fabric / Logic Apps などへ展開しやすい点も、Microsoft らしい特徴です。

## Microsoft Agent Framework

<https://github.com/microsoft/agent-framework>

Microsoft Foundry Agent Service は Foundry portal から no-code / low-code で試せます。一方で、アプリケーションに組み込む場合や、エージェントの挙動をコードとして管理したい場合は、フレームワークを使うことで、よりコードファーストに実装できます。

Microsoft の新しいエージェント基盤は、設計思想としての Microsoft Agent Framework (MAF) と、それを Azure 上で実装・操作するための Azure AI Projects SDK があります。本記事では、この SDK を使った実装方法を解説します。

Python では、Azure AI Projects SDK を使って Foundry project に接続し、Agent の作成、Conversation の作成、Response の生成、Tool の追加、ストリーミングなどをコードから扱えます。Foundry Agent Service の runtime components は Agent / Conversation / Response を中心に整理されており、Agent はモデル・instructions・tools をまとめた定義、Conversation は複数ターンの会話履歴、Response はユーザー入力に対して生成される実行結果として扱われます。

今回の記事では、公式ワークショップで使われている Python のコードファーストな流れをベースに、Foundry Agent Service SDK でエージェントを作り、Tool を追加し、会話を実行する流れを確認します。

### コードファーストでエージェントを作る

SDK を使うと、エージェントの作成から実行までをコードで管理できます。

Foundry portal で設定を作るだけでなく、モデル、instructions、tools、conversation、response 生成処理をコードとして表現できます。これにより、アプリケーション側のロジック、CI/CD、環境差分管理、テストと組み合わせやすくなります。

大まかな流れは、Project client を作成し、Agent を作成し、Conversation を作り、その Conversation に対して Response を生成する形です。

```
agent = project.agents.create_version(
    agent_name="sales-assistant",
    definition=PromptAgentDefinition(
        model="gpt-5-mini",
        instructions="あなたは売上データを分析するアシスタントです。",
    ),
)

# 実行（Responseの作成）
response = project.agents.responses.create(
    agent_name=agent.name,
    agent_version=agent.version,
    conversation_id=conversation.id,
    input="先月の売上を教えてください。",
)
```

実際の API 名や書き方は SDK のバージョンで変わる可能性がありますが、考え方としては、Foundry project に接続し、Agent を作成し、Conversation を作成し、Response を生成する、という流れになります。

Gemini の ADK では Agent を定義して Runner で実行する形でしたが、Azure では Foundry Agent Service 側の runtime components として Agent / Conversation / Response を扱う、という違いがあります。

### Agent / Conversation / Response の関係

Foundry Agent Service では、Agent / Conversation / Response の関係を次のように理解すると分かりやすいです。

```
Agent
  └─ モデル、instructions、tools を持つ

Conversation
  └─ 複数ターンの会話履歴を保持する

Response
  └─ Agent が Conversation の文脈とユーザー入力を処理して生成する結果
```

この構造を理解しておくと、会話状態をどこで持つのか、長期記憶は Memory に分けるのか、Tool の結果をどう回答に反映するのかが整理しやすくなります。

SDK では、Agent に Tool を追加することで、モデル単体ではできない処理を扱えます。

代表的な Tool は次の通りです。

| Tool | 役割 |
| --- | --- |
| Function Calling | アプリケーション側で定義した関数を呼び出す |
| File Search | アップロードしたファイルやドキュメントを検索する |
| Code Interpreter | Python を実行して分析・計算・可視化する |
| Web Search / Bing Grounding | Web 情報を取得し、citation 付きで回答する |
| Azure AI Search | Azure AI Search のインデックスを参照する |
| MCP Tool | MCP サーバ上のツールを呼び出す |
| OpenAPI Tool | OpenAPI 定義をもとに外部 HTTP API を呼び出す |

Tool の選択は、基本的にはモデルが instructions と Tool 定義を見て判断します。公式ドキュメントでも、Tool の説明や instructions に「いつどの Tool を使うべきか」を明確に書くことが重要とされています。tool\_choice を使うと、Tool 呼び出しを auto、required、none のように制御できます。

今回採用するワークショップでは、Function Calling、File Search、Code Interpreter、Bing Grounding などを順番に試せるため、Agent Service における Tool の考え方を理解するにはちょうどよい構成になっています。

### Foundry portal と SDK の使い分け

Microsoft Foundry Agent Service は、Foundry portal と SDK / REST API の両方から利用できます。

Foundry portal は、エージェントのプロトタイピングや動作確認に向いています。モデル、instructions、tools を画面から設定し、playground で会話を試しながら、Tool の呼び出しや回答の挙動を確認できます。Prompt agent のように、設定中心で作れるエージェントであれば、portal だけでもかなり試せます。

一方で、SDK はアプリケーションに組み込む場合や、コードとして管理したい場合に向いています。

ざっくり整理すると次のようになります。

| 方法 | 向いている用途 |
| --- | --- |
| Foundry portal | プロトタイピング、Prompt agent 作成、Tool 設定の確認、Playground での検証 |
| SDK / REST API | アプリ組み込み、CI/CD、コード管理、Conversation 制御、独自 UI との統合 |
| Hosted agent | Agent Framework / LangGraph / 独自コードで作ったエージェントのマネージド実行 |

この記事では、portal だけで完結する使い方ではなく、公式ワークショップに沿って Python SDK を使い、コードファーストにエージェントを作る流れを中心に見ていきます。

## 試してみる

### 採用するチュートリアル

<https://microsoft.github.io/build-your-first-agent-with-azure-ai-agent-service-workshop/>

### 1: 基本のエージェントを作る

#### Agent Service SDKを使う

`FoundryChatClient` を エンドポイント + モデル + 資格情報 の 3 点で初期化します。モデル指定は ChatClient 側で、後段の Agent には渡しません。

```
from agent_framework.foundry import FoundryChatClient
from azure.identity.aio import DefaultAzureCredential

async with DefaultAzureCredential() as credential:
    client = FoundryChatClient(
        project_endpoint="https://<resource>.services.ai.azure.com/api/projects/<project>",
        model="gpt-4o-mini",
        credential=credential,
    )
```

#### instructionsでエージェントの振る舞いを定義する

`client.as_agent(instructions=...)` が system prompt 相当です。検証時はインライン文字列で十分。本番は外部ファイル化 + `str.replace` で動的値（DB スキーマ等）を差し込むのが定石。

#### Conversationを作成する

LLM はステートレスなので、過去ターンを覚えさせるには履歴連結が必要。MAF はこれを `AgentSession` に閉じ込めます。`agent.create_session()` で生成し、`run()` 呼び出しに渡します。渡し忘れると毎回独立した会話扱いになります。

#### Responseを生成する

`agent.run()` は一括応答とストリーミングの 2 通り。

```
result = await agent.run("Hello", session=session)         # 一括
async for chunk in agent.run("Hello", session=session, stream=True):  # 逐次
    if chunk.text:
        print(chunk.text, end="", flush=True)
```

classic では EventHandler を継承する必要があった箇所が、`async for` ループ 1 つで済みます。

#### 複数ターンの会話を試す

ここまでを組み合わせた最終形です。

```
import asyncio
from agent_framework.foundry import FoundryChatClient
from azure.identity.aio import DefaultAzureCredential

async def main() -> None:
    async with DefaultAzureCredential() as credential:
        client = FoundryChatClient(
            project_endpoint="https://<resource>.services.ai.azure.com/api/projects/<project>",
            model="gpt-4o-mini",
            credential=credential,
        )
        agent = client.as_agent(
            name="Contoso Hello Agent",
            instructions="You are a friendly assistant for Contoso. Keep responses concise.",
        )
        session = agent.create_session()
        while True:
            prompt = input("\nYou: ").strip()
            if not prompt or prompt.lower() == "exit":
                break
            async for chunk in agent.run(prompt, session=session, stream=True):
                if chunk.text:
                    print(chunk.text, end="", flush=True)
            print()

asyncio.run(main())
```

`session` を渡せば前ターンを記憶し、外せば忘れる、というのがコード 1 行の差で確かめられます。なお `instructions` の内容によっては、範囲外と判断された質問に定型応答を返す挙動になるので、文脈引き継ぎを試すときは指示文と整合する話題で確認してください。

これで MAF の単一エージェント API のコア（`ChatClient` / `AIAgent` / `AgentSession` / Streaming）が揃いました。次は `@tool` デコレータで Python 関数を渡し、Function Calling に進みます。

### 2: Function Callingで外部ロジックを呼び出す

Lab 1 のエージェントは LLM の知識だけで応答していました。ここでは Python 関数を Tool としてエージェントに渡し、LLM が必要に応じて呼び出せるようにします。題材は「Contoso 売上データを SQLite から取得する関数」です。

#### Function Callingとは

LLM に「外部システムへ問い合わせる能力」を与える仕組みです。LLM は次の判断を自動で行います。

1. ユーザー質問に答えるために関数を呼ぶべきか
2. どの関数を呼ぶべきか
3. その関数に渡す引数の値

関数の実装は開発者の責任。LLM はあくまで「いつ、どう呼ぶか」を決めるだけで、実行はアプリ側が行います。

#### 売上データに対してSQLを実行する

ベースになる関数は SQLite に対する任意クエリ実行です。引数の SQL は LLM が動的に組み立てます。

```
async def async_fetch_sales_data_using_sqlite_query(self, sqlite_query: str) -> str:
    async with self.conn.execute(sqlite_query) as cursor:
        rows = await cursor.fetchall()
        columns = [d[0] for d in cursor.description]
    return pd.DataFrame(rows, columns=columns).to_json(orient="split")
```

DB は読み取り専用で接続するのがセキュリティ的に必須。LLM が破壊的 SQL を生成するリスクをそもそも遮断します。

#### LLMが関数を選択し、引数を生成する流れ

MAF では `@tool` デコレータを付け、引数に `Annotated[type, Field(description=...)]` で説明を付けるだけで、関数スキーマが LLM に自動公開されます。

```
from typing import Annotated
from agent_framework import tool
from pydantic import Field

@tool
async def fetch_sales_data_using_sqlite_query(
    sqlite_query: Annotated[
        str,
        Field(description="A well-formed SQLite query. Always include LIMIT 30."),
    ],
) -> str:
    """Run a SQLite query against the Contoso sales database and return JSON."""
    return await sales_data.async_fetch_sales_data_using_sqlite_query(sqlite_query)
```

`description` と docstring は LLM が「いつこの関数を呼ぶか」を判断する材料そのもの。曖昧に書くと選んでくれなかったり、誤った引数を作ったりするので、ツール定義の品質が直接エージェントの精度に効きます。

`as_agent()` の `tools=[...]` に関数を列挙すれば、あとは MAF が自動で「LLM 呼び出し → ツール実行 → 結果を LLM に返す」のループを回し、最終回答が出るまで繰り返します。

```
agent = client.as_agent(
    name="Contoso Sales Agent",
    instructions=instructions,
    tools=[fetch_sales_data_using_sqlite_query],
)
session = agent.create_session()

async for chunk in agent.run("What are the sales by region?", session=session, stream=True):
    if chunk.text:
        print(chunk.text, end="", flush=True)
```

実際に使ってみた結果が以下のようになっています。正しく Function Call Toolが使えていそうですね。

```
Enter your query (type exit to finish): What are the sales by region?

Function Call Tool: async_fetch_sales_data_using_sqlite_query
Executing query: SELECT region, SUM(revenue) AS total_sales FROM sales_data GROUP BY region LIMIT 30

Here are the total sales by region for Contoso:

| Region        | Total Sales  |
|---------------|--------------|
| AFRICA        | 5,227,467    |
| ASIA-PACIFIC  | 5,363,718    |
| CHINA         | 10,540,412   |
| EUROPE        | 9,990,708    |
| LATIN AMERICA | 5,386,552    |
| MIDDLE EAST   | 5,312,519    |
| NORTH AMERICA | 15,986,462   |

If you would like more details or sales data for a specific region or time period, please let me know!
```

### 3: File Searchで社内データを参照する

Lab 2 のエージェントは SQLite に入っている売上データなら答えられますが、テント製品のブランドや素材といったカタログ情報は持っていません。これを補うために、製品データシート PDF を Foundry の Vector Store に登録し、エージェントから検索できるようにします。

#### File Searchとは

社内ドキュメントや PDF を LLM の回答源にするための、Foundry が提供する Hosted な RAG (Retrieval Augmented Generation) ツールです。流れは次の 3ステップ。

1. ファイルを Vector Store にアップロード（自動で chunk 分割 + embedding 生成）
2. ユーザー質問が来たら、LLM が必要に応じて Vector Store を意味検索
3. 検索結果と引用情報が LLM に返り、回答が組み立てられる

Lab 2 の `@tool` で渡した関数が「自分で書いた処理」だったのに対し、File Search は「プロバイダー側がホストする処理」を呼ぶ Hosted ツールです。検索インデックスや埋め込みモデルの運用は Foundry に任せられます。

#### ファイルをVector Storeに登録する

ファイルをアップロードすると、Foundry が次の規則で前処理します。

* chunk 分割: 800 トークンずつ、overlap 400
* 埋め込みモデル: `text-embedding-3-large` で 256 次元
* 容量上限: 1 Vector Store あたり 10,000 ファイル / 1 ファイル 512 MB

クライアントコードからは「アップロード → Vector Store 作成」を呼ぶだけです。

```
file_info = await client.files.upload(path="datasheet/contoso-tents-datasheet.pdf")
vector_store = await client.vector_stores.create(
    file_ids=[file_info.id],
    name="Contoso Product Information Vector Store",
)
```

Vector Store は Foundry 側に永続化されます。アプリ起動のたびに作り直す実装はクォータと容量課金を圧迫するので、本番では Vector Store ID を環境変数で固定して再利用します。

#### 検索結果をコンテキストとして回答に使う

`client.get_file_search_tool(vector_store_ids=[...])` で Hosted ツールを取得し、Function Tool と同じく `tools=[...]` に列挙します。両者の併用が可能で、LLM がユーザー質問に応じて使い分けます。

```
file_search_tool = client.get_file_search_tool(vector_store_ids=[vector_store.id])

agent = client.as_agent(
    name="Contoso Sales Agent",
    instructions=instructions,
    tools=[
        fetch_sales_data_using_sqlite_query,   # Function Tool
        file_search_tool,                      # Hosted Tool
    ],
)
```

応答には citation（引用元のファイル名や chunk） が自動で付与されます。「この情報はどのファイルから引いてきたのか」が明示されるので、検証可能性とハルシネーション抑制の両方に効きます。

#### RAG的な検索をAgent Serviceで扱う

自前で RAG を組む場合（LangChain + Pinecone / pgvector など）と比べた特徴は次のとおり。

| 観点 | 自前 RAG | Foundry の File Search |
| --- | --- | --- |
| 埋め込みモデル | 自由選択 | `text-embedding-3-large` 固定 |
| chunk 戦略 | 自由 | 800 / overlap 400 固定 |
| ベクター DB | 自分で運用 | Foundry が管理 |
| Citation | 自前実装 | 自動付与 |
| 細かいチューニング | 高い | 低い |

「コードを最小化して RAG をすぐ動かす」用途は Hosted File Search が圧倒的に楽。逆に「埋め込みモデル選定や chunk 戦略を最適化したい」場合は自前実装の余地があります。

### 4: Code Interpreterで分析・可視化する

Lab 3 までで「売上 DB から取る (SQL)」「社内 PDF から取る (File Search)」ができるようになりました。次は取得したデータに対して集計や可視化を行えるようにします。MAF / Foundry の Code Interpreter を使うと、LLM が動的に Python を書いてサンドボックスで実行し、PNG や CSV を返してくれます。

#### Code Interpreterとは

LLM が「Python コードを書く → サンドボックスで実行する → 結果を受け取る」ループを自動で回す Hosted ツールです。実行基盤は Azure Container Apps Dynamic Sessions 上の Hyper-V 隔離コンテナ。

| 仕様 | 内容 |
| --- | --- |
| セッション | 1 conversation = 1 session、最大 1 時間 / アイドル 30 分で破棄 |
| 外向きネットワーク | 不可（追加 `pip install` も不可） |
| プリインストール | pandas / numpy / matplotlib / scikit-learn / pillow など |

LLM が書いた未知のコードを安全に走らせる基盤を自前で組むのは骨が折れますが、Hosted ツールならインスタンス管理ゼロで使えます。

#### データ分析を実行する

`client.get_code_interpreter_tool()` を呼び、Function Tool と並べて `tools=[...]` に渡します。事前リソース作成は不要。

```
code_interpreter_tool = client.get_code_interpreter_tool()

agent = client.as_agent(
    name=Config.AGENT_NAME,
    instructions=instructions,
    tools=[fetch_sales_data_using_sqlite_query, code_interpreter_tool],
)
```

`instructions` 側で「売上の取得は Function、その先の集計・描画は Code Interpreter」と書き分けるとツール選択が安定します。

#### グラフを生成する

Code Interpreter は `plt.savefig('/mnt/data/xxx.png')` でサンドボックス内にファイルを書きます。応答チャンクの `chunk.text` には現れないので、生成物の取得には別ルートが必要です。

実用上は 非ストリーミングで完走させて完了レスポンスを掘るのが楽です。`agent_framework` は OpenAI Responses API のレスポンスを `result.raw_representation.raw_representation` に保持しているので、そこから次を拾います。

* `ResponseCodeInterpreterToolCall.code` / `.outputs[]` — 生成された Python コードと stdout
* `output_text.annotations[]` の `container_file_citation` — 生成ファイルの `file_id` / `container_id`

ファイル本体は OpenAI クライアントの Containers Files API で取得します。OpenAI クライアントは `AIProjectClient.get_openai_client()` から払い出せます。

```
result = await agent.run(prompt, session=session)   # stream=True にしない
resp = await openai_client.containers.files.content.retrieve(
    file_id=ann.file_id, container_id=ann.container_id,
)
(Path("shared/files") / Path(ann.filename).name).write_bytes(await resp.aread())
```

`ResponseCodeInterpreterToolCall.code` を都度ターミナルに表示しておくと、classic 版にあった「`show code` で生成コードを確認」のデバッグ動線が再現できます。

#### 自然言語から分析タスクを実行する

複数ツールを併用して、1 ターンで「SQL で取得 → Code Interpreter で集計 → matplotlib で描画 → ファイル保存」までを LLM が組み立てます。たとえば次のような依頼が通ります。

* `Show sales by region as a pie chart` → 円グラフ PNG
* `Download as CSV file` → 直前の結果を CSV 出力
* `Simulate future sales by region using a Monte Carlo simulation. Show as a Line with Confidence Bands.`

![](https://static.zenn.studio/user-upload/6a25608a0024-20260506.png)  
*ヒートマップ作成例（日本語フォントが無く、文字化けしています）*

開発者が事前に「ヒートマップ生成関数」「モンテカルロ実行関数」等を実装する必要はありません。自然言語を中間言語にして、SQL と Python を LLM が橋渡しするのが Code Interpreter 入りエージェントの本質です。

### 5: Bing Groundingで外部情報を参照する

ここまでは Contoso の社内データに閉じた世界でした。次は Web 上の最新情報を引っ張ってくる Foundry の Grounding with Bing Search を入れます。結論を先に書くと、`agent-framework 1.2.2` 時点では MAF の `as_agent` 経由で Foundry Bing Grounding を呼ぶ手段はなく、OpenAI client 直叩きの hybrid 構成になります。

#### Grounding with Bing Searchとは

Foundry が提供する Bing 検索ツールです。LLM が必要に応じてクエリを生成し、検索結果のスニペットと URL がコンテキストに注入され、応答に `url_citation` annotation（タイトル + URL）が付きます。

事前に `Microsoft.Bing` プロバイダ登録、`Microsoft.Bing/accounts` リソース、Foundry account の Bing connection（`isSharedToAll=true`）が必要です。本リポジトリでは `infra/bing-grounding.bicep` で一括デプロイします。検索クエリ単位の従量課金。

#### Web情報を使って回答を補強する

`FoundryChatClient.get_web_search_tool()` は名前に反して Foundry の Bing Grounding を呼びません。実装は OpenAI 標準の `WebSearchTool` を構築するだけで、Bing connection は何も渡していません。実機では `web_search_call.action.sources=null`、citation なし、LLM が training data から捏造する状態になります。

代わりに `AIProjectClient.get_openai_client()` 経由の OpenAI client 直叩きで `bing_grounding` tool を呼びます。connection ID は project スコープ（`/accounts/<A>/projects/<P>/connections/<C>`）でなければ `not found` を返します。

```
async def run_bing_grounding(openai_client, prompt, instructions):
    return await openai_client.responses.create(
        model=Config.API_DEPLOYMENT_NAME,
        instructions=instructions,
        input=prompt,
        tools=[{
            "type": "bing_grounding",
            "bing_grounding": {
                "search_configurations": [
                    {"project_connection_id": PROJECT_CONNECTION_ID}
                ]
            },
        }],
    )
```

#### Citation付きの回答を確認する

OpenAI client から返る生 `Response` の `output[].content[].annotations[]` を辿り、`type == "url_citation"` を取り出します。

```
result = await run_bing_grounding(openai_client, prompt, instructions)
for o in result.output:
    if getattr(o, "type", None) != "message":
        continue
    for c in o.content or []:
        for ann in getattr(c, "annotations", None) or []:
            d = ann.model_dump() if hasattr(ann, "model_dump") else dict(ann)
            if d.get("type") == "url_citation":
                print(d.get("title"), d.get("url"))
```

#### 社内データと外部データの使い分け

| データ種別 | ツール | 経路 |
| --- | --- | --- |
| 売上 / 数値 | Function Calling | MAF `as_agent(tools=[fn])` |
| 社内ドキュメント | File Search | MAF `client.get_file_search_tool(...)` |
| 計算 / 可視化 | Code Interpreter | MAF `client.get_code_interpreter_tool()` |
| 外部 Web 情報 | Bing Grounding | OpenAI client 直叩き |

ディスパッチはキーワードベースか、LLM に「Bing が必要か」を 1 ターン目で判定させる方法もあります。Web Search はクエリが外部に送信される性質上、機密情報の取り扱いを `instructions` 側で明示的に縛るのが安全です。MAF の hosted tool ヘルパーが Foundry 固有機能をカバーしきれていない箇所は、OpenAI client 直叩きで補完するのが現時点の実用パターンです。

### 6: Observabilityで実行過程を確認する

MAF は OpenTelemetry GenAI セマンティック規約のスパンを自動発行するので、Application Insights に流して原因切り分けに使います。

#### 実行履歴を確認する

`infra/observability.bicep` で Log Analytics + App Insights + Foundry connection (`category: 'AppInsights'`) を作っておけば、エージェント生成前の 1 行で済みます。

```
await client.configure_azure_monitor(enable_sensitive_data=True)
```

Application Insights の Transaction search や Foundry Portal の Tracing タブで End-to-end が見えます。

#### Foundry Connection が他プラットフォームと違うところ

`configure_azure_monitor()` が引数ゼロで動くのも、Lab 5 の Bing Grounding が `project_connection_id` 1 つで呼べるのも、外部リソースへの接続情報を ARM 上の Connection リソースとして抽象化し SDK が「種類」で自動解決する Foundry の設計のおかげです。

| プラットフォーム | 外部リソース接続の管理 |
| --- | --- |
| Foundry | Connection = ARM リソース、category で抽象化、SDK が自動発見 |
| OpenAI Assistants / Responses | tool ごとに ID / API key を直接渡す |
| Amazon Bedrock Agents | Knowledge Base / Action Group は agent 内部の構成要素、再利用不可 |
| LangChain / AutoGen | SDK 任せ、credential も自前管理 |

![](https://static.zenn.studio/user-upload/555ca484a9b3-20260506.png)

## Microsoft Foundry Agent Serviceが向いていそうなケース

当たり前の話でありますが、相性がよいのは、Microsoft 365 や Azure をすでに業務基盤として使っているケースかとおもいます。  
SharePoint、Teams、Microsoft 365 Copilot、Azure AI Search、Microsoft Fabric、Logic Apps などと接続しやすく、社内データを参照しながら業務フローに組み込むエージェントを作りやすい構成になっています。

また、認証や権限管理を Microsoft Entra ID / Azure RBAC / Managed Identity に寄せられるため、エンタープライズ利用で避けて通れない「誰が、どの権限で、どのデータにアクセスするのか」を Azure の統制モデルに乗せやすい点も大きいです。

一方で、正直な所、SDK や Tool 周りは発展途上の印象もあります。今回試した範囲でも、MAF 経由で素直に扱える Tool と、OpenAI client を直接使った方がよい Tool が混在していました。そのため、すべてを抽象化された Agent Framework だけで完結させるというより、Foundry の Connection / Hosted Tool / OpenAI Responses API を組み合わせて使う理解が必要になります。

向いていそうなケースを整理すると、次のようになります。

| ケース | 理由 |
| --- | --- |
| Microsoft 365 / Teams / SharePoint を業務基盤にしている | 既存の業務データや利用者接点にエージェントを組み込みやすい |
| Azure AI Search / Fabric / Logic Apps など Azure 資産と連携したい | Azure 上のデータ・ワークフローと接続しやすい |
| エージェントを API や Teams / Copilot に配布したい | 作ったエージェントを業務チャネルへ展開しやすい |
| 認証・RBAC・Managed Identity・VNet を重視したい | エンタープライズ向けの統制を Azure の仕組みに寄せられる |
| Function Calling / File Search / Code Interpreter / Web Search をまとめて試したい | Hosted Tool とカスタム Function を組み合わせて検証しやすい |
| コードファーストで実装しつつ、Portal でも動作確認したい | SDK と Foundry portal の両方を使える |

逆に、Azure / Microsoft 365 との連携が薄い場合や、RAG の chunk 戦略・embedding モデル・検索基盤を細かく制御したい場合は、自前 RAG や LangGraph / LangChain ベースの構成の方が合う場面がありそうです。

## まとめ

Microsoft Foundry Agent Service を触ってみると、単体の Agent SDK というより、AI エージェントを業務システムとして運用するためのプラットフォームとして設計されていることが分かります。

Agent / Conversation / Response を中心に、Function Calling、File Search、Code Interpreter、Bing Grounding などの Tool を組み合わせることで、外部データ参照、業務ロジック実行、分析・可視化、Web 情報の取得まで扱えます。

また、Foundry connection によって Application Insights や Bing Grounding などの外部リソース接続を Azure リソースとして管理できる点も特徴的でした。コードに secret や connection string を埋め込まず、Bicep / RBAC / Managed Identity と合わせて管理できるのは、実運用では重要なポイントです。

一方で、現時点では Agent Framework、Azure AI Projects SDK、OpenAI Responses API、Foundry portal の責務がやや重なって見える部分もあります。特に Hosted Tool 周りは、MAF のヘルパーだけで完結するものと、OpenAI client を直接使った方がよいものがあり、実装時にはどのレイヤーの API を使っているのかを意識する必要がありました。

総じて、Microsoft Foundry Agent Service は、Microsoft 365 / Azure を中心に業務 AI エージェントを作りたい企業にとって有力な選択肢になりそうです。

最後までお読みいただき、ありがとうございました！
