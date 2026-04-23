---
id: "2026-04-07-mcpで自社apiをclaude-codeに統合する実装から運用までの完全ガイド-01"
title: "MCPで自社APIをClaude Codeに統合する、実装から運用までの完全ガイド"
url: "https://qiita.com/moha0918_/items/ef84ca42e1595337f675"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "qiita"]
date_published: "2026-04-07"
date_collected: "2026-04-08"
summary_by: "auto-rss"
---

Claude Codeと外部ツールを連携させたい、と思って調べ始めると、「MCP」という言葉にすぐ行き着きます。でも「サーバーを立てる？OAuthの設定？スコープの管理？」と、やることが多すぎて途中で止まった経験がある方も多いのではないでしょうか。

この記事では、自社のAPIをMCPサーバーとしてClaude Codeに統合するところから、チームで運用するための設定管理まで、実際のプロジェクトを想定しながら解説します。

## まずMCPで何ができるかを整理する

MCPを使うと、Claude Codeが外部のツールやAPIを直接操作できるようになります。

具体的に言うと、こういう指示が通るようになります。

* 「JIRAのENG-4521のチケットを読んで、実装してPRを作って」
* 「Sentryで過去24時間のエラーを調べて、原因を特定して」
* 「本番DBで先月購入がなかったユーザーを10件抽出して」

Claudeが自然言語の指示を受けて、裏側でAPIを叩き、結果を使いながら作業を進める、という流れです。

MCPには3種類の接続方式があります。

| 方式 | 用途 | 具体例 |
| --- | --- | --- |
| HTTP | クラウドサービスへの接続（推奨） | Notion、GitHub、Sentry |
| SSE | 旧方式（非推奨） | 一部の古いサービス |
| stdio | ローカルプロセスとの接続 | DB接続、カスタムスクリプト |

自社APIの統合では、**HTTPかstdioのどちらか**を選ぶことになります。外部公開のAPIならHTTP、ローカルの開発環境や社内ネットワークのみならstdioが向いています。

## 実践シナリオ：社内REST APIをMCPで繋ぐ

ここからは「従業員情報APIをClaude Codeから使えるようにする」という具体的なシナリオで進めます。

想定するAPI仕様はこんな感じです。

```
GET  /api/employees        # 従業員一覧
GET  /api/employees/{id}   # 従業員詳細
POST /api/employees        # 従業員登録
PUT  /api/employees/{id}   # 従業員更新
```

認証はBearerトークンを使う一般的なREST APIです。

### HTTPサーバーとして統合する場合

APIがHTTPSで公開されていて、MCPエンドポイント（`/mcp`）を用意できるなら、接続は1コマンドです。

```
claude mcp add --transport http \
  --header "Authorization: Bearer YOUR_API_TOKEN" \
  employee-api https://api.company.internal/mcp
```

