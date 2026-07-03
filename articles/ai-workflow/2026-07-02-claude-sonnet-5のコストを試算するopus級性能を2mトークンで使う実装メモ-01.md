---
id: "2026-07-02-claude-sonnet-5のコストを試算するopus級性能を2mトークンで使う実装メモ-01"
title: "Claude Sonnet 5のコストを試算する—Opus級性能を$2/Mトークンで使う実装メモ"
url: "https://zenn.dev/kairosai/articles/c35e38c26da95e"
source: "zenn"
category: "ai-workflow"
tags: ["API", "Gemini", "Python", "zenn"]
date_published: "2026-07-02"
date_collected: "2026-07-04"
summary_by: "auto-rss"
query: ""
---

## この記事について

2026年7月、AnthropicがClaude Sonnet 5をリリースしました。Opus 4.8に迫る性能を持ちながら、価格は$2/M入力トークン（8月末までの導入価格）で、Anthropic本体に加えAmazon Bedrock、Google Vertex AI、Microsoft Azureからも利用できます。

本記事では、Claude APIを使ってSonnet系モデルのコストを試算するシンプルなPythonスクリプトを紹介し、実際の業務でどの程度のコスト感になるかを見積もります。技術記事ですが、AI活用やAI副業でのコスト管理にも応用できる内容です。

## モデルの位置付け（2026年7月時点）

| モデル | 特徴 | 参考価格帯 |
| --- | --- | --- |
| Claude Opus 4.8 | 最上位モデル | 高価格帯 |
| Claude Sonnet 5 | Opus級に迫る性能、最もエージェント的なSonnet | $2/M入力（導入価格〜8/31） |
| Claude Sonnet 4.6 | 旧世代Sonnet | Sonnet 5より低性能 |

Sonnet 5は「Opus級の性能を、Sonnet並みの価格で」というのが最大のポイントです。

## コスト試算スクリプト

APIキーがなくても動作する、トークン数と価格からコストを概算するスクリプトです。実際に業務でAPIを叩く前の見積もりに使えます。

```
# cost_estimator.py
# Claude Sonnet 5 のコスト試算スクリプト

# 2026年7月時点の参考価格（$ / 1Mトークン）
# ※実際の最新価格は必ずAnthropic公式ドキュメントで確認してください
PRICING = {
    "claude-sonnet-5": {"input": 2.00, "output": 10.00},  # 導入価格(〜8/31)
        "claude-opus-4.8": {"input": 15.00, "output": 75.00},  # 参考値
        }

        def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
            """指定モデル・トークン数からコスト(USD)を概算する"""
                if model not in PRICING:
                        raise ValueError(f"未対応のモデルです: {model}")

                            price = PRICING[model]
                                input_cost = (input_tokens / 1_000_000) * price["input"]
                                    output_cost = (output_tokens / 1_000_000) * price["output"]
                                        return round(input_cost + output_cost, 4)

                                        def compare_models(input_tokens: int, output_tokens: int) -> None:
                                            """複数モデルのコストを比較表示する"""
                                                print(f"入力: {input_tokens:,}トークン / 出力: {output_tokens:,}トークン")
                                                    print("-" * 50)
                                                        for model in PRICING:
                                                                cost = estimate_cost(model, input_tokens, output_tokens)
                                                                        print(f"{model:20s} : ${cost}")

                                                                        if __name__ == "__main__":
                                                                            # 例: 副業のブログ記事生成1本あたり
                                                                                # 入力(プロンプト+参考資料) 8,000トークン、出力(記事本文) 3,000トークンを想定
                                                                                    compare_models(input_tokens=8000, output_tokens=3000)
                                                                                    ```

                                                                                    実行結果イメージ:

                                                                                    ```
                                                                                    入力: 8,000トークン / 出力: 3,000トークン
                                                                                    --------------------------------------------------
                                                                                    claude-sonnet-5      : $0.046
                                                                                    claude-opus-4.8      : $0.345
                                                                                    ```

                                                                                    このように、同じ作業量でもモデル選択によってコストが7倍以上変わることがわかります。記事生成やコードレビューなど「毎日繰り返す作業」ほど、モデルのコスト差が積み重なって効いてきます。

                                                                                    ## 実務での使い分けの考え方

                                                                                    筆者はAI副業・コンテンツ制作の現場で、次のような基準でモデルを使い分けています。

                                                                                    - **下書き・大量処理・定型作業**: Sonnet 5（コストと性能のバランスが良い）
                                                                                    - **最終チェック・重要な意思決定・複雑な推論**: Opus 4.8（コストは高いが精度を優先）
                                                                                    - **単純な分類・要約**: より軽量なモデル（Gemini 3.5 Flashなど他社の軽量モデルも選択肢）

                                                                                    Sonnet 5がOpus級に近づいたことで、これまで「Opusじゃないと不安」だった作業の多くをSonnet 5に移行できる可能性があります。実際に移行する際は、必ず自分のユースケースでの精度検証を行ってから本番運用に切り替えることをおすすめします。

                                                                                    ## まとめ

                                                                                    Claude Sonnet 5は、性能と価格のバランスが大きく改善された注目モデルです。API価格は今後変動する可能性があるため、本番導入前には必ず公式ドキュメントで最新価格を確認してください。今回紹介したような簡易コスト試算スクリプトを手元に用意しておくと、モデル選定やAI活用の副業案件の見積もりの際にも役立ちます。
```
