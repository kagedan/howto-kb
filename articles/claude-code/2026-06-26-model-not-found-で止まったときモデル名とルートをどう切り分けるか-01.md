---
id: "2026-06-26-model-not-found-で止まったときモデル名とルートをどう切り分けるか-01"
title: "model_not_found で止まったとき、モデル名とルートをどう切り分けるか"
url: "https://qiita.com/FlatkeyAI/items/c8a4c40e2db641696235"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "OpenAI", "Gemini", "qiita"]
date_published: "2026-06-26"
date_collected: "2026-06-27"
summary_by: "auto-rss"
query: ""
---

## はじめに

OpenAI 互換の API client から Claude や Gemini 系の model id を投げるとき、`model_not_found` で止まることがあります。

最初は私も「model 名を typo したかな」とだけ見ていたのですが、実際には model id、今の API key で見える model list、endpoint type、group、upstream の availability が混ざっていました。ここを一緒に見てしまうと、少し遠回りになると思います。

この記事では、Flatkey の OpenAI 互換 endpoint で確認した実レスポンスを例に、`model` だけを差し替えながら切り分ける手順を残します。Flatkey 固有の話というより、OpenAI 互換 API を複数 model で使うときの見方として読めるはずです。

## 再現環境

確認日は 2026-06-21 です。

| 項目 | 値 |
|---|---|
| client | `curl` |
| Chat Completions endpoint | `https://router.flatkey.ai/v1/chat/completions` |
| public catalog | `https://router.flatkey.ai/api/pricing` |
| authenticated model list | `GET https://router.flatkey.ai/v1/models` |
| 成功確認に使った model | `gemini-2.5-flash-lite` |
| 意図的に失敗させた model | `definitely-not-a-real-model-issue-88` |

API key は環境変数から読み、記事中では必ず伏せています。

## エラー全文

意図的に存在しない model id を投げたときのレスポンスです。

```json
{
  "error": {
    "code": "model_not_found",
    "message": "分组 company-employees 下模型 definitely-not-a-real-model-issue-88 无可用渠道（distributor） (request id: 202606210036523703855498268d9d6rcUO4Wqc)",
    "type": "new_api_error"
  }
}
```

HTTP status は `503` でした。ここは gateway や provider によって `404` などになるかもしれません。大事なのは status だけでなく、body の `code`、`message`、`request id` を一緒に見ることだと思います。

この message には、少なくとも次の情報が入っています。

| 見る場所 | 何が分かるか |
|---|---|
| `definitely-not-a-real-model-issue-88` | 今回投げた model id |
| `company-employees` | この request が見ている group |
| `无可用渠道（distributor）` | その group で利用できる channel がないこと |

## 3行まとめ

- まず public catalog と authenticated `/v1/models` を分けて見ます。
- 次に model の endpoint type と、投げている API path が合っているかを見ます。
- 最後に同じ curl で `model` だけを差し替え、auth と base URL の問題を切り離します。

## 調査順のテンプレート

私なら次からは、いきなり SDK の中を追わずに、次の順番で見ます。SDK は便利ですが、env、default model、retry、middleware が挟まると、どこで値が変わったのか見えにくくなることがあるためです。

| 順番 | 確認するもの | 見たいこと |
|---:|---|---|
| 1 | endpoint host | その key の発行元と base URL が合っているか |
| 2 | API path | model の endpoint type と path が合っているか |
| 3 | `/v1/models` | 今の key でその model id が見えるか |
| 4 | public catalog | group、endpoint type、availability がどう見えるか |
| 5 | positive control | 近い model に差し替えると同じ request が通るか |
| 6 | SDK 設定 | curl で通った値が SDK に同じ形で渡っているか |

この順番にすると、`model_not_found` を「model 名が存在しない」だけでなく、「この key と route では使えない」として読めます。細かいようですが、support に渡す情報もこの順にそろうので、あとで説明しやすいと思います。

