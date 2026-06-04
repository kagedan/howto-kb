---
id: "2026-06-03-ant-cliでclaude-managed-agentsの定義をgit管理して自動デプロイする-01"
title: "ant CLIでClaude Managed Agentsの定義をGit管理して自動デプロイする！"
url: "https://zenn.dev/uchunanora/articles/claude-managed-agents-versioning"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "zenn"]
date_published: "2026-06-03"
date_collected: "2026-06-04"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Managed Agentsを使うと、AIエージェントの実行基盤をAnthropicに丸ごと任せられるので最高です！  
長時間セッション、権限管理、ツール実行など、面倒な部分を全部やってくれるのでエージェントに何をさせるかに集中できます。  
ただ、コンソールからポチポチ作るのは手軽な反面、変更履歴も追えないしレビューもできません。  
そこで、agentの定義をYAMLでリポジトリに置き、`ant` CLIを使ってGitHub Actionsから更新する仕組みを作ります。

## 1. ant CLI

[ant](https://platform.claude.com/docs/en/api/sdks/cli) は、Claude APIをターミナルから叩くためのCLIです。

### セットアップ

公式ではHomebrew, curl, Goの3通りのインストール方法が用意されています。

<https://platform.claude.com/docs/en/api/sdks/cli>

```
brew install anthropics/tap/ant
```

インストールできたか確認します。

認証は、手元の開発なら `ant auth login` でブラウザのOAuthフローを通すのが手軽です。  
ブラウザが開いてAnthropicのアカウントでログインすれば、認証情報が保存されます。

## 2. agentをYAMLで定義する

まずは小さなagentを定義してみます。  
要約を返すだけのagentを `summarizer.agent.yaml` として書きます。

summarizer.agent.yaml

```
name: Summarizer
model: claude-sonnet-4-6
system: |
  You are a helpful assistant that writes concise summaries.
tools:
  - type: agent_toolset_20260401
```

このファイルを `create` に流し込むと、agentができます。

```
ant beta:agents create < summarizer.agent.yaml
```

```
{
  "id": "agent_XXXXXXXXXXXXXXXXXXXXX",
  "name": "Summarizer",
  "model": {
    "id": "claude-sonnet-4-6",
    "speed": "standard"
  },
  "system": "You are a helpful assistant that writes concise summaries.\n",
  "tools": [{ "type": "agent_toolset_20260401" }],
  "version": 1,
  "created_at": "2026-06-03T05:58:03.268470Z"
}
```

また、今あるagentは `list` で見られます。

```
ant beta:agents list --format json
```

![agent作成](https://static.zenn.studio/user-upload/2aa210244760-20260603.png)

## 3. agentを更新する

既存のagentを変えるには `update` を使います。  
ただし `update` は、agent ID と version をフラグで渡さないと動きません。

```
ant beta:agents update --agent-id agent_XXXXXXXXXXXXXXXXXXXXX --version 1 < summarizer.agent.yaml
```

`version` は楽観ロック用のトークンです。  
渡したversionがサーバー側の最新と食い違っていると、更新は弾かれます。  
更新が通るたびにversionは1つ上がるので、次に更新するときは最新のversionを渡し直します。

現在のversionは `retrieve` で取れます。

```
ant beta:agents retrieve --agent-id agent_XXXXXXXXXXXXXXXXXXXXX --transform version --raw-output
```

## 4. GitHub Actionsで自動デプロイする

やりたいのは、pushのたびに最新のYAMLを反映することです。  
ところが `create` は名前が同じでも毎回新しいagentを作るので、pushのたびに走らせると同じagentがどんどん増えてしまいます。  
かといって `update` は、既存のagent IDがないと打てません。  
そこで、agentが既にあるかを先に調べて、無ければ `create`、有れば `update` と打ち分けます。

ディレクトリ構成はこうなります。

```
.
├── agents/
│   ├── xxx.agent.yaml
│   └── yyy.agent.yaml
├── scripts/
│   └── apply-agent.sh
└── .github/
    └── workflows/
        └── deploy-agents.yml
```

この打ち分けを、小さなシェルスクリプトにします。

apply-agent.sh

```
#!/usr/bin/env bash
set -euo pipefail

file="$1"
name=$(yq '.name' "$file")

# 同じ name の agent が既にあるか探す
id=$(ant beta:agents list \
  --transform '{id,name}' --format jsonl \
  | jq -r --arg n "$name" 'select(.name==$n).id' \
  | head -1)

if [ -z "$id" ]; then
  echo "create: $name"
  ant beta:agents create < "$file"
else
  version=$(ant beta:agents retrieve --agent-id "$id" \
    --transform version --raw-output)
  echo "update: $name ($id, v$version)"
  ant beta:agents update --agent-id "$id" --version "$version" < "$file"
fi
```

ワークフローはこうなります。  
`agents/` 配下のYAMLが変わったときだけ走らせて、変更ぶんを適用します。

deploy-agents.yml

```
name: Deploy Managed Agents

on:
  push:
    branches: [main]
    paths:
      - "agents/**.agent.yaml"
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    env:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    steps:
      - uses: actions/checkout@v4

      - name: Install ant CLI
        run: |
          VERSION=1.10.0
          curl -fsSL "https://github.com/anthropics/anthropic-cli/releases/download/v${VERSION}/ant_${VERSION}_linux_amd64.tar.gz" \
            | sudo tar -xz -C /usr/local/bin ant

      - name: Apply agents
        run: |
          for f in agents/*.agent.yaml; do
            bash scripts/apply-agent.sh "$f"
          done
```

認証はAPIキーを使っていますが、長期キーを置きたくない場合は、[Workload Identity Federation](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation)で鍵レスにする手もあります。

## まとめ

agentの定義をYAMLにしてGitに置けば、変更はコミット履歴に残り、pushするだけで反映されます。  
`ant` 自体は、あれば更新なければ作成をやってくれないので、その判断を薄いスクリプトで補う形です。

コンソールポチポチとはおさらば！