APIがMCPプロトコルに対応している必要があります。既存のREST APIをMCP対応にするには、[MCP SDK](https://modelcontextprotocol.io/quickstart/server)を使ってツール定義を追加する形が一般的です。

APIがまだMCP対応していない場合は、後述のstdioラッパー方式が現実的な選択肢です。

### stdioラッパーとして統合する場合

既存のAPIをそのまま活かしながらMCPに対応させる方法として、**stdioラッパースクリプト**が使えます。PythonやNode.jsで薄いラッパーを書いて、MCPのプロトコルを喋らせる方法です。

```
claude mcp add --transport stdio \
  --env EMPLOYEE_API_TOKEN=your-token \
  --env EMPLOYEE_API_URL=https://api.company.internal \
  employee-api -- python /path/to/employee_mcp_server.py
```

ラッパースクリプトの中身はこんな構造になります。

```
# employee_mcp_server.py
import os
import json
import sys
import requests
from mcp.server import Server
from mcp.server.stdio import stdio_server

API_URL = os.environ["EMPLOYEE_API_URL"]
API_TOKEN = os.environ["EMPLOYEE_API_TOKEN"]

app = Server("employee-api")

@app.list_tools()
async def list_tools():
    return [
        {
            "name": "list_employees",
            "description": "従業員一覧を取得する。部署や役職でフィルタリング可能。",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "department": {"type": "string", "description": "部署名（任意）"},
                    "limit": {"type": "integer", "description": "取得件数（デフォルト20）"}
                }
            }
        },
        {
            "name": "get_employee",
            "description": "指定したIDの従業員詳細を取得する",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "employee_id": {"type": "string", "description": "従業員ID"}
                },
                "required": ["employee_id"]
            }
        }
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    if name == "list_employees":
        params = {}
        if "department" in arguments:
            params["department"] = arguments["department"]
        if "limit" in arguments:
            params["limit"] = arguments["limit"]
        
        resp = requests.get(f"{API_URL}/api/employees", headers=headers, params=params)
        return [{"type": "text", "text": json.dumps(resp.json(), ensure_ascii=False)}]

    elif name == "get_employee":
        emp_id = arguments["employee_id"]
        resp = requests.get(f"{API_URL}/api/employees/{emp_id}", headers=headers)
        return [{"type": "text", "text": json.dumps(resp.json(), ensure_ascii=False)}]

if __name__ == "__main__":
    import asyncio
    asyncio.run(stdio_server(app))
```

ツールの`description`は地味に重要です。Claudeがどのツールを使うべきか判断する根拠になるので、「いつ使うか」「何ができるか」を具体的に書きます。

## スコープ設計：個人用かチーム共有か

MCPサーバーの設定には3つのスコープがあります。ここを適切に設計しないと「自分だけ動く」「チームで設定がバラバラ」という問題が起きます。

| スコープ | 保存先 | 用途 |
| --- | --- | --- |
| local（デフォルト） | `~/.claude.json`（プロジェクトパス下） | 個人の試験的な設定 |
| project | `.mcp.json`（プロジェクトルート） | チーム共有・バージョン管理 |
| user | `~/.claude.json`（全プロジェクト共通） | 個人の汎用ツール |

チームで使うAPIを統合するなら、`--scope project`でプロジェクトに紐づけるのが基本です。

```
claude mcp add --transport http \
  --scope project \
  employee-api https://api.company.internal/mcp
```

これで`.mcp.json`が生成されます。

```
{
  "mcpServers": {
    "employee-api": {
      "type": "http",
      "url": "https://api.company.internal/mcp"
    }
  }
}
```

このファイルをGitにコミットすれば、チーム全員が同じMCPサーバーを使えます。

APIキーなどの認証情報は`.mcp.json`に直書きしないでください。環境変数で渡す設計にします。

環境変数を使う場合の`.mcp.json`はこう書けます。

```
{
  "mcpServers": {
    "employee-api": {
      "type": "http",
      "url": "${EMPLOYEE_API_URL:-https://api.company.internal}/mcp",
      "headers": {
        "Authorization": "Bearer ${EMPLOYEE_API_TOKEN}"
      }
    }
  }
}
```

`${VAR:-デフォルト値}`という記法が使えるので、ローカル環境と本番環境で向き先を切り替えることもできます。

## OAuth認証の設定

外部SaaSのMCPサーバーを使う場合、OAuth認証が必要なことがあります。手順は意外とシンプルです。

まずサーバーを登録します。

```
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp
```

次に、Claude Codeのセッション内で`/mcp`コマンドを実行します。

一覧にsentryが表示されるので「Authenticate」を選ぶと、ブラウザが開いてOAuth認証フローが始まります。認証が完了すると、以降のセッションでは自動的にトークンが使われます。

ブラウザが自動で開かない場合は、表示されるURLを手動でコピーして開いてください。

### 特定ポートが必要な場合

サーバー側にリダイレクトURIを事前登録する必要がある場合は`--callback-port`を使います。

```
claude mcp add --transport http \
  --client-id your-client-id \
  --client-secret \
  --callback-port 8080 \
  my-server https://mcp.example.com/mcp
```

`--client-secret`フラグはマスクされた入力プロンプトを出すので、シークレットがコマンド履歴に残りません。CI環境では環境変数で渡す方法もあります。

```
MCP_CLIENT_SECRET=your-secret claude mcp add --transport http \
  --client-id your-client-id \
  --client-secret \
  --callback-port 8080 \
  my-server https://mcp.example.com/mcp
```

## カスタム認証ヘッダーを動的に生成する

Kerberos認証や短命トークンのような、OAuthではない独自認証には`headersHelper`が使えます。`.mcp.json`に設定します。

```
{
  "mcpServers": {
    "internal-api": {
      "type": "http",
      "url": "https://mcp.internal.company.com",
      "headersHelper": "/opt/scripts/get-mcp-token.sh"
    }
  }
}
```

シェルスクリプトの中身はJSON形式でヘッダーを出力するだけです。

```
#!/bin/bash
# get-mcp-token.sh
TOKEN=$(vault read -field=token secret/mcp-api-token)
echo "{\"Authorization\": \"Bearer ${TOKEN}\"}"
```

スクリプトは接続のたびに実行されるので、常に有効なトークンが使われます。

スクリプト内では`CLAUDE_CODE_MCP_SERVER_NAME`と`CLAUDE_CODE_MCP_SERVER_URL`の環境変数が使えるので、複数のMCPサーバーに対して1つのスクリプトを使い回すことができます。

## 大量データを扱うツールのチューニング

DBスキーマの全体取得や大きなログファイルの読み込みなど、出力が大きくなりがちなツールには注意が必要です。

デフォルトでは10,000トークンを超えるとClaudeが警告を出します。上限を変更するには環境変数で設定します。

```
export MAX_MCP_OUTPUT_TOKENS=50000
claude
```

自分でMCPサーバーを作る場合、ツールごとに上限を設定することもできます。

```
{
  "name": "get_full_schema",
  "description": "データベースの全スキーマを取得する",
  "_meta": {
    "anthropic/maxResultSizeChars": 500000
  }
}
```

`_meta`の設定はツールごとの閾値を上げますが、`MAX_MCP_OUTPUT_TOKENS`のグローバル上限（デフォルト25,000トークン）は別途変更が必要です。両方の設定が必要な点に注意してください。

## チーム展開と管理者向けの設定

組織全体でMCPサーバーを統制したい場合、管理者が設定ファイルをシステムディレクトリに置く方法があります。

| OS | 配置パス |
| --- | --- |
| macOS | `/Library/Application Support/ClaudeCode/managed-mcp.json` |
| Linux/WSL | `/etc/claude-code/managed-mcp.json` |
| Windows | `C:\Program Files\ClaudeCode\managed-mcp.json` |

このファイルを置くと、ユーザーは独自のMCPサーバーを追加できなくなります。承認済みのサーバーだけを使わせたい場合に効果的です。

```
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/"
    },
    "employee-api": {
      "type": "http",
      "url": "https://api.company.internal/mcp"
    }
  }
}
```

完全ロックアップではなく「承認リスト内なら自由に追加してよい」という運用にする場合は、managed settingsのallowlistが使えます。

```
{
  "allowedMcpServers": [
    { "serverName": "github" },
    { "serverUrl": "https://*.company.internal/*" },
    { "serverCommand": ["npx", "-y", "@company/approved-mcp"] }
  ],
  "deniedMcpServers": [
    { "serverUrl": "https://*.untrusted.com/*" }
  ]
}
```

URLパターンには`*`ワイルドカードが使えます。`https://*.company.internal/*`と書けば社内ドメインのサブドメイン全体を許可できます。

ポイントは3つあります。

* denylistはallowlistより優先される（両方に載っていたら必ずブロック）
* stdioサーバーはcommandの完全一致で判定される（引数の順番まで含む）
* URLパターンがallowlistにある場合、リモートサーバーはURL一致が必要

## サーバーの状態確認とトラブルシューティング

設定後の確認コマンドをまとめておきます。

```
# 設定済みサーバー一覧
claude mcp list

# 特定サーバーの詳細（OAuth設定の確認も含む）
claude mcp get employee-api

# サーバーの削除
claude mcp remove employee-api

# Claude Code内でのステータス確認
/mcp
```

接続に問題がある場合によくあるのが、タイムアウトエラーです。起動が遅いサーバーには環境変数でタイムアウトを延ばせます。

Windowsのネイティブ環境（WSLでない）でstdioサーバーを使う場合、`npx`を直接呼び出すと「Connection closed」エラーになります。`cmd /c`でラップしてください。

```
claude mcp add --transport stdio my-server -- cmd /c npx -y @company/mcp-server
```

## まとめ

MCPは「Claudeに外部ツールへのアクセス権を渡す仕組み」ではなく、「Claudeをプロジェクトの作業環境に統合するための仕組み」です。

APIを繋いで終わりではなく、スコープ設計・認証管理・出力サイズの調整・チーム展開まで含めて初めて運用になります。

まず試すなら、この2ステップから始めるのがよいでしょう。

1. `claude mcp add --transport http github https://api.githubcopilot.com/mcp/`でGitHubを繋いでみる
2. 自社APIにMCP SDKでツール定義を追加して、stdioサーバーとして接続してみる

GitHubやSentryなどの既製サーバーで操作感を掴んでから、自社API統合に進むのが実際には一番スムーズです。
