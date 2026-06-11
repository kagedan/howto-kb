---
id: "2026-06-10-google-cloudgeapでclaude-fable-5を使えるようになりました-01"
title: "Google Cloud（GEAP）でClaude Fable 5を使えるようになりました"
url: "https://qiita.com/asayan_mana/items/63dbd68350738e6d818e"
source: "qiita"
category: "ai-workflow"
tags: ["AI-agent", "Gemini", "qiita"]
date_published: "2026-06-10"
date_collected: "2026-06-11"
summary_by: "auto-rss"
query: ""
---

# はじめに

2026年6月9日、Anthropic社の最新モデルであるClaude Fable 5 が、Google CloudのGemini Enterprise Agent Platform（GEAP）で一般提供（GA）されました。

Fable 5は従来のOpusシリーズとは位置づけが異なります。本記事ではFable 5の特徴・性能・GEAPにおける公式情報を整理します。

---

## Claudeのモデルを整理する

まず、現在公開されているClaudeのモデルを押さえておきます。

| ティア | モデル名 | 位置づけ |
|--------|---------|---------|
| Mythos  | Claude Mythos 5 | 安全制限を一部解除した研究・防衛向け（限定公開） |
| Fable  | Claude Fable 5 | Mythos 5 と同じ基盤（一般公開を目的としたセキュリティ対策済み） |
| Opus  | Claude Opus 4.8 | 従来のフラッグシップ |
| Sonnet  | Claude Sonnet 4.6 | バランス型 |
| Haiku  | Claude Haiku 4.5 | 軽量・高速 |

Fable 5 は **Mythos 5 と同一の基盤モデル** ですが、一般ユーザーが安全に使えるようセキュリティ対策を講じたモデルです。Anthropic はこれを「一般提供した中で最も強力なモデル」と位置づけています。

---

## Claude Fable 5のベンチマーク

Anthropic 公式ブログに掲載している評価指標のうち、ほぼすべての評価指数で最高スコアとなっています。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4439702/a72701a4-ac6a-450a-927f-600282212fa4.png)

出典：[Anthropic 公式ブログ](https://www.anthropic.com/news/claude-fable-5-mythos-5) 

---

## FableとMythosの違い

Mythosは非常に高性能なモデルのため、悪用によるセキュリティ被害のリスクがあります。そのため、セキュリティ対策を講じたモデルとしてFableが公開されました。
Anthropic社の公式ブログによるとセキュリティリスクのあるクエリについては、Claude Opus 4.8にフォールバックする仕組みとしているようです。

>原文：Releasing a model this capable comes with risks. Without safeguards, Fable 5’s capabilities in areas like cybersecurity could be misused to cause serious damage. We’ve therefore launched the model with safeguards that mean queries on some topics will instead receive a response from our next-most-capable model, Claude Opus 4.8. To release the model both safely and quickly, we’ve tuned these safeguards conservatively


>機械翻訳：これほど高性能なモデルをリリースするにはリスクが伴います。セキュリティ対策を講じなければ、サイバーセキュリティなどの分野におけるFable 5の機能が悪用され、深刻な被害を引き起こす可能性があります。そのため、一部のトピックに関するクエリに対しては、次善の選択肢として、より高性能なモデルであるClaude Opus 4.8から応答が返されるように、セキュリティ対策を施した上でモデルをリリースしました。モデルを安全かつ迅速にリリースするために、これらのセキュリティ対策は控えめに設定されています。

出典：[Anthropic 公式ブログ](https://www.anthropic.com/news/claude-fable-5-mythos-5) 


---

## GEAPにおけるClaude Fableの公式情報

### 公式情報
| 項目 | 内容 | 
|--------|---------|
| モデル ID | claude-fable-5 | 
| リリースステージ | GA | 
| 廃止予定日 | 2027 年 6 月 8 日以降 | 
| サポートされている入力	 | テキスト、画像、PDF | 
| サポートされている入力 | テキスト | 
| 最大入力トークン| 1,000,000 | 
| 最大出力トークン| 128,000 | 

その他詳細は、出典元をご確認ください。

出典：[Gemini Enterprise Agent Platform - Claude Fable 5](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/claude/fable-5?hl=ja)

### コスト
2026年6月10日時点では、公式ドキュメントにGEAPでFableを利用する際のコストが掲載されておりませんでした。
[Google Cloud公式ドキュメント - Anthropic の Claude モデル](https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing?hl=ja&_gl=1*1wcdzi2*_ga*MTAxNzY2NzguMTc3OTg4ODg1NA..*_ga_WH2QY8WWF5*czE3ODExMDMzNjYkbzM4JGcxJHQxNzgxMTAzOTczJGo1OSRsMCRoMA..#claude-models)



---

## まとめ

- Claude Fable 5 は Mythos 5 と同一の基盤を持つ、一般公開向け最強クラスのモデル
- ほぼすべてのベンチマークで最高スコア
- GEAPにて `claude-fable-5` のモデルIDを指定することで即座に利用可能

長い・複雑・マルチステップなタスクほど恩恵が大きいモデルです。GEAP を使っているなら試してみる価値があります。

---

## 参考リンク

- [Claude Fable 5 & Claude Mythos 5 - Anthropic](https://www.anthropic.com/news/claude-fable-5-mythos-5)
- [Cloud Fable 5 on Google Cloud - Google Cloud Blog](https://cloud.google.com/blog/products/ai-machine-learning/cloud-fable-5-on-google-cloud?hl=en)
- [Claude Fable 5 on GEAP - Google Cloud Docs](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/claude/fable-5)
- [Anthropic's Claude models on GEAP](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/claude)
