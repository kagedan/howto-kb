---
id: "2026-05-29-mfa-と企業プロキシ環境でno-mcp-servers-configured-failedを踏み抜-01"
title: "MFA と企業プロキシ環境で「No MCP servers configured / failed」を踏み抜いた話"
url: "https://zenn.dev/jins/articles/93791476756f87"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "Python", "zenn"]
date_published: "2026-05-29"
date_collected: "2026-05-30"
summary_by: "auto-rss"
query: ""
---

## はじめに

CLI上で動くAIエージェントの「Claude Code」がとても人気ですね。MCP(Model Context Protocol)を通してAWSに接続できるようになり、Claude Codeの可能性が広がっています(AWS MCP Server)。そこで、「よし、社内のAWS環境にも繋いでみるか」と思って、`mcp-proxy-for-aws` を導入したところ、

* AssumeRole + MFA 必須の AWS 環境
* SSL インスペクション付きの企業プロキシ（VPN / Zscaler 等）

というエンタープライズあるある構成と見事に衝突し、

* 「No MCP servers configured」
* `/mcp` 上で MCP が ✘ failed
* しかもエラー詳細が見えない

という状態にしばらくハマりました。。

<https://github.com/aws/mcp-proxy-for-aws>

この記事では、最終的に **「Claude Code 2.x + mcp-proxy-for-aws を、AssumeRole + MFA + 企業プロキシ環境で安定稼働させるまで」** にやったことを、ほぼ時系列でまとめます。

## 前提環境

* OS
* Claude Code
* 基盤モデル
  + Amazon Bedrock経由で、Anthropicモデルを使用
* MCP 関連
  + `uvx` (`uv` ベースの Python ランチャー)
  + `mcp-proxy-for-aws`（AWS 公式 MCP プロキシ）
* AWS 側
  + `~/.aws/config` で「IAM ユーザー → AssumeRole (SwitchRole)」構成
  + すべてのロール Assume に MFA 必須
* ネットワーク
  + 企業 VPN / セキュリティプロキシ
  + SSL インスペクションあり（独自 CA 証明書を配布）

## 最初に踏んだ落とし穴：`No MCP servers configured`

まず、公式ドキュメントなどを参考にして、グローバル設定や `.mcp.json` を用意しましたが、Claude のチャットで `/mcp` を実行すると、こう出ます。

```
/mcp   ⎿ No MCP servers configured. Please run /doctor if this is unexpected.
```

一見すると「設定が読まれていない」のか「JSON が壊れている」のか分かりません。

## やったこと

* ホームディレクトリ側

  + `~/.claude/config.json` を作成し `mcpServers` を定義
* プロジェクト側

  + 作業ディレクトリ直下に `.mcp.json` を作成
  + Claude 起動時に `--mcp-config="./.mcp.json"` を指定

ポイントは、**Claude 2.x 系では `.mcp.json` と `--mcp-config` を組み合わせると挙動が安定しやすい**という点でした。  
手元の環境では、グローバルの `~/.claude/config.json` のみだと、プロジェクト設定やバージョンの違いによって期待どおり読まれないように見受けられました。

## 最終的な `.mcp.json`（最小構成）

まずは、トラブルシュート対応として、Sandbox用のMCPを1個だけに絞りました。

```
{
  "mcpServers": {
    "aws-sandbox-bedrock": {
      "type": "stdio",
      "command": "/Users/username/.local/bin/uvx",
      "args": [
        "mcp-proxy-for-aws@latest",
        "https://aws-mcp.us-east-1.api.aws/mcp",
        "--profile",
        "sandbox-SwitchRoleForBedrock-Group",
        "--metadata",
        "AWS_REGION=ap-northeast-1"
      ]
    }
  }
}
```

ここで重要だったポイントは 3 つあります。

1. `type` は `stdio` にする  
   → `mcp-proxy-for-aws` はローカルプロセスとして起動するので、`stdio` で問題なし。
