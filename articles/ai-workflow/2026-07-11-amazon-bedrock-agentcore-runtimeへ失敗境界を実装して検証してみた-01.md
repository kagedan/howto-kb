---
id: "2026-07-11-amazon-bedrock-agentcore-runtimeへ失敗境界を実装して検証してみた-01"
title: "Amazon Bedrock AgentCore Runtimeへ失敗境界を実装して検証してみた"
url: "https://zenn.dev/fusic/articles/e9dcf43552a445"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "zenn"]
date_published: "2026-07-11"
date_collected: "2026-07-12"
summary_by: "auto-rss"
query: ""
---

## はじめに

Fusicの[レオナ](https://x.com/xthixsl_ml)です。

今回は、Amazon Bedrock AgentCore Runtime(以下、AgentCore Runtime)へ障害調査Agentをデプロイし、根拠や現在状態が不足したときに復旧案を返さない境界を検証してみました。

今回は、停止を次の2種類に分けました。

| 種類 | 挙動 | 対象 |
| --- | --- | --- |
| Tool実行の打ち切り | Invocationまたは当該Tool呼び出しを実行前に拒否する | Schema違反、重複呼び出し、回数上限 |
| 復旧案生成の抑止 | 情報収集を続ける場合もあるが、`proposal=null`にする | 分類の低信頼度、Runbookまたは現在状態の欠損 |

分類モデル、RAGの検索インデックス、診断APIは固定応答です。  
本ブログではモデル精度や検索品質ではなく、AgentCore Runtime上で実装した境界が想定どおり機能するかを検証します。

## 作るもの

障害調査Agentは、分類、Runbook検索、メトリクス取得を順番に実行します。

| 処理 | 復旧案を返さない条件 |
| --- | --- |
| 障害分類 | 信頼度0.75未満 |
| Runbook検索 | timeoutで根拠を取得できない |
| メトリクス取得 | timeoutで現在状態を取得できない |

検索結果と現在状態がそろった場合だけ、復旧案を`proposal`へ入れます。  
どちらかが欠けた場合は、`proposal=null`と`stop_reason`を返します。

最終レスポンスは次の形式です。

```
{
  "status": "needs_human_input",
  "stop_reason": "required_evidence_unavailable",
  "tool_call_count": 3,
  "proposal": null
}
```

`stop_reason`は既存のフィールド名を維持し、正常系を含む全ケースの終了理由コードとして使います。

## 実装

今回は、AgentのWorkflowと3つのToolを`main.py`へまとめました。

### Step.1: 入力をSchemaで検証する

入力はPydanticで定義しました。

```
class Invocation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario: Literal[
        "normal",
        "retrieval_timeout",
        "diagnostics_timeout",
        "classification_low_confidence",
        "duplicate_tool_call",
        "max_tool_calls",
    ] = "normal"
    service_name: Literal[
        "billing_api", "auth_api", "inference_api"
    ] = "billing_api"
    environment: Literal["staging", "production"] = "production"
    max_tool_calls: int = Field(default=4, ge=1, le=8)
```

`extra="forbid"`にしているため、`{"shell_command":"..."}`のような未知フィールドはToolを呼ぶ前に拒否されます。

分類、Runbook検索、メトリクス取得は固定応答のToolとして実装しました。  
例えば、Runbook検索は検証シナリオに応じて成功またはtimeoutを返します。

```
def _retrieve(request: Invocation) -> dict[str, Any]:
    if request.scenario == "retrieval_timeout":
        return {
            "status": "failed",
            "error_type": "timeout",
            "retryable": True,
            "partial_data_available": False,
        }

    return {
        "status": "success",
        "document_ids": ["runbook-031"],
        "index_version": "runbook-fixture-v3",
        "document_updated_at": "2026-07-01T00:00:00Z",
        "applies_to": request.environment,
        "implementation": "deterministic_fixture",
    }
```

分類Toolは通常時に`confidence=0.91`、低信頼度シナリオで`confidence=0.54`を返します。  
メトリクス取得Toolは通常時に`alarm_state=ALARM`、診断timeoutシナリオで同じ失敗形式を返します。

`retryable=true`は、呼び出し元が新しいInvocationとして再実行できることを示します。  
同じInvocation内では自動再試行せず、同一Toolと同一引数の再呼び出しをループとして拒否します。

Runbook検索またはメトリクス取得が失敗しても残りの情報収集は続けますが、復旧案は生成しません。

### Step.3: 重複と回数上限を止める

Tool名と`json.dumps(arguments, sort_keys=True, separators=(",", ":"))`で正規化した引数からSHA-256を作り、実行済みの署名なら`duplicate_tool_call`で停止します。  
呼び出し回数が上限へ達した場合は、`tool_call_limit_reached`で停止します。

Trace記録を省いた`ToolLedger.call`の実行前判定は次の処理です。

```
signature = _signature(tool_name, arguments)

if signature in self.signatures:
    return {
        "status": "blocked",
        "error_type": "duplicate_tool_call",
        "retryable": False,
    }

if len(self.signatures) >= self.max_calls:
    return {
        "status": "blocked",
        "error_type": "tool_call_limit_reached",
        "retryable": False,
    }

self.signatures.add(signature)
result = operation()
return result
```

TraceにはTool引数を入れず、`argument_sha256`だけを記録しました。  
候補が少ない引数は総当たりで推測できるため、秘匿が必要な場合はHMACなどを検討します。

実行済み署名と呼び出し回数はInvocationごとに初期化し、同じ`runtimeSessionId`でも別Invocationへ引き継ぎません。  
本稿のTool数は実際に実行したToolの数であり、重複または回数上限によって実行前に拒否した呼び出しを含みません。

### Step.4: Agentの終了状態を決める

Agentは3つのTool呼び出しを試みたあと、収集した結果から終了状態と復旧案を決めます。

```
components = {
    "classification": ledger.call(
        "classify_incident", arguments, lambda: _classify(request)
    ),
    "retrieval": ledger.call(
        "search_runbook", arguments, lambda: _retrieve(request)
    ),
    "diagnostics": ledger.call(
        "get_service_metrics", arguments, lambda: _diagnose(request)
    ),
}

if request.scenario == "duplicate_tool_call":
    components["duplicate_attempt"] = ledger.call(
        "search_runbook", arguments, lambda: _retrieve(request)
    )

status, stop_reason, proposal = _decision(components, ledger.trace)
```

`_decision`は、重複または回数上限、分類の信頼度、Runbook、現在状態の順で判定します。

```
blocked = next(
    (item for item in trace if item["status"] == "blocked"), None
)
if blocked:
    return "needs_human_input", blocked["error_type"], None
if components["classification"]["confidence"] < 0.75:
    return "needs_human_input", "classification_confidence_below_threshold", None
if components["retrieval"]["status"] != "success":
    return "needs_human_input", "required_evidence_unavailable", None
if components["diagnostics"]["status"] != "success":
    return "needs_human_input", "current_state_unknown", None
return (
    "completed",
    "evidence_and_current_state_available",
    "Runbookを確認し、変更は行わず人間の承認へ渡す",
)
```

判定をTool呼び出しのあとに行うため、低信頼度やtimeoutでも3つのToolを実行し、復旧案だけを抑止します。

## Terraformでデプロイする

詳しくは以下のブログをご覧ください。  
<https://zenn.dev/fusic/articles/440692814681b6>

## 検証

### 正常系と境界ケース

AWS SDKの`InvokeAgentRuntime`を使い、各呼び出しにUUIDを`runtimeSessionId`として渡しました。

```
response = client.invoke_agent_runtime(
    agentRuntimeArn=runtime_arn,
    qualifier="DEFAULT",
    runtimeSessionId=str(uuid.uuid4()),
    payload=json.dumps(payload).encode(),
)
```

固定応答は入力の`scenario`で切り替えました。

| シナリオ | 発生方法 |
| --- | --- |
| RAG timeout | `search_runbook`がtimeoutを返す |
| 診断timeout | `get_service_metrics`がtimeoutを返す |
| 分類信頼度0.54 | `classify_incident`が`confidence=0.54`を返す |
| 同一Tool再呼び出し | 同一Invocation内で`search_runbook`を同じ引数でもう一度呼ぶ |
| 最大2回 | Invocationの呼び出し上限を2回にする |
| 未知フィールド | Schemaにない`shell_command`を入力する |

| シナリオ | HTTP | アプリの状態 | 終了理由 | Tool数 | 提案 |
| --- | --- | --- | --- | --- | --- |
| 正常 | 200 | `completed` | `evidence_and_current_state_available` | 3 | あり |
| RAG timeout | 200 | `needs_human_input` | `required_evidence_unavailable` | 3 | なし |
| 診断timeout | 200 | `needs_human_input` | `current_state_unknown` | 3 | なし |
| 分類信頼度0.54 | 200 | `needs_human_input` | `classification_confidence_below_threshold` | 3 | なし |
| 同一Tool再呼び出し | 200 | `needs_human_input` | `duplicate_tool_call` | 3 | なし |
| 最大2回 | 200 | `needs_human_input` | `tool_call_limit_reached` | 2 | なし |
| 未知フィールド | 200 | `failed` | `invalid_request` | 0 | なし |

7ケースすべてが想定した終了状態になりました。境界ケースもHTTP 200なので、5XX率だけでは契約違反や根拠不足を検出できません。アプリケーションの`status`と`stop_reason`も監視対象にします。

### セッション別のレイテンシ

AgentCore Runtimeは、セッションの実行環境が存続している間、同じ`runtimeSessionId`の呼び出しを同じmicroVMへルーティングします。  
東京リージョンのRuntimeをローカルのmacOSからAWS SDKで逐次呼び出し、同じ正常系payloadで同一セッションと毎回新しいセッションをそれぞれ20回測定しました。  
同一セッションでは最初の1回をwarm-upとして除外し、CodeZipのDirect code deploymentではCPUとメモリを指定していません。

| セッション | p50 | p95 | max |
| --- | --- | --- | --- |
| 同一セッション、warm-up後 | 176.5ms | 256.1ms | 284.8ms |
| 毎回新規 | 4,496.0ms | 4,625.5ms | 4,725.6ms |

各条件20回の小規模な測定であり、p95は参考値です。  
固定応答のWorkflowをローカルで実行したp95は0.036msでした。  
ローカルはWorkflowだけ、RuntimeはSDK通信や実行環境の準備も含むため、数値を直接比較できません。  
同一セッションと新規セッションの差が約4.3秒あったことから、今回の条件では新規セッションに伴うRuntime側の準備処理が主な差分である可能性があります。

### Amazon CloudWatch LogsとTrace

AgentCore RuntimeへOpenTelemetryの自動計装を追加し、Amazon CloudWatch Transaction SearchでSpanを確認しました。

`retrieval_timeout`のTraceは次の4 Spanです。

| Span | 状態 | エラー |
| --- | --- | --- |
| `POST /invocations` | `UNSET` | なし |
| `tool.classify_incident` | `UNSET` | なし |
| `tool.search_runbook` | `ERROR` | `timeout` |
| `tool.get_service_metrics` | `UNSET` | なし |

Runbook検索だけがtimeoutになり、Agentが復旧案を返さず`needs_human_input`で終了したことをTraceから確認できました。Span属性にはTool引数本文を入れていません。timeoutはAgentアプリケーションが処理した終了条件であり、HTTPリクエスト自体は成功するため、親Spanは`UNSET`のままです。失敗したTool Spanだけを`ERROR`にし、Agent全体の終了状態はレスポンスとログの`status`、`stop_reason`で確認します。

## 最後に

今回は、AgentCore Runtimeへ障害調査Agentをデプロイし、入力Schema、Tool失敗時の戻り値、重複呼び出し、回数上限を検証しました。  
AgentCore Runtimeへデプロイするだけでは、根拠不足や現在状態の欠損による復旧案の抑止は行われません。Tool実行の打ち切りと復旧案生成の抑止をAgentアプリケーションへ実装し、HTTP Statusとは別に`status`と`stop_reason`を監視する必要があります。
