---
id: "2026-05-22-macbookにubuntuをインストールして日本語入力できるようになるまで-01"
title: "MacBookにUbuntuをインストールして日本語入力できるようになるまで"
url: "https://qiita.com/kazukikudo/items/da58164ec797394c0598"
source: "qiita"
category: "ai-workflow"
tags: ["Python", "qiita"]
date_published: "2026-05-22"
date_collected: "2026-05-23"
summary_by: "auto-rss"
query: ""
---

# はじめに

10年前のMacBook Pro 2015（8GBメモリ）が手元に余っていました。Windows 10をインストールして予備機として使っていましたが、動作が重すぎて実用に耐えませんでした。そこでUbuntu Desktop 24.04 LTSをインストールしてみることにしました。

結果から言うと、**Ubuntuは10年前のMacBookでも驚くほど軽快に動作します。** 起動は速く、ブラウザやターミナルの操作もストレスがありません。Windows 10では動作がもたつき、ファンが回り続けていた同じマシンとは思えないほどです。古いMacBookの再活用にUbuntuは非常に良い選択肢だと感じました。

Ubuntuのインストール自体もスムーズに完了しました。しかし、そこからが思いのほか長い道のりでした。**日本語入力ができない。**

この記事では、MacBook Pro 2015のJISキーボード上でUbuntu 24.04の日本語入力を「macOSと同じように」使えるようにするまでの試行錯誤をまとめています。

> **この記事について：** 実際にUbuntu上のブラウザからClaudeチャットとやり取りしながら問題を解決しました。約50往復の会話を経て解決に至り、この記事自体もそのチャット履歴をもとにClaudeに作成させたものです。

# めざした状態

- **英数キー**を押したら英字モードになる
- **かなキー**を押したら日本語入力モード（ローマ字入力）になる

macOSでは当たり前のこの動作を、Ubuntuで再現したいと思いました。

# 最初の状態

- 英数キー・かなキーともに**効かない**
- タスクバーに言語切り替えリンクがあり、マウスでは切り替えられる
- 「en」を選ぶと英字モードになる（問題なし）
- 「ja」を選ぶと**全角カナ**が入力される（ローマ字入力にならない）

# 原因の要約

今回の問題は大きく分けて**4つの原因**が重なっていました。

## 原因1：Mozcが入力メソッドとして登録されていなかった

`ibus-mozc` パッケージはインストールされていましたが、iBusの入力メソッドリストに「日本語 - Mozc」が追加されていませんでした。そのため「ja」を選んでも、Mozcではなくxkbの日本語キーマップが使われ、全角カナしか入力できませんでした。

## 原因2：MacBookのJISキーボードのキーコードが韓国語キーとして認識される

MacBook JISキーボードの英数キー・かなキーは、Linuxでは以下のように認識されていました。

| キー | keycode（xev） | keysym |
|------|---------------|--------|
| 英数 | 131 | `Hangul_Hanja`（韓国語） |
| かな | 130 | `Hangul`（韓国語） |

日本語キーボードで期待される `Muhenkan`（無変換）/ `Henkan`（変換）ではなく、韓国語用のキーとして認識されるため、日本語IMEの切り替えに使えませんでした。

## 原因3：Wayland環境の制限

Ubuntu 24.04はデフォルトでWaylandセッションを使用します。Wayland環境では `xdotool` や `ibus engine` コマンドによる外部からの入力ソース切り替えがブロックされます。X11への切り替えが必要でした。

## 原因4：GNOMEに「固定切り替え」の仕組みがない

macOSのように「英数→必ず英語」「かな→必ず日本語」という固定切り替え（ワンショット切り替え）は、GNOMEの標準機能に存在しません。GNOMEの `switch-input-source` はトグル方式のみで、入力ソースが2つの場合、どちらのキーを押しても交互に切り替わるだけです。

# 解決策

## ステップ1：iBusにMozcを登録する

