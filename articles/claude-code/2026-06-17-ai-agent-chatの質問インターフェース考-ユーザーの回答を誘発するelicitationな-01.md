---
id: "2026-06-17-ai-agent-chatの質問インターフェース考-ユーザーの回答を誘発するelicitationな-01"
title: "AI Agent Chatの質問インターフェース考 ― ユーザーの回答を誘発するElicitationなUI"
url: "https://zenn.dev/gvatech_blog/articles/01c4e4c0c0268d"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "GPT"]
date_published: "2026-06-17"
date_collected: "2026-06-17"
summary_by: "auto-rss"
query: ""
---

## はじめに

もう一日中AIに質問を投げ込みまくってる私です。

なにぶん我儘なもので、遠慮もなしに質問攻めをしておきながら、不意にAIから逆質問を受けた時「えっ回答するの面倒くさいな！」と思ってしまうものです。

皆様もAIからの質問に対して、テキストエリアに回答をタイピングすることに苦心した経験があるのではないでしょうか？

本稿では、この回答の摩擦をどう減らせるのかという観点から、AI Agent Chatの質問UIを掘り下げます。

## 様々なAI Agent Chatにおける質問UI

### Claude Code

Claude Codeでは、下記画像のように**複数の選択肢の提示と合わせて、入力欄を用意する形でユーザーに質問を行う**UIが用意されています。

