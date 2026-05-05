---
id: "2026-05-04-agentic-ragは本当に割に合わないのかa-ragを実務データで再検証する-01"
title: "Agentic RAGは本当に割に合わないのか？A-RAGを実務データで再検証する"
url: "https://zenn.dev/livingston/articles/23d8f7c1500abb"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "LLM", "zenn"]
date_published: "2026-05-04"
date_collected: "2026-05-05"
summary_by: "auto-rss"
---

## はじめに

結論から言うと、本データではA-RAG Fullを全面採用する理由はありませんでした。

!

* 全体Page HitはHybrid+RerankerとA-RAG Fullが同率（68%）ですが、A-RAG Fullはコスト比×11.32
* 複数セクション横断（タイプC）ではA-RAG Naiveが3/5問で最も多くヒットし、A-RAG Fullは2/5問にとどまる
* 実運用では、単純系はHybrid+Reranker、横断系だけA-RAG Naiveに流すRouter構成が現実的

以下、この結論に至るまでの検証を順を追って書きます。

前回の記事で、業務文書QAに対するRAGを4手法（Vanilla RAG / Hybrid RAG + Reranker / RAPTOR / Agentic RAG）で比較しました。結果として、項番直引きや単一セクションの意味検索ではHybrid RAG + Rerankerが強く、複数セクションを横断する質問ではAgentic RAGが有効でした。一方でAgentic RAGには次の問題が残りました。

* 単純な質問で余計な再検索を行う（タイプAで7/10問、タイプBで8/10問にとどまり、Hybrid+Rerankerを上回れない）
* 再検索のたびに正解ページから離れる（Drift）
* トークン消費が増える（前回計測でVanilla比3.6倍）

この不安定性は**Agentic RAGという方式そのものの限界**なのでしょうか。それとも、LLMに渡している**検索インターフェースが粗かった**だけなのでしょうか。

今回はこの問いを、A-RAG（Agentic Retrieval-Augmented Generation via Hierarchical Retrieval Interfaces）で検証します。A-RAGは、LLMに対して`keyword_search` / `semantic_search` / `chunk_read`の3つの検索ツールを階層的に提供する設計です。前回のAgentic RAGが`semantic_search`と`keyword_search`の2ツールだけだったのに対し、`chunk_read`で根拠を全文確認する経路が加わります。

検証の軸は次の3つです。

1. **A-RAGは、前回Agentic RAGの不安定さを改善できるのか**
2. **A-RAGは、前回最強だったHybrid RAG + Rerankerを置き換えられるのか**
3. **置き換えられないなら、どの質問タイプにだけA-RAGを使うのが現実的か**

A-RAGを勝たせるための実験にはしません。前回と同じ業務文書、同じ評価セットで、淡々と比較し採否を判断します。

## 前回の結論（出発点）

前回記事で得られた結論は、ざっくり次のとおりです。

* **Hybrid RAG + Reranker**は、単純クエリ（タイプA）と意味検索（タイプB）に強い基準線
* **Agentic RAG**は、複数セクション横断（タイプC）でのみ有効。ただし単純クエリではHybrid+Rerankerに劣り、コストはVanilla比3.6倍
* 最終構成は「単純クエリはHybrid+Reranker、複雑クエリだけAgenticに回すRouter構成」

今回の続編は、この最終構成の「Agentic」部分をA-RAGに置き換えるべきかを判断するためのものです。

## A-RAGとは何か

A-RAGはAgentic RAGの一種で、検索結果を渡すのではなく**検索の道具**をLLMに渡す設計です。具体的には次の3ツールをLLMに公開します。

| ツール | 目的 | 想定用途 |
| --- | --- | --- |
| `keyword_search(query, top_k)` | BM25によるキーワード検索 | 項番（E721など）、コード値、固有名詞、表の列名 |
| `semantic_search(query, top_k)` | ベクトル検索 | 概念や言い換え、業務フローの説明 |
| `chunk_read(chunk_id, include_adjacent)` | 指定チャンクの全文と前後チャンク取得 | スニペットで判断できないとき、表構造の確認、複数セクション横断の根拠強化 |

前回のAgentic RAGとの違いは2点です。

