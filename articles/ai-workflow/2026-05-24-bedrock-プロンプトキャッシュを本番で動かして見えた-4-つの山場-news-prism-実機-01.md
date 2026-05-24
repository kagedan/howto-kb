---
id: "2026-05-24-bedrock-プロンプトキャッシュを本番で動かして見えた-4-つの山場-news-prism-実機-01"
title: "Bedrock プロンプトキャッシュを本番で動かして見えた 4 つの山場 — News Prism 実機計測"
url: "https://qiita.com/tadokoro88/items/331782fca8c1c02bf3b7"
source: "qiita"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "Python", "qiita"]
date_published: "2026-05-24"
date_collected: "2026-05-24"
summary_by: "auto-rss"
query: ""
---

前回、自分の文脈で多角的にニュースを語る個人ツール **News Prism** を Bedrock で作った話を書きました。

https://qiita.com/tadokoro88/items/d9b463b5393460080c96

ここでは、その記事で軽く触れた **プロンプトキャッシュ** について、もう一段深掘りします。

News Prism は、1 つの記事 URL に対して Bedrock を 4 並列で叩き、中立要約 + 3 ペルソナの構造化 JSON を返す、個人用の News Reader アプリです。
プロンプトキャッシュを本番環境で利用するにあたり、ただ有効化するだけではない、いくつかの確認と設計判断が必要になりました。

本記事ではその 4 つを順に扱います。

- 新しいモデル (Sonnet 4.6) の仕様の実機検証
- キャッシュチェックポイントの設計
- 並列処理での独立キャッシュ設計
- コスト削減幅の把握

検証は **Anthropic 直接 API と Amazon Bedrock 経由の 2 経路で同条件**で行いました。
前提として Claude Sonnet 4.6 (`claude-sonnet-4-6` / `jp.anthropic.claude-sonnet-4-6` / ap-northeast-1)、2026-05 時点の挙動です。
これは今後変わる可能性があります。

# 1. Bedrock のプロンプトキャッシュとは？
本論に入る前に、公式ドキュメントに書かれている内容を整理します。

プロンプトキャッシュは、毎回ほぼ同じになるプロンプトプレフィックス (システムプロンプトや固定のコンテキスト) をキャッシュしておき、再利用時に入力トークンの再計算をスキップする機能です。
キャッシュチェックポイント (`cachePoint`) で「ここまでがプロンプトプレフィックス」というマーカーを置く形で使います。

https://docs.aws.amazon.com/ja_jp/bedrock/latest/userguide/prompt-caching.html

ポイントを整理すると次の通りです。

|観点|内容|
|:-|:-|
|対象|入力トークンのプロンプトプレフィックスを再利用 (出力には適用されない)|
|最小キャッシュ長|モデルごとに異なる (Sonnet 系の公式記載は 1,024 tokens)|
|TTL|デフォルト 5 分。一部モデルは 1 時間の延長 TTL もオプションで利用可能|
|料金倍率 (Anthropic 公式)|5 分書き込み 1.25x / 1 時間書き込み 2.0x / 読み出し 0.1x|
|自動マッチ|Claude モデルでは `cachePoint` を 1 つ置くだけで、最適なキャッシュマッチを自動で探してくれる|

https://platform.claude.com/docs/ja/build-with-claude/prompt-caching

News Prism での具体的な使い方は、下記のような構造です。

- プロンプトプレフィックス側 (cache 対象)：system prompt + tool 定義 + 指示文 + `<context>` ブロック (自分の目標と進捗)
- 可変部分：`<article>` ブロック (ニュース記事本文)

「毎回違う記事を投げても、プロンプトプレフィックスだけはキャッシュヒットする」状態を作るのが狙いです。

ちなみに 1h TTL の料金が 2.0x なのは「5 分用の cache write 1.25x」より重いということで、頻繁に書き換わるプロンプトプレフィックスだと逆にコストが増す場合もあります。
News Prism のように **1 つのプロンプトプレフィックスを 1 日に何度も読み返す** ユースケースでは、長めの TTL の方がコストメリットが出やすくなります。

