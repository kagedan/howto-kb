---
id: "2026-04-10-tailscaleでhttps通信local-pcのwebアプリにiphoneからアクセスする-01"
title: "Tailscaleでhttps通信。local PCのWebアプリにiphoneからアクセスする。"
url: "https://zenn.dev/nishina__n/articles/8a9a201b8f629e"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-10"
date_collected: "2026-04-12"
summary_by: "auto-rss"
---

## Tailscale

Tailscaleを使うとスマホとlocalPCをセキュアかつ、無料で接続できる。しかもhttpsで接続することが可能になる。Webブラウザベースのアプリではhttpsで接続していなければマイクの利用などがブラウザ側で制限されるため、必須の設定である。  
今回自作しているAIエージェントの[Voxclaw](https://github.com/Nishina-N/voxclaw/tree/main)を接続したが、https接続する時に少し手間がかかったので、記載しておく。今回の方法はlocalPCでlocalhostのwebページを立ち上げる場合に有効なので、応用も効くと思う。

## Voxclaw

[Voxclaw](https://github.com/Nishina-N/voxclaw/tree/main)は音声から意図推定して動作可能な軽量セキュアなAIエージェントで、先日リリースしたばかり。ユーザーの発話の意図推定をPWAで行っており、https接続が必須となる。  
<https://zenn.dev/nishina__n/articles/a11bda4b0d5e14>

<https://github.com/Nishina-N/voxclaw/tree/main>

## Tailscaleの準備

### TailScaleのインストール

ここから具体的な方法に入っていく。  
TailscaleのインストールはCLIで行う方法もあるけど、公式ページから行う方がCLIに慣れていない人にとっては簡単。右上の「Get started - it's free!」のボタンからGoogleアカウントなどで登録して、お使いのPCにインストールして下さい。

<https://tailscale.com>

### https設定

https設定をするには次の３ステップが必要となる。

**[手順1]**  
Tailscaleの[admin-dns](https://login.tailscale.com/admin/dns)ページか![](https://static.zenn.studio/user-upload/ef303ef76fc8-20260410.png)ら下記のMagicDNSとHTTPS CertificatesをEnableにする。MagicDNSはデフォルトでEnableだが、HTTPS Certificatesはデフォルトでdisableとなっていた。

![](https://static.zenn.studio/user-upload/51e7f57c155d-20260410.png)

**[手順2]**  
httpsに必要な秘密鍵と証明書をもらいます。  
ローカルPCのターミナル（WindowsではPowershellを使いました）で以下を実行します。  
ここで"XXXXXX.YYYYYY.ts.net"のXXXXXXは対照となるデバイス名、YYYYYYはTailnet DNS nameです。

TailscaleのMachinesタブより対象のデバイスを選んだあとの詳細画面のFull domainからコピーすることもできます。

```
PS > tailscale cert "XXXXXX.YYYYYY.ts.net"

# 以下が返ってくる
# Wrote public cert to XXXXXX.YYYYYY.ts.net.crt
# Wrote private key to XXXXXX.YYYYYY.ts.net.key
```

**[手順3]**  
続けて以下のコマンドを入力し、http://localhost:3000をFull domainに紐付けます。  
この作業により、localPCでVoxclawが立ち上がった時に開かれるlocalhost:3000にアクセスできるようになります。

```
PS > tailscale serve --bg http://localhost:3000
```

そうすると以下が返ってきます。

```
Available within your tailnet:

https://XXXXXX.YYYYYY.ts.net/
|-- proxy http://localhost:3000

Serve started and running in the background.
To disable the proxy, run: tailscale serve --https=443 off
```

ここまででlocalPCの指定したlocalhostをhttps接続する準備ができました。

## Voxclaw利用手順

### localPC側

1. 先ほどの手順でTailscaleのインストール及びlocalhost:3000のドメイン接続
2. Docker Desktopの起動
3. Voxclawの起動

```
# Voxclawのフォルダで下記コマンドを実施
PS > docker compose up -d --build
```

### スマホ側(iPhone)

**1. TailScaleアプリのインストール**  
アプリのインストール後、localPCと同じアカウントでログインし、端末をアカウントに紐づけて下さい。  
<https://apps.apple.com/jp/app/tailscale/id1470499037>

**2. ブラウザでアクセス**  
ブラウザ(Safari)から先ほどのFull Domain "<https://XXXXXX.YYYYYY.ts.net/>" にアクセスしましょう。

**3. ホーム画面に追加**  
Safariの共有ボタンからホーム画面に追加すると、PWAとなり、上の検索バーのスペースなどもアプリ表示に使うことができます。

## 最後に

今回の設定方法はhttpsを使ってlocalPCでたちがっているwebサービスとスマホを繋ぐ際に有効なので、[Voxclaw](https://github.com/Nishina-N/voxclaw/tree/main)ではなくてもぜひ試してみて下さい。

## 参考

<https://qiita.com/YUK_KND/items/7a3561ad6089431c532d>
