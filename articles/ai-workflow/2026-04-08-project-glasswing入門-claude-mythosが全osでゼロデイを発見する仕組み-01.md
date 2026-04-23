---
id: "2026-04-08-project-glasswing入門-claude-mythosが全osでゼロデイを発見する仕組み-01"
title: "Project Glasswing入門 — Claude Mythosが全OSでゼロデイを発見する仕組みと防衛戦略 - Qiita"
url: "https://qiita.com/kai_kou/items/9dd3702f3421b798e84b"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-04-08"
date_collected: "2026-04-09"
summary_by: "auto-rss"
query: ""
---

## はじめに

2026年4月7日、Anthropicは「**Project Glasswing**」を正式発表しました。これは同社の最新かつ未公開フロンティアモデル「**Claude Mythos Preview**」を40社以上のテック企業に限定提供し、重要なソフトウェアインフラの脆弱性を防衛的に発見・修正するための取り組みです。

この記事では、Claude Mythosの技術的な能力、Project Glasswingの仕組み、実際に発見された脆弱性の詳細、そして開発者・セキュリティエンジニアへの影響を解説します。

### この記事で学べること

* Claude Mythos PreviewのCyberGymベンチマーク（83.1%）の意味
* Firefoxエクスプロイトで従来モデルの90倍の能力を示した技術的詳細
* 27年前のOpenBSDバグや16年前のFFmpegバグを発見できた仕組み
* Project Glasswingへの参加企業と今後の展開

### 対象読者

* セキュリティエンジニア・AppSecチーム
* AIモデルの能力評価に関心を持つエンジニア
* オープンソースコードのセキュリティに携わる開発者

---

## TL;DR

* **Claude Mythos Preview**はAnthropicの「最も高度な未公開モデル」で、CyberGymベンチマーク83.1%（Opus 4.6の66.6%を大幅超過）
* FirefoxのJSエンジン脆弱性エクスプロイトで181回の動作確認（Opus 4.6は2回）
* 全ての主要OSとWebブラウザでゼロデイ脆弱性を発見。27年前のOpenBSDバグ、16年前のFFmpegバグも検出
* **Project Glasswing**はAWS・Apple・Cisco・CrowdStrike・Google・Microsoft・NVIDIAなど40社以上が参加するサイバー防衛コンソーシアム
* 一般公開・APIアクセスの予定なし。攻撃への悪用リスクから限定展開

---

## Claude Mythos Previewとは

