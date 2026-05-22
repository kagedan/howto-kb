---
id: "2026-05-21-fnoxの紹介-secretをaiに読ませずに管理する-01"
title: "fnoxの紹介 - SecretをAIに読ませずに管理する"
url: "https://zenn.dev/kazto/articles/6da1885e1c3934"
source: "zenn"
category: "ai-workflow"
tags: ["API", "zenn"]
date_published: "2026-05-21"
date_collected: "2026-05-22"
summary_by: "auto-rss"
query: ""
---

# fnoxとは

[fnox](https://fnox.jdx.dev/) とは、[mise](https://mise.jdx.dev/) を作成した [@jdxさん](https://github.com/jdx) のプロダクトのひとつです。  
データソースから秘密情報を読み出し、サブプロセスへ環境変数として提供します。

よくある `.env` は平文でAPIKeyなどを記載してあり、AIエージェントに読み込ませると誤って流出してしまう危険性がありました。

fnox の特徴としては、暗号化バックエンドやクラウドのキーストレージと連携して、安全に秘密情報をサブプロセスに渡すことが可能となっています。

## インストール

さすがmiseの作者のプロダクトだけあって、miseで簡単にインストールできます。

```
$ mise install fnox@latest
$ mise use -g fnox@latest
```

Rust開発環境がインストールされているのであれば、cargo経由でもインストール可能です。

<https://fnox.jdx.dev/guide/installation.html>

## 暗号化バックエンド age について

個人で使用する範囲では、暗号化ツール [age](https://github.com/filosottile/age) をインストールしておくと便利です。

fnox はデフォルトでageによる暗号化に対応しています。

Debian/Ubuntu系であればaptコマンドでインストール可能です。

MacのHomebrewを使用してもインストールできます。

### (初回のみ) age セットアップ

age の秘密鍵を作ります。

```
$ age-keygen -o ~/.config/fnox/age.txt
Public key: ageXXXXXXXX....
```

age.txtには公開鍵・秘密鍵が記載されています。

上記の公開鍵をコピペできるように別途保存しておきます。

### (初回のみ) fnox.toml の作成

上記で表示された公開鍵を `fnox.toml` に記載します。

`fnox init -g` でglobal(ユーザごと)の設定ファイルを作成します。  
-gオプションなしの `fnox init` では、プロジェクトごとの設定ファイルを作成できます。  
このファイルに暗号化された秘密情報が保存されます。

* global
  + `~/.config/fnox/config.toml`
* project
  + `path/to/project/fnox.toml`

どのプロバイダを使うかを選択できます。

* ローカル保存
* 1Passwordなどのパスワードマネージャ
* AWS KMSなどのクラウドKMS
* AWS Secrets Managerなどのクラウド
* macOSのKeychainなどのOS Keychain

本記事では触れませんが、クラウドのSecrets Managerと連携できるので商用プロダクトでの秘密情報のチーム内での共有にも便利かと思います。

以下の例ではローカル保存を選択します。

次に、暗号化プロバイダを選択します。

* Age による暗号化
* FIDO2
* KeePass
* GPG による暗号化
* 暗号化なしの平文
* YubiKey

ここではAge暗号化を選択します。

次に、先ほど作成した `age.txt` の公開鍵を登録します。

このあと、サンプルの秘密情報を登録するか聞かれますが、ここはどちらでもかまいません。  
試しに `foo=bar` みたいなシークレットを登録してみて、どのように暗号化されるか見てるとおもしろいです。

できあがった fnox.toml は、以下のようになっています。

```
default_provider = "age"

[providers.age]
type = "age"
recipients = ["ageXXXXXXXX..."]
```

### 秘密情報の登録

```
# 引数で指定
$ fnox set MY_SECRET secretXXXXXXXXX....

# インタラクティブ
$ fnox set MY_SECRET

# globalに保存
$ fnox set -g MY_SECRET secretXXXXXXXXX....
```

### 秘密情報を取得する

登録した秘密情報を取得します。

```
$ fnox exec -- npm run dev
or
$ fnox exec -- bash migrate-database.sh
or
$ fnox exec -- sh -c 'echo $MY_SECRET'
```

サブシェルに対して環境変数を注入するので、以下のやり方だと何も表示されないことに注意してください。

```
# 以下はなにも表示されません
$ fnox exec -- echo $MY_SECRET
```

# AIに平文の秘密情報を読ませない

通常、`.env` ファイルは平文で秘密情報を記載してあります。これをそのままAIエージェントに読ませると、以下のようなパターンで漏洩が発生してしまう恐れがあります。

* `git add .` で .env ファイルをコミット、気づかずにGitHubにpushしてしまう
* 悪意あるプロンプトを意図せず読ませてしまい、外部に送信される
* AIエージェントが開発の中で秘密情報をハードコードしてしまう

などなど。

そこで fnox を使って暗号化した上で保存することで、読み取られるリスクを低減することができます。

## 事例

たとえば、プロジェクトルートに秘密情報を登録してみます。

```
$ fnox init

🔐 Welcome to fnox setup wizard!

This will help you configure your first secret provider.

Would you like to set up a provider now? Yes
What type of provider do you want to use? Local (easy to start)
Select provider: Age encryption

Age uses public/private key pairs for encryption.
Generate a key with: age-keygen -o ~/.config/fnox/age.txt

Age public key (recipient):
Age public key (recipient): age1yurvyr3ym2zyzskmtc4cwxket3htc9qk6dzf6cw3nuywmkh00vaq2348gd
Provider name:
Provider name: age

🔍 Testing provider connection...
✓ Provider connection successful!

Would you like to add an example secret? No

✓ Created new fnox configuration at 'fnox.toml'

Next steps:
  • Add secrets: fnox set MY_SECRET <value>
  • List secrets: fnox list
  • Use in commands: fnox exec -- <command>
```

公開鍵を上記に記載してしまっていますが、秘密鍵がない限り問題ありません。

```
$ fnox set MY_SECRET (ひみつ)
✓ Set secret MY_SECRET

$ cat fnox.toml
default_provider = "age"

[providers.age]
type = "age"
recipients = ["age1yurvyr3ym2zyzskmtc4cwxket3htc9qk6dzf6cw3nuywmkh00vaq2348gd"]

[secrets]
MY_SECRET= { provider = "age", value = "YWdlLWVuY3J5cHRpb24ub3JnL3YxCi0+IFgyNTUxOSBjemFWK0llNXpTNTl0WFNveUVmK0VadERMZGdzdVZIbFNQM0Fna2x0NDBFCkp5VXpEa0QyVUVjaHljN2RWWHhTK0Y3Zy93NWFtSG91RVZJWkZnMyszVmsKLT4gL2tqaUJ8LWdyZWFzZSB7NFYgWXgnbSBTMHcKUFIwCi0tLSBiNmQ2ajgxeTJneTNhM05LR1ZnVFlYTGtjUUUxblFQS3lVQmpNVnRVUFBRCpXrKbHOu1LTgLD+q9MJY+G8YWMMRUGSBtYOlAX5iUvldRct72pygaqU", description = "foo" }
```

同様に暗号化されたデータを公開しても、やはり秘密鍵がない限り復号できません。  
仮にAIエージェントが `fnox.toml` を外部に送信してしまってもその内容までは取得できません。

これを実際使う場合に、以下のように使用します。

```
$ fnox exec -- sh -c 'echo $MY_SECRET'
(ひみつ)
```

# まとめ

秘密情報を環境変数に注入するツールとしてはdotenvxなどがありますが、AWSやAzureなどにも対応しているところがfnoxの利点かと思います。
