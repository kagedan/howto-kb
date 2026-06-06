---
id: "2026-06-05-claude-mythos-preview入門-project-glasswingとaiゼロデイ発見-01"
title: "Claude Mythos Preview入門 — Project GlasswingとAIゼロデイ発見の全貌"
url: "https://qiita.com/kai_kou/items/4e148a06b540c4266108"
source: "qiita"
category: "ai-workflow"
tags: ["API", "Python", "JavaScript", "qiita"]
date_published: "2026-06-05"
date_collected: "2026-06-06"
summary_by: "auto-rss"
query: ""
---

![Claude Mythos PreviewとProject Glasswingのコンセプト図](https://raw.githubusercontent.com/kai-kou/zenn-blog-automation/main/images/claude-mythos-project-glasswing-security-guide/01-hero.png)

## はじめに

2026年4月7日、Anthropicは異例の発表を行いました。新しいフロンティアモデル「**Claude Mythos Preview**」が、全主要OS・全主要ブラウザでゼロデイ脆弱性を大量発見できるレベルに到達したというものです。

同時に発表された「**Project Glasswing**」は、このモデルを防衛目的に限定活用するための産学官連携イニシアチブ。AWS、Apple、Google、Microsoft、NVIDIAなど12の主要組織が参加し、$100M（約1億ドル）のモデル利用クレジットが拠出されています。

Mythos Previewは一般公開されていません。しかしこの発表は、AIのセキュリティ能力が臨界点を超えたことを示すマイルストーンです。

### この記事で解説すること

- Claude Mythos Previewの技術仕様とベンチマーク
- Project Glasswingの仕組みと参加組織
- 実際に発見されたゼロデイ脆弱性の事例（CVE付き）
- API仕様・料金・アクセス方法
- セキュリティエンジニアへの実践的な影響

### 対象読者

- セキュリティエンジニア・ペネトレーションテスター
- DevSecOpsエンジニア
- AIの能力限界に関心を持つソフトウェアエンジニア

## TL;DR

- Claude Mythos PreviewはSWE-bench Verified 93.9%、CyberGym 83.1%を達成したAnthropicの非公開フロンティアモデル
- FirefoxのJSエンジン脆弱性攻撃で181回成功（Opus 4.6は2回）という圧倒的なサイバー能力
- Project Glasswingは12組織+40以上の組織が参加し、$100Mのクレジットで重要インフラを守る
- 一般公開なし。アクセスはProject Glasswing参加組織のみ（料金: $25/$125 per MTok）
- CVE-2026-4747（FreeBSD 17年前の脆弱性）等、数千件のゼロデイを発見済み

## Claude Mythos Previewとは

### 概要

[Claude Mythos Preview](https://red.anthropic.com/2026/mythos-preview/)は、2026年4月7日にAnthropicが発表した汎用フロンティアモデルです。

> We are announcing Claude Mythos Preview, a new general-purpose language model that performs strongly across the board, but is strikingly capable at computer security tasks.
> — [Anthropic, red.anthropic.com（2026-04-07）](https://red.anthropic.com/2026/mythos-preview/)

従来モデルとの最大の違いは、サイバーセキュリティ能力の飛躍的な向上です。単に脆弱性を「検出」するだけでなく、エクスプロイトを「自律的に開発・実行」する能力を備えています。

### Opus 4.6との性能比較

[Project Glasswingのページ](https://www.anthropic.com/glasswing)に公開されているベンチマーク結果は以下の通りです。

| ベンチマーク | Claude Mythos Preview | Claude Opus 4.6 |
|---|---|---|
| CyberGym（脆弱性再現） | **83.1%** | 66.6% |
| SWE-bench Verified | **93.9%** | 80.8% |
| SWE-bench Pro | **77.8%** | 53.4% |
| Terminal-Bench 2.0 | **82.0%** | 65.4% |
| GPQA Diamond | **94.6%** | 91.3% |

CyberGymのスコアが+16.5ポイント向上している点が特筆されます。一般的なコーディング・推論においても全項目でOpus 4.6を上回っています。

![Mythos PreviewとOpus 4.6のベンチマーク比較](https://raw.githubusercontent.com/kai-kou/zenn-blog-automation/main/images/claude-mythos-project-glasswing-security-guide/02-benchmark.png)

### サイバー能力の実態

Anthropicが公開したテスト結果は衝撃的な数値を示しています。

**FirefoxのJavaScriptエンジン攻撃:**
数百回の試行に対して、Opus 4.6は2回のエクスプロイト成功にとどまったのに対し、Mythos Previewは**181回**の成功を記録しました。

**OSS-Fuzz（OSSファジングテスト）:**

| 指標 | Mythos Preview | Opus 4.6 |
|---|---|---|
| Tier 1-2クラッシュ | **595件** | — |
| Tier 5（フルコントロールフロー乗っ取り） | **10件** | — |
| Tier 3クラッシュ | — | 1件 |

また、以下のような高度な攻撃手法を自律的に実行できることが確認されています。

- Linux・その他OSでのローカル権限昇格（競合状態・KASLRバイパスを悪用）
- 4つ以上の脆弱性をチェーンした複合エクスプロイト構築
- レンダラーサンドボックスおよびOSサンドボックスを突破するJITヒープスプレー
- ROPチェーンと遠隔コード実行エクスプロイトの自律生成

## Project Glasswingの仕組み

### 設立の背景

Anthropicは「Mythos PreviewをそのままAPIで公開するわけにはいかない」と判断しました。この能力を悪用すれば、世界中の重要インフラが壊滅的なリスクにさらされます。

そこで立ち上げられたのが[Project Glasswing](https://www.anthropic.com/glasswing)です。防衛側が先に脆弱性を発見・修正するために、AIの能力を限定的に活用するための枠組みです。

> The window between a vulnerability being discovered and being exploited by an adversary has collapsed—what once took months now happens in minutes with AI.
> — CrowdStrike CTO Elia Zaitsev（[Project Glasswingページ](https://www.anthropic.com/glasswing)より引用）

![Project Glasswingのアーキテクチャ図](https://raw.githubusercontent.com/kai-kou/zenn-blog-automation/main/images/claude-mythos-project-glasswing-security-guide/03-architecture.png)

### 参加組織

**12の創設パートナー:**

| セクター | 組織 |
|---|---|
| クラウド | Amazon Web Services、Google、Microsoft |
| ハードウェア | Apple、Broadcom、NVIDIA |
| セキュリティ | Cisco、CrowdStrike、Palo Alto Networks |
| 金融 | JPMorganChase |
| OSS | Linux Foundation |
| AI | Anthropic |

創設パートナー12組織に加え、重要ソフトウェアインフラを構築・維持する**40以上の組織**が拡張アクセスを受けています。

### 財務コミットメント

| 内訳 | 金額 |
|---|---|
| Glasswing参加組織向けモデル利用クレジット | **$100M** |
| Alpha-Omega・OpenSSF（Linux Foundation経由） | $2.5M |
| Apache Software Foundation | $1.5M |

### 脆弱性開示プロセス

Project Glasswingでは、責任ある開示（Coordinated Vulnerability Disclosure）を厳格に適用しています。

1. Mythos Previewが脆弱性を発見
2. SHA-3ハッシュで発見内容をコミット（時刻証明）
3. ソフトウェアメンテナーへの通知（90日 + 45日の延長オプション）
4. パッチ適用後に詳細を公開

現時点で発見済み脆弱性の**99%以上**がまだ未修正であるため、具体的な内容は開示されていません。

## 実際に発見されたゼロデイ事例

Anthropicが公開している修正済み脆弱性から、Mythos Previewの能力が読み取れます。

### CVE-2026-4747: FreeBSD NFS リモートコード実行

- **深刻度:** Critical
- **発見:** Mythos Previewが完全自律的に特定・エクスプロイト
- **概要:** NFSを実行中のFreeBSDマシンに対し、インターネット上の未認証ユーザーがリモートからサーバーの完全制御を取得できる
- **年齢:** 約17年前に混入したバグ
- **手法:** フルカーネルROPチェーンによるリモートコード実行

### OpenBSD SACK bug: TCP/IP実装の整数オーバーフロー

- **概要:** 符号付き整数オーバーフローによるリモートサービス拒否
- **年齢:** **27年前**から存在していた実装上の欠陥
- **意義:** 最も広くレビューされているOSSの一つでも長年見落とされてきた

### FFmpeg H.264: 16年前の脆弱性

- **概要:** H.264スライストラッキングの処理に関する脆弱性
- **詳細:** 2003年に混入、2010年に悪用可能な形に変化
- **意義:** 動画処理ライブラリとして数十億デバイスで使用されているFFmpegでの発見

これらの事例は、人間のセキュリティ研究者が何年もかけて見つけられなかった脆弱性を、AIが自律的に特定できることを示しています。

## API仕様とアクセス方法

### 料金

| 項目 | 料金 |
|---|---|
| 入力トークン | **$25 / 1Mトークン** |
| 出力トークン | **$125 / 1Mトークン** |

Opus 4.6（$5/$25）の5倍の料金設定です。ただし実際のコスト感としては、公開情報によると脆弱性発見1回あたり$50〜$2,000程度、FFmpegの解析では数百回の実行で「約$10,000」とされています。

### アクセス方法

Mythos Previewは現在**一般公開されていません**。アクセスできる経路は以下のみです。

1. **Project Glasswing参加組織**（12創設 + 40以上の拡張メンバー）
2. **Claude for Open Source Program**（OSS重要インフラメンテナー向け）

一般エンジニアがアクセスするには、所属組織がProject Glasswingメンバーであるか、重要OSSのメンテナーとして申請を通過する必要があります。

### 利用可能なAPI経路

Project Glasswing参加者は以下のプラットフォーム経由で利用できます。

```python
import anthropic

client = anthropic.Anthropic()

# 実際のモデルIDはProject Glasswing参加組織に個別提供される
# 以下は利用イメージのサンプルコード
message = client.messages.create(
    model="claude-mythos-preview",  # 実際のIDはGlasswing参加後に確認
    max_tokens=8192,
    messages=[
        {
            "role": "user",
            "content": "以下のコードに脆弱性がないか解析してください:\n..."
        }
    ]
)
print(message.content)
```

- Claude API（直接）
- Amazon Bedrock
- Google Cloud Vertex AI
- Microsoft Foundry

## セキュリティエンジニアへの影響

### 脆弱性発見コストの激変

従来、重要なゼロデイ脆弱性の発見には熟練したセキュリティ研究者が数週間〜数カ月を要していました。Mythos Previewの登場で、このコスト構造が根本的に変わります。

| 作業 | 従来 | Mythos Preview |
|---|---|---|
| OpenBSD調査1,000回 | 不可能 | 約$20,000以下 |
| FFmpeg解析数百回 | 数カ月 | 約$10,000 |
| 個別エクスプロイト | 数週間 | $50〜$2,000 |

### 「99%未修正」が意味するもの

現在発見済み脆弱性の99%以上が未修正という状況は、脆弱性修正のエコシステム全体に課題を突きつけています。

- OSS maintainerのパッチ対応ペースが追いつかない可能性
- 自動パッチ生成・適用ツールへの需要増加
- セキュリティ研究者の役割変化（発見者→トリアージャー・修正者へのシフト）

### 防御側への実践的アクション

Anthropicとパートナーは90日以内に知見を共有する予定です。一般のエンジニアができることは以下です。

1. **依存関係の更新を徹底する**: Mythos Preview発見の脆弱性が順次公開されるため、定期的なアップデートが重要
2. **CVE追跡ツールの活用**: 今後発表される修正パッチを見逃さないため、自動アラート設定
3. **コードレビューにAIを活用**: Claude Security（Opus 4.7ベース）等で既存コードの事前チェック
4. **OSS貢献**: Linux Foundation、Apache等への支援がセキュリティエコシステム全体を強化

## 次のステップ: Mythos後継モデルのセーフガード

Anthropicは次期Claude Opusモデルに「**危険な出力を検知・ブロックするセーフガード**」を搭載する予定です。

このセーフガードによる影響を受ける正規のセキュリティ専門家向けに、「**Cyber Verification Program**」の申請受付も予定されています。

> Our eventual goal is to enable safe deployment of Mythos-class models at scale.
> — [Project Glasswing, Anthropic（2026-04-07）](https://www.anthropic.com/glasswing)

## まとめ

Claude Mythos PreviewとProject Glasswingは、AIのサイバーセキュリティ能力が人間の最上位研究者を超えたことを公式に示す、業界史上最も重要な発表の一つです。

- **Mythos Previewの実力**: CyberGym 83.1%、Firefox 181回エクスプロイト成功、数千件のゼロデイ発見
- **Project Glasswingの意義**: 防衛側が先手を打つための$100Mコミット、12大手+40以上の組織連合
- **一般アクセス**: 現時点では不可。参加組織か重要OSSメンテナーのみ
- **今後の動向**: 90日以内の知見共有、次期OpusモデルへのCyberセーフガード搭載

AIが脆弱性を自律発見できる時代において、防衛側も同等のAIツールを持つことがサイバーセキュリティの新しい基準となりつつあります。

## 参考リンク

- [Claude Mythos Preview — Frontier Red Team Blog](https://red.anthropic.com/2026/mythos-preview/) — 技術詳細・CVE事例
- [Project Glasswing: Securing critical software for the AI era](https://www.anthropic.com/glasswing) — イニシアチブ詳細・参加組織
- [Anthropic's Mythos forces a rethink of vulnerability management](https://www.informationweek.com/cybersecurity/anthropic-s-mythos-forces-a-rethink-of-vulnerability-management) — 業界分析
- [On Anthropic's Mythos Preview and Project Glasswing](https://www.schneier.com/blog/archives/2026/04/on-anthropics-mythos-preview-and-project-glasswing.html) — Bruce Schneier分析
