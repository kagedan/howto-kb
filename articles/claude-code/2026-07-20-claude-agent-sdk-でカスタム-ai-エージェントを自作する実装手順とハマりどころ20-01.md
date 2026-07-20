---
id: "2026-07-20-claude-agent-sdk-でカスタム-ai-エージェントを自作する実装手順とハマりどころ20-01"
title: "Claude Agent SDK でカスタム AI エージェントを自作する実装手順とハマりどころ【2026】"
url: "https://qiita.com/yureki_lab/items/d64230d1302b4bb30660"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "Python"]
date_published: "2026-07-20"
date_collected: "2026-07-21"
summary_by: "auto-rss"
query: ""
---

## はじめに / 対象と前提

Claude Agent SDK(Python版)を使って、独自ツールを持たせた自作AIエージェントを動かすところまでを書く。

想定読者は以下の通り。

- Claude Code は業務で使っているが、SDK 経由で「自分のアプリに組み込む」のは初めて
- LangChain などの他フレームワークの Agent 実装経験はあるが、Claude Agent SDK は触ったことがない
- 「動かしてみたら権限まわりで詰まった」を先回りして知りたい

前提環境は以下。

- Python 3.11 以降
- `claude-agent-sdk` (pip パッケージ、2026年時点の最新系列)
- Anthropic API キー(環境変数 `ANTHROPIC_API_KEY`)

## TL;DR

- `query()` 関数だけで最小構成のエージェントは数行で動く
- 独自ツールは `@tool` デコレータ + `create_sdk_mcp_server` でローカル MCP サーバーとして生やす
- `permission_mode` を明示しないと、ツール実行のたびに承認待ちで止まる(自動化用途では詰む)
- マルチターンにするなら `query()` の使い捨てではなく `ClaudeSDKClient` を使う

## 手順 / 動かし方

### 1. インストール

```bash
pip install claude-agent-sdk
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 2. 最小構成で動かす

まずはツールなしの一問一答から。

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    options = ClaudeAgentOptions(
        system_prompt="あなたはPythonのコードレビューに特化したアシスタントです。",
        max_turns=1,
    )
    async for message in query(prompt="このコードの改善点を3つ挙げて", options=options):
        print(message)

asyncio.run(main())
```

`query()` は非同期ジェネレータで、テキストやツール実行結果のメッセージを逐次流してくる。1回きりのタスクならこれで十分。

### 3. カスタムツールを定義する

エージェントに社内APIを叩かせたいなど、独自ツールを持たせたい場合は `@tool` デコレータでローカル関数を定義し、`create_sdk_mcp_server` でまとめて MCP サーバー化する。

```python
from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeAgentOptions

@tool("get_deploy_status", "指定サービスの最新デプロイ状況を取得する", {"service_name": str})
async def get_deploy_status(args):
    service = args["service_name"]
    # 実際はここで社内APIを叩く。ここではダミー応答
    return {
        "content": [
            {"type": "text", "text": f"{service} は 3分前に正常デプロイ済み"}
        ]
    }

my_server = create_sdk_mcp_server(
    name="deploy-tools",
    version="1.0.0",
    tools=[get_deploy_status],
)

options = ClaudeAgentOptions(
    mcp_servers={"deploy": my_server},
    allowed_tools=["mcp__deploy__get_deploy_status"],
)
```

ツール名は SDK 内部で `mcp__<サーバー名>__<関数名>` の形に変換される。`allowed_tools` にはこの変換後の名前を書く必要がある点に注意。関数名だけ書いても認識されない。

### 4. permission_mode を使い分ける

デフォルトのままだとツール実行のたびに承認確認が挟まる。バッチ処理や自動化スクリプトでは明示的に指定する。

```python
options = ClaudeAgentOptions(
    mcp_servers={"deploy": my_server},
    allowed_tools=["mcp__deploy__get_deploy_status"],
    permission_mode="acceptEdits",  # ファイル編集系を自動承認
)
```

主な選択肢は次の4つ。

| モード | 挙動 |
|---|---|
| `default` | 逐一確認(対話用途向け) |
| `acceptEdits` | ファイル編集は自動承認、それ以外は確認 |
| `bypassPermissions` | 全ツール自動承認(信頼できるサンドボックス限定) |
| `plan` | 実行せず計画だけ立てさせる |

`bypassPermissions` は便利だが、実行環境を隔離していないと危険なコマンドもそのまま通る。CI や使い捨てコンテナ以外では避けたほうがいい。

### 5. マルチターンの会話ループを組む

Slack ボットのように会話を継続させたいなら `ClaudeSDKClient` を使う。

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

async def chat_loop():
    options = ClaudeAgentOptions(permission_mode="acceptEdits")
    async with ClaudeSDKClient(options=options) as client:
        while True:
            user_input = input("You: ")
            if user_input == "exit":
                break
            await client.query(user_input)
            async for message in client.receive_response():
                print(message)
```

`client` インスタンスがセッション状態(会話履歴)を保持してくれるので、毎ターン `system_prompt` を組み直す必要はない。

## ハマりどころ

### 1. カスタムツールのスキーマ不整合

`@tool` の第3引数(パラメータ定義)と実際に渡ってくる `args` の型が食い違うと、ツール呼び出し自体は成功するのに関数内で `KeyError` や `TypeError` が出る。数値を `str` で定義してしまい、モデルが文字列で渡してきたケースでハマった。パラメータ定義は簡易的な型ヒントでしかなく、実行時のバリデーションは自前で入れる必要がある。

### 2. permission_mode の設定漏れによる無限待ち

`permission_mode` を指定し忘れると、対話環境がない実行(cron やバックグラウンドジョブ)では承認プロンプトが誰にも表示されないまま処理がハングする。ログを見ても「ツールを呼ぼうとして止まっている」ようにしか見えず、原因特定に時間がかかった。自動実行用のスクリプトでは必ず明示することを徹底したい。

### 3. 会話ループでのコンテキスト肥大化

`ClaudeSDKClient` でセッションを使い回すと、ツール実行結果や過去の応答が蓄積してコンテキストが肥大化する。長時間稼働のチャットボットだと数十ターン目あたりからレスポンスが遅くなりコストも跳ね上がる。一定間隔でセッションを作り直す(会話の要約を `system_prompt` に埋め込んで再スタートする)運用が必要になる。

## 背景・補足

Claude Agent SDK はもともと Claude Code の内部実装をライブラリとして切り出したもので、ツール実行・権限管理・MCP 連携といった「エージェントを安全に動かす」土台がそのまま使える。LangChain 等と違い、Anthropic のモデル運用を前提に権限モデルが最初から組み込まれているのが特徴で、`permission_mode` はその象徴的な機能と言える。

## まとめ

- 最小構成なら `query()` 一発、独自ツールが必要なら `@tool` + `create_sdk_mcp_server`
- `permission_mode` は自動化用途なら必ず明示する。指定漏れは無限待ちに直結する
- カスタムツールの引数は自前でバリデーションを入れる、SDK 側の型ヒントは実行時チェックまではしてくれない
- マルチターン運用ではコンテキスト肥大化を見越して、セッションの作り直しポイントを設計しておく
