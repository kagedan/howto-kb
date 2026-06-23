---
id: "2026-06-22-openai-sdk-の-base-url-だけ変えて-claude-と-gemini-を呼んでみた-01"
title: "OpenAI SDK の `base_url` だけ変えて Claude と Gemini を呼んでみた"
url: "https://qiita.com/FlatkeyAI/items/c8dca7b7f49ad3f62c2f"
source: "qiita"
category: "ai-workflow"
tags: ["API", "LLM", "OpenAI", "Gemini", "GPT", "Python"]
date_published: "2026-06-22"
date_collected: "2026-06-23"
summary_by: "auto-rss"
query: ""
---

## はじめに

OpenAI SDK を使った小さい検証スクリプトは、手元にいくつかあります。

ただ、別のモデルを試したくなるたびに SDK や認証まわりを増やしていくと、比較用のコードがだんだん読みにくくなります。Claude を見るために別の client を足し、Gemini を見るためにまた別の client を足し、最後に「あれ、この差分はモデルの差なのか SDK の差なのか」となるやつです。私はよくやります。

今回は、OpenAI SDK の呼び出し形をほぼそのままにして、`base_url` と API key と `model` だけを変える構成を試しました。使ったのは Flatkey の OpenAI-compatible な router です。

この記事は 2026-06-22 時点の手元検証です。モデル ID や価格は変わる可能性があるので、実運用では必ず pricing と dashboard を見直してください。

## なぜ SDK を増やしたくなかったか

Claude には Claude の SDK があり、Gemini には Gemini の SDK があります。各 provider の機能を深く使うなら、それぞれの SDK を使うのが自然だと思います。

ただ、最初の比較段階では少し事情が違います。たとえば「この要約タスクは Claude と Gemini のどちらが読みやすいか」「同じプロンプトで失敗しやすいモデルはどれか」「費用を見ながら軽いモデルに逃がせるか」くらいを見たいだけなら、SDK の差分が大きいほど検証結果を読み違えやすくなります。

私の場合、検証スクリプトはあとから notebook や小さい batch に貼り替えることが多いです。そのとき provider ごとの import、client 初期化、レスポンス構造の違いが増えると、あとで自分が読んでもつらくなります。なので今回は、まず OpenAI SDK の形に寄せたまま、どこまでモデルだけ差し替えられるかを見ました。

## 3 行まとめ

- OpenAI Python SDK は `OpenAI(api_key=..., base_url=...)` で向き先を変えられました。
- Flatkey では `https://router.flatkey.ai/v1` を `base_url` にして、Claude と Gemini のモデル ID を差し替えて呼べました。
- `/v1/models` に出るだけでは安心しきれず、最後は小さいリクエストで `usage.total_tokens` まで見るのがよさそうでした。

## 検証環境

今回の手元環境はこれです。

```bash
python3 --version
# Python 3.12.3

python -c "import openai; print(openai.__version__)"
# 2.43.0
```

環境変数はこう置きました。実キーはもちろん記事にもログにも出しません。

```bash
export FLATKEY_API_KEY="sk-fk-..."
export FLATKEY_BASE_URL="https://router.flatkey.ai/v1"
export CLAUDE_MODEL="claude-haiku-4-5"
export GEMINI_MODEL="gemini-2.5-flash"
```

`openai` package は、今回の検証では次のように入れました。

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install "openai==2.43.0"
```

## まず普通の OpenAI SDK サンプルを置く

元のコードは、よくある `chat.completions.create` の形です。

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
)

response = client.chat.completions.create(
    model=os.environ.get("OPENAI_MODEL", "gpt-5.5"),
    messages=[
        {"role": "user", "content": "次の文字列だけを返してください: sdk-ok"},
    ],
    max_tokens=32,
    temperature=0,
)

print(response.choices[0].message.content)
```

ここではモデル名そのものより、`client` を作って `chat.completions.create(...)` を呼んでいる形だけ見ています。

この形をなるべく崩さず、Claude と Gemini に投げたい、というのが今回の目的です。

比較用のプロンプトも、最初はかなり小さくしました。長い文章生成や tool call をいきなり試すと、失敗したときに原因が endpoint なのか、モデル ID なのか、パラメータなのか、プロンプトなのかが見えにくくなるためです。

今回は「指定文字列だけ返す」という味気ないプロンプトにしています。記事としては地味ですが、疎通確認ではこれくらい退屈なほうが切り分けしやすいと思います。

## `base_url` と API key だけ差し替える

Flatkey の router を使う場合、差分は client 初期化のところに集まります。

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["FLATKEY_API_KEY"],
    base_url=os.environ.get("FLATKEY_BASE_URL", "https://router.flatkey.ai/v1"),
)
```

ここで `base_url` に入れるのは `/v1` までです。`/chat/completions` まで足した URL を入れると、SDK 側がさらに path を足すため、意図しない URL になる可能性があります。

Flatkey の公開ページでも OpenAI-compatible base URL として `https://router.flatkey.ai/v1` が案内されていました。以前見たメモでは別 URL と揺れていたのですが、今回の確認では router 側の `/v1/models` も HTTP 200 で返りました。