## まず catalog と `/v1/models` を分けて見る

public catalog に載っていることと、今の API key、account、group で使えることは別です。ここを混ぜると「catalog にはあるのになぜ」となりがちです。私はここを一度混ぜてしまいました。

Flatkey の public catalog は次のように確認できます。

```bash
curl -s https://router.flatkey.ai/api/pricing \
  | jq '.data[] | select(.model_name == "gemini-2.5-flash-lite")'
```

確認時点の public catalog は、638 model rows、23 vendors、`pricing_version=a42d372ccf0b5dd13ecf71203521f9d2` でした。

一方で、同じ日に authenticated `/v1/models` で見えた model は 47 件でした。つまり「全体 catalog」と「この key で見える list」は別物として扱う方が安全です。

```bash
curl -s https://router.flatkey.ai/v1/models \
  -H "Authorization: Bearer sk-fk-********" \
  | jq '.data[].id'
```

`/v1/models` に出てこない id を使っているなら、typo ではなく現在の key、account、group では使えない model として見るのがよさそうです。

## endpoint type と route を見る

OpenAI 互換 client から呼ぶ場合でも、すべての model が同じ path で動くとは限りません。public catalog には endpoint type と path の対応がありました。

| endpoint type | method | path |
|---|---|---|
| `openai` | `POST` | `/v1/chat/completions` |
| `openai-response` | `POST` | `/v1/responses` |
| `anthropic` | `POST` | `/v1/messages` |
| `gemini` | `POST` | `/v1beta/models/{model}:generateContent` |
| `image-generation` | `POST` | `/v1/images/generations` |
| `openai-video` | `POST` | `/v1/video/generations` |

たとえば `/v1/chat/completions` に投げるなら、その model が `openai` endpoint type を持っているかを先に見ます。Claude や Gemini の名前が入っている model でも、OpenAI 互換 route で受けられる形に用意されているかは別の確認です。

## group/provider を見る

今回の error body には `company-employees` という group が出ていました。model catalog 上の group と、request が実際に通る group がずれていると、model 名が正しそうに見えても失敗することがあります。

public catalog 側では、確認時点で次のような group が見えていました。

| group | article note |
|---|---|
| `Economy` | 汎用 model の低コスト寄り group として使われていた |
| `Standard` | 公式系 resource を含む group として使われていた |
| `Claude Economy` | Claude Code 系の cost effective group として使われていた |
| `Claude Official` | Claude Code 系の official resource group として使われていた |

group 名や availability は変わる可能性があるので、記事や runbook に書くときは確認日を添えるのがよいと思います。固定の真実として書くと、あとで自分が困ります。

## SDK 側の `model` と `base_url` を見る

curl で切り分ける前に、SDK 側で古い値を握っていることもあります。特に私は、env の `MODEL` とコード中の default model がずれているケースを見落としがちです。

見る場所はだいたいこのあたりです。

| 見る場所 | ありがちなずれ |
|---|---|
| `base_url` | provider 公式 endpoint と gateway endpoint が混ざっている |
| `api_key` | endpoint と違う発行元の key を使っている |
| `model` | 古い model id、provider prefix ありなし、preview 名のまま |
| request path | `chat/completions` と `responses` と provider-native path が混ざっている |

最小の env はこのくらいにしておくと、差し替え箇所が見えやすいです。

```bash
export OPENAI_BASE_URL="https://router.flatkey.ai/v1"
export OPENAI_API_KEY="sk-fk-********"
export MODEL="gemini-2.5-flash-lite"
```

SDK の前に curl で同じ値を使うと、SDK の初期化ミスと API route の問題を分けやすくなります。

## curl で `model` だけ差し替える

私が一番早いと思った切り分けは、同じ request body で `model` だけ変えることです。

まず失敗する request です。

