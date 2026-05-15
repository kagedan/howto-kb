---
id: "2026-05-14-claude-code-agentcore-runtimeステートフルmcpで要件充足チェックを実現-01"
title: "Claude Code × AgentCore Runtime：ステートフルMCPで要件充足チェックを実現する"
url: "https://zenn.dev/aws_japan/articles/2026-04-21-bedrock-agentcore-compliance-skill"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "LLM"]
date_published: "2026-05-14"
date_collected: "2026-05-15"
summary_by: "auto-rss"
query: ""
---

## はじめに

みなさん、仕様書通りにコードが実装されているか、どうやって確認していますか？

要件定義書やデザインドキュメントを書いて、実装して、レビューして。このサイクルの中で「仕様書に書かれた要件がコードで本当に満たされているか」を確認する作業は、多くの場合、人間のレビュアーに委ねられています。しかし、要件が数百、数千と増えていくと、手動レビューでは見落としが避けられません。特に、セキュリティ要件やパフォーマンス要件のように、コードの複数箇所にまたがる非機能要件の充足確認は困難です。

この課題を解決するために、Claude CodeやKiroといったAI Codingツールの**Skill**として、**Amazon Bedrock AgentCore Runtime**上に要件充足チェックのMCPツールを構築しました。AgentCore Runtimeは、MCPサーバーをマネージドにホストし、セッション隔離やスケーリングを提供する実行環境です。

### なぜMCPツールをサーバーサイドに構築するのか？

MCPツールはローカル環境にも構築できます。しかし、コンプライアンスチェックのようなガバナンス機能をローカルに置くと、以下の問題が生じます。

* **チーム間のばらつき**: 個人のローカル環境にルールや要件定義を置くと、メンバーごとにチェック基準が異なる状態になりやすい
* **ルールの陳腐化**: 組織の規約が更新されても、各ローカル環境への反映が徹底されない
* **監査の困難**: 誰がどの基準でチェックしたかの証跡が残らない

**AgentCore Runtimeでサーバーサイドに一元管理する**ことで、組織全体で統一されたコンプライアンスチェックが可能になります。要件定義の更新はサーバー側で一度行えば、全てのAI Codingツールから最新の基準で検証が実行されます。これはガバナンスの観点で極めて重要です。

本記事では、要件ドキュメントをAmazon Bedrock Knowledge Base（S3 Vectors）に格納し、MCPツール経由でコードとの突合チェックを行う仕組みの実装とデプロイを紹介します。

## アーキテクチャ

### 全体構成

### 使用サービス・技術一覧

| サービス / 技術 | 用途 |
| --- | --- |
| Amazon Bedrock AgentCore Runtime | MCP Serverのマネージド実行環境（セッション隔離） |
| Amazon Bedrock Knowledge Base | S3 Vectorsによる要件ドキュメントの検索基盤 |
| Amazon Bedrock (Claude) | コードと要件の突合評価（推論） |
| Amazon S3 | 要件ドキュメントの格納 |
| Terraform | S3、IAM、Knowledge Baseなど標準AWSリソースのIaC |
| AgentCore CLI | Runtime / Gatewayのデプロイ（CDK） |
| Python / stdlib http.server | MCP Serverの実装 |

## 実装

### 設計方針: ステートフルなMCPセッション

ユーザーがAI Codingツールに「このコードが要件を満たしているかチェックして」と依頼すると、Agentは以下のステップを自律的に実行します。

1. **要件の取得** — チェック対象の要件をKnowledge Baseから取得する
2. **コードの蓄積** — チェック対象のソースコードをセッションに追加する（複数回可）
3. **充足判定** — 蓄積されたコードが要件を満たしているかをLLMで判定する

ステップ2で蓄積したコードコンテキストは、MCPサーバー側のセッション内で保持され、ステップ3の判定で参照されます。Agent自体は状態を持たず、ツール側のセッションがステートフルに動作します。

MCPサーバーをステートフルにした理由：

* **チェック対象のファイルが事前に確定しない** — Agentが対話の中で必要なファイルを判断し、段階的に追加する
* **要件とコードの組み合わせが動的** — バリエーション指定で、チェック範囲を柔軟に変えられる
* **1回のLLM呼び出しでは処理しきれない** — 大量の要件 × 複数ファイルを一度に渡すとコンテキスト長を超える

AgentCore Runtimeはセッション単位でmicroVMを隔離するため、インメモリの状態管理で十分です。`Mcp-Session-Id` ヘッダーにより、同一セッションのリクエストは同じmicroVMにルーティングされます。このステートフルなセッション設計が、後述する「Runtime直接接続」を選択した技術的な理由でもあります。

### MCPツール設計

本システムでは、3つのMCPツールをパイプラインとして設計しています。