* `chunk_read`が加わり、検索結果のスニペットだけで判断せずに**全文と前後チャンクを確認する経路**ができる
* LLMが検索粒度（語彙一致/意味検索/全文確認）を選び分けられるため、質問タイプごとに適切な戦略を取りやすい

加えてA-RAGではContext Trackerを持ち、すでに読んだチャンクや実行した検索クエリを記録して、同じチャンクを何度も読まないように制御します。

## 今回の検証方針

なお、本記事はA-RAG論文実装の完全再現ではありません。論文の中核である「LLMに階層的な検索インターフェースを公開する」という考え方を、実務PDF・日本語文書QA向けに移植した検証です。そのため、結果はA-RAG一般の優劣ではなく、「この文書構造・この評価セット・この実装条件における採否判断」として扱います。

### 比較対象

| 構成 | 概要 |
| --- | --- |
| Hybrid RAG + Reranker | 前回の強い基準線（BM25 +ベクトル+ RRF + Cross-encoder Reranker） |
| 前回Agentic RAG | `semantic_search` + `keyword_search`の2ツール、最大3ラウンド |
| A-RAG Naive | `semantic_search` 1ツールのみ（ツール数を増やすこと自体の効果を切り分ける） |
| A-RAG Full | `keyword_search` + `semantic_search` + `chunk_read`の3ツール、Context Tracker付き |

A-RAG Naiveを入れたのは、「ツール数を増やすこと」と「階層的な検索インターフェース」の効果を切り分けるためです。1ツールのA-RAG Naive、2ツールの前回Agentic RAG、3ツールのA-RAG Fullと階段状に並べることで、検索インターフェース設計の効きどころを見ます。

なお、本記事での「A-RAG Naive」は、論文中のNaive A-RAGを厳密に再現したものではなく、`semantic_search`のみを使う1ツールAgentとして定義します。これは、ツール数を増やす効果と、クエリリファインのみで探索する効果を切り分けるための実験用ベースラインです。

### 評価データ

前回と同じ条件で測ります。

* **対象文書**：障害福祉サービスのインタフェース仕様書（PDF約620ページ。テキストと表が大量に混在し、同一構造のテーブルが繰り返し登場します）
* **チャンク**：350文字＋70文字オーバーラップ、計2,612チャンク
* **Embedding**：`intfloat/multilingual-e5-large`（1024次元）
* **Reranker**：`hotchpotch/japanese-reranker-cross-encoder-large-v1`
* **LLM**：`claude-sonnet-4-20250514`（前回と同じ）
* **評価セット**：前回と同じ25問（タイプA:10 /タイプB:10 /タイプC:5）

新しい評価セットを作るのではなく、前回と同じ問題を解いた結果を比較するほうが、A-RAGが前回Agentic RAGの何をどれだけ改善するのかが直接見られます。

## 実装

### A-RAG Fullのループ

LLMは1ループにつき1ツールを呼ぶこともあれば、複数並行で呼ぶこともあります。各ツール呼び出しの結果はContext Trackerに記録され、次のループの判断材料になります。

実装上の上限値はやや保守的に置いています。

| 項目 | 値 |
| --- | --- |
| `max_loops` | 8 |
| `max_tool_calls` | 12 |
| `max_read_chunks` | 15 |
| `temperature` | 0 |
| `include_adjacent` | true |

`max_tool_calls`や`max_read_chunks`に達した場合は、それ以降のツール呼び出しに対してエラー応答を返し、LLMに「収集済みの情報で回答する」よう促します。

### ツール定義

Anthropic SDKのtool use形式で次のように定義しています（一部のみ抜粋）。

```
TOOL_DEF_KEYWORD_SEARCH = {
    "name": "keyword_search",
    "description": (
        "BM25によるキーワード検索。項番（例: E721）、コード値、固有名詞、表の列名など、"
        "語彙一致が効く検索に使う。検索結果はスニペットで返るため、"
        "全文確認には chunk_read を併用すること。"
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "top_k": {"type": "integer", "default": 5},
        },
        "required": ["query"],
    },
}
```

検索結果は`chunk_id` `page` `heading` `snippet`（先頭140文字）`score`を返します。スニペットを絞っているのは、入力トークンに対する公平比較のためです。`chunk_read`のときだけ全文と前後チャンクを返します。

