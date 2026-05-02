---
id: "2026-05-01-ai-agentに外部通信させるのが怖いのでオレオレproxyを作った-01"
title: "AI Agentに外部通信させるのが怖いので、オレオレProxyを作った"
url: "https://zenn.dev/digeon/articles/11057eb2c974e3"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "OpenAI", "GPT", "Python"]
date_published: "2026-05-01"
date_collected: "2026-05-02"
summary_by: "auto-rss"
query: ""
---

AI Agent にローカル環境を触らせるのは便利ですが、外部通信までそのまま許すのは少し怖いです。

ローカルには GitHub token や npm token、cloud credential があります。単に通信先を眺めたいというより、それらを使って意図しない `POST` などの副作用ある request が走るのを避けたいです。

そこで、自分用に小さなローカル proxy を作りました。

やりたかったことは単純で、AI Agent が外へ出す通信を手元で観測しつつ、必要なものだけ通し、副作用がありそうなものは明示的に止め、MITM すると壊れるものは passthrough したい、というものです。

ここでいう MITM は、proxy が HTTPS をいったん終端し、request の method / path / header を見られる状態にすることです。passthrough は逆に、TLS を終端せず、中身を見ないまま接続先へ流すことを指しています。

作ったのは、`mitmproxy` の addon として動くローカル proxy です。

AI Agent や CLI tool の通信をこの proxy に集めて、通信先ごとに次の 3 つへ振り分けます。

* `passthrough`: TLS を触らず、そのまま通す
* `inspect`: MITM して method / path / header を見る
* `block`: 許可していない通信を拒否する

構成はこうです。

```
AI Agent / CLI tool
        |
        | HTTP_PROXY / HTTPS_PROXY
        v
local mitmproxy addon
        |
        +-- passthrough: TLS を触らずそのまま通す
        |
        +-- inspect: MITM して request rule を評価する
        |
        +-- block: 明示的に拒否する
        v
Internet
```

!

この記事では、完全な network sandbox を作る話はしません。

厳密に Agent の通信を proxy 経由に限定したいなら、iptables などで外向きの通信経路をふさぐ必要があります。ただし通信制御のやり方は Agent を使う環境に依存し、Codex App のように通信経路をふさぐこと自体が難しい環境もあります。

今回はそこまでは踏み込まず、汎用的な proxy 環境変数を設定するところまでにとどめます。

ただ、自分がローカルで使っている範囲では、proxy 環境変数だけでもわりと機能しました。Agent に「proxy を経由している」というコンテキストをわざわざ与えなければ、通信が block されたときも別経路で回避しようとするより、素直に失敗として扱うことが多かったです(gpt5.5 medium)。

## 何を作ったか

主な機能は次の通りです。

* HTTPS 通信を MITM して request を inspect する
* host / method / path / header による allow rule を書ける
* MITM すると壊れる host は TLS passthrough できる
* proxy 設定は JSON で管理する

proxy は `127.0.0.1:8787` で待ち受けます。

```
export HTTPS_PROXY=http://127.0.0.1:8787
export HTTP_PROXY=http://127.0.0.1:8787
```

これで Agent や CLI の通信がローカル proxy を通ります。

## 作った理由

AI Agent に外部通信を許すとき、気になる点は大きく 2 つあります。

1 つ目は、ローカルの credential を使った副作用のある request です。

自分の環境では、Agent をyolo mode でよく動かしています。毎回確認されないぶん便利ですが、その状態で外部通信まで素通しにするのは怖さがあります。

ローカルには GitHub token、npm token、cloud credential、各種 API key があります。Agent がそれらを使える状態で外部通信できるなら、単なる `GET` だけでなく、`POST` や `DELETE` のような状態を変える request も起こりえます。

もちろん Agent が悪意を持っているという話ではありません。問題は、Agent が実行する command や tool の先で、どの host にどんな method の request が発生するかを人間が毎回追いきれないことです。

2 つ目は、雑に MITM すると普通に壊れることです。

HTTPS を inspect するには CA の信頼設定が必要になります。さらに、一部の認証系 endpoint や CLI は独自の CA bundle を使っていたり、証明書まわりに繊細だったりします。全部を MITM すると、セキュリティ以前に開発体験が壊れます。

欲しかったのは、こういう境界でした。

* 副作用のある request は明示的な rule がない限り止める
* method / path / header を見たい通信は inspect する
* 見なくていい通信は passthrough する
* 知らない通信は block または限定的に allow する
* 設定は自分で読める形にする
* 壊れたときに調査できるようにする

## mitmproxy を選んだ理由

