---
id: "2026-06-03-amazon-bedrock-agentcore-memoryのlong-term-memory試し-01"
title: "Amazon Bedrock AgentCore MemoryのLong-term Memory試してみた"
url: "https://zenn.dev/fusic/articles/f9e9b194b3a9ad"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "AI-agent", "Python", "zenn"]
date_published: "2026-06-03"
date_collected: "2026-06-04"
summary_by: "auto-rss"
query: ""
---

## はじめに

Fusicの[レオナ](https://x.com/xthixsl_ml)です。  
今回は、Amazon Bedrock AgentCore MemoryのLong-term Memoryを試しました。

AgentCore Memoryは、AIエージェントに会話履歴やユーザーの好みを持たせるための機能です。本ブログでは、ランニングシューズの相談を題材にして、会話からLong-term Memoryがどのように抽出されるかを確認します。

また、TerraformでAgentCore MemoryとStrategyを作成し、Strands AgentsでAIエージェントを動かします。その後、別セッションからLong-term Memoryを使った応答と、抽出されたMemoryの中身を確認します。

## AgentCore Memoryとは

AgentCore Memoryは、AIエージェント向けのメモリ機能です。ユーザーとの会話を保存し、同じセッション内や別セッションから参照できるようにします。

メモリは2種類あります。

### Short-term Memory（短期記憶）

Short-term Memoryは、セッション内の会話ターンを保存します。同じセッション内で、直前のやり取りを参照したい場合に使います。

### Long-term Memory（長期記憶）

Long-term Memoryは、複数セッションをまたいで使うメモリです。会話からユーザーの好み、事実、セッション要約などを抽出して保存します。

Long-term Memoryはすぐに作られるわけではありません。Short-term Memoryにイベントを書き込むと、バックグラウンドで以下の処理が行われます。

1. Extraction: 会話から重要な情報を抽出
2. Consolidation: 抽出した情報を既存のメモリと統合

<https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory.html>

## Long-term MemoryのStrategy

Long-term Memoryでは、何を抽出するかを`Strategy`で指定します。主なStrategyをまとめてみました。

| Strategy | 説明 | 用途 |
| --- | --- | --- |
| `SEMANTIC` | 事実・知識の抽出 | 会話から事実情報を構造化して保存 |
| `USER_PREFERENCE` | ユーザーの好みの抽出 | 好みや嗜好を記憶して個別化 |
| `SUMMARIZATION` | 会話の要約 | セッション要約を作成して長期保存 |
| `EPISODIC` | エピソード記憶 | イベントやエピソードの記録 |
| `CUSTOM` | カスタム | モデルやプロンプトを指定してカスタマイズ |

1つのMemoryに最大6つまで`Strategy`を設定できます。  
ビルトインタイプ（`SEMANTIC`/`USER_PREFERENCE`/ `SUMMARIZATION`/`EPISODIC`）はそれぞれ1つずつ設定できます。`CUSTOM`は複数設定できます。

## 試してみた

ランニングシューズの相談を例に、Long-term Memoryの抽出を確認します。

### シナリオ

ユーザーがAIエージェントにランニングシューズを相談する場面を想定します。

会話には以下の情報を含めます。

* 普段は架空ブランドRunSampleの27cmを履いている
* 軽量でマラソン向けのシューズが欲しい
* 色は黒が好み
* 予算は2万円以内

この会話をStrands AgentsのAIエージェントで実行し、Long-term Memoryとしてどのように抽出されるかを確認します。

実在ブランド名は避けたいので、サンプルでは架空ブランドの`RunSample`を使います。

## 処理フロー

1. Strands AgentsのAIエージェントをローカルで実行する
2. AgentCore MemoryがバックグラウンドでLong-term Memoryを抽出する
3. SEMANTIC / USER\_PREFERENCE / SUMMARIZATIONの各Strategyに保存される
4. 別セッションのStrands AgentsからLong-term Memoryを取得する
5. 抽出されたMemoryの中身を確認する

### 構成

| リソース | 説明 |
| --- | --- |
| `AgentCore Memory` | 会話イベントとLong-term Memoryを保存 |
| `SEMANTIC Strategy` | 会話から事実情報を抽出 |
| `USER_PREFERENCE Strategy` | ユーザーの好みを抽出 |
| `SUMMARIZATION Strategy` | セッション要約を作成 |
| `Strands Agents` | AIエージェントをローカルで実行 |
| `AgentCoreMemorySessionManager` | Strands Agentsの会話をAgentCore Memoryに保存 |

## 実装

今回は`us-west-2`リージョンでデプロイします。

### 環境

* AWSアカウントと認証情報の設定
* Terraform
* Python 3.13
* uv
* AWS CLI

### ディレクトリ構造

以下のディレクトリ構成で作成します。

```
agentcore-memory-long-term/
├── agent.py
├── pyproject.toml
├── retrieve_memory.py
├── uv.lock
└── envs/
    └── dev/
        ├── iam.tf
        ├── memory.tf
        ├── outputs.tf
        ├── provider.tf
        ├── variables.tf
        └── versions.tf
```

### 1. プロジェクトセットアップ

Terminal

```
uv init --python 3.13
uv add bedrock-agentcore boto3 "botocore[crt]" strands-agents
```

`botocore[crt]`は`aws login`で取得したクレデンシャルを使う場合に必要です。これがないと`MissingDependencyException`が発生します。

実行前に利用するAWSプロファイルで`aws login`を済ませておきます。ログイン済みでもリフレッシュトークンが期限切れの場合は、`LoginRefreshRequired`が出るので再ログインが必要です。

Pythonの実行は`uv run python`で行います。依存関係は`pyproject.toml`にまとめます。

pyproject.toml

```
[project]
name = "agentcore-memory-long-term"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
  "bedrock-agentcore>=1.10.0",
  "boto3>=1.43.11",
  "botocore[crt]>=1.43.11",
  "strands-agents>=1.42.0",
]
```

### 2. Terraformコード

#### プロバイダー設定

AgentCore CLIではなくTerraformで作成します。  
AWS Provider v6.47.0で、`aws_bedrockagentcore_memory` と `aws_bedrockagentcore_memory_strategy` を使います。

envs/dev/versions.tf

```
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 6.47.0"
    }
  }
}
```

envs/dev/provider.tf

```
provider "aws" {
  region = var.aws_region
}
```

envs/dev/variables.tf

```
variable "aws_region" {
  description = "AWS region to deploy AgentCore Memory resources."
  type        = string
  default     = "us-west-2"
}

variable "memory_name" {
  description = "AgentCore Memory name."
  type        = string
  default     = "long_term_memory_demo"
}

variable "memory_role_name" {
  description = "IAM role name for AgentCore Memory."
  type        = string
  default     = "agentcore-memory-role"
}

variable "event_expiry_duration" {
  description = "Short-term Memory event retention period in days."
  type        = number
  default     = 30
}
```

envs/dev/iam.tf

```
data "aws_iam_policy_document" "assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["bedrock-agentcore.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "memory" {
  name               = var.memory_role_name
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

resource "aws_iam_role_policy_attachment" "memory" {
  role       = aws_iam_role.memory.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonBedrockAgentCoreMemoryBedrockModelInferenceExecutionRolePolicy"
}
```

envs/dev/memory.tf

```
resource "aws_bedrockagentcore_memory" "this" {
  name                      = var.memory_name
  description               = "AgentCore Memory Long-term Memory demo"
  event_expiry_duration     = var.event_expiry_duration
  memory_execution_role_arn = aws_iam_role.memory.arn
}

resource "aws_bedrockagentcore_memory_strategy" "semantic" {
  name        = "semantic_strategy"
  memory_id   = aws_bedrockagentcore_memory.this.id
  type        = "SEMANTIC"
  description = "Extract facts and knowledge from conversations"
  namespaces  = ["/actors/{actorId}/semantic/"]
}

# User Preference Strategy（ユーザー好みの抽出）
resource "aws_bedrockagentcore_memory_strategy" "user_preference" {
  name        = "user_preference_strategy"
  memory_id   = aws_bedrockagentcore_memory.this.id
  type        = "USER_PREFERENCE"
  description = "Track user preferences across sessions"
  namespaces  = ["/actors/{actorId}/preferences/"]
}

# Summarization Strategy（会話要約）
resource "aws_bedrockagentcore_memory_strategy" "summary" {
  name        = "summary_strategy"
  memory_id   = aws_bedrockagentcore_memory.this.id
  type        = "SUMMARIZATION"
  description = "Summarize conversation sessions"
  namespaces  = ["/actors/{actorId}/sessions/{sessionId}/summary/"]
}
```

envs/dev/outputs.tf

```
output "memory_id" {
  value = aws_bedrockagentcore_memory.this.id
}

output "memory_arn" {
  value = aws_bedrockagentcore_memory.this.arn
}
```

`aws_bedrockagentcore_memory`がMemory本体で、`aws_bedrockagentcore_memory_strategy`でStrategyを紐づけます。  
今回は`SEMANTIC`、`USER_PREFERENCE`、`SUMMARIZATION`の3つを設定しました。

namespaceには`{actorId}`を含めています。  
Long-term Memoryはnamespace単位で取得・検索します。`default`のような固定値にすると、複数ユーザーのメモリが同じnamespaceに入ります。  
ユーザーごとに分けたい場合は、`/actors/{actorId}/...`のようにactorを含めます。

また、`event_expiry_duration`はShort-term Memoryのイベント保持日数です。7〜365日の範囲で設定できます。今回は30日にしました。

### 3.デプロイ

Terminal

```
cd envs/dev
terraform init
terraform apply
```

### 4. Strands Agentsから実行する

Memoryが`ACTIVE`になったら、Strands AgentsのAIエージェントを実行します。  
ポイントは、Strands Agentsの`Agent`に`AgentCoreMemorySessionManager`を渡すところです。

これにより、`MemorySessionManager.add_turns`を直接呼び出さなくても、Strands Agentsの会話がAgentCore Memoryに保存されます。

agent.py

```
import os
import subprocess

from bedrock_agentcore.memory.integrations.strands.config import (
    AgentCoreMemoryConfig,
    RetrievalConfig,
)
from bedrock_agentcore.memory.integrations.strands.session_manager import (
    AgentCoreMemorySessionManager,
)
from strands import Agent

REGION = os.environ.get("AWS_REGION", "us-west-2")
MODEL_ID = os.environ.get("MODEL_ID", "us.amazon.nova-lite-v1:0")
ACTOR_ID = os.environ.get("ACTOR_ID", "user-001")
SOURCE_SESSION_ID = os.environ.get("SOURCE_SESSION_ID", "support-session-001")
QUERY_SESSION_ID = os.environ.get("QUERY_SESSION_ID", "support-session-002")

def get_memory_id() -> str:
    if memory_id := os.environ.get("MEMORY_ID"):
        return memory_id

    return subprocess.check_output(
        ["terraform", "-chdir=envs/dev", "output", "-raw", "memory_id"],
        text=True,
    ).strip()

def build_session_manager(memory_id: str, session_id: str, enable_ltm_retrieval: bool):
    retrieval_config = None
    if enable_ltm_retrieval:
        retrieval_config = {
            "/actors/{actorId}/semantic/": RetrievalConfig(top_k=5, relevance_score=0.0),
            "/actors/{actorId}/preferences/": RetrievalConfig(top_k=5, relevance_score=0.0),
            f"/actors/{{actorId}}/sessions/{SOURCE_SESSION_ID}/summary/": RetrievalConfig(
                top_k=3,
                relevance_score=0.0,
            ),
        }

    config = AgentCoreMemoryConfig(
        memory_id=memory_id,
        actor_id=ACTOR_ID,
        session_id=session_id,
        retrieval_config=retrieval_config,
    )
    return AgentCoreMemorySessionManager(config, region_name=REGION)

def build_agent(memory_id: str, session_id: str, enable_ltm_retrieval: bool = False):
    session_manager = build_session_manager(memory_id, session_id, enable_ltm_retrieval)
    agent = Agent(
        model=MODEL_ID,
        session_manager=session_manager,
        callback_handler=None,
        agent_id="running-shoe-agent",
        system_prompt=(
            "あなたはランニングシューズの販売員AIエージェントです。"
            "ユーザーのブランド、サイズ、用途、色、予算の希望を覚えながら、"
            "自然な日本語で短く回答してください。"
            "<user_context>がある場合は、過去の会話から得た記憶として参考にしてください。"
        ),
    )
    return agent, session_manager

def main() -> None:
    memory_id = get_memory_id()
    mode = os.environ.get("MODE", "write")

    if mode == "write":
        agent, session_manager = build_agent(memory_id, SOURCE_SESSION_ID)
        prompts = [
            "新しいランニングシューズを探しています。普段は架空ブランドRunSampleのサイズ27cmを履いています。"
            "軽量で、マラソン向けのものが欲しいです。",
            "いいですね！色は黒が好みです。あと、予算は2万円以内で考えています。",
        ]
        for prompt in prompts:
            print(agent(prompt))
        session_manager.close()

    if mode == "query":
        agent, session_manager = build_agent(memory_id, QUERY_SESSION_ID, True)
        print(agent("前回の相談内容を踏まえて、私に合うランニングシューズの条件を短く整理してください。"))
        session_manager.close()

if __name__ == "__main__":
    main()
```

書き込み用の会話を実行します。

Terminal

```
ACTOR_ID=running-shoe-sample-user-20260603 \
SOURCE_SESSION_ID=running-shoe-sample-session-write \
uv run python agent.py
```

Long-term Memoryへの抽出は非同期です。  
数分待ってから、別セッションでLong-term Memoryを使うモードを実行します。

Terminal

```
ACTOR_ID=running-shoe-sample-user-20260603 \
SOURCE_SESSION_ID=running-shoe-sample-session-write \
QUERY_SESSION_ID=running-shoe-sample-session-query \
MODE=query \
uv run python agent.py
```

#### Long-term Memoryの取得

イベントを書き込んだ後、数分待ってからLong-term Memoryを取得します。

retrieve\_memory.py

```
import os
import subprocess

from bedrock_agentcore.memory import MemorySessionManager

REGION = "us-west-2"
ACTOR_ID = os.environ.get("ACTOR_ID", "user-001")
SOURCE_SESSION_ID = os.environ.get("SOURCE_SESSION_ID", "support-session-001")
QUERY_SESSION_ID = os.environ.get("QUERY_SESSION_ID", "support-session-002")

STRATEGY_NAMESPACES = {
    "SEMANTIC": f"/actors/{ACTOR_ID}/semantic/",
    "USER_PREFERENCE": f"/actors/{ACTOR_ID}/preferences/",
    "SUMMARIZATION": f"/actors/{ACTOR_ID}/sessions/{SOURCE_SESSION_ID}/summary/",
}

def format_record(record):
    content = record.get("content", {})
    text = content.get("text", str(content)) if isinstance(content, dict) else str(content)
    lines = [f"  {text.strip()}"]

    score = record.get("score")
    if score is not None:
        lines.insert(0, f"  score={score:.3f}")

    namespaces = record.get("namespaces")
    created_at = record.get("createdAt")
    if namespaces or created_at:
        lines.append(f"  namespaces={namespaces} createdAt={created_at}")

    return "\n".join(lines)

def get_memory_id() -> str:
    if memory_id := os.environ.get("MEMORY_ID"):
        return memory_id

    return subprocess.check_output(
        ["terraform", "-chdir=envs/dev", "output", "-raw", "memory_id"],
        text=True,
    ).strip()

memory_id = get_memory_id()

session_manager = MemorySessionManager(
    memory_id=memory_id,
    region_name=REGION,
)

# 別セッションからでも Long-term Memory は取得可能
session = session_manager.create_memory_session(
    actor_id=ACTOR_ID,
    session_id=QUERY_SESSION_ID,
)

# Strategy ごとの namespace からレコードを一覧表示
print("=== Long-term Memory レコード一覧 ===")
for strategy_name, namespace in STRATEGY_NAMESPACES.items():
    print(f"--- {strategy_name} (namespace_prefix={namespace}) ---")
    memory_records = session.list_long_term_memory_records(
        namespace_prefix=namespace,
    )
    for record in memory_records:
        print(format_record(record))

# セマンティック検索
print("\n=== セマンティック検索: 靴の好み ===")
for strategy_name, namespace in STRATEGY_NAMESPACES.items():
    print(f"--- {strategy_name} (namespace_prefix={namespace}) ---")
    results = session.search_long_term_memories(
        query="ユーザーの靴のブランドやサイズの好みは？",
        namespace_prefix=namespace,
        top_k=3,
    )
    for result in results:
        print(format_record(result))
```

Terminal

```
uv run python retrieve_memory.py
```

`session_id`が異なる別セッションからでも、同じ`actor_id`のnamespaceを指定すればLong-term Memoryを取得できます。

レコード一覧は`list_long_term_memory_records`、検索は`search_long_term_memories`を使います。  
どちらも引数名は`namespace_prefix`です。

`namespace_prefix="/"`で全部まとめて取得するのではなく、Terraformで設定したnamespaceを指定します。  
今回は以下の3つを使います。

* `/actors/{actorId}/semantic/`
* `/actors/{actorId}/preferences/`
* `/actors/{actorId}/sessions/{sessionId}/summary/`

複数namespaceを横断したい場合は、クライアント側でそれぞれ問い合わせて結果をまとめます。

### 4. 実行

実際に実行します。  
まずStrands Agentsで会話を実行します。

strands-write

```
$ ACTOR_ID=running-shoe-sample-user-20260603 SOURCE_SESSION_ID=running-shoe-sample-session-write AWS_PROFILE=reona-dev uv run python agent.py
=== Strands Agents: 会話を書き込み ===
Memory ID: long_term_memory_demo-3RIYN8At8k
Actor ID: running-shoe-sample-user-20260603
Session ID: running-shoe-sample-session-write
Model ID: us.amazon.nova-lite-v1:0

[turn 1] user: 新しいランニングシューズを探しています。普段は架空ブランドRunSampleのサイズ27cmを履いています。軽量で、マラソン向けのものが欲しいです。
[turn 1] assistant: 了解しました。軽量でマラソン向けのRunSampleのランニングシューズを27cmでお探しですね。それでしたら、RunSampleの軽量マラソンモデルがおすすめです。お好みの色や予算はございますか？

[turn 2] user: いいですね！色は黒が好みです。あと、予算は2万円以内で考えています。
[turn 2] assistant: 黒の軽量マラソン向けRunSampleのシューズで2万円以内でしたら、いくつか候補があります。是非店頭でご覧になってみてはいかがでしょうか？
```

数分待つとLong-term Memoryにレコードが抽出されます。

次に、別セッションのStrands AgentsからLong-term Memoryを使って応答させます。

strands-query

```
$ ACTOR_ID=running-shoe-sample-user-20260603 SOURCE_SESSION_ID=running-shoe-sample-session-write QUERY_SESSION_ID=running-shoe-sample-session-query MODE=query AWS_PROFILE=reona-dev uv run python agent.py
=== Strands Agents: Long-term Memoryを使った別セッション応答 ===
Memory ID: long_term_memory_demo-3RIYN8At8k
Actor ID: running-shoe-sample-user-20260603
Session ID: running-shoe-sample-session-query
Model ID: us.amazon.nova-lite-v1:0

user: 前回の相談内容を踏まえて、私に合うランニングシューズの条件を短く整理してください。
assistant: ユーザーに合うランニングシューズは以下の条件です：

- ブランド：RunSample（普段から使用中）
- サイズ：27cm
- 特性：軽量でマラソン向け
- 色：黒
- 予算：2万円以内

RunSampleの軽量マラソンモデルを店頭で確認してみてください。
```

別セッションにも関わらず、前回の会話で伝えた条件を使って応答できました。  
これはStrands Agentsの`AgentCoreMemorySessionManager`が、Long-term Memoryを取得してエージェントのコンテキストに入れているためです。

抽出されたLong-term Memoryも確認します。

retrieve-memory

```
$ ACTOR_ID=running-shoe-sample-user-20260603 SOURCE_SESSION_ID=running-shoe-sample-session-write QUERY_SESSION_ID=running-shoe-sample-session-query AWS_PROFILE=reona-dev uv run python retrieve_memory.py
Memory ID: long_term_memory_demo-3RIYN8At8k

=== Long-term Memory レコード一覧 ===

--- SEMANTIC (namespace_prefix=/actors/running-shoe-sample-user-20260603/semantic/) ---
  The user's budget for running shoes is within 20,000 yen.
  The user prefers black color for running shoes.
  The user is looking for new running shoes that are lightweight and marathon-oriented.
  The user usually wears size 27cm running shoes from the fictional brand RunSample.

--- USER_PREFERENCE (namespace_prefix=/actors/running-shoe-sample-user-20260603/preferences/) ---
  {"preference":"シューズの色は黒が好み", ...}
  {"preference":"軽量でマラソン向けのランニングシューズを好む", ...}
  {"preference":"ランニングシューズのサイズは27cm", ...}
  {"preference":"ランニングシューズの予算は2万円以内", ...}

--- SUMMARIZATION (namespace_prefix=/actors/running-shoe-sample-user-20260603/sessions/running-shoe-sample-session-write/summary/) ---
  <topic name="ユーザーのランニングシューズ検索">...</topic>
```

#### SEMANTIC Strategyの抽出結果

`SEMANTIC`では、会話から事実が4件抽出されました。  
今回の実行では英語の文として保存されました。

semantic-records

```
"The user's budget for running shoes is within 20,000 yen."
"The user prefers black color for running shoes."
"The user is looking for new running shoes that are lightweight and marathon-oriented."
"The user usually wears size 27cm running shoes from the fictional brand RunSample."
```

ユーザーの希望条件が、短い文として保存されていることがわかります。

#### USER\_PREFERENCE Strategyの抽出結果

`USER_PREFERENCE`では、ユーザーの好みがJSONで抽出されました。

preference-record.json

```
{
  "context": "ユーザーは架空ブランドRunSampleのサイズ27cmを普段から履いていると明示している。",
  "preference": "ランニングシューズのサイズは27cm",
  "categories": ["ファッション", "スポーツ", "シューズ"]
}
```

preference-record.json

```
{
  "context": "ユーザーはランニングシューズに求める条件として「軽量」と「マラソン向け」を明示的に挙げている。",
  "preference": "軽量でマラソン向けのランニングシューズを好む",
  "categories": ["スポーツ", "ランニング", "シューズ"]
}
```

preference-record.json

```
{
  "context": "ユーザーはランニングシューズの予算として2万円以内を明示的に述べている。",
  "preference": "ランニングシューズの予算は2万円以内",
  "categories": ["ショッピング", "予算", "シューズ"]
}
```

`context`、`preference`、`categories`に分かれているので、アプリケーション側でも扱いやすそうです。  
こちらは日本語で抽出されました。

#### SUMMARIZATION Strategyの抽出結果

`SUMMARIZATION`では、セッション全体の要約がXML形式で生成されました。  
SUMMARIZATIONのnamespaceには`{actorId}`と`{sessionId}`を含めているので、この例では`/actors/running-shoe-sample-user-20260603/sessions/running-shoe-sample-session-write/summary/`を指定して取得します。

summary-record.xml

```
<topic name="ユーザーのランニングシューズ検索">
ユーザーは新しいランニングシューズを探している。条件は以下の通り：
- ブランド：RunSample（普段から使用中）
- サイズ：27cm
- 希望特性：軽量・マラソン向け
- 希望カラー：黒
- 予算：2万円以内

アシスタントはRunSampleの軽量マラソンモデルを候補として提案し、店頭での確認を勧めた。
</topic>
```

会話全体が「ユーザーのランニングシューズ検索」というトピックで要約されました。

#### セマンティック検索の結果

「ユーザーの靴のブランドやサイズの好みは？」というクエリで検索します。  
検索もnamespace単位なので、下の表は各namespaceに問い合わせた結果を並べています。

実際の検索ログの抜粋です。

semantic-search.log

```
=== セマンティック検索: 「靴の好み」 ===

--- SEMANTIC (namespace_prefix=/actors/running-shoe-sample-user-20260603/semantic/) ---
  score=0.459
  The user prefers black color for running shoes.
  score=0.441
  The user usually wears size 27cm running shoes from the fictional brand RunSample.
  score=0.419
  The user's budget for running shoes is within 20,000 yen.

--- USER_PREFERENCE (namespace_prefix=/actors/running-shoe-sample-user-20260603/preferences/) ---
  score=0.477
  {"preference":"シューズの色は黒が好み", ...}
  score=0.434
  {"preference":"ランニングシューズのサイズは27cm", ...}
  score=0.393
  {"preference":"軽量でマラソン向けのランニングシューズを好む", ...}

--- SUMMARIZATION (namespace_prefix=/actors/running-shoe-sample-user-20260603/sessions/running-shoe-sample-session-write/summary/) ---
  score=0.424
  <topic name="ユーザーのランニングシューズ検索">...</topic>
```

| スコア | 内容 | namespace | Strategy |
| --- | --- | --- | --- |
| 0.477 | シューズの色は黒が好み | `/actors/running-shoe-sample-user-20260603/preferences/` | USER\_PREFERENCE |
| 0.459 | The user prefers black color for running shoes. | `/actors/running-shoe-sample-user-20260603/semantic/` | SEMANTIC |
| 0.441 | The user usually wears size 27cm running shoes from the fictional brand RunSample. | `/actors/running-shoe-sample-user-20260603/semantic/` | SEMANTIC |
| 0.424 | ユーザーのランニングシューズ検索 | `/actors/running-shoe-sample-user-20260603/sessions/running-shoe-sample-session-write/summary/` | SUMMARIZATION |

クエリに近いレコードがスコア付きで返ります。  
複数のStrategyを横断して扱いたい場合は、各namespaceで検索してアプリケーション側で統合する形になります。

## 結果

今回の結果だと、3つのStrategyは以下のように使い分けできそうです。

| Strategy | 出力形式 | 抽出内容 | レコード数 |
| --- | --- | --- | --- |
| `SEMANTIC` | JSONの`fact`（今回の実行では英語文） | 客観的事実 | 4件 |
| `USER_PREFERENCE` | JSON（context/preference/categories） | 好み・嗜好 | 4件 |
| `SUMMARIZATION` | XMLトピック形式 | セッション要約 | 1件 |

ユーザーごとの設定や嗜好を使いたい場合は`USER_PREFERENCE`、事実情報を拾いたい場合は`SEMANTIC`、前回までの会話を引き継ぎたい場合は`SUMMARIZATION`が使いやすそうでした。

## 最後に

AgentCore MemoryのLong-term MemoryをTerraformとStrands Agentsで試してみました。セッションをまたいでユーザーの文脈を使いたい場合に便利そうです。
