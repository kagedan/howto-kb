---
id: "2026-06-01-claude-on-awsamazon-bedrock環境構築ガイド-claude-code-cla-01"
title: "Claude on AWS（Amazon Bedrock）環境構築ガイド — Claude Code & Claude Desktop"
url: "https://zenn.dev/kini/articles/ed704c0edb55c7"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "VSCode", "Python", "zenn"]
date_published: "2026-06-01"
date_collected: "2026-06-02"
summary_by: "auto-rss"
query: ""
---

## はじめに

社内で Amazon Bedrock 経由で Claude を使う環境を整備する機会があったため、その手順をまとめます。

対象は以下の2つのユースケースです。

* **Claude Code**（CLI ツール）を Bedrock 経由で使う
* **Claude Desktop**（GUIアプリ）を AWS Gateway 経由で使う

実際のセットアップ時に旧手順書との差異がいくつか判明したため、最新の動作確認済み情報として記録します。

---

## 前提条件

以下が揃っていることを確認してください。

| 項目 | 備考 |
| --- | --- |
| AWSアカウント | IAMユーザーのアクセスキーが払い出されていること |
| AWS CLI v2 | `aws --version` で確認 |
| Node.js 18以上 | Claude Code に必要 |
| Python 3系 | Claude Desktop のヘルパースクリプトに必要 |
| Bedrock のモデルアクセス | Anthropic モデルが有効化されていること |

---

## Part 1: Claude Code を Bedrock 経由で使う

### Step 1 — AWS CLI のインストール確認

```
aws --version
# aws-cli/2.x.x Python/3.x.x ... が表示されればOK
```