この変更は、既存コードに対してはかなり小さいです。実際には次のような差分になります。

```diff
- client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
+ client = OpenAI(
+     api_key=os.environ["FLATKEY_API_KEY"],
+     base_url="https://router.flatkey.ai/v1",
+ )
```

もちろん production のコードで URL を直書きするかは別問題です。私は `.env` や secret manager 側に寄せたほうが、検証環境と本番環境を切り替えやすいと思います。

## Claude と Gemini を同じ loop で呼ぶ

次に、モデル ID だけを配列にして回します。

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["FLATKEY_API_KEY"],
    base_url=os.environ.get("FLATKEY_BASE_URL", "https://router.flatkey.ai/v1"),
)

models = [
    ("claude", os.environ.get("CLAUDE_MODEL", "claude-haiku-4-5")),
    ("gemini", os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")),
]

for label, model in models:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": "次の文字列だけを返してください: flatkey-ok"},
        ],
        max_tokens=32,
        temperature=0,
    )

    text = response.choices[0].message.content
    total_tokens = response.usage.total_tokens if response.usage else None

    print(f"{label}\t{model}\t{text}\ttotal_tokens={total_tokens}")
```

手元では次のようになりました。

```text
claude  claude-haiku-4-5  flatkey-ok  total_tokens=31
gemini  gemini-2.5-flash  flatkey-ok  total_tokens=37
```

この時点で、少なくとも「同じ OpenAI SDK の `chat.completions.create` から Claude と Gemini に届く」ことは確認できました。

ここで見たいのは、返答の賢さではありません。まずは認証、endpoint、モデル ID、レスポンス取り出し、usage の有無を見ています。

本文の比較や評価を始めるのは、このあとでよいと思います。最初の一発で長文生成まで試すと、失敗時の情報が増えすぎます。私はこういう検証を焦ってまとめてやると、あとでログを見返したときに「どの変更で動いたのか」が分からなくなるので、疎通確認と品質評価は分けるようにしています。

## モデル ID の選び方

今回のモデル ID は、router の `/v1/models` で候補を見てから、小さいリクエストを通して選びました。

Claude 側は `claude-haiku-4-5` を使いました。記事用の疎通確認なので、重いモデルを選ぶ理由があまりなかったためです。Gemini 側は `gemini-2.5-flash` を使いました。`gemini-2.5-flash-lite` も動きましたが、記事内の例としては `gemini-2.5-flash` のほうが読み手に伝わりやすいと判断しました。

モデル一覧には preview や latest 系の ID もあります。便利そうに見えますが、記事や社内手順に残すなら、私は固定 ID を優先します。`latest` は追従してくれる反面、あとで同じ記事を読んだ人の実行結果が変わりやすいからです。

## curl でも最小確認する

SDK の前に router 自体を見たい場合は、`/v1/models` を叩くのが手早いです。

```bash
curl -sS \
  -H "Authorization: Bearer $FLATKEY_API_KEY" \
  "$FLATKEY_BASE_URL/models" \
  | jq -r '.data[]?.id' \
  | grep -Ei 'claude|gemini' \
  | head
```

今回の環境では、Claude 系と Gemini 系の ID が複数返ってきました。

```text
claude-haiku-4-5
claude-opus-4-7
claude-sonnet-4-6
gemini-2.5-flash
gemini-2.5-flash-lite
gemini-3-flash-preview
```

ただし、ここで出た ID がすべて今すぐ期待どおりに動くとは限らないと思います。実際、私の手元では `gemini-2.0-flash-lite` が一覧にありましたが、`chat.completions` では upstream から 404 が返りました。

なので、モデル一覧は候補探しに使い、記事や設定に書くモデル ID は小さいリクエストで一度通すのが安全そうです。

## usage と pricing も見る

疎通確認だけなら、レスポンス本文が返れば終わりにしたくなります。

ただ、複数モデルを同じ gateway から使う場合は、どのモデルに投げたのか、トークン数が取れているのか、あとから dashboard で追えるのかを見ておいたほうがよさそうです。

今回のコードでは、可能なら `response.usage.total_tokens` を出すようにしました。

```python
total_tokens = response.usage.total_tokens if response.usage else None
print(total_tokens)
```

また、Flatkey 側では pricing page と dashboard が分かれているので、私は次を確認対象にしました。

- 対象モデルが pricing page に載っているか
- 価格や provider の表記が想定と違わないか
- dashboard 側で usage や billing の記録を追えるか
- key、request id、メールアドレスなどをスクリーンショットに出していないか

この記事では、価格の数字はあえて書きません。価格表は更新されるものなので、記事本文に数字を固定するより、読者が見るべき場所を残すほうが事故が少ないと思ったためです。

もう少し実務寄りに見るなら、次の観点も足したいです。

- 同じリクエストを再実行したときに、同じモデルへ投げられているか
- 失敗時の status code と message がアプリ側のログに残るか
- 予算や quota を超えそうなときに dashboard 側で気づけるか
- provider を切り替えたときに、レスポンス本文以外の周辺フィールドに依存していないか

特に最後は少し危ないです。サンプルでは `choices[0].message.content` と `usage.total_tokens` だけを見ていますが、実アプリでは finish reason や tool call などに依存していることがあります。その場合は「OpenAI SDK で呼べた」だけで安心せず、アプリが実際に読んでいるフィールドまで確認したほうがよいと思います。

## 既存コードへ入れるなら

今回のサンプルは単体スクリプトですが、既存アプリに入れるなら、私は client 作成部分だけを関数に寄せると思います。

```python
import os
from openai import OpenAI

