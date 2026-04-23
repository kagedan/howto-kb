---
id: "2026-04-02-ssh接続先のリモート開発サーバーでclaude-code-voiceを使うpulseaudio-n-01"
title: "SSH接続先のリモート開発サーバーでClaude Code /voiceを使う（PulseAudio null-sink方式）"
url: "https://zenn.dev/eight8/articles/0714b324a05726"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "VSCode", "zenn"]
date_published: "2026-04-02"
date_collected: "2026-04-03"
summary_by: "auto-rss"
---

# マイクがない

マイクがない。

正確には、マイクはある。目の前のWindowsに繋がったBluetoothイヤホンにマイクはついている。ただ、私が開発しているのはそのWindowsではなく、隣の部屋に置いてあるUbuntuサーバーだ。VSCode Remote SSHで繋いでいる。画面の向こうにいるサーバーには、マイクがない。

Claude Codeに `/voice` という機能がある。スペースキーを長押しすると声でコードの指示が出せる。キーボードを打つより圧倒的に楽で、一度使うと戻れなくなる類の快適さだった。以前、WSL2で開発していた頃に、PulseAudioの設定や音量調整と格闘した末にどうにか使えるようにした。

開発環境をリモートサーバーに移した。`/voice` が使えなくなった。

公式ドキュメントにはこう書いてある。「Voice dictation also needs local microphone access, so it does not work in remote environments such as Claude Code on the web or SSH sessions」。ローカルマイクが必要なので、Web版やSSHセッションなどのリモート環境では動きません。以上。

以上、と言われても困る。

# そもそもWSL2で動いていたのはなぜか

ところで、WSL2でなぜ `/voice` が動いていたのかを考えると、話が少しおかしくなる。

WSL2もリモート環境だ。Windows上の仮想Linuxであり、物理的にマイクが繋がっているわけではない。にもかかわらず動いていたのは、WSLgという仕組みがWindowsのマイクをRDP経由でWSL2内のPulseAudioに橋渡ししていたからだ。つまり `/voice` は「ローカルマイク」を見ているのではなく、「PulseAudioのソース」を見ている。

PulseAudioのソースさえ見えていれば、その向こう側に本物のマイクがあろうが架空のマイクがあろうが、`/voice` は気にしない。

ということは、リモートサーバーにPulseAudioを入れて、そこに何らかの方法でマイクの音声を届けてやれば、動くのではないか。

公式が「動かない」と言っているものを動かそうとしている。まあそういうことは嫌いではない。

# 手段を探す

方法を探した。WindowsのマイクをリモートのLinuxに届ける手段。PulseAudioのネットワーク転送、PipeWire、SSHトンネル、専用ツール。いくつか試したが、Windows側にPulseAudioサーバーが必要だったり、GitHubリポジトリが404だったり、そもそもマイク入力方向に対応していなかったりで、全滅した。なんでや。

ネットワーク越しの音声転送は、ほとんどが再生方向なのだ。「リモートの音楽をローカルのスピーカーで鳴らしたい」という需要は山ほどある。逆にマイクの音をわざわざ別のマシンに送りたがる人が、あまりいないらしい。

結局、WSL2を経由することにした。開発環境としてはもう使っていないが、音声の踏み台としてだけ働いてもらう。WindowsのマイクはWSLgが勝手にPulseAudioに見せてくれるから、あとはそのデータをネットワーク越しにサーバーに送ればいい。

# 水道工事

やることを整理すると、水道工事みたいな話になる。

WSL2側でマイクの音を録音して、ホースで送る。サーバー側でホースから受け取って、バケツに注ぐ。`/voice` がそのバケツを覗きに来て、音声が入っていれば文字に変換する。

バケツというのは、PulseAudioの「null-sink」だ。どこにもスピーカーが繋がっていない架空のスピーカー。ここに音声を流し込むと、PulseAudioのモニター機能で「このスピーカーに今こんな音が来てますよ」と横から覗ける。その覗き窓をデフォルトのマイクとして登録する。つまり `/voice` を騙している。マイクなど繋がっていないのに、音が来ているように見せかけている。

まず、サーバー側にPulseAudioを入れて、架空のスピーカーを作る。

```
# サーバー側：PulseAudioと関連ツールをインストール
sudo apt-get install -y pulseaudio pulseaudio-utils sox ncat
```

null-sinkの設定を永続化しておく。

```
# サーバー側：/etc/pulse/default.pa.d/remote-mic.pa を作成
sudo tee /etc/pulse/default.pa.d/remote-mic.pa << 'EOF'
load-module module-null-sink sink_name=remote_mic_sink sink_properties=device.description="Remote_Mic_Sink" format=s16le rate=44100 channels=1
set-default-source remote_mic_sink.monitor
EOF
```

PulseAudioを起動して、受信側を立ち上げる。