未インストールの場合は[公式ドキュメント](https://docs.aws.amazon.com/ja_jp/cli/latest/userguide/getting-started-install.html)からインストールします。

### Step 2 — AWS 認証情報の設定

対話形式で以下を入力します。

```
AWS Access Key ID [None]: AKIA...（IAMのアクセスキーID）
AWS Secret Access Key [None]: ...（シークレットキー）
Default region name [None]: us-east-1
Default output format [None]: json
```

設定内容は `~/.aws/credentials`（キー）と `~/.aws/config`（リージョン等）に保存されます。

### Step 3 — 設定確認

```
aws sts get-caller-identity
```

以下のように UserId・Account・Arn が返れば認証成功です。

```
{
    "UserId": "AIDA...",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/your-username"
}
```

### Step 4 — Claude Code の Bedrock 接続を有効化

プロジェクトルートに `.env` ファイルを作成します。

```
CLAUDE_CODE_USE_BEDROCK=1
AWS_REGION=us-east-1
```

`.gitignore` への追記も忘れずに。

VSCode を使用している場合は `.vscode/launch.json` で `.env` を読み込む設定を追加します。

```
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Launch Program",
      "type": "node",
      "request": "launch",
      "program": "${workspaceFolder}/index.js",
      "envFile": "${workspaceFolder}/.env"
    }
  ]
}
```

環境変数の確認（Windows PowerShell）：

```
echo $env:CLAUDE_CODE_USE_BEDROCK  # → 1
echo $env:AWS_REGION               # → us-east-1
```

### Step 5 — Claude Code を起動

正常に起動し Bedrock への接続が確立されれば完了です。

---

## Part 2: Claude Desktop を AWS Gateway 経由で使う（Windows）

社内環境などで AWS Gateway + Workspace ID を経由して Claude Desktop を使う場合の手順です。

### Step 1 — 事前準備

管理者から以下を受け取ります。

| 項目 | 説明 |
| --- | --- |
| IAM アクセスキー ID | `AKIA...` で始まる文字列 |
| IAM シークレットアクセスキー | IAM 作成時にのみ表示される |
| Workspace ID | `wrkspc_xxxxxxxx` 形式 |
| リージョン | 例：`ap-northeast-1` |
| ヘルパースクリプト2ファイル | `.ps1` / `.cmd` |

### Step 2 — Python パッケージのインストール

```
pip install token-generator-for-aws-external-anthropic
```

動作確認：

```
python -c "from token_generator_for_aws_external_anthropic import TokenGenerator; print('ok')"
# ok と表示されればOK
```

### Step 3 — AWS プロファイルの設定

```
aws configure --profile a8i
```

```
AWS Access Key ID [None]: （管理者から受け取ったキー）
AWS Secret Access Key [None]: （管理者から受け取ったシークレット）
Default region name [None]: ap-northeast-1
Default output format [None]: json
```

確認：

```
aws configure list --profile a8i
# access_key の行に値が表示されればOK
```

### Step 4 — ヘルパースクリプトの配置と文字化け修正

#### フォルダを作成してファイルを配置

```
New-Item -ItemType Directory -Force -Path "C:\claude-helper"
```

配布された2ファイルを `C:\claude-helper\` にコピーします。

#### .cmd ファイルの修正

メモ帳で `C:\claude-helper\claude-aws-credential-helper.cmd` を開き、中身を以下に書き換えます。

```
@echo off
powershell.exe -ExecutionPolicy Bypass -File "C:\claude-helper\claude-aws-credential-helper.ps1"
```

#### .ps1 ファイルの修正

PowerShell で以下をそのまま貼り付けて実行します（スクリプトを正しい内容で上書きします）。

```
$content = @'
$ErrorActionPreference = "Stop"
$ProfileName = "a8i"
$Region      = "ap-northeast-1"
$export = aws configure export-credentials --profile $ProfileName --format powershell
Invoke-Expression ($export -join "`n")
python -c "from token_generator_for_aws_external_anthropic import TokenGenerator; print(TokenGenerator(region='$Region').get_token())"
'@
$content | Out-File -FilePath "C:\claude-helper\claude-aws-credential-helper.ps1" -Encoding UTF8
```

#### 動作確認

```
C:\claude-helper\claude-aws-credential-helper.cmd
```

`aws-external-anthropic-api-key-...` という長い文字列が表示されれば成功です。

### Step 5 — Claude Desktop の設定

#### Developer Mode を有効化

`Help → Troubleshooting → Enable Developer Mode`

#### Third-Party Inference の設定

`Developer → Configure Third-Party Inference` を開き、以下を設定します。

| 項目 | 値 |
| --- | --- |
| 接続（Connection） | **Gateway** を選択 |
| ゲートウェイ ベース URL | `https://aws-external-anthropic.ap-northeast-1.api.aws` |
| 認証情報の種類 | **ヘルパースクリプト** を選択 |
| ヘルパースクリプト | `C:\claude-helper\claude-aws-credential-helper.cmd` |
| TTL（秒） | `43200` |
| ゲートウェイ認証スキーム | `bearer` |

#### カスタム推論ヘッダーを追加

「＋ ヘッダーを追加」をクリックして以下を入力します。

| Header 名 | 値 |
| --- | --- |
| `anthropic-workspace-id` | `wrkspc_...`（管理者から受け取った Workspace ID） |

#### モデルを追加

以下の2つを追加します（上が既定モデル）。

```
claude-sonnet-4-6
claude-opus-4-7
```

Claude Desktop を再起動し、モデルピッカーで `claude-sonnet-4-6` を選択してメッセージが送受信できれば完了です。

---

## トラブルシューティング

| エラー / 症状 | 原因 | 対処 |
| --- | --- | --- |
| `aws: command not found` | AWS CLI 未インストール | AWS CLI v2 をインストール |
| `Unable to locate credentials` | 認証情報未設定 | `aws configure` を再実行 |
| `AccessDeniedException` | IAM 権限不足 | Bedrock 用ポリシーが付与されているか確認 |
| `Could not connect to the endpoint URL` | リージョン指定誤り | `AWS_REGION=us-east-1` を確認 |
| 文字化けエラーが出る | `.cmd` / `.ps1` が文字化け | Step 4 の修正手順を実施 |
| `aws: expected one argument` | `.ps1` の ProfileName が空 | Step 4 の `.ps1` 書き直し手順を実施 |
| `aws-external-anthropic-api-key-...` が出ない | プロファイル未設定 | Step 3 を再実施 |
| Claude Desktop が接続エラー | ヘルパースクリプトパス未設定 | 認証情報の種類で「ヘルパースクリプト」を選択し `.cmd` を指定 |

---

## まとめ

Claude Code と Claude Desktop、それぞれ Bedrock / AWS Gateway 経由で接続する手順をまとめました。

特にハマりやすいポイントは以下の3点でした。

1. `AWS_REGION` は `.env` に明示的に書く必要がある
2. ヘルパースクリプトの文字コードは ANSI で保存する
3. Claude Desktop の認証情報の種類は「ヘルパースクリプト」を選ぶ（「静的APIキー」ではない）

同じ環境を構築する方の参考になれば幸いです。
