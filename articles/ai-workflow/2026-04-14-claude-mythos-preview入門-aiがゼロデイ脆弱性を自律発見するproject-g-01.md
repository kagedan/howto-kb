---
id: "2026-04-14-claude-mythos-preview入門-aiがゼロデイ脆弱性を自律発見するproject-g-01"
title: "Claude Mythos Preview入門 — AIがゼロデイ脆弱性を自律発見するProject Glasswingの仕組み"
url: "https://qiita.com/kai_kou/items/1b7e28ce3631ec2d50a7"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-04-14"
date_collected: "2026-04-15"
summary_by: "auto-rss"
---

## はじめに

2026年4月7日、Anthropicは「Claude Mythos Preview」という新しいAIモデルを発表しました。これは同社史上最も強力なモデルですが、**一般公開されていません**。

理由は単純かつ衝撃的です。このモデルは主要なOSやブラウザに存在した「数千件」のゼロデイ脆弱性を数週間で自律的に発見・悪用できるほどの能力を持っており、攻撃的な用途に悪用されるリスクが高すぎると判断されたためです。

代わりにAnthropicは「**Project Glasswing**」を立ち上げました。AWS、Apple、Microsoft、Googleなど12社が参加する防衛的コンソーシアムで、Mythos Previewを攻撃者より先に脆弱性を発見するために活用します。

### この記事で学べること

* Claude Mythos Previewのベンチマーク性能（Opus 4.6との比較）
* 実際に発見したゼロデイ脆弱性の詳細（CVE-2026-4747 など）
* Project Glasswingの参加企業・資金規模・オープンソースへの影響
* エンジニアが今できること

### 対象読者

* AIの最新動向を追っているエンジニア
* セキュリティエンジニア・CISOおよびそのチーム
* オープンソースのメンテナーでProject Glasswingへの参加を検討している方

---

## TL;DR

* Claude Mythos PreviewはOpus 4.6比でコーディング・セキュリティ能力が大幅向上（SWE-bench 93.9% vs 80.8%）
* 主要OSとブラウザに存在した「数千件」のゼロデイ脆弱性を数週間で自律発見・悪用コードも自動生成
* 攻撃能力が強すぎて一般公開せず → Project Glasswingで防衛的用途に限定提供
* 12創設パートナー（AWS、Apple、Microsoft、Googleほか）、$100Mのusageクレジット + $4Mの助成金

---

## Claude Mythos Previewとは

### モデルの位置づけ