`ibus-setup` のGUIからは追加できなかったため、`gsettings` で直接登録しました。

```bash
gsettings set org.freedesktop.ibus.general preload-engines "['xkb:us::eng', 'mozc-jp']"
ibus write-cache
ibus restart
```

さらにGNOMEの入力ソースにMozcを追加しました。

```bash
gsettings set org.gnome.desktop.input-sources sources "[('xkb', 'jp'), ('ibus', 'mozc-jp')]"
```

## ステップ2：キーボードレイアウトをJIS配列にする

インストール時に英語キーボード配列（`us`）が設定されていたため、JIS配列に変更しました。

```bash
gsettings set org.gnome.desktop.input-sources sources "[('xkb', 'jp'), ('ibus', 'mozc-jp')]"
```

これにより、Shift+2 で `@` ではなく `"` が入力されるようになりました。

## ステップ3：WaylandからX11に切り替える

Wayland環境では外部からのキー送信や入力ソース切り替えが制限されるため、X11セッションに変更しました。

```bash
sudo sed -i 's/#WaylandEnable=false/WaylandEnable=false/' /etc/gdm3/custom.conf
sudo reboot
```

## ステップ4：英数・かなキーの固定切り替えスクリプトを作成する

GNOMEにはワンショット切り替えの仕組みがないため、Pythonスクリプトでキーイベントを監視し、固定切り替えを実現しました。

まず、デバイスファイルを読むために `input` グループに参加します。

```bash
sudo usermod -aG input $USER
# ログアウト→ログインが必要
```

必要なパッケージをインストールします。

```bash
sudo apt install python3-evdev xdotool -y
```

切り替えスクリプト `~/bin/ime-switch.py` を作成します。

```python
#!/usr/bin/env python3
import subprocess
import evdev
from evdev import ecodes

DEVICE = '/dev/input/event4'
KEY_EISU = 123   # 英数キー（evdevでのkeycode）
KEY_KANA = 122   # かなキー（evdevでのkeycode）

def get_current():
    result = subprocess.run(['ibus', 'engine'], capture_output=True, text=True)
    return result.stdout.strip()

def switch():
    subprocess.run(['xdotool', 'key', 'Super_L+space'], capture_output=True)

def main():
    dev = evdev.InputDevice(DEVICE)
    print(f"Listening on {dev.name}... (Ctrl+C to stop)")
    try:
        for event in dev.read_loop():
            if event.type == ecodes.EV_KEY and event.value == 1:
                if event.code == KEY_EISU:
                    cur = get_current()
                    if cur == 'mozc-jp':
                        switch()
                elif event.code == KEY_KANA:
                    cur = get_current()
                    if cur != 'mozc-jp':
                        switch()
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == '__main__':
    main()
```

**注意：** `DEVICE` のパスと `KEY_EISU` / `KEY_KANA` のコード値は環境によって異なります。以下のコマンドで確認できます。

```bash
# デバイスの特定
cat /proc/bus/input/devices | grep -B2 -A6 "Handlers"

# evdevでのキーコード確認（sudoなしで動く場合）
python3 -c "
import evdev
dev = evdev.InputDevice('/dev/input/event4')
for event in dev.read_loop():
    if event.type == 1 and event.value == 1:
        print(f'keycode={event.code}')
"
```

## ステップ5：ログイン時に自動起動する

```bash
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/ime-switch.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=IME Switch
Exec=python3 /home/kkudo/bin/ime-switch.py
Hidden=false
NoDisplay=true
X-GNOME-Autostart-enabled=true
EOF
```

## ステップ6：Mozc起動時にひらがなモードにする

デフォルトではMozcが「直接入力」モードで起動するため、`active_on_launch` を `True` に変更します。

```bash
sed -i 's/active_on_launch: False/active_on_launch: True/' ~/.config/mozc/ibus_config.textproto
ibus write-cache
ibus restart
```

# はまったポイント

