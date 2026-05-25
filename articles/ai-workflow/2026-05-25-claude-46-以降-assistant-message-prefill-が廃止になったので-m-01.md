---
id: "2026-05-25-claude-46-以降-assistant-message-prefill-が廃止になったので-m-01"
title: "Claude 4.6 以降 Assistant Message Prefill が廃止になったので max_tokens 超過時のリトライ処理を見直す"
url: "https://qiita.com/hayao_k/items/245053c219a5c5156227"
source: "qiita"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "AI-agent", "LLM", "VSCode", "Python"]
date_published: "2026-05-25"
date_collected: "2026-05-25"
summary_by: "auto-rss"
query: ""
---

## はじめに
Claude 4.6 世代での破壊的変更として、Assistant Message Prefill が廃止されました。

> When migrating from Sonnet 4.5
> 1. Prefilling assistant messages is no longer supported
> `This is a breaking change when migrating from Sonnet 4.5 or earlier.`

https://platform.claude.com/docs/en/about-claude/models/migration-guide#migrating-to-claude-sonnet-4-6

Assistant Message Prefill とはアシスタントの返答の冒頭部分をあらかじめ指定しておくことで LLM の応答を誘導するテクニックです。

代表的な使用例として JSON などの出力フォーマットの強制がありました。回答の先頭を `{` で Prefill することで LLM の応答は `Taro", "age": 30 }` といった JSON の中身となるため、「承知しました」などの不要なテキスト出力を抑制することができます。

```json
{
  "messages": [
    {"role": "user", "content": "JSON で名前と年齢を回答してください"},
    {"role": "assistant", "content": "{"}
  ]
}
```

最新の Opus 4.7 を含む、Cluade 4.6 以降では Assistant Message Prefill を使用したリクエストは 400 エラーになります。

```
This model does not support assistant message prefill. The conversation must end with a user message.
```

## max_tokens 超過時のリトライ処理
その他の代表的な使用例として、中断された応答の再開 (Continuations) がありました。LLM の出力が `max_tokens` に達して途中で途切れた場合、途切れた出力末尾を Prefill として使うことで、自然に続きの応答を生成させることができていました。

これによりユーザーに「続けて」などのメッセージを入力させることなく、応答全体を出力させることができます。ユーザー体験上、非常に重要な処理ですが 4.6 以降では実装を見直す必要があります。

具体的な方法は冒頭の移行ガイドに記載があり、継続処理をユーザーメッセージに移動する、ということで非常にシンプルですね。

> **Common prefill use cases and migrations:**
> * **Continuations** (resuming interrupted responses): Move the continuation to the user message: "Your previous response was interrupted and ended with `[previous_response]`. Continue from where you left off."


## 実装と動作検証
Bedrock の Coverse API のサンプルコードで、リトライ処理の動作と移行例を検証します。

### Prefill を用いたリトライ (エラー発生パターン)
コード全体は以下です。

```python
import boto3

client = boto3.client("bedrock-runtime", region_name="us-east-1")

def generate_with_retry(
    prompt: str,
    model_id: str = "global.anthropic.claude-sonnet-4-6",
    max_tokens: int = 512, #リトライを発生させるために意図的に短く設定
    max_retries: int = 10
) -> str:

    accumulated_text = ""
    retries = 0

    while retries < max_retries:
        messages = [
            {"role": "user", "content": [{"text": prompt}]}
        ]

        # 途中まで生成済みのテキストがあれば Prefill として追加
        if accumulated_text:
            messages.append({
                "role": "assistant",
                "content": [{"text": accumulated_text.rstrip()}]
            })

        response = client.converse_stream(
            modelId=model_id,
            messages=messages,
            inferenceConfig={"maxTokens": max_tokens}
        )

        stop_reason = None
        current_chunk = ""

        for event in response["stream"]:
            if "contentBlockDelta" in event:
                delta = event["contentBlockDelta"]["delta"]
                if "text" in delta:
                    text = delta["text"]
                    current_chunk += text
                    print(text, end="", flush=True)

            elif "messageStop" in event:
                stop_reason = event["messageStop"]["stopReason"]

        accumulated_text += current_chunk

        if stop_reason == "end_turn":
            print()
            break
        elif stop_reason == "max_tokens":
            retries += 1
            continue
        else:
            print()
            break

    return accumulated_text, retries


if __name__ == "__main__":
    result, retry_count = generate_with_retry(
        prompt="日本の歴史について詳しく説明してください。",
    )
    print(f"\n--- 最終テキスト文字数: {len(result)} / リトライ回数: {retry_count} ---")

```