```
# サーバー側：PulseAudio起動 + 受信プロセス
pulseaudio --start
ncat --ssl -lk 8725 | pacat --playback --format=s16le --rate=44100 --channels=1 --raw --device=remote_mic_sink &
```

`ncat` がポート8725で待ち構えて、届いたデータを `pacat` が架空のスピーカーに流し込む。ホースの受け口からバケツに注ぐ部分だ。ポート番号は8725。8(バ) 7(ケ) 2(ツ) 5(GO) で「バケツGO」。7をケと読むのはさすがにしんどいが、この構成の本質がバケツに音声を注いで覗き見するという話なので、まあいいだろう。

WSL2側はもっと単純で、マイクの音を録音してサーバーに送るだけでいい。

```
# WSL2側：ncatが入っていなければインストール
sudo apt install -y ncat

# WSL2側：音量ブースト（毎回必要）
pactl set-source-volume @DEFAULT_SOURCE@ 150%

# WSL2側：マイク音声をサーバーに送信
parecord --format=s16le --rate=44100 --channels=1 --raw | ncat --ssl <サーバーのIP> 8725
```

これで水道工事は完了である。蛇口（parecord）からホース（ncat）を通って、受け口（ncat）からバケツに注ぐ人（pacat）が架空のスピーカー（null-sink）に流し込む。`/voice` はモニター越しに覗いて、「おっマイクに音来てるやん」と思う。

# 最初の失敗

ただ、ここに辿り着くまでにひとつ失敗している。

最初はnull-sinkではなく、FIFOパイプ（module-pipe-source）方式で実装した。ネットワークから受け取った音声をパイプファイルに書き込んで、PulseAudioにそれを読ませる構成だ。

音声は届いた。録音して確認すると、ちゃんと私の声が入っている。なのに `/voice` は「No speech detected」を返す。届いているのに、認識されない。

原因を調べてみると、パイプのバッファだった。`/voice` が録音していない間もデータはパイプに流れ続けて溜まる。スペースキーを押した瞬間、パイプの中には数秒前の古い音声が溜まっていて、そっちが先に読まれる。私がリアルタイムで喋っている声は、古いデータの後ろに並んでいる。

糸電話で話しかけたのに、相手に聞こえているのは3秒前の咳払いだった、みたいな状態だ。そりゃ認識されない。

null-sink方式に変えたのはそのためだ。PulseAudioに直接流し込めば、バッファの管理はPulseAudioが引き受ける。古いデータが溜まることもない。変えた瞬間、動いた。

# 補足

レートを44100Hzにしたのは、WSLgのマイク（RDPSource）がその周波数で動いているからだ。`/voice` 内部では16000Hzが使われるが、WSL2側でリサンプルするより、サーバー側のPulseAudioに任せた方が音質がいい。

音量を150%にブーストしているのは、WSLgのRDPSourceがデフォルトだと信じがたいほど音が小さいからだ。振幅を測ると0.03程度しかない。200%にするとクリッピングして音が割れる。150%がちょうどいい。ただし、この値は私の環境での話だ。マイクの種類やサウンドカードの特性で変わる可能性がある。そもそもブーストが不要な環境もあるかもしれない。`sox` で振幅を確認しながら、自分の環境に合った値を探してほしい。

転送にTCPを使っているのは、楽だったからだ。本来、音声のリアルタイムストリーミングにはUDPの方が向いている。ただ、同じLANの中ならTCPで遅延が問題になることはまずない。隣の部屋のサーバーに対してUDPの利点を語るのは、徒歩3分のコンビニにタクシーを呼ぶくらい大げさな話である。

# 永続化

このままだと、サーバーを再起動するたびに受信プロセスを手で立ち上げ直すことになる。WSL2側も同様で、音量ブーストも送信プロセスも再起動で消える。面倒だ。

サーバー側はsystemdのユーザーサービスにしてしまえばいい。systemdのサービスファイルは `/etc/systemd/system/` に置くものだと思っていたが、`~/.config/systemd/user/` に置けばユーザー権限で動くサービスが作れる。`sudo` もいらない。PulseAudioもユーザーセッションで動いているので、こちらのほうが都合がいい。

```
# ~/.config/systemd/user/voice-receiver.service
[Unit]
Description=Voice receiver for Claude Code /voice
After=pulseaudio.service

[Service]
ExecStart=/bin/bash -c 'ncat --ssl -lk 8725 | pacat --playback --format=s16le --rate=44100 --channels=1 --raw --device=remote_mic_sink'
Restart=always
RestartSec=1

[Install]
WantedBy=default.target
```

```
# サーバー側：サービスの有効化・起動
systemctl --user daemon-reload
systemctl --user enable --now voice-receiver.service
```

WSL2側も、systemdが有効なら同じ要領でサービス化できる。