2. `command` は `uvx` の **フルパス**  
   → 自分の環境では `which uvx` の結果が `/Users/username/.local/bin/uvx` だったため、それをそのまま書きました。  
   → `command: "uvx"` のままだと、Claude の内部 PATH に `uvx` が入っておらず `ENOENT` で落ちるケースがあります。
3. `--profile` は CLI で動作確認済みのプロファイル名  
   → 事前に `AWS_PROFILE=sandbox-SwitchRoleForBedrock-Group aws sts get-caller-identity` が成功する状態まで整えておきます。

そのうえで、プロジェクトディレクトリで Claude を起動します。

```
cd ~/DevelopmentSpace/claudecode_work  &&
claude --mcp-config="./.mcp.json"
```

この時点で `/mcp` を実行すると、**MCP 自体は 1 個認識される**ようになりました。

```
/mcp   Manage MCP servers  1 server     Built-in MCPs (always available)    aws-sandbox-bedrock · ✘ failed
```

次の問題は「なぜ `failed` なのか」です。

## `✘ failed` の正体を掘る：`--debug` とログファイル

Claude Code 2.x の場合、`--debug` オプションを付けると、詳細なログをファイルに書き出してくれます。

```
claude --debug --mcp-config="./.mcp.json"
```

起動直後に、だいたいこんな表示が出ます。

```
Debug mode enabled Logging to: /Users/username/.claude/debug/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.txt
```

このログファイルを `sed` などで眺めると、MCP の起動エラーの詳細が分かります。

```
cat ~/.claude/debug/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.txt | sed -n '120,220p'
```

私のケースでは、最初はこんなエラーが出ていました。

```
botocore.exceptions.InvalidConfigError: The source profile "username@example.com" must have credentials. MCP server "aws-sandbox-bedrock": Connection failed: MCP error -32602: Invalid request parameters
```

## 原因1：`source_profile` にクレデンシャルがない

まず、`~/.aws/config` の設定はあり、ベースとなるIAMユーザーの認証情報を使い、MFA(多要素認証)を経て特定のロール(Sandbox環境のBedrock用ロール)に切り替え(AssumeRoleする)、標準の接続先として東京リージョンを利用する形の設定はしています。ただ、アクセスキーを使わずにAWS認証できる`aws login` を使用していたのですが、ここで詰まりました。

<https://aws.amazon.com/jp/blogs/news/simplified-developer-access-to-aws-with-aws-login/>

この状態では、`username@example.com` プロファイルにアクセスキー / SSO 設定が何もないため、`mcp-proxy-for-aws`（内部的には boto3/botocore）が `InvalidConfigError` を投げていました。いずれは、`aws login`での認証もサポートされると思いますが、今回はアクセスキーを用います。

## 対応：`~/.aws/credentials` にベースクレデンシャルを定義

とりあえずはトラブルシュートが目的のため、`~/.aws/credentials` を作成し、ベースとなる IAM ユーザーのアクセスキーを設定しました。

```
[username@example.com] aws_access_key_id = AKIAxxxxxxxxxxxxxxxx aws_secret_access_key = xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

そのうえで、CLI側でプロファイルチェーンが動くか確かめます。

```
AWS_PROFILE=username@example.com
aws sts get-caller-identity
# 結果を確認

