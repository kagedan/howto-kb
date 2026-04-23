---
id: "2026-03-28-claude-mythoscapybara解説-anthropicが公開しない最強aiの全貌-01"
title: "Claude Mythos（Capybara）解説 — Anthropicが公開しない最強AIの全貌"
url: "https://qiita.com/kai_kou/items/778e1cee2a872e4a75c9"
source: "qiita"
category: "ai-workflow"
tags: ["LLM", "qiita"]
date_published: "2026-03-28"
date_collected: "2026-03-29"
summary_by: "auto-rss"
---

## はじめに

2026年3月26〜27日、AI業界に衝撃が走りました。AnthropicのCMS（コンテンツ管理システム）の設定ミスにより、約3,000件の内部ドキュメントが一時的に公開状態になるという情報漏洩事件が発生。その中に、同社がひそかに開発中の未発表モデルの存在を示す草稿ブログ記事が2バージョン含まれており、「**Capybara**」（新Tier名）と「**Claude Mythos**」（そのTier内のモデル名）という2つの名称が明らかになりました。

### この記事で整理すること

* Claude Mythosとはどのようなモデルか
* 何がリークされ、何が判明したのか
* なぜAnthropicは公開しないのか
* エンジニアが知っておくべき示唆

### 対象読者

* Anthropic / Claudeの最新動向を追うエンジニア
* LLMのサイバーセキュリティリスクに関心のある方
* AI安全性・リリース戦略に興味のある方

---

## TL;DR

* Anthropicが内部ドキュメントを誤公開、未発表モデル「Claude Mythos（Capybara）」が明らかに
* Opus 4.6を凌駕する新階層モデル — コーディング・学術推論・**サイバーセキュリティの3軸で劇的に高いスコア**
* "currently far ahead of any other AI model in cyber capabilities" という自己評価
* 安全上の懸念から**一般公開の予定なし**、サイバー防衛専門組織への限定アクセスのみ
* 株式市場ではサイバーセキュリティ株が急落、Anthropicの対応声明は慎重なトーン

---

## リーク事件の経緯

### CMSの設定ミスという「最も皮肉な」情報漏洩

AI安全性を掲げるAnthropicが、内部ドキュメント管理システムの設定ミスによって自社の機密情報を漏洩させる――その皮肉な構図が多くのメディアに指摘されています。

