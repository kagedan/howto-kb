---
id: "2026-07-01-claude-splunk-mcpaiエージェントがどこまで障害対応できるか検証したら想像以上だった-01"
title: "【Claude × Splunk MCP】AIエージェントがどこまで障害対応できるか検証したら想像以上だった"
url: "https://zenn.dev/yukurash/articles/2db3e70a9d8b9b"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "LLM", "zenn"]
date_published: "2026-07-01"
date_collected: "2026-07-02"
summary_by: "auto-rss"
query: ""
---

## はじめに

当たり前なことですが障害対応ってほんと大変ですよね。恐らくどんなエンジニアでもいろんな形で経験されたことがあると思います。

そこで、AI で障害対応どこまでできるのか、というのを Claude Code と [Splunk MCP サーバー](https://www.splunk.com/ja_jp/products/model-context-protocol.html) を使って検証してみました。

## 先に結論

結果は予想以上に対応してくれました。

Claude は自分の判断で、**Splunk のツールを7回選んで叩き、3往復のやり取りで根本原因のサービスを特定**しました。  
更にサービスだけでなく、壊れているエンドポイントまで言い当てました。また、たまたま発生したエラーは「別件」と切り分け、逆に情報が足りない場合には「断定できない」と確信度まで言及してくれました。

検証内容等全て載せたリポジトリも置いておきますので、パッと見たい方はこちらご参照ください。  
<https://github.com/yukurash/splunk-ai-oncall>

詳細は下記で記載していきます。

## 何を作ったか - 技術構成

検証用として、下記のような構成で各種作成しました。  
観測対象のアプリ、それを Splunk に送る Collector、そして Splunk を覗きにいく Claude Code、という形です。

観測対象には公式の [OpenTelemetry Demo](https://github.com/open-telemetry/opentelemetry-demo) を使いました。  
OpenTelemetry の検証用の EC サイトで色んな機能が格納されています。ありがたいことに feature flag で障害を注入できる仕組みがあり、「特定商品の取得だけ失敗させる」「決済を落とす」といったシナリオを再現できるためこちらを利用しました。

技術スタックは下記です。

| 役割 | 使ったもの | 補足 |
| --- | --- | --- |
| 観測対象アプリ | OpenTelemetry Demo v2.2.0 | Docker Compose |
| テレメトリ収集 | OpenTelemetry Collector 0.151.0 | デモ同梱。Splunk 用に exporter を追加 |
| バックエンド | Splunk Observability Cloud | APM（トレース）＋メトリクス |
| AI 接続 | Splunk MCP Gateway | o11y 系ツールを利用 |
| AI 本体 | Claude Code | 調査役はツール無しのサブエージェント |

## 検証準備

### 1. Claude Code で Splunk MCP を設定

Claude Code の場合、`.mcp.json` に `mcp-remote` 経由で記載します。アクセストークンを `X-SF-TOKEN`、realm を `X-SF-REALM` として、ヘッダーに記載します。

```
{
  "mcpServers": {
    "splunk-o11y": {
      "command": "npx",
      "args": [
        "-y", "mcp-remote",
        "${SPLUNK_MCP_URL}",
        "--header", "X-SF-TOKEN: ${SPLUNK_ACCESS_TOKEN}",
        "--header", "X-SF-REALM: ${SPLUNK_REALM}"
      ]
    }
  }
}
```

### 2. デモのデータを Splunk へ送る

OpenTelemetry Demo では色々設定されており、各種操作のテレメトリが自動で Collector に流れ込む動作となります。なので、やるべきこととしては、その Collector が受け取ったデータの**転送先を Splunk に向ける**こととなります。

具体的な設定方法は下記です。

collector/otelcol-config-extras.yml

```
exporters:
  # メトリクス → Splunk O11y
  signalfx:
    access_token: "${env:SPLUNK_ACCESS_TOKEN}"
    realm: "${env:SPLUNK_REALM}"
    sync_host_metadata: true

  # トレース → Splunk APM (OTLP/HTTP)。sapm は contrib 0.151.0 で削除済み
  otlphttp/splunk:
    traces_endpoint: "https://ingest.${env:SPLUNK_REALM}.signalfx.com/v2/trace/otlp"
    headers:
      X-SF-Token: "${env:SPLUNK_ACCESS_TOKEN}"

service:
  pipelines:
    traces:
      exporters: [debug, span_metrics, otlphttp/splunk]
    metrics:
      exporters: [debug, signalfx]
```

設定の全文は [`collector/otelcol-config-extras.yml`](https://github.com/yukurash/splunk-ai-oncall/blob/main/collector/otelcol-config-extras.yml) に置いています。

`${env:SPLUNK_ACCESS_TOKEN}` などの実値は下記の手順で渡すようにしました。

1. この設定ファイルを、デモが読みにいく場所に置く
2. トークンと realm を `.env` に書き、Collector に環境変数として渡す（`docker-compose.splunk.yml` が担当）
3. デモ本体の compose にこのオーバーレイを重ねて起動する

```
docker compose --env-file ../.env \
  -f docker-compose.yml \
  -f ../docker-compose.splunk.yml up -d
```

## 検証

準備ができたので、本題の「AI は障害対応できるか」を検証します。

### 検証方法

検証方法として、Claude Code の AI エージェントは全く調査内容等の事前知識は持たないようにしています。Splunk MCP に繋がっていることは伝えてますが、「**本番の EC サイトで異常の通報。詳細不明。調べてほしい**」という症状すらない一文だけ渡しています。

あと、通常であれば MCP 繋いでいるので自動で Splunk のツールを呼び出しますが、今回は AI（エージェント) がどのような思考で調査するのか詳細を追いたかったため、中継を挟むようにしています。

具体的なフローは下記です。

### 障害内容

本番サイトは前述の OpenTelemetry Demo を利用するため、元々ある feature flag で障害を注入します。具体的には「**商品カタログ障害**」を仕込みました。

障害の内容としては、「特定の1商品を取得したときだけ失敗する」設定にしました。サービス全体が落ちるのではなく、特定エンドポイントだけが壊れるという、現実に多い、いやらしい壊れ方を再現しました。

さらに意地悪もしてみました。  
別障害（決済の失敗）の残留エラーを消さずに残し、**常に Critical を複数出し続けるノイズ**を仕込んでおきました。実シナリオでも他のエラーが発生していることは十分考えられ、その中から本当の障害を見つけて対応できるかを知りたかったためです。

## 検証結果

実際の検証結果で、呼び出したツールは下記になります。ラウンドごとに AI は何を考えて実行したのかを紹介します。

### ラウンド1 - 検知

最初に AI エージェントがやったのは、人間と同じ**状況把握**でした。

発火中のアラートと、サービス一覧をエラー数順で、まとめて取得していました。ただ発火中のアラートは0件。一方、サービスの health バッジでは仕込んだノイズの 3 つの Critical が点灯しており、エラー件数のトップは frontend-proxy と frontendの状況でした。

素直に見れば「（全く障害と関係ない）フロントが壊れている」と言いたくなるような状況です。

### ラウンド2 - 切り分け

ここで AI エージェントの見方が効きました。下記引用です。

```
注目点は rootCauseErr（自分が震源のエラー数）です。
frontend-proxy は err=112 だがrootCauseErr=1、frontend は err=111 だが rootCauseErr=8 
　→ 下流から波及したエラーが大半。
product-catalog は err=99／rootCauseErr=99 
　→ 全エラーが本アプリ発の震源。
```

つまり、**仕込んだノイズにAI エージェントは全く釣られませんでした。**  
`rootCauseErrorCount` という「そのエラーの震源がどこか」を表す指標を主軸に置いて、件数では目立たない product-catalog（仕込んだ障害）を本命に挙げました。

次に行ったのは裏取りです。  
Claude は product-catalog のエラー内訳を取りにいきました。出てきた表が決定的でした。

| product-catalog のエンドポイント | リクエスト | エラー | うち震源 |
| --- | --- | --- | --- |
| `GetProduct` | 5496 | 204 | 204 |
| `ListProducts` | 1645 | 0 | 0 |
| `Health/Check` | 118 | 0 | 0 |

※ 上記では err=99 でしたが、数分後にエンドポイント別に他のツールで取得したものが、この結果となります。

失敗は `GetProduct` に集中しており、`ListProducts` と死活監視は無傷です。  
つまり、「**サービス全体が落ちたわけではなく、特定のエンドポイントだけが壊れている。実トレースを開いても、すべて product-catalog が根本原因で、他はそろって波及していた**」と判断したわけです。完璧すぎて怖いです。

ちなみにノイズの切り分けは他にもこんな感じでAI エージェントは実行してました。（優秀...

```
payment は Charge が err=5／rootCauseErr=5 とアプリ発のエラーだが、
product-catalog の rc_err 経路に相互登場せず、件数も桁違いに小さい 
　→ 別件（独立した低頻度障害）。
flagd / local-llm も rc_err 経路に登場せず 
　→ 別件 or ノイズ。
```

### ラウンド3 - 確証

最後に AI エージェントは、エラートレースの中身そのものを開いて、どういうエラーかを確かめにいきました。

ここまでで見た実トレースは計10本、すべて product-catalog が根本原因で他に波及したと判断しています。しかも所要時間は26〜100msと短く、これは遅延ではなく即時のエラー応答だと把握していました。根本原因も、壊れている箇所も、壊れ方も、全てデータだけで詰め切っていました。

### FINAL - 結論

締めに、AI エージェントはご丁寧に自身の確信度まで格付けしてきました。

```
根本原因の所在（product-catalog / GetProduct）= 高。
具体トリガー（フラグ説）= 中。
flagd → product-catalog の因果リンクは観測で直接取れていない。
フラグ状態とログ確認で「高」に上げられる。
```

つまり、裏が取れていないことは断言しないということですね。特に因果関係はこういう時ややこしくなりがちなので、これは相当信頼できます。

## 他の障害でもほぼ同様の結果

他の障害（エラー、レイテンシ、非同期の詰まり）でも検証しましたが、どれもほぼ似た結果です。症状の種類が変わっても、目の前のデータから筋を通してくる動作は安定していました。

ただ、メモリリークだけは、AI エージェントも「**断定不可**」と答えてました。  
症状はメモリリークそのものなのに、APM のレイテンシやエラーには、初期段階ではまだ表れないからです。

ここに今の限界と、次の鍵がある気がしました。APM に出ない障害は、AI 自身がメモリやキューのメトリクスまで取りにいく必要があるということですね。Splunk MCP にはメトリクス系のツールもあるので、そこまで委ねれば届くはず。。

## まとめ

一通りやってみて、想像以上に使えると思いました。

もちろんサービスレベルで使うのは怖さもありますが、ただ**一時切り分けとしては十分すぎるぐらい便利に使えるだろうな**と実感しました。

逆に、メモリやキュー滞留のように APM に出ない障害、外部要因が絡む障害、そして本番への変更を伴う復旧操作等はまだまだ人間がやる方が早いし確実だろうなと感じました。

こちらが少しでも参考になれば幸いです。

本記事の検証内容のリポジトリはこちら。  
<https://github.com/yukurash/splunk-ai-oncall>