## xevとevdevでキーコードが違う

`xev` で確認したキーコード（131/130）と、Pythonの `evdev` ライブラリで取得するキーコード（123/122）が異なっていました。スクリプトでは evdev のコードを使う必要があります。

## ibus-setup のGUIでMozcが表示されない

`ibus-mozc` パッケージがインストール済みでも、`ibus-setup` の入力メソッド追加画面に「日本語 - Mozc」が表示されないことがありました。`ibus write-cache` を実行しても解決せず、`gsettings` で直接登録する必要がありました。

## sudoで実行するとiBusに接続できない

キーボードデバイス（`/dev/input/event*`）の読み取りにはroot権限が必要ですが、`sudo` で実行すると `ibus engine` コマンドがユーザーセッションのD-Busに接続できません。解決策として、ユーザーを `input` グループに追加し、sudoなしでデバイスを読み取れるようにしました。

## xdotool key super+space が効かない

`xdotool key super+space` では切り替わりませんでしたが、`xdotool key Super_L+space` では切り替わりました。キーシンボル名の大文字・小文字の違いに注意が必要です。

## Wayland環境ではxdotoolが使えない

Ubuntu 24.04のデフォルトであるWayland環境では、`xdotool` によるキーイベント送信がセキュリティ上ブロックされます。今回はX11に切り替えることで解決しましたが、Wayland対応の入力切り替え方法は今後の課題です。

# エピソード：日本語入力できない状態でClaudeと会話する

今回の問題解決は、Ubuntu上のブラウザからClaudeチャットと会話しながら進めました。

ここで困ったのが、**日本語入力ができない状態でチャットしなければならない**ということです。序盤はローマ字でこんな会話をしていました。

> 「tasukubar ni demasen.」（タスクバーに出ません）

> 「demasenn.」（出ません）

> 「sukurinshot wo syutokusite haritutenaidesu. dosurebayoika?」（スクリーンショットを取得して貼り付けないです。どうすればよいか？）

Claudeは日本語が入力できない状況を理解し、ローマ字の入力をそのまま読み取って対応してくれました。

最終的に解決するまで、Claudeとのやり取りは**約50往復**にのぼりました。途中で何度も方針転換が必要になり、xmodmap → iBusホットキー → GNOMEキーバインド → gdbus → gsettings → xdotool → Pythonスクリプトと、さまざまなアプローチを試しては失敗し、最終的にevdev + xdotoolの組み合わせにたどり着きました。

# 結論：Ubuntuの日本語入力は本当に大変なのか？

**一般的なPC（Windows用キーボード）にUbuntuをインストールする場合、日本語入力の設定はほぼ自動で完了します。** インストール時に「日本語」を選べば、iBus + Mozcが自動設定され、「半角/全角」キーでそのまま日本語入力ができます。

今回大変だったのは、以下のMacBook特有の事情が重なったためです。

1. **MacBookのJISキーボード**の英数/かなキーがLinuxで韓国語キーとして認識される
2. **Wayland**が外部からの入力操作をブロックする
3. **GNOMEにワンショット切り替え機能がない**ため自作が必要

Ubuntuが難しいのではなく、**MacBook + Ubuntu の組み合わせが特殊**だった、というのが正直な感想です。

一方で、OS自体の動作は非常に軽快です。Windows 10では重くて使いものにならなかった10年前のMacBookが、Ubuntuなら快適に使えます。日本語入力の設定さえ乗り越えれば、古いMacBookの再活用として十分おすすめできます。

# 環境情報

| 項目 | 内容 |
|------|------|
| ハードウェア | MacBook Pro 2015（Retina, 15-inch） |
| メモリ | 8GB |
| OS | Ubuntu Desktop 24.04 LTS |
| デスクトップ | GNOME（X11セッション） |
| IME | iBus + Mozc 2.28 |
| キーボード | JIS配列（Apple Internal Keyboard） |
