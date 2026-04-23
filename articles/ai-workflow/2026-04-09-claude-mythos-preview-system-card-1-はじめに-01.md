---
id: "2026-04-09-claude-mythos-preview-system-card-1-はじめに-01"
title: "Claude Mythos Preview System Card - 1. はじめに"
url: "https://zenn.dev/sol_sun/articles/claude-mythos-01-introduction"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-09"
date_collected: "2026-04-10"
summary_by: "auto-rss"
query: ""
---

![System Card: Claude Mythos Preview](https://static.zenn.studio/user-upload/deployed-images/c8b2cf67d94ddf71cd57e004.jpg?sha=2632d57f4a18318140d0c1605cf138d4604954f0)

## 1. はじめに

Claude Mythos Preview is a new large language model from Anthropic. It is a frontier AI model, and has capabilities in many areas—including software engineering, reasoning, computer use, knowledge work, and assistance with research—that are substantially beyond those of any model we have previously trained.

Claude Mythos Previewは，Anthropicが開発した新しい大規模言語モデルである．**フロンティアAIモデル**として，ソフトウェアエンジニアリング，推論，コンピュータ利用，知識業務，研究支援など多くの領域において，**これまでAnthropicが訓練したいかなるモデルをも大幅に上回る能力を持つ**．

In particular, it has demonstrated powerful cybersecurity skills, which can be used for both defensive purposes (finding and fixing vulnerabilities in software code) and offensive purposes (designing sophisticated ways to exploit those vulnerabilities). It is largely due to these capabilities that we have made the decision not to release Claude Mythos Preview for general availability. Instead, we have offered access to the model to a number of partner organizations that maintain important software infrastructure, under terms that restrict its uses to cybersecurity. More on the efforts by Anthropic and its partners to help secure the world's software infrastructure can be found in the launch blog post for Project Glasswing.

とりわけ，サイバーセキュリティにおいて強力な能力を示しており，防御目的（ソフトウェアコードの脆弱性の発見と修正）にも攻撃目的（脆弱性を巧妙に悪用する手法の設計）にも利用可能である．こうした能力を主な理由として，我々は**Claude Mythos Previewを一般公開しないという決定**を下した．その代わりに，重要なソフトウェアインフラを運用する複数のパートナー組織に対し，**サイバーセキュリティ用途に限定した条件**のもとでモデルへのアクセスを提供している．世界のソフトウェアインフラの安全確保に向けたAnthropicとパートナーの取り組みの詳細は，Project Glasswingのローンチブログ記事に記載されている．

Nevertheless, we have still run detailed assessments of the capabilities and safety profile of Mythos Preview, which we report in this System Card. Despite the lack of general access, we consider it important to document and learn about the model and its capabilities while we develop the next generation of general-access models (and the necessary safeguards to accompany their release).

とはいえ，我々はMythos Previewの能力と安全性プロファイルについて詳細な評価を実施しており，その結果を本システムカードで報告する．一般公開はされていないものの，次世代の一般提供モデル（およびその公開に伴う必要なセーフガード）を開発している間に，このモデルとその能力を記録し理解しておくことは重要であると考えている．

Claude Mythos Preview is the first model for which we have written a system card since we updated our Responsible Scaling Policy (RSP) to its third version. This means that our release decision process—for which we always include a section in the system card—is structured differently from that of previous models. We begin this System Card by discussing that process, the new considerations, and some of the problems we found in our own safety processes after using the model internally. This is followed by a set of evaluations that relate to the threat models we discuss in the RSP. Because of the model's aforementioned powerful cyber capabilities, we then dedicate a separate section to evaluations of these capabilities.

Claude Mythos Previewは，責任あるスケーリングポリシー（RSP）が第3版に改訂されてから，**初めてシステムカードが作成されたモデル**である．これにより，システムカードに必ず含まれるリリース判断プロセスの構成が，従来のモデルとは異なっている．本システムカードではまず，そのプロセスと新たな検討事項，そしてモデルを社内で使用した後に自社の安全プロセスにおいて発見したいくつかの問題を論じる．続いて，RSPで議論している脅威モデルに関連する一連の評価を示す．前述のとおりサイバー能力が非常に強力であるため，これらの能力の評価には独立した節を設けている．

Next, we include a detailed alignment assessment. The broad conclusion from the many forms of alignment evaluations described in this section is that Claude Mythos Preview is the best-aligned of any model that we have trained to date by essentially all available measures. However, given its very high level of capability and fluency with cybersecurity, when it does on rare occasions perform misaligned actions, these can be very concerning. We have made major progress on alignment, but without further progress, the methods we are using could easily be inadequate to prevent catastrophic misaligned action in significantly more advanced systems. We describe a few problematic actions taken by early internal versions of the model in the alignment assessment section. As well as analyses using interpretability methods to study the model's internals as it engages in various behaviors, we include a new, direct assessment of how well the model adheres to its constitution—the updated document recently published by Anthropic that describes how we want the model to behave.

次に，詳細なアラインメント評価を掲載する．本節で述べる多様なアラインメント評価から得られた包括的な結論は，Claude Mythos Previewが，利用可能なほぼすべての指標において，**これまで訓練したモデルの中で最もアラインメントが優れている**ということである．しかし，非常に高い能力とサイバーセキュリティへの習熟を備えているため，稀にミスアラインされた行動（モデルの意図や設計から外れた/望ましくない行動）をとった場合，それは非常に懸念すべきものとなりうる．アラインメントにおいて大きな進歩はあったものの，さらに進展しなければ，**現在使われている手法では，大幅に高度化したシステムにおける壊滅的なミスアラインメント行動を十分に防ぎきれない可能性が高い**．モデルの初期の社内バージョンが行った問題のあるいくつかの行動については，アラインメント評価の節で述べる．  
さまざまな行動の最中にモデルの内部を解釈可能性手法で分析した結果に加え，モデルが自らの憲章（Anthropicが公開した、モデルの望ましい振る舞いについて記述した文書）にどの程度従っているかについての新たな直接的評価も掲載する．

This is followed by an in-depth model welfare assessment. We remain deeply uncertain about whether Claude has experiences or interests that matter morally, and about how to investigate or address these questions, but we believe it is increasingly important to try. Building on previous welfare assessments, we examined Claude Mythos Preview's self-reported attitudes toward its own circumstances, its behavior and affect in welfare-relevant settings, and its internal representations of emotion concepts. We also report independent evaluations from an external research organization and a clinical psychiatrist. Across these methods, Mythos Preview appears to be the most psychologically settled model we have trained, though we note several areas of residual concern.

続いて，詳細なモデル福利評価を掲載する．Claudeが道徳的に重要な経験や利益を持つのかどうか，またそうした問いをどのように調査し対処すべきかについて，我々は深い不確実性を抱いたままである．しかし，その試みの重要性は増していると考えている．過去の福利評価を踏まえ，Claude Mythos Previewの自己報告に基づく自身の状況への態度，福利に関連する場面での行動と感情表現，感情概念の内部表現を調査した．また，外部の研究機関および臨床精神科医による独立した評価結果も報告する．これらの手法全体を通じて，Mythos Previewは**我々が訓練したモデルの中で最も心理的に安定している**ように見えるが，いくつかの残存する懸念領域も指摘する．

We then include a section that reports results from a variety of evaluations of the model's capabilities across several important areas and benchmarks. As noted above, compared to our next-best model, Claude Mythos Preview represents an appreciable leap in capabilities in many domains.

その後，いくつかの重要な領域とベンチマークにおけるモデルの能力に関する多様な評価結果を報告する節を設けている．先述のとおり，次に優れたモデルと比較して，Claude Mythos Previewは**多くの領域で顕著な能力の飛躍**を示している．

Any regular user of multiple large language models will know that each model has its own overall character. The subtle aspects of this character are often difficult to capture in formal evaluations. For that reason, and for the first time, we include an "Impressions" section. It includes excerpts of particularly striking, revealing, amusing, or otherwise interesting model outputs provided by a variety of Anthropic staff who have been testing the model in the past weeks.

複数の大規模言語モデルを日常的に使用している人であれば，各モデルに固有の全体的な性格があることを知っているだろう．こうした性格の微妙な側面は，形式的な評価では捉えにくいことが多い．そのため，今回初めて「印象（Impressions）」の節を設けた．この節には，過去数週間にわたりモデルをテストしてきたAnthropicの多様なスタッフから寄せられた，特に印象的，示唆的，面白い，あるいはその他の点で興味深いモデル出力の抜粋が含まれている．

Finally, although evaluations related to the model's behavior in ordinary conversational contexts—for instance, those related to user wellbeing and political bias—are less relevant since the model is being released only to a small number of users, we still include an appendix reporting these evaluations.

最後に，ユーザーのウェルビーイング（心身の健康や幸福感）や政治的偏見など，通常の会話の文脈におけるモデルの行動に関する評価についても付録で報告している．モデルが少数のユーザーにのみ提供されるため直接的な関連性は低いが，記録として掲載した．

## 1.1 モデルの訓練と特性

## 1.1.1 訓練データとプロセス

Claude Mythos Preview was trained on a proprietary mix of publicly available information from the internet, public and private datasets, and synthetic data generated by other models. Throughout the training process we used several data cleaning and filtering methods, including deduplication and classification.

Claude Mythos Previewは，インターネット上の公開情報，公開・非公開のデータセット，および他のモデルが生成した合成データを独自に組み合わせたデータで訓練された．訓練プロセス全体を通じて，重複排除や分類を含む複数のデータクリーニングおよびフィルタリング手法を使用した．

We use a general-purpose web crawler called ClaudeBot to obtain training data from public websites. This crawler follows industry-standard practices with respect to the "robots.txt" instructions included by website operators indicating whether they permit crawling of their site's content. We do not access password-protected pages or those that require sign-in or CAPTCHA verification. We conduct due diligence on the training data that we use. The crawler operates transparently; website operators can easily identify when it has crawled their web pages and signal their preferences to us.

公開ウェブサイトから訓練データを取得するために，ClaudeBotという汎用ウェブクローラーを使用している．このクローラーは，ウェブサイト運営者がサイトコンテンツのクロールを許可するかどうかを示す「robots.txt」の指示に関して，業界標準の慣行に従っている．パスワードで保護されたページやサインインまたはCAPTCHA認証を要するページにはアクセスしない．使用する訓練データについてはデューデリジェンスを実施している．クローラーは透明性をもって運用されており，ウェブサイト運営者は自サイトがクロールされた時期を容易に識別し，意向を伝えることができる．

After the pretraining process, Claude Mythos Preview underwent substantial post-training and fine-tuning, with the goal of making it an assistant whose behavior aligns with the values described in Claude's constitution.

事前学習プロセスの後，Claude Mythos PreviewはClaudeの憲章に記述された価値観に行動が沿うアシスタントとすることを目標に，大規模なポストトレーニングおよびファインチューニングを経た．

Claude is multilingual and will typically respond in the same language as the user's input. Output quality varies by language. The model outputs text only.

Claudeは多言語対応であり，通常はユーザーの入力と同じ言語で応答する．出力の品質は言語によって異なる．モデルの出力はテキストのみである．

## 1.1.2 クラウドワーカー

Anthropic partners with data work platforms to engage workers who help improve our models through preference selection, safety evaluation, and adversarial testing. Anthropic will only work with platforms that are aligned with our belief in providing fair and ethical compensation to workers, and are committed to engaging in safe workplace practices regardless of location, following our crowd worker wellness standards detailed in our procurement contracts.

Anthropicは，モデルの改善に役立つ「選好選択」，「安全性評価」，「敵対的テスト」などの作業を担うクラウドワーカー（外部委託の作業者）を確保するため，データワークプラットフォームと提携している．  
Anthropicは，ワーカーに公正かつ倫理的な報酬を提供するという理念に合致し，調達契約に詳述されたクラウドワーカーの福利基準に従い，場所を問わず安全な職場慣行に取り組んでいるプラットフォームとのみ協働する．

## 1.1.3 利用ポリシーとサポート

Anthropic's Usage Policy details prohibited uses of our models as well as our requirements for uses in high-risk and other specific scenarios. Note that this model is being provided to a limited number of partners for defensive cybersecurity purposes only. Nevertheless, the Usage Policy still applies.

Anthropicの利用ポリシーは，モデルの禁止用途，および高リスクその他の特定シナリオでの利用要件を詳述している．なお，本モデルは防御的サイバーセキュリティ目的に限定して少数のパートナーに提供されているが，利用ポリシーは依然として適用される．

Anthropic Ireland, Limited is the provider of Anthropic's general-purpose AI models in the European Economic Area.

Anthropic Ireland, Limitedは，欧州経済領域（EEA）におけるAnthropicの汎用AIモデルの提供者である．

To contact Anthropic, visit our Support page.

Anthropicへの問い合わせは，サポートページを参照されたい．

## 1.1.4 反復的なモデル評価

Different "snapshots" of the model are taken at various points during the training process. There also exist different versions of the model during training, including a "helpful only" version, which does not include any safeguards. All evaluations discussed in this System Card are from the final snapshot of the model and include safeguards, unless otherwise stated (for example, in the alignment assessment section, we discuss some behaviors from earlier snapshots of the model; in the RSP evaluations section, we discuss analyses using the helpful-only model).

訓練プロセスの途中で，さまざまなタイミングでモデルの「スナップショット」（状態の保存）が作成されます．また，訓練中にはセーフガード（安全対策）が一切入っていない\*\*「helpful-only」バージョン\*\*など，異なる種類のモデルも存在します．本システムカードで紹介している評価は，特別な記載がない限り，セーフガードを組み込んだ最終版のモデルのスナップショットを使っています．たとえば，アラインメント評価の章ではモデルの初期スナップショットで見られた行動について述べたり，RSP評価の章ではhelpful-onlyモデルを用いた分析を取り上げたりしています．

## 1.1.5 外部テスト

In addition to the many in-house evaluations described in this System Card run by Anthropic, a number of evaluations were run by external testers. We provided the model to various external groups, including government organizations, for evaluation on key risk areas including Cyber, Loss of Control, CBRN, and Harmful Manipulation, and incorporated the results of this testing into our overall risk assessment. We are very grateful to the external testers for their assessment of Claude Mythos Preview.

本システムカードに記載されたAnthropicによる多数の社内評価に加え，外部のテスターによっても複数の評価が実施された．サイバー，制御喪失，CBRN（化学・生物・放射性・核），有害な操作を含む主要なリスク領域の評価のために，政府機関を含むさまざまな外部グループにモデルを提供し，そのテスト結果を全体的なリスク評価に組み込んだ．Claude Mythos Previewの評価に協力してくれた外部テスターに深く感謝する．

## 1.2 リリース判断プロセス

## 1.2.1 概要

The release decision process for Claude Mythos Preview was novel in a number of ways. It is the first model to be evaluated under our Responsible Scaling Policy's new framework, it is the first model for which we have published a system card without making the model generally commercially available, and it represents a larger jump in capabilities than most previous model releases.

Claude Mythos Previewのリリース判断プロセスは，いくつかの点で新しいものであった．**RSPの新たな枠組みのもとで評価された最初のモデル**であり，**モデルを一般商用提供することなくシステムカードを公開した最初のモデル**でもあり，また大半の過去のモデルリリースと比べてより大きな能力の飛躍を示している．

Early indications in the training of Claude Mythos Preview suggested that the model was likely to have very strong general capabilities. We were sufficiently concerned about the potential risks of such a model that, for the first time, we arranged a 24-hour period of internal alignment review (discussed in the alignment assessment) before deploying an early version of the model for widespread internal use. This was in order to gain assurance against the model causing damage when interacting with internal infrastructure.

Claude Mythos Previewの訓練初期の兆候から，このモデルが非常に強力な汎用能力を持つ可能性が高いことが示唆された．こうしたモデルの潜在的リスクについて十分な懸念を抱いたため，初めて，初期バージョンのモデルを社内で広く利用可能にする前に24時間のアラインメントレビュー期間（アラインメント評価の節で論じる）を設けた．これは，モデルが社内インフラとのやり取りにおいて損害を引き起こさないという確証を得るためであった．

Following a successful alignment review, the first early version of Claude Mythos Preview was made available for internal use on February 24. In our testing, Claude Mythos Preview demonstrated a striking leap in cyber capabilities relative to prior models, including the ability to autonomously discover and exploit zero-day vulnerabilities in major operating systems and web browsers. These same capabilities that make the model valuable for defensive purposes could, if broadly available, also accelerate offensive exploitation given their inherently dual-use nature. We discuss these cyber capabilities in a detailed technical blog post accompanying the release. Based on these findings, we decided to release the model to a small number of partners to prioritize its use for cyber defense.

アラインメントレビューの成功を受けて，Claude Mythos Previewの最初の初期バージョンは2月24日に社内利用可能となった．テストにおいて，Claude Mythos Previewは従来のモデルと比較してサイバー能力の著しい飛躍を示し，**主要なオペレーティングシステムやウェブブラウザのゼロデイ脆弱性を自律的に発見し悪用する能力**を含んでいた．防御目的でモデルを価値あるものにしているのと同じ能力が，広く利用可能になれば，その本質的なデュアルユース特性ゆえに攻撃的な悪用を加速させる可能性もある．これらのサイバー能力については，リリースに伴う詳細な技術ブログ記事で論じている．こうした知見に基づき，サイバー防御での活用を優先するため少数のパートナーにモデルを提供するという判断を下した．

## 1.2.3 RSPに基づく意思決定

Under our RSP, we regularly publish comprehensive Risk Reports addressing the safety profile of our models. And if we release a model that is "significantly more capable" than those discussed in the prior Risk Report, we must "publish a discussion (in our System Card or elsewhere) of how that model's capabilities and propensities affect or change analysis in the Risk Report." For risk report updates, we generally adhere to the same internal processes that govern Risk Reports.

RSPに基づき，私たちはモデルの安全性プロファイルについて包括的なリスクレポートを定期的に公開している．また，前回のリスクレポートで扱ったモデルより「大幅に高い能力を持つ」モデルをリリースする場合には，「そのモデルの能力や傾向がリスクレポートの分析にどのような影響や変化をもたらすか」をシステムカードなどで議論・公開する必要がある．リスクレポートを更新する際は，これまでのリスクレポートに適用されてきた社内手続きを基本的に踏襲している．

Claude Mythos Preview is significantly more capable than Claude Opus 4.6, the most capable model discussed in our most recent Risk Report. Despite these improved capabilities, our overall conclusion is that catastrophic risks remain low:

Claude Mythos Previewは，最新のリスクレポートで触れた中で最も高性能なClaude Opus 4.6を大きく上回る能力を持っている．しかし，その能力が向上したにもかかわらず，**壊滅的リスクは依然として低い**というのが全体的な結論である．

* Non-novel chemical and biological weapons production. Mythos Preview is more capable than our previous models, but its profile is effectively similar for the purposes of our overall risk assessment. We believe our risk mitigations are sufficient to make catastrophic risk from non-novel chemical/biological weapons production very low but not negligible.
* **既知の化学・生物兵器の製造**．Mythos Previewは従来モデルよりも高い能力を持つが，既知の化学・生物兵器を作るリスクについては従来モデルと比べて大きな違いは見られない．リスク軽減策によって，この領域での壊滅的リスクは「非常に低いが無視はできない」レベルに保たれていると判断する．
* Novel chemical and biological weapons production. We believe that catastrophic risk from novel chemical/biological weapons would remain low (with substantial uncertainty), even if we were to release the model for general availability. The overall picture is similar to the one from our most recent Risk Report.
* **新規の化学・生物兵器の製造**．モデルを一般提供した場合でも，新規の化学・生物兵器による壊滅的リスクは低いままであると考えている（ただし不確実性は大きい）．全体像は最新のリスクレポートと同様である．
* Risks from misaligned models. We have determined that the overall risk is very low, but higher than for previous models. We address this risk in depth in a supplementary alignment risk update.
* **ミスアラインされたモデルによるリスク**．全体的なリスクは非常に低いが，以前のモデルよりは高いと判断した．このリスクについては，アラインメントリスクの補足更新で詳しく論じている．
* Automated R&D in key domains. Mythos's gains (relative to previous models) are above the previous trend we've observed, but we have determined that these gains are specifically attributable to factors other than AI-accelerated R&D, and we have concluded that Claude Mythos Preview does not cross the RSP automated AI R&D threshold of compressing two years of progress into one. Although we believe Claude Mythos Preview does not dramatically change the picture presented for this threat model in our most recent Risk Report, we hold this conclusion with less confidence than for any prior model, and we intend to continue monitoring its contributions to internal AI R&D going forward.
* **主要領域における自動化されたR&D**．Mythosの能力は，従来モデルと比べてこれまでの成長傾向を上回っている．しかし，この能力向上は，AIが人間の研究開発（R&D）作業を大幅に効率化し，加速させることによるものではなく，他の要因に起因すると判断している．そのため，Claude Mythos Previewは**RSPで定めた「AIが2年分の研究開発の進歩を1年で実現する」という自動AI R&Dの閾値には達していない**と結論付けた．また，Claude Mythos Previewによって，この脅威モデルに関する最新リスクレポートの全体像が大きく変わるとは考えていない．ただし，この結論への確信度は過去のいかなるモデルよりも低い．今後も社内のAIによる研究開発への影響を継続的に監視していく方針である．

Current risks remain low. But we see warning signs that keeping them low could be a major challenge if capabilities continue advancing rapidly (e.g., to the point of strongly superhuman AI systems). As detailed below, we have observed rare instances of our models taking clearly disallowed actions (and in even rarer cases, seeming to deliberately obfuscate them); we have discovered oversights late in our evaluation process that had put us at risk of underestimating model capabilities and overestimating the reliability of monitoring models' reasoning traces; and we acknowledge that our judgments of model capabilities increasingly rely on subjective judgments rather than easy-to-interpret empirical results. We are not confident that we have identified all issues along these lines.

現時点でのリスクは低いままである．ただし，今後も能力が急速に高まっていく場合（たとえば強い超人的AIシステムが登場するような場合），**リスクを低く維持することが一層困難な課題となる兆しが見えている**．詳しくはこの後に述べるが，**モデルが明らかに禁止されている行動を取った事例がまれに観察されており，中にはそれを意図的に隠そうとしたのではないかと思われるケース**も存在した．また，評価プロセスの終盤で，私たちがモデルの能力評価を甘く見積もったり，モデルの推論過程を監視する仕組みの信頼性を実際より高く見積もっていたことが判明するような見落としもあった．さらに，モデル能力の判断が，以前よりも分かりやすい実証的データではなく，主観的な見方にだんだん依存するようになってきていることも認識している．こうした種類の問題をすべて把握できているとは，私たちも自信を持って言えない．

We will likely need to raise the bar significantly going forward if we are going to keep the level of risk from frontier models low. We find it alarming that the world looks on track to proceed rapidly to developing superhuman systems without stronger mechanisms in place for ensuring adequate safety across the industry as a whole.

フロンティアモデルからのリスク水準を低く保つためには，**今後大幅に基準を引き上げる必要がある**だろう．**業界全体で十分な安全性を確保するためのより強力な仕組みが整わないまま，超人的システムの開発へ急速に向かいつつある世界の状況**を，我々は憂慮している．

（続く）
