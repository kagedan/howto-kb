---
id: "2026-07-21-claude-code-cli-から-databricks-の-claude-モデルを利用する-01"
title: "Claude Code CLI から Databricks の Claude モデルを利用する"
url: "https://qiita.com/satoshi_enomoto/items/9c9e9d008d52e534cb1a"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "OpenAI", "qiita"]
date_published: "2026-07-21"
date_collected: "2026-07-22"
summary_by: "auto-rss"
query: ""
---

## はじめに

本記事では、VS Code の WSL 環境から Claude Code を実行し、推論モデルとして Azure Databricks の Unity AI Gateway 経由で提供される Claude モデルを利用する手順を整理します。

構成は以下のとおりです。

```text
VS Code
  └─ WSL
      └─ Claude Code CLI
          └─ Unity AI Gateway
              └─ Databricks の Claude モデル
```

## 前提
* VS Code で WSL をセットアップ
* Databricksワークスペースへのアクセス
* 新しい Unity AI Gateway を有効化
    * https://learn.microsoft.com/ja-jp/azure/databricks/ai-gateway/

## 環境セットアップ

### Node.jsをインストール

```bash
# nvm をインストール
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/master/install.sh | bash

# nvm を読み込む
source ~/.bashrc

# nvm を使って Node.js をインストール
nvm install --lts

# バージョン確認
node --version
npm --version
```

### Claude Code CLI をインストール

```bash
# Claude Code CLI をインストール
npm install -g @anthropic-ai/claude-code

# バージョン確認
claude --version
```

### Databricks CLI をインストール

```bash
# unzip をインストール
sudo apt update && sudo apt install -y unzip

# Databricks CLI をインストール
curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sudo sh

# バージョン確認
databricks -v
```

### Databricksワークスペースへの認証

```bash
databricks auth login --host https://adb-xxxxxxxxxxxxxxxx.x.azuredatabricks.net
```

:::note info
証明書エラー

以下のようなエラーが発生した場合、社内 CA 証明書を WSL へコピーして登録する必要があります。

>curl failed to verify the legitimacy of the server and therefore could not establish a secure connection to it. To learn more about this situation and how to fix it, please visit the webpage mentioned above.

```bash
# WSL へコピー
sudo cp /mnt/c/Users/<Windowsユーザー名>/Downloads/company-root-ca.cer \
  /usr/local/share/ca-certificates/company-root-ca.crt

# 証明書の登録
sudo chmod 644 /usr/local/share/ca-certificates/company-root-ca.crt
sudo update-ca-certificates

# 環境変数を設定
export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
export CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
export NODE_EXTRA_CA_CERTS=/usr/local/share/ca-certificates/company-root-ca.crt
```

:::

## モデルのアクセストークンを取得

AI ゲートウェイで使用するモデルを選択して、アクセストークンを生成してメモしておきます。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3478068/62347b2a-8d67-4a3a-b06a-b63d7ca838f1.png)

## Claude Code 設定を作成

`~/.claude` フォルダに設定ファイルを作成します。

```bash
nano ~/.claude/settings.json
```

設定値は以下のようにします。

```json
{
  "env": {
    "ANTHROPIC_MODEL": "system.ai.claude-sonnet-4-5",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "system.ai.claude-sonnet-4-5",
    "ANTHROPIC_BASE_URL": "https://<workspace>.azuredatabricks.net/ai-gateway/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "dapi...",
    "CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS": "1"
  }
}
```

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3478068/d3a94f7e-0d84-4331-a4de-3f028ea9d2fc.png)

:::note info
`ANTHROPIC_BASE_URL` について

`ANTHROPIC_BASE_URL` に OpenAI 互換の Chat Completions URL ( `https://<workspace>/ai-gateway/mlflow/v1/chat/completions` ) を設定すると以下のエラーが発生しました。

>API Error: 400 Request path '/ai-gateway/mlflow/v1/chat/completions/v1/messages?beta=true' doesn't match any known API type and is classified as an unmanaged api request. Set the Databricks-Model-Provider-Service header to the name of the model provider service to forward this request to.

Anthropic Messages API 互換の URL ( `https://<workspace>.azuredatabricks.net/ai-gateway/anthropic` ) を設定する必要があります。
:::

:::note info
`CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS` について

Claude Code が自動付与する `anthropic-beta` ヘッダーを、Databricks の Anthropic 互換エンドポイントが認識できずに以下のエラーが発生しました。

>API Error: 400 {"message":"invalid beta flag"}

`"CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS": "1"` を追記することで解決しました。
:::

## 動作確認

以下で claude を起動します。

```bash
claude
```

`テスト` と打ち込み、回答が返ってくることが確認できました。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3478068/5aeb93fd-2fa7-4441-a890-0ff1537356ee.png)

Databricks ワークスペース側で使用したトークン数を確認できます。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3478068/f67a842a-53ef-4be9-b105-67c2b13ca318.png)