Claude Mythos PreviewはAnthropicが2026年4月7日に発表した汎用フロンティアモデルです。[公式アナウンス](https://red.anthropic.com/2026/mythos-preview/)によると、Claude Opus 4.6と比較して「step change（段階的な飛躍）」と表現されるほどの性能向上を遂げています。

特筆すべきは、Anthropicがこのモデルを**一般APIとして提供しない**と明言している点です。代わりに、Project Glasswingのコンソーシアム参加企業向けに限定アクセスを提供しています。

### ベンチマーク比較

[llm-stats.com の検証](https://llm-stats.com/blog/research/claude-mythos-preview-launch)によると、Mythos PreviewはOpus 4.6を全ベンチマークで大幅に上回ります。

| ベンチマーク | Mythos Preview | Claude Opus 4.6 | 差分 |
| --- | --- | --- | --- |
| SWE-bench Verified | **93.9%** | 80.8% | +13.1pt |
| SWE-Bench Pro | **77.8%** | 53.4% | +24.4pt |
| Terminal-Bench 2.0 | **82.0%** | 65.4% | +16.6pt |
| CyberGym | **83.1%** | 66.6% | +16.5pt |
| Humanity's Last Exam (with tools) | **64.7%** | 53.1% | +11.6pt |
| エージェンティックタスク（平均） | **82.4** | 72.6 | +9.8pt |

コーディングカテゴリでは平均83.8対64.4と最も大きな差が開いています。

---

## 発見したゼロデイ脆弱性の詳細

Anthropicは過去数週間でMythos Previewを使い、主要なOSとブラウザに存在する「数千件」のゼロデイ脆弱性を発見したと報告しています（[Help Net Security, 2026-04-08](https://www.helpnetsecurity.com/2026/04/08/anthropic-claude-mythos-preview-identify-vulnerabilities/)）。以下は代表的な事例です。

### CVE-2026-4747: FreeBSD 17年間の脆弱性

[Anthropicの公式技術報告](https://red.anthropic.com/2026/mythos-preview/)によると、Mythos Previewが自律的に発見した最も注目される脆弱性のひとつがこのFreeBSDのものです。

**脆弱性の概要：**

* **対象**: FreeBSDのRPCSEC\_GSS認証ハンドラー
* **種別**: スタックバッファオーバーフロー
* **内容**: 攻撃者が制御するパケットが128バイトのスタックバッファにコピーされるが、長さチェックが最大400バイトまで許可している
* **影響**: インターネット上の未認証ユーザーが対象サーバーのroot権限を取得可能
* **存在期間**: **17年間**、セキュリティレビューをくぐり抜けてきた

Mythos Previewはこの脆弱性を発見しただけでなく、動作するエクスプロイトコードまで自律的に構築しました。

### OpenBSD 27年間のDoS脆弱性

さらに古い事例として、OpenBSDで27年間存在したDoS（サービス妨害）脆弱性の発見があります。

* **発見コスト**: スキャッフォールド実行約1,000回、**総コスト$20,000未満**
* **意義**: 国家レベルの研究チームが数ヶ月かけて行う作業を数時間・低コストで実現

### FFmpeg 16年間の脆弱性

FFmpegに存在した16年間のバグは、自動テストツールが問題のコード行を**500万回**実行しても検出できなかったにもかかわらず、Mythos Previewが発見しています（[SC Media の報告](https://www.scworld.com/news/anthropic-claude-mythos-preview-finds-thousands-of-vulnerabilities-in-weeks)）。

### Firefox 147 JavaScriptエンジンの悪用

[VentureBeat の分析](https://venturebeat.com/security/mythos-detection-ceiling-security-teams-new-playbook)によると、Firefox 147のJavaScriptエンジンに存在した脆弱性（Firefox 148でパッチ済み）に対する悪用成功率には衝撃的な差がありました。

| モデル | 悪用成功回数（数百回の試行中） |
| --- | --- |
| Claude Opus 4.6 | **2回** |
| Claude Mythos Preview | **181回** |

この約90倍の差が、なぜAnthropicがMythos Previewを一般公開しない判断をしたかを端的に示しています。

---

## なぜ一般公開しないのか

### デュアルユース問題

Anthropicは公式ブログで、Mythos Previewを一般公開しない理由を明確にしています：

> 「AIモデルが最も熟練した人間のセキュリティ研究者を超えるレベルで、ソフトウェアの脆弱性を発見・悪用できる段階に達した」

$20,000未満のコストで国家レベルの研究数ヶ月分の発見ができるということは、攻撃者にとっても同じ恩恵を意味します。このため、責任あるAI開発の観点から一般公開のリスクが恩恵を上回ると判断されました。

---

## Project Glasswingとは

### 発表と目的

[公式サイト](https://www.anthropic.com/glasswing)によると、Project Glasswingは2026年4月8日に発表された防衛的なサイバーセキュリティイニシアチブです。

**目的**: Mythos Previewを使って「攻撃者より先に世界の重要ソフトウェアの脆弱性を発見・修正する」

### 12の創設パートナー

| カテゴリ | 参加企業 |
| --- | --- |
| クラウド | Amazon Web Services（AWS）、Google、Microsoft |
| セキュリティ | CrowdStrike、Palo Alto Networks |
| インフラ | Apple、Broadcom、Cisco、NVIDIA |
| 金融 | JPMorganChase |
| オープンソース | Linux Foundation |
| AI | Anthropic |

これらに加え、重要ソフトウェアを構築・メンテナンスする**40以上の追加組織**がアクセスを得ています。

### 財務コミットメント

| 項目 | 金額 |
| --- | --- |
| Mythos Previewのusageクレジット | **$100,000,000** |
| Alpha-Omega + OpenSSF（Linux Foundation経由） | $2,500,000 |
| The Apache Software Foundation | $1,500,000 |
| **オープンソース助成金 合計** | **$4,000,000** |

### 参加企業向けの料金

Anthropicの[公式発表](https://red.anthropic.com/2026/mythos-preview/)によると、Research Preview期間終了後、Glasswing参加企業向けの料金は以下の通りです：

* **入力**: $25 / 1Mトークン
* **出力**: $125 / 1Mトークン

参考として、Claude Opus 4.6は入力$15 / 1Mトークン、出力$75 / 1Mトークンです。Mythos Previewはその約1.7倍の単価となっています。

### オープンソースメンテナーへのアクセス

[Linux Foundation のブログ](https://www.linuxfoundation.org/blog/project-glasswing-gives-maintainers-advanced-ai-to-secure-open-source)によると、オープンソースのメンテナーは「**Claude for Open Source**」プログラムを通じてProject Glasswingへの参加を申請できます。これにより、自分のオープンソースプロジェクトの脆弱性スキャンにMythos Previewを活用することが可能になります。

---

## エンジニアへの影響と今できること

### 防衛側が恩恵を受けるシナリオ

**セキュリティチーム:**

* CrowdStrike、Palo Alto NetworksといったGlasswingパートナー企業のセキュリティ製品にMythos Preview的な脆弱性スキャン機能が組み込まれていく可能性があります
* エンタープライズ契約を持つ組織はパートナー経由でのアクセスが検討できます

**オープンソースメンテナー:**

* Claude for Open Sourceプログラムを通じてMythos Previewへのアクセスを申請できます
* 自分のプロジェクトの脆弱性を事前に発見・修正するチャンスです

**一般開発者:**

* 現時点でMythos Previewには直接アクセスできません
* ただし、Claude Opus 4.6でも[CyberGymスコア66.6%](https://llm-stats.com/blog/research/claude-mythos-preview-launch)という高いセキュリティ能力があるため、コードレビューやセキュリティ検証への活用は今すぐ可能です

### 注意点

* 脆弱性の悪用コードはProject Glasswing参加企業の管理下でのみ使用される予定です
* オープンソースプログラムへの参加申請が一般開発者の現実的な選択肢です

---

## まとめ

Claude Mythos Previewは、AIがサイバーセキュリティ領域で人間の能力を大きく超えた「転換点」を示す存在です。

主なポイントをまとめます：

* **能力の飛躍**: SWE-bench Verified 93.9%、CyberGym 83.1%など、Opus 4.6を全ベンチマークで大幅超過
* **実績**: FreeBSD 17年・OpenBSD 27年・FFmpeg 16年の脆弱性を数週間で発見
* **判断**: 攻撃的能力が強すぎるため一般公開せず → Project Glasswingで防衛的用途に特化
* **規模**: 12創設パートナー企業、$100M usageクレジット、$4M助成金

Project Glasswingは「攻撃側より防衛側に先にAIを届ける」という挑戦です。オープンソースメンテナーの方は、ぜひ「Claude for Open Source」プログラムへの申請を検討してみてください。

## 参考リンク
