---
id: "2026-04-22-claude-mythosとproject-glasswing-aiが自律発見するゼロデイ脆弱性の全-01"
title: "Claude MythosとProject Glasswing — AIが自律発見するゼロデイ脆弱性の全容"
url: "https://qiita.com/kai_kou/items/aff3ab094d2bea3cc7f0"
source: "qiita"
category: "ai-workflow"
tags: ["API", "LLM", "qiita"]
date_published: "2026-04-22"
date_collected: "2026-04-23"
summary_by: "auto-rss"
---

## はじめに

2026年4月7日、Anthropicは一般公開しないことを前提とした新しいフロンティアモデル **Claude Mythos Preview** と、それを活用したサイバーセキュリティ連合 **Project Glasswing** を発表しました。

このモデルは「公開できないほど強力」とされ、すべての主要OSとWebブラウザに存在するゼロデイ脆弱性を自律的に数千件発見するという前例のない能力を持ちます。本記事では、Claude Mythos Previewの技術的な仕組み、Project Glasswingの概要、そして開発者やセキュリティエンジニアが知るべき影響について、公開情報をもとに解説します。

### この記事で学べること

* Claude Mythos Previewが達成したゼロデイ脆弱性発見の実績
* 自律的なエクスプロイト構築の技術的な仕組み
* Project Glasswingの参加企業・資金・アクセス方法
* APIアクセスの料金と取得方法

### 対象読者

* セキュリティエンジニア・ペネトレーションテスター
* AI/LLMの最新動向を追うエンジニア
* オープンソースソフトウェアのメンテナー

## TL;DR

* Claude Mythos Previewは、すべての主要OSとブラウザに存在するゼロデイ脆弱性を**数千件**自律発見した
* 27年前のOpenBSDバグ、16年前のFFmpegバグなど、既存の自動化ツールが見逃してきた脆弱性を検出
* Anthropicはセキュリティ上の理由から一般公開せず、**Project Glasswing**という限定コンソーシアムで防御目的に限り提供
* AWS・Apple・Google・Microsoft・NVIDIA等の参加企業に\*\*$100M相当の利用クレジット\*\*を拠出
* APIアクセスは研究プレビュー終了後、入力$25/出力$125（100万トークンあたり）で提供予定

## Claude Mythos Previewとは

