---
id: "2026-06-23-claudegptgemini-を同じ評価表で比べるためのスクリプト-01"
title: "Claude・GPT・Gemini を同じ評価表で比べるためのスクリプト"
url: "https://qiita.com/FlatkeyAI/items/7d393f797f5419b84d87"
source: "qiita"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "LLM", "OpenAI", "Gemini", "GPT"]
date_published: "2026-06-23"
date_collected: "2026-06-24"
summary_by: "auto-rss"
query: ""
---

## はじめに

モデル比較をするとき、私はすぐ感想戦に寄ってしまいます。

「こっちの返答が自然」「こっちの方が速そう」「このモデルは賢い気がする」みたいな話は、雑談としては楽しいのですが、チームで後から見返すには少し弱いです。特に Claude、GPT、Gemini を同じ機能候補で比べると、プロンプトも評価メモもバラバラになりがちでした。

今回は、同じ prompt set を複数モデルに投げて、応答時間、usage、回答、ざっくり評価メモ欄を CSV に残す小さいスクリプトを書きました。性能を断定する記事ではなく、チームで比較を始めるための型として読んでもらえると近いです。

## 3行まとめ

- `models.csv` と `prompts.csv` を用意して、全組み合わせを順番に実行する
- `elapsed_ms`、`usage.total_tokens`、回答本文、エラーを同じ CSV に残す
- 点数とメモはあえて人間が後から埋める。自動採点より、まず評価表をそろえる

## この記事で比べないこと

先に線を引いておくと、この記事では「どのモデルが一番強いか」は決めません。

理由は、モデルの良し悪しがタスクでかなり変わるからです。問い合わせ分類では十分に見えるモデルでも、長い仕様書の要約では抜けが気になるかもしれません。逆に、長文回答がうまいモデルでも、短い JSON 生成では余計な説明を足して困ることがあります。

また、応答時間も固定値ではありません。同じモデルでも、時間帯、上流の混み具合、出力長、リトライ、ストリーミング有無で変わります。1回の実行結果をランキングにするより、同じ表に残して「もう一度同じ条件で試せる」状態にする方が、私の用途には合っていました。

この記事で作るのは、比較の結論ではなく、比較を始めるための台紙です。

## 前提

私の手元では、次の条件で確認しました。

| 項目 | 値 |
|---|---|
| Python | `3.12.3` |
| API 形式 | OpenAI 互換の `/chat/completions` |
| Base URL | `https://router.flatkey.ai/v1` |
| スクリプト依存 | Python 標準ライブラリのみ |

Flatkey は Claude、GPT、Gemini などを 1 つの API key / base URL から扱えるので、今回のように「同じコードでモデルだけ替える」検証には相性がよかったです。ただし、この記事の主役は Flatkey の機能紹介ではなく、比較表の作り方です。

モデル ID はアカウントや時期で変わるので、ここでは 2026-06-23 に私の環境で見えていた例として載せています。自分のダッシュボードや `/v1/models` で見える ID に置き換えてください。

## CSV を2つ用意する

まず、比較したいモデルを `models.csv` に書きます。

```csv
label,model
claude,claude-haiku-4-5
gpt,gpt-5.4-mini
gemini,gemini-2.5-flash-lite
```

次に、投げたいプロンプトを `prompts.csv` に書きます。実務では、ここを自分たちの問い合わせ、要約、分類、RAG 回答、コード修正などに置き換えるのが大事だと思います。

```csv
prompt_id,prompt_text
summarize,"次のメモを3行で要約してください。メモ: APIの利用量が増え、モデル別のコストと応答時間を週次で見たい。"
classify,"次の問い合わせを support / sales / bug のどれかに分類し、理由を1文で書いてください。問い合わせ: ダッシュボードのusageが昨日から増えている理由を知りたい。"
```

この2つを分けておくと、後からモデルだけ追加したり、prompt set だけ差し替えたりできます。私は最初、1つの JSON に全部書こうとしていましたが、チームで編集するなら CSV の方が雑に扱いやすいかもしれません。

## prompt set の選び方

prompt set は、本番で多い処理と、失敗すると困る処理を混ぜるのがよさそうです。

たとえば社内ツールなら、単純な要約だけでなく、問い合わせ分類、権限に関わる質問、曖昧な日本語、長い入力、短い出力形式指定を入れます。AI 機能の裏側で使うなら、RAG の回答、根拠の引用、JSON 生成、ツール呼び出し用の引数生成も候補になります。

逆に、デモ映えするプロンプトだけを入れると、比較表としては弱くなります。きれいに回答できる問題だけでは、本番で困る差が見えにくいからです。私は「普段ログに残っている失敗例を少し丸めて入れる」くらいが、最初の prompt set としてちょうどよいと思っています。

小さく始めるなら、まずは5問から10問で十分です。いきなり100問にすると、評価メモを書く人が疲れて、結局誰も見なくなります。最初は少ないプロンプトで表の形を決めて、必要になったら増やす方が続きやすいです。