# 2. 新しいモデルの仕様を実機で確かめる — Sonnet 4.6 の実効最小と TTL 1h
新しいモデルがリリースされると、公式ドキュメントの追従が後ろに回ったり、複数の出典で記載が食い違ったりすることがあります。
2026-05 時点で Sonnet 4.6 がまさにこの状況で、**AWS 公式 (en / ja) と Anthropic 公式 (en / ja) でそれぞれ記載状態に差** があり、Sonnet 4.6 を実機で動かしている開発者にとっては迷いやすい状況でした。
英語版が優先されると記述するドキュメントもありますが、英語版が常に最新の実態を表しているとは言い切れません。

そこで、実機で `cache_creation_input_tokens` / `cache_read_input_tokens` を出して、自分で確かめておきました。
結果としては実効最小は AWS / Anthropic の英語版と実機で一致した一方、Anthropic の日本語版は別の値を記載しており、1h TTL は AWS 公式 (en / ja) の記載とは異なる挙動が見えました。
新しいモデルを業務で使う場合、**ドキュメントの追従や食い違いを待たずに実機で確かめる** ようにすると安心して判断を進められます。

## 公式ドキュメントの状態 (2026-05 時点)
2026-05 時点で、両者の Sonnet 4.6 への言及は以下のように分かれています。

