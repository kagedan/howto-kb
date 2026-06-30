---
id: "2026-06-30-ubuntuにclaude-codeをインストールする手順-01"
title: "UbuntuにClaude Codeをインストールする手順"
url: "https://zenn.dev/reika_sui/articles/ff74f98575d048"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "zenn"]
date_published: "2026-06-30"
date_collected: "2026-07-01"
summary_by: "auto-rss"
query: ""
---

# はじめに

この記事では、Ubuntu / Linux / WSL 環境に Claude Code をインストールする手順をまとめます。

Claude Code は、ターミナル上で利用できるAIコーディング支援ツールです。  
現在の公式手順では、Ubuntu / Linux / WSL では **Native Install** が推奨されています。

<https://code.claude.com/docs/en/quickstart>

# 対象環境

この記事では、主に以下の環境を対象にします。

| 項目 | 内容 |
| --- | --- |
| OS | Ubuntu 20.04 以上 |
| 推奨OS | Ubuntu 22.04 LTS / Ubuntu 24.04 LTS |
| 環境 | Linux / WSL |
| CPU | x64 または ARM64 |
| メモリ | 4GB以上推奨 |
| シェル | Bash / Zsh |
| ネットワーク | インターネット接続必須 |

# 事前確認

まず、OSとCPUアーキテクチャを確認します。

メモリを確認します。

シェルを確認します。

`curl` が入っているか確認します。

`curl` と `ca-certificates` がない場合はインストールします。

```
sudo apt update
sudo apt install -y curl ca-certificates
```

# 方法1: Native Installでインストールする

Ubuntu / Linux / WSL では、この方法を第一候補にします。

```
curl -fsSL https://claude.ai/install.sh | bash
```

インストール後、シェルを再読み込みします。

バージョンを確認します。

診断を実行します。

# stableチャンネルを指定してインストールする

安定版を使いたい場合は、`stable` を指定します。

```
curl -fsSL https://claude.ai/install.sh | bash -s stable
```

シェルを再読み込みします。

確認します。

```
claude --version
claude doctor
```

# 初回ログイン

作業用ディレクトリを作成します。

```
mkdir -p ~/projects/claude-test
cd ~/projects/claude-test
```

Claude Codeを起動します。

初回起動時にログインが求められます。  
ブラウザが開いたら、画面の案内に従ってClaudeアカウントでログインします。

# WSLやSSH環境でログインする場合

WSL、SSH、コンテナ環境では、ブラウザ認証後のリダイレクトがうまく戻らない場合があります。

その場合は、ブラウザに表示されたコードをターミナル側へ貼り付けます。

```
Paste code here if prompted
```

ログインをやり直す場合は、以下を実行します。

WSLでWindows側のChromeを使いたい場合は、次のように `BROWSER` を指定します。

```
export BROWSER="/mnt/c/Program Files/Google/Chrome/Application/chrome.exe"
claude auth login
```

Microsoft Edgeを使う場合は以下です。

```
export BROWSER="/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
claude auth login
```

# 方法2: npmでインストールする

Node.jsを利用している環境では、npmでインストールすることもできます。

ただし、公式手順ではNative Installが推奨されているため、基本的にはNative Installを優先します。

Node.jsとnpmを確認します。

Node.js 18以上が必要です。

Claude Codeをインストールします。

```
npm install -g @anthropic-ai/claude-code
```

確認します。

```
claude --version
claude doctor
```

npm版を更新する場合は以下です。

```
npm install -g @anthropic-ai/claude-code@latest
```

# 方法3: aptで管理する

複数台のUbuntuで管理したい場合や、パッケージ管理をaptに寄せたい場合はapt版を使います。

GPGキー保存用ディレクトリを作成します。

```
sudo apt update
sudo apt install -y curl ca-certificates gnupg

sudo install -d -m 0755 /etc/apt/keyrings
```

GPGキーを取得します。

```
sudo curl -fsSL https://downloads.claude.ai/keys/claude-code.asc   -o /etc/apt/keyrings/claude-code.asc
```

GPGキーを確認します。

```
gpg --show-keys /etc/apt/keyrings/claude-code.asc
```

stableリポジトリを追加します。

```
echo "deb [signed-by=/etc/apt/keyrings/claude-code.asc] https://downloads.claude.ai/claude-code/apt/stable stable main"   | sudo tee /etc/apt/sources.list.d/claude-code.list
```

パッケージ一覧を更新します。

Claude Codeをインストールします。

```
sudo apt install -y claude-code
```

確認します。

```
claude --version
claude doctor
```

apt版を更新する場合は以下です。

```
sudo apt update
sudo apt upgrade -y claude-code
```

# 更新方法

Native Install版を更新する場合は、以下を実行します。

npm版を更新する場合は、以下を実行します。

```
npm install -g @anthropic-ai/claude-code@latest
```

apt版を更新する場合は、以下を実行します。

```
sudo apt update
sudo apt upgrade -y claude-code
```

# アンインストール

導入方法によって削除手順が異なります。

## Native Install版

```
rm -f ~/.local/bin/claude
rm -rf ~/.local/share/claude
```

## npm版

```
npm uninstall -g @anthropic-ai/claude-code
```

## apt版

```
sudo apt remove -y claude-code
sudo rm -f /etc/apt/sources.list.d/claude-code.list
sudo rm -f /etc/apt/keyrings/claude-code.asc
sudo apt update
```

削除後に確認します。

```
which -a claude || true
type -a claude || true
```

# 最短手順

Ubuntu / WSLで最短インストールする場合は、以下を実行します。

```
sudo apt update
sudo apt install -y curl ca-certificates

curl -fsSL https://claude.ai/install.sh | bash

exec "$SHELL" -l

claude --version
claude doctor
```

その後、作業ディレクトリで起動します。

```
mkdir -p ~/projects/claude-test
cd ~/projects/claude-test
claude
```

# 参考
