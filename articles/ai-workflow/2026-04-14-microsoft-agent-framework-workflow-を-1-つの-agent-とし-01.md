---
id: "2026-04-14-microsoft-agent-framework-workflow-を-1-つの-agent-とし-01"
title: "【Microsoft Agent Framework 】workflow を 1 つの agent として扱うには"
url: "https://zenn.dev/headwaters/articles/3bba6f48b62e43"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "zenn"]
date_published: "2026-04-14"
date_collected: "2026-04-15"
summary_by: "auto-rss"
---

<https://learn.microsoft.com/ja-jp/agent-framework/workflows/as-agents?pivots=programming-language-python>

# Microsoft Agent Framework の `workflow.as_agent()` は何がうれしいのか

Microsoft Agent Framework を触っていると、単一の agent を作るところまでは比較的すんなり進みます。

一方で、複数の agent をつないだ workflow を作り始めると、こんな疑問が出てきます。

* workflow は `run()` できるのに、なぜわざわざ agent 化するのか
* 単一 agent と何が違うのか
* どんな場面で `workflow.as_agent()` が効くのか

結論からいうと、`workflow.as_agent()` は **複雑な multi-agent workflow を、外側からは普通の agent として扱えるようにするための機能** です。

内部では複数の agent が順番に動いていても、呼び出し側は `run()` を中心に、必要に応じて `create_session()` も使いながら、単一 agent とほぼ同じ感覚で扱えます。

この記事では、Microsoft Agent Framework 初学者向けに、`workflow.as_agent()` の役割と使いどころを Python サンプルで整理します。

## まず結論: `workflow.as_agent()` が解決すること

`workflow.as_agent()` の価値は、細かい API より先に次の 3 点で理解すると入りやすいです。

1. **workflow を単一の agent API に包める**
2. **呼び出し側は `run()` をそのまま使え、必要なら `create_session()` も使える**
3. **既存の agent ベース実装や chat UI に組み込みやすくなる**

つまり、**内部は workflow、外側は agent** にしたいときに効きます。

## 単一 agent / workflow / workflow-as-agent の違い

| 方式 | 向いているケース | 呼び出し側の見え方 |
| --- | --- | --- |
| 単一 agent | 単純な会話、ツール呼び出し | 普通の agent |
| `workflow.run()` | workflow の内部イベントや流れを直接扱いたい | workflow 固有 API |
| `workflow.as_agent()` | 複数 agent の流れを隠して再利用したい | 普通の agent |

この比較で大事なのは、`workflow.as_agent()` は workflow を消しているわけではなく、**workflow を agent インターフェースで包んでいる** という点です。

## 最小イメージ

まずは最小イメージだけ見ると、やっていることはかなりシンプルです。

```
workflow = SequentialBuilder(
    participants=[researcher, writer, reviewer],
).build()

workflow_agent = workflow.as_agent(name="WorkflowSummaryAgent")
session = workflow_agent.create_session()
response = await workflow_agent.run("RAG について説明して", session=session)

print(response.text)
```

注目したいのはこの 2 行です。

```
workflow_agent = workflow.as_agent(name="WorkflowSummaryAgent")
response = await workflow_agent.run("RAG について説明して", session=session)
```

ここで workflow 全体が 1 つの agent として見えるようになります。

## サンプルコード

今回のサンプルでは、Microsoft Learn の Python 例に合わせて、Azure AI Foundry 向けの `FoundryChatClient` を作り、そこから 3 つの専門 agent を順番につないでいます。

* `Researcher`: 論点整理
* `Writer`: 説明文のドラフト作成
* `Reviewer`: 最終レビュー

