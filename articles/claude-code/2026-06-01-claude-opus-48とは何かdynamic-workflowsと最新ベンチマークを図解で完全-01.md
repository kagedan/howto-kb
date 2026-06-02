---
id: "2026-06-01-claude-opus-48とは何かdynamic-workflowsと最新ベンチマークを図解で完全-01"
title: "Claude Opus 4.8とは何か？Dynamic Workflowsと最新ベンチマークを図解で完全整理"
url: "https://qiita.com/ryukiebe0911/items/0e8849151b881d105840"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "OpenAI", "Gemini", "GPT", "qiita"]
date_published: "2026-06-01"
date_collected: "2026-06-02"
summary_by: "auto-rss"
query: ""
---

# Claude Opus 4.8 を読むための用語集【図解・完全版】— SWE-bench / GDPval / Dynamic Workflows ほか


[![Claude Opus 4.8 解説記事サムネイル](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4437835/88cf6121-0bd0-4949-9e87-706cf21ca766.png)](https://note.com/ebe0911/n/ne066f91baba8)

:::note info
本記事は「**AI実験レポート Vol.0（Claude Opus 4.8 と Dynamic Workflows）**」の副読本（用語集）の**図解・完全版**です。本文に出てくるベンチマーク名やエージェント用語を、図とセットで、非専門の方でも追えるようにまとめました。定義は「ざっくり理解する」ことを優先しています。正確な仕様は各公式（システムカード等）をご参照ください。
:::

## はじめに

新しいAIモデルの記事には、`SWE-bench Pro` や `GDPval`、`Dynamic Workflows` といった見慣れない言葉が一気に出てきます。本稿では、それらを「何を測る／意味するものか」＋「本文での数値」をセットで、図解つきで並べました。上から読む必要はなく、気になった語だけ拾ってください。

## 全体像：ベンチマーク早見マップ

まず、本稿に出てくるベンチマークを「何を測るか」で5つに分けて俯瞰します。個別の定義はこの後の各セクションにあります。

![図1 AIベンチマーク早見マップ](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4437835/15efa0df-af5b-486d-87f3-b2c0bd7968be.png)
*図1. AIベンチマーク早見マップ（測定領域で分類）*

## モデル・プラットフォーム

| 用語 | 意味 |
|---|---|
| Claude Opus 4.8 | Anthropic の最上位モデルの最新版（2026年5月28日公開）。本シリーズ Vol.0 の主役。 |
| Claude Opus 4.7 | 4.8 の前バージョン（2026年4月）。比較の基準。 |
| GPT-5.5 | OpenAI のモデル。端末コーディングなど一部で 4.8 を上回る比較対象。 |
| Gemini 3.1 Pro | Google のモデル。比較対象。 |
| Anthropic | Claude を開発する企業。 |
| Amazon Bedrock | AWS の生成AI基盤。Opus 4.8 が即日提供されたプラットフォームの一つ。 |
| Google Cloud Vertex AI | Google Cloud の生成AI基盤。同上。 |
| Microsoft Foundry | Microsoft の生成AI基盤。同上（コンテキストは20万トークン）。 |
| コンテキストウィンドウ | モデルが一度に扱えるテキスト量の上限。Opus 4.8 は最大100万トークン。 |
| トークン | モデルが処理・課金の単位とするテキストの最小単位（単語の断片など）。 |

![スクリーンショット 2026-06-01 10.30.54.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4437835/019427d8-4a43-4688-9758-fc6b07c001f5.png)
*図2. Claude Opus のリリース系譜（4.7→4.8 はわずか41日）*

## ベンチマーク①：コーディング系

| 用語 | 意味 |
|---|---|
| SWE-bench Verified | 実在の GitHub 課題（バグ修正など）を最後まで解けるか測る標準ベンチ。人手で検証された500問。すでに飽和に近い（本稿: 4.8 = 88.6%）。 |
| SWE-bench Pro | SWE-bench の「難しく・汚染の少ない」版。差がつきやすく実力を測りやすいため、本稿ではコーディングの中心指標（本稿: 4.7 = 64.3% → 4.8 = 69.2%）。 |
| SWE-bench Multilingual | SWE-bench を多言語のコードに広げた版（本稿: 4.8 = 84.4%）。 |
| Terminal-Bench (2.1) | ターミナル（コマンドライン）上でエージェントがタスクをこなす能力を測る。実行環境＝ハーネスで結果が変わる点に注意。本稿では GPT-5.5（78.2）が 4.8（74.6）を上回る。 |

## ベンチマーク②：エージェント／コンピュータ操作系

| 用語 | 意味 |
|---|---|
| OSWorld-Verified | 実際の OS（Ubuntu などの仮想マシン）上で、文書編集・Web 閲覧・ファイル操作といった現実の PC 作業をこなせるか測る（本稿: 4.8 = 83.4%）。 |
| Online-Mind2Web | 実在の Web サイトを自律的に操作・ナビゲートする能力を測る（本稿: 4.8 = 84%）。 |
| BrowseComp | 見つけにくい情報を Web ブラウジングで探し出すエージェント能力を測るベンチ。 |
| MCP-Atlas | MCP（モデルが外部ツールに接続する規格）を介したツール利用の能力を測るとされるベンチ。 |

## ベンチマーク③：推論・知識・数学・知識労働系

| 用語 | 意味 |
|---|---|
| HLE（Humanity's Last Exam） | 各分野の専門家レベルの超難問を集めた、現行で最も難しい一般推論ベンチの一つ（本稿: ツールなし 4.8 = 49.8%）。 |
| GPQA Diamond | 大学院レベルの科学（物理・化学・生物など）の難問。各社が高得点で「飽和」気味（本稿: 4.8 = 93.6%、各社ほぼ同等）。 |
| USAMO 2026 | 全米数学オリンピックの証明問題。数学的推論の深さを測る（本稿: 4.7 = 69.3% → 4.8 = 96.7%、+27.4pt）。 |
| GDPval | OpenAI による「経済的に価値ある実務タスク」のベンチ。米国 GDP 上位9業種・44職種の、実務家（平均14年の経験）の仕事を題材にする。 |
| GDPval-AA | 上記 GDPval を **Artificial Analysis 社**が独自に評価した版。モデルにシェルと Web 閲覧を与えたエージェント実行で、ブラインドの一騎打ち比較から **Elo** を算出（本稿: 4.8 = 1890）。 |
| Elo（イロ） | 対戦比較から相対的な強さを数値化する仕組み（元はチェス）。高いほど強く、点差が大きいほど勝率が高い（例：121点差 ≒ 勝率約67%）。 |

### 数値で見るとどうなるか

各ベンチマークの実際の数値（Opus 4.7 / 4.8 / 他社）をまとめると、次のとおりです。「淡い色」は 4.8 が首位ではない項目です。
![table1_summary (4).png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4437835/e4ba77e8-f359-4264-b846-ee6928f51b85.png)
*図3. 主要ベンチマーク比較（Claude Opus 4.7 vs 4.8）*

## Dynamic Workflows・エージェントの用語

| 用語 | 意味 |
|---|---|
| Dynamic Workflows | Claude Code の新機能（リサーチプレビュー）。親エージェントが処理を動的に組み立て、多数のサブエージェントを並列実行し、敵対的に検証して、収束するまで反復する仕組み。 |
| オーケストレーター（親エージェント） | 全体の段取りを決め、サブエージェントを統括する司令塔。 |
| サブエージェント | 親の指示で個別タスクを担う作業エージェント。Dynamic Workflows では数十〜数百を並列で起動する。 |
| 並列実行 | 複数の処理を同時に走らせること。多数のサブエージェントが、別々の角度から同時に探索する。 |
| 敵対的エージェント（adversarial） | 出てきた結論に、あえて反証を試みる役。単独エージェントが陥りがちな過信を抑える狙い。 |
| 収束 | 反復のなかで答えが安定し、結論が定まること。収束してから報告する。 |

![fig3_dynamic_workflows.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4437835/9a5e65e3-d90e-4a08-b22d-cc9ea35cc2f6.png)

*図4. Dynamic Workflows の処理フロー*

## モデルの動作・設定の用語

| 用語 | 意味 |
|---|---|
| エフォート（effort） | モデルがタスクにかける「労力」（思考量）の段階。low / medium / high / xhigh / max があり、Opus 4.8 の既定は high。 |
| adaptive thinking | 問題の難しさに応じて、思考の深さを自動で調整する仕組み。 |
| fast mode | 速度を優先する動作モード。Opus 4.8 では約2.5倍速・料金2倍（ただし 4.7 の fast mode より3倍安い）。 |
| システムカード | モデルの評価結果や安全性などを公式にまとめた文書。本稿のベンチ数値の主な出典。 |

## 信頼性・評価の用語

| 用語 | 意味 |
|---|---|
| ハルシネーション | もっともらしいが事実でない出力を生成してしまう現象。 |
| 過信（overconfidence） | 根拠が薄いのに、自信たっぷりに断言してしまう傾向。Opus 4.8 は 4.7 比で10倍以上低減と報告。 |
| 自己申告 | モデルが自分の不確実性や誤りを、自分から明示すること。本稿でいう「信頼性」の核。 |
| ベンチマーク飽和 | 多くのモデルが高得点に達し、差がつかなくなった状態（例：GPQA）。 |
| ハーネス | ベンチを実行する環境・足回りのこと。同じベンチでもハーネスが違うと数値が変わる（Terminal-Bench の注意点）。 |
| n=1／シングルショット | 1回だけ実行し、平均を取らない測定。「一度聞いて、返ってきたものを読む」という実際の使い方に近い。Vol.1 で採用予定。 |

本稿の「信頼性」と Dynamic Workflows は、じつは同じ狙い——AIの過信をどう抑えるか——への、層を変えた回答として読めます。

![fig4_two_layers.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4437835/24e0f430-55ee-4727-90be-5a1c1907c463.png)
*図5. 過信を抑える二層構造（モデル単体の正直さ × 複数エージェントの相互反証）*

## おわりに

用語が分かると、ベンチマーク表は「どこが本当に伸びたのか」を読む道具になります。本編 Vol.0 では、この用語をもとに `能力・信頼性・コスト` の3軸で Claude Opus 4.8 を整理しています。あわせてどうぞ。

## 参考

- Anthropic「Introducing Claude Opus 4.8」: https://www.anthropic.com/news/claude-opus-4-8
- OpenAI「GDPval」: https://openai.com/index/gdpval/
- Artificial Analysis「GDPval-AA Leaderboard」: https://artificialanalysis.ai/evaluations/gdpval-aa

---