[Futurism報道](https://futurism.com/artificial-intelligence/anthropic-step-change-new-model-claude-mythos)によると、Anthropicのウェブサイトに接続されたCMSが誤って設定され、アップロードされたファイルが検索可能な状態になっていたとのこと。この状態は一定期間継続し、約3,000件の内部ドキュメントが誰でもアクセスできる状態に置かれていました。

発見したのは以下の2名の研究者です：

* **Roy Paz**（LayerX Security、シニアAIセキュリティ研究者）
* **Alexandre Pauwels**（University of Cambridge、サイバーセキュリティ研究者）

2名が独立して発見したことが、この漏洩の規模と期間を示唆しています。

### 発覚後のAnthropicの対応

Anthropicはモデルの存在を認め、以下の公式声明を発表しました：

> "We're developing a general purpose model with meaningful advances in reasoning, coding, and cybersecurity. Given the strength of its capabilities, we're being deliberate about how we release it."  
> — [Anthropic公式声明](https://fortune.com/2026/03/26/anthropic-says-testing-mythos-powerful-new-ai-model-after-data-leak-reveals-its-existence-step-change-in-capabilities/)（2026-03-27）

さらに続けて「We consider this model a step change and the most capable we've built to date.（このモデルは段階的な変化であり、これまでに構築した中で最も高性能なものと考えています）」とも述べています。

「能力の強さゆえに、リリースを慎重に進めている」という姿勢は、単なる開発中モデルの説明を超えた、意図的な抑制を示唆するものです。

---

## Claude Mythosとは何か

### モデルのポジショニング

リークされた草稿ドキュメントは2バージョン存在し、v1が「Mythos」、v2が「Capybara」という名称を使用していました。研究者らの分析によると、**Capybara は新しいTier（階層）の名称**、**Mythos はそのTier内のモデル名**と見られています。

漏洩したv2草稿には以下の記述があります：

> "'Capybara' is a new name for a new tier of model: larger and more intelligent than our Opus models—which were, until now, our most powerful."  
> — リーク内部ドキュメント（草稿v2）

[The Decoder](https://the-decoder.com/anthropic-leak-reveals-new-model-claude-mythos-with-dramatically-higher-scores-on-tests-than-any-previous-model/)や[Fortune](https://fortune.com/2026/03/26/anthropic-says-testing-mythos-powerful-new-ai-model-after-data-leak-reveals-its-existence-step-change-in-capabilities/)の報道を総合すると、Anthropicのモデルラインナップは以下のように拡張されることになります：

| 階層（Tier） | モデル | ステータス |
| --- | --- | --- |
| Capybara（新・最上位） | Claude Mythos | 限定テスト中（非公開） |
| Opus | Claude Opus 4.6 | 現行最高性能 |
| Sonnet | Claude Sonnet 4.6 | 現行主力 |
| Haiku | Claude Haiku 4.5 | 現行エントリー |

### 3つの強化軸

漏洩した草稿は、Claude Mythosが既存のどのモデルよりも「劇的に高いスコア」を記録した3つのベンチマーク領域を明示しています：

**注意**: 漏洩ドキュメントには**具体的なベンチマーク数値は一切含まれていません**。すべて「dramatically higher scores」という定性的な記述にとどまります。比較基準として、Opus 4.6はTerminal-Bench 2.0で65.4%を記録しGPT-5.2-Codexを上回っています（これはMythosの数値ではなく、現行Opusの参考値）。

**1. ソフトウェアコーディング**  
SWE-benchなどのコーディングタスクで「dramatically higher scores」。具体的な数値は未公開ですが、公式の表現では現行Opusを大幅に上回るとされています。

**2. 学術的推論（Academic Reasoning）**  
数学・科学・論理推論を含む学術ベンチマーク群でのスコア向上。大学院レベルの問題解決能力の飛躍的な改善が報告されています。

**3. サイバーセキュリティ（最も注目される領域）**  
ここが最も重要なポイントです。リーク文書は以下のように記しています：

> "currently far ahead of any other AI model in cyber capabilities"

「現時点でサイバー能力において他のすべてのAIモデルを大幅に上回っている」という評価は、モデルの能力の飛躍を示すと同時に、なぜ公開しないのかを説明する核心でもあります。

---

## なぜAnthropicは公開しないのか

### 2つの理由：安全性と計算コスト

Anthropicが Claude Mythosを一般公開しない理由は主に2つあります。

#### 理由1: 前例のないサイバーセキュリティリスク

リーク文書は以下の強い表現を使用しています：

> "presages an upcoming wave of models that can exploit vulnerabilities in ways that far outpace the efforts of defenders"

「防御側の努力を大幅に上回るスピードで脆弱性を悪用できるモデルの波を予兆する」という記述は、Anthropicが自社モデルのリスクを十分認識していることを示しています。

[Fortune](https://fortune.com/2026/03/27/anthropic-leaked-ai-mythos-cybersecurity-risk/)の報道によると、Anthropicは「unprecedented cybersecurity risks（前例のないサイバーセキュリティリスク）」という表現を内部的に使用していたとされます。

#### 理由2: 高い計算コスト

漏洩ドキュメントにはコストに関する記述も含まれており、[Futurismの分析](https://futurism.com/artificial-intelligence/anthropic-step-change-new-model-claude-mythos)によれば「非常に高い訓練・運用コスト」が課題とされています。Anthropicは「we're working to make it much more efficient before any general release（一般公開前に大幅にコスト効率を改善する必要がある）」と述べており、デプロイ戦略そのものが未確定な状態です。

### 限定アクセス戦略

公開の代わりに、Anthropicはサイバー防衛に特化した組織への限定アクセスを進めています。これは「攻撃者より先に防御側がシステムを強化できるようにする（harden their systems）」という目的に基づいています。

この戦略は、以下の論理に基づいています：

1. 攻撃側への能力付与を防ぐ
2. 防御側の研究機関に先行アクセスを与える
3. 実際の脅威シナリオでのモデル評価を進める
4. 安全な公開タイミングを模索する

---

## サイバーセキュリティ業界・市場への影響

### 株式市場の反応

このリークは金融市場にも即時に影響を与えました：

* **サイバーセキュリティ株の急落**: [CNBC報道](https://www.cnbc.com/2026/03/27/anthropic-cybersecurity-stocks-ai-mythos.html)によると、iShares Cybersecurity ETFが約4.5%下落。CrowdStrike・Palo Alto Networks・Zscalerが各約6%、SentinelOneが約6%、Okta約7%、Tenableが約9%下落するなど、「AIが攻撃力で防御を凌駕する」懸念が市場全体に広がりました
* **ビットコイン価格の下落**: [CoinDesk報道](https://www.coindesk.com/markets/2026/03/27/anthropic-s-massive-claude-mythos-leak-reveals-a-new-ai-model-that-could-be-a-cybersecurity-nightmare)によると、Bitcoinは$70,000を割り込み約$66,000まで下落。広範なリスクオフセンチメントが暗号資産市場にも波及しました

### 米国防総省との関係

注目すべき動きとして、米国防総省（Pentagon）の関係者がこのリークについてコメントを発表しています。[Gizmodo報道](https://gizmodo.com/leaked-anthropic-model-presents-unprecedented-cybersecurity-risks-much-to-pentagons-pleasure-2000739088)によると、Pentagonは以前からAnthropicに対して国内監視や完全自律兵器への活用を求めていましたが、Anthropicが同意できる範囲を超えていたとして交渉が難航していました。

この文脈から、Pentagonが今回のリークを「好都合」と受け止めている側面も指摘されています。「サイバーセキュリティリスク」というフレーミング自体が、競合的な利害関係を反映している可能性も否定できません。

### Anthropic IPOとの関係

[Bloomberg・The Informationの報道](https://fortune.com/2026/03/27/anthropic-data-leak-reveals-powerful-secret-mythos-ai-model/)（2026年3月27日）によると、Anthropicは2026年10月のIPOを検討中とされています。「圧倒的最強モデルが存在する」という事実は、投資家向けのバリュエーション根拠としても機能するため、リーク事件の影響は単純なネガティブニュースにとどまらない複雑な側面があります。

---

## エンジニアが知っておくべき示唆

### 1. 「性能と安全性のトレードオフ」の新局面

Claude Mythosのケースは、LLMの能力向上がある閾値を超えた時に「公開すべきでない」という判断が現実になることを示しています。これは今後のAI開発において：

* フロンティアモデルの「二層化」（公開版 vs 研究版）が加速する可能性
* 政府機関・研究機関向け専用モデルという新市場の形成
* 能力評価ベンチマークとリリース判断の連動

という方向性を示唆しています。

### 2. サイバーセキュリティ用途のAIへの注目

「サイバー防衛機関に限定アクセス」という戦略は、AI×サイバーセキュリティという領域の重要性を示しています。現状でも：

* AIによる脆弱性スキャン（CodexのCVE-Bench対応など）
* AIによるセキュリティインシデント分析
* レッドチーム自動化

などが進んでいますが、Mythosレベルの能力が防御側に提供されれば、セキュリティオペレーションのあり方が根本的に変わる可能性があります。

### 3. 情報漏洩事件自体の教訓

AIの安全性を標榜する企業が情報漏洩事件を起こしたという事実は、それ自体が重要な教訓です：

* CMSのアクセス制御は定期的に監査する
* 内部ドキュメントには適切な公開範囲を設定する
* 「安全性への注力」と「運用セキュリティ」は別の問題

---

## まとめ

Claude Mythosのリークは、AI業界における以下の現実を浮き彫りにしました：

* **能力の非対称性**: 最強のAIモデルは既に「公開できない」水準に達しつつある
* **安全性と公開性のジレンマ**: 最も有用なモデルが最も危険でもある
* **二層化するAIエコシステム**: 公開モデルと非公開モデルの格差が開く可能性
* **サイバーセキュリティのパラダイムシフト**: AI駆動の攻撃vs防御という新局面

Anthropicは「能力の強さゆえに慎重にリリースする」と述べていますが、現時点では具体的な公開計画は示されていません。Claude Mythosがいつ、どのような形で開発者の手に届くかは不明ですが、その登場がAI能力の新しいベースラインを設定することは間違いないでしょう。

---

## 参考リンク