```
import asyncio
import os

from azure.identity import AzureCliCredential
from dotenv import load_dotenv

load_dotenv()

from agent_framework.foundry import FoundryChatClient
from agent_framework.orchestrations import SequentialBuilder

def create_workflow_agent():
    client = FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ["FOUNDRY_MODEL"],
        credential=AzureCliCredential(),
    )

    researcher = client.as_agent(
        name="Researcher",
        instructions=(
            "あなたはリサーチ担当です。"
            "ユーザーの依頼を読み、重要な論点・前提・注意点を短く整理してください。"
        ),
    )
    writer = client.as_agent(
        name="Writer",
        instructions=(
            "あなたは文章作成担当です。"
            "前段の内容を受け取り、わかりやすい日本語の説明文を作成してください。"
        ),
    )
    reviewer = client.as_agent(
        name="Reviewer",
        instructions=(
            "あなたはレビュー担当です。"
            "最終回答として自然で読みやすく、抜け漏れの少ない説明に仕上げてください。"
        ),
    )

    workflow = SequentialBuilder(
        participants=[researcher, writer, reviewer],
    ).build()
    return workflow.as_agent(name="WorkflowSummaryAgent")

async def main() -> None:
    workflow_agent = create_workflow_agent()
    session = workflow_agent.create_session()

    response = await workflow_agent.run(
        "RAG について初学者向けに説明して",
        session=session,
    )
    print(response.text)

if __name__ == "__main__":
    asyncio.run(main())
```

## コードの読みどころ

### 1. まず各 participant が agent になっている

このサンプルでは、`client.as_agent(...)` で 3 つの役割を持つ agent を作っています。

```
researcher = client.as_agent(...)
writer = client.as_agent(...)
reviewer = client.as_agent(...)
```

ここで作っているのは、単なる関数ではなく **agent 互換の participant** です。公式の Workflows as Agents ページでも、この `client.as_agent(...)` パターンがそのまま使われています。

### 2. `SequentialBuilder` で順番につなぐ

```
workflow = SequentialBuilder(
    participants=[researcher, writer, reviewer],
).build()
```

初学者にとって `SequentialBuilder` が分かりやすいのは、**何がどう流れるかが直感的だから** です。

* Researcher が論点整理する
* Writer がそれをもとに文章を書く
* Reviewer が最後に整える

workflow の graph 構造を細かく意識しなくても、「順番に役割を渡している」ということがすぐ伝わります。

### 3. `workflow.as_agent()` が記事の中心

```
workflow_agent = workflow.as_agent(name="WorkflowSummaryAgent")
```

この 1 行が重要です。

ここで workflow 全体が **1 つの agent として見える** ようになります。

つまり、呼び出し側はもう `Researcher -> Writer -> Reviewer` という内部構造を知らなくてもよくなります。

## 呼び出し側のコードがシンプルになる

workflow を agent 化すると、使う側のコードはかなり単純になります。

```
session = workflow_agent.create_session()
response = await workflow_agent.run("RAG について説明して", session=session)
```

この書き方は、単一 agent を扱うときとかなり近いです。

ここが `workflow.as_agent()` の大きな価値です。**作る側は複雑な orchestration を保ちつつ、使う側には単純な API だけを見せられる** ようになります。

## なぜ `workflow.as_agent()` が必要なのか

ここが一番大事なポイントです。

workflow は `run()` で直接実行できます。では、なぜさらに agent 化するのでしょうか。

理由は、**workflow をアプリケーションの外部境界に出したとき、agent として見せたほうが扱いやすいから** です。

### 統一インターフェース

単一 agent も複雑な workflow も、どちらも `run()` を中心に、必要なら `create_session()` を併用して扱えるようになります。

これは UI 層やアプリケーション層で効いてきます。呼び出し先が単一 agent か multi-agent workflow かを、毎回呼び出し側が意識しなくて済みます。

### 再利用しやすい

workflow 全体を 1 つの agent として別のシステムに渡せます。

たとえば、裏側では Researcher / Writer / Reviewer が動いていても、別のアプリケーションから見ると「文章生成 agent」として扱えます。

この「まとまりとして再利用できる」感覚は、workflow を直接露出する場合よりかなり強いです。

### session 管理を agent 側に寄せられる

`workflow.as_agent()` を使うと、session の扱いも agent の流儀に寄せられます。

```
session = workflow_agent.create_session()
```

この形にしておくと、会話状態の継続や再開を、workflow 専用の別モデルとしてではなく、agent session として統一して考えられます。

なお、Python の現行 API では session は必須ではありません。複数ターンの状態を明示的に持たせたいときに `create_session()` を使う、という理解で大丈夫です。

### streaming にもつなぎやすい

workflow の途中経過を、agent の streaming update として受け取れるのも利点です。

特に複数 agent が順番に動く場合、「いま誰が何を出しているか」を streaming で UI に出したくなることがあります。

そのとき、workflow 固有のイベントをアプリケーションが直接解釈するより、agent の更新として扱えたほうが接続しやすいです。

### 外部入力要求の橋渡し