```
# ~/.config/systemd/user/voice-sender.service
[Unit]
Description=Voice sender for Claude Code /voice
After=pulseaudio.service

[Service]
ExecStartPre=/bin/bash -c 'pactl set-source-volume @DEFAULT_SOURCE@ 150%%'
ExecStart=/bin/bash -c 'parecord --format=s16le --rate=44100 --channels=1 --raw | ncat --ssl <サーバーのIP> 8725'
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
```

```
# WSL2側：サービスの有効化・起動
systemctl --user daemon-reload
systemctl --user enable --now voice-sender.service
```

`ExecStartPre` で音量ブーストを済ませてから送信が始まる。WSL2のsystemdを有効にするには `/etc/wsl.conf` に `[boot]` セクションで `systemd=true` を書いておく必要がある。

ひとつ注意がある。`ncat` は `pacat` にパイプで繋がっているので、接続が一度切れるとパイプが壊れてプロセスごと死ぬ。WSL2を再起動した、ネットワークが一瞬切れた、そういうことで水道管が破裂する。`Restart=always` はそのための設定で、死んでも1秒後に立ち上がり直す。WSL2側も5秒後にリトライする。お互いが倒れても起き上がる仕組みにしておかないと、ある朝突然声が届かなくなって途方に暮れることになる。

これでどちらも再起動後に自動で立ち上がる。蛇口もホースもバケツも、毎朝勝手にセットされる。水道工事の永久保証である。

ただし、永久保証にも但し書きがある。

`/voice` が返すエラーは2種類ある。

「No audio detected from microphone. Check that the correct input device is selected and that Claude Code has microphone access.」は、そもそも音声データが届いていない。Windows（WSL2）を再起動した後に出やすい。サーバー側の `ncat` が前回のセッションの接続を掴んだまま、新しい接続をうまく処理できなくなっている。

「No speech detected.」は、音声データは届いているが音声として認識されない。音量不足か、接続が中途半端な状態になっている。

どちらの場合も、まずサーバー側のサービスを再起動すれば大抵は直る。

```
# サーバー側：受信サービスの再起動
systemctl --user restart voice-receiver.service
```

それでもダメなら、WSL2側も再起動する。

```
# WSL2側：送信サービスの再起動
systemctl --user restart voice-sender.service
```

音量ブーストが外れている可能性もある。WSL2側で確認して、150%になっていなければ戻す。

```
# WSL2側：音量確認
pactl get-source-volume @DEFAULT_SOURCE@
```

この再起動を毎回手で打つのも面倒なので、Claude Codeのスキルにしてしまった。`/voice-restart` と打てばサーバー側のサービスを再起動してくれる。音声入力が繋がらない時に、音声入力ではなくテキストで `/voice-restart` と打つ。なんとも間抜けな光景だが、実用上は助かっている。

根本的には `ncat` がパイプで `pacat` に繋がっている構成上、接続の切り替わりで壊れやすい。もっとスマートな方法があれば教えてほしい。

# セキュリティ

音声データがネットワークを平文で流れるのは、隣の部屋の話であっても今どき行儀が悪い。LAN内だから大丈夫、は、ハガキに書いても届くから封筒はいらない、と言っているようなものだ。`ncat` には `--ssl` オプションがあるので、送受信の両方につけておく。それだけで暗号化される。接続元を絞りたければ `--allow <IP>` も足せばいい。

---

全部できあがってから、他の人はどうやっているのか検索してみた。同じ問題にぶつかった人が、どんなアプローチで解決したのかを知りたかった。

見つからなかった。PulseAudioのネットワーク転送をやっている人はいる。null-sinkで仮想マイクを作っている人もいる。ただ「それを組み合わせてClaude Codeの `/voice` をSSH越しに動かす」という構成は、少なくとも検索で引っかかる範囲には出てこなかった。VoiceMode MCPのように `/voice` とは別の仕組みで音声対話を実現しているプロジェクトはあったが、`/voice` そのものをリモートで動かすという方向の記事は見当たらない。

技術的には何も高度なことはしていない。録音して、送って、受けて、流し込む。水道工事である。もっとスマートなやり方があるのかもしれないが、とりあえず通った水は飲めた。味はわからない。知らんけど。

# おわりに

この文章は、その音声入力で書いている。

別の部屋にあるサーバーのターミナルで `/voice` を起動し、スペースキーを押して喋る。声はBluetoothイヤホンのマイクからWindowsに入り、WSLgを通ってWSL2のPulseAudioに届き、`ncat` でSSL付きのTCPに乗って、LANを渡って、サーバーの `ncat` に届き、`pacat` がPulseAudioの架空のスピーカーに流し込み、そのモニターを `/voice` が覗いて、文字になる。

このどうかしている経路を、私の声は毎回律儀に辿っている。声が文字になるまでの遅延は、体感ではほとんどない。

マイクのないサーバーに、声が届いている。

公式には動かないはずの場所で、動いている。それだけのことだが、それだけのことが、なんだか妙に嬉しい。
