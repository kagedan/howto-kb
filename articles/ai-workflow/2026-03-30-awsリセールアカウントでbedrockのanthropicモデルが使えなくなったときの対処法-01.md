---
id: "2026-03-30-awsリセールアカウントでbedrockのanthropicモデルが使えなくなったときの対処法-01"
title: "AWSリセールアカウントでBedrockのAnthropicモデルが使えなくなったときの対処法"
url: "https://qiita.com/nishikawa/items/4abd518c0def925f735a"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-03-30"
date_collected: "2026-03-31"
summary_by: "auto-rss"
---

## はじめに

AWS のリセール（請求代行）アカウントで Amazon Bedrock の Anthropic モデルを使用していたところ、モデルの更新をきっかけに2つの問題が立て続けに発生しました。

- **問題① リセールアカウントで新しい Anthropic モデルが使えない**
- **問題② 別アカウントの Bedrock を使うようにしたら、今度は認証情報が1時間で切れる**

この記事では、その原因と対処法をまとめます。

**構成のイメージ**

```mermaid
flowchart LR
    subgraph resale1[リセールアカウント]
        L1[Lambda] -->|①AI生成リクエスト| B1[Bedrock]
        B1 -->|②生成テキストを返す| L1
        L1 -->|③JSONとしてS3に保存| S1[S3]
    end
```

某スポーツの試合情報を基にハイライトテキストを生成する用途で使っていました。

---

## 問題① リセールアカウントで Anthropic モデルが制限さ
