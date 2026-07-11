---
id: "2026-07-11-日本のaiプラットフォームでglmdeepseekなど7モデルのコードレビュー性能を検証する-01"
title: "日本のAIプラットフォームでGLM・DeepSeekなど7モデルのコードレビュー性能を検証する"
url: "https://zenn.dev/thegatebreaker/articles/aiand_inference_7models_review"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "OpenAI", "GPT", "zenn"]
date_published: "2026-07-11"
date_collected: "2026-07-12"
summary_by: "auto-rss"
query: ""
---

# 日本のAIプラットフォームでGLM・DeepSeekなど7モデルのコードレビュー性能を検証する

「低価格」「1Mコンテキスト」といったスペックは魅力的です。ただしコードレビューで重要なのは、スペック表ではなく、実在する不具合をどれだけ拾い、確認にいくら掛かるかです。

## TL;DR

* 同一の3ファイルを7モデルでレビューし、Codexで監査したところ、精度は52.1〜85.1%まで分散しました。
* 確認済み指摘1件当たりのコストは、Claude最安のHaiku 4.5比で無料〜約3.7分の1でした。ただしClaudeはエージェント型、今回の7モデルは単発APIであり、公平なモデル能力比較ではありません。
* 7モデル併用では、確認済み指摘の約16%が単独モデルだけの発見でした。監査を前提にすれば、複数モデルの併用は取りこぼし対策になり得ます。
* 財務データ処理の3ファイルを対象にした単発評価（N=1）です。一般的な能力ランキングや、そのままの導入推奨ではありません。

## 背景：ai& Inferenceとこの実験

これは「最も賢いモデル」を決めるベンチマークではありません。社内で実施済みのClaude 4価格帯比較を、ai& Inference経由の7モデルへ拡張し、AIコードレビューの費用対効果を確認したケーススタディです。

ai&（株式会社エーアイ・アンド、横浜）は日本企業です。Qwen・GLM・Kimi・DeepSeekは中国発ラボが公開したオープンウェイトモデルですが、今回の推論実行はai&保有の日本国内インフラ上で行われ、各ラボの海外APIへプロキシされるものではありません。

