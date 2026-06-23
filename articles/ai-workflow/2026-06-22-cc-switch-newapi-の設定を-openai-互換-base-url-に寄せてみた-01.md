---
id: "2026-06-22-cc-switch-newapi-の設定を-openai-互換-base-url-に寄せてみた-01"
title: "CC Switch / NewAPI の設定を OpenAI 互換 base URL に寄せてみた"
url: "https://qiita.com/FlatkeyAI/items/54f663291b2ac4afd364"
source: "qiita"
category: "ai-workflow"
tags: ["API", "OpenAI", "Gemini", "qiita"]
date_published: "2026-06-22"
date_collected: "2026-06-23"
summary_by: "auto-rss"
query: ""
---

## はじめに

CC Switch と NewAPI 系の設定を触っていると、結局 `base URL`、`API key`、`model name` の 3 つをどこでそろえるのかで迷いました。

画面上では `Endpoint URL`、`API Address`、`base_url` など名前が少しずつ違うのに、最終的には OpenAI 互換の `/v1/chat/completions` に向ける、という場面が多いです。私も最初は「どの URL をどこまで入れるんだっけ」となったので、自分用の確認手順として残しておきます。

この記事では Flatkey を例にしますが、主役は宣伝ではなく、OpenAI 互換 API に寄せるときの確認順です。値はそのまま丸写しせず、自分のダッシュボードに表示されるものを優先してください。

## この記事で扱うこと

扱う範囲は次のあたりです。

- CC Switch 側で provider を追加するときに見る項目
- NewAPI / Flatkey 側で確認する `base URL` と `API key`
- `/v1/models` で使える model name を確認する流れ
- 最後に `curl` で Chat Completions 形式の疎通を見る流れ

逆に、Claude native Messages API への変換、Codex や Gemini CLI それぞれの細かい内部挙動、NewAPI のサーバ構築手順までは深く扱いません。そこまで混ぜると、私の理解も記事も散らかりそうでした。

## 前提環境

今回の確認では、OpenAI 互換の Chat Completions として呼べることを前提にしました。

| 項目 | 今回の例 |
|---|---|
| 接続先 | Flatkey の OpenAI 互換 API |
| base URL | `https://console.flatkey.ai/v1` |
| 確認モデル | `gemini-2.5-flash-lite` |
| モデル一覧 | 認証付き `GET /v1/models` で確認 |
| 疎通確認 | `POST /v1/chat/completions` |

Flatkey の過去の資料や環境によっては `https://router.flatkey.ai/v1` を見ることもあります。ここは記事の文字列より、自分のアカウントで表示されている URL を優先した方が安全だと思います。

## 設定項目表

先に表でそろえると、あとでかなり楽でした。

| 確認するもの | CC Switch 側で見る名前の例 | NewAPI / Flatkey 側で見る場所 | メモ |
|---|---|---|---|
| Base URL | `Endpoint URL` / `base_url` | ダッシュボードや token/provider の詳細 | 通常は `/v1` までを base URL として扱う |
| API key | `API Key` | key / token 管理画面 | 記録やスクショでは必ず隠す |
| Model name | `Main Model` / model list | `/v1/models` や model catalog | 認証付き model list に出る名前を使う |
| API format | OpenAI compatible / Chat Completions | NewAPI 側の API 形式 | この記事では `/v1/chat/completions` に寄せる |
| Full URL mode | Full URL Mode | CC Switch の詳細設定 | 完全な非標準 endpoint を入れるときだけ検討する |

私がハマりかけたのは、`base URL` と完全な endpoint URL を混ぜるところでした。たとえば `https://example.com/v1` を入れる想定の場所に、うっかり `https://example.com/v1/chat/completions` まで入れると、ツール側がさらにパスを足して変な URL になる可能性があります。

## NewAPI / Flatkey 側で確認する

NewAPI は OpenAI 標準形式と互換の統一 API entry point を持つ、という考え方です。Flatkey も同じように、1 つの key と OpenAI 互換 base URL に寄せて複数モデルを呼ぶ使い方になります。

まず見るのはこの 2 つです。

1. API key が発行されているか
2. OpenAI 互換の base URL がどれか

Flatkey の現行ページでは、例として次の形が出ています。

```text
https://console.flatkey.ai/v1
```

ただし、ここは固定値として覚えるより、ダッシュボードやドキュメント上の表示を確認する方が良いです。社内環境、プロキシ、旧 URL、移行中の URL が混ざると、記事のサンプルだけでは判断できないためです。

