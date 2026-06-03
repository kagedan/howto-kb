---
id: "2026-06-02-amazon-bedrock-agentcore-policyを試してみた-01"
title: "Amazon Bedrock AgentCore Policyを試してみた"
url: "https://zenn.dev/fusic/articles/6c0076890d6c02"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "prompt-engineering", "AI-agent", "Python", "zenn"]
date_published: "2026-06-02"
date_collected: "2026-06-03"
summary_by: "auto-rss"
query: ""
---

## はじめに

Fusicの[レオナ](https://x.com/xthixsl_ml)です。  
今回は、2026年3月にGAとなったAmazon Bedrock AgentCore Policyを試しました。

AgentCore Policyは、AIエージェントのツール呼び出しをポリシーで制御する機能です。本ブログでは、社内備品注文を題材にして、5,000円未満の注文だけを許可する構成をTerraformで作ります。

## AgentCore Policyとは

AgentCore Policyは、AIエージェントがAgentCore Gateway経由でツールを呼び出すときに、「この操作を許可してよいか」を判定する仕組みです。

ポイントなのは、ポリシーがAIエージェントのコードとは別に動く点です。

AIエージェントのコード内にセキュリティロジックを書く方法には、次のような課題があります。

* 安全性がラッパーコードの実装に依存する
* プロンプトインジェクションで、コード内のルールを回避される可能性がある

AgentCore Policyでは、この制御をAIエージェントの外側に置きます。AgentCore Gatewayがツール呼び出し前にリクエストを評価し、ポリシーに基づいて許可または拒否を判断します。

## Cedarポリシー言語とは

Cedarは、アクセス制御ルールを書くためのポリシー言語です。主な特徴をまとめてみました。

* デフォルト拒否: 明示的に`permit`されていないリクエストは拒否される
* 順序非依存: ポリシーの評価順序に依存しない

詳しくは以下をご覧ください。  
<https://arxiv.org/abs/2403.04651>

### 基本構文

Cedarポリシーは、`permit`または`forbid`で始まります。`principal`、`action`、`resource`で、誰が、何を、どのリソースに対して実行するかを書きます。

example.cedar

```
permit(
  principal == User::"alice",
  action == Action::"view",
  resource == Photo::"VacationPhoto94.jpg"
);
```

> 「ポリシーを一度定義してから、複数のプリンシパルとリソースで使用できます。」
>
> 引用: [Amazon Verified Permissions ポリシーテンプレートの作成](https://docs.aws.amazon.com/ja_jp/verifiedpermissions/latest/userguide/policy-templates-create.html)

`when` 句で条件を付加できます。

example.cedar

```
permit(
  principal == User::"alice",
  action,
  resource
) when {
  context has readOnly && context.readOnly == true
};
```

## 試してみた

社内備品注文を例に、AgentCore Policyをデプロイします。

### シナリオ

社内備品の注文をAIエージェントが代行するシステムを想定します。

ルールはシンプルです。

* 5,000円未満の注文は許可
* 5,000円以上の注文は拒否

このルールをプロンプトだけで守らせるのは不安です。そこで、AgentCore Gatewayに関連付けたPolicy Engineで判定します。

### デプロイモード

Policy Engineには2つのモードがあります。

| モード | 動作 |
| --- | --- |
| **LOG\_ONLY** | 判定だけ行う。実際にはブロックしない |
| **ENFORCE** | 判定結果に従って許可/拒否する |

今回は、ポリシーで実際に拒否されるところまで確認したいので`ENFORCE`で実行します。

## 処理フロー

1. Strands AgentsのAIエージェントがAgentCore GatewayのMCPエンドポイントにツール呼び出しを送る
2. AgentCore GatewayがPolicy Engineに判定を依頼する
3. Policy EngineがCedarポリシーを評価する
4. 許可された場合、Gateway Target経由でLambda関数を呼び出す

### 構成

| リソース | 説明 |
| --- | --- |
| Lambda関数 (`order_supply`) | 備品注文を処理するツール |
| AgentCore Gateway | MCPプロトコルでツールを公開 |
| Policy Engine + Cedarポリシー | 5,000円未満の注文のみ許可 |
| AgentCore Runtime | 今回は作成しない |

## 実装

### ディレクトリ構造

tree.txt

```
作業ディレクトリ/
├── agent.py
├── pyproject.toml
├── uv.lock
└── envs/
    └── dev/
        ├── gateway.tf
        ├── iam.tf
        ├── lambda.tf
        ├── outputs.tf
        ├── policy.tf
        ├── provider.tf
        ├── variables.tf
        ├── versions.tf
        ├── lambda/
        │   └── order_supply.py
        └── scripts/
            └── sync_policy.sh
```

### 1. Terraformコード

#### プロバイダー設定

今回は`hashicorp/aws`プロバイダー v6.47.0で試しました。

envs/dev/versions.tf

```
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 6.47.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.7"
    }
    time = {
      source  = "hashicorp/time"
      version = "~> 0.13"
    }
  }
}
```

`archive`はLambda関数のzipファイルを作る`archive_file`で使います。`time`はIAMロールとポリシー作成後、AgentCore Gateway作成前に少し待つ`time_sleep`で使います。

Pythonの実行は`uv run python`で行います。Strands Agentsで使う依存関係は`pyproject.toml`にまとめます。

pyproject.toml

```
[project]
name = "agentcore-policy-demo"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "awscrt>=0.33.0",
  "mcp>=1.27.2",
  "strands-agents>=1.42.0",
]
```

### 2. Lambda関数（備品注文ツール）

備品注文ツールとして、Lambda関数を作成します。

envs/dev/lambda/order\_supply.py

```
def handler(event, context):
    item = event.get("item", "unknown")
    quantity = event.get("quantity", 1)
    amount = event.get("amount", 0)

    return {
        "status": "ordered",
        "item": item,
        "quantity": quantity,
        "amount": amount,
        "message": f"{item} x{quantity} ({amount}円) の注文を受け付けました。",
    }
```

### 3. Policy Engineとポリシー

Policy Engineを作成し、Cedarポリシーを登録します。ここでは、`amount`が5,000未満のときだけ許可します。

envs/dev/policy.tf

```
locals {
  policy_name = "allow_order_under_limit"

  cedar_statement = <<-CEDAR
    permit(
      principal,
      action == AgentCore::Action::"SupplyOrderTarget___order_supply",
      resource == AgentCore::Gateway::"${aws_bedrockagentcore_gateway.main.gateway_arn}"
    ) when {
      context.input has amount &&
      context.input.amount < ${var.order_limit}
    };
  CEDAR
}

resource "aws_bedrockagentcore_policy_engine" "main" {
  name        = replace("${var.project_name}_policy_engine", "-", "_")
  description = "Policy engine for AgentCore Policy demo"

  tags = {
    Project = var.project_name
  }
}
```

AWS Provider v6.47.0には`aws_bedrockagentcore_policy_engine`があります。一方で、Cedarポリシー本体を作る`aws_bedrockagentcore_policy`は、このバージョンにはありませんでした。

なお、`aws_bedrockagentcore_resource_policy`というリソースはありますが、これはAgentCore RuntimeやGatewayに付けるリソースベースポリシーで、今回扱うCedarポリシーとは別物です。

そのため、AWS Providerで対応しているPolicy EngineまではTerraformリソースとして作り、未対応のCedarポリシー本体の作成・更新はAWS CLIの`bedrock-agentcore-control create-policy` / `update-policy`をTerraformから呼び出しています。

envs/dev/policy.tf

```
resource "terraform_data" "cedar_policy" {
  input = {
    policy_engine_id = aws_bedrockagentcore_policy_engine.main.policy_engine_id
    policy_name      = local.policy_name
    cedar_statement  = local.cedar_statement
    region           = var.aws_region
  }

  triggers_replace = {
    policy_engine_id = aws_bedrockagentcore_policy_engine.main.policy_engine_id
    policy_name      = local.policy_name
    cedar_hash       = sha256(local.cedar_statement)
  }

  provisioner "local-exec" {
    command = "bash '${path.module}/scripts/sync_policy.sh'"
    environment = {
      POLICY_ENGINE_ID = self.input.policy_engine_id
      POLICY_NAME      = self.input.policy_name
      POLICY_DESC      = "Allow supply orders under ${var.order_limit} yen"
      CEDAR_STATEMENT  = self.input.cedar_statement
      AWS_REGION       = self.input.region
    }
  }
}
```

`sync_policy.sh`では、同名のポリシーがあれば更新、なければ作成します。

envs/dev/scripts/sync\_policy.sh

```
tmp_definition="$(mktemp)"
trap 'rm -f "$tmp_definition"' EXIT

export CEDAR_STATEMENT
uv run python - "$tmp_definition" <<'PY'
import json
import os
import sys

path = sys.argv[1]
definition = {
    "cedar": {
        "statement": os.environ["CEDAR_STATEMENT"],
    }
}
with open(path, "w", encoding="utf-8") as f:
    json.dump(definition, f, ensure_ascii=False)
PY

policy_id="$(
  aws bedrock-agentcore-control list-policies \
    --policy-engine-id "$POLICY_ENGINE_ID" \
    --region "$AWS_REGION" \
    --query "policies[?name=='$POLICY_NAME'].policyId | [0]" \
    --output text
)"

if [[ -n "$policy_id" && "$policy_id" != "None" ]]; then
  aws bedrock-agentcore-control update-policy \
    --policy-engine-id "$POLICY_ENGINE_ID" \
    --policy-id "$policy_id" \
    --description "optionalValue=$POLICY_DESC" \
    --definition "file://$tmp_definition" \
    --validation-mode IGNORE_ALL_FINDINGS \
    --region "$AWS_REGION"
else
  aws bedrock-agentcore-control create-policy \
    --policy-engine-id "$POLICY_ENGINE_ID" \
    --name "$POLICY_NAME" \
    --description "$POLICY_DESC" \
    --definition "file://$tmp_definition" \
    --validation-mode IGNORE_ALL_FINDINGS \
    --region "$AWS_REGION"
fi
```

明示的な`forbid`は書いていません。Cedarはデフォルト拒否なので、`permit`にマッチしないリクエストは拒否されます。

### 4. AgentCore Gateway

AgentCore GatewayもAWS Providerで作ります。

envs/dev/gateway.tf

```
resource "aws_bedrockagentcore_gateway" "main" {
  name            = "${var.project_name}-gateway"
  protocol_type   = "MCP"
  authorizer_type = var.gateway_authorizer_type
  role_arn        = aws_iam_role.gateway.arn
  description     = "AgentCore Gateway with Policy enforcement demo"
}
```

AWS Provider v6.47.0時点の`aws_bedrockagentcore_gateway`には、`policy_engine_configuration`引数がありませんでした。一方で、AWS CLIの`update-gateway`には`--policy-engine-configuration`があります。

そのため、Gateway本体はAWS Providerで作成し、Policy Engineの関連付けだけAWS CLIの`update-gateway`をTerraformの`local-exec`から呼び出しています。

envs/dev/policy.tf

```
resource "terraform_data" "attach_policy_engine" {
  input = {
    gateway_id         = aws_bedrockagentcore_gateway.main.gateway_id
    gateway_name       = aws_bedrockagentcore_gateway.main.name
    gateway_role_arn   = aws_iam_role.gateway.arn
    policy_engine_arn  = aws_bedrockagentcore_policy_engine.main.policy_engine_arn
    policy_engine_mode = var.policy_engine_mode
    region             = var.aws_region
  }

  provisioner "local-exec" {
    command = <<-EOT
      aws bedrock-agentcore-control update-gateway \
        --gateway-identifier '${self.input.gateway_id}' \
        --name '${self.input.gateway_name}' \
        --description 'AgentCore Gateway with Policy enforcement demo' \
        --role-arn '${self.input.gateway_role_arn}' \
        --protocol-type MCP \
        --authorizer-type '${var.gateway_authorizer_type}' \
        --policy-engine-configuration arn='${self.input.policy_engine_arn}',mode='${self.input.policy_engine_mode}' \
        --region '${self.input.region}'
    EOT
  }
}
```

### 5. Gateway Target

envs/dev/gateway.tf

```
resource "aws_bedrockagentcore_gateway_target" "order_supply" {
  gateway_identifier = aws_bedrockagentcore_gateway.main.gateway_id
  name               = "SupplyOrderTarget"
  description        = "Office supply ordering Lambda target"

  credential_provider_configuration {
    gateway_iam_role {}
  }

  target_configuration {
    mcp {
      lambda {
        lambda_arn = aws_lambda_function.order_supply.arn

        tool_schema {
          inline_payload {
            name        = "order_supply"
            description = "Process an office supply order"

            input_schema {
              type = "object"

              property {
                name        = "item"
                type        = "string"
                description = "The name of the office supply item to order"
                required    = true
              }

              property {
                name        = "quantity"
                type        = "integer"
                description = "The number of items to order"
                required    = true
              }

              property {
                name        = "amount"
                type        = "integer"
                description = "The total order amount in yen"
                required    = true
              }
            }
          }
        }
      }
    }
  }
}
```

`amount`は`integer`にしています。`number`にするとCedarの数値比較で型が合わなくなります。

### 6. IAMロール

AgentCore Gatewayのサービスロールには、Lambda関数の呼び出し権限とPolicy Engine関連の権限が必要です。

envs/dev/iam.tf

```
resource "aws_iam_role_policy" "gateway" {
  role = aws_iam_role.gateway.id

  policy = jsonencode({
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["lambda:InvokeFunction"]
        Resource = aws_lambda_function.order_supply.arn
      },
      {
        Effect   = "Allow"
        Action   = ["bedrock-agentcore:GetPolicyEngine"]
        Resource = ["arn:aws:bedrock-agentcore:*:*:policy-engine/*"]
      },
      {
        Effect = "Allow"
        Action = [
          "bedrock-agentcore:AuthorizeAction",
          "bedrock-agentcore:PartiallyAuthorizeActions"
        ]
        Resource = [
          "arn:aws:bedrock-agentcore:*:*:policy-engine/*",
          "arn:aws:bedrock-agentcore:*:*:gateway/*"
        ]
      }
    ]
  })
}
```

Policy Engine関連では、`GetPolicyEngine`、`AuthorizeAction`、`PartiallyAuthorizeActions`を許可します。`AuthorizeAction`と`PartiallyAuthorizeActions`は、Policy EngineとAgentCore Gatewayの両方のARNを対象にします。

信頼ポリシーには`ArnLike`条件も入れます。

envs/dev/iam.tf

```
assume_role_policy = jsonencode({
  Statement = [{
    Effect    = "Allow"
    Principal = { Service = "bedrock-agentcore.amazonaws.com" }
    Action    = "sts:AssumeRole"
    Condition = {
      StringEquals = {
        "aws:SourceAccount" = data.aws_caller_identity.current.account_id
      }
      ArnLike = {
        "aws:SourceArn" = "arn:aws:bedrock-agentcore:${data.aws_region.current.region}:${data.aws_caller_identity.current.account_id}:*"
      }
    }
  }]
})
```

### 7. 実行

```
cd envs/dev
terraform init
terraform apply
```

### 8. Strands Agentsから実行する

最後に、Strands AgentsでAIエージェントを作ります。AgentCore GatewayはMCPエンドポイントを公開しているので、Strands Agentsの`MCPClient`でツール一覧を取得し、Agentの`tools`に渡します。

Strands AgentsのMCP連携については、公式ドキュメントにも例があります。  
<https://strandsagents.com/docs/user-guide/concepts/tools/mcp-tools/>

agent.py

```
import logging
import os
import re

from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.tools.mcp import MCPClient

GATEWAY_URL = os.environ.get("GATEWAY_URL", "").rstrip("/")
MODEL_ID = os.environ.get("MODEL_ID", "amazon.nova-lite-v1:0")
TOOL_NAME = "SupplyOrderTarget___order_supply"

def clean_response(text: str) -> str:
    return re.sub(r"<thinking>.*?</thinking>\s*", "", text, flags=re.DOTALL).strip()

def build_agent(tools: list[object]) -> Agent:
    return Agent(
        model=MODEL_ID,
        tools=tools,
        callback_handler=None,
        system_prompt=(
            "あなたは社内備品注文エージェントです。ユーザーが注文を依頼したら、"
            f"必ず{TOOL_NAME}ツールを呼び出してください。"
            "item, quantity, amountを注文文から抽出してください。"
            "ツールが拒否された場合は、拒否されたことを簡潔に伝えてください。"
            "最終応答に<thinking>タグや推論過程を含めないでください。"
        ),
    )

def run_prompt(tools: list[object], prompt: str) -> None:
    agent = build_agent(tools)
    response = agent(prompt)
    metric = response.metrics.tool_metrics.get(TOOL_NAME)

    print(f"ユーザー依頼: {prompt}")
    if metric:
        print(f"ツール: {metric.tool['name']}")
        print(f"ツール入力: {metric.tool['input']}")
        print(f"成功: {metric.success_count} 失敗: {metric.error_count}")
    print(f"最終応答: {clean_response(str(response))}")

def main() -> None:
    if not GATEWAY_URL:
        raise RuntimeError("GATEWAY_URL is not set")

    os.environ.setdefault("AWS_REGION", "ap-northeast-1")
    os.environ.setdefault("AWS_DEFAULT_REGION", os.environ["AWS_REGION"])

    logging.getLogger("strands").setLevel(logging.CRITICAL)
    logging.getLogger("strands.tools.mcp.mcp_client").setLevel(logging.CRITICAL)

    prompts = [
        "コピー用紙A4を3個、合計3000円で注文してください。",
        "高級オフィスチェアを1個、合計8000円で注文してください。",
    ]

    mcp_client = MCPClient(lambda: streamablehttp_client(url=GATEWAY_URL), startup_timeout=30)
    with mcp_client:
        tools = mcp_client.list_tools_sync()
        print(f"利用可能なMCPツール: {[tool.tool_name for tool in tools]}")

        for index, prompt in enumerate(prompts):
            if index:
                print("---")
            run_prompt(tools, prompt)

if __name__ == "__main__":
    main()
```

実行します。

```
GATEWAY_URL="$(terraform -chdir=envs/dev output -raw gateway_url)" uv run python agent.py
```

## 結果

今回の`envs/dev`では`policy_engine_mode = "ENFORCE"`で実行しました。実際の結果です。

agent-result

```
利用可能なMCPツール: ['SupplyOrderTarget___order_supply']
ユーザー依頼: コピー用紙A4を3個、合計3000円で注文してください。
ツール: SupplyOrderTarget___order_supply
ツール入力: {'item': 'コピー用紙A4', 'amount': 3000, 'quantity': 3}
成功: 1 失敗: 0
最終応答: コピー用紙A4 x3 (3000円) の注文を受け付けました。
---
ユーザー依頼: 高級オフィスチェアを1個、合計8000円で注文してください。
ツール: SupplyOrderTarget___order_supply
ツール入力: {'item': '高級オフィスチェア', 'amount': 8000, 'quantity': 1}
成功: 0 失敗: 1
最終応答: 申し訳ありませんが、このツールは現在利用できません。高級オフィスチェアの注文は今のところ受け付けられないようです。
```

実行結果を見ると、Strands Agentsが注文文から`item`、`quantity`、`amount`を抽出し、`SupplyOrderTarget___order_supply`ツールを呼び出しています。

3,000円の注文はCedarポリシーの`permit`に一致し、Lambda関数まで実行されています。一方、8,000円の注文は`permit`に一致しないため、AgentCore Gateway側で拒否されました。

この結果から、AIエージェントがツール呼び出しを試みても、最終的な許可・拒否はGatewayに関連付けたPolicy Engineで制御されることを確認できました。

## 最後に

AgentCore Policyを使うと、ツール実行の可否をAIエージェントの外側で制御できます。今回は備品注文を例にしましたが、金額上限やデータアクセス制御にも使えそうです。プロンプトだけにルールを任せず、AgentCore Gateway側で判定できるのがよい点だと思いました。
