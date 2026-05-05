---
id: "2026-05-03-claude-mythos-preview入門-swe-bench-939project-glass-01"
title: "Claude Mythos Preview入門 — SWE-bench 93.9%・Project Glasswingの全貌"
url: "https://zenn.dev/kai_kou/articles/204-claude-mythos-preview-project-glasswing-guide"
source: "zenn"
category: "ai-workflow"
tags: ["API", "zenn"]
date_published: "2026-05-03"
date_collected: "2026-05-05"
summary_by: "auto-rss"
---

## はじめに

2026年4月7日、Anthropicは史上最も強力なモデル「**Claude Mythos Preview**」を限定公開しました。SWE-bench Verifiedで93.9%を達成し、全主要OSと全主要ブラウザでゼロデイ脆弱性を数千件自律発見したこのモデルは、通常のAPI公開なしに**防衛的サイバーセキュリティ専用**として提供されています。

Amazon、Apple、Microsoft、Googleなど12社以上が参加する「**Project Glasswing**」という連合の中核を担うClaudeの新モデルについて、公開情報をもとに詳しく解説します。

### この記事で学べること

* Claude Mythos Previewのベンチマーク性能と他モデルとの比較
* ゼロデイ脆弱性自律発見能力の詳細
* Project Glasswingの構造・参加企業・資金規模
* アクセス方法・料金体系
* 開発者への影響と示唆

### 対象読者

* AIセキュリティ・AIエージェント技術の動向に関心があるエンジニア
* Claude APIを活用しているサービス開発者
* サイバーセキュリティ担当者

## TL;DR

* **Claude Mythos Preview**: SWE-bench Verified 93.9%、業界最高水準のコーディング・セキュリティ性能
* **一般公開なし**: 招待制・防衛的サイバーセキュリティ用途限定
* **Project Glasswing**: Amazon・Apple・Microsoft等12社+40以上の組織が参加する防衛的セキュリティ連合
* **Anthropicコミット**: $100M使用クレジット + OSS組織への$4M寄付
* **料金**: $25/M入力トークン・$125/M出力トークン（招待制）

---

## Claude Mythos Preview とは

Claude Mythos Previewは、Anthropicが2026年4月7日に公開した汎用フロンティアモデルです。コーディング・数学・セキュリティタスク全般で優れた性能を示しますが、特筆すべきはその**コンピュータセキュリティ能力**です。

公式発表によると、Anthropicは意図的にこのモデルの一般公開をしないと明言しています。その理由は「モデルの能力が公共の安全にとってリスクになり得る」ためです。

## ベンチマーク性能の詳細

### コーディング性能

| ベンチマーク | Mythos Preview | Opus 4.6 | GPT-5.4 | Gemini 3.1 Pro |
| --- | --- | --- | --- | --- |
| SWE-bench Verified | **93.9%** | 80.8% | — | — |
| SWE-bench Pro | **77.8%** | — | — | — |
| Terminal-Bench 2.0 | **82%** | — | 75.1% | 68.5% |

SWE-bench VerifiedはGitHubのリアルなバグ修正タスクを自律的に解決する能力を測定するベンチマークです。Mythos Previewの93.9%はOpus 4.6を13.1ポイント上回り、2026年4月時点での業界最高スコアとなっています。

### 数学・推論性能

| ベンチマーク | Mythos Preview | Opus 4.6 差分 |
| --- | --- | --- |
| USAMO 2026 | **97.6%** | +55.3pt |

USAMO（米国数学オリンピック）2026年版で97.6%という驚異的なスコアを達成しました。

### サイバーセキュリティ性能

| ベンチマーク | Mythos Preview | Opus 4.6 |
| --- | --- | --- |
| CyberGym | **83.1%** | 66.6% |
| Firefox 147（exploit生成数） | **181件** | 2件 |

CyberGymはAIエージェントの脆弱性解析能力を評価するベンチマークです。Mythos Previewは前世代のOpus 4.6と比べて約16.5ポイント高いスコアを示しています。

Firefox 147のベンチマークでは、Mythos Previewが181件のexploitを生成したのに対し、Opus 4.6は2件にとどまりました。**90倍**という差は定量的に見ても異次元の能力差を示しています。

---

## ゼロデイ脆弱性の自律発見能力

Anthropicによると、Claude Mythos Previewは過去数週間で以下を達成しています:

* **全主要OS・全主要ブラウザ**でゼロデイ脆弱性を**数千件**自律発見
* 最古は**27年間存在していたOpenBSDのバグ**
* Webブラウザに対して、レンダラーとOSSサンドボックスの両方を突破する複雑なJITヒープスプレーを含む4つの脆弱性を連鎖させたexploitを開発