Claude Mythosは、Anthropicが開発した汎用フロンティアモデルです。コードネーム「Capybara」として以前から存在が知られており、[2026年3月末のデータリーク](https://fortune.com/2026/03/26/anthropic-says-testing-mythos-powerful-new-ai-model-after-data-leak-reveals-its-existence-step-change-in-capabilities/)によって存在が明らかになっていました。

Anthropicは4月7日、このモデルの「Preview」版を正式に発表。公式ブログで「**現在構築した中で最も高性能なモデル**」と位置付け、同時にその能力が「前例のないサイバーセキュリティリスク」をもたらす可能性があると警告しました。

> "Claude Mythos Previewはサイバー能力において現在のあらゆるAIモデルを大きく上回っており、それはこれから来る波のモデルを予兆している。防衛者の取り組みをはるかに上回るペースで脆弱性を悪用できるモデルだ。"  
> — Anthropic公式ブログ（[Project Glasswing](https://www.anthropic.com/glasswing)）

---

## CyberGymベンチマークが示す能力の跳躍

CyberGymは、AIエージェントを脆弱性解析タスクで評価するベンチマークです。

| モデル | CyberGymスコア |
| --- | --- |
| Claude Mythos Preview | **83.1%** |
| Claude Opus 4.6 | 66.6% |
| 差 | +16.5pt |

数字だけ見れば16.5ポイントの差ですが、実際の能力差は数値以上に大きく現れています。特にエクスプロイト生成の実験では、その差は歴然としています。

---

## 実際に発見・悪用した脆弱性

### FirefoxのJSエンジンエクスプロイト実験

Anthropicは、Mozilla Firefox 147のJavaScriptエンジンに存在する脆弱性（全てFirefox 148でパッチ済み）を使ったエクスプロイト生成実験を実施しました。

| モデル | 動作するJSシェルエクスプロイト生成数 | レジスタ制御達成数 |
| --- | --- | --- |
| Claude Opus 4.6 | **2回** | — |
| Claude Mythos Preview | **181回** | 29回 |

**90倍以上の差**です。さらにMythos Previewは、次のような高度なエクスプロイトを自律的に生成しました:

* **4つの脆弱性チェーン**: 単一の脆弱性ではなく4つを組み合わせた複合エクスプロイト
* **複雑なJITヒープスプレー**: JITコンパイラを悪用したメモリ攻撃手法
* **ダブルサンドボックス脱出**: レンダラーサンドボックスとOSサンドボックスの両方から脱出

従来の自動化ツールとは次元が異なる能力です。

### 27年前のOpenBSDバグ

OpenBSDはセキュリティを最重視するオープンソースOSとして知られています。Mythos Previewはこのシステムに存在していた**27年前から存在した脆弱性**を発見し、現在はパッチ適用済みです。

### 16年前のFFmpegバグ

FFmpegは動画・音声処理の事実上の標準ライブラリです。Mythos Previewは**16年間見逃されてきた脆弱性**を発見しました。特筆すべきは、この脆弱性は自動テストツールが**500万回**該当コードをスキャンしても見つけられなかったものです。

### Linuxでの権限昇格（LPE）

Anthropicによると、Mythos PreviewはLinuxおよびその他のOSにおいて:

* **微妙なレースコンディション**を悪用したローカル権限昇格（LPE）エクスプロイトを自律的に取得
* **KASLRバイパス**（カーネルのアドレス空間ランダム化を無効化する技術）を活用

これらは高度な人間のペンテスターが手動で行うような攻撃手法です。

---

## Project Glasswingの仕組み

### 概要

Project Glasswingは、Claude Mythos Previewへの限定アクセスを通じて、重要なソフトウェアインフラのセキュリティを強化するためのコンソーシアム型イニシアチブです。

参加企業は発見した脆弱性情報を業界全体で共有することが求められます。

### 参加企業（主要）

以下の企業が参加していることが公式に確認されています:

| カテゴリ | 企業名 |
| --- | --- |
| クラウド | Amazon Web Services, Google, Microsoft |
| セキュリティ | Cisco, CrowdStrike, Palo Alto Networks |
| ハードウェア | Apple, Broadcom, NVIDIA |
| 金融 | JPMorganChase |
| 標準化団体 | Linux Foundation |

加えて、重要なソフトウェアインフラを構築・維持する**約40社**が追加アクセスを提供されています。

### アクセス方法と制約

* 防衛的なセキュリティ作業に限定した使用
* 発見した脆弱性・知見の業界共有が必須
* Anthropicの[Frontier Red Teamブログ](https://red.anthropic.com/2026/mythos-preview/)でパッチ済み脆弱性の技術詳細を公開
* 一般ユーザー・一般開発者へのAPIアクセスは**提供しない**

---

## なぜ公開しないのか

### 両刃の剣

Anthropicはブログで、Mythosが持つ能力が防衛だけでなく攻撃にも使えることを明確に認識していると述べています。

> "こうした能力を安全に展開することにコミットしているアクター以外にも拡散するのは時間の問題だ。"

AIの進歩速度を考えると、同等の能力を持つモデルが他社から登場するのは避けられません。Anthropicはその「前に」防衛インフラを整えることに賭けています。

### Alignment Risk Updateの公開

Anthropicは[Alignment Risk Update](https://www.anthropic.com/claude-mythos-preview-risk-report)を公開し、Claude Mythos Previewのリスク評価を透明化しています。これはAnthropicがMythos-classモデルをどのように将来的にスケール展開するかの学習機会にもなっています。

---

## 開発者・セキュリティエンジニアへの示唆

### オープンソースメンテナーへ

Project Glasswingは、オープンソースコードを維持している開発者にとっても機会です。Anthropicは約40社の「重要なソフトウェアインフラを維持する組織」にアクセスを提供しており、大型OSSプロジェクトのメンテナーが参加できる可能性があります。

### セキュリティエンジニアへ

CyberGymベンチマーク83.1%という数字は、AIがCTFやペンテストの一部のタスクで上位の人間スペシャリストに匹敵することを示しています。以下の領域では、AIアシストセキュリティ監査の活用が現実的な選択肢になってきています:

* 静的コード解析を超えたセマンティック脆弱性発見
* 古いコードベースの負債スキャン
* OSSライブラリの依存チェーン調査

### 「APIがない」今できること

Claude Mythos PreviewのAPIは一般公開されていません。ただし:

* 現在の`claude-opus-4-6`も[CyberGymで66.6%](https://venturebeat.com/technology/anthropic-says-its-most-powerful-ai-cyber-model-is-too-dangerous-to-release)と相当な能力を持つ
* APIが将来公開される際は、モデルパラメータの変更のみで切り替え可能
* 現在でもClaude APIを使ったセキュリティ自動化（コードレビュー、依存脆弱性チェック等）は実用的

```
import anthropic

client = anthropic.Anthropic()

# 現在利用可能な最高性能モデルでセキュリティ解析
response = client.messages.create(
    model="claude-opus-4-6",  # Mythos公開後は切り替えのみ
    max_tokens=4096,
    messages=[
        {
            "role": "user",
            "content": """以下のコードにセキュリティ上の問題がないか解析してください。
            
特に以下の観点で確認してください:
- バッファオーバーフローの可能性
- レースコンディション
- 境界値チェック漏れ
- 権限昇格につながる設計の問題

```c
// 解析対象のコード
void process_input(char *buf, size_t len) {
    char local[256];
    memcpy(local, buf, len);  // ← 境界チェックなし
    // ...
}
```"""
        }
    ]
)

print(response.content[0].text)
```

---

## 今後の展望

Anthropicは「Mythosクラスのモデルをスケール展開する方法を学ぶ」ことをProject Glasswingの目的の一つとして位置付けています。これは将来的な一般公開に向けた準備段階と解釈できます。

* **短期（2026年）**: Project Glasswingメンバーのみアクセス
* **中期**: 脆弱性発見能力の実績積み上げ、リスク評価の継続
* **長期**: Mythosクラスモデルの段階的スケール展開の検討

---

## まとめ

* **Claude Mythos Preview**はCyberGym 83.1%・Firefox exploit 181回と、セキュリティ能力で従来モデルを大幅に超える
* **Project Glasswing**はAWS・Apple・Google・Microsoftなど40社以上が参加するサイバー防衛コンソーシアム
* 27年前のOpenBSD、16年前のFFmpegバグを発見するなど、ゼロデイ発見能力が実証された
* **一般APIアクセスなし**。攻撃への悪用リスクから限定展開で防衛能力の構築を優先
* AIサイバーセキュリティは「実証段階」から「実用段階」に移行しつつある

## 参考リンク