| ツール名 | 役割 | 入力 | 出力 |
| --- | --- | --- | --- |
| `list_requirements` | 要件一覧の取得 | `variant`（デフォルト: `"basic"`） | 要件ID・タイトルのリスト |
| `add_code_context` | チェック対象コードの追加 | `file_path`, `source_code`, `language` | 追加結果（ファイル数等） |
| `check_compliance` | 要件充足チェックの実行 | `variant`, `requirement_ids`（任意） | 要件ごとのpass/fail + 説明 |

この3ツールは `list_requirements` → `add_code_context` → `check_compliance` の順に呼び出すことを想定しています。`add_code_context` で蓄積されたコードコンテキストに対し、`check_compliance` が要件の取得と突合評価をまとめて実行します。

#### list\_requirements

Knowledge Baseから要件を検索し、セッションに格納します。`variant` パラメータを指定することで、セキュリティ要件のみ、パフォーマンス要件のみといったフィルタリングが可能です。

```
def tool_list_requirements(variant: str = "basic") -> list[dict]:
    """Knowledge Base からバリエーション指定で要件一覧を取得"""
    kb_id = os.getenv("KNOWLEDGE_BASE_ID")
    if not kb_id:
        return [{"error": "KNOWLEDGE_BASE_ID not configured"}]

    client = _get_bedrock_agent_client()
    response = client.retrieve(
        knowledgeBaseId=kb_id,
        retrievalQuery={"text": f"variant:{variant} 要件一覧"},
        retrievalConfiguration={
            "vectorSearchConfiguration": {
                "numberOfResults": 20,
                "filter": {
                    "equals": {"key": "variant", "value": variant}
                }
            }
        }
    )

    results = []
    for item in response.get("retrievalResults", []):
        metadata = item.get("metadata", {})
        results.append({
            "id": metadata.get("requirement_id", ""),
            "title": metadata.get("title", ""),
            "variant": metadata.get("variant", variant)
        })
    return results
```

#### add\_code\_context

チェック対象のソースコードをセッションに追加します。複数回呼び出すことで、複数ファイルのコードを蓄積できます。

```
def tool_add_code_context(file_path: str, source_code: str, language: str = "python") -> dict:
    """セッションにソースコードを蓄積"""
    _code_contexts.append({
        "file_path": file_path,
        "source_code": source_code,
        "language": language
    })
    return {
        "success": True,
        "file_path": file_path,
        "total_files": len(_code_contexts)
    }
```

#### check\_compliance

セッションに蓄積された要件とコードを突合し、要件ごとにpass/failを判定します。Amazon Bedrockの推論を使って評価を行います。

```
def tool_check_compliance(variant: str = "basic", requirement_ids: list[str] | None = None) -> dict:
    """蓄積されたコードに対して要件充足をチェック"""
    if not _code_contexts:
        return {"error": "No code context. Call add_code_context first."}

    requirements = tool_list_requirements(variant)
    if requirement_ids:
        requirements = [r for r in requirements if r.get("id") in requirement_ids]

    code_text = "\n".join([
        f"--- {ctx['file_path']} ({ctx['language']}) ---\n{ctx['source_code']}"
        for ctx in _code_contexts
    ])

    client = _get_bedrock_runtime_client()
    details = []
    pass_count = 0

    for req in requirements:
        prompt = f"""要件に対してコードが充足しているか判定してください。

要件:
- ID: {req.get('id', '')}
- タイトル: {req.get('title', '')}

コード:
{code_text}

JSON形式で回答: {{"status": "PASS" or "FAIL", "evidence": "根拠", "suggestion": "提案"}}"""

        response = client.invoke_model(
            modelId="jp.anthropic.claude-haiku-4-5-20251001-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}]
            })
        )
        result = json.loads(response["body"].read())
        # ... 結果を解析してdetailsに追加 ...

    return {
        "passed": pass_count == len(requirements),
        "variant": variant,
        "summary": f"{pass_count}/{len(requirements)} requirements satisfied",
        "details": details
    }
```

**なぜClaude Haiku 4.5を選択したか**: `check_compliance` は要件ごとにループで1回ずつLLMを呼び出す設計のため、要件数 × ファイル数に比例してコストが増加します。各呼び出しのタスクは「1要件に対するPASS/FAIL判定」という単純な二値分類であり、Haiku 4.5で十分な精度が得られます。Sonnetと比較して約1/3のコストで済むうえ、レイテンシも短いため、pre-commit hookやCI/CDでの利用にも適しています。

### Stateful MCP Serverの実装ポイント

標準的なMCPサーバーはステートレスですが、本システムでは `add_code_context` で蓄積したコードを `check_compliance` で参照するため、セッション内で状態を保持する設計にしています。