ai&自身の公式プレスリリースでも「すべての処理を日本国内のインフラで完結させる」「サービス基盤はすべて、ai&自身が保有・運営するハードウェア上で稼働します。レンタルのクラウドキャパシティは利用せず、データ経路に海外管轄が入ることもありません」と明記されています（[PR TIMES、2026年6月23日付プレスリリース](https://prtimes.jp/main/html/rd/p/000000016.000180050.html)）。ただし、この主張を裏付ける独立した第三者機関による技術監査報告書は、現時点では確認できていません。ここまでの内容は、ai&自身の公式発表と契約文書（ToS）に基づく確認です。

* **Qwen3.6-27B**（Alibaba、中国）— 汎用の中規模モデル。唯一の無料枠。
* **Gemma-4-31B-it**（Google、米国）— 軽量・オンデバイス志向のGemma系列。
* **Kimi-K2.7-Code**（Moonshot AI、中国）— コード特化のKimi派生モデル。
* **GLM-5.2**（Zhipu/Z.ai、中国）— 中英バイリンガルで、ツール・エージェント用途に強みを持つとされる系列。
* **DeepSeek-V4-Flash**（DeepSeek、中国）— 低コスト・高速志向の軽量版。
* **DeepSeek-V4-Pro**（DeepSeek、中国）— 同系列の上位モデル。
* **gpt-oss-120b**（OpenAI、米国）— OpenAIのオープンウェイトモデル。

| モデル | 入力($/1M) | キャッシュ入力($/1M) | 出力($/1M) | コンテキスト長 |
| --- | --- | --- | --- | --- |
| Qwen3.6-27B | 0.00 | 0.00 | 0.00 | 262K |
| Gemma-4-31B-it | 0.20 | 0.05 | 0.50 | 262K |
| Kimi-K2.7-Code | 0.65 | 0.20 | 3.50 | 262K |
| GLM-5.2 | 0.80 | 0.30 | 4.00 | 1M |
| DeepSeek-V4-Flash | 0.15 | 0.08 | 0.25 | 1M |
| DeepSeek-V4-Pro | 1.00 | 0.25 | 2.50 | 1M |
| gpt-oss-120b | 0.15 | 0.08 | 0.60 | 131K |
| Haiku 4.5 | 1.00 | 0.10 | 5.00 | 200K |
| Sonnet 4.6 | 3.00 | 0.30 | 15.00 | 1M |
| Opus 4.8 | 5.00 | 0.50 | 25.00 | 1M |
| Fable 5 | 10.00 | 1.00 | 50.00 | 1M（出力上限128K） |

![モデル別の価格帯](https://raw.githubusercontent.com/hyqube/tgb-media/main/images/issue_650_aiand_code_review_extension/fig1_price_per_token_ja.png)

## 手法：同じ3ファイル・同じプロンプト・同じCodex監査

対象は実運用中の財務データパイプラインです。開示情報コレクター、取引所コレクター、財務指標抽出ツールの3ファイルに、同一の敵対的コードレビュープロンプトを与えました。

各モデルの指摘は、別ベンダーのローカルCLIであるCodexが`CONFIRMED`、`REFUTED`、`UNCERTAIN`へ監査しています。

![実験フロー](https://raw.githubusercontent.com/hyqube/tgb-media/main/images/issue_650_aiand_code_review_extension/fig2_experiment_flow_ja.png)

3ファイルのうち1つには、Fableが修正する前のバージョンを渡しました。残り2ファイルは元研究時点から変更がありません。これにより、元研究と同じ条件で今回の7モデルにも調査を依頼しています。

| 項目 | 元研究 | 今回 |
| --- | --- | --- |
| 実行形態 | Claude Codeのエージェント | OpenAI互換chat completion APIへの単発呼び出し |
| ファイルアクセス | 直接読み取りツールあり | ツールアクセスなし |
| コードの渡し方 | リポジトリから実ファイルを読む | 本文をプロンプトに直接埋め込む |

!

ここは最重要の制約です。元研究のClaude 4モデルはファイルを直接読むツールアクセスを持つエージェントでした。一方、今回の7モデルはツールなしの単発API呼び出しです。

したがって本稿は、Claudeとai&モデルの公平な能力比較ではありません。低コストな単発APIが、実コードを埋め込んだレビューでどこまで有用な指摘に迫れるかを見るケーススタディです。各モデル・各ファイルの評価も単発実行（N=1）です。

### 実コードを送る前に：利用規約を確認した

実運用コードを新規ベンダーへ送る前に、ai& Inference API Terms of Service（2026-07-06付）を確認しました。

![ai&のAPI利用規約が定めていること](https://raw.githubusercontent.com/hyqube/tgb-media/main/images/issue_650_aiand_code_review_extension/fig12_tos_summary_ja.png)

## 生の指摘件数だけでは判断できない

モデルが多く指摘するほど良いとは限りません。生（Codex監査前に各モデルが自己申告した）の重要度ラベルの基準はモデルごとに異なり、誤検知や判断保留も混ざります。

| モデル | 生・重大 | 生・中 | 生・軽微 | 生指摘計 | 合計所要時間 |
| --- | --- | --- | --- | --- | --- |
| Qwen3.6-27B | 7 | 13 | 9 | 29 | 8分56秒 |
| Gemma-4-31B-it | 7 | 7 | 6 | 20 | 2分02秒 |
| Kimi-K2.7-Code | 11 | 23 | 15 | 49 | 7分14秒 |
| GLM-5.2 | 15 | 25 | 28 | 68 | 10分06秒 |
| DeepSeek-V4-Flash | 12 | 17 | 20 | 49 | 1分23秒 |
| DeepSeek-V4-Pro | 11 | 18 | 17 | 46 | 2分33秒 |
| gpt-oss-120b | 6 | 10 | 16 | 32 | 1分03秒 |

![生・重大バグ指摘件数](https://raw.githubusercontent.com/hyqube/tgb-media/main/images/issue_650_aiand_code_review_extension/fig3_raw_critical_claims_ja.png)

以降は、生の件数ではなく監査後の確認済み件数を主指標にします。

## Codex監査後：精度ランキング

精度は **確認済み ÷ 監査対象** です。`UNCERTAIN`も分母に含めます。

| モデル | 監査対象 | 確認済み | 却下 | 不明 | 精度 |
| --- | --- | --- | --- | --- | --- |
| GLM-5.2 | 67 | 57 | 8 | 2 | 85.1% |
| Kimi-K2.7-Code | 49 | 40 | 6 | 3 | 81.6% |
| DeepSeek-V4-Pro | 48 | 32 | 13 | 3 | 66.7% |
| Qwen3.6-27B | 29 | 19 | 10 | 0 | 65.5% |
| gpt-oss-120b | 32 | 20 | 10 | 1 | 62.5% |
| Gemma-4-31B-it | 20 | 11 | 9 | 0 | 55.0% |
| DeepSeek-V4-Flash | 48 | 25 | 19 | 4 | 52.1% |

![監査精度](https://raw.githubusercontent.com/hyqube/tgb-media/main/images/issue_650_aiand_code_review_extension/fig4_precision_ja.png)

GLM-5.2とKimi-K2.7-Codeが80%を超え、他の5モデルは52〜67%に集中しました。元研究の参考値は、Haiku 4.5が68%、Sonnet 4.6が93%、Opus 4.8が89%、Fable 5が98%です。

GLM-5.2の85.1%は、50,924トークンという大きな出力量を使った結果でもあります。別ドメインや別の実行では、精度と出力量の双方が変わり得ます。

## 確認済み指摘1件あたりのコスト

総額よりも、確認済みの有用な指摘を1件得る費用が運用上は扱いやすい指標です。

| モデル | プロンプト | キャッシュ済み | 出力 | 総コスト | 確認済み | $/確認済み1件 |
| --- | --- | --- | --- | --- | --- | --- |
| Qwen3.6-27B | 34,935 | 0 | 23,847 | $0.0000 | 19 | $0.00000 |
| DeepSeek-V4-Flash | 34,488 | 16,768 | 16,313 | $0.0081 | 25 | $0.00032 |
| gpt-oss-120b | 32,342 | 32,342 | 11,747 | $0.0096 | 20 | $0.00048 |
| Gemma-4-31B-it | 38,869 | 0 | 4,194 | $0.0099 | 11 | $0.00090 |
| DeepSeek-V4-Pro | 34,488 | 34,304 | 17,471 | $0.0524 | 32 | $0.00164 |
| GLM-5.2 | 32,043 | 11,136 | 50,924 | $0.2238 | 57 | $0.00393 |
| Kimi-K2.7-Code | 32,054 | 0 | 50,172 | $0.1964 | 40 | $0.00491 |

元研究のClaude 4 tierは、Haiku 4.5が$0.018、Sonnet 4.6が$0.034、Opus 4.8が$0.055、Fable 5が$0.068でした。

![確認済み指摘1件当たりコスト](https://raw.githubusercontent.com/hyqube/tgb-media/main/images/issue_650_aiand_code_review_extension/fig5_cost_per_confirmed_ja.png)

今回のケースでは、7モデルはいずれもClaude最安のHaiku 4.5より低コストでした。最も高いKimiでも約3.7分の1、Flashは約56分の1です。

ただし、これはClaudeのエージェント型レビューとai&の単発APIレビューを比べた参考値です。公平な能力比較や将来の実費保証ではありません。

入力・キャッシュ入力・出力の構成、キャッシュヒット量、出力量がモデルごとに異なるため、価格表の差はそのまま実効コスト差になりません。

![価格差と実効コスト差](https://raw.githubusercontent.com/hyqube/tgb-media/main/images/issue_650_aiand_code_review_extension/fig6_price_vs_real_cost_ja.png)

実験全体（7モデル×3ファイルの21回、502エラーによる再実行を含む）の総使用料は¥170（約$1.1）でした。同程度のレビューセットを毎日100回、30日実行するなら単純換算で月額約¥510,000ですが、これは対象サイズ・出力・再試行・キャッシュ率で大きく変わる概算です。

参考までに、同じレビュー範囲をSonnet 4.6のみで行うと、1回あたり約$1.33（39件確認済み×$0.034）。同じ月100回×30日換算では約¥615,000となり、モデル数は1つだけなのに、ai&の7モデル合計より高くつく計算になります。

## 複数モデル併用の価値：ユニーク指摘

204件の確認済み指摘について、他の6モデルにも同じ根本原因の指摘があるかをCodexが自動照合しました。

| モデル | 確認済み | 重複 | ユニーク |
| --- | --- | --- | --- |
| GLM-5.2 | 57 | 45 | 12 |
| Kimi-K2.7-Code | 40 | 32 | 8 |
| DeepSeek-V4-Pro | 32 | 25 | 7 |
| DeepSeek-V4-Flash | 25 | 23 | 2 |
| gpt-oss-120b | 20 | 18 | 2 |
| Qwen3.6-27B | 19 | 18 | 1 |
| Gemma-4-31B-it | 11 | 10 | 1 |
| 合計 | 204 | 171 | 33 |

![重複とユニーク指摘](https://raw.githubusercontent.com/hyqube/tgb-media/main/images/issue_650_aiand_code_review_extension/fig7_shared_vs_unique_ja.png)

約6件に1件は、そのモデルだけが見つけた指摘でした。ユニーク率はDeepSeek-V4-Pro、GLM-5.2、Kimi-K2.7-Codeが約20%前後で、精度ランキングとは異なる並びです。

| 重要度 | 件数 |
| --- | --- |
| 重大 | 1 |
| 中 | 11 |
| 軽微 | 21 |
| 合計 | 33 |

![ユニーク指摘の重要度](https://raw.githubusercontent.com/hyqube/tgb-media/main/images/issue_650_aiand_code_review_extension/fig8_unique_severity_ja.png)

唯一の重大なユニーク指摘は次のものでした。

* **Kimi-K2.7-Code / 取引所コレクター**：UTF-8 BOMが2種類の入力ファイルの先頭ヘッダー名を壊し、列マッチングを無効化する。

多くのユニーク指摘は軽微〜中程度でしたが、強いモデル同士でも見逃し方が完全には重ならないことが分かります。

## 限界と結論

これは財務データ処理の3ファイルに対する単発評価です。同じモデルを再実行すれば、指摘内容や件数が変わる可能性があります。フロントエンド、インフラYAML、大規模リポジトリへは、そのまま一般化できません。

また、精度・確認済み件数・ユニーク判定はすべてCodexという単一監査ツールに依存しています。Codex自身の判断を全数人手検証したわけではありません。

今回の条件では、GLM-5.2とKimi-K2.7-Codeは監査付きレビューの主力候補になり得ます。DeepSeek-V4-Proは、ユニーク発見の多さから併用時の取りこぼし防止役として検討できます。

![運用サマリー](https://raw.githubusercontent.com/hyqube/tgb-media/main/images/issue_650_aiand_code_review_extension/infographic_summary_ja.png)

重要なのは「最も賢いモデル」を一つ選ぶことではなく、確認済みの価値を低コストで増やし、見逃しを減らせるレビュー運用を作ることです。

**ai& Inference**: <https://aiand.com/>