## スクリプト

標準ライブラリだけで書いた版です。OpenAI SDK を使ってもよいのですが、この記事では依存を減らして、何を送って何を保存しているか見える形にしました。

```python
#!/usr/bin/env python3
import argparse
import csv
import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def call_model(base_url, api_key, model, prompt, max_tokens):
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": max_tokens,
    }
    req = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=60) as res:
            elapsed_ms = round((time.perf_counter() - started) * 1000)
            data = json.loads(res.read().decode("utf-8", "replace"))
            usage = data.get("usage") or {}
            answer = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return {
                "status": res.status,
                "elapsed_ms": elapsed_ms,
                "prompt_tokens": usage.get("prompt_tokens", ""),
                "completion_tokens": usage.get("completion_tokens", ""),
                "total_tokens": usage.get("total_tokens", ""),
                "answer": answer,
                "error": "",
            }
    except urllib.error.HTTPError as e:
        elapsed_ms = round((time.perf_counter() - started) * 1000)
        return {
            "status": e.code,
            "elapsed_ms": elapsed_ms,
            "prompt_tokens": "",
            "completion_tokens": "",
            "total_tokens": "",
            "answer": "",
            "error": e.read().decode("utf-8", "replace")[:1000],
        }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", default="models.csv")
    parser.add_argument("--prompts", default="prompts.csv")
    parser.add_argument("--out", default="model_eval_results.csv")
    parser.add_argument("--max-tokens", type=int, default=160)
    args = parser.parse_args()

    api_key = os.environ["FLATKEY_API_KEY"]
    base_url = os.environ.get("FLATKEY_BASE_URL", "https://router.flatkey.ai/v1")
    models = read_csv(args.models)
    prompts = read_csv(args.prompts)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    fieldnames = [
        "run_id",
        "timestamp_utc",
        "prompt_id",
        "prompt_text",
        "model_label",
        "model",
        "status",
        "elapsed_ms",
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
        "answer",
        "error",
        "eval_score_1_to_5",
        "eval_memo",
    ]

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for prompt_row in prompts:
            for model_row in models:
                result = call_model(
                    base_url,
                    api_key,
                    model_row["model"],
                    prompt_row["prompt_text"],
                    args.max_tokens,
                )
                writer.writerow(
                    {
                        "run_id": run_id,
                        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                        "prompt_id": prompt_row["prompt_id"],
                        "prompt_text": prompt_row["prompt_text"],
                        "model_label": model_row["label"],
                        "model": model_row["model"],
                        **result,
                        "eval_score_1_to_5": "",
                        "eval_memo": "",
                    }
                )


if __name__ == "__main__":
    main()
```

## 実行する

API key は環境変数に入れます。記事に貼るときは当然ですが本物の key は出さないようにします。

```bash
export FLATKEY_API_KEY="sk-..."
export FLATKEY_BASE_URL="https://router.flatkey.ai/v1"

python3 compare_models.py \
  --models models.csv \
  --prompts prompts.csv \
  --out model_eval_results.csv \
  --max-tokens 120
```

これで、`models.csv` のモデル数と `prompts.csv` のプロンプト数を掛けた行数が出ます。3モデル、2プロンプトなら6行です。

## 私の1回だけの結果

まず疎通確認として、次の短いプロンプトを3モデルに投げました。

```text
日本語で ok だけ返してください。
```

結果はこうでした。

| model | status | elapsed_ms | total_tokens | answer |
|---|---:|---:|---:|---|
| `claude-haiku-4-5` | 200 | 4820 | 24 | `ok` |
| `gpt-5.4-mini` | 200 | 1948 | 20 | `ok` |
| `gemini-2.5-flash-lite` | 200 | 1369 | 9 | `ok` |

この表だけで「Gemini が一番速い」みたいな結論にはしません。1回だけの短文プロンプトですし、経路、時間帯、上流状態、キャッシュ、出力長で簡単に変わります。ここで見たいのは、同じ列で記録できているかです。

次に、上の `prompts.csv` を使って6行の CSV も出しました。たとえば要約タスクでは、3モデルとも HTTP 200 で返り、`elapsed_ms` と `total_tokens` が同じ列に入りました。ここまでそろうと、後はチームの人が `eval_score_1_to_5` と `eval_memo` を埋められます。

## 評価メモは自動化しすぎない

最初は評価点も LLM に付けさせようと思いました。ただ、今回はやめました。

理由は単純で、最初の比較では「自分たちが何を良い回答と見なすか」をそろえる方が大事だからです。たとえば同じ要約でも、CS 向けなら丁寧さを見たいかもしれませんし、社内ログ向けなら短さと分類の安定性を見たいかもしれません。

私なら、最初の評価表ではこのくらいのメモ欄を見ます。

