---
id: "2026-03-22-備忘録claude-codeからラズパイに直接ssh接続して操作させる方法-01"
title: "【備忘録】Claude Codeからラズパイに直接SSH接続して操作させる方法"
url: "https://qiita.com/sk283/items/750d9ef502172cbbb5af"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-03-22"
date_collected: "2026-03-23"
summary_by: "auto-rss"
---

## はじめに

ラズパイの自宅サーバー構築をClaude（Webチャット版）と進めていたのですが、毎回「このコマンドを実行して」→「結果はこうでした」のやり取りが発生して、正直しんどかったです。

そこで**Claude Code**（ターミナル版のClaude）を導入し、SSHでラズパイに直接接続させることで、コマンド実行からエラー対応まで全部自動でやってもらえるようになりました。

この記事では、Claude CodeからラズパイにパスワードなしでSSH接続できるようにするまでの手順をまとめます。

## 前提環境

| 項目 | 内容 |
| --- | --- |
| 操作PC | Claude Codeが動いているマシン |
| ラズパイ | Raspberry Pi 3（Raspberry Pi OS / Debian bookworm） |
| ネットワーク | 同一LAN内（PCとラズパイが同じネットワークにいる） |

IPアドレスやユーザー名は環境に合わせて読み替えてください。この記事では以下を例として使います。

* ラズパイのローカルIP: `192.168.x.x`
* ラズパイのユーザー名: `myuser`

## なぜパスワードなしSSHが必要なのか

Claude Codeはターミナル上で動作し、`ssh`コマンドを実行できます。しかし、パスワード認証のままだと毎回パスワード入力を求められ、Claude Codeが自動で作業を進められません。

**SSH公開鍵認証**を設定すれば、パスワードなしでログインできるようになり、Claude Codeがラズパイ上でコマンドを自由に実行できるようになります。

## 手順

### 1. SSH鍵ペアを作成する（PC側）

操作PCのターミナルで以下を実行します。

```
ssh-keygen -t ed25519 -f ~/.ssh/id_raspi -N ""
```

| オプション | 意味 |
| --- | --- |
| `-t ed25519` | 鍵の種類。ed25519は現在推奨されているアルゴリズム |
| `-f ~/.ssh/id_raspi` | 鍵ファイルの保存先。名前は自由に変えてOK |
| `-N ""` | パスフレーズを空にする（Claude Codeが自動で使えるようにするため） |

これで2つのファイルが作られます。

* `~/.ssh/id_raspi` → 秘密鍵（**絶対に外部に公開しない**）
* `~/.ssh/id_raspi.pub` → 公開鍵（ラズパイに送るほう）

### 2. 公開鍵をラズパイに送る（PC側）

```
ssh-copy-id -i ~/.ssh/id_raspi.pub myuser@192.168.x.x
```

ここで**最後の1回だけ**ラズパイのパスワードを聞かれるので入力してください。これ以降はパスワード不要になります。

### 3. パスワードなしで接続できるか確認

```
ssh -i ~/.ssh/id_raspi myuser@192.168.x.x
```

パスワードを聞かれずにログインできれば成功です。

### 4. SSH設定ファイルで接続を簡略化する（PC側）

毎回IPアドレスと鍵ファイルを指定するのは面倒なので、`~/.ssh/config`に設定を書きます。

```
cat >> ~/.ssh/config << 'EOF'
Host raspi
    HostName 192.168.x.x
    User myuser
    IdentityFile ~/.ssh/id_raspi
EOF
```

これで以下だけでログインできるようになります。

### 5. CLAUDE.md を作成する

Claude Codeには**CLAUDE.md**という仕組みがあり、プロジェクトのルートディレクトリに置いておくと起動時に自動で読み込んでくれます。ここにサーバーの接続情報やプロジェクトの概要を書いておけば、毎回説明する必要がなくなります。

```
mkdir ~/my-server-project
cd ~/my-server-project
```

`CLAUDE.md` の例：

```
# サーバー構築プロジェクト
 
## サーバー接続情報
### Raspberry Pi
- SSH: `ssh raspi`（~/.ssh/config に設定済み）
 
## 作業ルール
- 設定変更前に必ずバックアップを取る（cp file file.bak）
- APIキーやシークレットをコミットしない
- ファイル編集後は所有者・パーミッションを変更しないこと
 
## やりたいこと
（ここにプロジェクトの概要を書く）
```

### 6. Claude Codeを起動して動作確認

```
cd ~/my-server-project
claude
```

Claude Codeが起動したら、試しにこう聞いてみましょう。

```
ラズパイに接続して、OSのバージョンとディスク使用量を確認して
```

Claude Codeが自動で `ssh raspi` → `cat /etc/os-release` → `df -h` のように実行してくれれば成功です。

## セキュリティ上の注意点

パスワードなしSSHは便利ですが、セキュリティ面で押さえておくべきポイントがあります。

### 秘密鍵の管理

* 秘密鍵（`~/.ssh/id_raspi`）は**絶対にGitにコミットしたり、他人に共有しない**
* パーミッションが正しいことを確認：

```
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_raspi
chmod 644 ~/.ssh/id_raspi.pub
```

### パスワード認証を無効化する（推奨）

公開鍵認証が動いたら、ラズパイ側でパスワードでのSSHログインを無効化しておくと安全です。

```
# ラズパイ側で実行
sudo nano /etc/ssh/sshd_config
```

以下の行を変更（または追加）：

```
PasswordAuthentication no
```

設定を反映：

```
sudo systemctl restart sshd
```

パスワード認証を無効化する前に、公開鍵でログインできることを**必ず確認**してください。ミスるとSSHで入れなくなります（その場合はモニターとキーボードを直接つないで復旧します）。

### ファイアウォールの設定（推奨）

```
# ラズパイ側で実行
sudo apt install ufw
sudo ufw allow ssh
sudo ufw enable
```

## よくあるトラブル

### `Permission denied (publickey)` と出る

鍵ファイルのパーミッションが間違っている可能性があります。

```
# PC側
chmod 600 ~/.ssh/id_raspi
 
# ラズパイ側
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### `ssh-copy-id` が使えない

手動で公開鍵をコピーすることもできます。

```
# PC側で公開鍵の中身を表示
cat ~/.ssh/id_raspi.pub
 
# ラズパイ側で authorized_keys に追記
mkdir -p ~/.ssh
echo "（↑の内容をペースト）" >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### `~/.ssh/config` を書いたのに `ssh raspi` で繋がらない

configファイルのパーミッションを確認してください。

## まとめ

1. **SSH公開鍵認証**を設定してパスワードなしログインを実現
2. **~/.ssh/config** で接続先をエイリアス化
3. **CLAUDE.md** にサーバー情報と作業ルールを記載
4. Claude Codeを起動すれば、あとは対話でラズパイを操作できる

Webチャット版のClaudeだと「コマンドを実行して」→「結果を貼り付けて」の往復が必要でしたが、Claude Code + SSH公開鍵認証の組み合わせで、指示を出すだけでラズパイの操作・設定変更・トラブルシューティングまで自動で進めてくれるようになりました。

サーバー構築のような「ターミナルでコマンドを打つ作業」との相性は抜群です。