def build_llm_client() -> OpenAI:
    return OpenAI(
        api_key=os.environ["FLATKEY_API_KEY"],
        base_url=os.environ["FLATKEY_BASE_URL"],
    )
```

呼び出し側は、できるだけ `client.chat.completions.create(...)` のままにしておきます。そうしておくと、OpenAI 直呼びに戻す検証や、別 gateway との比較もやりやすいです。

ただし、全機能が完全に同じとは考えないほうがいいです。特定 provider 固有の機能、Responses API 前提の機能、画像や音声など endpoint が違う機能は、今回の `chat.completions` サンプルとは別に確認が必要です。この記事では、あくまで text chat の最小疎通だけを扱っています。

## ハマったところ

### `base_url` に path を足しすぎない

OpenAI SDK の client に渡すのは `https://router.flatkey.ai/v1` です。

`https://router.flatkey.ai/v1/chat/completions` を `base_url` に入れると、SDK のリソース path と重なります。私は gateway 系の検証でこの手のミスを何度かやっているので、まずここを疑うようにしています。

### モデル一覧だけで確定しない

`/v1/models` は便利ですが、実リクエストが通るかどうかは別でした。

今回も、一覧に出た Gemini の古い ID で 404 が返りました。記事にするなら「一覧にあった」ではなく「この ID で実際に小さく投げた」まで確認したほうがよさそうです。

### usage が返る前提にしすぎない

今回の 2 モデルでは `usage.total_tokens` が見えました。

ただし、gateway や upstream の組み合わせによっては usage の形が変わることもあるかもしれません。サンプルコードでは `if response.usage else None` にしておくと、検証中に余計なところで落ちにくいです。

### key を出さない

これは当たり前なのですが、記事化するときほど危ないです。

検証ログ、スクリーンショット、curl の履歴、dashboard 画像に key や account 情報が残っていないかは、投稿前にもう一回見たほうがいいと思います。私はこういう見落としが怖いので、記事に載せるコマンドは全部 `$FLATKEY_API_KEY` だけにしています。

### 成功ログを小さく残す

私は今回、成功時に model、短い出力、total tokens だけを残しました。

本当は response object を丸ごと見たくなりますが、記事に貼るログとしては情報量が多すぎますし、将来どのフィールドが sensitive になるかも分かりません。まずは、再現に必要な最小ログだけ残すほうが扱いやすいと思います。

エラー時も同じで、全文をそのまま貼る前に、key や account 情報が混ざっていないか確認したほうがいいです。今回の `gemini-2.0-flash-lite` の 404 は、モデル ID が古い可能性を示す情報としては有用でしたが、そのまま本文に大きく貼る必要はないと判断しました。

## まとめ

OpenAI SDK の既存コードから Claude と Gemini を触るだけなら、今回の範囲ではかなり小さい差分で済みました。

主な変更点はこの 3 つです。

- `api_key` を Flatkey 用にする
- `base_url` を `https://router.flatkey.ai/v1` にする
- `model` を `claude-haiku-4-5` や `gemini-2.5-flash` にする

個人的には、SDK を増やさず比較できるのはありがたいです。一方で、モデル ID と pricing は固定知識にしないほうがよさそうでした。`/v1/models`、小さい実リクエスト、usage、pricing、dashboard までを一セットで見るのが、地味ですが一番安心だと思います。

手元の OpenAI SDK サンプルで `base_url` を差し替えて疎通し、必要なら Flatkey の pricing と dashboard を確認する、くらいの軽い入り方がちょうどよいかもしれません。

間違いあったらコメントください。よろしくお願いします。

## 参考

- [Flatkey](https://flatkey.ai/)
- [Flatkey Model Pricing](https://flatkey.ai/pricing)
- [OpenAI Python SDK](https://github.com/openai/openai-python)