やりたいことに対して、`mitmproxy` はちょうどよかったです。

HTTP proxy として動き、HTTPS の CONNECT を扱えて、必要なら HTTPS を inspect できます。さらに addon として Python で判定ロジックを書けます。

* HTTPS MITM のための CA 生成が標準で用意されている
* addon として Python コードを書ける
* `http_connect` や `request` のような hook がある
* request / response の情報にアクセスしやすい
* ローカル開発用途なら十分に枯れている

起動は `mitmdump` に addon を渡すだけです。

```
mitmdump \
  --mode regular \
  --listen-host 127.0.0.1 \
  --listen-port 8787 \
  --set connection_strategy=lazy \
  -s addon.py
```

実際には shell script にして、設定ファイルから host / port を読むようにしました。

使う側は前述の proxy 環境変数を向けるだけです。Codex CLI でも Claude Code でも、通常の proxy 環境変数を見る tool なら同じ境界に乗せられます。

## 設定ファイル

設定は JSON にしました。

ざっくりこういう形です。

config/proxy.config.json

```
{
  "host": "127.0.0.1",
  "port": 8787,
  "tls": {
    "passthroughHosts": [
      "localhost",
      "127.0.0.1",
      "api.openai.com",
      "github.com",
      "*.github.com",
      "*.githubusercontent.com"
    ]
  },
  "requestFiltering": {
    "inspectFallbackAllowedMethods": ["GET"],
    "allowRules": []
  }
}
```

大きく 3 つの概念に分けています。

### tls.passthroughHosts

`tls.passthroughHosts` に入った host は MITM しません。

TLS を触らずにそのまま通すので、proxy 側では HTTPS の中身を見ません。CA 設定も不要になります。

たとえば認証系 endpoint、GitHub 関連、OpenAI API など、MITM する必要が薄いものや MITM すると壊れやすいものをここに置きます。

config/proxy.config.json

```
{
  "tls": {
    "passthroughHosts": [
      "api.openai.com",
      "auth.openai.com",
      "github.com",
      "*.github.com"
    ]
  }
}
```

### requestFiltering.allowRules

`allowRules` は MITM した request に対する許可ルールです。

host、method、protocol、path、user agent、header などで絞れます。

config/proxy.config.json

```
{
  "requestFiltering": {
    "allowRules": [
      {
        "name": "aws dynamodb list-tables",
        "methods": ["POST"],
        "protocols": ["https"],
        "hosts": ["dynamodb.ap-northeast-1.amazonaws.com"],
        "pathPatterns": ["/"],
        "headerPatterns": {
          "X-Amz-Target": ["DynamoDB_20120810.ListTables"]
        }
      }
    ]
  }
}
```

この例では、DynamoDB の `ListTables` だけを許可します。DynamoDB の API は `POST /` に `X-Amz-Target` header で operation 名を載せるので、method だけでなく header も見て絞ります。実際の method / path / header は、proxy のログや AWS の API Reference を見て合わせます。

`allowRules[].hosts` に書いた host は、自動的に inspect 対象にしています。つまり「この host は MITM して、中身を rule で見る」という意思表示になります。

### inspectFallbackAllowedMethods

`inspectFallbackAllowedMethods` は、明示的な rule がない host に対する fallback です。

config/proxy.config.json

```
{
  "requestFiltering": {
    "inspectFallbackAllowedMethods": ["GET"]
  }
}
```

この設定だと、未知の host でも GET だけは inspect したうえで通します。

自分の使い方では、Agent に web 検索はしてほしいので GET は許可しています。副作用がありそうな POST / PUT / DELETE などは、必要になったときだけ allow rule に落とし込む、という運用です。

## 判定の優先順位

CONNECT 時点では、だいたい次の順番で判定しています。

1. `tls.passthroughHosts` に一致したら passthrough
2. `allowRules[].hosts` に一致したら MITM
3. host を省略した `allowRules[]` があれば MITM
4. `inspectFallbackAllowedMethods` が非空なら MITM fallback
5. どれにも当たらなければ block

同じ host が複数箇所に出てきた場合、static な `passthroughHosts` を最優先にしました。

この順番にしておくと運用しやすいです。MITM すると壊れる host は、まず最初に逃がしたいです。後段の allow rule で何をしていても、passthrough に入っているなら触らない、というルールのほうが読みやすいです。

## 運用でハマったところ

少し面倒だったのが AWS と CA まわりです。

まず AWS です。

AWS CLI はローカルの credential を使って API を叩きます。だからこそ、AWS 向けの通信はただ passthrough するより、MITM して method / path / header を allow rule で絞りたいです。

