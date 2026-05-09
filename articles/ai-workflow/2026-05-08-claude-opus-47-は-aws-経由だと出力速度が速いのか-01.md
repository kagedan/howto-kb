---
id: "2026-05-08-claude-opus-47-は-aws-経由だと出力速度が速いのか-01"
title: "Claude Opus 4.7 は AWS 経由だと出力速度が速いのか？"
url: "https://zenn.dev/aws_japan/articles/2026-05-08-opus4-7-speed"
source: "zenn"
category: "ai-workflow"
tags: ["API", "zenn"]
date_published: "2026-05-08"
date_collected: "2026-05-09"
summary_by: "auto-rss"
query: ""
---

答え: YES.

以下は 2026-05-08 に取得した Artificial Analysis <https://artificialanalysis.ai/> における Opus 4.7 の出力速度を比較したものです。

![Artificial Analysis における Opus 4.7 の出力速度比較](https://static.zenn.studio/user-upload/deployed-images/8f97bc80a175d1d3d962331d.png?sha=fca8ea65af33ef149f635b7b05f2945d291f2b3e)  
*2026-05-08 に取得した Artificial Analysis におけるプロバイダ毎の Opus 4.7 の出力速度比較*

本記事では、この結果を読み解いていきたいと思います。

## Artificial Analysis とは

Artificial Analysis <https://artificialanalysis.ai/> は AI モデルのベンチマークサイトで、米国の同名の会社が運営しているものです。  
Nat Friedman, Daniel Gross, Andrew Ng が出資しており、AI モデルのベンチマーク情報源としては最もよく使われるものの一つであると感じます。

広範なベンチマークの結果が整備されているので、必要に応じてベンチマークの結果を参照して比較することができます。  
AI モデルの全体的な性能指標としてよく使われるのは、以下で示される Artificial Analysis Intelligence Index です。これは、エージェント的なタスク、コーディングタスク、一般的なタスク、科学的なタスクなど複数の主要なベンチマークタスクの結果を加重平均したものになっています。

![Artificial Analysis における Artificial Analysis Intelligence Index](https://static.zenn.studio/user-upload/deployed-images/8c7a54aa8d10738015bb3ddd.png?sha=e01da76878ccb23129a0733159954ec56d7bab37)  
*2026-05-08 に取得した Artificial Analysis における Artificial Analysis Intelligence Index*

その他にも、個別のベンチマークタスク、コスト効率性、処理速度、など様々な切り口で比較することが可能です。

### プロバイダ毎の比較

Artificial Analysis の興味深い切り口の一つが API プロバイダごとの比較です。  
これは同じモデルでもプロバイダによってスループットや Time to First Token などが変わるため、それを定量的に比較するためのものです。

冒頭で示した結果は Claude Opus 4.7 (Adaptive Reasoning, Max Effort) に対する各プロバイダの情報をまとめたページ <https://artificialanalysis.ai/models/claude-opus-4-7/providers> から取得したものになります。

どのような条件で実験しているかは <https://artificialanalysis.ai/methodology/performance-benchmarking> で詳しく説明されており、いくつかピックアップすると以下のようなものになります:

* 1k/10k入力トークンを1日8回テストし、100k入力トークンを1週間に1回テストする。
* 個々のテスト実行では、テスト時に生成したユニークなプロンプトを使用する。プロンプトは、さまざまな長文入力コンテンツ（例：記事）と、説明/要約、質疑応答生成、比較分析、翻訳、視覚的アーティファクト生成を含むさまざまなタスクを組み合わせている。
* パフォーマンス測定値は過去72時間の中央値（P50）を用いる。100kプロンプト長ワークロードは週1回テストされ、過去14日間の中央値（P50）を用いる。
* テストをするサーバーは Google Cloud の us-central1-a ゾーンにホストする。

これで実験をして、 `出力速度 ＝ （総トークン数 − 最初のチャンクトークン数） ÷ （最終トークンチャンク受信時刻 − 最初のトークンチャンク受信時刻）` を測定したものが、冒頭で示した以下の結果になります。この結果を以って、AWS 経由だと出力速度が速いと結論づけています。

![Artificial Analysis における Opus 4.7 の出力速度比較](https://static.zenn.studio/user-upload/deployed-images/8f97bc80a175d1d3d962331d.png?sha=fca8ea65af33ef149f635b7b05f2945d291f2b3e)  
*（再掲）2026-05-08 に取得した Artificial Analysis におけるプロバイダ毎の Opus 4.7 の出力速度比較*

他の指標について見てみると、大きな差は見られません。  
例えば、 `エンドツーエンドレスポンス時間 ＝ 入力処理時間 ＋ 平均 Reasoning トークン数 ÷ Reasoning 出力速度 ＋ 500 ÷ 回答出力速度` で定義される、入力処理や Reasoning も含めて 500 トークンの回答を生成する時間に関しては、以下で見るようにプロバイダ毎の明確な違いは見られません。

![Artificial Analysis における Opus 4.7 の End-to-End Response Time 比較](https://static.zenn.studio/user-upload/deployed-images/c5451fde1d3522c89b579b8c.png?sha=7c6a9cdc9ac3d2ab62cfd86bf2c19c8a35621a01)  
*2026-05-08 に取得した Artificial Analysis におけるプロバイダ毎の Opus 4.7 の End-to-End Response Time 比較*

これらの結果を見ると、トークン数が小さい場合は明確な差は感じづらいが、トークン数が大きい場合は差が顕著に出ていると理解できます。  
これは Opus 4.7 に特徴的であり、Opus 4.6 の場合 <https://artificialanalysis.ai/models/claude-opus-4-6-adaptive/providers> は大きな差は見られません。

## その他の情報源

Artificial Analysis 以外にも、例えば OpenRouter でもパフォーマンスのモニタリングが公開 <https://openrouter.ai/anthropic/claude-opus-4.7/performance> されています。

![OpenRouter における Opus 4.7 のスループット比較](https://static.zenn.studio/user-upload/deployed-images/4a1aa6fe4edab538fab9d1c4.png?sha=6dabcb373371ba1971d632437fdf8078e6b10d40)  
*2026-05-08 に取得した OpenRouter におけるプロバイダ毎の Opus 4.7 のスループット比較*

Artificial Analysis と比べると OpenRouter のメトリクスは多様な本番トラフィックから算出された結果であると説明 <https://openrouter.ai/announcements/auto-exacto> されており、プロバイダ間で同じ条件で比較されていなかったりトークンの長さを分けた系統的な実験をしているわけでもないことに注意してください。

## まとめ

「なんか AWS 経由で使うと Opus 4.7 の処理が速い気がする」という話題を見て、気になったので少し調べてまとめてみましたが、トークン数が大きい場合には明確に違いが出ていました。  
Artificial Analysis は様々な切り口で比較できるので見ていて面白いですね。

Opus 4.7 はリリースされて一ヶ月も経っていないので、今後様々な最適化がなされて結果が変わっていくことが想定されるため、あくまで記事執筆時点の情報であることに注意してください。
