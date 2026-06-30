---
id: "2026-06-30-otel-の送信先を-splunk-に切り替えai-agent-monitoring-で-claud-01"
title: "OTel の送信先を Splunk に切り替え、AI Agent Monitoring で Claude を見る"
url: "https://zenn.dev/propagandist/articles/0007-splunk-claude-ai-agent-monitoring"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "AI-agent", "LLM", "zenn"]
date_published: "2026-06-30"
date_collected: "2026-07-01"
summary_by: "auto-rss"
query: ""
---

## この記事について

* **対象読者**：Spring Boot × Claude を OpenTelemetry で計測している人（ローカルの Jaeger/Prometheus 構成など）。その送信先を **Splunk Observability Cloud** に向け、**Splunk の AI Agent Monitoring で LLM 呼び出しを見たい**人
* **得られること**：アプリのコードは変えず、**送信先（エンドポイントとトークン）だけ**で Splunk へ切り替える手順。Splunk APM に `chat <model>` の span が出るところまで。そして **AI Agent Monitoring** が `gen_ai.*` 計装を自動認識し、モデル別のリクエスト・トークン・レイテンシ・コストを集計するところまで（コスト表示は新モデルで後述の注意あり）
* **前提・環境**：Java 21 / Spring Boot 3.5 / OpenTelemetry（OTLP 送信ができている構成）。**Splunk Observability Cloud のアカウント**（無料トライアル可）と、その **realm・アクセストークン**