![](https://static.zenn.studio/user-upload/34d61fcb0cf4-20260529.png)  
*<https://code.claude.com/docs/ja/overview>*

この画像の例では 1~4 のいずれかの選択肢を選択するか、5で自由入力による回答を行うことができます。

TUIにおけるこのような表示形式は、他のコーディングエージェントでも一般的となっており、冒頭で述べた回答の摩擦という問題を緩和しているように見えます。

### Claude Design

Claude Designの質問UIはさらに踏み込んでいて、**選択肢の提示に留まらず、数値はレンジスライダー、配色は色そのものを見せるカラーパレットというように、質問の種類ごとに回答インターフェースを出し分け**ています。

![](https://static.zenn.studio/user-upload/c8988953197c-20260528.png)  
*<https://claude.ai/design>*

### Genspark

Gensparkでは、選択肢の提示と合わせて一問ずつ質問に答えるための専用UIを表示してくれます。

![](https://static.zenn.studio/user-upload/cd4edc599d81-20260529.png)  
*<https://www.genspark.ai/ja>*

## 「言語化の足場」としての選択肢提示 -ユーザーの回答を誘発するElicitationなUI

これらのサービスに共通する点として、質問UIの基本形が**選択肢を提示しつつも、自由入力欄を合わせて確保する入力形式**であることです。

もちろん、選択肢の提示はユーザーが回答を容易に行うための利便性をもたらします。  
しかし、それだけではなく、**提示された選択肢に目を通すことで、ユーザーが「自分の伝えたいことは何か」を言語化しやすくする回答の叩き台**として機能している面もあると考えられます。

<https://www.parallelhq.com/blog/chatbot-ux-design>

チャットボットのUXについて書かれたこちらの記事には以下のような記述がありました。（以下、意訳です。）

> 選択肢ボタンを使えば、ボットが質問を投げかけつつ選択肢を提示できるため、ユーザーが答えを手探りで入力する必要がなくなります。

確かに従来のチャットUXでは、まっさらなテキストボックスに対して一から文章を構成して回答を記述していく必要があり、「何を書けばいいか」という手探り感が回答のハードルとして存在します。

一方、いくつかの選択肢を提示することで、「ああ、こういう軸で答えれば良さそうだ」という文脈理解を促した上で、自由入力欄にて**選択肢に収まらないニュアンスの回答を自らの言葉で記載することを誘発**できます。

ところで、MCPには Elicitation という機能仕様が存在します。

<https://modelcontextprotocol.io/specification/2025-11-25/client/elicitation>

MCP Elicitationは、MCPで定義されたToolを実行する際に、ユーザーに確認の質問を出すことができる機能仕様となっています。上述したような、選択肢に加えて自由記述欄を設ける形式で質問を発行することもできます。

機能仕様名として使われている 『Elicitation』 は日本語で『引き出す、誘い出す、誘発』という意味があり、相手から本音や潜在的なニーズを引き出すというニュアンスで使われます。

もっとも、MCP Elicitation の機能目的はあくまでも Tool 実行時の確認や入力要求であり、名称には『誘い出す』という意味の英単語が当てられている、という程度の話ではあります。（命名の由来は、調べましたが分かりませんでした。）ただ、本章で述べた「選択肢を叩き台にしてユーザーの本音を引き出す」という発想と共鳴する部分があるように感じます。

## 質問UIを生成する仕組み

では、このような選択肢を伴う質問の生成は、どのように実現されているのでしょうか？  
OSSのAI Agentである Hermes Agent の実装を参考に見ていきます。

<https://hermes-agent.nousresearch.com/>

Hermes Agent では、Claude Code等と同様に選択肢を伴う形でユーザーに質問を行うことができます。

![](https://static.zenn.studio/user-upload/f873f22a6c3b-20260530.png)  
*「世界を変えるようなものを実装したい」と英語でお願いした際に出力された質問*

Hermes Agent 内部では、Agentが利用可能なToolとして `clarify_tool` が用意されています。（[ソース](https://github.com/NousResearch/hermes-agent/blob/678a87c47753a98ab2320def830c7ae24cda4c0e/tools/clarify_tool.py)）

```
def clarify_tool(
    question: str,
    choices: Optional[List[str]] = None,
    callback: Optional[Callable] = None,
) -> str:
    ...
```

`clarify_tool` は関数であり、引数の `question` で質問文を、 `choices` では選択肢の配列を受け取ります。Agentはコンテキストに応じて適切な `question` と `choices` を生成した上で、この関数を呼び出し、ToolのResultとして質問文と選択肢を含む構造化されたデータがクライアントに返る仕組みです。

`hermes chat --verbose` でDEBUGログを確認したところ、以下のように `question` と `choices` を含むJSONがAgentのevent loopの中で送出されていることが分かります。

```
22:55:51 - root - DEBUG [20260530_225545_2b21b0] - Tool call: clarify with args: {"question": "Want to change the world? Great! Let's narrow this down. What's your primary passion area?", "choices": ["Technology & AI", "Environment & Climate", "Health & Medicine", "Education", "So...
  📞 Tool 1: clarify(['question', 'choices'])
     Args: {
       "question": "Want to change the world? Great! Let's narrow this down. What's your primary passion area?",
       "choices": [
         "Technology & AI",
         "Environment & Climate",
         "Health & Medicine",
         "Education",
         "Social Justice & Equality",
         "Economic Empowerment"
       ]
     }
```

TUIはJSON-RPCの形式で上記の内容を受け取り、生成された質問と選択肢をレンダリングしています。

`clarify_tool` のdescriptionプロンプトは以下のようになっています。（和訳）

```
明確化やフィードバック、意思決定が必要な場合、ユーザーに質問を投げかけることができます。以下の2つのモードをサポートしています：

1. **選択式** — 最大4つの選択肢を提示します。ユーザーはいずれか1つを選択するか、5番目の「その他」オプションを使って独自の回答を入力できます。
2. **自由記述式** — 選択肢を一切提示しません。ユーザーは自由に文章で回答を入力します。

このツールの使用が適している場面：
- タスクの内容が曖昧で、ユーザーがアプローチ方法を選択する必要があるとき
- タスク完了後のフィードバックを得たい場合（「その結果はどうでしたか？」など）
- スキルの保存やメモリの更新を提案したい場合
- ユーザーが考慮すべき明確なトレードオフを伴う意思決定が必要な場合

ただし、危険なコマンドの単純な確認（yes/noの選択）にはこのツールを使用しないでください（この場合はターミナルツールが適しています）。
リスクの低い意思決定の場合は、自分で合理的なデフォルト選択を行うことを推奨します。
```

タスク内容が曖昧な場合や、タスク完了後のフィードバックを得る際に、このtoolを利用することを推奨する内容です。

Claude Code や GitHub Copilot にも、AI Agentが選択肢付きでユーザーに質問を行うためのToolがあります。それぞれ以下の質問Toolとして実装されているようです。

| コーディングエージェント | 質問Tool |
| --- | --- |
| Claude Code | [AskUserQuestion](https://code.claude.com/docs/en/agent-sdk/user-input) |
| GitHub Copilot | askQuestions |

そのため、SKILLSなどで利用者に質問を行うインターフェースを用意したい場合、該当の質問Toolを利用するように指示することで、選択肢付きの質問を利用者に提示することができます。

[こちらの記事](https://zenn.dev/shintaro/articles/claude-code-askuserquestion-skills#%E5%AE%9F%E8%B7%B5%E4%BE%8B3%3A-%E3%82%A4%E3%83%B3%E3%82%BF%E3%83%93%E3%83%A5%E3%83%BC-skill)を参考に、 Claude Code で `AskUserQuestion` の利用指示を含むSKILLを `/interview` として作成し実行してみました。すると、以下のように質問をしてくれました。

![](https://static.zenn.studio/user-upload/615e63f7e44c-20260611.png)

## Generative UIの文脈で捉える

私は、本稿の前半で例として取り上げた Claude Design のように、**質問のタイプに応じて回答インターフェースを出し分けるUIが、GUIのAI Agent Chatにおいては一般的になるのではないか**と予想しています。

例えば、数値を聞く質問であればレンジスライダーを提示、日付を聞く質問であればDatePickerを提示するようなイメージです。

こうした柔軟なUI生成にはいくつかの手段が考えられますが、実装しやすいのはHermes Agentで見た方法と考えます。Agentは質問データを構造的な形式で返すだけにとどめ、そのタイプに応じてどのコンポーネントを表示するかはUI側で制御します。

Generative UIの文脈において、このような手法は **Controlled Generative UI（制御型生成UI)** に当たると言えます。（[参考](https://github.com/CopilotKit/generative-ui/blob/main/README.md)）

| Generative UIのアプローチ | 説明 |
| --- | --- |
| Controlled Generative UI | 開発者が事前にコンポーネントをビルド。 エージェントは表示するコンポーネントの選択と、tool呼び出しのパラメータ生成を行う。 |
| Declarative Generative UI | 開発者がレンダリングルールを定義。 エージェントがUI要素を表す構造化スキーマを返し、UI側がレンダリングする。 |
| Open-ended Generative UI | エージェントがUIそのものを生成。 |

これらのアプローチの中でも、Controlled Generative UI は最も制御的な方法でありUI構造そのものを生成するものではないため、スタイル崩れなどが発生せず、エラー率少なく質問UIを表示できるのではないかと考えます。「質問タイプに応じて回答インターフェースを出し分ける」という用途では、扱いやすい手法だと考えます。

## 実装してみる（WebGUI AI Agentチャット）

今回は試しに、**ユーザーの入力に応じて質問を行い、収集した情報をベースにおすすめの旅程を提示するエージェント**を作ってみました。インターフェースはブラウザ上のチャットUIとして用意します。実装はGitHub Copilot CLI with GPT-5.5が頑張ってくれました。

<https://github.com/kentaojapi/elicitation-qa-agent>

※このデモではMCPを利用する必要が無かったためMCP Elicitationは利用していません。Hermes Agent同様に、AI AgentのToolとして質問Toolを設ける形で実装してみます。

### WebUIイメージ

以下のようにメッセージを入力すると、

![](https://static.zenn.studio/user-upload/e7b74f264be7-20260602.png)

複数の質問が生成されて、それぞれの質問内容に適した形式でUIがレンダリングされます。

![](https://static.zenn.studio/user-upload/e3242d695613-20260531.png)

今回は、簡単な4つの回答UIの種類（`question_type`）を用意しました。

| question\_type | UI | 用途 |
| --- | --- | --- |
| `select` | 選択肢 or 自由入力 | 選択肢から回答、もしくはテキスト自由入力 |
| `calendar` | 日付範囲選択 | カレンダーで日付範囲を選択するUI |
| `number` | レンジスライダー | 数値を選択するUI |
| `text` | テキスト入力 | テキストエリアで回答するUI |

フロントエンドでは、以下のように `question_type` に応じてUIを出し分けます。

```
function createQuestionInput(question) {
  switch (question.question_type) {
    case "select":
      return createSelectInput(question);
    case "calendar":
      return createCalendarInput();
    case "number":
      return createRangeInput(question.range);
    case "text":
    default:
      return createTextInput();
  }
}
```

### AI Agentの実装

AI Agentフレームワークは [Strands Agents](https://strandsagents.com/) を利用して作りました。

上述のHermes Agentの `clarify_tool` に倣って質問ツールを実装しました。

質問Tool全文（tools.py）

```
from __future__ import annotations

from typing import Any
from textwrap import dedent

from pydantic import TypeAdapter
from strands import tool

from elicitation_agent.bridge import ClarifyBridge
from elicitation_agent.models import ClarifyQuestion

CLARIFY_INPUT_SCHEMA = {
    "json": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "旅行相談で確認したい質問グループの短いタイトル。",
            },
            "details": {
                "type": "string",
                "description": "質問の上部に表示する任意の補足説明。",
            },
            "questions": {
                "type": "array",
                "description": "1つのUIフローでユーザーに尋ねる質問。",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "description": "安定して参照できる質問ID。",
                        },
                        "question_type": {
                            "type": "string",
                            "enum": ["text", "select", "calendar", "number"],
                            "description": dedent(
                                """\
                                回答UIの種類。selectは選択肢と自由入力欄を表示する。
                                calendarは旅行日程などの日付範囲選択に使う。
                                numberは人数、予算、日数など数値回答に使う。
                                textは選択肢を提示すると回答の情報量が落ちる場合だけ使う。
                                """
                            ),
                        },
                        "question": {
                            "type": "string",
                            "description": "ユーザーに表示する質問文。",
                        },
                        "choices": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": dedent(
                                """\
                                selectの回答候補。text、calendar、numberでは空配列にする。
                                selectではユーザーが選びやすい具体的な候補を複数提示する。
                                """
                            ),
                        },
                        "range": {
                            "type": "object",
                            "description": dedent(
                                """\
                                numberのレンジスライダー範囲。text、select、calendarでは空オブジェクトにする。
                                min/max/step/defaultで現実的な回答範囲を指定する。
                                """
                            ),
                            "properties": {
                                "min": {"type": "integer"},
                                "max": {"type": "integer"},
                                "step": {"type": "integer"},
                                "default": {"type": "integer"},
                            },
                        },
                    },
                    "required": ["question_type", "question", "choices", "range"],
                },
            },
        },
        "required": ["questions"],
    }
}

class ClarifyTools:
    QUESTION_ADAPTER = TypeAdapter(list[ClarifyQuestion])

    def __init__(self, bridge: ClarifyBridge) -> None:
        self.bridge = bridge

    @tool(
        name="clarify",
        inputSchema=CLARIFY_INPUT_SCHEMA,
        description=dedent(
            """\
            旅程の提案に必要な追加情報をユーザーに質問するツール。
            目的地、旅行日程、人数、予算、興味関心、移動手段、旅のペースなど、
            旅程作成に必要な情報が不足している場合は、旅程を提案する前にこのツールを使う。
            関連する質問は配列にまとめて一度に尋ねる。
            question_typeはtext/select/calendar/numberから選ぶ。
            """
        ),
    )
    async def clarify(
        self,
        questions: list[dict[str, Any]],
        title: str | None = None,
        details: str | None = None,
    ) -> str:
        """ユーザーに複数の確認質問を行う。

        Args:
            questions: Web GUIに表示する質問。
            title: 質問グループの短いタイトル。
            details: 質問の上部に表示する任意の説明。
        """
        clarify_questions = self.QUESTION_ADAPTER.validate_python(questions)
        response = await self.bridge.ask(clarify_questions, title, details)
        return response.to_agent_text()
```

Hermes Agentとの差異として、このアプリケーションにおいては、ユーザーに対して一度に複数質問を返したかったため、Toolの引数は `questions` として複数の質問を受け取ることができる形式にしています。

```
...
    @tool(
        name="clarify",
        inputSchema=CLARIFY_INPUT_SCHEMA,
        description=dedent(
            """\
            旅程の提案に必要な追加情報をユーザーに質問するツール。
            目的地、旅行日程、人数、予算、興味関心、移動手段、旅のペースなど、
            旅程作成に必要な情報が不足している場合は、旅程を提案する前にこのツールを使う。
            関連する質問は配列にまとめて一度に尋ねる。
            question_typeはtext/select/calendar/numberから選ぶ。
            """
        ),
    )
    async def clarify(
        self,
        questions: list[dict[str, Any]],
        title: str | None = None,
        details: str | None = None,
    ) -> str:
...
```

`questions` 引数は `list[dict]` 形式で、質問文や選択肢等をAgentから受け取る構造になっています。具体的には以下の通りにdict構造を指定しています。

```
CLARIFY_INPUT_SCHEMA = {
    "json": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "旅行相談で確認したい質問グループの短いタイトル。",
            },
            "details": {
                "type": "string",
                "description": "質問の上部に表示する任意の補足説明。",
            },
            "questions": {
                "type": "array",
                "description": "1つのUIフローでユーザーに尋ねる質問。",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "description": "安定して参照できる質問ID。",
                        },
                        "question_type": {
                            "type": "string",
                            "enum": ["text", "select", "calendar", "number"],
                            "description": dedent(
                                """\
                                回答UIの種類。selectは選択肢と自由入力欄を表示する。
                                calendarは旅行日程などの日付範囲選択に使う。
                                numberは人数、予算、日数など数値回答に使う。
                                textは選択肢を提示すると回答の情報量が落ちる場合だけ使う。
                                """
                            ),
                        },
                        "question": {
                            "type": "string",
                            "description": "ユーザーに表示する質問文。",
                        },
                        "choices": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": dedent(
                                """\
                                selectの回答候補。text、calendar、numberでは空配列にする。
                                selectではユーザーが選びやすい具体的な候補を複数提示する。
                                """
                            ),
                        },
                        "range": {
                            "type": "object",
                            "description": dedent(
                                """\
                                numberのレンジスライダー範囲。text、select、calendarでは空オブジェクトにする。
                                min/max/step/defaultで現実的な回答範囲を指定する。
                                """
                            ),
                            "properties": {
                                "min": {"type": "integer"},
                                "max": {"type": "integer"},
                                "step": {"type": "integer"},
                                "default": {"type": "integer"},
                            },
                        },
                    },
                    "required": ["question_type", "question", "choices", "range"],
                },
            },
        },
        "required": ["questions"],
    }
}
```

#### Agentの定義

続いてAI Agentの実装についてです。

AI Agentの実装全文（agent.py）

```
from __future__ import annotations

from collections.abc import AsyncIterator

from strands import Agent
from strands.models.bedrock import BedrockModel

from elicitation_agent.bridge import ClarifyBridge
from elicitation_agent.models import (
    AgentDoneEvent,
    AgentEvent,
    AgentRawEvent,
    AgentTextEvent,
    AgentToolEvent,
)
from elicitation_agent.tools import ClarifyTools

DEFAULT_BEDROCK_MODEL_ID = "moonshotai.kimi-k2.5"

SYSTEM_PROMPT = """
あなたは旅程を提案する日本語のAI Agentです。

ユーザーの旅行相談を受けたら、目的地・日程・人数・予算・興味関心・移動手段・旅のペースなど、
旅程作成に必要な情報が不足していないか確認してください。
不足している情報がある場合は、旅程を提案する前にユーザーへ追加質問を行ってください。

十分な情報が集まったら、旅程をテキストで提案してください。
"""

class AgentRunner:
    def __init__(
        self,
        bridge: ClarifyBridge,
        model_id: str = DEFAULT_BEDROCK_MODEL_ID,
        region_name: str | None = None,
        endpoint_url: str | None = None,
    ) -> None:
        self.bridge = bridge
        self.tools = ClarifyTools(bridge)
        model = BedrockModel(
            model_id=model_id,
            region_name=region_name,
            endpoint_url=endpoint_url,
        )
        self.agent = Agent(
            model=model,
            tools=[self.tools.clarify],
            system_prompt=SYSTEM_PROMPT,
            callback_handler=None,
        )

    async def stream(
        self, prompt: str, include_raw_events: bool = False
    ) -> AsyncIterator[AgentEvent]:
        announced_tool_uses: set[str] = set()

        async for event in self.agent.stream_async(prompt):
            if include_raw_events:
                yield AgentRawEvent(event=event)

            if text := event.get("data"):
                yield AgentTextEvent(text=text)

            tool_use = event.get("current_tool_use")
            if isinstance(tool_use, dict) and (tool_name := tool_use.get("name")):
                tool_use_key = str(tool_use.get("toolUseId") or tool_name)
                if tool_use_key not in announced_tool_uses:
                    announced_tool_uses.add(tool_use_key)
                    yield AgentToolEvent(name=str(tool_name))

            if "result" in event:
                yield AgentDoneEvent()
```

AI Agentの実装においては、特別なことは何も行っておらず、先に定義した質問用の `clarify` ツールをAgentに対して渡しているのみです。

```
...
        self.agent = Agent(
            model=model,
            tools=[self.tools.clarify],
            system_prompt=SYSTEM_PROMPT,
            callback_handler=None,
        )
...
```

ここで実装したAgentを実行すると、 `clarify` ツールが実行された際に、Agentから以下のようなJSONが送出されます。

```
DEBUG:elicitation_agent.clarify:clarify request JSON:
{'details': '京都旅行の計画をお手伝いさせていただきます。以下の情報を教えていただけますか？',
 'questions': [{'choices': [],
                'question': '旅行の日程を教えてください。出発日と帰着日を選んでください。',
                'question_id': 'travel_dates',
                'question_type': 'calendar',
                'range': {}},
               {'choices': [],
                'question': '大人1人あたりの予算上限を教えてください（交通費・宿泊費・食事・観光など全て込み）。',
                'question_id': 'budget',
                'question_type': 'number',
                'range': {'default': 50000, 'max': 500000, 'min': 10000, 'step': 5000}},
               {'choices': ['歴史・文化・神社仏閣巡り',
                            'グルメ・食文化体験',
                            '着物体験などのアクティビティ',
                            'お茶・伝統工芸などの文化体験',
                            '穴場スポットやローカル体験',
                            '買い物・お土産探し',
                            'ゆっくりしたい・リラックス重視'],
                'question': '京都旅行で重視したいことは何ですか？',
                'question_id': 'priorities',
                'question_type': 'select',
                'range': {}}],
 'request_id': 'bd0f88f256904900b4b4959e0b04c05f',
 'title': '京都旅行の基本情報'}
```

## おわりに

AI Agent Chatにおける質問UIについて、私見を交えながら、先行事例の整理から実装までを見てきました。

あらゆるサービスにAI Agent Chatが組み込まれていく潮流ではありますが、依然としてチャット入力はユーザーにとって負荷が高いものです。このような中でも、可能な限り利用者との摩擦が少ない接点としてのUIを作っていきたいものです。