```
from http.server import HTTPServer, BaseHTTPRequestHandler

# セッション内のコードコンテキスト
_code_contexts: list[dict] = []
```

AgentCore Runtimeの初期化タイムアウト（30秒）を回避するため、FastMCPではなくPython標準ライブラリの `http.server` を使用しています。FastMCP + Starlette + uvicorn の依存解決に時間がかかり、初期化が間に合わないためです。

設計上のポイントは以下の通りです。

* **セッションスコープ**: AgentCore Runtimeはセッション単位でmicroVMを隔離するため、モジュールレベルの変数でも安全に状態を保持できる
* **シンプルな状態管理**: `check_compliance` が内部で `list_requirements` を呼び出すため、状態管理はコードコンテキストの蓄積のみに絞っている
* **エラーハンドリング**: コードコンテキストが空の場合は明確なエラーメッセージを返す

### S3 Vectorsメタデータ設計

要件ドキュメントはS3に格納し、Bedrock Knowledge BaseのS3 Vectorsで検索可能にします。各ドキュメントにはメタデータを付与し、バリエーション別のフィルタリングを実現します。

```
{
  "key": "req-001-basic",
  "data": [0.123, 0.456, "..."],
  "metadata": {
    "requirement_id": "REQ-001",
    "variant": "basic",
    "title": "ユーザーはメールアドレスでログインできること",
    "source_document": "requirements-v1.md"
  }
}
```

メタデータの設計方針は以下の通りです。

| フィールド | 型 | 用途 | 例 |
| --- | --- | --- | --- |
| `requirement_id` | STRING | 要件の一意識別子 | `"REQ-001"`, `"SEC-001"` |
| `variant` | STRING | 要件バリエーションによるフィルタリング | `"basic"`, `"advanced"` |
| `title` | STRING | 要件の概要タイトル | `"ユーザーはメールアドレスでログインできること"` |
| `source_document` | STRING | 元の要件ドキュメント名 | `"requirements-v1.md"` |

S3バケット内のディレクトリ構成例は以下の通りです。

```
s3://<BUCKET_NAME>/requirements/
├── security/
│   ├── SEC-001.md
│   ├── SEC-001.md.metadata.json
│   ├── SEC-002.md
│   └── SEC-002.md.metadata.json
├── performance/
│   ├── PERF-001.md
│   └── PERF-001.md.metadata.json
└── functional/
    ├── FUNC-001.md
    └── FUNC-001.md.metadata.json
```

## パイプライン化

### pre-commit hookによる自動チェック

Git の pre-commit hook を使って、コミット時に自動で要件充足チェックを実行できます。Runtime への接続には SigV4 署名が必要なため、Python の `boto3` + `botocore` を使用しています。

```
#!/usr/bin/env bash
# .git/hooks/pre-commit

set -uo pipefail

RUNTIME_ARN="${COMPLIANCE_RUNTIME_ARN:-}"

if [ -z "$RUNTIME_ARN" ]; then
    echo "[pre-commit] COMPLIANCE_RUNTIME_ARN が未設定のためスキップします"
    exit 0
fi

CHANGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(c|cpp|h|dart|py|ts|java)$' || true)

if [ -z "$CHANGED_FILES" ]; then
    exit 0
fi

echo "[pre-commit] コード要件充足チェックを実行中..."

# SigV4署名付きでRuntimeに直接リクエストを送るPythonスクリプト
python3 -c "
import json, ssl, http.client, os, sys
from urllib.parse import quote
import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

runtime_arn = os.environ['COMPLIANCE_RUNTIME_ARN']
region = os.environ.get('AWS_REGION', 'ap-northeast-1')
encoded_arn = quote(runtime_arn, safe='')
host = f'bedrock-agentcore.{region}.amazonaws.com'
path = f'/runtimes/{encoded_arn}/invocations'
endpoint = f'https://{host}{path}'

session = boto3.Session(region_name=region)
credentials = session.get_credentials().get_frozen_credentials()
service = 'bedrock-agentcore'
session_id = None

def mcp_call(body_dict):
    global session_id
    body = json.dumps(body_dict)
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream'}
    if session_id:
        headers['Mcp-Session-Id'] = session_id
    req = AWSRequest(method='POST', url=endpoint, data=body, headers=headers)
    SigV4Auth(credentials, service, region).add_auth(req)
    ctx = ssl.create_default_context()
    conn = http.client.HTTPSConnection(host, context=ctx, timeout=300)
    conn.request('POST', path, body=body.encode(), headers=dict(req.headers))
    resp = conn.getresponse()
    resp_headers = {k.lower(): v for k, v in resp.getheaders()}
    new_sid = resp_headers.get('mcp-session-id')
    if new_sid:
        session_id = new_sid
    data = resp.read().decode()
    conn.close()
    return json.loads(data)

# 変更ファイルを蓄積
files = '''${CHANGED_FILES}'''.strip().split('\n')
for f in files:
    if not f:
        continue
    ext = f.rsplit('.', 1)[-1]
    lang_map = {'c': 'c', 'h': 'c', 'cpp': 'cpp', 'py': 'python', 'ts': 'typescript', 'java': 'java', 'dart': 'dart'}
    lang = lang_map.get(ext, ext)
    try:
        content = open(f).read()
    except:
        continue
    mcp_call({'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call', 'params': {'name': 'add_code_context', 'arguments': {'file_path': f, 'source_code': content, 'language': lang}}})

# チェック実行
result = mcp_call({'jsonrpc': '2.0', 'id': 2, 'method': 'tools/call', 'params': {'name': 'check_compliance', 'arguments': {'variant': os.environ.get('COMPLIANCE_VARIANT', 'basic')}}})
text = result.get('result', {}).get('content', [{}])[0].get('text', '{}')
report = json.loads(text)
if not report.get('passed', True):
    print('Warning: ' + report.get('summary', ''))
    sys.exit(0)  # 警告のみ、コミットはブロックしない
"

exit 0
```