`stop_reason == "max_tokens"` を検知した場合に Assistant Message Prefill でリトライしています。

```py
        # 途中まで生成済みのテキストがあれば Prefill として追加
        if accumulated_text:
            messages.append({
                "role": "assistant",
                "content": [{"text": accumulated_text.rstrip()}]
            })
```

テキストを `rstrip()` しているのはテキストの末尾に空白文字が含まれると、以下のようなエラーが発生するからです。(チャンクの境界で末尾に空白が入りやすい)

```
The model returned the following errors: messages: final assistant content cannot end with trailing whitespace
```

モデル ID に `global.anthropic.claude-sonnet-4-5-20250929-v1:0` を指定した場合は正常に処理されます。

```
$ python test.py
# 日本の歴史概要

日本の歴史を時代区分ごとに説明します。

## **古代（～平安時代）**

### 縄文・弥生時代
- **縄文時代**（紀元前14000年頃～）：狩猟採集生活、縄文土器
- **弥生時代**（紀元前10世紀頃～）：稲作伝来、金属器使用

~~途中の出力は省略~~

### 平成・令和時代
- **平成**（1989～2019年）：バブル崩壊、経済停滞
- **令和**（2019年～）：現在

日本は長い歴史の中で、独自の文化を育みながら発展してきました。

--- 最終テキスト文字数: 962 / リトライ回数: 1 ---
```

モデル ID を `global.anthropic.claude-sonnet-4-6` に変更して実行すると、リトライ処理のタイミングでエラーが発生します。

```
$ python test.py
# 日本の歴史概説

## 1. 先史・原始時代

- **旧石器時代**（約3万年以上前）：日本列島に人類が居住
- **縄文時代**（約1万6千年前〜紀元前3世紀）：土器・狩猟採集文化
- **弥生時代**（紀元前3世紀〜3世紀）：大陸から稲作・金属器が伝来、農耕社会へ

---

~~途中の出力は省略~~

---

## 4. 近世

- **安土桃山時代**（1573〜1603年）：織田信長・豊臣秀吉による全国統一、キリスト教伝来、Traceback (most recent call last):
  File "C:\vscode\prefill\test.py", line 63, in <module>
    result, retry_count = generate_with_retry(
                          ~~~~~~~~~~~~~~~~~~~^
        prompt="日本の歴史について概説してください。",
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\vscode\prefill\test.py", line 27, in generate_with_retry
    response = client.converse_stream(
        modelId=model_id,
        messages=messages,
        inferenceConfig={"maxTokens": max_tokens}
    )
  File "C:\Python313\Lib\site-packages\botocore\client.py", line 602, in _api_call
    return self._make_api_call(operation_name, kwargs)
           ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Python313\Lib\site-packages\botocore\context.py", line 123, in wrapper
    return func(*args, **kwargs)
  File "C:\Python313\Lib\site-packages\botocore\client.py", line 1078, in _make_api_call
    raise error_class(parsed_response, operation_name)
botocore.errorfactory.ValidationException: An error occurred (ValidationException) when calling the ConverseStream operation: The model returned the following errors: This model does not support assistant message prefill. The conversation must end with a user message.
```

### ユーザーメッセージで指示 (エラー無し)
コード全体は以下です。