|出典|Sonnet 4.6 最小 cache 長|Sonnet 4.6 の 1h TTL|
|:-|:-|:-|
|[AWS 公式 (en)](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html)|**1,024 tokens**|**5 分のみ** (Sonnet 4.5 は対応)|
|[AWS 公式 (ja)](https://docs.aws.amazon.com/ja_jp/bedrock/latest/userguide/prompt-caching.html)|**記載なし**|**記載なし** (Sonnet 4.5 まで)|
|[Anthropic 公式 (en)](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)|**1,024 tokens**|**対応**|
|[Anthropic 公式 (ja)](https://platform.claude.com/docs/ja/build-with-claude/prompt-caching)|**2,048 tokens**|**対応**|

整理すると以下の食い違い・追従ラグが見えます。

- **実効最小**: AWS 公式 (en) と Anthropic 公式 (en) は 1,024 と明示。**Anthropic 公式 (ja) は 2,048 と記載しており、en と食い違っている**。AWS 公式 (ja) は Sonnet 4.6 自体が未記載
- **1h TTL**: AWS 公式 (en / ja) は Sonnet 4.6 を 1h 対応モデルとして挙げていない。一方で Anthropic 公式 (en / ja) は「対応 (Amazon Bedrock 含む)」と明記
- **モデル ID**: AWS 公式 (en) では `anthropic.claude-sonnet-4-6` と記載 (`-v1:0` などの suffix なし) で、リリース型は GA 扱い

これらを踏まえて、実機で 2 経路の挙動を確認してみました。

## 検証スクリプト
Anthropic SDK は `Anthropic` (直接) と `AnthropicBedrock` (Bedrock 経由) の 2 つを同じパッケージから使えます。
両者でシステムプロンプトのサイズを倍率で変えながら二分探索をかけました。

<details>
<summary>検証用 Python コード例</summary>

```python
from anthropic import Anthropic, AnthropicBedrock

def _make_client(provider: str):
    if provider == "anthropic":
        return Anthropic(), "claude-sonnet-4-6"
    else:
        return AnthropicBedrock(aws_region="ap-northeast-1"), "jp.anthropic.claude-sonnet-4-6"

def call(client, model_id, system_prompt):
    response = client.messages.create(
        model=model_id,
        max_tokens=64,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral", "ttl": "1h"},
            }
        ],
        messages=[{"role": "user", "content": "ping"}],
    )
    usage = response.usage
    print(f"input={usage.input_tokens} "
          f"cache_creation={getattr(usage, 'cache_creation_input_tokens', 0) or 0} "
          f"cache_read={getattr(usage, 'cache_read_input_tokens', 0) or 0}")
```

</details>

`--provider` で経路を切り替え、`--repeat` でシステムプロンプトのサイズを倍率指定する形にして、両経路で同じシステムプロンプトを使いました。

## 実効最小 cache 長
2 経路ともに、**約 1,024 tokens が境界**でした。
具体的には 1,001 tokens で `cache_creation_input_tokens = 0` (cache 不発)、1,158 tokens で `cache_creation_input_tokens = 1,158` (cache 成立) です。

|観点|Anthropic 直接 API|Bedrock 経由 (`jp.anthropic.claude-sonnet-4-6`)|
|:-|:-|:-|
|1,001 tokens (× 3.0)|cache 不発|cache 不発|
|**1,158 tokens (× 3.5)**|**cache 成立**|**cache 成立**|
|1,326 tokens (× 4.0)|cache 成立|cache 成立|

**両経路で完全に同じ境界**、AWS 公式 (en) と Anthropic 公式 (en) の Sonnet 4.6 = 1,024 minimum とも一致しています (Anthropic 公式 (ja) は 2,048 と記載しており、こちらとは食い違います)。

<details>
<summary>二分探索の生データ</summary>

|倍率|tokens|Anthropic 直接|Bedrock 経由|
|:-|:-|:-|:-|
|× 0.5|171|cache 不発|cache 不発|
|× 1.0|339|cache 不発|cache 不発|
|× 1.5|502|cache 不発|cache 不発|
|× 2.0|670|cache 不発|cache 不発|
|× 2.5|833|cache 不発|cache 不発|
|× 3.0|1,001|cache 不発|cache 不発|
|× 3.5|**1,158**|**cache 成立**|**cache 成立**|
|× 4.0|1,326|cache 成立|cache 成立|
|× 5.0|1,657|cache 成立|cache 成立|

</details>

## TTL 1h の動作確認
AWS 公式ドキュメント (en / ja) では、延長 1h TTL の対応モデルとして Sonnet 4.6 が挙げられていません。
一方で Anthropic 公式は「対応 (Amazon Bedrock 含む)」と明記しているので、実機で確かめてみました。

結果は Sonnet 4.6 でも動きました。

検証は単純で、同じプロンプトを 10 分空けてから投げ直します。
デフォルト 5 分 TTL ならキャッシュヒットせず、1h TTL ならヒットとなります。
2 回目の呼び出しで `cache_read_input_tokens` が 0 より大きいかを確認しました。

```
[1st call] cache_creation_input_tokens=2,060 cache_read_input_tokens=0
[sleep] 600 秒待機
[2nd call] cache_creation_input_tokens=0 cache_read_input_tokens=2,060
```

2 回目に `cache_read_input_tokens=2,060` でキャッシュヒットしています。
延長 1h TTL が効いている証拠です。

これも Anthropic 直接 API と Bedrock 経由の両方で同じ結果でした。

## ここから学んだこと
新しいモデルでは、ベンダーをまたぐ出典間の食い違いだけでなく、**同じベンダーの en / ja 間でも食い違いが起きうる**ことが見えました。
公式同士でも値が割れている状況では、**実機で `cache_creation_input_tokens` / `cache_read_input_tokens` を出しておくと、ドキュメントの解釈に迷っても自分で判断を確定できます**。
複数の公式ドキュメントを併読しつつ、最後は実機で確かめる、というのが現状の正攻法だと感じました。

# 3. キャッシュチェックポイントの設計
キャッシュチェックポイントは「ここまでがプロンプトプレフィックス」というマーカーですが、**何をプロンプトプレフィックスとするか** が運用効率を大きく左右します。

News Prism では、毎日違うニュース記事を投げるユースケースなので、プロンプトプレフィックスに「毎回同じ部分」を集めて、可変部分に「毎回違う記事本文」を置く構造にしました。

実装は次のような形です。

```python
messages = [
    {
        "role": "user",
        "content": [
            {"text": f"次に与える記事を {persona_label} として分析し、{tool_name} ツールで結果を返してください。"},
            {"text": f"<context>\n{context_md_body}\n</context>"},
            {"cachePoint": {"type": "default"}},
            {"text": f"<article>\n{article_body}\n</article>"},
        ],
    }
]
```

`cachePoint` を `<article>` の **直前**に置くことで、プロンプトプレフィックス (system + tools + 指示 + `<context>`) が固定化されます。
朝のニュースチェックで複数記事を連投しても、2 件目以降はプロンプトプレフィックスだけキャッシュヒットする状態になります。

## 失敗パターン
`cachePoint` を `<article>` の **後ろ**に置いてしまうと、毎回プロンプトプレフィックスの中身に「異なる記事本文」が含まれることになり、キャッシュキーが記事ごとに変わって毎回キャッシュミスします。
当たり前のことのようですが、プロンプトプレフィックスと可変部分の境界を意識せずに書くと踏んでしまうかもしれないパターンです。

<img src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4049424/93f00225-043f-4dc0-8643-5e04954c5f49.jpeg" width="70%">

# 4. 並列処理でのキャッシュ活用
News Prism は中立要約 + 3 ペルソナの解析を **Bedrock 4 並列**で行っています。
ペルソナごとにシステムプロンプトが違うため、Bedrock のキャッシュキーも独立し、**4 つの独立した cache** が同時に成立する構造になります。

実装はシンプルに `ThreadPoolExecutor` で並列化しています。

```python
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = {
        executor.submit(self._invoke_persona, persona, article): persona
        for persona in PERSONAS  # summary, scoe, supply_chain_security, blogger
    }
    results = {persona: future.result() for future, persona in futures.items()}
```

実機の per-call データを見ると、4 つの cache が同時にヒットしているのが分かります。

|persona|latency (ms)|cache_read tokens|
|:-|:-|:-|
|supply_chain_security|17,162|3,403|
|blogger|19,188|3,467|
|scoe|20,883|3,478|
|summary|22,673|3,090|
|**合計 / wall**|**24,228 (= 最遅 + 並列収束)**|**13,438**|

並列度を上げても **待ち時間は最も遅い call が律速** となります。
そのため出力量をペルソナごとに均等化しておかないと、特定のペルソナが律速になって全体が遅くなります。

News Prism では各ペルソナの出力サイズを揃える指示をシステムプロンプトに入れることで、最遅 call の暴走を抑えています。

<img src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4049424/a43f38a2-4d8c-46a6-a8e5-6a4affa4e87a.jpeg" width="70%">

# 5. コスト削減について
プロンプトキャッシュを利用することで、実際にどれくらいのコスト削減を見込めるのでしょうか。
本番の処理で実機計測した値を、入力のみ / 出力込みの両方で示します。

## 実機計測
News Prism の Lambda 本番 (`jp.anthropic.claude-sonnet-4-6` / ap-northeast-1) で 8 記事を連投したときの数値です。

<details>
<summary>キャッシュの生データ</summary>

|#|wall_ms|cache_read|cache_write|input|output|
|:-|:-|:-|:-|:-|:-|
|1|10,769|0|13,909|6,860|2,135|
|2|12,392|13,909|0|3,908|2,125|
|3|12,817|13,909|0|4,268|2,110|
|4|12,284|13,909|0|4,096|2,051|
|5|12,102|13,909|0|3,220|2,037|
|6|13,358|13,909|0|3,756|1,799|
|7|11,254|13,909|0|4,204|1,886|
|8|10,886|13,909|0|3,832|1,787|

</details>

要約するとこうなります。

|項目|値|
|:-|:-|
|wall_ms (avg)|11,982|
|total_cache_read|97,363 (= 13,909 × 7)|
|total_cache_write|13,909 (= 1 write)|
|total_input_tokens|34,144|
|total_output_tokens|15,930|
|**入力側コスト削減 (出力分除く)**|**57.9%**|
|**トータルコスト削減 (出力込み)**|**37.4%**|

入力側だけで見ると 57.9% 削減、出力込みのトータルでは 37.4% 削減です。
Bedrock はトークンあたりの課金ですので、コスト削減メリットは十分にあると言えそうです。

## 削減率の限界
削減率は **連投回数が増えるほど大きくなる** 性質があります。
cache write は通常入力の 1.25x コスト、cache read は 0.1x コストです。

cache read が **入力の 0.1x コストで済む**ため、すべての入力トークンがキャッシュヒットすれば理論上限は 90% 削減になります。
News Prism は `<article>` (記事本文) 部分が毎回違うため、その分はキャッシュ対象にならず、**実効は 75% 程度** に落ち着きます。
連投回数を無限に大きくすると、入力トークンの削減率はこの 75% に近づきます。

<img src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4049424/0a176fef-1d47-4db6-b3ed-6a5972c601e0.jpeg" width="70%">

# まとめ
News Prism の本番運用を題材に、Bedrock プロンプトキャッシュの 4 つの観点を AWS 公式 (en / ja) / Anthropic 公式 (en / ja) / 2 経路 (Bedrock, Anthropic API) の実機検証で見てきました。

仕様の確認からキャッシュチェックポイントの設計、コスト削減試算まで、当たり前のようでいて、実際に踏まないと気付きにくい設計判断がありました。
キャッシュでコストやレイテンシを抑えつつ、上手に AI モデルを活用していきたいですね。

今日も小さな学びを。

### Bedrock 関連記事
https://qiita.com/tadokoro88/items/d9b463b5393460080c96
