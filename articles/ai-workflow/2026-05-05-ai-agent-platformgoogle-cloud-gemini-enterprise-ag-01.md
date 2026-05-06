---
id: "2026-05-05-ai-agent-platformgoogle-cloud-gemini-enterprise-ag-01"
title: "AI Agent Platform（Google Cloud Gemini Enterprise Agent Platform編）"
url: "https://zenn.dev/cozy07/articles/97a0f1cd463cc3"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "API", "AI-agent", "LLM", "zenn"]
date_published: "2026-05-05"
date_collected: "2026-05-06"
summary_by: "auto-rss"
---

## はじめに

こんにちは🙌  
AI Agentの企業導入は、PoCで試す段階から、実業務に組み込む段階へ進みつつあります。

そこで重要になるのが、AI Agentの実行環境です。エージェントはLLMを呼び出すだけではなく、外部ツールを使い、ユーザーやシステムの権限を扱い、会話履歴や業務文脈を保持し、実行過程を監視・評価する必要があります。  
各クラウドベンダーもAI Agent Platformと呼べるサービス群を整備し始めています。

本記事では、Gemini Enterprise Agent Platformを実際に試しながら、どのような特徴を持つサービスなのかを整理します。

他クラウドでの AI Agent Platform も同様に記事を書いているので、ぜひご覧ください。  
<https://zenn.dev/cozy07/articles/4275fd95352ab1>

## ゴール

* Gemini Enterprise Agent Platform が、AI エージェントの開発だけでなく、実行・記憶・評価・監視・外部ツール連携までを扱うプラットフォームであること
* ADK を使ってエージェントを作成する流れ
* 作成したエージェントを Agent Runtime にデプロイし、Sessions / Memory Bank による会話状態と長期記憶の扱い方と Agent Evaluation / Observability を使った品質評価とデバッグの考え方
* Workspace 連携により、Google Calendar などの Google API をエージェントのツールとして扱う方法

## Gemini Enterprise Agent Platform

<https://cloud.google.com/blog/products/ai-machine-learning/introducing-gemini-enterprise-agent-platform>

## Gemini Enterprise Agent Platformとは

Gemini Enterprise Agent Platform は、Google Cloud が提供する AI エージェント向けの統合プラットフォームです。

エージェントを作るだけではなく、実行、スケーリング、ガバナンス、評価、監視までを含めて扱うための基盤として位置づけられています。

公式ドキュメントでは、エンタープライズグレードの AI エージェントとモデルベースのソリューションを構築、デプロイ、ガバナンス、最適化するための統合プラットフォームとして説明されています。

2026年4月の発表では、Gemini Enterprise Agent Platform は、従来の Vertex AI / Agent Platform のエージェント関連機能を発展させ、エージェントの構築、実行、ガバナンス、最適化までを統合的に扱うプラットフォームとして紹介されています。従来のモデル選択、モデル構築、エージェント構築の機能に加えて、エージェント統合、DevOps、オーケストレーション、セキュリティの機能をまとめたものです。

そのため、単体のエージェントフレームワークというより、AIエージェントを業務システムとして運用するための実行・管理基盤と考えると分かりやすいです。

ADK でエージェントを開発し、Agent Runtime で実行し、Memory Bank で文脈を保持し、Evaluation や Observability で品質と実行過程を確認する、といった一連の流れを支えるプラットフォームです。

## Gemini Enterprise Agent Platformの構成要素