### Context Tracker

```
class ContextTracker:
    read_chunk_ids: set[str]                  # 既読チャンクID
    searched_queries: list[tuple[str, str]]   # (tool, query)の履歴
    tool_call_count: dict[str, int]           # ツール別呼び出し回数
    retrieved_pages: set[int]                 # 検索ヒットしたページ
    evidence_pages: set[int]                  # chunk_read で読んだページ
    chunk_read_total: int
    chunk_read_redundant: int
```

これで次の3つを測ります。

* **Drift pages**：正解ページ到達後、後続検索で正解外ページへ拡散したページ数
* **Redundant Read Rate**：すでに読んだチャンクをもう一度`chunk_read`した割合
* **Tool Choiceの傾向**：質問タイプ別に、どのツールが先に呼ばれるか

### ログ形式（1問1行のJSONL）

4手法すべてを次の共通スキーマで記録し、後段の集計を一本化しています。

```
{
  "question_id": "C03",
  "type": "C",
  "method": "arag_full",
  "question": "...",
  "gold_pages": [231],
  "answer": "...",
  "retrieved_pages": [231, 232],
  "evidence_pages": [231],
  "tool_calls": [
    {"tool": "keyword_search", "input": {"query": "受給者証番号 属性 バイト数"}, "loop": 1, "is_error": false},
    {"tool": "chunk_read", "input": {"chunk_id": "abc123def456"}, "loop": 2, "is_error": false}
  ],
  "metrics": {
    "loop_count": 3,
    "tool_call_count": 2,
    "read_chunk_count": 1,
    "redundant_read_rate": 0.0,
    "input_tokens": 12345,
    "output_tokens": 678,
    "latency_ms": 18600,
    "llm_calls": 3,
    "stop_reason": "end_turn",
    "drift_pages": 0
  }
}
```

## 評価方法

評価指標は4カテゴリに分けています。

### 検索品質

| 指標 | 内容 | 自動測定 |
| --- | --- | --- |
| Page Hit@k | 正解ページが取得結果に含まれるか | ✅ |
| Drift pages | 正解ページ到達後、後続検索で正解外ページへ拡散したページ数 | ✅ |

### 回答品質

| 指標 | 内容 | 自動測定 |
| --- | --- | --- |
| Answer Correctness | 最終回答が正しいか | 人手レビュー（失敗例4件＋成功例1件） |
| Citation Correctness | `[p.123]`形式の引用ページが正解ページと一致するか | ✅ |

なお、RAG評価一般で扱われるFaithfulness（根拠にないことを言っていないか）やMissing Evidence（必要な根拠を落としていないか）は、今回のスコープから外しました。これらは人手評価への依存度が高く、評価者の属性（業務知識の深さや仕様書への習熟度）によって判定が大きく振れる懸念があるためです。例えば熟練者と新人では「根拠として十分」とみなす範囲が異なり、現時点では評価者間の評価スキルを平準化する仕組みを用意できていません。比較の再現性を優先し、自動測定可能なPage HitとCitation Correctnessを軸に置いています。

### Agent挙動

| 指標 | 内容 | 自動測定 |
| --- | --- | --- |
| Tool Call Count | 1問あたりの平均ツール呼び出し回数 | ✅ |
| Loop Count | 1問あたりの推論ループ数 | ✅ |
| Redundant Read Rate | 既読チャンクへの再読率 | ✅ |

### 運用コスト

| 指標 | 内容 | 自動測定 |
| --- | --- | --- |
| 入出力トークン数 | 1問あたりの平均 | ✅ |
| 平均レイテンシ | 1問あたりの応答時間 | ✅ |
| LLM呼び出し回数 | 1問あたりの呼び出し回数 | ✅ |
| コスト比 | Hybrid+Rerankerを1.0とした比率。入力トークン:出力トークンの単価比≒ 1:5（Claude Sonnet 4の公開価格に基づく重み付け）で算出した重み付きトークン換算 | ✅ |

LLM-as-a-Judgeも今回のスコープ外で、Answer Correctnessは失敗例・成功例として代表ケースを人手で見ます。`Is Agentic RAG worth it?`でも、Agentic RAGはEnhanced RAGに比べて入力・出力トークンとレイテンシが増えやすいことが報告されており（v2のTable 9では平均比率として入力トークンは約2.7〜3.6倍、出力トークンは約1.7〜1.8倍、レイテンシは約1.4〜1.5倍）、コスト指標は精度と同じ重みで扱います。