### GitHub Actionsによるパイプライン統合

pre-commit hookはローカル環境に依存するため、チーム全体での強制力がありません。GitHub Actionsを使えば、Push/PRをトリガーにサーバーサイドで自動チェックを実行できます。

```
# .github/workflows/compliance-check.yml
name: Compliance Check
on:
  push:
    branches: [main]
  pull_request:

jobs:
  check:
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # OIDC認証用
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-actions-compliance
          aws-region: ap-northeast-1

      - name: Run compliance check
        env:
          MCP_ENDPOINT: ${{ secrets.MCP_ENDPOINT }}
        run: |
          # 変更ファイルを蓄積
          for file in $(git diff --name-only HEAD~1 -- '*.c' '*.cpp' '*.h' '*.dart' '*.py' '*.ts' '*.java'); do
            curl -s -X POST "$MCP_ENDPOINT" \
              -H "Content-Type: application/json" \
              -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/call\",\"params\":{\"name\":\"add_code_context\",\"arguments\":{\"file_path\":\"$file\",\"source_code\":$(cat "$file" | jq -Rs .),\"language\":\"python\"}}}"
          done

          # チェック実行
          RESULT=$(curl -s -X POST "$MCP_ENDPOINT" \
            -H "Content-Type: application/json" \
            -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"check_compliance","arguments":{"variant":"basic"}}}')

          echo "$RESULT" | jq .
```

GitHub ActionsではOIDC連携によるIAM認証を使用するため、シークレットにトークンを保存する必要がありません。これにより、ローカル（pre-commit hook、警告のみ）とCI/CD（GitHub Actions、必須チェック）の二段構えでガバナンスを実現できます。

上記の例では、直前のコミットとのdiff（変更されたソースファイル）を1ファイルずつ `add_code_context` で蓄積し、最後に `check_compliance` で一括チェックしています。AI Agentが自律的に判断するのではなく、スクリプトが機械的に変更ファイルを渡す方式のため、チェック漏れが発生しません。

## デプロイ手順

### 前提条件

* AWSアカウント
* Terraform >= 1.5
* AWS CLI v2
* Python >= 3.13
* Amazon Bedrock のモデルアクセスが有効化済み（Claude Haiku 4.5以上）

### AgentCore CLIによるデプロイ

AgentCoreリソース（Runtime、Gateway）のデプロイには `agentcore` CLI を使用します。CLIは内部でCDK（AWS Cloud Development Kit）を使用しており、`agentcore deploy` コマンド一つでRuntime + Gatewayが構築されます。

```
# AgentCore CLIのインストール
npm i -g @aws/agentcore

# エントリポイントとIAMロールを設定
agentcore configure --entrypoint src/mcp_server.py -er <IAM_ROLE_ARN>

# デプロイ（Runtime + Gateway を一括作成）
agentcore deploy
```

S3バケットやIAMロールなどの基盤リソースはTerraformで管理し、AgentCore固有リソースは `agentcore` CLI で管理するハイブリッド構成です。

```
terraform/
├── main.tf          # プロバイダー設定
├── backend.tf       # S3バックエンド
├── variables.tf     # 変数定義
├── iam.tf           # IAMロール・ポリシー
├── s3.tf            # 要件ドキュメント用S3バケット
├── cognito.tf       # 認証設定
└── outputs.tf       # 出力値

agentcore/
├── agentcore.json   # AgentCore CLI設定（Runtime + Gateway定義）
└── cdk/             # CDKスタック（CLIが自動生成・管理）
```

### Terraformによる基盤リソースのデプロイ

