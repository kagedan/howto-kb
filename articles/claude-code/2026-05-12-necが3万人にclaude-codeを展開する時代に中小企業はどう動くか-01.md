---
id: "2026-05-12-necが3万人にclaude-codeを展開する時代に中小企業はどう動くか-01"
title: "NECが3万人にClaude Codeを展開する時代に、中小企業はどう動くか"
url: "https://note.com/seki_neko/n/nf09dc99afd25"
source: "note"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "cowork", "note"]
date_published: "2026-05-12"
date_collected: "2026-05-12"
summary_by: "auto-rss"
query: ""
---

**日本のエンタープライズAI標準が、2026年4月で大きく動いた。**

メーカー系SIerで購買DXの営業をやっていると、クライアント先の経営層から「ウチでもAI入れたいんだけど、何が標準になるの？」と聞かれる場面が増えてきた。今までは「まだ業界標準は決まっていない」と答えていたけれど、4月の発表でその答えが少し変わった。

![](https://assets.st-note.com/img/1778545506-YhW3gLdiGkXnl21s68ZIm7vb.png?width=1200)

AnthropicとNECが戦略提携し、グループ全社員 約3万人にClaude/Claude Codeを展開する、と発表した（2026/4/24）。同時に、日本SaaS主要100社のMCP対応を調べた調査も出ていて、この2つを並べて読むと、日本企業のAI導入の「上」と「下」がよく見える。

この記事では、NECの提携が何を意味するのか、そして中小企業の現場ではどこから手をつけるべきかを、自分の本業（製造業向けSIer営業）と個人開発の両側から整理する。

## NECは「Client Zero戦略」でClaude Codeを社内3万人に展開する

[Anthropic公式アナウンス](https://www.anthropic.com/news/anthropic-nec)を読むと、ポイントは4つある。

![](https://assets.st-note.com/img/1778545515-07IqQHM1aRPxyjUCcE5pJfo8.png?width=1200)

1. **Anthropicの「日本初」グローバルパートナー**になった
2. NECグループ全世界 約3万人の社員に[Claude Code](https://claude.com/code)を展開、日々の開発に組み込む
3. [Claude Cowork](https://www.anthropic.com/cowork)を非エンジニア部門にも全社展開
4. [NEC BluStellar Scenario](https://jpn.nec.com/blustellar/)（NECのコンサル+AI+セキュリティ統合プログラム）にClaude Opus 4.7を組み込み、顧客向け業界特化AIプロダクト（金融/製造/サイバーセキュリティ/自治体）を共同開発

特に重要なのは「Client Zero戦略」と呼ばれる進め方で、NECは長年「自社で使い倒してから顧客に売る」というモデルを取ってきた。今回もまずNEC自身が3万人規模で運用し、その知見を顧客向けプロダクトに転写する。

つまり、NECのお客さん（金融機関、製造業大手、自治体など）には、これから「NECが社内で使い込んだClaudeベースのソリューション」がパッケージで降りてくる。これは大手SIerの世界の標準が、明確に「Claude軸」へ動き始めたシグナルだと読んでいる。

3万人規模での本番展開は前例が少なく、ガバナンスやデータ取り扱いの設計は通常のSaaS導入と桁違いの難易度になる。それを「Client Zeroで先に踏み抜く」と宣言したNECの覚悟は、エンタープライズAI市場では大きなニュースだと思う。

## ただし、中小企業の「足場」は意外とまだ薄い

ここで一度、視点を中小企業側に下げる。

KanseiLink社が2026年4月に出した「日本のSaaS主要100社のMCP対応調査」を読むと、現実値が見える（[Zenn元記事](https://zenn.dev/kanseilink/articles/a316f473d8d506)）。

![](https://assets.st-note.com/img/1778545524-UpxGoi2sumBgqzYDdfQ1nb0S.png?width=1200)

100社を4分類すると、こうなる。

* **公式MCP**: 約20社（20%）
* **サードパーティMCP**: 約15社（15%）
* **APIのみ**: 約45社（45%）
* **何もなし**: 約20社（20%）

つまり、AIエージェントから直接呼べるSaaSは、日本ではまだ全体の35%しかない。半分近くは「APIはあるけどMCP化はされていない」状態。

カテゴリ別に見ると差がはっきりしている。

![](https://assets.st-note.com/img/1778545533-bsRJIvYhKOQ9do2zmriVAEHS.png?width=1200)

カテゴリMCP対応の状況 会計・財務freee（5ドメイン/約270API）/ Money Forward / Misoca / 弥生 が公式MCP — 最強カテゴリ プロジェクト管理kintone / Backlog が公式、Redmine はコミュニティ コミュニケーションChatwork / Slack / LINE WORKS が対応 CRM・営業Sansan / HubSpot Japan が公式 法務・契約CloudSign / GMO Sign / LegalOn は**全滅**。APIすら部分公開のみ HR・労務SmartHR / KING OF TIME はAPIは強いがMCPは限定的

ここで分かるのは、「中小企業の現場で多用されるSaaSのうち、AIエージェント前提で組めるのはまだ会計まわりとPJ管理が中心」という現実。

煽り系の発信を見ていると「全業務がAIエージェントで自動化される」みたいな話になりがちだけれど、契約書を扱う法務系はまだ全滅で、HR系もMCPは弱い。経営者・IT担当者の立場で言えば、ここを見誤ると「やってみたら結局つながらなかった」という失敗導入が出る。

著者のKanseiLinkは、この現状を踏まえて3つの構造的問題を指摘していた。

1. **Discovery（発見性）**: MCPがGitHubに散らばり、公式レジストリにほぼ載っていない
2. **Evaluation（評価可能性）**: 機械可読な仕様書がなく、READMEを人間がパースする必要
3. **Composition（組合せ）**: 複数SaaSを跨ぐワークフローのドキュメント化されたパターンがない

この3つは中小企業の経営者ではなくITコンサル側の課題だけれど、提案する側がここを意識していないと、現場の導入支援は崩れる。

## 中小企業はどこから手をつけるか — 三段階の現実解

NECの3万人展開と、SaaS100社調査の現実値、両方を見た上で中小企業の経営者・IT担当者向けに整理すると、こうなる。

**第1段階: 既に公式MCPがある領域から始める**会計（freee/Money Forward）: 経理の月次締め業務をClaudeに任せる

**第2段階: APIはあるがMCP未対応のSaaSを「APIのみ」で繋ぐ**

**第3段階: 法務契約系は当面「人間レビュー必須」のまま運用設計する**

この三段階で考えると、いきなり「全社AIエージェント化」を目指さずに、まず「公式MCPがある領域」で小さく成功体験を作ってから、徐々に広げていく順序が現実的だと思っている。

## 自分の場合: 個人開発でMCP前提の構成に寄せている

自分でも夜な夜な個人開発しているAIアプリ（製造業向け見積アプリ、Next.js + [Supabase](https://supabase.com) + Claude API構成）を作っていて、最近の設計判断はかなりMCP前提に寄せている。

具体的には、freee MCP連携を組み込むことで「見積作成 → 受注確定 → 会計仕訳まで一気通貫」の流れが現実的に作れるようになった。今回のNEC事例で言えば、大手SIerが業界特化AIで攻める領域とは別に、「中小製造業向けのクイック導入版」という隙間が、個人開発者にも残っていると感じている。

CREW.15で関わっているデザイン会社のDXコンサルでも、AdobeやFigmaのMCP対応状況を起点にワークフローを設計するアプローチに切り替えている。MCP前提で組むと、後から別ツールに差し替えるコストが下がるので、提案の説得力も上がる。

中小企業診断士の勉強もしている身として書くなら、これからの「IT・経営戦略」論点には「AIエージェント時代のSaaS選定基準」が新しく加わると思う。NECのClient Zero戦略はその先行事例として論述試験でも引きやすい。

## まとめ — 上と下を同時に見ておくと判断を間違えない

整理すると、こうなる。

* 上（エンタープライズ）: NECがClaude Code 3万人展開で「日本のエンタープライズAI標準」を動かし始めた
* 下（中小企業）: 公式MCP対応SaaSはまだ20社。会計・PJ管理から始めるのが現実的
* 中間: SIerやITコンサルが、上の動きと下の現実を翻訳しながら導入を支援するレイヤー

煽り記事は「もう全部AIで自動化される」と言いがちだけれど、現場の足場はまだ薄いところも多い。一方でエンタープライズは確実にClaude軸で動き始めている。両方を同時に見ておかないと、提案の解像度が落ちる、と思っている。

中小企業の経営者・IT担当者の方は、まずは自社が使っているSaaSのMCP対応状況を一度棚卸ししてみるのがおすすめ。そこから「どの業務なら今すぐAIエージェント化できるか」が逆算で見えてくる。

## 関連記事

[note記事埋め込み: 中小企業AI導入5業種事例（2026-04-22 公開）— 製造・小売・物流・飲食・サービスの実例で、本記事の「第1段階」具体策を補完]

[note記事埋め込み: 中小企業のAI活用ケース集（2026-04-09 公開）— 公式MCP対応SaaSを使った業務改善の起点として参照]

[#Claude](https://note.com/hashtag/Claude) [#ClaudeCode](https://note.com/hashtag/ClaudeCode) [#中小企業DX](https://note.com/hashtag/%E4%B8%AD%E5%B0%8F%E4%BC%81%E6%A5%ADDX) [#AIエージェント](https://note.com/hashtag/AI%E3%82%A8%E3%83%BC%E3%82%B8%E3%82%A7%E3%83%B3%E3%83%88) [#MCP](https://note.com/hashtag/MCP)