## 実験結果

### 全体サマリー

| 手法 | n | Page Hit | Citation Correctness | 平均トークン(in/out) | 平均時間 (Hybrid+Reranker比) | コスト比 | 平均ツール呼び出し |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Hybrid+Reranker | 25 | 68% | 68% | 2,384/313 | 26.8s (×1.00) | ×1.00 | 0.00 |
| Legacy Agentic | 25 | 68% | 36% | 9,605/426 | 8.8s (×0.33) | ×2.97 | 2.44 |
| A-RAG Naive | 25 | 64% | 44% | 23,566/905 | 19.0s (×0.71) | ×7.11 | 4.60 |
| A-RAG Full | 25 | 68% | 52% | 39,946/949 | 20.6s (×0.77) | ×11.32 | 5.60 |

平均時間カラムの`(×N)`はHybrid+Rerankerの平均時間に対する比率で、1未満は短く、1超は長くなります。コスト比は前述の重み付けトークン換算に基づきます。

特にA-RAG Fullは、タイプC 5問中3問で`max_loops`に到達しており、横断質問で探索が長引きやすい傾向が見られました。

### タイプ別Page Hit Rate

| 手法 | A | B | C | 全体 |
| --- | --- | --- | --- | --- |
| Hybrid+Reranker | 70% | 90% | 20% | 68% |
| Legacy Agentic | 70% | 80% | 40% | 68% |
| A-RAG Naive | 50% | 80% | 60% | 64% |
| A-RAG Full | 80% | 70% | 40% | 68% |

タイプ別の平均レイテンシは次の通りです。

| 手法 | A | B | C |
| --- | --- | --- | --- |
| Hybrid+Reranker | 23.7s | 29.3s | 28.1s |
| Legacy Agentic | 7.8s | 10.6s | 7.2s |
| A-RAG Naive | 14.8s | 19.1s | 27.3s |
| A-RAG Full | 14.5s | 23.2s | 27.6s |

### タイプAの結果

タイプAは項番・コード値・表の値を直接引く質問です。BM25が効きやすい質問タイプで、前回もHybrid+Rerankerが最強でした。

観点：

* A-RAG Fullは`keyword_search`を初手で選べているか
* A-RAG Naiveは`semantic_search`だけで項番直引きに到達できるか
* 余計な再検索（query reformulation）が発生していないか

| 手法 | Page Hit |
| --- | --- |
| Hybrid+Reranker | 70% |
| Legacy Agentic | 70% |
| A-RAG Naive | 50% |
| **A-RAG Full** | **80%** |

タイプAでは想定と異なり、**A-RAG Full（8/10問）がHybrid+Reranker（7/10問）を1問分上回りました**。実ログを見ると、A-RAG Fullは項番・コード値の質問で初手`keyword_search`を一貫して選んでおり、固有名詞や項目名が`BM25で候補を確定→ chunk_readで全文確認`という流れに乗りやすいことが確認できます。

一方、A-RAG Naiveは`semantic_search`のみで項番直引きを試みますが、項番のような短い記号列はベクトル検索のスコア差が出にくく、5/10問にとどまりました。`keyword_search`を使えるかどうかが、項番直引きの精度を左右する典型例です。

### タイプBの結果

タイプBは意味検索・業務フロー説明など、語彙一致しない質問です。

観点：

* `semantic_search`中心で十分か
* A-RAG Fullは単純な質問でも`chunk_read`まで進んでしまうか
* 1ツールのA-RAG Naiveと3ツールのA-RAG Fullでどちらが安定するか

| 手法 | Page Hit |
| --- | --- |
| **Hybrid+Reranker** | **90%** |
| Legacy Agentic | 80% |
| A-RAG Naive | 80% |
| A-RAG Full | 70% |

タイプBではHybrid+Reranker（9/10問）が最も多くヒットし、A-RAG Fullは7/10問でこのタイプでは最も少ないという想定外の結果になりました。Rerankerによる上位再評価が、語彙一致しない質問にもしっかり効いている形です。

