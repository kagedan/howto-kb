---
id: "2026-04-27-海外でesimを使ったらclaudeに繋がらなくなった話原因はipジオロケーションだった-01"
title: "海外でeSIMを使ったらClaudeに繋がらなくなった話。原因はIPジオロケーションだった"
url: "https://zenn.dev/kuyan/articles/62d61dccd63aee"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-27"
date_collected: "2026-04-28"
summary_by: "auto-rss"
query: ""
---

## 3行まとめ

* 韓国でHutchison HKのeSIMを使ったら、Claudeにアクセスできなくなった
* 原因は「どこに居るか」ではなく、「どこの国のネットワークを通っているか」
* eSIMローミングの場合、データの出口IPはeSIM発行元の国になる

## 何が起きたか

韓国ソウルに滞在中、Hutchison HK（香港の通信事業者）が発行するeSIMを使っていました。eSIMは現地でSKT（韓国の通信事業者）の電波を自動でつかんでくれて、ネット接続も問題ない。普通に使えていました。

ところが、Claudeを開くとアクセスできない。Claudeは香港での提供対象外なので、「香港からのアクセス」と判定されてブロックされたようです。

ホテルのWi-Fiに切り替えると、Claudeにはあっさりアクセスできました。原因はeSIM側にあると分かったので、仕組みを調べてみました。

## IPジオロケーションは「IPアドレスの登録国」を見ている

Webサービスがアクセス元の国を判定するとき、見ているのは**IPアドレス**です。具体的には次のような情報を参照しています。

* **ASN（Autonomous System Number※）**：そのIPがどの組織に割り当てられているか
* **APNIC・ARIN等の登録情報**：そのIPブロックがどの国で登録されているか
* HTTPヘッダー（X-Forwarded-For等）

つまり「物理的にどこにいるか」ではなく、「使っているIPがどの国の組織に登録されているか」で判定されます。GPS情報は使われません。

## 検証：自分のIP情報を見てみる

`https://ipinfo.io/json` に `curl` を投げると、自分のIPの登録情報がJSONで返ってきます。実際にやってみました。

### ①ホテルのWi-Fi経由（韓国）

```
$ curl https://ipinfo.io/json
{
  "ip": "xxx.xxx.xx.xxx",
  "city": "Seoul",
  "region": "Seoul",
  "country": "KR",
  "loc": "xx.xxxx,xxx.xxxx",
  "org": "AS4766 Korea Telecom",
  "timezone": "Asia/Seoul"
}
```

`country: KR`、`AS4766` はKorea Telecom（韓国）。当然ながら韓国判定です。

### ②eSIM（Hutchison HK）経由・ローミング中

```
$ curl https://ipinfo.io/json
{
  "ip": "xxx.xxx.xxx.xxx",
  "city": "Hong Kong",
  "region": "Hong Kong",
  "country": "HK",
  "loc": "xx.xxxx,xxx.xxxx",
  "org": "AS10118 Hutchison Telephone Company Limited",
  "timezone": "Asia/Hong_Kong"
}
```

`country: HK`。物理的には韓国にいるのに、IP的には香港でした。同じ場所・同じ時刻で、ネットワークを切り替えただけでこの差が出ます。

これがClaudeに「香港」と判定された正体です。

## なぜeSIMだと出口IPが香港になるのか

eSIMが韓国でSKTにつながっているのに、出口IPが香港になる理由は、モバイル通信の経路にあります。

通信経路はこう流れています。

```
[デバイス]
  ↓ 電波（韓国）
[SKT基地局]
  ↓ ローミング協定でHutchisonへトラフィック転送
[HutchisonバックボーンPGW※]（香港）
  ↓ ここで初めてインターネットに出る
[インターネット]
  ↓
[Claude]
```

ポイントは、SKTはあくまで「電波を貸している」だけで、データはHutchisonのネットワーク（香港）まで運ばれてからインターネットに出る、という設計になっていることです。これはホームルーティングと呼ばれる方式です。

「契約者の通信は契約事業者の管理下を通す」という考え方で、課金管理・利用制限・コンテンツフィルタの一貫性を保つ目的があります。Hutchisonの契約者は世界中どこから接続しても、最終的にHutchisonのネットワークから出ていくわけです。

結果として、ClaudeのサーバーはHutchisonのIP（香港登録）を見て「香港からのアクセス」と判定する、という流れでした。

## 結局どうすればよかったか

選択肢は3つあります。

| 方法 | メリット | デメリット |
| --- | --- | --- |
| 現地のWi-Fiを使う | 手軽・追加費用なし | 外出中は使えない |
| 韓国ローカルeSIMを別途追加 | 出口IPが韓国になる | SIM追加の手間・費用 |
| VPN経由で接続 | 任意の国のIPに変更可能 | 通信速度低下の可能性 |

Hutchisonに限らず、海外旅行用の周遊eSIMは同じ仕組みで動いているので、出口IPがeSIM発行国になります。サービスによってはこのIPが利用対象外でブロックされることがあるので、覚えておくと便利です。

## さいごに

eSIMで「現地で問題なく使えてるのに、特定のサービスだけ繋がらない」現象に遭遇したら、まず `curl https://ipinfo.io/json` で出口IPを確認してみるのをおすすめします。

「物理的に居る場所」と「IP的に居る場所」がズレるのはeSIMローミングならではの面白い特性です。普段は意識しないインターネットの裏側が垣間見えた出来事でした。