従来型のベンチマーク（既知の脆弱性の再現）ではなく、**未発見のゼロデイを実際に見つける**という実世界タスクへのフォーカスは、モデルが既存のベンチマークを飽和させているためとAnthropicは説明しています。

---

## Project Glasswing の全貌

### 概要

Project Glasswingは、AIの時代における重要ソフトウェアインフラのセキュリティを確保することを目的とした連合です。Claude Mythos Previewにアクセスできる組織は、防衛的サイバーセキュリティ活動（脆弱性発見・修正）のみに使用するという条件を受け入れています。

### 参加組織

**ローンチパートナー（12社以上、Anthropic含む）:**

| カテゴリ | 企業・組織 |
| --- | --- |
| AI | Anthropic |
| クラウド | Amazon Web Services, Microsoft, Google |
| テクノロジー | Apple, Broadcom, NVIDIA |
| セキュリティ | Cisco, CrowdStrike, Palo Alto Networks |
| 金融 | JPMorganChase |
| OSS | Linux Foundation |

さらに、**40以上の追加組織**が重要ソフトウェアインフラの構築・保守に携わる組織として招待されています。

### Anthropicの財務コミットメント

* **使用クレジット: $100M**（Project Glasswing参加組織への提供）
* **OSS組織への寄付: $4M**

### 意義

参加企業のほとんどは相互に競合するテクノロジー大手ですが、「重要インフラのセキュリティ確保」という共通目標のもとで協力するという点は注目に値します。CrowdStrikeのような純粋なセキュリティ専業企業から、JPMorganChaseのような金融機関まで参加していることからも、プロジェクトの幅広さがわかります。

---

## アクセス方法と料金

### アクセス経路

Claude Mythos Previewは以下のプラットフォームで利用可能ですが、いずれも**招待制**です:

* **Claude API**（claude.ai）
* **Amazon Bedrock**
* **Google Cloud Vertex AI**
* **Microsoft Foundry**

一般開発者向けのセルフサーブサインアップは提供されておらず、自己申し込みによる取得はできません。

### 料金

Project Glasswing参加組織向け（初期$100Mクレジット使用後）の料金は以下の通りです:

| トークン種別 | 単価 |
| --- | --- |
| 入力 | $25 / 100万トークン |
| 出力 | $125 / 100万トークン |

参考として、Claude Opus 4.6（一般公開モデル）は入力$15/M、出力$75/Mです。Mythos Previewは約1.67倍のプレミアム設定となっています。

---

## 開発者への示唆

### 現時点での影響

一般開発者はClaude Mythos Previewに直接アクセスできませんが、以下の観点から注目する価値があります:

1. **AIセキュリティの転換点**: AIが「脆弱性を発見・悪用できる」レベルに達したことが公式に認められた最初のケースです。セキュアなAIエージェント設計の重要性が増しています。
2. **今後のモデル展開の先行指標**: AnthropicはMythosの能力を参照点として将来的なモデルに反映させると考えられます。Opus 4.6より13ポイント上のSWE-benchスコアは、次世代公開モデルで一部反映される可能性があります。
3. **防衛的セキュリティワークフローの標準化**: Project Glasswingで採用されているAI駆動の脆弱性スキャン・修正のワークフローは、将来的に一般開発者向けのセキュリティツールとして提供される可能性があります。

### 現在利用できるモデルとの比較

| モデル | SWE-bench Verified | 一般公開 |
| --- | --- | --- |
| **Claude Mythos Preview** | 93.9% | ✗ 招待制のみ |
| Claude Opus 4.6 | 80.8% | ✓ |
| GPT-5.4 | 約80% | ✓ |
| Gemini 3.1 Pro | 約80% | ✓ |

現状では、日常のコーディング・開発タスクにはClaude Opus 4.6が引き続き最有力の選択肢です。

---

## まとめ

* **Claude Mythos Preview**はSWE-bench Verified 93.9%、Terminal-Bench 2.0 82%、CyberGym 83.1%を達成したAnthropicの史上最強モデル
* 全主要OS・ブラウザでゼロデイ脆弱性を数千件自律発見する能力から、**一般公開なし**の方針が取られている
* **Project Glasswing**はAmazon・Apple・Microsoft・Google等12社+40以上の組織が参加し、$100Mの使用クレジットを伴う防衛的サイバーセキュリティ連合
* アクセスは招待制で料金は$25/$125（入力/出力）per 100万トークン
* 一般開発者への直接影響は現時点では限定的だが、AI時代のセキュリティパラダイム転換を示す重要なマイルストーン

## 参考リンク