注目すべきは、**ツール数を増やしたA-RAG Fullが、1ツールのA-RAG Naive（8/10問）を1問分下回った**ことです。実ログを見ると、Fullは単純な意味検索で済む質問でも`keyword_search`や`chunk_read`を呼びに行き、結果として根拠が分散して回答精度を下げているケースが見られます。「ツールが豊富にあれば賢く使い分ける」という直観は、本データでは成立しませんでした。

### タイプCの結果

タイプCは複数セクションを横断する質問で、前回Agentic RAGが唯一改善した質問タイプです。

観点：

* A-RAG Fullは`keyword_search`で候補を拾い`chunk_read`で全文確認、という多段戦略が取れているか
* 前回Agentic RAGと比較してDriftページ数が下がったか
* Hybrid+Rerankerの単発検索ではなぜ届かないかが、A-RAGの検索ログから読み取れるか

| 手法 | Page Hit |
| --- | --- |
| Hybrid+Reranker | 20% |
| Legacy Agentic | 40% |
| **A-RAG Naive** | **60%** |
| A-RAG Full | 40% |

タイプCではHybrid+Rerankerが1/5問に落ち込み、ここでようやくAgent系の優位が出ます。本データでは\*\*A-RAG Naive（3/5問）\*\*がA-RAG FullとLegacy Agentic（いずれも2/5問）を1問分上回りました。n=5のため統計的に強い結論とは言えませんが、少なくとも本データでは「ツールを増やせば横断質問に強くなる」とは言えませんでした。

A-RAG Naiveの検索ログを見ると、`semantic_search`のクエリを段階的にリファインする戦略（語彙を増やしていく/視点を変える）でgoldページに到達するパターンが多く見られます。横断質問のように「最初の検索クエリでは届かないが、リファインを重ねれば届く」種類の問題には、ツール選択のオーバーヘッドがないNaiveの方が向いていたと解釈できます。

A-RAG Fullでは、初手の`semantic_search`で当たりをつけた後に`keyword_search`で別語彙を試したり、`chunk_read`で文脈確認に時間を使ったりして、結果として`max_loops`で停止するケースが多く見られました（タイプC 5問中3問が`max_loops`到達）。

A-RAG論文はツール多様性の利点を主張していますが、本データのように「語彙が短く、検索精度の差が出にくい仕様書」では、**ツール選択コストがそれを相殺している**と読めます。

### コスト・レイテンシ

| 手法 | 平均ツール呼び出し | 平均read数 | 平均Driftページ数 | 冗長read率 | 平均LLM呼び出し | コスト比 |
| --- | --- | --- | --- | --- | --- | --- |
| Hybrid+Reranker | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | ×1.00 |
| Legacy Agentic | 2.44 | 0.00 | 0.00 | 0.00 | 2.92 | ×2.97 |
| A-RAG Naive | 4.60 | 0.00 | 6.00 | 0.00 | 5.60 | ×7.11 |
| A-RAG Full | 5.60 | 2.52 | 3.32 | 0.01 | 6.60 | ×11.32 |

## 成功例：A-RAG Naiveが少ないツールで自然収束した例

タイプCの問題C03を、A-RAG NaiveとA-RAG Fullの両方で解いた例です。両方ともgoldページp.231をretrieveできましたが、収束の仕方とコストには大きな差が出ました。

```
質問: 「受給者証番号」と「証記載市町村番号」はそれぞれどのような属性・バイト数で、
      支払業務のどの情報に含まれますか？
gold: [p.231]
```

A-RAG Naiveはクエリを段階的に絞り込み、6ループで`end_turn`（モデルが自然停止）に至りました。

```
A-RAG Naive（6 tool calls / 33k input tokens / end_turn）
  L1 semantic_search("受給者証番号 証記載市町村番号 属性 バイト数 支払業務")
  L2 semantic_search("支払業務 受給者証番号 英数 10バイト")
  L3 semantic_search("支払業務 都道府県助成金請求情報 受給者証番号 証記載市町村番号")
  L4 semantic_search("都道府県助成金請求情報 基本情報レコード 項目 属性 バイト数")
  L5 semantic_search("基本情報レコード 受給者証番号 証記載市町村番号 項目名 属性")
  L6 semantic_search("支払業務 基本情報レコード 項目一覧 受給者証番号 市町村番号")
  → retrieved に p.231 を含む / 自然停止
```

