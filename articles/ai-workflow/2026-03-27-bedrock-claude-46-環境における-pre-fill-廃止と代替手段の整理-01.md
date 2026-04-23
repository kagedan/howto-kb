---
id: "2026-03-27-bedrock-claude-46-環境における-pre-fill-廃止と代替手段の整理-01"
title: "Bedrock (Claude 4.6) 環境における pre-fill 廃止と代替手段の整理"
url: "https://qiita.com/enumura1/items/d0f53e82ed6b59668b67"
source: "qiita"
category: "ai-workflow"
tags: ["Python", "qiita"]
date_published: "2026-03-27"
date_collected: "2026-03-27"
summary_by: "auto-rss"
---

# はじめに

Lambda（Python）から Bedrock 経由で Claude を呼んでいる構成で、モデルを Sonnet 4.5 → Sonnet 4.6 に差し替えたところ、今まで動いていたコードが 400 エラーで落ちました。

モデルID

```
- 旧：jp.anthropic.claude-sonnet-4-5-20250929-v1:0
- 新：jp.anthropic.claude-sonnet-4-6
```

原因は pre-fill（アシスタントメッセージのプリフィル）の廃止です。  
Claude 4.6 では、`messages` の末尾に `role: "assistant"` を置く書き方がエラーになります。

