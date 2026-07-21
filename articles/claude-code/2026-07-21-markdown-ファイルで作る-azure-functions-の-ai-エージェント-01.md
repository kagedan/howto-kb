---
id: "2026-07-21-markdown-ファイルで作る-azure-functions-の-ai-エージェント-01"
title: "Markdown ファイルで作る Azure Functions の AI エージェント"
url: "https://zenn.dev/akkodis_jp/articles/6ec38ebe049f00"
source: "zenn"
category: "claude-code"
tags: ["MCP", "API", "AI-agent", "LLM", "Python", "zenn"]
date_published: "2026-07-21"
date_collected: "2026-07-22"
summary_by: "auto-rss"
query: ""
---

# azurefunctions-agents-runtime のサンプルを試してみた

Azure Functions 上で AI エージェントを動かせるということで、公式リポジトリのサンプルをほぼそのまま触ってみた。

<https://github.com/Azure/azure-functions-agents-runtime>

まだ Preview だけども、`.agent.md` を置くだけでチャット UI と API が立ち上がる。  
興味深い。

## サンプルのファイル構成

サンプルを動かすために、公式リポジトリから以下のファイルをローカルにコピーして中を確かめてみる。

* `host.json`
* `local.settings.json`
* `requirements.txt`
* `function_app.py`
* `agents.config.yaml`

中を確認。

### `host.json`

HTTP のパスを `/api/...` からいじっている。

```
    :
  "extensions": {
    "http": {
      "routePrefix": ""
    }
  },
    :
```

### `local.settings.json`

環境変数でエージェントが使う LLM を設定。  
Microsoft Foundry にデプロイした LLM を使う場合は以下を設定。

```
{
  "IsEncrypted": false,
  "Values": {
      :
    "AZURE_FUNCTIONS_AGENTS_PROVIDER": "foundry",
    "FOUNDRY_PROJECT_ENDPOINT": "https://<FOUNDRYアカウント名>.services.ai.azure.com/api/projects/<FOUNDRYプロジェクト名>",
    "FOUNDRY_MODEL": "<モデルデプロイ名>"
      :
  }
}
```

### `requirements.txt`

依存関係は `azurefunctions-agents-runtime` だけ。

```
azurefunctions-agents-runtime
```

### `agents.config.yaml`

`azurefunctions-agents-runtime` の設定ファイル。

```
# Default runtime configuration
model: $FOUNDRY_MODEL
timeout: 900
```

### `function_app.py`

`function_app.py` は最小構成。  
アプリ本体はこれだけ。

```
from azure_functions_agents import create_function_app

app = create_function_app()
```

## エージェント固有のファイル

実際のエージェント追加は、`*.agent.md` というファイルを置くだけ。  
あとは `azurefunctions-agents-runtime` が、`*.agent.md` を読んで、関数を自動で追加してくれる。  
シンプル。

今回は試しにエージェントを2つ作ってみた。

どちらも front matter に `builtin_endpoints: true` が入っていて、これがあるとチャット UI / Chat API / MCP が一式で有効になる。

## セットアップ

まず依存モジュールをインストール（仮想環境 `.venv` の場合）。

```
.venv/bin/python -m pip install -r requirements.txt
```

続いて起動。

## 起動してみる

通常の Azure Functions のプロジェクトと同じように `func start` してみる。  
すると、起動ログから以下のエンドポイントが設定されたのがわかる。

### Chat UI

各エージェントとの会話を確認できるチャット UI が開く。

* `http://localhost:7071/agents/polite/`
* `http://localhost:7071/agents/lazy/`

### Chat API

* `POST http://localhost:7071/agents/polite/chat`
* `POST http://localhost:7071/agents/polite/chatstream`
* `POST http://localhost:7071/agents/lazy/chat`
* `POST http://localhost:7071/agents/lazy/chatstream`

### MCP

* `http://localhost:7071/runtime/webhooks/mcp`
* `http://localhost:7071/runtime/webhooks/mcp/sse` (legacy)

`*.agent.md` を 2 つ置いただけで、  
この辺が全部そろうのは体験としてだいぶ楽。

一部のエンドポイントにある `/agents/` の下の部分には、`.agent.md` のファイル名で使ったエージェント名 (`lazy.agent.md` であれば `lazy` の部分) が入ってくる。  
ファイル内の `name` フィールドはパスには使われないので注意。

## 気づいたこと

1. 最小コードで動く

関数アプリ本体は `create_function_app()` だけで成立するので、  
「まず試してみる」までの距離が短い。

2. エージェントの追加が簡単

今回みたいにキャラ違いのエージェントを並べるだけなら、  
`.agent.md` を増やすだけでよい。

3. モデル設定は環境変数から

`agents.config.yaml` が

```
model: $FOUNDRY_MODEL
timeout: 900
```

になっているので、モデル（Microsoft Foundry ならデプロイメント）変更は環境変数から。  
`local.settings.json` 側で吸収できる。

## まとめ

「Functions で AI エージェントをすぐ動かしたい」なら、かなり手触りがよかった。

* `.agent.md` を書くだけで管理しやすい
* Chat UI / API / MCP が最初からそろう
* Python 側のエントリポイントが最小

次は `tools/` に Python 関数を追加して、MCP 経由のツール実行まで試したい。

以上。
