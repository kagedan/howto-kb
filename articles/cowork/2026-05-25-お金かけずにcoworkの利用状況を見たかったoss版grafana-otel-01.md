---
id: "2026-05-25-お金かけずにcoworkの利用状況を見たかったoss版grafana-otel-01"
title: "お金かけずにCoworkの利用状況を見たかった（OSS版Grafana + OTel）"
url: "https://zenn.dev/avot/articles/01541221ea9161"
source: "zenn"
category: "cowork"
tags: ["prompt-engineering", "API", "cowork", "zenn"]
date_published: "2026-05-25"
date_collected: "2026-05-26"
summary_by: "auto-rss"
query: ""
---

# 経緯

弊環境はrsyslogのログをPromtail→Lokiで泥臭く集めて、EC2上のGrafanaで見るという構成がすでに動いていた。  
Coworkを組織に展開したはいいものの、誰がどれだけ使ってるか把握できないのが気になっていた。  
CoworkにOTelエクスポート機能があることを知って、せっかくなら既存の監視スタックに乗っけてしまおうという話。

※[OTel（OpenTelemetry）：特定のスタックじゃなくて「ログの共通規格」みたいなやつ。](https://opentelemetry.io/)

# 既存環境

* オンプレのUbuntuサーバ（ログ収集サーバ）でSyslog環境をDockerで実装
* 具体的にはrsyslog + Promtail + Loki が docker-composeで動作中
* んでLokiの中身はEC2においてるGrafanaから見てる（プライベートIPのみ）
* クライアントはWindows + VPN越しに接続

Loki的に気にするのはディスクですがまぁ空きがあったので大丈夫という感じで。

# 構成（弄ってないとこは割愛）

EC2のプライベートIPにはFortiClientのVPN越しでアクセスできるので、ALBとかは不要。

# やったこと

## docker-compose.yamlに追記

```
  alloy:
    image: grafana/alloy:latest
    ports:
      - "4318:4318"
      - "12345:12345"
    volumes:
      - ./alloy-config.alloy:/etc/alloy/config.alloy
    command:
      - run
      - --server.http.listen-addr=0.0.0.0:12345
      - /etc/alloy/config.alloy
    networks:
      - loki

  prometheus:
    image: prom/prometheus:latest
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--web.enable-remote-write-receiver'
      - '--storage.tsdb.retention.time=30d'
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yaml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - loki

volumes:
  prometheus_data:
```

## alloy-config.alloy

```
livedebugging {
  enabled = true
}

// OTLP受信
otelcol.receiver.otlp "cowork" {
  http {
    endpoint = "0.0.0.0:4318"
  }
  output {
    metrics = [otelcol.exporter.prometheus.default.input]
    logs    = [otelcol.exporter.loki.default.input]
  }
}

// メトリクス → Prometheus
otelcol.exporter.prometheus "default" {
  forward_to = [prometheus.remote_write.local.receiver]
}

prometheus.remote_write "local" {
  endpoint {
    url = "http://prometheus:9090/api/v1/write"
  }
}

// ログ → Loki
otelcol.exporter.loki "default" {
  forward_to = [loki.write.local.receiver]
}

loki.write "local" {
  endpoint {
    url = "http://loki:3100/loki/api/v1/push"
  }
  external_labels = {
    "service_name" = "cowork",
  }
}
```

## prometheus.yaml

```
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: alloy
    static_configs:
      - targets: ["alloy:12345"]
```

## 起動

```
docker compose up -d alloy prometheus
```

## CoworkのOTLP設定（管理者画面）

| 項目 | 値 |
| --- | --- |
| OTLPエンドポイント | `http://ログ収集サーバのIP:4318` |
| OTLPプロトコル | `http/protobuf` |
| OTLPヘッダー | 空欄 |
| リソース属性 | `deployment.environment=prod` |

ベースURLを入れるだけでよく、`/v1/logs`は自動で付加される。

# ポイント・ハマりどころ

* **Prometheusが起動しない** → `prometheus.yaml`に`retention.time`をyamlで書こうとしてハマった。保持期間はdocker-composeの`--storage.tsdb.retention.time=30d`で指定する。
* **AlloyのLive Debuggingが使えない** → v1.16.1では`--stability.level=experimental`フラグが廃止。`alloy-config.alloy`に`livedebugging { enabled = true }`を追記するのが正しい。
* **AlloyからLokiにログが届かない** → `loki.write`に`external_labels`で`service_name`を付与したら解決した。
* **設定変更の反映タイミング** → CoworkのOTLP設定は新しいセッション開始時にロードされる。既存セッションには反映されない。
* **管理者アカウントにプランを付与していない場合の動作確認が地獄** → 自分でCoworkのタスクを投げて確認ということができないので、AlloyのLive Debuggingをひたすら眺めて誰かがタスクを実行するのを待つしかなかった。じっとDebugを見続けるのはかなり苦痛だった。テスト用にプラン付きのアカウントを持っておくことを強くおすすめします。

# 届くイベントについて

全イベントに`user.email`が含まれるのでユーザー識別はそのままできる。

主なイベント：

| イベント | 内容 |
| --- | --- |
| `api_request` | APIコール。`cost_usd`や`input_tokens`が含まれる |
| `tool_result` | ツール実行結果。`tool_name`や`duration_ms`が含まれる |
| `tool_decision` | ツール許可/拒否の記録 |
| `user_prompt` | ユーザーのプロンプト送信 |

LokiにJSONパースで展開するとフィールドが`attributes_user_email`や`attributes_cost_usd`といった形になる（Loki 2.8.0で確認）。

# GrafanaのLogQLクエリ例

ユーザー別APIリクエスト回数：

```
sum by (attributes_user_email) (
  count_over_time(
    {service_name="cowork"} | json | attributes_event_name="api_request" [$__range]
  )
)
```

ユーザー別累計コスト：

```
sum by (attributes_user_email) (
  sum_over_time(
    {service_name="cowork"} | json | attributes_event_name="api_request"
    | unwrap attributes_cost_usd | __error__="" [$__range]
  )
)
```

# まとめ

既存のLoki環境があればAlloyとPrometheusを追加するだけで乗っかれる。  
新たにサーバを立てる必要もなかったし、EC2側もGrafanaのデータソースを追加するだけで済んだ。

CoworkのOTelはログプロトコルなのでTraceやMetricsは別途Alloyで振り分ける構成にする必要がある点だけ注意。