| 観点 | 見ること |
|---|---|
| 正確さ | 入力にないことを足していないか |
| 形式 | 指定した行数、分類名、JSON などを守っているか |
| 使いやすさ | そのまま UI や運用メモに入れられるか |
| コスト | `total_tokens` が想定より増えていないか |
| 失敗時 | HTTP status と error を見て再現できるか |

このあたりは、モデルの一般的な能力というより、自分たちの機能に対する相性だと思います。

## 評価会で見る順番

CSV が出たら、私は次の順番で見ます。

まず、HTTP status と error を見ます。失敗している行があるなら、品質以前にモデル ID、base URL、認証、パラメータ、上流エラーを切り分けます。失敗行を消してしまうと、後で「たまたま動いた結果」だけが残るので、エラーも同じ表に残すようにしています。

次に、指定形式を守っているかを見ます。要約なら行数、分類ならラベル、JSON ならパースできるかです。文章の好みより先に、機械的に落とせる条件を確認します。この段階で落ちるモデルは、プロンプトを直すか、用途から外すかを決めやすいです。

最後に、回答の中身を読みます。ここで初めて、自然さ、情報の抜け、余計な推測、プロダクトの語彙との相性をメモします。全員が同じ列を見ているので、「速いけど形式が崩れやすい」「少し遅いけど要約が安定する」みたいな議論がしやすくなります。

この順番にしておくと、モデルの好き嫌いだけで決まりにくくなります。私自身、最初は文章の雰囲気に引っ張られていましたが、表にすると少し冷静になれました。

## スコアは粗くてよい

`eval_score_1_to_5` は、最初から厳密な採点基準にしなくてもよいと思います。

私なら、1は使えない、3は要確認だが候補、5はその用途ならかなり良い、くらいの粗さで始めます。大事なのは、数字だけでなく `eval_memo` に理由を書くことです。「短い」「丁寧」だけでは後で思い出せないので、「分類ラベルは合っているが理由が長い」「根拠にない推測を1つ足した」くらいまで書けると、次のプロンプト改善に使えます。

複数人で見る場合は、全員の点数を平均するより、まずメモのズレを見る方が有益でした。ある人は正確さを見ていて、別の人は文体を見ていることがあるからです。そのズレ自体が、プロダクトとして何を重視するかの議論になります。

## ハマったポイント

### model ID は固定しすぎない

モデル名は変わります。アカウントで見えるモデルも変わります。

記事では例として `claude-haiku-4-5`、`gpt-5.4-mini`、`gemini-2.5-flash-lite` を使っていますが、そのまま永続的に使えると決めつけない方が安全です。実行前に `/v1/models` やダッシュボードで確認するのがよいと思います。

### usage の中身はプロバイダで少し違う

OpenAI 互換のレスポンスでも、`usage` の細かいフィールドはモデルや上流プロバイダで違うことがあります。この記事のスクリプトでは、共通で見やすい `prompt_tokens`、`completion_tokens`、`total_tokens` だけを CSV の主列にしています。

必要なら、生の usage JSON を別列に残すのもありです。ただ、最初から列を増やしすぎると評価表が読まれなくなるので、私はいったん削りました。

### 1プロンプトで勝敗を決めない

モデル比較で一番やりがちなのが、1つのプロンプトで「これは強い」「これは弱い」と言ってしまうことだと思います。私もついそう見てしまいます。

実務では、問い合わせ分類、長文要約、JSON 生成、曖昧な日本語指示、RAG の根拠付き回答など、最低でも数種類は入れたいです。さらに本当は、成功例だけでなく失敗しやすい境界ケースを入れた方がよいです。

## Flatkey でやった理由

今回 Flatkey を使った理由は、複数プロバイダの key と SDK を分けずに、同じ `/chat/completions` 形式で投げられるからです。比較のスクリプトでは、検証したい差分をなるべく「モデル ID」だけに寄せたいので、base URL と認証の形がそろっているのは楽でした。

また、実行後に usage や billing をダッシュボード側でも見られる前提にできるので、CSV 側の `total_tokens` と運用側の利用量を後で突き合わせやすいです。ここも数字を盛って語るところではなく、チームで確認するための材料だと思います。

## まとめ

Claude、GPT、Gemini を比べるとき、いきなり「どれが一番賢いか」を決めようとすると、話がふわっとしがちです。

私はまず、同じ prompt set、同じモデル一覧、同じ CSV 列で結果を残すところから始めるのがよさそうだと思いました。応答時間と usage は機械的に保存し、品質メモは人間が自分たちの用途に合わせて埋める。地味ですが、チームで後から議論しやすい形になります。

この記事の CSV テンプレートを自分たちの prompt set に置き換えるだけでも、最初の評価表にはなると思います。間違いあったらコメントください。よろしくお願いします。

## 参考

- Flatkey のダッシュボードで見える model catalog と `/v1/models`
- Qiita tag API
- OpenAI 互換の `/chat/completions` レスポンス形式
