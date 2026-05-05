---
id: "2026-05-04-dev-container-で-claude-code-を安全に使う環境構築ガイド-01"
title: "Dev Container で Claude Code を安全に使う環境構築ガイド"
url: "https://qiita.com/hiroyukiwk/items/40990bc9a940d68b2980"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "qiita"]
date_published: "2026-05-04"
date_collected: "2026-05-05"
summary_by: "auto-rss"
---

## はじめに

Claude Code はエージェントとしてファイルの読み書き・コマンド実行・ネットワークアクセスを自律的に行います。そのままローカル環境で使うと、意図せず重要なファイルを変更されるリスクがあります。

Dev Container を使えば、Claude Code をコンテナ内に閉じ込めて安全に使えます。ホストの `~/Documents` や `~/.ssh` にはアクセスできないので、何か壊れてもコンテナを削除するだけで元通りです。

## 環境

- Mac（Apple Silicon）
- Docker Desktop
- VS Code

## 事前準備

### Docker Desktop のインストール・起動

[Docker Desktop](https://www.docker.com/products/docker-desktop/) をインストールして起動しておきます。メニューバーにクジラアイコンが表示されていればOKです。

### VS Code 拡張のインストール

VS Code に **Dev Containers**（Microsoft製）をインストールします。

## セットアップ手順

### 1. プロジェクトフォルダを作成

```bash
mkdir -p ~/MyProject/my-app
cd ~/MyProject/my-app
```

### 2. `.devcontainer/devcontainer.json` を作成

```
my-app/
└── .devcontainer/
    └── devcontainer.json
```

```jsonc
{
  "name": "Claude Code Sandbox",
  "image": "mcr.microsoft.com/devcontainers/base:ubuntu",
  "features": {
    "ghcr.io/anthropics/devcontainer-features/claude-code:1.0": {}
  },
  "remoteUser": "vscode",
  "postCreateCommand": "sudo chown -R vscode:vscode /home/vscode/.claude"
}
```

> **⚠️ featureのパスに注意**
> ネット上には古い情報が残っています。正しいパスは以下です。
> ```
> ghcr.io/anthropics/devcontainer-features/claude-code:1.0
> ```

> **💡 `postCreateCommand` について**
> `.claude` ディレクトリのオーナーが `root` になっているとClaude Codeが起動できません。この1行で権限を事前に修正します。

### 3. VS Code でコンテナを起動

VS Code でプロジェクトフォルダを開き、`Cmd+Shift+P` → **Dev Containers: Reopen in Container** を実行します。

初回はイメージのダウンロードがあるので数分かかります。

### 4. ターミナルで Claude Code を起動

コンテナが起動したら、VS Code のターミナルで以下を実行します。

```bash
claude
```

プロンプトが `/workspaces/my-app` になっていればコンテナ内で動いています。

### 5. 認証

初回起動時に以下の画面が出ます。

```
Select login method:
❯ 1. Claude account with subscription · Pro, Max, Team, or Enterprise
  2. Anthropic Console account · API usage billing
  3. 3rd-party platform · Amazon Bedrock, Microsoft Foundry, or Vertex AI
```

Claude Pro などのサブスクリプションを持っている場合は **1** を選びます。ブラウザが開いてログインできます。

## 毎回の起動手順

1. Docker Desktop が起動していることを確認
2. VS Code でプロジェクトを開く
3. `Cmd+Shift+P` → **Dev Containers: Reopen in Container**
4. ターミナルで `claude` を実行

## 新しいプロジェクトを始めるとき

動作確認済みの `.devcontainer` をコピーして使い回します。

```bash
cp -r ~/MyProject/my-app/.devcontainer ~/MyProject/新プロジェクト名/
```

## プロンプトの見方

```
vscode ➜ /workspaces/my-app $
  ↑              ↑            ↑
ユーザー名     今いる場所   入力待ち
```

コンテナ内のユーザーは `vscode`、作業場所は `/workspaces/` 以下になります。ホストの `/Users/ユーザー名/MyProject/my-app` がここにマウントされているため、コンテナ内でファイルを編集するとホスト側にも反映されます。

## セキュリティのポイント

| 項目 | 内容 |
|------|------|
| ホストのファイル保護 | `~/Documents`・`~/.ssh`・`~/.aws` 等にはアクセス不可 |
| 壊れたときのリカバリ | コンテナを削除するだけで元通り |
| `--dangerously-skip-permissions` | コンテナ内なら安全に使える |

## トラブルシューティング

### `.claude` の権限エラーが出る

```bash
sudo chown -R vscode:vscode /home/vscode/.claude
```

### コンテナを作り直したい

`Cmd+Shift+P` → **Dev Containers: Rebuild Container**

### featureが取得できない（403エラー）

featureのパスが間違っています。以下の正しいパスを使ってください。

```
ghcr.io/anthropics/devcontainer-features/claude-code:1.0
```

## まとめ

Dev Container を使うことで、Claude Code をホストマシンから完全に隔離した環境で動かせます。一度 `.devcontainer` フォルダを作れば、新しいプロジェクトにコピーするだけで同じ環境がすぐ使えるのが便利です。

`--dangerously-skip-permissions` も安心して使えるようになるので、Claude Code の作業効率が大幅に上がります。

## 感想
Claude に聞きながら進めましたが、それでも結構エラーが出て難しかったです。
- featureのパスが古い情報のままだった：ネット上に誤ったパスが出回っており、403エラーが出て最初は原因がわかりませんでした。
- .claude` ディレクトリの権限問題：オーナーが `root` になっていてClaude Codeが起動できず、`postCreateCommand` で対処しました。

この記事ではそのあたりのハマりポイントも含めてまとめているので、同じところで詰まっている方の参考になれば嬉しいです。

## 参考
[Claude Code 公式ドキュメント - Development containers](https://code.claude.com/docs/en/devcontainer)
[anthropics/devcontainer-features - GitHub](https://github.com/anthropics/devcontainer-features)
[Docker公式 - Claude Code](https://docs.docker.com/ai/sandboxes/agents/claude-code/)
