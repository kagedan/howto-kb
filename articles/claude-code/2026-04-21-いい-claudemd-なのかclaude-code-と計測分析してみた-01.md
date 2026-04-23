---
id: "2026-04-21-いい-claudemd-なのかclaude-code-と計測分析してみた-01"
title: "いい CLAUDE.md なのか、Claude Code と計測・分析してみた"
url: "https://zenn.dev/progate/articles/cb3018bbfc5aad"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "zenn"]
date_published: "2026-04-21"
date_collected: "2026-04-22"
summary_by: "auto-rss"
---

Progate でエンジニア見習いをしている横江( [@yokoe24](https://x.com/yokoe24) )です！  
先月から業務委託でお手伝いさせていただいております。

## CLAUDE.md が物足りない問題！

Progate はバックエンドとフロントエンドのリポジトリがしっかり分かれていて、  
その両方の実装が必要な時があります。

しかし、フロントエンドのリポジトリをさわっているときに違和感がありました。

**「なんか…… Claude Code の実行が遅いし、精度が低い気がする……」**

バックエンドでの Claude Code 体験が高くて  
**「うおおお、すぐに実装できて最高ぉぉおお！！🏃‍➡️🏃‍➡️🏃‍➡️」** となっていたぶん、  
フロントエンドでの開発に違和感がありました。

`CLAUDE.md` を読むと、  
README では Docker での起動を推奨しているのに  
lint を Docker 外で走らせる指示があるなど、気になるところがいくつかありました。

時間はかかるけど、これを直したほうが私の生産効率は上がるはず……！  
そう考え、 `CLAUDE.md` の改修に取りかかることにしました。

## それは本当にいい CLAUDE.md なのか？

`CLAUDE.md` は329行にわたっていて、  
そのわりにはバックエンド側のリポジトリの存在を書いていないなど、  
Claude Code が全体観を捉えるには情報が足りていません。

そこで、Progate が Devin の [DeepWiki](https://docs.devin.ai/ja/work-with-devin/deepwiki) を使って  
リポジトリ横断の知識を Devin に蓄えていることを活用して、  
「このリポジトリの CLAUDE.md を刷新するならどうする？」と Devin に投げかけてドラフトを作ってもらうことにしました。

最初の質問からいろいろ調整を加えて出来上がった `CLAUDE.md` は  
なんと131行！ **約60%の行数削減！！**

行数は減りましたが、本当にこれはいい `CLAUDE.md` なのでしょうか？  
必要な情報まで抜け落ちたのではないでしょうか？

そこで、計測してみることにしました 💪

## 計測に役立つ `--output-format json` 形式

```
claude -p "<質問文>" --output-format json --max-turns 20
```

このようなコマンドが役立ちました！

`--max-turns 20` は指定しなくても大丈夫ですが、  
無限ループに陥って終わらず、トークンを無駄に消費することを念のために防いでいます。

**`--output-format json` を指定するのが大事**で、  
Claude Code は以下のように、かかった時間やコストなどを出力してくれます。

出力されるJSONの例（長いので折りたたんでます）

```
{
  "type": "result",
  "subtype": "success",
  "is_error": false,
  "duration_ms": 30479,
  "duration_api_ms": 30860,
  "num_turns": 7,
  "result": "最終的な回答の文章......",
  "stop_reason": "end_turn",
  "session_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "total_cost_usd": 0.35247599999999996,
  "usage": {
    "input_tokens": 3348,
    "cache_creation_input_tokens": 41512,
    "cache_read_input_tokens": 78554,
    "output_tokens": 1463,
    "server_tool_use": {
      "web_search_requests": 0,
      "web_fetch_requests": 0
    },
    "service_tier": "standard",
    "cache_creation": {
      "ephemeral_1h_input_tokens": 41512,
      "ephemeral_5m_input_tokens": 0
    },
    "inference_geo": "",
    "iterations": [
      {
        "input_tokens": 1,
        "output_tokens": 701,
        "cache_read_input_tokens": 30592,
        "cache_creation_input_tokens": 10920,
        "cache_creation": {
          "ephemeral_5m_input_tokens": 0,
          "ephemeral_1h_input_tokens": 10920
        },
        "type": "message"
      }
    ],
    "speed": "standard"
  },
  "modelUsage": {
    "claude-haiku-4-5-20251001": {
      "inputTokens": 359,
      "outputTokens": 15,
      "cacheReadInputTokens": 0,
      "cacheCreationInputTokens": 0,
      "webSearchRequests": 0,
      "costUSD": 0.00043400000000000003,
      "contextWindow": 200000,
      "maxOutputTokens": 32000
    },
    "claude-opus-4-6[1m]": {
      "inputTokens": 3348,
      "outputTokens": 1463,
      "cacheReadInputTokens": 78554,
      "cacheCreationInputTokens": 41512,
      "webSearchRequests": 0,
      "costUSD": 0.352042,
      "contextWindow": 1000000,
      "maxOutputTokens": 64000
    }
  },
  "permission_denials": [],
  "terminal_reason": "completed",
  "fast_mode_state": "off",
  "uuid": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

かかった時間を示す `duration_ms` や、  
従量課金の場合の推定金額を示す `total_cost_usd` がポイントですね！

```
claude -p "<質問文>" --output-format json --max-turns 20
```

変更前と変更後の `CLAUDE.md` それぞれの状態で同じ質問文を複数回投げて、  
JSON 出力の結果を Claude Code に渡すことで、Before/After の分析をお願いすることにしました。

なお、なんらかのキャッシュがあるのか、  
１回目よりも２回目以降のほうが早く終わる傾向にあるので、  
１回目の実行結果は捨てるのがもしかしたらいいかもしれません。  
（追記： [X で教えていただいた](https://x.com/imaimai17468/status/2046569685869826193)のですが、検証ごとにDockerを立ち上げて環境を分離する方法を取るのがより良さそうです！）

## 実際に計測してみて：質問文が大事！

### 実装計画系の質問は計測に不向き

まず最初に質問したのは、  
「〇〇演習を新たに作る場合は何が必要？ 実装計画をまとめてみて」という質問でした。  
しかし、**実装計画を聞くのは失敗**でした。

「デザインはどのようにするのか？ 他の演習は今どのような実装か？」など、  
注意深く実装しようと考えるときと、ストレートに考えるときがあり、  
そのブレで**実行時間やコストに関して各回で差が出やすく**、数値だけで良し悪しを判断するには不向きな質問でした。

### 探索を求める質問は、少し難しめの設定だといい感じ

次に試したのは、  
「HTML演習の正誤判定のロジックはどこにある？」という質問で、これは上手くいきました。

そして、わずかな差ではありますが、  
平均コストが減少していることも確認できました。

| 指標 | Before | After |
| --- | --- | --- |
| 平均コスト | $0.234 | $0.207 |
| 中央値 | $0.248 | $0.223 |
| 変動係数 | 0.209 | 0.115 |
| 平均ターン数 | 5.6 | 6.6 |
| 平均実行秒数 | 33.4s | 28.8s |
| 試行回数 | 8回 | 8回 |

`CLAUDE.md` の行数を大幅に減らしても、  
少なくとも悪化していない、ということが確かめられました。

「どこにある？」系の質問は注意が必要で、**カンタンな質問すぎると差が出ません**。

**少し難しい探索が必要で、かつ実際にエンジニアがおこないそうな質問**が良く、  
Claude Code に手伝ってもらいつつ考えました。

### エラー理由を発見してもらう質問も微妙かも？

次におこなったのが  
「HTML演習でプレビューパネルが表示されない場合は何を確認すればいい？」という、  
問題が発生したときの解決方法を問うものでした。

これは、当時はいい結果が出たのですが、  
１回の実行時間が長いぶん試行回数を４回と少なくしていたために、  
たまたま上振れていたようです。

今やってみたら After のほうが平均コストが増していました。

| 指標 | Before | After |
| --- | --- | --- |
| 平均コスト | $0.367 | $0.427 |
| 中央値 | $0.357 | $0.424 |
| 変動係数 | 0.226 | 0.269 |
| 平均ターン数 | 2.0 | 2.0 |
| 平均実行秒数 | 95.1s | 105.1s |
| 試行回数 | 8回 | 8回 |

エラー理由を問うのは、実装計画を問うのと同様、  
回答精度を高めるためにどこまで調査するのか、その時々の気分でのブレが大きそうです。

定量的な計測には不向きですが、  
**回答の質が上がるかを確認する**という点においては有用な質問でした。

今回の `CLAUDE.md` の変更では、バックエンド側のリポジトリを必要に応じて参照するよう指示していたのですが、  
見事、バックエンド側も調査した上での回答もおこなえるようになっていて、  
回答の質は向上していることが確認できました。  
（バックエンド側のファイルも見に行くんだから、実行時間やコストはそりゃ増えるよなぁ……）

## まとめ

いい CLAUDE.md を書けているのか、分析するために必要なのは以下のことでした！

1. 単純には発見できない**探索系の質問**を、 Claude Code に手伝ってもらいつつ考える
2. `claude -p "<質問文>" --output-format json --max-turns 20` の形式で質問する
3. **出力されたJSONを Claude Code に渡し**、Before/After を分析してもらう

以下のようなコマンドをおこなうと、複数回の実行結果をファイルにまとめてくれて便利です。

```
# ２度目以降でキャッシュが効く可能性があるので、１度目の結果は捨てる
claude -p "<質問文>" --output-format json --max-turns 20

# 変更前の CLAUDE.md が存在するブランチで
TMP_FILE_NAME=before_results.json; touch ${TMP_FILE_NAME}; for i in {1..5}; do claude -p "<質問文>" --output-format json --max-turns 20 >> ${TMP_FILE_NAME} && echo "" >> ${TMP_FILE_NAME}; done

# 変更後の CLAUDE.md が存在するブランチで
TMP_FILE_NAME=after_results.json; touch ${TMP_FILE_NAME}; for i in {1..5}; do claude -p "<質問文>" --output-format json --max-turns 20 >> ${TMP_FILE_NAME} && echo "" >> ${TMP_FILE_NAME}; done
```

これを作成した上で、Claude Code に例えば

> CLAUDE.md の改善を試しています。CLAUDE.md の Before/After の状態それぞれで、  
> claude -p "<質問文>" --output-format json --max-turns 20  
> を複数回おこない、その結果を before\_results.json, after\_results.json に格納しました。 Before/After を分析してください。

のように質問すると、いい感じにまとめてくれます。

## もっといい分析方法をください！

こうして出来上がった `CLAUDE.md` によって、  
前よりもスムーズな実装が出来るようになりました！

今回の分析方法についてはかなり自己流で、  
世の中にはもっといい方法を見つけた人もいそうです。

ぜひ、「自分はこの方法で `CLAUDE.md` の良さを計測している」という知見を  
コメントや X などで教えてくださると幸いです！🌟

ここまで読んでくださり、ありがとうございました！！