```
# s3.tf - 要件ドキュメント格納用バケット
resource "aws_s3_bucket" "requirements" {
  bucket = "compliance-requirements-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_bucket_versioning" "requirements" {
  bucket = aws_s3_bucket.requirements.id
  versioning_configuration {
    status = "Enabled"
  }
}
```

```
# knowledge_base.tf - Bedrock Knowledge Base（S3 Vectors）
resource "aws_bedrockagent_knowledge_base" "compliance" {
  name     = "compliance-requirements"
  role_arn = aws_iam_role.knowledge_base.arn

  knowledge_base_configuration {
    type = "VECTOR"
    vector_knowledge_base_configuration {
      embedding_model_arn = "arn:aws:bedrock:<YOUR_REGION>::foundation-model/amazon.titan-embed-text-v2:0"
    }
  }

  storage_configuration {
    type = "S3_VECTORS"
    s3_vectors_configuration {
      bucket_arn = "arn:aws:s3vectors:<YOUR_REGION>:<ACCOUNT_ID>:vector-bucket/<VECTOR_BUCKET>"
      index_name = "requirements"
    }
  }
}

resource "aws_bedrockagent_data_source" "requirements" {
  name              = "requirements-docs"
  knowledge_base_id = aws_bedrockagent_knowledge_base.compliance.id

  data_source_configuration {
    type = "S3"
    s3_configuration {
      bucket_arn = aws_s3_bucket.requirements.arn
    }
  }
}
```

Terraform適用後、`agentcore deploy` でRuntimeをデプロイします。

### AgentCoreリソースのデプロイ

Terraform適用後、`agentcore deploy` でRuntimeをデプロイします。`agentcore.json` に定義されたRuntime設定に基づき、CDKが裏で動いてインフラを構築します。

```
#!/usr/bin/env bash
# scripts/deploy-agentcore.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

export AWS_REGION="${AWS_REGION:-ap-northeast-1}"
export AWS_DEFAULT_REGION="${AWS_REGION}"

echo "==> agentcore deploy 実行中..."
agentcore deploy --yes --verbose --target default

echo "==> デプロイ完了"
```

`agentcore.json` の設定例:

```
{
  "$schema": "https://schema.agentcore.aws.dev/v1/agentcore.json",
  "name": "codecompliance",
  "version": 1,
  "managedBy": "CDK",
  "runtimes": [
    {
      "name": "codecompliance",
      "build": "CodeZip",
      "entrypoint": "mcp_server.py",
      "codeLocation": "src/",
      "runtimeVersion": "PYTHON_3_13",
      "networkMode": "PUBLIC",
      "protocol": "MCP",
      "executionRoleArn": "arn:aws:iam::<ACCOUNT_ID>:role/<ROLE_NAME>",
      "envVars": [
        {"name": "KNOWLEDGE_BASE_ID", "value": "<KB_ID>"}
      ]
    }
  ]
}
```

## Claude Code への登録

### MCPサーバーの登録