workflow の中には、人間の確認や追加入力を途中で要求したいケースがあります。

そのような workflow 側の要求を、agent 側では function call 的な形で表に出せます。

この橋渡しがあることで、human-in-the-loop を含む workflow でも、agent インターフェースを保ちやすくなります。

## `workflow.run()` とどう使い分けるか

ここは実務で気になるポイントだと思います。

結論としては、どちらが上位互換というより、**どこに境界を置きたいか** で選ぶのが分かりやすいです。

### `workflow.run()` が向いているケース

* workflow の内部イベントを細かく見たい
* 実行フローを直接制御したい
* workflow そのものを主役として扱いたい

### `workflow.as_agent()` が向いているケース

* アプリケーションからは普通の agent として扱いたい
* 既存の agent ベース実装に統合したい
* 複数 agent の内部構成を隠したい
* session や streaming も agent API に寄せたい

私なら、**workflow の内部を観察・制御したいなら `workflow.run()`、外部公開用の部品にしたいなら `workflow.as_agent()`** と覚えます。

## low-level workflow との違い

Microsoft Agent Framework には、`Executor` や `WorkflowBuilder` を直接使う low-level な workflow の組み方もあります。

これは workflow の仕組みを理解するにはとても良いです。ただし、そのまま `as_agent()` にできるとは限りません。ここで効いてくるのが **start executor = workflow の最初の受け口** という考え方です。

`workflow.as_agent()` にすると、外側から見るとその workflow は 1 つの agent です。なので最初に渡されるのは、「ユーザーが送った文字列を agent 側で包んだ message 群」や「system / user の会話 message」です。つまり、start executor は最初から **message の形の入力を受け取れる入口** になっている必要があります。

たとえば、start executor が「まず文字列を受け取って加工する」前提で作られているとします。こういう executor は、`text: str` をそのまま受ける設計になります。

```
@handler
async def first_step(self, text: str, ctx: WorkflowContext[str]) -> None:
    await ctx.send_message(text.upper())
```

この設計は、`workflow.run("hello")` のように low-level workflow を直接実行するぶんには自然です。

でも `workflow.as_agent()` にすると、外から最初に入ってくるのは `str` ではなく message です。なので、`text: str` 前提の start executor をそのまま workflow の入口に置くと、agent の入口とは噛み合いません。

逆に、start executor 自体が最初から `messages: list[Message]` を受け取るようにしておけば、agent から来た入力をそのまま受け止められます。

```
@handler
async def normalize(self, messages: list[Message], ctx: WorkflowContext[list[Message]]) -> None:
    user_request = extract_latest_user_text(messages)
    ...
```

この形なら、外側の agent から渡された message をまずこの正規化ステップで受けて、そこで「最新の user 発話を抜き出す」「後続 executor や agent が扱いやすい形式に整える」といった橋渡しができます。つまり、**message を受ける入口を 1 つ置いておくと、low-level workflow でも `workflow.as_agent()` に載せやすくなる** わけです。

`client.as_agent(...)` で作った participant は、もともと message を受け取って動く agent なので、この入口条件を満たしやすいです。だから `SequentialBuilder + client.as_agent(...)` のような構成は、`workflow.as_agent()` と相性がよいです。

つまり、初学者が最初に理解したいのは次の 2 段階です。

1. **複数の agent を順につなぐ**
2. **その workflow を 1 つの agent として扱う**

この流れを学ぶなら、`SequentialBuilder + workflow.as_agent()` はかなり入りやすい選択です。

## 実行に必要な設定

Microsoft Foundry を使うなら、たとえば次のような環境変数を設定します。

```
FOUNDRY_PROJECT_ENDPOINT=...
FOUNDRY_MODEL=...
```

認証は `AzureCliCredential` を使っているので、事前に Azure CLI でログインしておきます。

実行はシンプルです。

```
uv run python sample\agent_workflow_as_agent.py
```

## まとめ

`workflow.as_agent()` は、複数 agent の workflow を **普通の agent として使える部品** に変えるための機能です。

ポイントを 2 つに絞ると、次のようになります。

1. **内部は multi-agent workflow のまま保てる**
2. **外部との接続は単純な agent API に寄せられる**

workflow を直接実行するだけではなく、**再利用可能な agent として扱いたい** と思ったときに、`workflow.as_agent()` の価値がはっきり見えてきます。

## 参考