Anthropic の [マイグレーションガイド](https://platform.claude.com/docs/en/about-claude/models/migration-guide) に Breaking changes として記載されている内容です。

この記事では、変更の内容と対応策をまとめています。

# pre-fill とは？

`messages` 配列の最後に assistant（生成AI側）ロールのメッセージを入れて、モデルの出力の先頭を誘導するチューニングです。Anthropic のドキュメントにも記載されています。

参考：[Prompting best practices — Migrating away from prefilled responses](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)

```
# Sonnet 4.5 以前で動いていたコード
response = bedrock_runtime.invoke_model(
    modelId="jp.anthropic.claude-sonnet-4-5-20250929-v1:0",
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [
            {"role": "user", "content": "キーワードをJSON配列で返して。..."},
            {"role": "assistant", "content": "["}  # ← pre-fill
        ]
    })
)
```

レスポンスを指定のフォーマットや前置きの続きから生成する用途で使われるものになります。

## 4.6 での変更内容

Anthropic の [マイグレーションガイド](https://platform.claude.com/docs/en/about-claude/models/migration-guide) に以下の記載があります。

> **Prefill removal:** Prefilling assistant messages returns a 400 error on Claude 4.6 models. Use structured outputs, system prompt instructions, or `output_config.format` instead.

4.6 系（Opus、Sonnet）の両方が対象です。

今回 Lambda から Bedrock のモデルを Sonnet 4.5 → Sonnet 4.6 に差し替えて呼び出したところ、エラーに落ちました。

```
This model does not support assistant message prefill.
The conversation must end with a user message.
```

再現コード（Lambda で 400 エラーを確認する）

```
import json
import boto3

bedrock_runtime = boto3.client("bedrock-runtime", region_name="ap-northeast-1")

def lambda_handler(event, context):
    try:
        response = bedrock_runtime.invoke_model(
            modelId="jp.anthropic.claude-sonnet-4-6",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1024,
                "messages": [
                    {
                        "role": "user",
                        "content": "AWSの主要サービスを3つ挙げてJSON配列で返してください。"
                    },
                    {
                        "role": "assistant",
                        "content": "["  # ← これが原因
                    }
                ]
            })
        )
        result = json.loads(response["body"].read())
        return {"statusCode": 200, "body": json.dumps(result)}

    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(e)})
        }
```

`modelId` を `jp.anthropic.claude-sonnet-4-5-20250929-v1:0`（Sonnet 4.5）に戻すと正常に動きます。

## pre-fill の用途別の移行先

マイグレーションガイドでは、pre-fill の用途別に移行先が案内されています。  
ここでは以下の2つを取り上げます。

1. JSON 等の出力形式を強制したい場合

> **Controlling output formatting** (forcing JSON/YAML output): Use structured outputs or tools with enum fields for classification tasks.

→ JSON 等の出力形式を強制したい場合は Structured Outputs を使う。

1. 出力の前置きを制御したい場合

> **Eliminating preambles** (removing "Here is..." phrases): Add direct instructions in the system prompt: "Respond directly without preamble. Do not start with phrases like 'Here is...', 'Based on...', etc."

→ 「Here is...」のような前置きを消したい場合は、システムプロンプトで直接指示する。

参考：[Migration guide — When migrating from Sonnet 4.5](https://platform.claude.com/docs/en/about-claude/models/migration-guide#when-migrating-from-sonnet-4-5)

## 対応策1：Structured Outputs（JSON Schema 指定）

決まった構造の JSON を出力させたい 場合に使います。

APIをコールする際に、出力してほしいJSON Schema を渡すことで、モデルのレスポンスがスキーマに沿った形で返るようになります。

Bedrock では `output_config.format` パラメータで指定します。

### コード例

```
import json
import boto3

bedrock_runtime = boto3.client("bedrock-runtime", region_name="ap-northeast-1")

def lambda_handler(event, context):
    user_text = event.get("text", "")

    response = bedrock_runtime.invoke_model(
        modelId="jp.anthropic.claude-sonnet-4-6",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "messages": [
                {
                    "role": "user",
                    "content": f"以下のテキストからキーワードを抽出してください。\n\n{user_text}"
                }
            ],
            "output_config": {
                "format": {
                    "type": "json_schema",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "keywords": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "抽出されたキーワードのリスト"
                            }
                        },
                        "required": ["keywords"],
                        "additionalProperties": false
                    }
                }
            }
        })
    )

    result = json.loads(response["body"].read())
    output = json.loads(result["content"][0]["text"])

    return {"statusCode": 200, "body": json.dumps({"keywords": output["keywords"]})}
```

検証結果（Lambda → Bedrock 実行）

スキーマで定義した `keywords`（文字列のリスト）を持つオブジェクトが返ることを期待しています。

期待するレスポンス構造

```
{
  "keywords": ["キーワード1", "キーワード2", "キーワード3"]
}
```

以下のテキストを `user_text` として渡しました。

> Amazon BedrockはAWSが提供するフルマネージドサービスで、主要なAI企業の基盤モデルを単一のAPIで利用できます。

レスポンス（`content[0].text` をパースした結果）：

```
{
  "keywords": [
    "Amazon Bedrock",
    "AWS",
    "フルマネージドサービス",
    "AI企業",
    "基盤モデル",
    "API"
  ]
}
```

スキーマで定義した `keywords`（文字列の配列）の構造通りに出力されています。

Structured Outputsを使ってスキーマ定義なしでJSONだけ固定、はできるのか検証してみました。

[Structured Outputs > InvokeModel (Anthropic Claude)](https://docs.aws.amazon.com/bedrock/latest/userguide/structured-output.html)では、例として`output_config.format.type` に指定できる値は `"json_schema"` が記載されています。スキーマなしで JSON であることだけを固定するモードはどうなるのかわからなかったです。

`"type": "json_schema"` でスキーマを `{"type": "object"}` だけにする（プロパティ定義なし）とどうなるか検証しました。

```
"output_config": {
    "format": {
        "type": "json_schema",
        "schema": {
            "type": "object"
        }
    }
}
```

検証結果：400 エラーでした。  
`additionalProperties` の明示的な指定が必須でした。

```
ValidationException: For 'object' type, 'additionalProperties' must be explicitly set to false
```

`"additionalProperties": false` を追加すると API 呼び出し自体は成功しますが、`properties` を定義していないため `{}`（空オブジェクト）しか返りません。  
スキーマ定義なしでの JSON 出力固定はできないため、`properties` を含むスキーマ定義が必要でした。

検証用コード全文

```
import json
import boto3

bedrock_runtime = boto3.client("bedrock-runtime", region_name="ap-northeast-1")

def test_loose_schema(event, context):
    """プロパティなしの緩いスキーマで通るかの検証"""
    try:
        response = bedrock_runtime.invoke_model(
            modelId="jp.anthropic.claude-sonnet-4-6",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1024,
                "messages": [
                    {
                        "role": "user",
                        "content": "AWSの主要サービスを3つ、名前と説明付きで教えて。"
                    }
                ],
                "output_config": {
                    "format": {
                        "type": "json_schema",
                        "schema": {
                            "type": "object"
                        }
                    }
                }
            })
        )
        result = json.loads(response["body"].read())
        return {
            "statusCode": 200,
            "pattern": "loose_schema",
            "body": result["content"][0]["text"]
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "pattern": "loose_schema",
            "error": str(e)
        }
```

## 対応策2：システムプロンプトでの指示

対応策1の Structured Outputs では、JSON の中身の項目（`properties`）まで定義する必要があります。  
「スキーマ定義なしでJSONだけ固定」の検証で確認した通り、`properties` を定義しないと空オブジェクトしか返ってこなかったです。

JSON で返してほしいが中身の構造まで決めきれない場合や、「Here is...」のような前置きを出さずに回答させたい場合は、システムプロンプトで出力形式を指示する方法があります。

マイグレーションガイドには以下の記載があります。

> **Eliminating preambles** (removing "Here is..." phrases): Add direct instructions in the system prompt: "Respond directly without preamble. Do not start with phrases like 'Here is...', 'Based on...', etc."

参考：[Migration guide — When migrating from Sonnet 4.5](https://platform.claude.com/docs/en/about-claude/models/migration-guide#when-migrating-from-sonnet-4-5)

今回は、システムプロンプトの指示でレスポンスを JSON 形式で生成するように指示します。

```
import json
import boto3

bedrock_runtime = boto3.client("bedrock-runtime", region_name="ap-northeast-1")

def lambda_handler(event, context):
    user_text = event.get("text", "")

    response = bedrock_runtime.invoke_model(
        modelId="jp.anthropic.claude-sonnet-4-6",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "system": (
                "あなたはキーワード抽出エンジンです。"
                "応答は要素がJSONオブジェクトのリストで返してください。"
                "前置き、説明、コードブロックは不要です。"
                '例: [{"keyword": "キーワード1"}, {"keyword": "キーワード2"}]'
            ),
            "messages": [
                {
                    "role": "user",
                    "content": f"以下のテキストからキーワードを抽出してください。\n\n{user_text}"
                }
            ]
        })
    )

    result = json.loads(response["body"].read())
    output_text = result["content"][0]["text"].strip()
    keywords = json.loads(output_text)

    return {"statusCode": 200, "body": json.dumps({"keywords": keywords})}
```

Structured Outputs とは異なりスキーマによる出力制御がないため、レスポンスが期待した形式でない可能性があります。JSON パースの失敗に備えたガードやリトライを入れておくと安全です。

検証結果（Lambda → Bedrock 実行）

以下のテキストを `user_text` として渡しました。

> Amazon BedrockはAWSが提供するフルマネージドサービスで、主要なAI企業の基盤モデルを単一のAPIで利用できます。

前置きなしで、要素が JSON オブジェクトのリストが返ってきました。

```
[
  {"keyword": "Amazon Bedrock"},
  {"keyword": "AWS"},
  {"keyword": "フルマネージドサービス"},
  {"keyword": "AI企業"},
  {"keyword": "基盤モデル"},
  {"keyword": "API"}
]
```

システムプロンプトの指示通りの形式で出力されています。

## どっちを使うか

レスポンスのフォーマットや形式を指定したい場合、以下のように場合分けできるかと思います。

## 参考リンク