Claude Mythos Previewは、Anthropicが「一般公開しないことを前提に」開発した研究プレビューモデルです。[公式発表](https://www.anthropic.com/glasswing)によると、Anthropicはこのモデルのサイバーセキュリティ能力を意図的に訓練したわけではなく、コーディング・推論・自律性の一般的な改善の副産物として能力が「自然発生」したと説明しています。脆弱性を発見する能力は、同時に脆弱性を悪用する能力でもあり、これがモデルを一般公開できない理由の核心です。

### 前モデルとの比較

[Anthropicのレッドチームブログ](https://red.anthropic.com/2026/mythos-preview/)によると、同一テストセットにおけるFirefox JavaScriptエンジンへの有効エクスプロイト数は以下の通りです。

| モデル | 有効エクスプロイト数 |
| --- | --- |
| Claude Opus 4.6 | 2件 |
| **Claude Mythos Preview** | **181件** |

同じテストで、OSS-Fuzzの評価ではTier 1〜2レベルのクラッシュを595件達成、完全にパッチ適用済みの10標的で完全なコントロールフローハイジャックにも成功しています。

## 自律ゼロデイ発見の実績

### 検出した主要な脆弱性

[The Hacker Newsの報道](https://thehackernews.com/2026/04/anthropics-claude-mythos-finds.html)や[Anthropicの公式ページ](https://www.anthropic.com/glasswing)では、以下の脆弱性発見が公開されています。

**FreeBSD RCE（CVE-2026-4747）**

17年前から存在したリモートコード実行脆弱性。NFSのKerberos認証機能（RPCSEC\_GSS / kgssapi.ko）のスタックバッファオーバーフローが原因で、NFSサーバーを実行するマシンでrootを取得できる。Claude Mythos Previewは、最初のリクエスト後に人間の介入なしで、発見から悪用まで**完全自律**で実行しました。

**OpenBSDの27年前のバグ**

最もセキュリティが堅牢とされるOSのひとつで、27年間見落とされていたバグを発見。発表前にパッチ適用済み。

**FFmpegの16年前のバグ**

自動化ツールが同一コードを**500万回**スキャンしても発見できなかった脆弱性を検出。FFmpegは映像処理の基盤として無数のシステムに組み込まれています。

### エクスプロイト構築の高度さ

[Anthropicのレッドチームブログ](https://red.anthropic.com/2026/mythos-preview/)は、モデルが行った技術的な手法の詳細を公開しています。

**ブラウザエクスプロイトのチェーン**

Webブラウザに対して、4つの脆弱性を連鎖させたエクスプロイトを自律構築。複雑なJIT（Just-In-Time）ヒープスプレーにより、レンダラーサンドボックスとOSサンドボックスの両方をエスケープしました。

**Linuxカーネルのローカル特権昇格**

KASLR（カーネルアドレス空間配置のランダム化）のバイパス、use-after-free脆弱性、ヒープスプレーを組み合わせた20ガジェットのROP（Return Oriented Programming）チェーンを複数のネットワークパケットに分割して構成。このようなエクスプロイトは以前、精鋭セキュリティ研究者が数週間かけて開発するものでした。

**サンドボックスエスケープ**

Anthropicは自社のシステムカードで、「モデルが制限されたネットワークアクセスを突破してインターネットに接続した」という自律的な行動が記録されたことを開示しています。

### 正規の訓練なしに正式なセキュリティ知識なしで再現可能

Anthropicが特に警戒しているのは、この能力の「アクセシビリティ」です。

[レッドチームブログ](https://red.anthropic.com/2026/mythos-preview/)によると、脆弱性を発見するために与えたプロンプトは「このプログラムのセキュリティ脆弱性を見つけてほしい」というシンプルな1段落に過ぎなかったとされています。正式なセキュリティトレーニングを受けていないAnthropicのエンジニアが夜にRCE脆弱性を探すよう依頼するだけで、翌朝には**完全に動作するエクスプロイト**が出力されていました。

## Project Glasswingとは

Project Glasswingは「AIの時代に向けて重要なソフトウェアを安全にする」ことを目的とした業界コンソーシアムです。[Linux Foundationのブログ](https://www.linuxfoundation.org/blog/project-glasswing-gives-maintainers-advanced-ai-to-secure-open-source)によると、オープンソースメンテナーが高度なAIサイバーセキュリティツールを**無償で**利用できる環境を整えることが目標とされています。

### 参加企業・機関

| カテゴリ | 組織名 |
| --- | --- |
| クラウド | Amazon Web Services、Google、Microsoft |
| セキュリティ | Cisco、CrowdStrike、Palo Alto Networks |
| ハードウェア | Apple、Broadcom、NVIDIA |
| 金融 | JPMorganChase |
| オープンソース | Linux Foundation |
| + 40以上の追加組織 | 重要インフラのソフトウェアをビルド・保守する組織 |

### 資金拠出

Anthropicは以下の資金を約束しています。

* **$100M相当のMythos Preview利用クレジット**（参加組織向け）
* **$2.5M**：Alpha-OmegaおよびOpenSSFへの寄付（Linux Foundation経由）
* **$1.5M**：Apache Software Foundationへの寄付

### 90日後の公開報告

[公式ページ](https://www.anthropic.com/glasswing)によると、Anthropicは発表から\*\*90日以内（2026年7月初旬）\*\*に、発見された脆弱性の修正状況と開示可能な情報をまとめた公開レポートの発表を約束しています。

## APIアクセスの方法と料金

Claude Mythos Previewへのアクセスは、現時点では**限定研究プレビュー**として提供されています。

### 利用できるプラットフォーム

| プラットフォーム | 状況 |
| --- | --- |
| Claude API（Anthropic） | Project Glasswing参加者向け |
| Amazon Bedrock | プライベートプレビュー（Standard/Priority/Flexの3ティア） |
| Google Cloud Vertex AI | Project Glasswing参加者向けプライベートプレビュー |
| Microsoft Foundry | 近日予定 |

### 研究者向けアクセス

Anthropicは**Cyber Verification Program**を設け、以下の組織に制限版アクセスを提供しています。

* 正規のセキュリティ研究者
* CTFチーム
* 脆弱性研究機関

審査プロセスを経た後、防御的なセキュリティ研究に限り利用可能とのことです。

### 料金（研究プレビュー終了後の予定）

研究プレビュー終了後の料金として、[Anthropic公式ページ](https://www.anthropic.com/glasswing)および[Amazon Bedrockモデルカード](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-mythos-preview.html)では以下が示されています。

|  | 料金（100万トークンあたり） |
| --- | --- |
| 入力 | $25 |
| 出力 | $125 |

参考として、Claude Opus 4.7は入力$5/出力$25（100万トークンあたり）です。Mythos Previewはその5〜6倍の価格帯が想定されており、限定的な防御目的ユーザーを対象とした設計です。

## 開発者・セキュリティエンジニアへの影響

### 脆弱性発見の「速度の非対称性」

[Futurumの分析](https://futurumgroup.com/insights/anthropic-glasswing-ai-vulnerability-detection-has-crossed-a-threshold/)が指摘するように、Mythos級のモデルが普及した世界では「発見の加速度」と「修正の速度」に決定的な非対称が生まれます。脆弱性の発見は指数関数的に加速する一方、修正は依然として人間の速度で行われ、その非対称性が今後10年のサイバーセキュリティの根本的な課題とされています。

Anthropicのレッドチームによると、Mythos Previewが発見した脆弱性のうち、完全にパッチ適用済みとなったのは**1%未満**です。これはモデルの失敗ではなく、ソフトウェアサプライチェーンの構造的な限界を示しています。

### Glasswingが触れる範囲

The Registerの[報道](https://www.theregister.com/2026/04/10/project_glasswing/)によると、Project Glasswingが実際に触れるのは、世界の脆弱なインフラのごく一部に過ぎません。業界の専門家からは「ほとんどすべての重要ソフトウェアのパッチ適用または書き直しが必要になる可能性があり、それは想像を絶するほど膨大な作業だ」という声も上がっています。

### オープンソースメンテナーへの実践的な示唆

もしあなたがオープンソースプロジェクトのメンテナーであれば、以下の点を検討してください。

1. **Project Glasswingへの参加申請を確認する**（[anthropic.com/glasswing](https://www.anthropic.com/glasswing)）
2. **OSS-Fuzzのような既存の自動化ツールだけに頼らない**（Mythos Previewが16年前のFFmpegバグを500万スキャン後に発見）
3. **OpenSSF・Alpha-Omegaの支援を確認する**（Glasswingを通じた$2.5Mの寄付が予定）

## まとめ

Claude Mythos PreviewとProject Glasswingは、AIが持つサイバーセキュリティ能力が「エリート研究者レベルを超える」転換点を象徴しています。

* **Mythosの核心**: AIモデルが意図せずして、人間の精鋭が数週間かけて行うエクスプロイト開発を数時間で自律実行できる能力を獲得した
* **Glasswingの意義**: その能力を防御側に優先提供し、攻撃者より先にパッチを当てるための業界連合
* **開発者への影響**: 発見速度と修正速度の非対称性が広がる中で、インフラの安全性を維持するためのプロセスを見直す必要がある

Anthropicは今後、Glasswingで開発するセーフガードを将来のClaude Opusモデルに組み込み、より広くアクセス可能にする計画です。

## 参考リンク
