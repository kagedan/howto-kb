---
id: "2026-07-18-claudeってazureで使えないの-2026年6月にgaしてましたmicrosoft-found-01"
title: "「ClaudeってAzureで使えないの？」→ 2026年6月にGAしてました（Microsoft Foundry）"
url: "https://qiita.com/ait0303/items/c3b343ea838f3aad3773"
source: "qiita"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "OpenAI", "GPT", "Python", "JavaScript"]
date_published: "2026-07-18"
date_collected: "2026-07-19"
summary_by: "auto-rss"
query: ""
---

> この記事は導入の要点だけをまとめた入口記事です。**FoundryでのデプロイやMessages APIの呼び方、本家API/Bedrockとの違いまで含めた本編は、ブログにまとめています。**
> 👉 [ClaudeがMicrosoft Foundryで使える！2026年6月GA｜三者提携の背景とMessages APIでの使い方](https://ait0303.com/claude-on-foundry/)

## こんな人向け

- 社内から「ChatGPTじゃなくてClaudeを使いたい」と言われたが、Azure環境で安全に動かせるのか分からない
- 「ClaudeはAnthropic本家かAWS Bedrock」という古い認識のままアップデートできていない
- GAとプレビューの違いを曖昧にしたまま社内提案して事故りたくない

## 結論：2026年6月29日、ClaudeがMicrosoft FoundryでGA

これまでAzureで生成AIといえばGPT系（Azure OpenAI）が中心でした。ですが状況は変わっています。

- **2026年6月29日、AnthropicのClaudeモデルがMicrosoft Foundry（旧Azure AI Foundry）でGA（一般提供）**
- 提供モデルは **Claude Opus 4.8**（高精度）と **Claude Haiku 4.5**（高速・軽量）
- 呼び出しは **Messages API**（Anthropic標準の形式）

## いちばん大事：GAとプレビューの区別

「ClaudeがFoundryでGA」と言っても、**すべての形態がGAではありません**。ここを混同すると事故ります。

| 提供形態 | 推論を動かす場所 | ステータス（2026/6/29時点） |
|---|---|---|
| Azureホスト版 | Azure（Microsoft）側 | **GA** |
| Anthropicインフラ版 | Anthropic側 | **プレビュー** |

本番前提で設計するなら、まずは **GAされている「Azureホスト版」** を選ぶのが安全です。

## なぜMicrosoftとAnthropicが組んだ？

起点は **2025年11月18日のMicrosoft × NVIDIA × Anthropicの三者戦略提携** です。

- Anthropic … Claude（頭脳）
- Microsoft/Azure … 販売・運用基盤（認証・ガバナンス・課金）
- NVIDIA … 計算資源（GPUは **GB300 Blackwell Ultra**）

つまり「いつものAzureの認証・コスト管理のまま、GPTだけでなくClaudeも選べる」ようになった、というのが本質です。

## どう呼ぶ？（エンドポイントだけ先出し）

```
https://<resource>.services.ai.azure.com/anthropic/v1/messages
```

認証は **Entra ID**（推奨・キーレス）または **APIキー**。Python / JavaScript / REST から Messages API 形式で叩けます。

---

## 続きはブログで

- Foundryでデプロイ → Messages APIで呼ぶ**最短の手順の全体像**
- 対応機能（prompt caching / extended thinking / tool streaming）
- **本家Anthropic API・AWS Bedrockとの違い**と、Azureで使う利点（Entra ID・ガバナンス一元化）
- 全社に安全に配るには？（APIMを前段に置く実践への導線）

を、Microsoft Learn（公式）を日本語で噛み砕いて解説しています。

👉 **[ClaudeがMicrosoft Foundryで使える！2026年6月GA｜三者提携の背景とMessages APIでの使い方](https://ait0303.com/claude-on-foundry/)**
