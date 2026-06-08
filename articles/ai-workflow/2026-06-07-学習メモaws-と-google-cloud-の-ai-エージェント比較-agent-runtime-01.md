---
id: "2026-06-07-学習メモaws-と-google-cloud-の-ai-エージェント比較-agent-runtime-01"
title: "【学習メモ】AWS と Google Cloud の AI エージェント比較 — Agent Runtime × AgentCore"
url: "https://zenn.dev/rrrrrrrrrrr/articles/f7eb6dfa07f5e9"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "API", "AI-agent", "Gemini", "zenn"]
date_published: "2026-06-07"
date_collected: "2026-06-08"
summary_by: "auto-rss"
query: ""
---

## この記事について

---

## 1. Amazon Bedrock とは？Google Cloud の世界に置き換えてみると？

Amazon Bedrock とは、AWS が提供する生成AIサービス。主に以下の表のサービスから構成されています。  
Google Cloud の世界に置き換えてみるとこんな感じです。（筆者目線のため間違いがあれば教えてください）

| サービス・機能 | 概要 | Google Cloud の世界では？ |
| --- | --- | --- |
| Amazon Bedrock（全般） | 様々なAIモデルをサーバレスで利用できるサービス | Gemini Enterprise Agent Platform（旧：Vertex AI） |
| Strands Agents | AWS が提供するオープンソースのエージェント開発フレームワーク | ADK（Agent Development Kit） |
| Bedrock AgentCore | AI エージェントを本番環境で構築・デプロイ・運用するためのプラットフォーム | Agent Runtime（旧：Vertex AI Agent Engine） |
| Bedrock ナレッジベース | RAGを実現するマネージドサービス | Agent Search（旧：Vertex AI Search） |

---

## 2. 普段の動線で見る対応

エージェントを作る場合はそれぞれどのツールを使う必要があるのか？といったことを改めて整理してみました。

| 役割 | Google Cloud | AWS |
| --- | --- | --- |
| 書く（フレームワーク） | ADK | Strands Agents |
| 最適な環境で動かす（デプロイ・実行） | Agent Runtime | AgentCore Runtime |

※なお、Google Cloud では Cloud Run や GKE、AWS では Lambda などでも工夫すれば AI エージェントをホストすること自体は可能です。ただし「エージェント専門の最適化された基盤」という観点では、上記が該当します。

---

## 3. AgentCore 全体 ↔ Google Cloud のマッピング

現時点の私の理解度のマッピング。細かい仕様などは当然違うので今後理解を深めていきたいです！

| 機能 | Google Cloud | AWS |
| --- | --- | --- |
| 実行・デプロイ | Agent Runtime（本体） | AgentCore **Runtime** |
| 記憶 | Agent Runtime の **Memory Bank** | AgentCore **Memory** |
| 認証 | [Agent Identity](https://docs.cloud.google.com/gemini-enterprise-agent-platform/govern/agent-identity-overview) | AgentCore **Identity** |
| ツール / API 連携 | ADK の tools / MCP | AgentCore **Gateway** |
| 監視 | Cloud Trace / Logging | AgentCore **Observability** |

> 補足（マッピングの注意点）
>
> * **ツール/API 連携**：AgentCore Gateway は「既存 API や Lambda を MCP ツールに変換する」基盤。GCP 側は ADK tools + MCP が近いものの、専用のマネージド基盤としての対応物は現状あまり明確ではありません。

### 認証を3つの軸で分けて見る

本編についてはまずは Google Cloud 側で整理します。

「認証」とひとことで言っても、エージェント基盤では役割が3つに分かれます。Google Cloud の Agent Runtime ではそれぞれの担い手が異なるので、混同しないよう整理しておきます。  
AWS については [Amazon Bedrock AgentCore 実践入門 Strands Agentsで構築するAIエージェント [AWS深掘りガイド]](https://www.sbcr.jp/product/4815641238/) 第7章に詳しく記載があるので学んでから記載します^^

| 認証の軸 | 何を守るか | Google Cloud での担い手 |
| --- | --- | --- |
| インバウンド | 誰がエージェントを呼び出せるか | **IAM** |
| アウトバウンド | エージェントが GCP リソースへアクセスする際の身元 | **Agent Identity**（SPIFFE / X.509） |
| 第三者 OAuth 代理 | ユーザーに代わって外部サービス（Slack・GitHub 等）へアクセス | **Agent Identity の Auth manager**（Preview） |

## 4. 感想

昨年3月に、私がAWS、Azure、Google Cloud 3社のAIエージェント構成を比較した記事を執筆したときよりも、マルチクラウドで同じようなことが実現できるようになってきていると感じました。大枠で捉えると、デプロイ基盤（Agent Runtime / AgentCore Runtime）、記憶、認証など、主要な部品がどちらのクラウドにも揃いつつあり、両者が同じ方向に収束してきている印象です。逆に言えば、マルチクラウドでアップデートを追い続けること自体が、AIエージェントの潮流についていく一番の近道になりそうだと思いました。

次は各機能の違いを、ハンズオンを通じて実際に手を動かしながら比較していきたいです。

※当時（2025年3月）に私が執筆した記事：[生成AIのAIエージェントを大手3社（AWS、Azure、Google Cloud）で徹底比較してみた](https://blog.g-gen.co.jp/entry/comparing-agent-architecture-across-cloud-vendors)

---

## 5. 参考ドキュメント