AWS API はサービスや operation によって method / path が違います。`inspectFallbackAllowedMethods` で GET を通す運用なら、allow rule では POST など副作用がありうる method を絞るほうが分かりやすいです。

たとえば DynamoDB の `ListTables` は読み取り系の operation ですが、HTTP としては `POST /` です。これだけ許可するなら次のように書けます。

config/proxy.config.json

```
{
  "requestFiltering": {
    "allowRules": [
      {
        "name": "aws dynamodb list-tables",
        "methods": ["POST"],
        "protocols": ["https"],
        "hosts": ["dynamodb.ap-northeast-1.amazonaws.com"],
        "pathPatterns": ["/"],
        "headerPatterns": {
          "X-Amz-Target": ["DynamoDB_20120810.ListTables"]
        }
      }
    ]
  }
}
```

AWS の request は SigV4 で署名されるので、credential 由来の header 条件で絞ることもできます。自分の環境では、この形で一時 credential ごとに許可範囲を分けています。

config/proxy.config.json

```
{
  "requestFiltering": {
    "allowRules": [
      {
        "name": "aws session token",
        "methods": ["*"],
        "protocols": ["https"],
        "hosts": ["*.amazonaws.com"],
        "headerPatterns": {
          "X-Amz-Security-Token": ["<YOUR_SESSION_TOKEN>"]
        }
      }
    ]
  }
}
```

`<YOUR_SESSION_TOKEN>` には、実際に許可したい一時 credential の session token を入れます。

次に CA です。MITM する場合、クライアントは mitmproxy の CA を信頼する必要があります。

mitmproxy は初回起動時に `~/.mitmproxy/` 配下へ CA を作ります。

Ubuntu / WSL なら、たとえば次のように system trust store に入れます。

```
sudo cp ~/.mitmproxy/mitmproxy-ca-cert.pem /usr/local/share/ca-certificates/mitmproxy.crt
sudo update-ca-certificates
```

ただし、これで全部解決するわけではありません。

ツールによっては、OS に CA を入れただけではその CA を見てくれないことがあります。AWS CLI も、参照している CA bundle に mitmproxy の CA が入っていないと、proxy 経由だけ `CERTIFICATE_VERIFY_FAILED` になります。

この手の問題は proxy のロジックではなく、クライアント側の trust store 問題であることが多いです。

`ca_bundle` は、AWS CLI に「証明書検証で使う CA bundle はこれ」と明示する設定です。自分の環境では、AWS CLI 用に `~/.aws/config` 側へこれを書いておくのが安定しました。

~/.aws/config

```
[default]
region = ap-northeast-1
ca_bundle = /etc/ssl/certs/ca-certificates.crt
```

`curl` では通るのに AWS CLI では落ちる、system CA に入れたのに Node.js 系 tool だけ失敗する、ということはあります。こういうときは次を確認します。

* その host は本当に inspect する必要があるか
* client がどの CA bundle を見ているか
* passthrough に逃がしたほうが自然ではないか

inspect が不要な host は、passthrough に寄せるほうが安定します。

ログも重要です。Agent は複数の command をまとめて実行するので、package manager、GitHub、API、認証 endpoint などへの通信が一気に出ます。proxy のログに、

```
[passthrough] CONNECT api.openai.com:443 reason="passthrough host: api.openai.com"
[allowed] GET https://example.com reason="inspect fallback allow: GET"
[blocked] POST https://example.com/api reason="blocked POST https://example.com/api"
```

のように残れば、何が通って何が止まったかを追えます。

ローカルの credential がある環境では、「どこへ通信したか」だけでなく、「どんな method が通ったか」と「明示していない副作用のある request を止められたか」を確認できることが大事です。

もちろん、これは万能なセキュリティ境界ではありません。OS レベルの firewall や sandbox の代わりではなく、ローカル開発で Agent の通信を観測し、必要な範囲で止めるための道具です。

## まとめ

AI Agent がコードを書く時代になると、エディタや shell の権限だけでなく、ネットワークの境界も自分で設計したくなります。

今回作った proxy は、そのための小さな実験でした。

* Agent の通信を proxy に集める
* MITM するものと passthrough するものを分ける
* allow rule で副作用のある request を明示的に制御する
* AWS のような credential 付き request も rule で制御する

やっていることは単純ですが、Agent を日常的に使う環境では、このくらいの境界があるだけでも扱いやすくなります。

リポジトリはこちらです。

<https://github.com/yamacrypt/agent-proxy>