```python
import boto3

client = boto3.client("bedrock-runtime", region_name="us-east-1")

def generate_with_retry(
    prompt: str,
    model_id: str = "global.anthropic.claude-sonnet-4-6",
    max_tokens: int = 512,
    max_retries: int = 10
) -> tuple[str, int]:

    accumulated_text = ""
    retries = 0

    # 1. メッセージ履歴はループの外で初期化し、文脈を維持する
    messages = [
        {"role": "user", "content": [{"text": prompt}]}
    ]

    while retries < max_retries:
        response = client.converse_stream(
            modelId=model_id,
            messages=messages,
            inferenceConfig={"maxTokens": max_tokens}
        )

        stop_reason = None
        current_chunk = ""

        for event in response["stream"]:
            if "contentBlockDelta" in event:
                delta = event["contentBlockDelta"]["delta"]
                if "text" in delta:
                    text = delta["text"]
                    current_chunk += text
                    print(text, end="", flush=True)

            elif "messageStop" in event:
                stop_reason = event["messageStop"]["stopReason"]

        accumulated_text += current_chunk

        if stop_reason == "end_turn" or stop_reason == "stop_sequence":
            print()
            break
        elif stop_reason == "max_tokens":
            retries += 1
            
            # 2. 中断されたアシスタントの回答を履歴に追加
            messages.append({
                "role": "assistant",
                "content": [{"text": current_chunk}]
            })
            
            # 3. ガイドに準拠した Continuation メッセージを作成
            # 文脈を繋ぐために直前の約 100 文字だけを抽出して [previous_response] とする
            snippet = current_chunk[-100:] if len(current_chunk) > 100 else current_chunk
            
            continuation_prompt = (
                f"Your previous response was interrupted and ended with \"{snippet}\". "
                f"Continue from where you left off. Do not include any introductory text."
            )
            
            # 4. ユーザーメッセージとして続きを要求
            messages.append({
                "role": "user",
                "content": [{"text": continuation_prompt}]
            })
            
            continue
        else:
            print()
            break

    return accumulated_text, retries


if __name__ == "__main__":
    result, retry_count = generate_with_retry(
        prompt="日本の歴史について詳しく説明してください。",
    )
    print(f"\n--- 最終テキスト文字数: {len(result)} / リトライ回数: {retry_count} ---")

```

主なポイントはコメント行として記載した 4 点です。

1. メッセージ履歴はループの外で初期化し、文脈を維持する
1. 中断された今回のアシスタントの回答を履歴に追加
1. ガイドに準拠した Continuation メッセージを作成
1. ユーザーメッセージとして続きを要求

Prefill 使用時のコードのように生成した全テキスト (accumulated_text) をユーザープロンプトに埋め込み、「この続きを書いて」としてしまうと、モデルはその長文の続きを書くという「新しいタスク」だと認識します。結果、テキストの結合が破綻して max_retries に到達するまで文章を生成し続けてしまいます。

移行後は長文生成を会話の往復として扱うため、出力が切れた際は、生成された差分だけをアシスタントの回答として履歴に追加します。

Continuation メッセージ作成の際、再開位置を伝える目的であれば全テキストを渡す必要はないので、末尾 100 文字を抽出することでトークンを節約します。メッセージの送信時には念のため「前置きは一切含めないで」を追加しています。

修正後のコードでは `global.anthropic.claude-sonnet-4-6` でも正常にリトライが動作しました。
```
$ python test2.py
# 日本の歴史概説

## 1. 先史・原始時代

- **旧石器時代**（約3万年以上前）：日本列島に人類が居住
- **縄文時代**（約1万6千年前〜前3世紀）：土器・狩猟採集文化
- **弥生時代**（前3世紀〜3世紀）：大陸から稲作・金属器が伝来、農耕社会へ移行

---

~~途中の出力は省略~~

---

## 14. 令和時代（2019年〜現在）

- 新型コロナウイルス感染症のパンデミック（2020年〜）
- 東京オリンピック・パラリンピック開催（2021年）
- デジタル化・脱炭素社会への取り組み
- 安全保障・外交政策の見直し

---

## まとめ

日本の歴史は、大陸文化の受容と独自文化の発展を繰り返しながら形成されてきました。近代以降は急速な近代化と戦争・復興を経て、現在は成熟した民主主義国家として国際社会で重要な役割を担っています。

--- 最終テキスト文字数: 2136 / リトライ回数: 3 ---
```

## 補足：Bedrock AgentCore SDK などの対応状況
ここまで長々と書いてしまいましたが、Strands Agents などのエージェント開発 SDK では SDK が会話履歴の管理やリトライ処理を担っており、開発者が Assistant Message Prefill を直接扱ったり意識したりする場面はほとんどありません。

Bedrock AgentCore SDK の場合は、2026/2/24 リリースの v1.3.2 以降で早々に修正されています。

https://github.com/aws/bedrock-agentcore-sdk-python/pull/271

以上です。
参考になれば幸いです。