```bash
curl https://router.flatkey.ai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-fk-********" \
  -d '{
    "model": "definitely-not-a-real-model-issue-88",
    "messages": [
      { "role": "user", "content": "ping" }
    ],
    "max_tokens": 2
  }'
```

次に、同じ body で `model` だけを `gemini-2.5-flash-lite` にします。

```bash
curl https://router.flatkey.ai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-fk-********" \
  -d '{
    "model": "gemini-2.5-flash-lite",
    "messages": [
      { "role": "user", "content": "ping" }
    ],
    "max_tokens": 2
  }'
```

この positive control は HTTP 200 になり、要約すると次の結果でした。

```json
{
  "http_status": 200,
  "model": "gemini-2.5-flash-lite",
  "choices_len": 1,
  "first_content": "ok",
  "usage": {
    "prompt_tokens": 4,
    "completion_tokens": 1,
    "total_tokens": 5
  }
}
```

同じ key、同じ base URL、同じ path、同じ headers で片方だけ成功するなら、auth や base URL よりも model id、group、endpoint type、runtime availability を疑う方が筋がよさそうです。

## catalog にあるのに落ちるケース

もうひとつ紛らわしかったのが、catalog に出ている model でも runtime で落ちるケースです。

確認時点で `gemini-2.0-flash-lite` は catalog/list 側に見えましたが、Chat Completions で投げると upstream 側から次の 404 が返りました。

```json
{
  "error": {
    "message": "This model models/gemini-2.0-flash-lite is no longer available. Please update your code to use a newer model for the latest features and improvements.",
    "type": "upstream_error",
    "param": "",
    "code": 404
  }
}
```

これは `model_not_found` とは別ですが、調査順としてはかなり近いです。catalog の存在確認だけで終わらせず、`availability_status` や実レスポンスまで見る必要がある、という例だと思います。

## よくある読み違い

今回のメモを runbook にするなら、私は次の読み違いを先に潰します。

| 読み違い | 実際に見ること |
|---|---|
| catalog にあるから呼べる | authenticated `/v1/models` と group を見る |
| OpenAI 互換だから全部 `/v1/chat/completions` | endpoint type と path を見る |
| 401 ではないから key は無関係 | key に紐づく account、group、quota を見る |
| 近い model が成功したから全部正常 | 失敗した model 個別の availability を見る |
| SDK の `model` を変えたから変わっている | curl の request body で実際の値を見る |

特に「OpenAI 互換」という言葉は、client の形を合わせられるという意味であって、すべての provider-native model が同じ route にそのまま生えている、という意味ではない場合があります。ここを雑に読むと、私のように model 名だけを何度も書き換えることになります。

## 解決しないときに support に送るもの

自分で切り分けても分からないときは、support に送る情報をそろえた方が早いです。API key そのものや private prompt は送らない前提です。

| 項目 | 例 |
|---|---|
| HTTP status | `503` |
| error code | `model_not_found` |
| error body | redacted JSON |
| request id | response body に入っていた id |
| endpoint host/path | `https://router.flatkey.ai/v1/chat/completions` |
| model id | `gemini-2.5-flash-lite` など |
| request timestamp | timezone 付き |
| positive control | 同じ curl で成功した model があるか |

この形にしておくと、「key が悪いのか」「route が悪いのか」「model availability が悪いのか」を相手も見やすいと思います。

## おわりに

`model_not_found` は model 名の typo だけでなく、今の key で見える model list、endpoint type、group、upstream availability の問題として読むと切り分けやすかったです。

私の場合は、最初に catalog だけ見てしまい、runtime の availability と authenticated `/v1/models` を分けるのが少し遅れました。今後はまず curl で `model` だけ差し替え、成功する近い model を positive control にしてから SDK 側へ戻ると思います。

同じように Claude、Gemini、DeepSeek などを OpenAI 互換 client から呼んでいて詰まった方は、どの model id と endpoint type の組み合わせで止まったかをコメントでもらえると助かります。

間違いあったらコメントください。よろしくお願いします。