同じ問題をA-RAG Fullに解かせると、3ツールを使い分けた挙句、8ループで`max_loops`を踏みました。

```
A-RAG Full（8 tool calls / 62k input tokens / max_loops）
  L1 keyword_search("受給者証番号")
  L2 keyword_search("証記載市町村番号")
  L3 chunk_read("66623359c5b9")
  L4 chunk_read("69798ebaff76")
  L5 semantic_search("支払業務 受給者証番号 証記載市町村番号")
  L6 keyword_search("支払業務 都道府県助成金請求情報")
  L7 chunk_read("c3e3d8a0cb80")
  L8 chunk_read("6e1cadc9a42c")
  → retrieved に p.231 を含む / 予算切れ
```

観察ポイントは次の通りです。

* 同じretrieve結果（gold p.231ヒット）に到達するのに、Naiveは6ステップ、Fullは8ステップ
* 入力トークンはNaive 33kに対しFull 62kと**約2倍**
* Naiveは「クエリの語彙を増やしていく」単一戦略で自然収束したのに対し、Fullはkeyword/chunk\_read/semanticを順不同に呼び続けてmax\_loopsを踏みました
* ツールを増やしたことで「どのツールを次に呼ぶか」の選択コストが増え、根拠探索の効率が下がっています

`Is Agentic RAG worth it?`では、Agentic RAGが追加の推論ステップや再検索によってコスト・時間を増やしやすく、文書リスト改善では明示的なrerankerがAgentic側を上回るケースが報告されています。本実験でも、ツール呼び出しや探索ステップを増やしても必ず精度向上に結びつくわけではない、という近い傾向が見られました。

## 失敗例

A-RAG Fullが`page_hit=False`になった8問のうち、典型的な失敗パターンを4分類で見ます。

```
質問: 必須入力の記号「◎」「○」「△」はそれぞれ何を意味しますか？
gold: [p.20]
retrieved: [325, 518, 527, 532, 538]
tool_calls: keyword_search → chunk_read → chunk_read（end_turn / 3 ステップ）
```

「◎」「○」「△」のような記号は、語彙としては短く、また同様の記号定義が仕様書内の複数のページに散在しているため、`keyword_search`の語彙一致ではgoldページを最上位に引きにくい性質があります。Fullは初手で`keyword_search`を選び、ヒットした類似定義ページを`chunk_read`で確認して`end_turn`で停止しました。回答内容自体は記号の意味として正しく書けていますが、引用ページがgoldではなく、page\_hitとしてはfail判定です。

このケースは`semantic_search`を初手にしていれば「必須入力/パターン毎/任意」のような**意味的な記述**経由でgold p.20に届いた可能性が高く、**ツール選択の初手で詰まった例**といえます。

### Retrieval Drift（C04：再検索で正解ページから離れた）

```
質問: 平成26年4月を境にした共同生活介護およびその他のサービス体系変更
gold: [p.10, p.37]
retrieved: [43, 55, 56, 57, ..., 116, 117, ...]（gold は含まず）
tool_calls: semantic_search → chunk_read × 2 → keyword_search × 2 → semantic × 2 → keyword
```

L1の`semantic_search`は妥当なクエリでスタートしましたが、L4以降「共同生活介護31」「宿泊型自立訓練34」のような**個別語彙への絞り込み**、L6/L7で「制度改正サービス統合」のような**より抽象的な再検索**へと振れていき、最終的にgold p.10/p.37とは別の周辺ページ（p.116/p.117などサービス種類コード表）を根拠として回答しました。回答テキスト自体は読みやすく整っているものの、引用はgold外です。

これは本記事でDriftと呼んでいる現象の典型です。A-RAG論文の失敗分類でいえばWrong StrategyやEntity Confusionに近い失敗で、**最初に当たりをつけた領域に固執せず、検索クエリの変動が大きすぎる**ことが原因と考えられます。

### Over-search（C01：同一語彙を執拗に検索して予算切れ）

```
質問: 「重度者支援体制加算」のコード値と、※5 のルール
gold: [p.35, p.38]
tool_calls: keyword × 3 → semantic → chunk_read → keyword（※5 ルール）→ semantic → chunk_read（max_loops）
```