AWS_PROFILE=sandbox-SwitchRoleForBedrock-Group
aws sts get-caller-identity
# 結果を確認
```

ここまで通るようになれば、`mcp-proxy-for-aws` も同じプロファイル構成でクレデンシャルを解決できるはずです。

## Claude側のUX問題：MFAプロンプトが見えづらい！

ベースクレデンシャル問題を解決したあと、Claude を起動すると、毎回こういう表示になります。

```
Enter MFA code for arn:aws:iam::444455556666:mfa/username@example.com:
```

ここで少しハマったのが、**カーソルや入力が一切表示されない**ことです。  
通常の CLI で `aws sts get-caller-identity` を叩いたときのMFAプロンプトと違い、「入力を受け付けているのかどうか分からない」状態に見えてしまいます。

結論から言うと、

* その行にフォーカスは来ている
* 6 桁の MFA コードをそのまま打って Enter すればよい
* 入力中の数字は画面に表示されない（パスワード扱い）

というだけでした。しかし、MFAコードを入れて数秒待ち、Claude のプロンプトに戻り、その後 `/mcp` を実行すると、以下が表示されます。なぜだ。。

```
/mcp   Manage MCP servers  1 server     Built-in MCPs (always available)    aws-sandbox-bedrock · ✘ failed
```

## 事前に STS しても意味がない

ここで一度、次のような zsh 関数も試しました。

```
function claude-aws() {
  AWS_PROFILE=sandbox-SwitchRoleForBedrock-Group \
    aws sts get-caller-identity
    
  cd ~/DevelopmentSpace/claudecode_work && \
    claude --mcp-config="./.mcp.json"
}
```

意図としては「先にCLIでMFAを済ませてSTSセッションを作ってから、Claude を起動したい」というものです。  
しかし、実際には Claude 起動後に再度 MFA を求められました。

これは、

* `aws sts` は「プロセス A」
* `mcp-proxy-for-aws` は「プロセス B」

として、それぞれが独立に `~/.aws/config` / `~/.aws/credentials` を読んで STS するため、A で張ったセッションが B に共有されないためです。

加えて、`mcp-proxy-for-aws` の内部で動いている Python の AWS SDK（boto3）は、`~/.aws/config` に `mfa_serial` の記述を見つけると、自前で標準入力（stdin）から MFA コードを要求して AssumeRole し直そうとします。  
Claude Code はこの標準入力を裏の MCP プロセスにそのまま繋いでいるため、結果として「事前に CLI で STS を叩いても、MCP 側で再度プロンプトが出てしまう」という構造になっていました。つまり、**事前にSTSを叩いても、MCP側のMFAプロンプトを消すことはできない** 構造のようです。

## とりあえずの割り切り

`.mcp.json` は sandbox 用 MCP 1 個だけにしておき、「1 セッション = 1 アカウント」の単位で使う形で、このまま進めます。本当は、AWSをマルチアカウント運用しているので、それに最適化された手順にしたいのですが、それは後で再検討します。

## 次に踏んだ落とし穴は、企業プロキシの SSL インスペクションによる `CERTIFICATE_VERIFY_FAILED`

MFAとプロファイル周りが整った後も `✘ failed` が続きます。

その場合、`--debug`ログや `/bin/sh` ラップでMCPプロセスの`stderr`を拾うと、こんなエラーが出ます。

```
httpx.ConnectError: [SSL: CERTIFICATE_VERIFY_FAILED]   certificate verify failed: self-signed certificate in certificate chain (_ssl.c:1017)
```

## 原因

* 社内のプロキシ / VPNがSSLインスペクションを行っている。
* ブラウザやAWS CLIは、macOS のキーチェーン(System keychain)を見に行くため、社内CA を信頼して動作する。
* しかし `mcp-proxy-for-aws` が内部で利用している `httpx` は、システムキーチェーンを見ず、独自の CA バンドルだけを信用する。 → 結果的に、社内 CA が「怪しい自己署名証明書」として拒否される。

## 対応：macOS キーチェーンからCAをPEM化して`SSL_CERT_FILE`で渡す

macOSの`security`コマンドを使って、システムキーチェーンに入っている証明書をPEMに書き出し、`SSL_CERT_FILE` で `httpx` に読ませます。

## 1. PEM ファイルの作成

```
# システムキーチェーンから証明書を抽出
security find-certificate -a -p /Library/Keychains/System.keychain \
  > ~/.mcp_certs.pem

# Apple 標準ルート証明書も追記
security find-certificate -a -p /System/Library/Keychains/SystemRootCertificates.keychain \
  >> ~/.mcp_certs.pem
