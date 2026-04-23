---
id: "2026-03-31-raspberry-piでclaude-codeを起動時に自動実行してdiscordボットとして常駐-01"
title: "Raspberry PiでClaude Codeを起動時に自動実行してDiscordボットとして常駐させる"
url: "https://qiita.com/supertask/items/ab017f78d75fb9a1f61b"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-03-31"
date_collected: "2026-03-31"
summary_by: "auto-rss"
---

## はじめに

Raspberry Pi を常時稼働サーバーとして使い、PC起動時に Claude Code を自動起動して Discord  
チャンネルに常駐させる方法を紹介します。

ターミナルウィンドウが画面上に表示されるので、Claude の動作状況をいつでも目視で確認できます。

### 環境

* Raspberry Pi 5 (aarch64)
* Debian 13 (trixie) / Raspberry Pi OS
* Claude Code 2.1.x
* デスクトップ環境 (Wayland / lxterminal)

## 前提条件

* Claude Code がインストール済みで `claude` コマンドが使えること
* Discord プラグインが設定済みであること
* デスクトップ環境が有効であること

## セットアップ手順

### 1. tmux のインストール

（必須ではありませんが、あると便利です）

```
sudo apt-get install -y tmux
```

### 2. Claude 実行スクリプトの作成

Claude Code を適切な環境変数付きで起動するスクリプトです。

**`~/.local/bin/claude-run.sh`**

```
#!/bin/bash
export HOME=/home/$USER
export PATH="$HOME/.bun/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export CLAUBBIT=1
exec claude --dangerously-skip-permissions --channels plugin:discord@claude-plugins-official
```

> **ポイント**: `CLAUBBIT=1` を設定することで、非対話環境で表示されるワークスペース信頼ダイアログをスキップできます。

```
chmod +x ~/.local/bin/claude-run.sh
```

### 3. 起動スクリプトの作成

デスクトップが準備できるまで待ってから、ターミナルウィンドウを開くスクリプトです。

**`~/.local/bin/claude-startup.sh`**

```
#!/bin/bash
# Claude startup script - runs at boot via systemd
# Opens a visible terminal window on the desktop
export HOME=/home/$USER
export PATH="$HOME/.bun/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export XDG_RUNTIME_DIR=/run/user/$(id -u)
export WAYLAND_DISPLAY=wayland-0
export DISPLAY=:0

# Wait for desktop to be ready
until [ -S "$XDG_RUNTIME_DIR/$WAYLAND_DISPLAY" ] || [ -S "/tmp/.X11-unix/X0" ]; do
    sleep 2
done
sleep 3

# Open a terminal window running Claude (--no-remote prevents fork)
exec lxterminal --no-remote --title="Claude Discord" -e ~/.local/bin/claude-run.sh
```

```
chmod +x ~/.local/bin/claude-startup.sh
```

> **解説**:
>
> * `until` ループでデスクトップ環境（Wayland または X11）が起動するまで待機します
> * `lxterminal --no-remote` でフォークせずにプロセスが維持されます（systemd が正しくプロセスを追跡するために必要）

### 4. systemd ユーザーサービスの作成

**`~/.config/systemd/user/claude-startup.service`**

```
[Unit]
Description=Claude Startup Service
After=network-online.target graphical-session.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=%h/.local/bin/claude-startup.sh
Restart=on-failure
RestartSec=30
Environment=HOME=%h

[Install]
WantedBy=default.target
```

### 5. Linger の有効化とサービスの起動

```
# ログインしていなくてもユーザーサービスが起動するようにする
sudo loginctl enable-linger $USER

# デーモンをリロードしてサービスを有効化・起動
systemctl --user daemon-reload
systemctl --user enable claude-startup.service
systemctl --user start claude-startup.service
```

## 動作確認

### サービスの状態を確認

```
systemctl --user status claude-startup.service
```

`Active: active (running)` と表示されれば成功です。

### 画面の確認

デスクトップに「Claude Discord」というタイトルのターミナルウィンドウが表示され、Claude Code  
が動作しているのが確認できます。

## よく使うコマンド

| 操作 | コマンド |
| --- | --- |
| サービス停止 | `systemctl --user stop claude-startup.service` |
| サービス起動 | `systemctl --user start claude-startup.service` |
| サービス再起動 | `systemctl --user restart claude-startup.service` |
| 状態確認 | `systemctl --user status claude-startup.service` |
| ログ確認 | `journalctl --user -u claude-startup.service -f` |
| 自動起動を無効化 | `systemctl --user disable claude-startup.service` |

## トラブルシューティング

### 信頼ダイアログが表示される

`claude-run.sh` に `export CLAUBBIT=1`  
が設定されているか確認してください。この環境変数がワークスペース信頼ダイアログをスキップします。

### ターミナルが表示されない

デスクトップ環境のディスプレイサーバーの種類を確認してください。

```
echo $XDG_SESSION_TYPE  # wayland or x11
echo $WAYLAND_DISPLAY   # wayland-0 など
```

Wayland の場合は `WAYLAND_DISPLAY`、X11 の場合は `DISPLAY` の値を `claude-startup.sh` に合わせて修正してください。

### サービスがすぐに終了する

`lxterminal` に `--no-remote` オプションが付いているか確認してください。これがないとプロセスがフォークして systemd  
がサービス終了と判断します。

### 別のターミナルエミュレータを使う場合

`lxterminal` 以外を使う場合は、`claude-startup.sh` の `exec` 行を変更してください。

```
# GNOME Terminal の場合
exec gnome-terminal --title="Claude Discord" -- ~/.local/bin/claude-run.sh

# xterm の場合
exec xterm -title "Claude Discord" -e ~/.local/bin/claude-run.sh
```

## おわりに

この設定により、Raspberry Pi の電源を入れるだけで Claude Code が自動的に Discord  
に接続し、ターミナルウィンドウで動作状況を確認できるようになります。常時稼働の AI アシスタントとして活用できます。