## CC Switch 側で provider を追加する

CC Switch の provider 設定では、OpenAI 互換 provider として扱うなら、だいたい次の順で入れます。

1. provider の名前を決める
2. API key を入れる
3. Endpoint URL / base URL を入れる
4. model name を入れる
5. 必要なら Fetch Models を押して一覧を取る

CC Switch の docs では、model-aware provider form で API key と Endpoint URL を使い、OpenAI 互換の `/v1/models` を呼んで model list を取得する流れが説明されています。

ここで大事なのは、model name を雰囲気で書かないことだと思います。公開 catalog に出ている名前、別のツールで使った名前、手元のメモにある名前が、今の key で必ず呼べるとは限りません。認証付き `/v1/models` に出たものを使うのが一番事故りにくいです。

## curl で model list を見る

まず model list を見ます。ここで返ってきた ID を、CC Switch の model 設定にも使います。

```bash
BASE_URL="https://console.flatkey.ai/v1"
API_KEY="sk-..."

curl "$BASE_URL/models" \
  -H "Authorization: Bearer $API_KEY"
```

今回の確認では、認証付き `/v1/models` で 47 件の model が返り、`gemini-2.5-flash-lite` が含まれていました。実際の記事やログに貼るときは、key、account 情報、request ID のようなものは残さない方がいいです。

## curl で Chat Completions を見る

次に小さい Chat Completions を 1 回だけ投げました。

```bash
BASE_URL="https://console.flatkey.ai/v1"
API_KEY="sk-..."
MODEL="gemini-2.5-flash-lite"

curl "$BASE_URL/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'"$MODEL"'",
    "messages": [
      { "role": "user", "content": "Reply with ok." }
    ],
    "max_tokens": 5
  }'
```

実行結果は、必要なところだけ抜くと次のような形でした。

```json
{
  "object": "chat.completion",
  "model": "gemini-2.5-flash-lite",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "ok."
      }
    }
  ],
  "usage": {
    "total_tokens": 7
  }
}
```

これで少なくとも、key、base URL、model name、Chat Completions の 4 点は一度に確認できます。CC Switch の画面で動かない場合も、この `curl` が通るかどうかで切り分けると見やすいです。

## ハマりやすいポイント

個人的には、次の表を見ながら確認すると戻りやすかったです。

| 症状 | 先に見るところ |
|---|---|
| `401` / `403` | API key、token の権限、有効期限 |
| `/v1/models` が `404` / `405` | provider が models endpoint を持つか、base URL が正しいか |
| `model_not_found` | model name が認証付き list にあるか、route/group が合っているか |
| URL が二重になる | `/v1` と `/chat/completions` をどこで足しているか |
| CC Switch だけ動かない | Full URL Mode を使うべき endpoint ではないか |

CC Switch docs では、通常は `base_url` を prefix として扱い、固定パスを後ろに足す挙動が説明されています。一方で、非標準の完全な endpoint を使う provider では Full URL Mode を使う、と読むのが自然そうです。

なので、OpenAI 互換の標準的な `/v1/chat/completions` に寄せるなら、まずは base URL をきれいにして、Full URL Mode は後回しでいいと思います。ここを最初から触ると、私なら余計に迷います。

## まとめ

CC Switch / NewAPI 系の設定は、項目名が少し違っても、見る順番を固定するとだいぶ整理できます。

- まず `base URL` を確認する
- 次に `API key` を入れる
- 認証付き `/v1/models` で `model name` を決める
- 最後に `/v1/chat/completions` を小さく投げる

Flatkey のような OpenAI 互換 gateway を使う場合も、記事の URL を暗記するより、自分のダッシュボードに出ている base URL と key を見て、`curl` で一度確認するのが一番手堅いと思いました。

## 参考

- Flatkey: https://flatkey.ai/
- CC Switch Add Provider docs: https://github.com/farion1231/cc-switch/blob/main/docs/user-manual/en/2-providers/2.1-add.md
- NewAPI CC Switch docs: https://www.newapi.ai/en/docs/apps/cc-switch
- NewAPI ChatCompletions docs: https://www.newapi.ai/en/docs/api/ai-model/chat/openai/createchatcompletion
- NewAPI Models docs: https://www.newapi.ai/en/docs/api/ai-model/models/list/listmodels

## おわりに

設定項目自体は少ないのに、`base URL` と endpoint の境目で毎回少し不安になります。自分もまだ環境差で見落とすことがありそうなので、間違いあったらコメントください。よろしくお願いします。
