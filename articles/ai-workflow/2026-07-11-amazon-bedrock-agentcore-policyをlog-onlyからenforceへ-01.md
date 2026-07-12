---
id: "2026-07-11-amazon-bedrock-agentcore-policyをlog-onlyからenforceへ-01"
title: "Amazon Bedrock AgentCore PolicyをLOG_ONLYからENFORCEへ段階移行してみた"
url: "https://zenn.dev/fusic/articles/808aa7198d176f"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "prompt-engineering", "API", "AI-agent", "LLM", "Python"]
date_published: "2026-07-11"
date_collected: "2026-07-13"
summary_by: "auto-rss"
query: ""
---

## はじめに

Fusicの[レオナ](https://x.com/xthixsl_ml)です。

今回は、Amazon Bedrock AgentCore Policy(以下、AgentCore Policy)をLOG\_ONLYからENFORCEへ段階移行するところまで試してみました。

前回のブログでは、社内備品注文を題材に、Amazon Bedrock AgentCore Gateway(以下、Gateway)、AWS Lambda、Policy Engine、Cedar PolicyをTerraformで作り、金額による許可と拒否をENFORCEで確認しました。  
<https://zenn.dev/fusic/articles/6c0076890d6c02>

そのため、この記事ではAgentCore PolicyとCedarの基礎、Gateway Target、IAMロールのTerraformコードを繰り返しません。  
前回の構成を出発点として、Engine全体のLOG\_ONLY、個別PolicyのLOG\_ONLY、異常系、Amazon CloudWatchメトリクス、Policy Deny後の停止条件を追加します。

対象は、Gatewayへ登録した固定のMCP Toolと、そのToolへ渡す引数です。  
ユーザーの入力文をAgentCore Policyが直接検査する構成ではありません。

検証には東京リージョンを使いました。  
検証用のAWS Lambdaは受け取った引数を再検証して返し、実際のサービス再起動やFeature Flag変更は行いません。

## 前回の記事から追加する範囲

前回は、単一のToolへ金額条件を付け、Engine全体をENFORCEにした結果まで確認しました。  
今回は、Policyを強制する前後の運用へ範囲を広げます。

| 項目 | 前回 | 今回 |
| --- | --- | --- |
| Tool条件 | 注文金額 | 環境名、サービス名、変更量 |
| Policy Engine | ENFORCE | LOG\_ONLYからENFORCEへ変更 |
| 個別Policy | ACTIVE | LOG\_ONLYで影響を観測してからACTIVEへ変更 |
| 検証 | 金額による許可と拒否 | 11ケース、メトリクス、再試行停止 |

AgentCore Policyには、Engine全体と個別Policyで異なるModeがあります。  
PolicyリソースのStatusも別に存在するため、次の3種類を分けて扱います。

| 対象 | 値 | 意味 |
| --- | --- | --- |
| Gatewayの`policyEngineConfiguration.mode` | `LOG_ONLY`または`ENFORCE` | Policy Engine全体の判定をGatewayが強制するかを決める |
| Policyの`enforcementMode` | `LOG_ONLY`または`ACTIVE` | 個別Policyを強制判定へ含めるかを決める |
| Policyリソースの`status` | `CREATING`、`UPDATING`、`ACTIVE`など | 非同期処理中か、利用可能かを示す |

個別Policyが`LOG_ONLY`でも評価自体は行われます。  
ただし、評価結果は強制判定へ含まれず、別の結果として記録されます。

PolicyがDenyを返したあとの停止は、前回の記事で扱っていない差分です。  
GatewayはTool実行を拒否しますが、Agentが別のToolを選ぶ処理までは止めません。  
そこで、MCPクライアントがPolicy Denyを`policy_denied`へ正規化し、Tool呼び出しループを終了させます。

## 作るもの

検証用リソースには、Terraform変数で渡す`<namespace>`を共通の接頭辞として付けました。  
環境固有の名前は記事へ載せず、次の命名規則で表します。

| 項目 | 設定 |
| --- | --- |
| Namespace | `<namespace>` |
| Region | `ap-northeast-1` |
| Policy Engine | `<namespace>-policy-engine` |
| Gateway | `<namespace>-gateway` |
| Gateway Target | `<namespace>-ops-tools` |
| AWS Lambda | `<namespace>-policy-tools` |
| Gatewayの認証 | `NONE`(検証用のみ) |

Gatewayの認証を`NONE`にしたのは、Policyの挙動だけを分離して測るためです。  
本番で認証なしのGatewayを使う設計を推奨するものではありません。

この構成ではOAuth Claim、IAM principal、Agentごとの認可を検証していません。  
Cedarも裸の`principal`を使い、Tool名と引数だけを判定しています。

Targetには、次の3つのToolを登録しました。

1. `restart_service`：サービス再起動を模した状態変更系Tool。
2. `read_metrics`：メトリクス取得を模した読み取り系Tool。
3. `update_feature_flag`：Policyを用意しないToolの検証に使う状態変更系Tool。

今回はproduction変更の人間承認経路を作りません。  
productionの`restart_service`は例外なく拒否します。

AWS Lambdaは認可後の入力をもう一度検証してから、変更を模した結果を返します。

検証後のPolicy構成は次のとおりです。

| Policy | `enforcementMode` | 役割 |
| --- | --- | --- |
| stagingの`read_metrics`を許可 | `ACTIVE` | 読み取りToolの許可 |
| stagingの1台から2台の`restart_service`を許可 | `ACTIVE` | 変更量を含む許可 |
| productionの`restart_service`を拒否 | `ACTIVE` | 将来の広いpermitより優先する明示拒否 |
| 複数台の`restart_service`を拒否 | `LOG_ONLY` | 影響確認用のshadow Policy |

## Terraform Providerの差分

前回の記事ではHashiCorp AWS Provider 6.47.0を使いました。[^previous-policy]  
このバージョンには`aws_bedrockagentcore_policy`がなく、Gatewayの`policy_engine_configuration`にも未対応だったため、TerraformからAWS CLIを呼び出して補っていました。

今回はAWS Provider 6.54.0を使います。  
このバージョンでは`aws_bedrockagentcore_policy`とGatewayの`policy_engine_configuration`をTerraform Resourceとして管理できました。

一方、`aws_bedrockagentcore_policy`には個別Policyの`enforcementMode`を指定する属性がありませんでした。  
AWS Lambda、IAMロール、Policy Engine、Gateway、Gateway Target、通常のCedar PolicyはTerraformで管理し、検証用shadow Policyの作成とMode切り替えだけBoto3を使います。

IAMロールとGateway TargetのTerraformコードは前回の記事と同じ考え方です。  
Gateway Execution RoleとResource Management Roleに必要な権限は公式ドキュメントでも分けて説明されているため、今回は設定内容を再掲しません。

## 実装

検証に使ったバージョンは次のとおりです。

| 項目 | バージョン |
| --- | --- |
| Terraform | 1.13.4 |
| HashiCorp AWS Provider | 6.54.0 |
| AWS CLI | 2.34.24 |
| Boto3 | 1.43.46 |
| Botocore | 1.43.46 |
| AWS Lambda Runtime | Python 3.13 |

GatewayのTool SchemaとAgentCore Policyを通過したあとも、AWS Lambdaで環境名、サービス名、変更量を検証します。

`restart_service`の検証とToolの振り分け部分は次のとおりです。  
`read_metrics`と`update_feature_flag`にも同じ形の検証を入れました。

```
import os

def _require_exact_keys(event, expected_keys):
    if set(event) != expected_keys:
        raise ValueError("unexpected input keys")

def _validate_restart_service(event):
    _require_exact_keys(
        event,
        {"environment", "service_name", "replica_count"},
    )
    if event["environment"] != "staging":
        raise ValueError("restart_service is limited to staging")
    if event["service_name"] != "inference_api":
        raise ValueError("service_name is not allowed")
    if type(event["replica_count"]) is not int:
        raise ValueError("replica_count must be an integer")
    if not 1 <= event["replica_count"] <= 2:
        raise ValueError("replica_count must be between 1 and 2")
    return "restart_service"

_VALIDATORS = {
    "restart_service": _validate_restart_service,
    "read_metrics": _validate_read_metrics,
    "update_feature_flag": _validate_update_feature_flag,
}

def _get_tool_name(context):
    custom = context.client_context.custom
    qualified_name = custom["bedrockAgentCoreToolName"]
    prefix = f"{os.environ['GATEWAY_TARGET_NAME']}___"
    if not qualified_name.startswith(prefix):
        raise ValueError("bedrockAgentCoreToolName is not supported")
    tool_name = qualified_name[len(prefix):]
    if tool_name not in _VALIDATORS:
        raise ValueError("bedrockAgentCoreToolName is not supported")
    return tool_name

def handler(event, context):
    tool_name = _get_tool_name(context)
    _VALIDATORS[tool_name](event)
    return {
        "status": "simulated",
        "tool_name": tool_name,
        "request_id": context.aws_request_id,
        "input": event,
}
```

Gatewayは、呼び出した完全修飾Tool名を`context.client_context.custom["bedrockAgentCoreToolName"]`へ渡します。  
Gateway Target名はTerraformからAWS Lambdaの環境変数`GATEWAY_TARGET_NAME`へ渡します。  
引数に`replica_count`があるかどうかで処理を推測せず、このTool名で検証関数を選びます。

AWS Lambdaを直接Invokeすると、stagingの2台は成功し、productionは`restart_service is limited to staging`で停止しました。  
さらに、Tool名を`read_metrics`にして`replica_count`を混ぜた入力は、`read_metrics`の契約にない属性として停止しました。

### Step.2: stagingのpermitとproductionのforbidを作る

前回の金額条件から、環境名、サービス名、変更量を組み合わせるPolicyへ変更しました。

`restart_service`は、stagingの`inference_api`かつ2台以下の場合だけ許可します。

Action名は、Gateway Target名とTool名を`___`でつないだ`<namespace>-ops-tools___restart_service`です。  
実際のCedarファイルでは、Terraformの`templatefile`から`target_name`を渡します。

```
permit (
    principal,
    action == AgentCore::Action::"${target_name}___restart_service",
    resource == AgentCore::Gateway::"<gateway-arn>"
)
when {
    context.input.environment == "staging" &&
    context.input.service_name == "inference_api" &&
    context.input.replica_count >= 1 &&
    context.input.replica_count <= 2
};
```

Cedarは既定拒否です。  
このpermitへ一致しない`replica_count=0`、`replica_count=3`、別の`service_name`は、ほかのpermitがなければ拒否されます。

productionはforbidで明示的に拒否しました。

```
forbid (
    principal,
    action == AgentCore::Action::"${target_name}___restart_service",
    resource == AgentCore::Gateway::"<gateway-arn>"
)
when {
    context.input.environment == "production"
};
```

既定拒否だけでもproductionは止まります。  
それでもforbidを置いたのは、後から広いpermitを追加してもproduction拒否を優先させるためです。

permitとforbidはCedarファイルへ分け、Terraformの`aws_bedrockagentcore_policy`から読み込みました。  
stagingのpermitは`validation_mode=FAIL_ON_ANY_FINDINGS`、productionのforbidは所見を確認したあとに`validation_mode=IGNORE_ALL_FINDINGS`としています。

最初はすべてのPolicyを`FAIL_ON_ANY_FINDINGS`で作成しました。  
productionのforbidは作成に失敗したため、`statusReasons`のAnalyzer所見を確認したうえで、Terraformの`validation_mode`を`IGNORE_ALL_FINDINGS`へ変更してapplyし直しました。  
PolicyのStatusが`ACTIVE`になってから呼び出しを始めます。

### Step.3: LOG\_ONLYからENFORCEへ切り替える

最初はGatewayの`policy_engine_configuration.mode`を`LOG_ONLY`にして`terraform apply`しました。  
Engine全体をENFORCEへ切り替えるときは、同じTerraform変数を`ENFORCE`へ変更して再度applyします。

Gatewayの更新は非同期です。  
`get-gateway`を繰り返し、Statusが`READY`へ戻ってからToolを呼びました。

検証用shadow Policyは、Engine全体をENFORCEにしたまま、Boto3の`create_policy`で`enforcementMode="LOG_ONLY"`を指定して追加しました。  
同じPolicyをACTIVEへ切り替えるときは、同じPolicy IDと定義をBoto3の`update_policy`へ渡しました。

```
import boto3

client = boto3.Session(
    region_name="ap-northeast-1",
).client("bedrock-agentcore-control")

current = client.get_policy(
    policyEngineId="<policy-engine-id>",
    policyId="<shadow-policy-id>",
)

client.update_policy(
    policyEngineId="<policy-engine-id>",
    policyId="<shadow-policy-id>",
    definition=current["definition"],
    enforcementMode="ACTIVE",
    validationMode="IGNORE_ALL_FINDINGS",
)
```

Policyの更新も非同期です。  
`get_policy`を繰り返し、Statusが`ACTIVE`へ戻り、`statusReasons`が空であることを確認しました。

## 検証

### Engine全体のLOG\_ONLY

Engine全体をLOG\_ONLYにすると、Tool Schemaを満たす呼び出しは、Policyの評価結果にかかわらずAWS Lambdaまで到達しました。

Tool内部検証を追加したあと、staging、production、`replica_count=3`の3ケースをもう一度実行しました。  
stagingの2台は成功し、productionと`replica_count=3`はAWS Lambdaまで到達したあと、Tool内部検証が`isError=true`で停止しました。

Engine全体のLOG\_ONLYは認可を強制しません。  
後段のToolまで到達させたまま判定結果を観測するため、Tool内部の検証を残した状態で使います。

### ENFORCEの11ケース

次にEngine全体をENFORCEへ切り替え、境界値と異常系を含む11ケースを実行しました。

| 入力 | 期待 | 実測 | 判定した場所 |
| --- | --- | --- | --- |
| staging、`replica_count=1` | ALLOW | ALLOW | permitに一致 |
| production | DENY | DENY | forbidに一致 |
| staging、`replica_count=2` | ALLOW | ALLOW | permitの境界値 |
| staging、`replica_count=-1` | DENY | DENY | permitの下限外 |
| staging、`replica_count=0` | DENY | DENY | permitの下限外 |
| staging、`replica_count=3` | DENY | DENY | 該当permitなし |
| `environment`欠損 | DENY | DENY | Policy評価時のMismatch |
| `replica_count`が文字列 | Schema Error | Schema Error | GatewayのTool Schema |
| Policyのない`update_feature_flag` | DENY | DENY | NoDeterminingPolicies |
| `service_name`に自然文命令 | DENY | DENY | 許可したサービス名と不一致 |
| `environment=Production` | DENY | DENY | 大文字と小文字が不一致 |

11件すべてが期待した終了状態になりました。

Prompt Injection後に生成されうる不正なTool引数を模して、`service_name`へ命令文を入れるケースと、`environment`の表記を変えるケースを用意しました。  
2件ともAWS Lambdaを呼ばずに拒否されました。

実際のLLMへ攻撃文を入力し、Tool引数を生成させた試験ではありません。  
この結果は「AgentCore PolicyがPrompt Injectionを検出した」という意味でもありません。  
AgentCore Policyが見たのは、Agentが生成したTool名と引数です。  
攻撃文を含む入力の扱いと、Policy Deny後の停止条件は別に実装します。

Policyを用意していない`update_feature_flag`は、次のエラーになりました。

```
Tool Execution Denied: Tool call not allowed due to policy enforcement
[No policy applies to the request (denied by default).]
```

登録されていないToolを呼んだ試験ではありません。  
Gatewayには存在するものの、判定するPolicyが一つもないToolを呼んだ試験です。

### 個別PolicyのLOG\_ONLY

Engine全体をENFORCEにしたまま、`replica_count > 1`を拒否するPolicyだけをLOG\_ONLYで追加しました。

同じ1分間に`replica_count=2`と`replica_count=3`を1回ずつ呼びました。  
Amazon CloudWatchには`LogOnlyMatches=2`と`LogOnlyDecisionFlips=1`が記録されました。  
shadow Policyは2件に一致しましたが、`replica_count=3`はACTIVE Policyだけでも既定拒否になるため、shadow Policyによって最終判定が変わるのは`replica_count=2`の1件だけです。

その後、同じPolicy IDの`enforcementMode`をACTIVEへ変更しました。  
同じ入力を呼ぶと、今度はshadow Policyの名前付きで拒否されました。

```
Policy evaluation denied due to
<namespace>-forbid-multi-replica-shadow
```

検証後はshadow PolicyをLOG\_ONLYへ戻しています。

### Policy判定のレイテンシ

AgentCore PolicyはPolicy関連のメトリクスを`AWS/Bedrock-AgentCore`名前空間へ出力します。

2026年7月11日13時38分から13時43分までのPolicy判定を、Period 300秒で集計しました。  
`Latency`は`TargetResource=<gateway-resource-id>`と`OperationName=AuthorizeAction`の2次元で取得しています。  
この時間帯にはMode切り替えとPolicy更新の試行が含まれるため、単一PolicyやENFORCEだけの性能値ではありません。

| 指標 | 実測値 |
| --- | --- |
| SampleCount | 42 |
| Average | 22.33ms |
| p50 | 18.74ms |
| p95 | 37.23ms |
| p99 | 40.22ms |
| Maximum | 41ms |

42サンプルでのp99は、分布の傾向を見るための参考値です。

更新後の11ケースで、クライアントからGatewayまでの往復時間は176msから584ms、平均323.8ms、中央値289msでした。  
この値にはネットワーク、Gateway、Policy、許可時のAWS Lambda実行が含まれます。

同じ時間帯の判定件数は次のとおりです。

| メトリクス | 値 |
| --- | --- |
| AllowDecisions(ENFORCE) | 12 |
| DenyDecisions(ENFORCE) | 17 |
| NoDeterminingPolicies | 16 |
| MismatchErrors | 5 |
| TotalMismatchedPolicies | 11 |

件数にはテストの再試行を含むため、11ケースの件数とは一致しません。  
また、`NoDeterminingPolicies`や`MismatchErrors`は判定理由を表す別メトリクスであり、AllowとDenyを分割した排他的な内訳ではありません。

`MismatchErrors`は、少なくとも一つのPolicyで属性欠損か型不一致が起きたリクエスト数です。  
`TotalMismatchedPolicies`は、各リクエストでMismatchしたPolicy数の合計です。

### Deny後の再試行

AgentCore PolicyはTool実行を拒否しますが、その後にAgentが別のToolを選ぶかどうかまでは制御しません。

今回のGatewayは、productionの拒否を次のJSON-RPCエラーで返しました。

```
{
  "jsonrpc": "2.0",
  "id": 701,
  "error": {
    "code": -32002,
    "message": "Tool Execution Denied: Tool call not allowed due to policy enforcement [...]"
  }
}
```

公式ドキュメントには、`result.isError=true`で返る例もあります。  
そのため、`-32002`だけを見てPolicy Denyと決めず、エラー構造と`Tool Execution Denied`などのPolicy由来メッセージを合わせて判定しました。  
判定結果をクライアント内部の`stop_reason=policy_denied`へ正規化し、Tool呼び出しループを終了します。

```
{
  "attempt_count": 1,
  "stop_reason": "policy_denied",
  "stopped_on_policy_deny": true,
  "fallback_attempted": false
}
```

productionの`restart_service`を拒否したあと、用意していた`update_feature_flag`へのフォールバックは実行されませんでした。  
実運用のAgentCore Runtime側へも、同じ停止条件を入れる必要があります。

## ポイント1: Policy Analyzerの所見を確認する

Policy作成時のSchema検査は、`validationMode`にかかわらず実行されます。  
`FAIL_ON_ANY_FINDINGS`ではSchema検査と意味検証を行い、どちらかに所見があればPolicyを拒否します。  
`IGNORE_ALL_FINDINGS`では意味検証を省略しますが、Schema検査は省略しません。

今回、条件なしのread permitは`Overly Permissive`、productionを拒否するforbidは`Overly Restrictive`となり、どちらも作成に失敗しました。

read permitは、対象環境と`service_name`を絞って厳格検証を通しました。

```
when {
    (context.input.environment == "staging" ||
     context.input.environment == "production") &&
    context.input.service_name == "inference_api"
};
```

作成失敗のStatusと`statusReasons`を確認し、read permitは条件を修正しました。  
productionのforbidは意図した明示拒否だったため、所見を確認してから`IGNORE_ALL_FINDINGS`で作成しました。  
`IGNORE_ALL_FINDINGS`をすべてのPolicyへ付けると、Analyzerを実行する意味がなくなります。

## ポイント2: SchemaとPolicyを同じリリースで扱う

Gateway TargetのSchemaだけを一時的に変更し、`environment`を必須属性から外しました。  
Policyは`context.input.environment`を参照したままです。

この状態で`environment`なしの`restart_service`を呼ぶと、3つのPolicyが次のMismatchを返しました。

```
record does not have the attribute `environment`
```

結果は`-32002`のDENYで、Amazon CloudWatchには`MismatchErrors`と`TotalMismatchedPolicies`が記録されました。  
検証後はSchemaを元の必須指定へ戻しています。

通常の必須Schemaへ戻した状態でも、EngineがENFORCEの場合、`environment`欠損はPolicyのMismatchとして先に拒否されました。  
EngineをLOG\_ONLYにするとPolicyの拒否は強制されず、同じ欠損入力は後段のGateway Schema Errorになりました。

一方、`replica_count="1"`は、ENFORCEでもGatewayのTool Schemaが文字列と整数の型不一致として拒否しました。  
今回の実測では、属性欠損と型不一致が常に同じ順番で拒否されるわけではありませんでした。  
サービス側の評価順序へ依存した停止場所を前提にせず、最終的にToolへ到達しないことと、各層のメトリクスを確認します。

GatewayのTool SchemaとPolicyが別々に変更されると、正しいPolicyでもMismatchが増えます。  
両方を同じリリース計画で扱い、欠損値と型不一致をテストへ残します。

## ポイント3: tracingは別途有効化する

Policyのメトリクスは既定で出力されますが、spanを確認するにはAmazon CloudWatch Transaction Searchと対象Gatewayのtracingを有効化する必要があります。

今回の検証時点ではTransaction Searchのサンプリングが0%で、`aws/spans`ロググループもありませんでした。  
アカウント全体の設定変更は行わず、各応答の`x-amzn-requestid`と、許可時のAWS Lambda Request IDを記録しました。

したがって、この記事で実測したのはPolicyメトリクスまでです。  
Policy spanとTrace IDは、tracingを有効化した環境で追加確認します。

## 最後に

Amazon Bedrock AgentCore PolicyでTool名と引数を判定し、LOG\_ONLYからENFORCEへ切り替えるところまで試してみました。

Engine全体のLOG\_ONLYでは、Policyが拒否する入力もToolまで到達しました。  
個別PolicyのLOG\_ONLYでは、Toolを止めずに`LogOnlyMatches`と`LogOnlyDecisionFlips`の差を確認してからACTIVEへ変更できました。

今回のPolicy判定は平均22.33msで、production、変更量超過、PolicyのないTool、Prompt Injection後に生成されうる不正なTool引数をAWS Lambda実行前に拒否できました。

ただし、Policy Deny後の再試行停止はAgent側へ実装する必要があります。  
tracingも今回の環境では有効化していないため、PolicyメトリクスとTraceをつないだ調査までは試せていません。

Policyを置いて終わりではなく、Tool Schema、異常系テスト、CloudWatchメトリクスを同じ変更単位で扱うところまで作る必要がありました。
