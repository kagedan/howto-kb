---
id: "2026-04-16-cc-clipでリモートサーバーのclaude-codeに画像を直接ペーストできるようにする-01"
title: "cc-clipでリモートサーバーのClaude Codeに画像を直接ペーストできるようにする"
url: "https://zenn.dev/zaico/articles/45bffcd94b5c68"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-16"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

株式会社ZAICOでCTOをやっている [@fukata](https://x.com/fukata) です。

## はじめに

リモートサーバー上でClaude Codeを使っていると、画像を貼り付けたい場面がありませんか？ローカル環境であればCtrl+Vで済むところが、SSH越しだとそうはいきません。これまではGyazoなどの外部サービスを経由したり、一度サーバーに画像をアップロードする必要がありました。

[cc-clip](https://github.com/ShunmeiCho/cc-clip)を使えば、SSHトンネル経由でローカルのクリップボードをリモートに転送し、Ctrl+Vで画像を直接ペーストできるようになります。

筆者は自宅サーバーへの接続に[Tailscale](https://tailscale.com/)を使用しています。Tailscaleを使うとVPNの面倒な設定なしにプライベートネットワークを構築でき、`ssh dev`のようにホスト名で簡単にアクセスできます。

この記事では、Ubuntu Desktop環境からTailscale SSH経由でリモートサーバーに接続しているケースでのセットアップ方法を紹介します。

## 環境

| 項目 | 内容 |
| --- | --- |
| ローカル | Ubuntu Desktop |
| リモート | Ubuntu 24.04（自宅サーバー） |
| ターミナル | Ghostty |
| 接続方法 | Tailscale SSH（`ssh dev`） |

## セットアップ手順

### 1. cc-clipのインストール

ローカルマシンで以下を実行します。

```
curl -fsSL https://raw.githubusercontent.com/ShunmeiCho/cc-clip/main/scripts/install.sh | sh
```

`~/.local/bin`をPATHに追加して、インストールを確認します。

### 2. xclipのインストール

ローカルがUbuntu Desktopの場合、クリップボードツールとしてxclipが必要です。

```
sudo apt install -y xclip
```

### 3. デーモンの自動起動設定

`cc-clip setup`を実行する前に、ローカルでデーモンを起動しておく必要があります。これを忘れるとsetupが途中で止まります。

macOSやWindowsでは`cc-clip setup`が自動起動の設定まで行ってくれますが、Linuxでは自動起動が設定されません。手動で`cc-clip serve`を毎回実行するのは手間なので、systemdのユーザーサービスとして登録しておくのがおすすめです。

以下の内容で`~/.config/systemd/user/cc-clip.service`を作成します。

```
[Unit]
Description=cc-clip clipboard daemon
After=graphical-session.target

[Service]
Type=simple
ExecStart=%h/.local/bin/cc-clip serve --port 18339
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
```

サービスを有効化して起動します。

```
systemctl --user daemon-reload
systemctl --user enable --now cc-clip
```

起動状態を確認します。

```
systemctl --user status cc-clip
```

ログを確認したい場合は以下を実行します。

```
journalctl --user -u cc-clip -f
```

サービスが正常に起動していれば、`cc-clip status`でもデーモンの稼働を確認できます。

### 4. セットアップの実行

`~/.ssh/config`に定義されたホスト名を指定してsetupを実行します。

このコマンドが自動で以下を行います。

* SSHの`RemoteForward`設定
* リモートサーバーへのcc-clipとshim（xclipの代替スクリプト）のデプロイ
* トークンの生成と同期
* トンネルの確認

### 5. doctorで確認

setupが完了したら、必ずdoctorで全項目がpassしているか確認してください。

```
cc-clip doctor --host dev
```

全項目passであれば完了です。

```
Local checks:
  daemon:        [pass] running on :18339
  clipboard:     [pass] xclip available
  token:         [pass] present (64 chars)
  token-expiry:  [pass] token valid, expires in 29d23h

Remote checks:
  ssh:           [pass] connected to dev
  remote-bin:    [pass] cc-clip 0.5.0
  shim:          [pass] xclip shim installed
  path-order:    [pass]
  tunnel:        [pass] port 18339 forwarded
  remote-token:  [pass] token file present
  token-match:   [pass] remote token matches local
  deploy-state:  [pass] deploy.json present and valid
  path-fix:      [pass] PATH marker present in shell rc file

All checks passed. cc-clip is ready.
```

### 6. 使ってみる

SSHでリモートサーバーに接続し、Claude Codeを起動します。ローカルでクリップボードに画像をコピーした状態でCtrl+Vを押せば、画像が直接ペーストされます。

## ハマりポイント

### デーモンを先に起動しておく

`cc-clip setup`はローカルのデーモンが起動していることを前提にしています。デーモンが起動していない状態でsetupを実行すると、ステップ3で止まります。

```
[3/4] Starting local daemon...
      daemon not running. Start it first: cc-clip serve
```

先に`cc-clip serve`を実行してから再度setupを行ってください。

### xclipが必要

Ubuntu Desktopの場合、xclipがインストールされていないとdoctorのclipboardチェックがFAILします。`sudo apt install -y xclip`でインストールしてください。

### SSHの再接続が必要な場合がある

setupがSSHの`RemoteForward`設定を`~/.ssh/config`に書き込みますが、setup実行時に既存のSSHセッションが張られていると、そのセッションにはRemoteForwardが反映されません。doctorでtunnelがFAILする場合は、SSHセッションを一度切断して再接続してください。

## Tailscale SSHについて

Tailscale SSHを使っている場合、通常の`ssh dev`コマンドで接続していれば問題ありません。`~/.ssh/config`の設定（RemoteForwardなど）が適用されます。

ただし`tailscale ssh dev`コマンドで接続している場合は、`~/.ssh/config`が無視されるためRemoteForwardが効きません。通常の`ssh`コマンドを使ってください。

## まとめ

リモートサーバーでClaude Codeを動かしていて、画像を貼り付ける場面がある方はぜひcc-clipを試してみてください。Gyazoや手動アップロードの手間がなくなり、Ctrl+V一発で画像をペーストできるようになります。

なお、今回のセットアップ作業自体、ローカルのClaude Code上で行いました。cc-clipのリポジトリのREADMEを読んでもらい、インストールコマンドの実行からdoctorでの確認まで、ほとんどClaude Codeが自動で進めてくれました。セットアップに不安がある方は、Claude Codeに「cc-clipをセットアップして」とお願いしてみるのもおすすめです。

セットアップ後は`cc-clip doctor --host <ホスト名>`で動作確認をお忘れなく。