Claude Code から AgentCore Runtime 上の MCP サーバーに接続するには、AWS公式の [mcp-proxy-for-aws](https://pypi.org/project/mcp-proxy-for-aws/) を使用します。このプロキシは SigV4 署名と `Mcp-Session-Id` によるステートフルセッション管理を自動で行います。

```
claude mcp add compliance -- \
  uvx mcp-proxy-for-aws@latest \
  "https://bedrock-agentcore.ap-northeast-1.amazonaws.com/runtimes/<URL_ENCODED_RUNTIME_ARN>/invocations" \
  --region ap-northeast-1
```

これで `compliance` という名前の MCP サーバーが登録され、`add_code_context`、`check_compliance` 等のツールが Claude Code から利用可能になります。

`mcp-proxy-for-aws` は内部で MCP SDK の `streamable_http_client` を使用しており、以下を自動的に処理します:

* **SigV4署名**: AWS CLI の認証情報（`~/.aws/credentials`、SSO、IAMロール）を使って自動署名
* **セッション管理**: `Mcp-Session-Id` ヘッダーの保持と送信。同一セッション内のリクエストが同じ microVM にルーティングされる
* **プロトコル変換**: Claude Code の stdio と AgentCore Runtime の Streamable HTTP を橋渡し

### Skillの登録

MCPサーバーの登録だけでは、Claude Code はツールの**使い方**（どの順番で呼ぶか、どんなプロンプトで呼び出すか）を知りません。Skill を定義することで、ユーザーが「コンプライアンスチェックして」と言うだけで、Claude が適切な手順でツールを呼び出せるようになります。

プロジェクトルートに `.claude/skills/code-compliance/SKILL.md` を配置します。

```
# Code Compliance Skill

コードが仕様書・コーディング規約等に準拠しているかを検証するスキルです。

## 利用可能なツール

### list_requirements
Knowledge Base からバリエーション指定で要件ID一覧を取得します。

**パラメータ:**
- `variant` (必須): バリエーション名（例: "basic", "advanced"）

### add_code_context
セッションにソースコードを蓄積します。複数回呼び出し可能です。

**パラメータ:**
- `file_path` (必須): ファイルパス
- `source_code` (必須): ソースコード
- `language` (必須): プログラミング言語

### check_compliance
蓄積されたコードに対して要件充足をチェックします。

**パラメータ:**
- `variant` (必須): バリエーション名（メタデータフィルタ用）
- `requirement_ids` (任意): 対象要件IDリスト（省略時は全件チェック）

## 使い方

1. `list_requirements` で対象バリエーションの要件一覧を確認
2. `add_code_context` でチェック対象のソースコードを蓄積（複数ファイル可）
3. `check_compliance` で要件充足チェックを実行

## 使用例

\```
要件書のbasicバリエーションに対して、src/auth.pyの要件充足をチェックしてください。
\```
```

この SKILL.md を配置することで、Claude Code で `/code-compliance` としてスキルが呼び出せるようになります。ユーザーは自然言語で指示するだけで、Claude がツールの呼び出し順序を自動的に判断します。

## 動作確認

### Claude Codeでの対話例

Claude Codeでの対話例は以下の通りです。

```
You: セキュリティ要件に対してauth.pyのコンプライアンスチェックをしてください

Claude: セキュリティ要件を取得し、auth.pyのコンプライアンスチェックを実行します。

1. まず、セキュリティ要件を確認します。
   [list_requirements(variant="security")]
   → 5件の要件が見つかりました。

2. auth.pyのコードを追加します。
   [add_code_context(file_path="src/auth.py", source_code="...", language="python")]
   → コードコンテキストを追加しました（1ファイル蓄積済み）。

3. コンプライアンスチェックを実行します。
   [check_compliance(variant="security")]

結果:
  ✅ SEC-001: パスワードハッシュ化 - bcryptによるハッシュ化を確認
  ✅ SEC-002: 入力バリデーション - Pydanticスキーマによる検証を確認
  ❌ SEC-003: レート制限 - APIエンドポイントにレート制限が未実装
  ✅ SEC-004: SQLインジェクション対策 - パラメータ化クエリを確認
  ✅ SEC-005: 認証トークン有効期限 - JWT有効期限30分を確認

5件中4件が合格、1件が不合格です。SEC-003のレート制限の実装を推奨します。
```

### Kiroからの利用

Kiroではカスタムエージェント定義（`.kiro/agents/`）にMCPサーバー設定を直接記述します。`tools` / `allowedTools` に `@compliance` を指定することで、エージェントがMCPツールにアクセスできるようになります。

```
// .kiro/agents/code-compliance.json
{
  "name": "Code Compliance",
  "description": "コードが仕様書・コーディング規約等に準拠しているかを検証するエージェント",
  "prompt": "コードの要件充足チェックを行います。まず対象ファイルを読み込み、list_requirements でバリエーションの要件一覧を取得し、add_code_context でソースコードを蓄積してから、check_compliance で充足判定を実行してください。",
  "tools": [
    "fs_read",
    "glob",
    "grep",
    "@compliance"
  ],
  "allowedTools": [
    "fs_read",
    "glob",
    "grep",
    "@compliance"
  ],
  "mcpServers": {
    "compliance": {
      "command": "uvx",
      "args": [
        "mcp-proxy-for-aws@latest",
        "https://bedrock-agentcore.ap-northeast-1.amazonaws.com/runtimes/<URL_ENCODED_RUNTIME_ARN>/invocations",
        "--region", "ap-northeast-1"
      ]
    }
  }
}
```

ポイント:

* **`mcpServers`**: エージェント定義内に接続先を直接記述する。グローバルのMCP設定とは別にエージェント単位で管理できる
* **`tools` / `allowedTools`**: `@compliance` でMCPサーバー名を参照し、そのサーバーが提供する全ツールへのアクセスを許可する
* **`prompt`**: エージェントへの指示。ツールの呼び出し順序を明記することで、正しいパイプラインが実行される

### バリエーション指定での要件チェック

`list_requirements` の `variant` パラメータを使って、特定カテゴリの要件のみをチェックできます。

```
You: パフォーマンス要件だけチェックしてください

Claude: パフォーマンス要件に絞ってチェックを実行します。

1. パフォーマンス要件を取得します。
   [list_requirements(variant="performance")]
   → 3件の要件が見つかりました。
   - PERF-001: API応答時間 200ms以内
   - PERF-002: データベースクエリ 50ms以内
   - PERF-003: メモリ使用量 512MB以内

2. 対象コードを追加します。
   [add_code_context(file_path="src/api/handler.py", source_code="...", language="python")]
   [add_code_context(file_path="src/db/queries.py", source_code="...", language="python")]

3. チェック実行
   [check_compliance(variant="performance")]

結果:
  ✅ PERF-001: N+1クエリなし、キャッシュ実装済み
  ❌ PERF-002: 結合クエリにインデックスが不足している可能性
  ✅ PERF-003: ストリーミング処理によりメモリ効率良好
```

### セマンティックサーチによる要件の絞り込み

バリエーション指定はカテゴリ単位の粗い絞り込みですが、Knowledge BaseのS3 Vectorsを活用すれば、要件の**内容**に基づいた意味的な絞り込みが可能です。

例えば、特定のドメインにおける車載ソフトウェアの安全要件が数万件ある中で「ブレーキ制御に関連する要件だけチェックしたい」というケースを考えます。

```
You: ブレーキ制御に関連する安全要件に対して、brake_controller.c をチェックしてください

Claude: ブレーキ制御に関連する要件をセマンティックサーチで取得します。

1. 要件を検索します。
   [list_requirements(query="ブレーキ制御 緊急停止 フェイルセーフ")]
   → 意味的に関連する4件が見つかりました。
   - SAFETY-012: ブレーキ信号は10ms以内に処理されること
   - SAFETY-015: センサー異常時はフェイルセーフモードに移行すること
   - SAFETY-023: 緊急停止要求は他の制御より優先されること
   - SAFETY-031: ブレーキ圧力の計算値は冗長系で検証されること

2. 対象コードを追加します。
   [add_code_context(file_path="src/brake_controller.c", source_code="...", language="c")]

3. チェック実行
   [check_compliance(requirement_ids=["SAFETY-012", "SAFETY-015", "SAFETY-023", "SAFETY-031"])]

結果:
  ✅ SAFETY-012: brake_process()のWCET解析で10ms以内を確認
  ✅ SAFETY-015: sensor_fault_handler()でフェイルセーフ移行を実装
  ❌ SAFETY-023: 優先度制御が未実装。RTOSのタスク優先度設定を推奨
  ✅ SAFETY-031: calc_brake_pressure()で二重計算・比較を実装
```

このように、要件をベクトル化してS3 Vectorsで管理することで、「ブレーキ」という単語が含まれない要件（例: SAFETY-015のフェイルセーフ）も意味的に関連するものとして検索できます。数万件の要件から人手で関連要件を選ぶのは現実的ではありませんが、セマンティックサーチであれば瞬時に絞り込めます。

さらに、メタデータフィルタとセマンティックサーチを組み合わせることも可能です。例えば車載ソフトウェアであれば、variantに車種や仕向けを設定（`variant="bev-xxx-jp"`）し、その中から「ブレーキ制御」で自然言語検索すれば、特定バリエーションかつブレーキに関連する要件だけを効率的に抽出できます。カテゴリによる粗い絞り込みと、自然言語による意味的な絞り込みを併用することで、大量の要件の中から必要なものを正確に特定できます。

## クリーンアップ

デプロイしたリソースを削除する場合は、AgentCore固有リソースを先に削除してからTerraformで基盤リソースを削除します。

```
#!/usr/bin/env bash
# scripts/teardown.sh

set -euo pipefail

TERRAFORM_DIR="./terraform"
AWS_REGION=$(terraform -chdir="$TERRAFORM_DIR" output -raw region)

echo "==> CLI作成リソースを削除..."
if [[ -f "${TERRAFORM_DIR}/cli-outputs.json" ]]; then
    RUNTIME_ID=$(jq -r '.agentcore_runtime_id' "${TERRAFORM_DIR}/cli-outputs.json")

    if [[ -n "$RUNTIME_ID" && "$RUNTIME_ID" != "null" ]]; then
        aws bedrock-agentcore-control delete-agent-runtime \
            --agent-runtime-id "${RUNTIME_ID}" \
            --region "${AWS_REGION}"
        echo "    Deleted Runtime: ${RUNTIME_ID}"
    fi

    rm "${TERRAFORM_DIR}/cli-outputs.json"
fi

echo "==> Terraformリソースを削除..."
cd "$TERRAFORM_DIR"
terraform destroy -auto-approve

echo "==> クリーンアップ完了"
```

## Claude Codeからの接続

### 接続構成: Runtime直接接続 + mcp-proxy-for-aws

Claude CodeからAgentCore上のMCPサーバーに接続するには、AWS公式の **mcp-proxy-for-aws** を使用します。これはstdioプロキシで、SigV4署名の付与と `Mcp-Session-Id` によるステートフルセッション管理を自動的に行います。

```
claude mcp add compliance -- \
  uvx mcp-proxy-for-aws@latest \
  "https://bedrock-agentcore.ap-northeast-1.amazonaws.com/runtimes/<URL_ENCODED_RUNTIME_ARN>/invocations" \
  --region ap-northeast-1
```

この構成では、AWS CLIの認証情報（`~/.aws/credentials`、SSO、IAMロール）がそのまま使われます。トークンの手動管理は不要です。

### なぜGateway経由ではなくRuntime直接接続なのか

AgentCore Gatewayを経由する構成も可能ですが、2026年5月時点では以下の制約があります。

**セッション維持の問題**: 本システムの `add_code_context` → `check_compliance` パイプラインはセッション内でコードコンテキストを蓄積するステートフルな設計です。MCP Streamable HTTPでは `Mcp-Session-Id` ヘッダーによって同一セッションのリクエストが同じmicroVMにルーティングされますが、Gateway経由ではこのヘッダーが正しく中継されないケースがあり、リクエストごとに別のmicroVMにルーティングされてコンテキストが失われます。

> AgentCore Runtime routes requests based on the `mcp-session-id` header value. Different session ids will be served by different containers to ensure session isolation. The same session id will be served by the same container for the lifetime of the container.  
> — [AWS re:Post](https://repost.aws/questions/QU-YbedQP2Qj6QwqR5EnuELQ)

**Runtime直接接続であれば**、AgentCore Runtime が `Mcp-Session-Id` を直接管理し、同一セッション内のリクエストは確実に同じmicroVMで処理されます。

```
# Gateway経由（ステートフルMCPで問題あり）
Claude Code → mcp-proxy-for-aws → AgentCore Gateway → Runtime
                                   ↑ Mcp-Session-Idの中継に問題

# Runtime直接接続（推奨）
Claude Code → mcp-proxy-for-aws → AgentCore Runtime
                                   ↑ Mcp-Session-Idを直接管理
```

### なぜstdioプロキシが必要なのか

Claude CodeはMCP仕様に準拠したOAuth認証（RFC 9728）をサポートしていますが、AgentCore RuntimeのInbound認証はIAM（SigV4）です。Claude Code自体はSigV4署名を行えないため、stdioプロキシがSigV4署名を代行します。

なお、AgentCore GatewayはInbound側でのMCP OAuth（RFC 9728）に2026年5月時点で未対応のため、Gateway経由でもOAuthフローは使えません。将来的にGatewayがRFC 9728に対応すれば、プロキシなしでClaude Codeから直接接続できるようになる可能性があります。

## 制限事項・注意点

* **コールドスタート**: microVM の初回起動には数秒かかります。MCP サーバー接続時（`initialize` / `tools/list`）に Runtime への通信が発生するため、初回接続時にコールドスタートの待ちが生じます。`warmup` ツールを用意しておき、接続後に一度呼び出すことで以降のレイテンシを緩和できます。
* **セッションのライフタイム**: AgentCore Runtime のセッションはアイドルタイムアウト（デフォルト15分）で終了します。タイムアウト後は新しいmicroVMが割り当てられ、蓄積したコードコンテキストは失われます。
* **Gateway非対応**: 2026年5月時点で、AgentCore Gateway 経由ではステートフルMCPセッションが正常に動作しません。Runtime 直接接続が必要です。

## まとめ

### 学び・気づき

**AgentCore CLIによるデプロイ**

AgentCoreのRuntime、Gatewayは `agentcore` CLI でデプロイします。CLIは内部でCDKを使用しており、`agentcore deploy` 一つでインフラが構築されます。S3やIAMなどの基盤リソースはTerraformで管理し、AgentCore固有リソースはCLIに任せるハイブリッド構成が現実的です。

**Stateful MCP Serverの設計**

MCPサーバーは基本的にステートレスに設計するのがベストプラクティスですが、今回のようにツール間でパイプラインを構成する場合は、セッションスコープでの状態保持が有効です。AgentCore Runtimeがセッション管理を担ってくれるため、実装側はシンプルなインメモリ状態管理で十分でした。

## おわりに

コードの品質を組織的に保つためには、要件に対するトレーサビリティの担保とガバナンスの強制力が求められます。要件充足チェックをMCPツールとしてサーバーサイドに集約することで、統一された基準での検証が可能になり、CI/CDやpre-commit hookと組み合わせることでガバナンスを開発フローに組み込めます。また、判定タスクを1要件単位に分割する設計により、Claude Haiku 4.5のような比較的安価なモデルで十分な精度を維持しつつ、1回あたりのトークン消費も抑えられます。コンプライアンスチェックの品質とコスト効率の両立を検討されている方は、ぜひこのアーキテクチャを参考にしてみてください。

## 参考
