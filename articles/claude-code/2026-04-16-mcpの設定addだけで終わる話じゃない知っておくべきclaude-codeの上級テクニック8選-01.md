---
id: "2026-04-16-mcpの設定addだけで終わる話じゃない知っておくべきclaude-codeの上級テクニック8選-01"
title: "MCPの設定、addだけで終わる話じゃない。知っておくべきClaude Codeの上級テクニック8選"
url: "https://qiita.com/moha0918_/items/0ac1abef9834b3e3dbec"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "qiita"]
date_published: "2026-04-16"
date_collected: "2026-04-16"
summary_by: "auto-rss"
query: ""
---

Claude CodeでMCPサーバーを使っている人は多いと思います。`claude mcp add` でサーバーを追加して、ツールが動くようになったら「OK、設定完了」と。

でも公式ドキュメントをちゃんと読むと、addの先にけっこう重要な設定が埋まっています。コンテキストウィンドウの圧迫を防ぐTool Search、社内認証に対応するheadersHelper、チーム共有を安全にする環境変数展開――このあたりは知っているだけで運用が変わります。

この記事では、MCPの基本は分かっている前提で、次のステップとなる上級テクニックを8つまとめました。前半3つは特に重要なので詳しく、残り5つはテーブル+コード例で手短にいきます。

## Tool Searchでコンテキストの無駄遣いを防ぐ

MCPサーバーを5つ、10と追加していくと、ツール定義だけでコンテキストウィンドウが埋まっていきます。「最近レスポンスが遅い」「compactionが頻発する」――原因がMCPのツール定義だった、というのは割とある話です。

Tool Searchは、**ツールのスキーマをオンデマンドで読み込む仕組み**です。セッション開始時にはツール名だけロードされ、Claudeが実際に使う段階で初めてスキーマが展開されます。

Tool Searchはデフォルトで有効です。何も設定しなくても、MCPツールは自動的にdeferred（遅延読み込み）されます。

とはいえ、環境によっては挙動をカスタマイズしたいケースもあります。`ENABLE_TOOL_SEARCH` 環境変数で制御できます。

| 値 | 挙動 |
| --- | --- |
| 未設定 | 全MCPツールをdeferred（デフォルト） |
| `true` | 非ファーストパーティホストでも強制的にdeferred |
| `auto` | コンテキストの10%に収まれば先読み、超えたらdeferred |
| `auto:5` | 閾値を5%にカスタム指定 |
| `false` | 全MCPツールを先読み（Tool Search無効） |

```
# MCPサーバーが多い環境向け：閾値5%でTool Searchを使う
ENABLE_TOOL_SEARCH=auto:5 claude
```

毎回指定するのが面倒なら、settings.jsonの `env` に書いておきます。

```
{
  "env": {
    "ENABLE_TOOL_SEARCH": "auto:5"
  }
}
```

注意点として、Tool Searchは **Sonnet 4以降またはOpus 4以降** のモデルでのみ動作します。Haikuでは使えません。また、`ANTHROPIC_BASE_URL` がサードパーティのプロキシを指している場合、`tool_reference` ブロック未対応だとエラーになります。その場合は明示的に `true` にするか `false` で無効化してください。

MCPサーバーを開発している方へ。server instructionsフィールドを充実させておくと、Tool Searchの精度が上がります。ただし説明文は2KBで切られるので、大事な情報は先頭に寄せましょう。

## headersHelperで動的認証ヘッダーを生成する

OAuth対応のリモートMCPサーバーなら `/mcp` コマンドで認証できます。問題は **社内のSSO基盤やKerberos認証を使っているケース**です。固定のBearerトークンでは対応できません。

`headersHelper` は、MCPサーバーへの接続時にシェルコマンドを実行して、認証ヘッダーを動的に生成する仕組みです。

```
{
  "mcpServers": {
    "internal-api": {
      "type": "http",
      "url": "https://mcp.internal.example.com",
      "headersHelper": "/opt/bin/get-mcp-auth-headers.sh"
    }
  }
}
```

ヘルパースクリプトの要件は3つだけです。

* stdoutに **JSON形式のキーバリュー** を出力する
* **10秒以内** に完了する
* 静的な `headers` と同名のキーがあればヘルパー側が優先される

```
#!/bin/bash
# get-mcp-auth-headers.sh
TOKEN=$(get-corporate-sso-token)
echo "{\"Authorization\": \"Bearer ${TOKEN}\"}"
```

ポイントは、ヘルパー実行時に環境変数が自動セットされることです。これを使えば **1つのスクリプトで複数サーバーに対応** できます。

| 環境変数 | 値 |
| --- | --- |
| `CLAUDE_CODE_MCP_SERVER_NAME` | MCPサーバー名 |
| `CLAUDE_CODE_MCP_SERVER_URL` | MCPサーバーのURL |

```
#!/bin/bash
# 1つのスクリプトで複数サーバーに対応する例
case "$CLAUDE_CODE_MCP_SERVER_NAME" in
  "staging-api") TOKEN=$(get-staging-token) ;;
  "prod-api")    TOKEN=$(get-prod-token) ;;
  *)             TOKEN=$(get-default-token) ;;
esac
echo "{\"Authorization\": \"Bearer ${TOKEN}\"}"
```

headersHelperは任意のシェルコマンドを実行します。Project/Localスコープの場合はワークスペース信頼ダイアログの承認が必要です。信頼できるリポジトリでのみ使いましょう。

