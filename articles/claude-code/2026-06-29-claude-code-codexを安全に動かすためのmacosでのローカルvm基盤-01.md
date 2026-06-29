---
id: "2026-06-29-claude-code-codexを安全に動かすためのmacosでのローカルvm基盤-01"
title: "Claude Code / Codexを安全に動かすためのmacOSでのローカルVM基盤"
url: "https://zenn.dev/inventit/articles/secure-ai-agent-local-vm"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "Gemini", "zenn"]
date_published: "2026-06-29"
date_collected: "2026-06-30"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Code や Codex のような AI Agent を開発に使う機会が増えてきました。

コードの修正、コマンド実行、Terraform の確認、AWS CLI の操作などを自然言語で依頼できるのは便利です。一方で、AI Agent にローカルマシン上で自由にコマンドを実行させることには、それなりの怖さがあります。

たとえば、以下のようなものをそのまま触らせるのは避けたいです。

* ホスト macOS のホームディレクトリ全体
* 個人の `~/.aws`
* ホスト macOS 側の SSH 秘密鍵
* Terraform の `apply` 権限
* 開発者本人の権限で操作できる社内・クラウド環境

そこで、Claude Code / Codex などの AI Agent を安全に動かすために、macOS 上に Lima を使ったローカル VM 基盤を作りました。

リポジトリはこちらです。

<https://github.com/mtakahashi-ivi/agent-infra>

## 作ったもの

このプロジェクトでは、AI Agent 専用の Ubuntu VM を Lima で構築します。

主な特徴は以下です。

* macOS ホストと AI Agent の実行環境を分離する
* Agent が触れるファイルシステムを専用ワークスペースに限定する
* ホストの `~/.aws` を VM にマウントしない
* `mise` で VM 内の CLI ツールバージョンを管理する
* `./bin/setup` で VM 作成からツール導入まで自動化する
* `./bin/agent` で VM 内にログイン、またはコマンドを実行する
* `./bin/doctor` で環境の状態を診断する

利用方法はリポジトリの `README.md` を参照してください。

AI Agent を直接ホスト macOS 上で動かすのではなく、専用の VM に閉じ込めて使う構成です。

## なぜローカル VM に分離するのか

AI Agent は、開発者の代わりにコマンドを実行できます。

これは強力ですが、裏を返すと、開発者が持っている権限をそのまま AI Agent に渡すことにもなります。

たとえば、ホストのホームディレクトリ全体を見える状態にしておくと、Agent は意図せず以下にアクセスできてしまいます。

* 他プロジェクトのソースコード
* ローカルに置いた設定ファイル
* シェル履歴
* 認証情報
* 一時ファイル

また、ホストの `~/.aws` をそのまま共有すると、普段使っている AWS プロファイルを Agent も利用できてしまいます。

AI Agent を便利に使うためには、単にツールをインストールするだけでなく、「Agent がどこまで触ってよいか」を先に決めておく必要があります。

このプロジェクトでは、その境界を Lima VM と専用ワークスペースで作ることにしました。

## 全体構成

構成はシンプルです。

```
macOS Host
  ├── agent-infra repository
  ├── ~/agent-workspace/home        # VM にマウントする専用領域
  └── Lima VM: agent-infra
        ├── Ubuntu 24.04
        ├── Claude Code / Codex / Gemini CLI
        ├── AWS CLI
        ├── Terraform
        └── mise
```

ホストから VM に共有するのは、原則として `~/agent-workspace/home` だけです。

Agent の作業は、このディレクトリ配下で完結させます。リポジトリルートやホストのホームディレクトリ全体は直接マウントしません。

## Lima の設定

VM の定義は `lima.yaml` に書いています。

標準スペックは以下です。

```
vmType: "vz"

images:
  - location: "https://cloud-images.ubuntu.com/releases/24.04/release/ubuntu-24.04-server-cloudimg-arm64.img"
    arch: "aarch64"

cpus: 4
memory: "8GiB"
disk: "60GiB"
```

Apple Silicon Mac での利用を前提に、Ubuntu 24.04 の ARM64 イメージを使っています。

マウント設定では、AI Agent 専用のワークスペースだけを共有します。

```
mounts:
  - location: "~/agent-workspace/home"
    writable: true
```

この設計により、Agent がアクセスできるホスト側の範囲を限定できます。

## ツール管理には mise を使う

VM 内のツール管理には `mise` を使っています。

AI Agent 用の環境では、Node.js、AWS CLI、Terraform、tflint、terraform-docs、uv、yq など、さまざまな CLI が必要になります。

これらを都度手作業で入れると、開発者ごとにバージョンがずれます。また、VM を作り直したときの復旧も面倒です。

`mise` の詳しい使い方は以下を参照してください。

