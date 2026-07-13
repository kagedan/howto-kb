---
id: "2026-07-13-claude-code-のcontextskillを評価するevalsツール徹底比較-トークン数と性-01"
title: "Claude Code のContext・Skillを評価する『Evals』ツール徹底比較 〜トークン数と性能をどう測るか〜"
url: "https://zenn.dev/yamitake/articles/claude-code-evals-tools-guide"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "prompt-engineering", "LLM", "Python"]
date_published: "2026-07-13"
date_collected: "2026-07-14"
summary_by: "auto-rss"
query: ""
---

## はじめに

> 「Skillを追加したら、ちゃんと精度は上がったの？」  
> 「CLAUDE.md にコンテキストを盛り込んだけど、トークン消費とレスポンスは大丈夫？」

Claude Code に大量の `CLAUDE.md` を読ませたり、独自の **Skill** を作り込んだりしていると、必ずぶつかるのがこの問いです。「なんとなく良くなった気がする」で運用を続けると、**気づかないうちにトークン単価が膨らみ、精度はむしろ下がっている**——ということが起こります。

そこで登場するのが **Evals（評価）** の考え方と専用ツールです。この記事では、

* そもそも「評価」で何を測るのか（品質軸とコスト軸）
* Claude Code に**標準搭載**されているトークン・コスト計測機能
* promptfoo / DeepEval / Braintrust / LangSmith / Ragas などの**Evals専用フレームワーク**
* それぞれ**どういうときに有効か**、比較表つき
* Skill やコンテキストの**性能を実際に測るワークフロー**

を、リンク付きでできるだけ分かりやすく整理します。

## そもそも「評価（Evals）」で何を測るのか

LLM の評価は、大きく **2つの軸**に分かれます。ここを混同すると「どのツールを使えばいいか」が分からなくなります。

| 軸 | 測るもの | 例 |
| --- | --- | --- |
| **品質（Quality）** | 出力が期待どおりか | 正答率、指示追従、ハルシネーション有無、フォーマット遵守 |
| **コスト/性能（Cost & Latency）** | どれだけ食うか | 入力/出力トークン数、$コスト、レイテンシ、context window 使用率 |

Claude Code で Skill やコンテキストをチューニングするときは、この **両方をセットで**見る必要があります。

* Skill を足したら品質は上がったが、毎回 8,000 トークン読み込むようになって遅く・高くなった → コスト軸で赤字
* コンテキストを削ったらトークンは減ったが、指示追従が崩れた → 品質軸で赤字

**「品質を保ったまま、いかに安く・速くするか」**——これが評価の目的です。

## ① まずは Claude Code 標準機能でトークン・コストを測る

外部ツールを入れる前に、Claude Code 自身が持つ計測機能を使い倒しましょう。**追加インストール不要**でコスト軸をすぐ測れます。

### `/context` — コンテキストウィンドウの内訳を可視化

セッション中に `/context` を実行すると、いま context window を **何が・どれだけ占有しているか**（システムプロンプト、`CLAUDE.md`、ツール定義、会話履歴、Skill など）が内訳表示されます。

> Skill やコンテキストファイルを追加した「前後」で `/context` を見比べると、**その追加が何トークンぶんの固定コストを生んだか**が一目で分かります。

### `/cost` — セッションのトークン数と料金

`/cost` はそのセッションで消費した入力/出力トークン数と概算コストを表示します。ある作業を「Skillあり/なし」で2回流して `/cost` を比較すれば、**同じタスクのコスト差分**が測れます。

### ccusage — ローカルログからトークン/コストを集計する定番CLI

