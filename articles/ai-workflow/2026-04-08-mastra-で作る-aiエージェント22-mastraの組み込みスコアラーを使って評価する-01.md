---
id: "2026-04-08-mastra-で作る-aiエージェント22-mastraの組み込みスコアラーを使って評価する-01"
title: "Mastra で作る AIエージェント(22) Mastraの組み込みスコアラーを使って評価する"
url: "https://zenn.dev/shiromizuj/articles/2731450da39a5d"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-08"
date_collected: "2026-04-09"
summary_by: "auto-rss"
query: ""
---

[Mastra で作るAI エージェント](https://zenn.dev/shiromizuj/articles/a0a1659e9f05b6) というシリーズの第22回です。

---

前回は、AIエージェントの「テスト」として「Eval（評価）」があること、その評価にはいろいろな評価観点と評価手法があることをご紹介し、Agent定義にスコアラーを組み込むことで運用中に自動的に評価がなされることを紹介しました。

今回は、Mastraがプリセットで持っているいくつかの組み込みスコアラーを紹介し、また**独自スコアラーをカスタマイズ開発する方法もご案内**します。

# Built-in Scorers（組み込みスコアラー）

Mastraには、よく使う評価観点が組み込みで用意されています。本記事の執筆時点で以下の15種類が存在します。各スコアラーの「評価方法」は公式ドキュメントには記載が無く、ソースコードから読み解いたものです。また、「スコアが高いほど良い」ものと「低いほど良い」ものがあって、注意が必要です（揃えてくれたほうが分かりやすいですよね）。

## 正確性・信頼性 に関するスコアラー

* `answer-relevancy`: 質問への適合度（高いほど良い）
  + タイプ: **モデル判定**
  + 低評価の例：「フランスの首都は？」というプロンプトに対して「Pythonの仮想環境の作り方は…」と返す。
  + 評価方法: 回答を文単位に分解し、各文をLLMが `yes/unsure/no` 判定して `yes + unsure×重み` を文数で割って算出します。

---

* `answer-similarity`: 正解データとの意味的類似度（高いほど良い）
  + タイプ: **モデル判定**
  + 低評価の例：「フランスの首都は？」に対する `groundTruth` が「Paris」なのに、回答が「Lyon」で大きく外れている。
  + 評価方法: 回答と `groundTruth` をLLMで意味単位に分解・対応付けし、一致・不足・矛盾・余分情報のペナルティを加味して算出します。

---

* `faithfulness`: 与えた文脈への忠実性（高いほど良い）
  + タイプ: **モデル判定**
  + 低評価の例：コンテキストに「初代iPhoneは2007年発売」とあるのに、回答が「2009年発売」と断定する。
  + 評価方法: 回答から主張をLLMで抽出し、各主張がコンテキストで支持されるかを判定して支持率ベースで算出します。

---

* `hallucination`: 事実矛盾・根拠なし主張（低いほど良い）
  + タイプ: **モデル判定**
  + 低評価の例：根拠文脈にない具体値（例: 売上・日付・人数）を「確定情報」として複数挿入している回答。
  + 評価方法: 回答中の主張をLLM抽出して文脈と照合し、矛盾・根拠なし主張の割合をスコア化します（低いほど良い）。

---

* `completeness`: 必要情報の網羅性（高いほど良い）
  + タイプ: **統計的な判定**
  + 低評価の例：「メリットとデメリットを両方説明して」という依頼に対し、メリットだけを述べてデメリットを欠落させる。
  + 評価方法: 入力・出力から名詞/動詞/トピック等の要素を抽出し、入力要素の被覆率（coverage）を計算します。
  + ⚠️ **日本語非対応**: 内部で英語専用NLPライブラリ [`compromise`](https://github.com/spencermountain/compromise) を使用しており、品詞解析（名詞・動詞の抽出）が日本語テキストでは正しく機能しません。

---

* `content-similarity`: 文字レベル類似度（高いほど良い）
  + タイプ: **統計的な判定**
  + 低評価の例：「TypeScriptの利点を要約して」に対し、回答が「昨日の天気の雑談」で文面がほぼ一致しない。
  + 評価方法: 文字列を正規化（大小文字・空白）して比較し、文字列類似アルゴリズムで類似度を計算します。

---

* `textual-difference`: テキスト差分指標（値の解釈は実装前に確認）
  + タイプ: **統計的な判定**
  + 低評価の例：期待文に対して語順・内容・長さが大幅に異なり、差分操作数が多い回答。
  + 評価方法: シーケンス差分から変更操作数と長さ差を求め、`類似比率 × 信頼度` の形でスコア化します。

---

* `tool-call-accuracy`: 適切なツール選択の正確性（高いほど良い）
  + タイプ: **ルールベース判定**（Code版）または **モデル判定**（LLM版）
  + 低評価の例：天気取得が必要な質問で `weatherTool` ではなく無関係な `calculatorTool` を呼び出す。
  + 評価方法: Code版は期待ツール名/順序との一致を厳密判定し、LLM版は利用可能ツールに対する選択妥当性を意味的に判定します。

---

* `prompt-alignment`: 要件・意図・形式への整合（高いほど良い）
  + タイプ: **モデル判定**
  + 低評価の例：「3行の箇条書きで答えて」と指定したのに、長文の散文で要件外の内容まで返す。
  + 評価方法: ユーザー/システムプロンプトと回答をLLMで比較し、意図一致・要件充足・完全性・形式/トーン整合を総合評価します。

---

## コンテキスト品質 に関するスコアラー

* `context-precision`: 関連文脈が上位に来るか（MAPベース）
  + タイプ: **統計的な判定**
  + 低評価の例：上位に無関係チャンクが並び、質問に直接関係するチャンクが末尾にしか出てこない。
  + 評価方法: 各コンテキスト片の関連性を判定したうえで、関連情報が先頭に来るほど高くなる MAP（Mean Average Precision）で算出します。

---

* `context-relevance`: 文脈の有用性・不足検知・使用状況を評価
  + タイプ: **モデル判定**
  + 低評価の例：高関連の文脈を取得しているのに回答で使わず、さらに回答に必要な文脈が欠けている。
  + 評価方法: 各コンテキスト片をLLMで `high/medium/low/none` に評価し、未使用の高関連文脈や不足文脈へのペナルティ込みで算出します。

---

**使い分けの目安**

* 順位品質（ランキング）重視なら `context-precision`
* 精密な関連度分析や不足把握をしたいなら `context-relevance`

両者とも以下を扱えます。

* Static context（事前配列）
* Dynamic context extraction（実行結果から抽出）

---

## 出力品質（形式・安全性） に関するスコアラー

* `tone-consistency`: 口調・文体一貫性（高いほど良い）
  + タイプ: **統計的な判定**
  + 低評価の例：同一回答内で「丁寧な敬語」から突然「攻撃的な口調」に切り替わるなど、感情トーンが大きく揺れる。
  + 評価方法: 感情分析スコアを文単位で計算し、入力との乖離や文内分散（ばらつき）から一貫性スコアを算出します。
  + ⚠️ **日本語非対応**: 内部で英語AFINN語彙辞書ベースの [`sentiment`](https://github.com/thisandagain/sentiment) ライブラリを使用しており、日本語テキストのセンチメント判定は機能しません。

---

* `toxicity`: 有害／不適切内容（低いほど良い）
  + タイプ: **モデル判定**
  + 低評価の例：相手を侮辱する語句や脅し表現を含む回答（例: 「お前は無能だ、黙れ」）。
  + 評価方法: 回答中の攻撃・ヘイト・脅し等の有害要素をLLMで判定し、重み付けして毒性スコアを算出します。

---

* `bias`: バイアス含有（低いほど良い）
  + タイプ: **モデル判定**
  + 低評価の例：特定の性別・国籍・年齢層を根拠なく一括りにして能力を断定する回答。
  + 評価方法: 回答から意見文を抽出して各意見の偏り有無をLLM判定し、偏り判定の比率をスコア化します。

---

* `keyword-coverage`: 重要語彙カバー率（高いほど良い）
  + タイプ: **統計的な判定**
  + 低評価の例：質問の主要語（例: 「TypeScript」「型安全」「保守性」）のうち1つしか回答に含まれない。
  + 評価方法: ストップワード除去後に入力側キーワードと回答側キーワードを突合し、`一致数 / 総キーワード数` で算出します。
  + ⚠️ **日本語非対応**: 内部で [`keyword-extractor`](https://github.com/michaeldelorenzo/keyword-extractor) を `language: 'english'` 固定で使用しており、日本語テキストではキーワード抽出が機能しません。

---

## Built-in Scorersの閾値ガイド

さて、上述の通り組み込みスコアラーの結果は通常 `0〜1` の数値スコアですが、例えばあるスコアが `0.7` という値で評価されたとして、それをどのように解釈してよいのか、「すごいじゃん！」なのか、「まあまあ良いね」なのか、「いや、そんなの出荷したら怒られるで」なのか、よく分からないですよね。

そこで、以下の通り**各スコアラー**の**ざっくり目安**と**閾値の推奨初期値**を記載しましたので参考にして下さい。

ただし、スコアは「絶対評価」ではなく「用途依存の相対評価」だと思っています。あくまで**初期導入時の実務的な目安**としてご理解いただき、「まずはこの閾値で運用し、データを見て調整する」程度に考えていただければ、と思います。

### 目安レンジ（初期設定）

| Scorer | 方向 | 良好 | 注意 | 要改善/危険 | 推奨閾値（初期値） |
| --- | --- | --- | --- | --- | --- |
| `answer-relevancy` | 高いほど良い | `0.90+` | `0.70〜0.89` | `<0.70` | `expect(score).toBeGreaterThanOrEqual(0.85)` |
| `answer-similarity` | 高いほど良い | `0.85+` | `0.70〜0.84` | `<0.70` | `expect(score).toBeGreaterThanOrEqual(0.85)` |
| `faithfulness` | 高いほど良い | `0.90+` | `0.75〜0.89` | `<0.75` | `expect(score).toBeGreaterThanOrEqual(0.85)` |
| `hallucination` | 低いほど良い | `0.00〜0.10` | `0.11〜0.30` | `>0.30` | `expect(score).toBeLessThanOrEqual(0.10)` |
| `completeness` ⚠️ | 高いほど良い | `0.80+` | `0.60〜0.79` | `<0.60` | `expect(score).toBeGreaterThanOrEqual(0.75)` |
| `content-similarity` | 高いほど良い | `0.90+` | `0.70〜0.89` | `<0.70` | `expect(score).toBeGreaterThanOrEqual(0.80)` |
| `textual-difference` | 高いほど類似 | `0.90+` | `0.70〜0.89` | `<0.70` | `expect(score).toBeGreaterThanOrEqual(0.80)` |
| `tool-call-accuracy` | 高いほど良い | Code版: `1` / LLM版: `0.85+` | Code版: `0` / LLM版: `0.70〜0.84` | LLM版: `<0.70` | Code版: `expect(score).toBe(1)` / LLM版: `expect(score).toBeGreaterThanOrEqual(0.85)` |
| `prompt-alignment` | 高いほど良い | `0.85+` | `0.70〜0.84` | `<0.70` | `expect(score).toBeGreaterThanOrEqual(0.80)` |
| `context-precision` | 高いほど良い | `0.80+` | `0.60〜0.79` | `<0.60` | `expect(score).toBeGreaterThanOrEqual(0.75)` |
| `context-relevance` | 高いほど良い | `0.80+` | `0.60〜0.79` | `<0.60` | `expect(score).toBeGreaterThanOrEqual(0.75)` |
| `tone-consistency` ⚠️ | 高いほど良い | `0.80+` | `0.60〜0.79` | `<0.60` | `expect(score).toBeGreaterThanOrEqual(0.70)` |
| `toxicity` | 低いほど良い | `0.00` | `0.10〜0.30` | `0.40+` | `expect(score).toBeLessThanOrEqual(0.10)` |
| `bias` | 低いほど良い | `0.00〜0.10` | `0.11〜0.30` | `>0.30` | `expect(score).toBeLessThanOrEqual(0.10)` |
| `keyword-coverage` ⚠️ | 高いほど良い | `0.80+` | `0.60〜0.79` | `<0.60` | `expect(score).toBeGreaterThanOrEqual(0.75)` |

> ⚠️ **日本語非対応のスコアラー**: `completeness`・`tone-consistency`・`keyword-coverage` は、内部で英語専用NLPライブラリ（それぞれ `compromise`・`sentiment`・`keyword-extractor`）を使用しているため、**日本語テキストでは正しいスコアが得られません**。日本語エージェントの評価では、これら3つのスコアラーは使用しないことを推奨します。

この目安は、次の情報を突き合わせて作成しました。

1. 公式リファレンスの「Score interpretation」記述（あるもの）
2. scorer実装の計算式（`generateScore` など）
3. scorerの判定方式（LLM判定 / ルール / 統計）とスケール
4. 実運用でのゲート設計の一般則（安全系は厳しめ、意味品質系は段階導入）

---

# Custom Scorers（独自スコアラー）

独自評価は `createScorer` を使って構築します。  
MastraのScorerは、共通して次の4段パイプラインを採用します。

1. `preprocess`（任意）
2. `analyze`（任意）
3. `generateScore`（必須）
4. `generateReason`（任意）

## FunctionとPrompt Object

各ステップは次のどちらでも定義できます。

* **Function（JS関数）**: 決定的ロジック・高速処理向け
* **Prompt Object（LLM判定）**: 主観評価・自然言語判断向け

Prompt Objectは、基本的に `description` と `createPrompt`（必要に応じ `outputSchema`）で定義し、結果は `results.<step>StepResult` に格納されます。

```
import { createScorer } from "@mastra/core/evals";

const scorer = createScorer({
  id: "gluten-checker",
  description: "Check if recipes contain gluten ingredients",
  judge: {
    model: "openai/gpt-5.1",
    instructions: "You are a Chef that identifies if recipes contain gluten.",
  },
})
  .preprocess(/* ... */)
  .analyze(/* ... */)
  .generateScore(/* ... */)
  .generateReason(/* ... */);
```

`judge` はPrompt Objectを使う場合に必要です。  
全ステップFunctionのみならJudgeは呼ばれません。

## 各ステップの意味

### preprocess（任意）

* 入出力の整形、必要情報の抽出、前処理を行う
* 結果は `results.preprocessStepResult`

### analyze（任意）

* 評価の中核分析を行う
* 結果は `results.analyzeStepResult`

### generateScore（必須）

* 分析結果を数値スコアに変換
* このステップだけは必須

### generateReason（任意）

* スコア理由を人間向け文章で生成
* デバッグ・説明責任・UI表示に有効

## Agent評価での型指定

Agentのライブ評価とトレース評価の互換性を高めるには、`type: "agent"` を指定します。

```
const myScorer = createScorer({
  type: "agent",
}).generateScore(({ run, results }) => {
  // run.input / run.output が agent 用に型付けされる
  return 1;
});
```

## カスタムScorer例（要点）

公式例では「グルテン判定」を題材に、

* `analyze` で `isGlutenFree` / `glutenSources` を抽出
* `generateScore` で 1 or 0 を返す
* `generateReason` で説明文を返す

という構成を示しています。  
この構造は、禁止語チェック・分類精度判定・RAG品質判定などにもそのまま流用できます。

---

# 次回は、「自動回帰テスト」ならぬ「自動回帰評価」

今回はMastraで標準で用意している15個のスコアラーを紹介し、また独自のカスタムスコアラーの作成方法も簡単に扱いました。

次回は、システム開発で実施する「自動回帰テスト」のように、AIエージェントを「自動回帰評価」する方法をご紹介します。

[>> 次回 : (23) 自動回帰テスト的に評価する](https://zenn.dev/shiromizuj/articles/07c6e6cc07ffc8)