L1〜L3で「重度者支援体制加算」「重度者支援体制加算コード値」「※5」と段階的にキーワードを変えながら3回連続で`keyword_search`を実行、L6で再び「※5ルール」を`keyword_search`しています。項番98の存在は途中で確認できていましたが、※5のルール本文（p.38周辺）に到達できず、同一テーマ周辺を執拗に検索して8ループの予算を使い切りました。

回答自体も「※5の具体的な内容については回答できません」と自己申告しており、**Agentループが停止判断（end\_turn）に踏み切れず、過剰なツール呼び出しを繰り返す**タイプの失敗です。`max_loops`到達はA-RAG Fullの8件中5件で発生しており、頻発しています。

### Table Structure Loss（A06：類似構造の別表を引いた）

```
質問: 「福祉・介護職員等ベースアップ等支援加算の有無」のコード値
gold: [p.35]
retrieved: [149, 183, 205, 338, 368, 394]（gold は含まず）
回答: 1:無し / 2:有り（コード値自体は正しい）
citations: [p.149, p.394]（項番192 と項番108）
```

「福祉・介護職員等ベースアップ等支援加算の有無」という同一項目は、仕様書内の**障害福祉サービス等（項番192）と障害児支援（項番108）**のそれぞれの項番表に**同じコード値（1:無し/ 2:有り）で繰り返し登場**します。Fullはkeyword\_searchで項番192と項番108のページを引いて回答し、**コード値としては正解**を生成しましたが、評価でgoldとした項番35のページには到達しませんでした。

このケースは、A-RAGの検索失敗であると同時に、Page Hit評価の限界も示しています。回答値そのものは正しい一方で、goldで指定した一次参照ページとは異なる類似表を引用したため、Citation Correctnessではfailになります。業務文書QAでは「値が正しいか」「一次参照として妥当なページか」「同一値を持つ別表でも許容するか」を分けて評価しないと、実運用上の正解と評価上の正解がずれる可能性があります。

---

これらの失敗パターンはA-RAG論文でもentity confusion / wrong retrieval strategy / question misunderstandingとして整理されており、業務文書QAでも同様の傾向が出ます。なお、A-RAG **Naive**（`semantic_search`のみ）ではTool Selection ErrorとOver-searchのうちkeyword選択ミス系が構造的に発生しないため、シンプルさが効率に寄与しています。

## Router + Hybrid/A-RAG Naive構成

全質問をA-RAGに流すのは、主にトークンコストとループ不安定性の面で過剰です。なお、本実験ではHybrid+Reranker側のreranker処理が重く、平均レイテンシだけを見るとA-RAG系の方が短くなりました。そのため、ここでの採用判断はレイテンシ単独ではなく、Page Hit、Citation Correctness、トークンコスト、`max_loops`到達率を合わせて見ています。前回記事と同じく、軽量なQuery Routerで振り分けます。今回の検証では複雑クエリの振り先として**A-RAG FullではなくA-RAG Naive**を採用します（タイプCでNaive 3/5問 > Full 2/5問、コスト比もNaive ×7.11 < Full ×11.32のため）。

Routerの分類は3クラスです。

| 分類 | 判定条件 | 実行する構成 |
| --- | --- | --- |
| Direct Lookup | 項番・コード値・単一表 | Hybrid RAG + Reranker |
| Semantic QA | 単一セクションの意味検索 | Hybrid RAG + Reranker |
| Multi-hop / Compare | 複数セクション横断・比較・統合 | **A-RAG Naive** |

この構成の理論値は、評価セット（A 10問/ B 10問/ C 5問）に対して次のように計算できます（Routerが完全分類できた場合）。

| シナリオ | A | B | C | 全体Page Hit | コスト比 |
| --- | --- | --- | --- | --- | --- |
| 全問Hybrid+Reranker | 70% | 90% | 20% | 68% | ×1.00 |
| 全問A-RAG Full | 80% | 70% | 40% | 68% | ×11.32 |
| **Router (Hybrid + Naive)** | **70%** | **90%** | **60%** | **76%** | **約×2.22** |

