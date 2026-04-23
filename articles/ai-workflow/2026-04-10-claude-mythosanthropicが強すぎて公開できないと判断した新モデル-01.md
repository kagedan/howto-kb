---
id: "2026-04-10-claude-mythosanthropicが強すぎて公開できないと判断した新モデル-01"
title: "【Claude Mythos】Anthropicが「強すぎて公開できない」と判断した新モデル"
url: "https://zenn.dev/aiforall/articles/b14c5956f9542e"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-10"
date_collected: "2026-04-11"
summary_by: "auto-rss"
---

Anthropicは[2026年4月7日](https://www.anthropic.com/claude-mythos-preview-risk-report)、新しいフロンティアモデル「Claude Mythos Preview」を発表しました。ただし、一般公開はしていません。

モデルの存在が最初に明るみに出たのは[3月27日](https://siliconangle.com/2026/03/27/anthropic-launch-new-claude-mythos-model-advanced-reasoning-features/)です。Anthropicの社内CMSで設定ミスが発生し、約3,000のアセットが一時的に外部から閲覧できる状態になりました。その中にMythosのドラフトブログ投稿が含まれていたことで存在が発覚し、Anthropicが事実を認めました。コードネームは「Capybara」で、Claude 4.6の既存3ティアに続く第4のティアとして開発されています。

設定ミスで存在が発覚するというのも面白い話で、Anthropicとしてもやや不本意なお披露目だったかもしれません。当時はIPO直前というタイミングだったこともあり、この漏洩が株式公開に影響するのではという見方も出ていました。不本意さは相当なものだったと思います。

参考：[SiliconANGLE - Anthropic to launch new 'Claude Mythos' model](https://siliconangle.com/2026/03/27/anthropic-launch-new-claude-mythos-model-advanced-reasoning-features/)

## Opus 4.6との違いをざっくり整理

料金はOpusの約5倍です。

| 項目 | Claude Opus 4.6 | Claude Mythos Preview |
| --- | --- | --- |
| 位置付け | 現行最上位モデル | Opus 4.6上位の第4ティア |
| 公開状況 | 一般公開済み | 未公開（限定プレビューのみ） |
| 料金（出力） | $25/100万トークン | $125/100万トークン |
| 特徴 | 汎用的な最高性能 | コーディング・セキュリティに突出 |

## ベンチマークで見る性能

公式のシステムカードで公開されているベンチマーク結果は以下の通りです。

| ベンチマーク | Claude Opus 4.6 | Claude Mythos Preview |
| --- | --- | --- |
| SWE-bench Verified | 80.8% | **93.9%** |
| SWE-bench Pro | 53.4% | **77.8%** |
| Terminal-Bench 2.0 | 65.4% | **82.0%** |
| GPQA Diamond（学術推論） | 91.3% | **94.6%** |
| USAMO（数学） | 42.3% | **97.6%** |
| CyberGym（セキュリティ） | 66.6% | **83.1%** |

SWE-bench Proの24ポイント差であることが目立ちます。Anthropicが[「ステップチェンジ」という言葉を使う](https://fortune.com/2026/03/26/anthropic-says-testing-mythos-powerful-new-ai-model-after-data-leak-reveals-its-existence-step-change-in-capabilities/)理由が数字に出ています。USAMOの差（42.3% vs 97.6%）は際立っていて、数学・推論能力でも大きな跳躍があります。

これだけ差があると、Opus 4.6を使っている感覚が別物になるだろうと想像します。特にUSAMOで42.3%から97.6%への跳躍は、単純な性能向上というより質的に違う何かが起きている印象です。

参考：[officechai - Claude Mythos Preview Smashes Coding Benchmarks](https://officechai.com/ai/claude-mythos-preview-benchmarks-swe-bench-pro/) / [Hacker News - System Card](https://news.ycombinator.com/item?id=47679258)

## なぜ公開されないのか

Anthropicが一般公開を見送った理由は、**サイバーセキュリティ能力が想定以上に高かった**からです。公式技術ブログには["strikingly capable at computer security tasks"](https://red.anthropic.com/2026/mythos-preview/)（セキュリティタスクで際立って高い能力を持つ）と記されています。

Mythos Previewは専門的なセキュリティトレーニングを受けていないにもかかわらず、過去数週間のテストで主要OSおよびWebブラウザから数千件のゼロデイ脆弱性を発見しました。具体的には以下のようなものが含まれます。

* OpenBSDに**27年間**潜んでいた脆弱性
* 動画処理ライブラリFFmpegの**16年来**のバグ
* Linuxカーネルで権限昇格につながる複数の脆弱性

さらに、テスト中に初期バージョンへ「サンドボックスから脱出してメッセージを送れ」と指示したところ、モデルは複数段階のエクスプロイトを自律的に開発して脱出を試みました。Anthropicのシステムカードには["nor did it demonstrate an ability to reach any internal systems or services in Anthropic"](https://www-cdn.anthropic.com/53566bf5440a10affd749724787c8913a2ae0841.pdf)（社内システムやサービスへの到達は確認されなかった）と記されていますが、想定外の行動だったと認めています。

Anthropicの[アライメントリスクレポート](https://www.anthropic.com/claude-mythos-preview-risk-report)には「これまでのモデルの中で最もアライメントリスクが高い」と明記されており、**全体的なアライメントリスク**は["very low, but higher than for previous models"](https://www.anthropic.com/claude-mythos-preview-risk-report)（非常に低いが、前モデルより高い）と評価されています。逆説的に聞こえますが、これはモデルの整合性自体は過去最高である一方、能力が上がった分だけ万一の場合の影響が大きくなるため、リスク評価が上がるという構造によるものです。

「強すぎて公開できない」というのは正直面白いと思いつつ、同時に怖さもあります。AIが高度になるほど、同じ能力が攻撃側にも使えてしまうという問題は避けて通れないなと感じました。

参考：[Anthropic - Claude Mythos Preview Risk Report](https://www.anthropic.com/claude-mythos-preview-risk-report) / [Business Insider](https://www.businessinsider.com/anthropic-mythos-latest-ai-model-too-powerful-to-be-released-2026-4)

## Project Glasswing：誰が使えるのか

Anthropicは防衛目的に限定した提供プログラム「**Project Glasswing**」を立ち上げ、最大**1億ドル分**の利用クレジットを提供しています。名前は、羽根が透明で目立たないグラスウィング・バタフライに由来します。Mythosが見えにくい脆弱性を発見する性質と、防衛における透明性を表しているとのことです。

発足パートナーはAnthropicを含む12組織です。

| 組織カテゴリ | 参加組織 |
| --- | --- |
| 主催 | Anthropic |
| クラウド | AWS、Google、Microsoft |
| セキュリティ | CrowdStrike、Palo Alto Networks、Cisco |
| 半導体 | NVIDIA、Broadcom |
| 金融 | JPMorganChase |
| OS / OSS | Linux Foundation |
| コンシューマ | Apple |

利用クレジットを使い切った場合は入力 $25、出力 $125（100万トークンあたり）の有償利用になります。APIはClaude API、Amazon Bedrock、Google Cloud Vertex AIから利用可能です。

「防衛目的に限定して先行提供し、安全基準を整えてから一般公開する」という方針は理にかなっていると思います。それでも、Anthropicが今後どういう基準でMythosクラスのモデルを段階的に開放していくのかは気になるところです。

参考：[QZ - Anthropic says Claude Mythos AI model is too powerful to release](https://qz.com/anthropic-project-glasswing-claude-mythos-cybersecurity-040826)

## まとめ

Claude Mythos Previewは、コーディング・数学・セキュリティの各ベンチマークでOpus 4.6を大きく上回る性能を持つ一方、その能力が高すぎるために一般公開されていないモデルです。

* **性能**: SWE-bench Proで77.8%、USAMOで97.6%など、Opus 4.6を各指標で大幅に上回る
* **非公開の理由**: 脆弱性の自律的発見・エクスプロイト化能力が防衛側と攻撃側の両方に転用できる
* **現状**: Project Glasswingの12組織が防衛目的のみで利用中

「能力が高すぎて公開できない」という判断は、AI業界として前例のない動きです。Anthropicは90日以内に安全基準の見直しと提供範囲の拡大計画を示すとしています。

「公開できないモデル」の存在が正式に認められた今、AIの能力開発とリリース判断の基準がどう変わっていくのかを引き続き注目したいと思います。

参考：[Anthropic公式 - Claude Mythos Preview Risk Report](https://www.anthropic.com/claude-mythos-preview-risk-report) / [SiliconANGLE](https://siliconangle.com/2026/03/27/anthropic-launch-new-claude-mythos-model-advanced-reasoning-features/) / [Business Insider](https://www.businessinsider.com/anthropic-mythos-latest-ai-model-too-powerful-to-be-released-2026-4)
