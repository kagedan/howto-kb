---
id: "2026-06-13-anthropicが初のmythos級モデルclaude-fable-5を一般公開過去最強ただしサイ-01"
title: "Anthropicが初のMythos級モデル「Claude Fable 5」を一般公開——“過去最強”、ただしサイバー能力は封印"
url: "https://qiita.com/quotidia/items/93d15444372d79d05246"
source: "qiita"
category: "ai-workflow"
tags: ["API", "qiita"]
date_published: "2026-06-13"
date_collected: "2026-06-13"
summary_by: "auto-rss"
query: ""
---

> 本記事は筆者が運営する AI Quotidia (ai.quotidia.jp) の海外ニュース解説記事です。

<strong>Anthropic（アンソロピック）は2026年6月9日、初のMythos級AIモデル「Claude Fable 5」を一般公開しました——同社が「これまで広く提供した中で最も強力」とする一方、サイバーセキュリティ作業は実行できないよう封じられています（出典: The Verge / Bloomberg, 2026-06-09）。</strong>しかもこの公開は、同社自身が「AIは危険になりすぎている」と警告したわずか数日後のことでした（出典: TechCrunch, 2026-06-09）。本記事は2026年6月時点の報道に基づいて、この「最強」と「封印」の同居を一緒に噛み砕いていきます。

## この記事のポイント

- Anthropicが2026年6月9日、新AIモデル「Claude Fable 5」を一般公開した（出典: The Verge, 2026-06-09）
- 同社が「これまで広く提供した中で最も強力」と位置づける、一般が使える初のMythos級モデル（出典: The Verge / TechCrunch, 2026-06-09）
- サイバーセキュリティ作業は実行できないようブロックされている（出典: Bloomberg, 2026-06-09）
- 公開の数日前、同社は「AIは危険になりすぎている」と警告していた（出典: TechCrunch, 2026-06-09）
- Bloomberg・TechCrunch・The Vergeの米主要3媒体が同日に一斉に報じた

## そもそも「Mythos」とは

<strong>Mythosとは、Anthropicがソフトウェアの脆弱性発見などの高度なタスクに投入してきた、同社最上位級のAIモデル系統である。</strong>Quotidiaの既報のとおり、Mythosはゼロデイ脆弱性（修正パッチが存在しない未知の欠陥）を数千件発見し、段階展開プログラム「Project Glasswing」では初動1か月で1万件超の脆弱性を見つけたと報じられています。つまり、サイバー領域で実際に結果を出してきた系統です。

そして<strong>ガードレールとは、AIモデルが危険・不適切な出力や操作をしないように、設計段階で組み込まれる利用制限のことである。</strong>今回のClaude Fable 5は、このガードレールを強くかけた状態で一般に開放された、という構図になります。

## 「過去最強」と「封印」の同居

今回の公開の最大の特徴は、性能の高さそのものではなく、<strong>最も強い能力の一部をあらかじめ封じた状態で「広く配る」と決めた</strong>点にあります。

| | Mythos（従来） | Claude Fable 5（今回） |
|---|---|---|
| 提供範囲 | 一般には開放されず | 一般公開（widely available） |
| サイバー能力 | 脆弱性発見で実績（初動1か月で1万件超） | 実行できないようブロック |
| 位置づけ | 同社最上位級のモデル系統 | 一般が使える初のMythos級 |

TechCrunch（2026-06-09）は、この公開が「AIは危険になりすぎている」という同社自身の警告の数日後だったことを指摘しています。危険性を最もよく知る開発元が、能力の蓋の設計も自分で行った——そういう構図です。

## 公開直後の反響——「ガードレールが厳しすぎる」

ただし、蓋の閉め方には早くも異論が出ています。

TechCrunch（2026-06-10）によると、セキュリティ研究者たちは「Fableのガードレールは、防御目的の研究にすら使えないほど厳しい」と不満を表明しています。さらにThe Verge（2026-06-10）は、Claude Fable 5が基本的な生物学の質問にさえ答えない事例を報じました。<strong>安全のための制限が、正当な用途まで巻き込んでいるのではないか</strong>——という論点です。

## 日本にとっての意味

TechCrunch（2026-06-09）によると、API料金は100万入力トークンあたり10ドル・100万出力トークンあたり50ドル（Opus 4.8の2倍）で、APIと従量制Enterpriseでは即日提供、サブスクリプション向けは段階展開で2026年6月22日までは追加費用なしとされています。<strong>一方、日本語対応・日本向け提供条件は、本稿時点の報道では確認できていません。</strong>そのため「日本でもすぐに最強モデルが使える」と断定はできません。

そのうえで、日本の利用者・企業にとって重要なのは、<strong>「何ができるか」だけでなく「何が意図的に制限されているか」が、モデル選びの仕様項目になった</strong>という変化です。生成AIの業務導入が進む日本でも、セキュリティ調査や研究開発のような正当な用途が制限に触れる場面は今後増える可能性があり、導入検証の際に「制限仕様」を確認する習慣が、これまで以上に意味を持つようになります。

## まとめ（FAQ）

<strong>Q. Claude Fable 5は誰でも使える？</strong>
A. Anthropicが「広く提供する（widely available）」初のMythos級モデルと報じられています（出典: The Verge, 2026-06-09）。APIと従量制Enterpriseでは即日、サブスクリプションでは段階展開で提供されます（出典: TechCrunch, 2026-06-09）。日本語対応・日本向け提供条件は報道時点で未確認です。

<strong>Q. MythosとClaude Fable 5の違いは？</strong>
A. Fable 5はMythos級の能力を持ちながら、サイバーセキュリティ作業を実行できないようブロックされた一般公開版です（出典: Bloomberg, 2026-06-09）。

<strong>Q. なぜサイバー能力を封じたのか？</strong>
A. 同社は公開の数日前に「AIは危険になりすぎている」と警告しており（出典: TechCrunch, 2026-06-09）、Anthropicは顧客が早く恩恵を受けられるよう意図的に保守側に倒した設計だと説明し、誤検出の削減に取り組んでいるとしています（出典: The Verge, 2026-06-10）。

<strong>Q. ガードレールに問題は出ていない？</strong>
A. セキュリティ研究者から「研究にも使えないほど厳しい」との不満が出ており（出典: TechCrunch, 2026-06-10）、基本的な生物学の質問に答えない事例も報じられています（出典: The Verge, 2026-06-10）。


---

参考元: https://techcrunch.com/2026/06/09/anthropic-released-claude-fable-5-its-most-powerful-model-publicly-days-after-warning-ai-is-getting-too-dangerous/

---

> この記事は [AI Quotidia](https://ai.quotidia.jp?utm_source=qiita&utm_medium=referral) から転載しています。
> **文豪モード**（情景描写と比喩で読む）・**速報モード**（30秒で読める）もサイトで読めます。
> 👉 https://ai.quotidia.jp?utm_source=qiita&utm_medium=referral