Router構成のコスト比は、A/B 20問をHybrid（×1.00）、C 5問をA-RAG Naive（×7.11）として加重平均した概算値です。**全体精度は単独構成のいずれをも上回り、コストはA-RAG Fullの約1/5**に抑えられます。

実運用ではRouter自体の分類精度が課題になりますが、A/B/Cの判別は、まずはキーワード（「比較」「両方」「合わせて」「フロー」等）と質問長を使った軽量ルールから試せる範囲です。前回記事のRouter設計をそのまま流用できます。

## まとめ

A-RAGは、前回のAgentic RAGが抱えていた「複雑クエリでも安定しない」問題を一部改善できましたが、**「3ツール構成（A-RAG Full）の方が賢い」という直観は本データでは成立しません**でした。

主要な観察を整理すると次の通りです。

* \*\*タイプA（直引き）\*\*ではA-RAG Full（8/10問）がHybrid+Reranker（7/10問）を1問分上回り、`keyword_search`の効果が確認できた
* \*\*タイプB（意味検索）\*\*ではHybrid+Reranker（9/10問）が最も多くヒットし、A-RAG Fullは7/10問にとどまった。Rerankerの効果が大きい
* \*\*タイプC（横断）\*\*ではA-RAG Naive（3/5問）がA-RAG FullとLegacy Agentic（いずれも2/5問）を1問分上回った（n=5のため強い結論ではない）
* 全体Page HitはHybrid・Legacy Agentic・A-RAG Fullの3構成が同率（68%）、Citation CorrectnessはHybrid（68%）が単独首位
* コスト比はA-RAG Full ×11.32、A-RAG Naive ×7.11と高く、`max_loops`到達もA-RAG Fullで頻発（タイプC 5問中3問）

実務的な含意は次の通りです。

> タイプAではA-RAG FullがPage Hitで1問分上回りましたが、コスト比×11.32を許容してまで採用する差とは言いにくく、Citation Correctness全体ではHybrid+Rerankerが上回っています。そのため、単純な直引きクエリにA-RAG Fullを常用するのではなく、A/Bの単純系はHybrid+Reranker、Cの横断系だけA-RAG Naiveに回す構成が現実的と判断しました。
>
> 加えて、**「ツール数を増やすほど賢くなる」という前提は本データでは成立しませんでした**。タイプCで最も多くヒットしたのは3ツールのA-RAG Fullではなく、`semantic_search`のみで反復クエリリファインを行うA-RAG Naiveでした。前回の最終構成を更新するなら、複雑クエリの処理先を従来のAgentic RAGから**A-RAG Naive**に置き換えるのが現実解です。

A-RAG論文はツール多様性の利点を強調していますが、**短い語彙が中心の業務文書QAでは、ツール選択コストが多様性のメリットを相殺する**ことが本実験で確認されました。また、`Is Agentic RAG worth it?`が示した「Agentic RAGはコスト・時間が増えやすく、rerankerがAgent側を上回る局面がある」という傾向とも整合的でした。一方で、業務PDFの「同型表が複数領域に繰り返し登場する」「項番のような短い記号列でBM25が強く効く」といった文書構造由来の事情は同論文の比較範囲では扱われておらず、本実験で固有に見えた観点です。新手法を導入する前に、ツール構成の**最小単位**から効果を測ることの重要性を、改めて示した形です。

### A-RAGを導入すべきケース（ガイドライン）

最後に、今回の検証から得られたA-RAGの適用条件をまとめます。なお、以下は本実験の個別レイテンシではなく、LLM多段呼び出しを含むA-RAGを実運用に載せる際の一般的な適用条件として整理します。

| 条件 | A-RAG適性 |
| --- | --- |
| 複数セクション横断の質問が多い | 高い |
| 単純な項番検索が大半 | 低い（Hybrid+Rerankerで十分） |
| レイテンシ制約が厳しい | 低い |
| 根拠探索のログが運用上重要 | 中〜高 |
| 表構造が崩れやすいPDF | 前処理次第 |
| 質問が曖昧で再検索が必要 | 高い |

A-RAGは万能な置き換え先ではありません。それでも、Agentic RAGを実務で使うなら、検索インターフェース・Router・Reranker・コスト制御をどう設計するかが性能とコストの大半を決める、ということは確認できました。

---