<https://zenn.dev/inventit/articles/mise-tool-version-management>

そこで、基本的な OS パッケージは Lima の provisioning で導入し、言語ランタイムや開発用 CLI は `mise` で管理する構成にしています。

`./bin/setup` では、VM 作成後に `mise` の設定を VM 内へ配置し、必要なツールをインストールします。

```
mkdir -p ~/.config/mise
cat <<'MISE_CONFIG' > ~/.config/mise/config.toml
# mise-config.toml の内容
MISE_CONFIG

mise install -y
```

これにより、VM を作り直しても同じツールセットを再現しやすくなります。

## Agent の作業ディレクトリを固定する

Lima には、ホスト側のカレントディレクトリに合わせて VM 内の作業ディレクトリを移動しようとする挙動があります。

通常の開発では便利ですが、AI Agent 用の隔離環境としては少し困ります。ホスト側の場所に引きずられるより、常に専用ワークスペースで作業してほしいためです。

そこで、`./bin/agent` というラッパーを用意しています。

```
./bin/agent
./bin/agent terraform plan
./bin/agent aws sts get-caller-identity
```

内部では `limactl shell` の `--workdir` に専用ワークスペースを指定しています。

```
run_in_vm() {
    if [ $# -eq 0 ]; then
        LIMA_SHELL_SET_WORKDIR=0 limactl shell --workdir "$C_AGENT_WORKSPACE" "$C_VM_NAME"
    else
        LIMA_SHELL_SET_WORKDIR=0 limactl shell --workdir "$C_AGENT_WORKSPACE" "$C_VM_NAME" bash -lc "$*"
    fi
}
```

これにより、Agent の作業開始地点を常に `~/agent-workspace/home` に揃えられます。

## AWS 認証情報はホストと共有しない

このプロジェクトでは、ホスト側の `~/.aws` を VM にマウントしません。

AWS 認証情報は VM 内で独立して設定します。

AI Agent に渡す AWS 権限は、開発者本人が普段使っている権限とは分けるべきです。

特に Terraform を扱う場合、Agent には基本的に読み取り権限を渡し、`terraform plan` までを担当させる方針にしています。`apply` は人間がレビューしたうえで実行する、という境界を置きます。

この考え方により、Agent がクラウド環境を誤って変更・削除するリスクを下げられます。

## Git の認証は VM 専用の SSH 鍵を使う

GitHub や Bitbucket へのアクセスでは、VM 専用の SSH 鍵を作成します。

`./bin/configure-git` を実行すると、VM 内で Git のユーザー名とメールアドレスを設定し、必要に応じて SSH 鍵を生成します。

生成する鍵は VM 内の `~/.ssh/id_ed25519_lima` です。

```
ssh-keygen -t ed25519 -N "" -f "$HOME/.ssh/id_ed25519_lima" -C "lima-agent-infra"
```

その後、表示された公開鍵を GitHub や Bitbucket に登録します。

ホスト macOS 側の SSH 秘密鍵をそのまま VM にコピーするのではなく、AI Agent 用 VM の鍵として分けることで、ホスト側の既存の SSH 設定と切り離せます。

AI Agent 専用のボットアカウントを用意できる場合は、そのアカウントにこの公開鍵を登録するのが理想です。初期検証では開発者アカウントに登録して使うこともできますが、その場合も「VM 用の鍵」として分けておくと、あとから無効化しやすくなります。

## 使ってみた感触

この構成にしてよかった点は、AI Agent に渡している範囲を説明しやすくなったことです。

「ホストの全部を触れる」のではなく、「この VM の、このワークスペースを触れる」と言えるようになります。

また、AWS 認証情報を VM 内で分離しているため、Agent 専用の権限を設計しやすくなりました。

Claude Code や Codex は便利ですが、便利さだけを見てホスト上で直接動かすと、あとから権限境界を整理するのが難しくなります。

最初に実行環境を分けておくことで、AI Agent を開発フローに組み込みやすくなります。

## まとめ

AI Agent を安全に使うには、プロンプトや運用ルールだけでなく、実行環境そのものの設計が重要です。

今回作った `agent-infra` では、Lima を使って macOS 上に専用の Ubuntu VM を作り、Claude Code / Codex などの AI Agent をその中で動かす構成にしました。

ポイントは以下です。

* AI Agent 専用の VM を作る
* ホストと共有するディレクトリを限定する
* ホストの `~/.aws` を共有しない
* VM 内のツールは `mise` で再現可能にする
* Agent の作業ディレクトリを専用ワークスペースに固定する
* AWS や Terraform の権限境界を明確にする

AI Agent を便利な開発者として使う前に、まず「どこまで触ってよいか」をインフラとして定義する。

このリポジトリは、そのための小さなローカル基盤です。