> この記事は「[OpenTelemetry の GenAI 規約に沿って Claude 呼び出しを計装する](https://zenn.dev/propagandist/articles/0005-otel-genai-semconv-claude)」の続編です。同じアプリの**送信先を差し替える**話なので、規約に沿わせた計装そのものは前回までを引き継ぎます。

> エンドポイント形式・設定キー・画面は\*\*執筆時点（2026年6月）\*\*のものです。realm 名やトークンは契約ごとに異なり、最新仕様は[Splunk の公式ドキュメント](https://help.splunk.com/en/splunk-observability-cloud)で確認してください。AI Agent Monitoring は比較的新しい機能で、表示の有無は契約・提供状況によります。

## OpenTelemetry の約束：送信先は付け替えられる

OpenTelemetry でいちばん効いてくる性質は、**計装と送信先が切り離されている**ことです。アプリは「OTLP で送る」とだけ決めておけば、受け取る側は——ローカルの Collector でも、SaaS でも——**付け替えられます**。

前回まで、Claude 呼び出しを `Observation`（= span）で包み、`gen_ai.*` の属性を載せてきました。この計装は Splunk 専用ではありません。だから Splunk へ送るのに、**アプリのコードを書き換える必要はありません**。変えるのは送信先だけです。

とくに、[GenAI 規約に沿わせておく](https://zenn.dev/propagandist/articles/0005-otel-genai-semconv-claude)と、Splunk 側でも属性が素直に扱えます。`gen_ai.request.model` や `gen_ai.usage.output_tokens` という共通名で載っているので、ベンダーをまたいでも同じ問いを投げられます。これが「規約に沿う」見返りでもあります。

## 結論（先に全体像）

送信先を Splunk Observability Cloud に向ける道は2つあります。どちらも**アプリのコードは不変**です。

1. **アプリから直接 OTLP で送る**：エンドポイントを Splunk の取り込み口にし、`X-SF-Token` ヘッダにアクセストークンを付ける。Collector 不要の最小構成
2. **Splunk 配布の OTel Collector 経由（推奨）**：アプリは Collector に OTLP で送り、Collector が Splunk へ転送する。本番向きで、サンプリングや属性加工も挟める

送れたら、**Splunk APM** で `chat <model>` の span を確認し、**AI Agent Monitoring** でモデル別の集計を見ます。

## 手順1：realm とアクセストークンを用意する

Splunk Observability Cloud で2つの値を確認します。

* **realm（リージョン識別子）**：組織が割り当てられたデータセンターの識別子（例：`us1`・`jp0` など）。プロフィール画面で確認できます。エンドポイントの URL に入ります
* **アクセストークン**：データ取り込み用のトークン。設定の「アクセストークン（Access Tokens）」から取得します。**API アクセス用のトークンとは別物**なので注意します

> **用語**：Splunk の **realm** は送信先リージョンを表す短い識別子です。エンドポイントは `ingest.<realm>.observability.splunkcloud.com` の形になります。realm を間違えると、認証は通っても**データが届きません**。

トークンは秘密情報なので、コードに直書きせず環境変数（`.env` など）に置きます。

```
# .env（コミットしない）
SPLUNK_REALM=us1
SPLUNK_ACCESS_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxx
# 前回までで使っている Claude の API キーも同じ .env に置く（手順3で読み込む）
ANTHROPIC_API_KEY=sk-ant-...
```

## 手順2A：アプリから直接 OTLP で送る

最小構成は、Spring Boot の OTLP 送信先を **Splunk の取り込み口**に向け、ヘッダに `X-SF-Token` を足すだけです。`application.yaml` の送信先設定を差し替えます。

```
management:
  otlp:
    tracing:
      # トレースの取り込み口（realm を自分の値に）
      endpoint: https://ingest.${SPLUNK_REALM}.observability.splunkcloud.com/v2/trace/otlp
      headers:
        X-SF-Token: ${SPLUNK_ACCESS_TOKEN}
    metrics:
      export:
        # メトリクスの取り込み口
        url: https://ingest.${SPLUNK_REALM}.observability.splunkcloud.com/v2/datapoint/otlp
        headers:
          X-SF-Token: ${SPLUNK_ACCESS_TOKEN}
```

ローカル検証のときは `http://localhost:4318/...` だった部分を、Splunk の HTTPS エンドポイントに替えただけです。`service.name`（`spring.application.name`）はそのままで、Splunk 側でもサービス名として表示されます。

> このプロパティ名は **Spring Boot 3.x** のものです（執筆時点 3.5）。**Spring Boot 4.0 以降**はトレースの OTLP 設定キーが `management.opentelemetry.tracing.export.otlp.*` 系に変わるので、お使いのバージョンの公式ドキュメントで読み替えてください。

> 認証は通るのにデータが出ないときは、**realm の取り違え**か、**トークンの種別違い**（取り込み用ではないトークンを使っている）がほとんどです。次の「つまずき」も参照してください。

## 手順2B：Splunk 配布の OTel Collector 経由（推奨）

本番では、アプリと Splunk の間に **Collector** を挟むのが定石です。サンプリングや属性加工（テールサンプリング・マスキング）を Collector 側で挟めますし、送信先を一括で管理できます。

Splunk は OpenTelemetry Collector の配布版を提供しており、**realm とアクセストークンを環境変数で渡すだけ**で、Splunk 向けのエクスポータが構成されます。

```
# docker compose（要点）：Splunk 配布の Collector に realm/token を渡す
services:
  otelcol:
    image: quay.io/signalfx/splunk-otel-collector:latest
    environment:
      - SPLUNK_REALM=${SPLUNK_REALM}
      - SPLUNK_ACCESS_TOKEN=${SPLUNK_ACCESS_TOKEN}
    ports:
      - "4318:4318"   # アプリはここへ OTLP/HTTP で送る（ローカルと同じ向き先）
```

この場合、アプリ側の `application.yaml` は**ローカル検証のとき（`http://localhost:4318/...`）のまま**で構いません。送信先（Splunk）を知っているのは Collector だけになり、アプリは送信先を意識しません。これが「計装と送信先の分離」のいちばん素直な形です。

## 手順3：リクエストを送ってトレースを発生させる

このアプリは**起動しただけでは Claude を呼びません**（意図しないトークン消費を避けるためです）。トレースを出すには、`/ask` エンドポイントを呼びます。手順1で `.env` に入れた realm・アクセストークンと、`ANTHROPIC_API_KEY` を読み込んで起動し、1回呼んでみます。

```
./gradlew bootRun
curl "http://localhost:8080/ask?prompt=Spring%20Boot%20を一言で"
```

1回の呼び出しで、受信リクエストの span と、その子の `chat <model>` span が1組できます。手順4の APM はこれで追えます。ただし手順5の **AI Agent Monitoring はモデル別・p90/p99 などの集計ビュー**なので、数回呼んでおくとチャートが見栄えします。

> **すぐに出なくても慌てないでください。** SaaS への取り込みには数十秒〜数分のラグがあります。APM や AI overview がまだ空なら、少し待って画面を更新します。集計ビューは直近の時間窓（例：`-15m`）で見るので、窓から外れた古いトレースは数回呼び直すと確実です。

## 手順4：Splunk APM で span を見る

データが届いたら、**Splunk APM** でサービス（`service.name`）を開きます。受信リクエストの span の下に、Claude 呼び出しの span（[規約に沿った計装](https://zenn.dev/propagandist/articles/0005-otel-genai-semconv-claude)なら `chat <model>`）が子として連なり、`gen_ai.*` の属性——モデル名・トークン・停止理由——が乗っているのを確認できます。トークンのメトリクス（`gen_ai.client.token.usage`）も、ダッシュボードのチャートとして扱えます。

![Splunk APM のトレース画面](https://static.zenn.studio/user-upload/deployed-images/3ec9fb2d1f1e54b0f2e03382.png?sha=0f4ba996d37a0359be403545517a4166e8f8cd75)

*Splunk APM：受信リクエストの配下に `chat <model>` の span が連なり、`gen_ai.*` 属性で1呼び出しの内訳を追える。*

## 手順5：AI Agent Monitoring で Claude 呼び出しを見る

Splunk Observability Cloud の **AI Agent Monitoring**（APM 配下・"New" 機能）は、`gen_ai.*` 規約に沿った span を**自動で「AI/LLM 呼び出し」と認識**します。そのうえで、モデル別・プロバイダ別・操作別に集計してくれます。**APM → AI Agent Monitoring → AI overview** を開きます。

規約に沿わせてあれば、こちらが Splunk 側で何も設定しなくても、次の集計がそのまま出ます。

* **Requests / Errors**：`chat` span の件数とエラー率（`gen_ai.operation.name=chat` を認識）
* **Tokens**：入力・出力トークンの合計（`gen_ai.usage.input_tokens` / `gen_ai.usage.output_tokens`）
* **Performance by Latencies**：`gen_ai.request.model`（モデル）・`gen_ai.provider.name`（`anthropic`）・操作（`chat`）ごとのレイテンシ（p50/p90/p99）
* **Token Usage and Cost**：モデル別のトークン推移と推定コスト

![Splunk AI Agent Monitoring の AI overview](https://static.zenn.studio/user-upload/deployed-images/3d5953f4fd1902c3ac4531d5.png?sha=b38f3cba639b0cbd3c4f93f0038a4d74d20812f2)

*Splunk AI Agent Monitoring（AI overview）：`gen_ai.*` 規約に沿わせた Claude 呼び出しを自動認識し、リクエスト数・トークン・モデル別レイテンシを集計する。*

> **「規約に沿わせる見返り」がここに出ます。** こちらは Splunk 専用の属性を一切足していません。`gen_ai.request.model` や `gen_ai.usage.*` という共通名で載せておいただけで、Splunk が「これは Claude の chat 呼び出し」と解釈し、モデル別の画面を自動で組み立てます。「LLM 呼び出しを OpenTelemetry で計測する」と「その計測を Splunk の AI 機能に読み解かせる」が、ここでつながります。

### コスト表示の注意：ベンダー推定は新モデルに追従しない

AI overview の **Estimated cost** は、Splunk 内部の**モデル別単価テーブル**で計算します。新しいモデル（本稿の `claude-opus-4-8` など）は単価テーブルに無いことがあり、その場合**トークンは集計されてもコストは $0 のまま**になります。

これは壊れているのではなく、**ベンダーのコスト推定はモデルの新発売に遅れる**という性質です。だから本連載の計装では、コストを**自前のメトリクス** `gen_ai.client.cost.usd`（単価は設定値）でも持たせています。Splunk の **Metrics** で `gen_ai.client.cost.usd` を選べば、ベンダー推定が未対応でも**自分の単価での実額**を追えます。「ベンダーの自動集計」と「自前メトリクス」は、こうして役割を分けて共存させます。

## つまずきポイントと解決

送信先を SaaS に向けるときは、ローカルでは起きなかった点でつまずきます。

* **認証は通るのにデータが出ない**：**realm の取り違え**が最有力です。エンドポイントの `<realm>` が、プロフィールに表示された値と一致しているか確認します。
* **送ったのに APM / AI overview に出てこない**：**取り込みのラグ**（数十秒〜数分）が主因です。少し待って画面を更新します。集計ビューは直近の窓（`-15m` など）で見るので、トラフィックを数回流すと確実です。
* **トークンの種別を間違える**：取り込みには\*\*アクセストークン（Access Token）\*\*を使います。API 用トークンや、ユーザーのセッショントークンでは取り込めません。
* **属性が Splunk 側で扱いづらい**：自己流の属性名だと検索やダッシュボードに乗りにくいです。**GenAI 規約名**（`gen_ai.request.model` など）に寄せておくと、APM でも素直に扱えます。
* **ローカル構成と二者択一に見える**：そうではありません。Collector のエクスポータを増やせば、**ローカルの Jaeger と Splunk へ同時に**送れます。移行期は併送しておくと安全です。
* **AI overview の Estimated cost が $0 のまま**：新しいモデルが Splunk の単価テーブルに無いためです（トークンは集計されます）。自前の `gen_ai.client.cost.usd` メトリクスを併用すれば実額を追えます。
* **トライアルの期限**：無料トライアルには期間があります。検証とスクリーンショットの取得は、期間内にまとめて済ませます。

## まとめ

「ローカルで計測する」から「Splunk Observability Cloud で運用する」への移行は、計装を変えずに**送信先だけ**で済みます。

* OpenTelemetry は**計装と送信先が分離**している。Splunk へは**エンドポイントと `X-SF-Token`** で向けられる
* 最小なら**アプリから直接 OTLP**、本番なら**Splunk 配布の Collector 経由**（realm・トークンを環境変数で渡すだけ）
* **Splunk APM** で `chat <model>` の span と `gen_ai.*` 属性を確認でき、**AI Agent Monitoring** がそれを自動集計してモデル別のリクエスト・トークン・レイテンシを出す
* コスト推定は新モデルに追従しないことがある。自前の `gen_ai.client.cost.usd` を併用すると実額を追える
* realm とトークン種別の取り違えが定番のつまずき。GenAI 規約名に寄せておくと SaaS 側でも扱いやすい

LLM 呼び出しを計測し、その計測を Splunk の AI 機能に自動で読み解かせる——可観測性と AI が、ここで一周します。計装を規約に沿わせておくほど、その一周は滑らかになります。

ここでは「送信先を Splunk へ切り替える」ことに絞りましたが、**仕様定義から実装・テスト・デプロイまで**を Claude Code と一気通貫で進める流れは、拙著にまとめています。Spring Security / JPA / Flyway や本番デプロイ（Railway）まで、AI と対話しながら1つのWebアプリを完成させる構成です。

📘 『**Claude Codeと生み出す Spring Boot実践開発 ～AI日記アプリを仕様定義からデプロイまで～**』

※ Amazon のリンクはアフィリエイトリンクを含みます。