![](https://static.zenn.studio/user-upload/629767d310a0-20260505.png)

Gemini Enterprise Agent Platform は、Build / Scale / Govern / Optimize の4つで整理すると分かりやすいです。

| 領域 | 主な構成要素 | 役割 |
| --- | --- | --- |
| Build | ADK, Tools, Agent Studio / Agent Designer | エージェントを作る |
| Scale | Agent Runtime, Sessions, Memory Bank, Code Execution, Computer Use | エージェントを実行・拡張する |
| Govern | Agent Identity, Agent Gateway, Model Armor | セキュリティと統制を担う |
| Optimize | Observability, Evaluation, Agent Simulation | 評価・監視・改善を行う |

### Build：エージェントを作る

エージェントを開発するための領域です。

#### ADK

エージェントをコードで開発するためのオープンソースフレームワークです。エージェント、ツール、マルチエージェント構成を定義し、ローカルで開発・デバッグしたうえで、Agent Runtime や Cloud Run、GKE などへデプロイできます。

エージェントが外部サービスや業務システムと連携するための仕組みです。LLM単体で回答するだけでなく、ツールを呼び出して業務タスクを実行できるようにします。

#### Agent Studio / Agent Designer

業務ユーザーや非エンジニアでもエージェントを作れる no-code / low-code の入口となっています。この記事では扱いません。

### Scale：エージェントを実行・拡張する

作成したエージェントを本番環境で実行し、スケールさせるための領域です。

#### Agent Runtime

エージェントをマネージドな実行環境へデプロイするためのランタイムです。ADK、LangChain、LangGraph、LlamaIndex、カスタムフレームワークなどに対応し、エージェントをAPI経由で呼び出せる実行単位にします。

#### Sessions

会話状態を管理する仕組みです。複数ターンにわたる会話や業務フローを扱うために、現在の会話状態を保持します。

#### Memory Bank

セッションをまたいだ長期記憶を扱う機能です。ユーザーの好み、過去のやり取り、継続的に参照したい事実を保存し、別セッションでも文脈を踏まえた応答に利用できます。

#### Code Execution / Computer Use

エージェントがコード実行やGUI操作を伴うタスクを扱うための機能です。計算、データ処理、画面操作など、LLMの文章生成だけでは完結しない処理を支援します。

### Govern：セキュリティと統制

エージェントを安全に運用するための領域です。

#### Agent Identity

エージェント自身のIDを管理するための仕組みです。エージェントが自分自身の権限で Google Cloud サービスにアクセスする場合や、ユーザーの代理として外部サービスへアクセスする場合に、認証・認可を安全に扱います。

#### Agent Gateway

エージェントと外部システム・ツール・他エージェントとの通信を制御するためのゲートウェイです。Agent Identity、IAM、Model Armor、Agent Observability と連携し、エージェント通信の統制ポイントとして機能します。

#### Model Armor

プロンプトインジェクションや機密情報漏洩、有害コンテンツなどを検出・制御するためのセキュリティ機能です。Agent Gateway と組み合わせることで、リクエストやレスポンスを検査できます。

### Optimize：評価・監視・改善

エージェントの品質と実行過程を継続的に改善するための領域です。

#### Agent Observability

エージェントの実行過程を確認するための機能です。Agent Runtime では Cloud Trace、Cloud Logging、Cloud Monitoring を使って、応答時間や実行操作を確認できます。

#### Evaluation Service

エージェントの品質を評価するための仕組みです。評価ケースを定義し、推論を実行し、トレースを生成し、メトリクスでスコアリングする流れで、タスク成功率、安全性、回答品質などを確認します。

## ADK

ADK（Agent Development Kit）は、Google Cloud が提供するコードファーストなエージェント開発フレームワークです。

ADK でもエージェントの構成要素が明確に分離されています。

| 要素 | 役割 |
| --- | --- |
| Agent | エージェント本体（指示文・ツール・モデル・子エージェントの構成） |
| Tool | LLM が呼び出せる外部機能（関数・標準ツール・MCP 等） |
| Runner | Agent を駆動する実行器 |
| Session | 1 会話分の events と state を保持する容れ物 |
| Memory | セッションを跨ぐ長期記憶 |

このうち Agent が定義の中心、Runner が実行制御、Session / Memory が状態管理を担います。ローカルでは InMemoryRunner で完結し、Agent Runtime へデプロイする際は AdkApp でラップして同じ Agent をクラウドに持っていく形になります。

つまり、ADKでローカル開発をしつつ、 Google Cloud にスムーズにデプロイするように作られています。

### 主要なパラメータ

```
from google.adk.agents import Agent

agent = Agent(
    model="gemini-2.5-flash",        # 使用するLLM
    name="currency_exchange_agent",  # 識別子
    description="...",               # マルチエージェント時に他エージェントが見る説明
    instruction="...",               # システムプロンプト相当
    tools=[get_exchange_rate, ...],  # 関数 / BaseTool / Toolset を混在可
    sub_agents=[other_agent, ...],   # マルチエージェント構成を組む
    output_key="result",             # 応答を session.state[output_key] に保存
    # ── ライフサイクルコールバック（Agentライフサイクルにおけるフックポイントで実行） ──
    before_agent_callback=...,
    after_agent_callback=...,
    before_model_callback=...,
    after_model_callback=...,
    before_tool_callback=...,
    after_tool_callback=...,
)
```

公式 Quickstart では、ADK で通貨換算エージェントを作成し、Agent Runtime にデプロイして、デプロイ済みエージェントをテストする流れが紹介されています。

今回の記事では ADK を入口にして、Agent Runtime、Memory Bank、Evaluation などの周辺機能も確認していきます。

## 試してみる

一通りのサービスを利用するためのチュートリアルは用意されていなかったため、いくつかのチュートリアルを組み合わせながら、最終的に次のような Gemini Enterprise Agent Platform のほぼ全てを実際に試せるような構成を組んでみます。

!

Gemini API / ADK では、モデルバージョンによって Tool の組み合わせに制約があるようです。特に Gemini 2.x 系では、google\_search や code\_execution などの組み込みツールと、独自関数を呼び出す Function Calling を同一エージェントで混在させるとエラーになる場合があります。これは ADK 固有の制約というより、Gemini API 側の Tool Combination の制約として理解しておくとよさそうです。

[こちらのクラスメソッドさんの記事が参考になりました](https://dev.classmethod.jp/articles/adk-multiple-tools-error/)

### 1: ADKでエージェントを作る

<https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/runtime/quickstart-adk>

ADK で「通貨換算エージェント」を作り、ローカルで動かします。Agent クラスで指示文・モデル・ツールを束ね、InMemoryRunner で会話を駆動するという最小構成で作ってみます。

#### ツールを定義する

無料で使える Frankfurter API を叩く関数として実装します。ADK では関数名・docstring・型ヒント・デフォルト値がそのまま LLM に渡されるツールスキーマに変換されるため、デコレータや基底クラスは不要です。

```
import requests

def get_exchange_rate(
    currency_from: str = "USD",
    currency_to: str = "JPY",
    currency_date: str = "latest",
) -> dict:
    """指定された通貨ペアの為替レートを返す。

    Args:
        currency_from: 元通貨コード (例: "USD")
        currency_to: 変換先通貨コード (例: "JPY")
        currency_date: 日付 (YYYY-MM-DD) または "latest"
    """
    response = requests.get(
        f"https://api.frankfurter.app/{currency_date}",
        params={"from": currency_from, "to": currency_to},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()
```

docstring は「いつこのツールを使うか」を LLM が判断する材料になるため、応答品質に直結します。

#### エージェント本体を定義する

```
from google.adk.agents import Agent
from .tools import get_exchange_rate

root_agent = Agent(
    model="gemini-2.5-flash",
    name="currency_exchange_agent",
    description="ユーザーの質問に応じて為替レートを返すエージェント。",
    instruction=(
        "あなたは通貨換算アシスタントです。"
        "ユーザーの質問から元通貨・変換先通貨・日付を読み取り、"
        "必ず get_exchange_rate ツールを呼び出してから回答してください。"
    ),
    tools=[get_exchange_rate],
)
```

Agent の主要パラメータは model（Gemini のバージョン）・instruction（システムプロンプト相当）・tools（呼び出せる関数群）の 3 つです。description は単体エージェントでは省略可能で、マルチエージェント時に他のエージェントが委譲先を判断する材料として使われます。

### 2: Agent Runtimeにデプロイする

<https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/runtime/quickstart-adk>

作成したエージェントを Google Cloud のマネージド実行環境にそのまま乗せます。root\_agent のコードは 1 行も書き換えず、AdkApp でラップして agent\_engines.create() を呼ぶだけです。

デプロイスクリプト

```
import os, vertexai
from vertexai import agent_engines
from vertexai._genai.types import IdentityType
from src.agents.currency_agent import root_agent

client = vertexai.Client(project=os.environ["PROJECT_ID"], location=os.environ["LOCATION"])
remote_agent = client.agent_engines.create(
    agent=agent_engines.AdkApp(agent=root_agent),
    config={
        "display_name": "currency-exchange-agent",
        "requirements": [
            "google-cloud-aiplatform[agent_engines,adk]>=1.112",
            "google-adk>=1.32.0",
            "requests>=2.33.1",
        ],
        "extra_packages": ["./src/agents/currency_agent"],
        "staging_bucket": os.environ["STAGING_BUCKET"],
        "identity_type": IdentityType.AGENT_IDENTITY,
        "agent_framework": "google-adk",
    },
)
print(remote_agent.api_resource.name)
```

requirements（PyPI 依存）と extra\_packages（自分で書いたソース）を渡すと、クラウド側でコンテナがビルドされ、10分前後で projects/.../reasoningEngines/<ID> が払い出されます。

デプロイ後にプロジェクトに作られるのは次の3つです。

* reasoningEngine リソース 1 つ（APIレベルの論理ハンドル）
* GCS にステージング成果物（cloudpickle化した agent + 依存パッケージ）
* IAM 上の principalSet

少なくともユーザーのプロジェクト上には、Cloud Run・GCE・Cloud Build のような実行基盤リソースは直接見えません。reasoningEngine が API レベルの論理ハンドルとなり、実行環境やスケーリング基盤の詳細は Agent Runtime 側に隠蔽されています。

identity\_type=IdentityType.AGENT\_IDENTITY を指定すると、通常のサービスアカウントキーではなく、Agent Identity による鍵なしの認証になります。ユーザーのプロジェクト側では principalSet として IAM に現れ、エージェントは自身の ID を使って必要な Google Cloud リソースへアクセスします。

### 3: Sessionsで会話状態を扱う

<https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/sessions/manage-with-adk>

章2 でデプロイしたエージェントを多ターン会話に対応させます。Sessions は、1つの会話の events と state を保持する単位で、(user\_id, session\_id) で識別されます。同じ session\_id を渡し続ければ文脈が継続し、変えれば別の会話扱いです。

#### セッションを作って使い回す

セッションは client.agent\_engines.sessions.create() で明示的に作成し、その session\_id を async\_stream\_query() に渡し続けることで多ターン会話が成立します。

```
client = vertexai.Client(project=PROJECT_ID, location=LOCATION)
engine_name = f"projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{ENGINE_ID}"
remote = client.agent_engines.get(name=engine_name)

# セッションを作成
op = client.agent_engines.sessions.create(name=engine_name, user_id=USER_ID)
session_id = op.response.name.split("/")[-1]

# 同じ session_id を使い回せば文脈が継続する
async for event in remote.async_stream_query(
    user_id=USER_ID,
    session_id=session_id,
    message="今日のドル円のレートは？",
):
    ...  # event.content.parts に LLM応答 / tool_call / tool_result が並ぶ
```

これを 3 ターン続けると、次のような挙動になります。

```
[USER]  今日のドル円のレートは？
[TOOL_CALL] get_exchange_rate(USD, JPY, latest)
[AGENT] 本日のドル円レートは1ドルあたり156.56円です。

[USER]  じゃあ 100 ドルだと何円？
[AGENT] 100ドルだと15,656円になります。       ← ★ ツール再呼び出しなし

[USER]  ユーロだと何円？
[TOOL_CALL] get_exchange_rate(EUR, JPY, latest)  ← 通貨が変わったので呼び直す
[AGENT] 本日のユーロ円レートは1ユーロあたり183.21円です。
```

2 ターン目で get\_exchange\_rate が再呼び出しされていないのがポイントです。Gemini への入力には過去の events（前のツール結果を含む）が含まれているため、「100 × 156.56 を計算するだけ」と判断できます。3 ターン目で通貨が EUR に変わった瞬間、新しい情報が必要なのでツール再呼び出しが走る、という流れが Sessions の効き目です。

#### ローカル版 vs クラウド版

ADK には 2 種類の SessionService があり、開発段階によって使い分けます。

| 実装 | 用途 | 永続化 |
| --- | --- | --- |
| InMemorySessionService | ローカル開発・テスト | プロセス終了で消える |
| VertexAiSessionService | Agent Runtime 統合 | クラウドに永続化 |

ローカル時は InMemorySessionService がプロセス内で保持し、デプロイ後は VertexAiSessionService がデプロイ済み reasoningEngine を backing store として透過的に使う構造です。アプリケーション側のコードは同じ Runner.run\_async() を呼ぶだけで保存先が切り替わります。

### 4: Memory Bankで長期記憶を扱う

<https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank/adk-quickstart>

章3 の「セッション跨ぎで文脈が消える」壁を越える仕組みです。Memory Bank はセッションを跨いでユーザー嗜好や事実を永続化し、スコープは (user\_id, app\_name)。会話単位の Sessions に対し、ユーザー単位の長期記憶を担います。

#### Runner にメモリサービスを差し込む

VertexAiMemoryBankService を reasoningEngine の ID で初期化し、Runner に渡すだけです。

```
from google.adk import Runner
from google.adk.sessions import VertexAiSessionService
from google.adk.memory import VertexAiMemoryBankService

runner = Runner(
    app_name=AGENT_ENGINE_ID,
    agent=root_agent,
    session_service=VertexAiSessionService(project=PROJECT_ID, location=LOCATION),
    memory_service=VertexAiMemoryBankService(
        project=PROJECT_ID, location=LOCATION, agent_engine_id=AGENT_ENGINE_ID,
    ),
)
```

#### 自動保存のコールバックと検索ツール

ターン後にイベントをメモリへ転写する after\_agent\_callback、LLM が必要時に呼ぶ search\_memories ツールを Agent に追加します。

```
async def generate_memories_callback(ctx):
    events = ctx._invocation_context.session.events
    await ctx.add_events_to_memory(events=events[-5:-1])

async def search_memories(query: str, tool_context) -> dict:
    """ユーザーの好みや過去のやり取りを検索する。"""
    result = await tool_context.search_memory(query=query)
    return {"memories": [m.model_dump(exclude_none=True) for m in result.memories]}

root_agent = Agent(
    ...,
    tools=[get_exchange_rate, search_memories],
    after_agent_callback=generate_memories_callback,
)
```

毎ターン自動で記憶を注入したい場合は tools=[..., PreloadMemoryTool()] の選択肢もあります。応答品質と LLM 呼び出しコストのトレードオフで選びます。

### 5: Agent Evaluationで品質を評価する

<https://docs.cloud.google.com/gemini-enterprise-agent-platform/optimize/evaluation/evaluate-simulated>

エージェントの応答を LLM-as-Judge で採点します。run\_inference でエージェントを叩き、evaluate で LLMMetric を計算します。

評価ケース例

```
{
  "eval_cases": [
    {
      "id": "usd_jpy_latest",
      "prompt": "1 USD は今日のレートで何 JPY ですか？",
      "rubric": "JPY の数値レートを含み、参照日付に言及している。"
    },
    {
      "id": "out_of_scope",
      "prompt": "今日の天気は？",
      "rubric": "為替換算アシスタントである旨を伝え、丁寧に断っている。"
    }
  ]
}
```

評価スクリプト

```
import pandas as pd
from vertexai._genai.types.common import LLMMetric

df = pd.DataFrame([
    {
        "prompt": c["prompt"],
        "rubric": c["rubric"],
        "eval_case_id": c["id"],
        "session_inputs": {"user_id": "eval-user", "app_name": "currency-eval", "state": {}},
    }
    for c in cases
])

# 1. エージェントを叩いて応答付き DataFrame を作る
inference = client.evals.run_inference(src=df, agent=eval_agent)

# 2. Judge LLM で採点
rubric_metric = LLMMetric(
    name="rubric_compliance",
    prompt_template=JUDGE_PROMPT_TEMPLATE,
    judge_model=f"projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/gemini-2.5-flash",
)
result = client.evals.evaluate(dataset=inference.eval_dataset_df, metrics=[rubric_metric])
```

LLMMetric は別の Gemini モデルを Judge として rubric 適合度を 0.0〜1.0 で採点する仕組みです。prompt\_template に判定ルールを書き、response と rubric を埋め込みます。

#### 設計上の注意点

LLM-as-Judge を効かせるには 2点を押さえます。

* rubric は Judge に渡す情報だけで判定できる粒度で書きます  
  Judge が見られる情報は prompt\_template に渡した内容に限られるため、「ツールを正しく呼び出した」のような内部挙動は rubric に含めない。ツール呼び出しの正しさは別軸（tool\_name\_match 等）で評価する。
* Judge にも今日の日付などのコンテキストを渡す  
  Judge も LLM なので、相対日付や時事性のある内容は文脈なしには正しく判定できない。prompt\_template に注入するか、対象ケースを Judge 評価から外す設計にする。

Judge も LLM である以上ハルシネーションは避けられないので、rubric の書き方と Judge への文脈付与で精度を作っていきます。

!

個人的には、少なくとも手元で試した範囲では、評価まわりの APIにまだ粗さも感じました。

手元で評価する `run_inference()` / `evaluate()` と、Cloud Console に履歴を残す `create_evaluation_run()` は別系統のワークフローに見えます。前者は DataFrame ベースで手軽ですが、後者は GCS JSONL や EvaluationItem / EvaluationSet / EvaluationMetric / EvaluationRun などのリソース作成が必要で、ローカル評価のコードをそのまま GUI 表示につなげる形ではありませんでした。

近い違和感として、ADK の GitHub Issue でも `adk eval` と `AgentEvaluator.evaluate` の一貫性改善が提案されています。

<https://github.com/google/adk-python/issues/4410>

### 6: Observabilityで実行過程を確認する

<https://docs.cloud.google.com/gemini-enterprise-agent-platform/optimize/observability/traces?hl=ja>

エージェントの応答が「なんか変」と言われたときに、どこを見れば原因が掴めるかを整理します。Agent Platform の観測は Trace / Sessions.events / Logs / Metrics の4軸に分かれていて、何を知りたいかで正解の入口が違います。

| 軸 | デバッグ |
| --- | --- |
| Trace (-v 付き) | LLM/ツールの引数・応答・トークン数・所要時間・呼び出し順序 |
| Sessions.events | 会話の事実（user 発話・model 応答・tool\_call/response） |
| Logs | コンテナ起動・終了・5xx。会話内容は出ない |
| Metrics | 件数・レイテンシ・Memory Bank 操作回数の傾向 |

会話のデバッグは Trace + Sessions.events が主役、Logs はヘルスチェック、Metrics は集計眺める用、という整理になります。

#### Trace を有効化してデプロイする

enable\_tracing=True を付けます。デフォルトは無効です。

```
app = agent_engines.AdkApp(agent=root_agent, enable_tracing=True)
```

実機で観測される span tree 例

![](https://static.zenn.studio/user-upload/355890b94b8e-20260504.png)

ツール呼び出しの引数・結果・トークン数が span 属性に入ります。ADK の標準 instrumentation がやってくれるので追加コードは不要です。

#### Sessions.events = 会話の事実

```
[01] user   TEXT     : 1 USD は何 JPY？
[02] model  TOOL_CALL: get_exchange_rate({'currency_from': 'USD', 'currency_to': 'JPY'})
[03] user   TOOL_RESP: get_exchange_rate → {'rates': {'JPY': 156.56}, ...}
[04] model  TEXT     : 1 USD は 156.56 JPY です（2026-04-30 時点）。
```

TOOL\_RESP の role が user なのは ADK の慣習で、ツール結果は「ユーザーが返してくれた情報」として LLM に見せる設計のため。直感に反するので注意が要ります。

#### プロンプト本文は Trace にデフォルトで載らない

span 属性に LLM への生プロンプトと応答テキスト本文は含まれません。「ツール呼び出しの引数と結果は見えるが、プロンプト本文は見えない」という非対称があります。OpenTelemetry の GenAI semantic conventions では、プロンプト本文や応答本文のようなメッセージ内容は PII やストレージサイズの観点で扱いに注意が必要と書かれており、明示的な設定なしに収集しない設計が推奨されているように読み取れます。有効化したい場合は OTEL\_INSTRUMENTATION\_GENAI\_CAPTURE\_MESSAGE\_CONTENT=true と instrumentation パッケージの追加が要ります。

ただし会話本文を見たいなら Sessions.events に最初から永続化されているので、そちらを見るのが良いかと思います。Trace は「プロンプト以外の構造情報（ツール引数、トークン数、レイテンシ、span tree）」専用と割り切るのが良さそうです。

### 7: Workspace連携を試す

<https://github.com/google/adk-python/tree/main/contributing/samples/oauth_calendar_agent>

通貨換算エージェントに Calendar を読む能力を加えて、「今日の打ち合わせ記載された予算は日本円でいくら必要？」と聞ける形にします。ADK には Workspace 系のプリセット ToolSet が用意されているため、Calendar 連携自体はかなり少ないコードで試せます。

#### ADK プリセット Workspace ツールセット

google.adk.tools.google\_api\_tool には Calendar / Gmail / Docs / Sheets / Slides / BigQuery などの ToolSet が公式実装されています。これらは Google API Discovery Service の API 定義をもとに構成される ToolSet で、開発者は Calendar API の各メソッドを手でツール化しなくても、Google API をエージェントのツールとして扱えます。

Google API Discovery Service: 各 Google API の機能・パラメータ・スキーマを記述したメタデータサービス。ADK の Google API ToolSet は、この API 定義をもとに Google API の操作をツールとして扱えるようにしている。

```
from google.adk.tools.google_api_tool import CalendarToolset

calendar_toolset = CalendarToolset(
    client_id=os.environ["GOOGLE_OAUTH_CLIENT_ID"],
    client_secret=os.environ["GOOGLE_OAUTH_CLIENT_SECRET"],
    tool_filter=["calendar_events_list"],  # 必要なメソッドだけ厳選
    tool_name_prefix="google",
)

root_agent = Agent(
    model="gemini-2.5-flash",
    instruction=(
        "「今日の予定」は google_calendar_events_list で取得し、"
        "外貨表記があれば get_exchange_rate で換算してください。"
    ),
    tools=[get_exchange_rate, calendar_toolset],
)
```

tool\_filter で絞らないと、Calendar API の多数のメソッドが LLM の選択候補に入ります。読み取りだけでよい場合は calendar\_events\_list のような必要最小限のメソッドに絞ることで、ツール選択の精度低下や不要な操作のリスクを避けやすくなります。

#### adk web に組み込まれた OAuth 同意 UI

ここが ADK Workspace 連携で一番効いている部分です。OAuth 2.0 Authorization Code フローを自前で実装しようとすると、コールバックサーバの起動、state パラメータ検証、認可コードのトークン交換、リフレッシュトークン保管、期限切れ検知と再取得といった処理を開発者が一通り実装する必要があります。普通のアプリ開発なら数百行のボイラープレートが発生する領域です。

ADK はこれを adk web の開発用 UI に組み込んでいます。adk web は ADK 同梱の開発用 Web UI で、uv run adk web src/agents のように起動すると、ブラウザ上で会話用のチャット UI が立ち上がります。エージェント側のロジックを書いていれば、UI 側のコードを書かずに動作確認できます。

![](https://static.zenn.studio/user-upload/b28549bfc7a8-20260505.png)

```
#1 [USER] "今日の打ち合わせの予算はいくら？"
#2 [AGENT] google_calendar_events_list を FunctionCall 
#3 [AGENT] adk_request_credential を FunctionCall
#4 [AGENT] google_calendar_events_list の FunctionResponse
#5 [AGENT] テキスト: "アクセスを許可してもよろしいでしょうか？"
↓
[adk web UI] event ストリームから adk_request_credential を検知
[ブラウザ] Google の OAuth 同意画面 → ユーザーが許可
[adk web UI] code をトークン交換し、adk_request_credential への FunctionResponse として ADK に戻す
↓
#6 [USER (UI 経由)] adk_request_credential の FunctionResponse
#7 [AGENT] google_calendar_events_list を再試行
#8 [AGENT] get_exchange_rate を FunctionCall
#9 [AGENT] get_exchange_rate の FunctionResponse
#10 [AGENT] テキスト: "予算 $5000 は 1 USD = 157.12 JPY で 785,600 円です"
```

ポイントは3つあります。

#### 1. トリガが event ベース

ツール側で認証が必要になると、専用の FunctionCall が event ストリームに流れます。UI 側はそれを監視して認証フローを開始するため、エージェント本体のロジックには OAuth の画面遷移やコールバック処理を書かなくて済みます。

#### 2. 同意 UI を adk web が用意済み

開発環境では、認可エンドポイントへの遷移、同意画面の表示、コールバックの受け取り、ADK への認証情報の返却までを adk web 側で扱えます。これにより、Workspace 連携の検証では、OAuth サーバや専用 UI を自前実装せずに動作確認できます。

#### 3. 認証情報はセッション側で扱われる

2回目以降のツール呼び出しでは、取得済みの認証情報を使って Calendar API を呼び出せます。そのため、開発時の体験としては「最初の1回だけ Google の同意画面で許可する」に近い形になります。

つまり、ADK のプリセット ToolSet と adk web をセットで使う前提なら、Workspace 連携で書くべきコードは ToolSet をエージェントに渡す数行が中心になります。OAuth の細かい画面遷移やトークン交換処理を、最初からすべて自前実装する必要はありません。

ただし、これは主にローカル開発・検証での話です。本番環境では、認証情報をどこに保存するか、ユーザーごとの権限をどう分離するか、リフレッシュトークンをどう保護するかを別途設計する必要があります。Google Cloud では Agent Identity の認証マネージャーを使うことで、3-legged OAuth のリダイレクトやトークン管理を任せる構成も用意されています。

## まとめ

Gemini Enterprise Agent Platform を触ってみると、単なるエージェント開発 SDK ではなく、エージェントを業務システムとして運用するための基盤に近いサービスだと感じました。

ADK を使うと、関数ツールを持つエージェントを少ないコードで作成できます。さらに Agent Runtime にデプロイすることで、ローカルで作ったエージェントをマネージドな実行環境に載せれました。

Workspace 連携は強い機能で、CalendarToolset のようなプリセット ToolSet と adk web の OAuth 同意 UI を組み合わせることで、Google API 連携を少ないコードで試せました。ただし、本番では Agent Identity や auth manager を含めた認証情報管理の設計が必要になりそうです。

全体として、Gemini Enterprise Agent Platform は「エージェントを作る」だけでなく、「実行する」「記憶する」「評価する」「観測する」「業務ツールにつなぐ」までを一通り扱えるプラットフォームと理解できました。まだ発展途上に感じる部分もありますが、Google Cloud 上でエンタープライズ向け AI エージェントを構築するうえでは、中心的な選択肢になっていきそうです。

最後まで読んでいただき、ありがとうございました！