ヘルパーはセッション開始時と再接続時に毎回実行されます。トークン取得のキャッシュはスクリプト側の責任なので、遅い認証基盤の場合はそこも考慮に入れてください。

## .mcp.jsonでチーム設定を安全に共有する

チーム全員が同じMCPサーバーを使うなら、`.mcp.json` をリポジトリにコミットするのが正攻法です。ただし、APIキーをハードコードするわけにはいきません。

Claude Codeは `.mcp.json` 内での **環境変数展開** をサポートしています。

```
{
  "mcpServers": {
    "api-server": {
      "type": "http",
      "url": "${API_BASE_URL:-https://api.staging.example.com}/mcp",
      "headers": {
        "Authorization": "Bearer ${API_KEY}"
      }
    }
  }
}
```

`${VAR:-default}` 構文でデフォルト値を指定できます。本番・ステージング・ローカルで設定ファイルを分ける必要がなく、各開発者が自分の環境変数で値を上書きするだけです。

展開可能なフィールドは以下の5つです。

* `command` -- サーバー実行パス
* `args` -- コマンドライン引数
* `env` -- サーバーに渡す環境変数
* `url` -- HTTPサーバーのURL
* `headers` -- 認証ヘッダー等

必須の環境変数が未設定かつデフォルト値もない場合、設定の解析時にエラーになります。CIで動かす場合は特に注意してください。

### scopeの使い分けも合わせて考える

`.mcp.json` はProjectスコープに該当します。スコープは3種類あり、同名サーバーが複数定義されている場合は上位が優先されます。

| 優先度 | スコープ | チーム共有 | 用途の例 |
| --- | --- | --- | --- |
| 1 | **local**（デフォルト） | 不可 | 個人のAPIキー付きサーバー |
| 2 | **project** | 可（VCS経由） | チーム標準のツール |
| 3 | **user** | 不可 | 全プロジェクト共通のユーティリティ |

さらにその下にplugin提供のサーバー、claude.ai connectorsと続きます。

```
# 個人用（local -- デフォルト）
claude mcp add --transport http my-debug https://debug.example.com

# チーム共有（.mcp.jsonに書き出される）
claude mcp add --transport http paypal --scope project https://mcp.paypal.com/mcp

# 全プロジェクトで使う
claude mcp add --transport http hubspot --scope user https://mcp.hubspot.com/anthropic
```

よくあるパターンとして、チーム共通の接続先はProjectスコープの `.mcp.json` で定義し、APIキーや個人用サーバーはLocalスコープで上書きする、という使い分けがうまく機能します。

## まだまだある上級テクニック5選

ここからは、使用頻度はやや低いものの「ここぞ」で効いてくるテクニックをまとめて紹介します。

| テクニック | 概要 | コマンド/設定例 |
| --- | --- | --- |
| Claude CodeをMCPサーバー化 | Claude Codeのツール（ファイル操作・検索）を他のMCPクライアントに公開 | `claude mcp serve` |
| maxResultSizeChars | MCPツール単位で出力上限を引き上げ（MCP開発者向け、最大500,000文字） | `"_meta": {"anthropic/maxResultSizeChars": 200000}` |
| Channels | MCPサーバーからセッションへのプッシュ通知。CI結果やアラートの受信に | `claude --channels` で有効化 |
| OAuth事前設定 | Dynamic Client Registration非対応サーバーでのOAuth認証 | `--client-id` `--client-secret` `--callback-port` |
| Managed MCP | 組織全体のMCPサーバーを一元管理し、ユーザーの追加を制限 | `managed-mcp.json` を所定のシステムパスに配置 |

### Claude CodeをMCPサーバーにする

この中で特に面白いのがこれです。以下の設定をClaude Desktopの設定ファイルに追加します。

```
{
  "mcpServers": {
    "claude-code": {
      "type": "stdio",
      "command": "claude",
      "args": ["mcp", "serve"],
      "env": {}
    }
  }
}
```

Claude DesktopのGUIで会話しながら、裏でClaude Codeのファイル操作・検索ツールを使える構成になります。`claude` コマンドがPATHに通っていない場合は `which claude` で取得したフルパスを指定してください。

### Managed MCPで組織管理する

`managed-mcp.json` を以下のパスに配置すると、ユーザーは独自にMCPサーバーを追加できなくなります。

| OS | 配置パス |
| --- | --- |
| macOS | `/Library/Application Support/ClaudeCode/managed-mcp.json` |
| Linux / WSL | `/etc/claude-code/managed-mcp.json` |
| Windows | `C:\Program Files\ClaudeCode\managed-mcp.json` |

もう少し柔軟にやりたい場合は、managed settingsの `allowedMcpServers` / `deniedMcpServers` でURLパターンベースの許可・拒否ルールを組めます。

```
{
  "allowedMcpServers": [
    { "serverUrl": "https://mcp.company.com/*" },
    { "serverUrl": "https://*.internal.corp/*" }
  ],
  "deniedMcpServers": [
    { "serverUrl": "https://*.untrusted.com/*" }
  ]
}
```

denyリストはallowリストより常に優先されます。まずは広めにallowしておいて、問題のあるサーバーだけdenyで塞ぐ運用が現実的でしょう。

## まとめ

`claude mcp add` は入り口でしかありません。Tool Searchでコンテキストを節約し、headersHelperで社内認証に対応し、.mcp.jsonの環境変数展開でチーム共有を安全にする――こうした設定を詰めていくことで、MCPの活用範囲は段違いに広がります。公式ドキュメントには今回紹介しきれなかった細かい設定もまだあるので、一度目を通しておくことをおすすめします。