[**ccusage**](https://github.com/ryoppippi/ccusage) は、Claude Code がローカルに残す JSONL ログを解析し、**日別・セッション別・モデル別のトークン数とコスト**を集計してくれるサードパーティCLIです。インストール不要で試せます。

```
# 日別のトークン/コストレポート
npx ccusage@latest

# セッション単位で集計
npx ccusage@latest session
```

`/cost` が「いまのセッション」向けなのに対し、ccusage は**過去にわたる傾向**（このSkillを導入してから月のトークンがどう変わったか等）を追うのに向いています。

## ② 品質を測る「Evals専用フレームワーク」

コスト軸が標準機能で測れる一方、**品質軸は「テストケース × 期待値 × 採点」の仕組み**が必要です。ここで専用フレームワークの出番になります。Skill やプロンプトを変えたときに「精度が本当に上がったか」を**回帰テストのように**回せます。

### promptfoo — プロンプト/モデルを横並び比較する定番

[**promptfoo**](https://www.promptfoo.dev/) は、複数のプロンプトやモデル、パラメータを**表形式で横並び比較**できるOSSツール。YAMLでテストケースと評価基準（assertion）を書き、CLI/WebUIで結果を見られます。Anthropic モデルにも対応。

```
# promptfooconfig.yaml（イメージ）
prompts:
  - "Skillなし: {{input}}"
  - "Skillあり: {{input}}"
providers:
  - anthropic:messages:claude-opus-4-8
tests:
  - vars: { input: "請求書PDFから合計金額を抽出して" }
    assert:
      - type: contains
        value: "合計"
      - type: cost         # コスト上限もアサートできる
        threshold: 0.01
      - type: latency
        threshold: 3000
```

**有効なとき**: 「A案とB案のプロンプト/Skill、どっちが良い？」を**素早く定量比較**したいとき。`cost` や `latency` を assertion にできるので、**品質とコストを同じ表で見られる**のが強み。CI に組み込みやすい。

### DeepEval — pytest感覚でLLMをテスト

[**DeepEval**](https://www.deepeval.com/) は「LLM版 pytest」。`assert_test()` のように書け、**回答の関連性・忠実性・ハルシネーション**などのメトリクスが標準搭載。既存のPythonテスト資産に馴染ませやすい。

**有効なとき**: すでに Python/pytest で開発していて、**CIに品質テストを組み込みたい**とき。RAG系メトリクスも豊富。

### Braintrust — 評価データセットとログの運用基盤

[**Braintrust**](https://www.braintrust.dev/) は、評価用データセットの管理・実験の比較・本番ログの観測を一気通貫でこなす**商用プラットフォーム**。実験ごとのスコア差分をダッシュボードで追える。

**有効なとき**: チームで継続的に評価を回し、**「どのバージョンが良かったか」を履歴で管理**したいとき。個人の単発比較よりチーム運用向き。

### LangSmith — トレース＋評価の統合観測

[**LangSmith**](https://www.langchain.com/langsmith)（LangChain製、ただし非LangChainでも利用可）は、実行の\*\*トレース（どのステップで何トークン使ったか）\*\*と評価を統合。エージェント的な多段処理のボトルネック把握に強い。

**有効なとき**: マルチステップのエージェントで、**どのステップがトークン/レイテンシを食っているか**まで深掘りしたいとき。

### Ragas — RAG特化の評価

[**Ragas**](https://docs.ragas.io/) は RAG に特化。**faithfulness（忠実性）/ context precision / context recall** など、検索した文脈が回答にどう効いたかを定量化。

**有効なとき**: 社内ドキュメント検索やMCP経由の外部知識を組み込んだ構成で、\*\*「文脈が正しく効いているか」\*\*を評価したいとき（前提知識として、当リポジトリの RAG/pg\_vector 記事も参照）。

### Anthropic Console の Evaluate 機能

Anthropic の [**Console / Workbench**](https://console.anthropic.com/) には、プロンプトのテストケースを並べて出力を比較する**評価タブ**が用意されています。ツールを入れずGUIで手軽に試せるのが利点。

**有効なとき**: エンジニア以外も含め、**まずGUIで手早くプロンプトを比較**したいとき。

### Inspect — 研究・厳密なベンチマーク向け

[**Inspect**](https://inspect.aisi.org.uk/)（英国 AI Safety Institute 製OSS）は、大規模で厳密な評価に耐える設計。データセット・ソルバー・スコアラーを組み合わせて本格的なベンチを組める。

**有効なとき**: 個人のチューニングを超えて、**再現性ある厳密なベンチマーク**を組みたい研究寄りの用途。

## 比較早見表：どれを、いつ使う？

| ツール | 主眼 | 主に測る軸 | こんなときに有効 | リンク |
| --- | --- | --- | --- | --- |
| `/context`（標準） | context内訳の可視化 | コスト | Skill/CLAUDE.md追加の固定コストを即確認 | [docs](https://docs.claude.com/en/docs/claude-code/costs) |
| `/cost`（標準） | セッションのコスト | コスト | 「あり/なし」でタスクコストを比較 | [docs](https://docs.claude.com/en/docs/claude-code/costs) |
| **ccusage** | ローカルログ集計 | コスト | 導入前後の**傾向**を日次で追う | [GitHub](https://github.com/ryoppippi/ccusage) |
| **promptfoo** | 横並び比較 | 品質＋コスト | A/B案の**定量比較**・CI組み込み | [公式](https://www.promptfoo.dev/) |
| **DeepEval** | pytest風テスト | 品質 | Python資産でCIに組み込む | [公式](https://www.deepeval.com/) |
| **Braintrust** | 実験の運用基盤 | 品質＋コスト | チームで履歴管理 | [公式](https://www.braintrust.dev/) |
| **LangSmith** | トレース＋評価 | 品質＋コスト | 多段処理のボトルネック特定 | [公式](https://www.langchain.com/langsmith) |
| **Ragas** | RAG特化 | 品質 | 文脈が効いているか評価 | [docs](https://docs.ragas.io/) |
| **Console Evaluate** | GUI比較 | 品質 | まずGUIで手軽に | [docs](https://docs.claude.com/en/docs/test-and-evaluate/eval-tool) |
| **Inspect** | 厳密なベンチ | 品質 | 再現性ある研究用途 | [公式](https://inspect.aisi.org.uk/) |

**ざっくり選び方**：

1. **まずは標準機能（`/context`・`/cost`）＋ ccusage** でコスト軸を掴む（無料・即日）
2. 品質のA/B比較をしたくなったら **promptfoo**（コストも同じ表で見られる）
3. Python/CIに深く組み込むなら **DeepEval**、RAG構成なら **Ragas**
4. チームで継続運用するなら **Braintrust / LangSmith**

## 実践：Skill／コンテキストの性能を測るワークフロー

「Skillを作ったあとにトークン数やパフォーマンスを計りたい」という具体的な目的に対して、最小構成のやり方を示します。

### ステップ1：固定コスト（読み込みコスト）を測る

Skill やコンテキストは、**使う/使わないにかかわらず読み込まれるだけでトークンを消費**します。

1. Skill を無効化した状態で `/context` を実行 → 数値を記録
2. Skill を有効化して再度 `/context` → 差分が **Skillの固定コスト**

これで「この Skill は毎リクエスト◯◯トークンの固定費」が分かります。稀にしか使わないのに常時読み込む重い Skill は、分割や遅延読み込みを検討する材料になります。

### ステップ2：実タスクでの総コストを比較する

代表的なタスクを2〜3個決め、**Skillあり/なしで同じタスクを実行**し、それぞれ `/cost`（または ccusage）で入力/出力トークンと概算コストを記録します。

| タスク | Skillなし | Skillあり | 差分 |
| --- | --- | --- | --- |
| 請求書抽出 | 4,200 tok / 8.4s | 3,100 tok / 5.1s | −1,100 / −3.3s |
| コード修正 | 6,800 tok | 7,900 tok | +1,100 |

Skill が**うまくワークして手数が減れば総コストは下がる**こともあれば、読み込み固定費だけ増えることもあります。数字で見て初めて判断できます。

### ステップ3：品質を回帰テスト化する

コストが下がっても**品質が落ちていないか**を promptfoo などで固定。テストケースをYAMLに残しておけば、次に Skill を更新したときに**同じ基準で再評価**でき、デグレを防げます。

```
# 品質とコストを同時にアサートする例
tests:
  - vars: { input: "..." }
    assert:
      - type: llm-rubric        # LLMに採点させる
        value: "指定フォーマットで、合計金額が正しく抽出されている"
      - type: cost
        threshold: 0.02
```

## まとめ

* 評価は **品質軸**と**コスト/性能軸**の2つをセットで見る
* **コスト軸**は Claude Code 標準の `/context`・`/cost` と **ccusage** でまず無料で測れる
* **品質軸**は **promptfoo（比較）/ DeepEval（pytest風）/ Ragas（RAG）/ Braintrust・LangSmith（運用）/ Inspect（厳密）** など用途で使い分ける
* promptfoo は **cost/latency もアサートできる**ため、品質とコストを1枚の表で見たいときの第一候補
* Skill の性能は **①固定コスト → ②実タスク総コスト → ③品質の回帰テスト** の順で測るとブレない

「なんとなく良くなった気がする」を、**数字で言い切れる状態**に変えていきましょう。

## 参考リンク

### 公式ソース

### Evalsツール

### トークン/コスト計測