```

## 2. `.mcp.json` で `SSL_CERT_FILE` を指定

```
{
  "mcpServers": {
    "aws-sandbox-bedrock": {
      "type": "stdio",
      "command": "/Users/username/.local/bin/uvx",
      "args": [
        "mcp-proxy-for-aws@latest",
        "https://aws-mcp.us-east-1.api.aws/mcp",
        "--profile",
        "sandbox-SwitchRoleForBedrock-Group",
        "--metadata",
        "AWS_REGION=ap-northeast-1"
      ],
      "env": {
        "SSL_CERT_FILE": "/Users/username/.mcp_certs.pem"
      }
    }
  }
}
```

`SSL_CERT_FILE` は Python / `httpx` が見る標準的な環境変数なので、この設定で社内CAも信頼されるようになります。再度 Claude を起動して MFA を入れ、`/mcp` を実行すると、今度は `✔ connected` になりました！！

## おまけ：`/bin/sh` ラップで stderr を拾うデバッグ方法

MCP（特に `stdio`）の厄介な点は、「起動エラーが ClaudeのUIに出ない」ことです。  
`--debug` だけでは見えない場合、`.mcp.json` でいったん `/bin/sh` を挟んで stderr をファイルに落とすと、原因切り分けがしやすくなりました。

```
{
  "mcpServers": {
    "aws-sandbox-bedrock": {
      "type": "stdio",
      "command": "/bin/sh",
      "args": [
        "-c",
        "/Users/username/.local/bin/uvx mcp-proxy-for-aws@latest https://aws-mcp.us-east-1.api.aws/mcp --profile sandbox-SwitchRoleForBedrock-Group --metadata AWS_REGION=ap-northeast-1 2> /tmp/mcp-error.log"
      ]
    }
  }
}
```

* Claude 起動 → `/mcp` → `✘ failed` のタイミングで `/tmp/mcp-error.log` を確認。
* 原因が分かったら、`command` を元の `uvx` に戻す。

## まとめ

今回の構成（Claude Code + AWS MCP + AssumeRole + MFA + 企業プロキシ）でハマったポイントを整理すると、だいたい次のようになります。

1. **MCP 設定が読まれない問題**  
   → プロジェクト直下に `.mcp.json` を置き、Claude 起動時に `--mcp-config="./.mcp.json"` を明示する。
2. **`uvx` が見つからない / `ENOENT` 問題**  
   → `which uvx` でフルパスを確認し、`.mcp.json` の `command` に絶対パスを書く。
3. **`botocore.exceptions.InvalidConfigError: source profile ... must have credentials`**  
   → `~/.aws/credentials` に `source_profile` 用のベースクレデンシャルを定義し、`aws sts get-caller-identity` が通るところまで整える。
4. **Claude TUI内の MFA プロンプトが見えづらい問題**  
   → 起動直後の `Enter MFA code ...` で、数字はエコーされないが入力自体は受け付けていると理解し、6 桁＋Enter を 1 回だけ入れる運用に割り切る。  
   → `.mcp.json` を 1 アカウントだけにしておくと、1 セッション 1 回の MFA に抑えられる。
5. **企業プロキシ（SSL インスペクション）による `CERTIFICATE_VERIFY_FAILED`**  
   → `security find-certificate` で macOS のキーチェーンからCAをPEM化し、`SSL_CERT_FILE` で `mcp-proxy-for-aws`（内部の `httpx`）に渡す。
6. **エラーが UI に出ない問題**  
   → 一時的に `/bin/sh` で MCP コマンドをラップし、stderr をファイルにリダイレクトして中身を見る。

特に、

* `.mcp.json` の場所と起動オプションの関係
* IAM プロファイルチェーン（`source_profile` / `role_arn` / `mfa_serial`）
* 企業プロキシと `SSL_CERT_FILE`

あたりは、Claude Code に限らず「Python ベースの CLI と企業ネットワークがぶつかるときの典型的なハマりどころ」だと思います。この記事はあくまで検証用であり、本番/組織標準には各社ポリシー準拠する形で運用するようにしてください。同じように、MFA と企業プロキシの狭間で MCP が `failed` になって困っている方の参考になれば幸いです。
