---
id: "2026-05-12-あのopus-と-opus-1m-contextの3か月後-opus-47-リリースと-anthro-01"
title: "あの「Opus と Opus (1M context)」の3か月後 — Opus 4.7 リリースと Anthropic 公式ポストモーテム"
url: "https://zenn.dev/kimkiyong/articles/7ba6385803a8f3"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "prompt-engineering", "API", "LLM"]
date_published: "2026-05-12"
date_collected: "2026-05-13"
summary_by: "auto-rss"
query: ""
---

> 2026年2月、私は[Claude Code の「Opus」と「Opus (1M context)」は何が違うのか？](https://zenn.dev/kimkiyong/articles/4414db3199a499)という記事を書いた。「1M トークンは銀の弾丸ではない」「MRCR v2 で 256K の 93% から 1M の 76% に劣化する」「GitHub Issue では 78K で compaction が止まり、92点が38点に落ちたという報告がある」— 当時 Opus 4.6 を巡って起きていた現象を整理したものだ。
>
> あれから3か月。Opus 4.7 がリリースされ、Anthropic は公式に「品質劣化」を認め、ベンチマークは差し替えられ、トークナイザーは肥大化し、Claude Code の Code タブから Opus 4.6 は消えた。本記事は、その3か月で何が起きたかの**答え合わせ**である。

---

## 結論を3行で

* 前回記事の核心「**コンテキストは大きいほど良いわけではない**」は、Opus 4.7 でむしろ強化された。MRCR v2 は 1M で 76% → **32.2%** に半減した。
* Anthropic は4月23日のポストモーテムで、Opus 4.6 期間に重なって発生した「effort ダウングレード」「キャッシュバグ」「冗長性抑制プロンプト」の3要因を公式に認めた。前回記事で挙げた**92→38点問題は、ベンチマーク作者の幻覚ではなかった**。
* ただしモデル名・上限・価格・既定設定はすべて書き換わった。Claude Code Desktop の Code タブには「Opus 4.7（実質1M）」一択しか残っていない。

---

## 1. Opus 4.7 リリース — 「同じ Opus 4.6 が2つ並んでいる」世界の終わり

前回記事の冒頭はこう始まっていた。「Claude Code のモデル選択画面には、同じ Opus 4.6 が2つ並んでいる」。この前提は2026年4月16日に終わった。

Anthropic は[Claude Opus 4.7 を発表](https://www.anthropic.com/news/claude-opus-4-7)し、Claude Code の既定モデルに据えた。重要な仕様変更を整理する。

| 項目 | Opus 4.6 (2026/02) | Opus 4.7 (2026/04) |
| --- | --- | --- |
| コンテキスト上限 | 200K / 1M（beta） | **1M（標準）** |
| 出力上限 | 64K | **128K** |
| Claude Code 既定 effort | high → medium → high（変遷あり） | **xhigh**（high と max の中間） |
| Max/Team/Enterprise の挙動 | 申請ベース | **Opus は自動的に1M** |
| トークナイザー | 既存 | **新版（1.0〜1.35倍）** |
| API 価格 | $5 / $25 per MTok | **据え置き** |
| 200K 超のプレミアム料金 | あり ($10 / $37.50) | **あり**（API Console 等で適用） |

つまり、前回記事の「Opus」と「Opus (1M context)」という二択は、**Claude Code 上では存在しなくなった**。Opus 4.6 は[Issue #49689](https://github.com/anthropics/claude-code/issues/49689) の通り Claude Code Desktop の Code タブのモデルピッカーから削除され、現状 Code タブからは Opus 4.6 は呼び出せない。Copilot Pro+ でも段階的に廃止予定だ。

Claude Code には同時に `/ultrareview` という新コマンドが追加され、effort level の既定は xhigh に格上げされている。「高い思考量がコーディング品質に効く」という Anthropic の判断が、設計に反映された格好だ。

---

## 2. MRCR v2 半減事件 — 76% → 32.2% への崩落

前回記事で「劣化曲線」の根拠として最も多く参照したのが、Anthropic 自身が公表した MRCR v2 のスコアだった。Opus 4.6 は 256K で 93%、1M で 76%。「17ポイントの低下だが、競合の Gemini 3 Pro (24.5%) や Sonnet 4.5 (18.5%) と比べれば圧倒的」というのが当時の整理だった。

ところが Opus 4.7 のシステムカードに掲載された MRCR v2 8-needle のスコアは衝撃的だった。

| コンテキスト長 | Opus 4.6 | Opus 4.7 |
| --- | --- | --- |
| 256K | 91.9% | **59.2%** |
| 1M | 78.3% | **32.2%** |

[llm-stats の集計](https://llm-stats.com/blog/research/claude-opus-4-7-launch)や[WentuoAI の検証記事](https://blog.wentuo.ai/en/claude-opus-4-7-long-context-regression-en.html)で広く知られるようになったが、1M では**ほぼ半減**である。前回記事で「8つの針のうち2つを見落とす」と書いた水準が、「ほぼ半分しか見つけられない」に近い水準にまで落ち込んだ。

### Anthropic の弁明と「ベンチマーク差し替え」

この数字に対する Anthropic 側の説明は、要約すると「MRCR は不自然な benchmark だから廃止する」だ。Anthropic の Boris Cherny 氏は X 上で[次のように述べた](https://x.com/scaling01/status/2044823378079400041)。

> MRCR は distractor を積み上げて引っかけるベンチマークで、人々が実際に long context を使う形ではない。GraphWalks の方が応用上の long context reasoning のシグナルとして優れている。

そして実際、GraphWalks では **38.7% → 58.6%** と Opus 4.7 は改善している。さらに Opus 4.7 のシステムカードでは「科学的誠実さのために MRCR も併載している」と言及されており、MRCR から GraphWalks への評価軸シフトが明確に進められている。

しかしコミュニティの反応は手厳しい。[Xlork のレビュー記事](https://xlork.com/blog/claude-opus-4-7-backlash)は「スコアが落ちた直後にベンチマークを差し替えるのは説明として弱い」と批判し、deep research エージェントや RAG パイプラインの構築者からは「我々の用途では MRCR の挙動こそ実態に近い」という反論が相次いだ。

### 何を信じるべきか

前回記事の主張、「**コンテキストは大きいほど良いわけではない**」「**1M は銀の弾丸ではない**」は、Opus 4.7 で**むしろ強化されたと言うべきだろう**。MRCR が「正しい」ベンチマークかどうかとは別に、1M の領域で前世代より精度が下がっているという事実は変わらない。RAG・deep-research・大規模コードベース横断の用途では、**Opus 4.7 への移行は A/B 検証してから判断すべき**というのが現時点の素直な落とし所だ。

---

## 3. 新トークナイザー — 「価格据え置き」の裏で起きた実質値上げ

Opus 4.7 はトークナイザーが刷新された。これは前回記事では存在しなかった論点だ。

[Anthropic 公式ドキュメント](https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-7)は「同じ入力が 1.0〜1.35 倍のトークン数になりうる」と認めている。実測値はさらに上で、[claudecodecamp の計測](https://www.claudecodecamp.com/p/i-measured-claude-4-7-s-new-tokenizer-here-s-what-it-costs-you)では実コンテンツで 1.47 倍、CLAUDE.md ファイルで 1.45 倍と報告された。Simon Willison 氏も[類似の検証](https://simonwillison.net/2026/apr/20/claude-token-counts/)を公開している。

単価は据え置きだが、消費トークン数が増えるため、Pro/Max の利用枠が早く尽きる。「実質12〜18%の値上げ」と評する記事が多く、より厳しい計測では「30〜45%の値上げ」と表現される。Pro サブスクライバーが「3問で利用枠を使い切った」という報告もあり、[The Register](https://www.theregister.com/software/2026/04/23/claude-opus-47-has-turned-into-an-overzealous-query-cop/5225593)や[DnyUz](https://dnyuz.com/2026/04/17/the-claude-lash-is-here-opus-4-7-is-burning-through-tokens-and-some-peoples-patience/)等が大きく取り上げた。

これは前回記事のコスト表を**実質的に書き換える事実**だ。「200K を超えた瞬間にプレミアム料金（入力2倍・出力1.5倍）」は今でも有効だが、それ以前に**毎リクエスト1.1〜1.5倍のトークン消費が乗ってくる**ことを前提に運用設計する必要がある。

---

## 4. サイレント切替バグ — 1M コンテキストの混乱

「Max プランで1Mを使えるようにしてほしい」という前回記事で引用した要望（[Issue #23879](https://github.com/anthropics/claude-code/issues/23879)）は、表面上は叶った。Max/Team/Enterprise では Opus が自動的に1Mに切り替わる仕様になっている。

しかし、そこから新しい地獄が始まった。

### Issue #49541: ~4倍の利用枠焼き切れ

[Issue #49541](https://github.com/anthropics/claude-code/issues/49541) の報告は典型例だ。あるユーザーが Opus 4.6 でセッションを開始したところ、途中で**何の通知もなく** Opus 4.7 [1M] に切り替わった。直後から利用枠の消費が急加速し、5時間枠を30分で使い切った。

* 切り替え前: max 250K 程度のコンテキストで autocompact 動作
* 切り替え後: max 650K 以上に成長、autocompact は200K境界では効かない
* さらに 4.7 のトークナイザーで約 1.35 倍

つまり「サイレントなモデル切替」と「1Mで autocompact が効かない」と「新トークナイザー」が**3つ重なって約4倍の burn rate**になった、というのがこの Issue の本質だ。

### Issue #53031 / #55504 / #53872: 1M なのか 200K なのかわからない問題

さらに、ユーザー側が明示的にモデルを選んでも実際の挙動が一致しない事例が多発している。

**UI 表示、実際の上限、課金カウントの三者が一致しない**状態が、5月時点でも複数 Issue として開いたままだ。前回記事で取り上げた「`/context` が 200K と表示される」（[Issue #23432](https://github.com/anthropics/claude-code/issues/23432)）の系譜は、形を変えて生き残っている。

### Compaction 周りの新顔

前回記事の核として参照した [Issue #23751](https://github.com/anthropics/claude-code/issues/23751)（78Kで compaction 失敗）は、Issue #2038 の重複として close された。要約用モデル側のコンテキスト制約という原因も認識されており、Claude Code 側では autocompact thrash ループ検出などの改善は入っている。

しかし、後継の Issue が次々と立っている。

そして、前回記事で取り上げた[Issue #23711](https://github.com/anthropics/claude-code/issues/23711)（compaction 閾値の設定可能化）は duplicate で close されたが、**未だ実装されていない**。後継要望（[#41818](https://github.com/anthropics/claude-code/issues/41818)・[#46695](https://github.com/anthropics/claude-code/issues/46695)・[#34925](https://github.com/anthropics/claude-code/issues/34925)・[#34202](https://github.com/anthropics/claude-code/issues/34202)）が積み上がっている。PreCompact hook で「ブロック」はできるようになったが、「閾値を変える」ことはまだできない。

---

## 5. Anthropic 公式ポストモーテム — 92→38 は幻覚ではなかった

前回記事で最も衝撃的だった引用は [Issue #24991](https://github.com/anthropics/claude-code/issues/24991) の「Opus 4.6 のスコアが2月10〜11日頃に92点から38点へ落ちた」だった。同じモデル ID で挙動が変わる不可解な現象だ。

その答えが3月にも4月初頭にもないまま、コミュニティでは「Anthropic がこっそりモデルを量子化したのでは」「サンプラーをいじったのでは」という疑念が膨らんでいった。そして2026年4月23日、Anthropic は[An update on recent Claude Code quality reports](https://www.anthropic.com/engineering/april-23-postmortem)を公開し、**3つの独立した変更が重なって品質劣化を引き起こしていた**ことを認めた。

### 原因1: Reasoning effort のダウングレード（3/4〜4/7）

Opus 4.6 リリース時、Claude Code の既定 effort は high だった。しかし「思考が長すぎて UI が固まって見える」「latency とトークン消費が不均衡」というフィードバックを受け、**3月4日に既定を high → medium に下げた**。これが思考量の不足を招き、品質が落ちた。

4月7日に逆戻しが行われ、現在は Opus 4.7 については xhigh、それ以外は high が既定となっている。

### 原因2: キャッシュバグ（3/26〜4/10）

「1時間以上アイドルだったセッションの古い thinking blocks をクリアする」という変更を3月26日にデプロイしたところ、バグで**毎ターン削除**するようになってしまった。結果、Claude は同じ会話の中で文脈を失い続け、「物忘れ」「同じ間違いの反復」「自分勝手な判断」が出現した。**前回記事で引用した Issue #24437・#25067・#26533 等の「指示を忘れる」系の報告の多くはこのバグで説明がつく**。4月10日に修正された。

### 原因3: 冗長性抑制プロンプト（4/16〜4/20）

Opus 4.7 リリース日に「冗長性を抑える」システムプロンプトを追加したところ、他の変更と組み合わさってコーディング品質が低下した。4月20日に revert され、v2.1.116 で完全に解消された。4月23日には全サブスクライバーの利用枠がリセットされている。

### 含意

これは前回記事の主張を**裏付けたと同時に修正もした**事件だ。

* 裏付け: 「同じモデル ID でも実行環境の違いで大幅に性能が変わる」という指摘は完全に正しかった。Issue #24991 の作者は幻覚を見ていたわけではない。
* 修正: 「コンテキスト長の問題ではない」という前回記事の慎重な但し書きも正しかった。原因は effort・キャッシュ・プロンプトの3つで、コンテキスト長劣化とは独立だった。

[VentureBeat](https://venturebeat.com/technology/mystery-solved-anthropic-reveals-changes-to-claudes-harnesses-and-operating-instructions-likely-caused-degradation) や [Fortune](https://fortune.com/2026/04/24/anthropic-engineering-missteps-claude-code-performance-decline-user-backlash/) が大きく取り上げ、AI ベンダーの「harness 変更」のリスクが業界共通の論点に格上げされた事件でもある。

---

## 6. Opus 4.7 固有の挙動 — "Overzealous Query Cop"

ポストモーテムで4.6 期間の問題は片付いたが、4.7 には **4.7 固有の新しい問題**が出ている。

### 過剰なセーフガードと「拒否癖」

[The Register が "overzealous query cop" と評した](https://www.theregister.com/software/2026/04/23/claude-opus-47-has-turned-into-an-overzealous-query-cop/5225593)挙動が代表的だ。「HTML をパースしてくれ」と頼んだら「これは malware の解析ではないか」と疑って拒否する、といった事例が[Hacker News](https://news.ycombinator.com/item?id=47814832)で広く話題になった。

背景には、後述する **Mythos Preview** の存在がある。Anthropic は Opus 4.7 を「Mythos より弱いがセーフガードを強めた版」として出荷しており、サイバー関連の prompt パターンには敏感に反応する設計になっている。問題は、その判定が広めにかかっていて、健全なタスクまで巻き込んでいる点だ。

### 「指示を文字通り解釈する」副作用

[Anthropic 公式の「Best practices for Opus 4.7」](https://claude.com/blog/best-practices-for-using-claude-opus-4-7-with-claude-code)は、はっきりこう書いている。

> Opus 4.7 interprets instructions more literally than 4.6, meaning prompts relying on the model to fill in context now underperform.

これは大きな転換だ。Opus 4.6 までは「行間を読んで埋めてくれる」傾向だったが、4.7 は「書かれた通りにだけ動く」方向にチューニングされた。結果、**Opus 4.6 用にチューニングしたプロンプトは4.7 でむしろ品質を落とす**。

[Issue #50235](https://github.com/anthropics/claude-code/issues/50235) のハルシネーション報告、[Issue #54817](https://github.com/anthropics/claude-code/issues/54817) のプロジェクトコンテキスト喪失、「指摘されてもバグを認めず元のコードを擁護する」といった報告は、この「文字通り解釈」の副作用と読める。

### 個別 Issue で見る5月の状況

| Issue | 内容 | 状態 |
| --- | --- | --- |
| [#56356](https://github.com/anthropics/claude-code/issues/56356) | Opus 4.7 が thinking blocks を返さない（v2.1.128） | 5/5 open |
| [#57315](https://github.com/anthropics/claude-code/issues/57315) | v2.1.133 で MCP ツールがモデルに公開されない | 5/8 open |
| [#55584](https://github.com/anthropics/claude-code/issues/55584) | Sonnet 4.6 の1M版が Desktop に出ない | 5/2 open（duplicate） |
| [#52534](https://github.com/anthropics/claude-code/issues/52534) | Opus 4.7 が `CLAUDE_CODE_EFFORT_LEVEL` を無視 | open |

「同じモデル ID で挙動が変わる」系の報告は形を変えて続いている、というのが正直なところだ。

---

## 7. Mythos Preview — 「上位モデル」の影

前回記事には登場しなかったが、3か月の間に Anthropic は **Mythos Preview** という新クラスのモデルの存在を公開した（[red.anthropic.com](https://red.anthropic.com/2026/mythos-preview/)）。

Mythos は一般提供されておらず、**Project Glasswing** という枠組みで Amazon・Apple・Microsoft・Cisco・Linux Foundation 等にゲート付きで配布されている。サイバーセキュリティに極めて強く、Anthropic 自身が「主要 OS と主要ブラウザに対して数千件のゼロデイ脆弱性を発見できた」と発表したことで世間に知られるようになった（[TechCrunch](https://techcrunch.com/2026/04/07/anthropic-mythos-ai-model-preview-security/)）。

Opus 4.7 のシステムカードは「Mythos のサイバー能力には届かないが、セーフガードを強めた」と明記している。前述の「拒否癖」「過剰な malware 警戒」はここに源流がある。

直接 Claude Code で使えるモデルではないが、**Opus 4.7 の挙動を読み解く文脈として無視できない存在**になっている。

---

## 8. プロンプト戦略はどう変わるべきか

前回記事の「実践的ガイドライン」は3か月で書き換えが必要だ。

### 古いガイドライン（前回）と新しいガイドライン

| 観点 | 前回記事（2026/02） | 現在（2026/05） |
| --- | --- | --- |
| 主役モデル | Opus 4.6 | **Opus 4.7（既定）** |
| 既定 effort | 不明確 | **xhigh** |
| 「Opus か Opus (1M)」 | 二択で選ぶ | **1Mが既定、UIから 200K を選べない場面が多い** |
| 50% ルール | 200Kの50〜60% | **1M の30〜40%（300〜400K）が体感** |
| プロンプトの作り方 | 簡潔 + 文脈に頼る | **意図・成功条件・制約を明示的に書く** |
| 価格モデル | 200K境界で2倍 | **境界は同じだが、トークナイザーで実質1.1〜1.5倍** |

### 今の Opus 4.7 で効くプロンプト書法

公式の Best Practices は要するに「**人間のエンジニアに依頼するように書け**」だ。曖昧さに頼って Claude が推測してくれることを期待するのではなく、最初のターンで完全な仕様を渡す。サブエージェントを使うなら「ファイル全体を最初に読め」と明示する。Adaptive Thinking を増やしたいなら「これは見た目以上に難しい問題だ。step by step で考えてから答えよ」と直接書く。

前回記事で触れた「`opusplan`」エイリアス（計画は Opus、実装は Sonnet）は今も有効で、コスト最適化の手段としてむしろ重要性が増している。Effort Level は xhigh が既定で、`low / medium / high / xhigh / max` の5段階に進化した。

---

## 9. 「劣化開始点」は 300〜400K へ前倒し

前回記事では「コミュニティ経験則の50%ルール」を紹介した。これは1Mモードで500〜600Kあたりが劣化開始点という見立てだった。

3か月後の現状では、コミュニティの感覚は**もう少し早い側に寄った**ように見える。[Mejba Ahmed 氏の解説](https://www.mejba.me/blog/claude-code-1m-context-management)は「Claude Code では 300〜400K（1Mの30〜40%）から context rot を感じる」と述べ、複数のブログが同水準を引いている。これは Opus 4.7 の MRCR 半減とも整合する。

Chroma Research 自身は[MLOps Community で「Opus 4.7 を対象とした context rot の続報研究は予定していない」](https://home.mlops.community/public/videos/context-rot-reading-group)と発言している。つまり**独立した検証は依然として薄い**状態が続いており、現時点では「Anthropic の公式数字 + ユーザー体感」しか手がかりがない。この状況は3か月前と変わらない。

ベンチマーク値ではなく「自分のタスクで劣化開始点を測る」という姿勢は、前回より重要になったと言える。

---

## 10. まとめ — コンテキストエンジニアリングの第二章

3か月前の記事は、「1Mが使えるようになった世界で、それでも 1M を埋めないことが大切」というメッセージで締めた。これは今でも有効だ。むしろ、**Opus 4.7・新トークナイザー・MRCR半減・サイレント切替バグの組み合わせで、その重要性は数段上がった**。

しかし「コンテキストエンジニアリング」の意味合いは、3か月で変わった。

* **3か月前**: 「**量を絞る**」が主題だった。1Mあるからといって 1M 詰めない。compaction を意識する。
* **現在**: 「**曖昧さを絞る**」も同等以上に重要になった。Opus 4.7 は文字通り解釈するので、行間に頼ったプロンプトは劣化する。意図・成功条件・制約を明示的に書く。

そして、**モデル名・上限・価格・既定設定はすべて変動する**ということも忘れてはいけない。4月23日のポストモーテムが示したように、harness の小さな変更が品質を大きく動かす。Anthropic は今後も同じことをやる可能性があるし、それは Anthropic に限らず全 AI ベンダーに共通の構造的リスクだ。

前回記事に寄せた「**1M トークンは銀の弾丸ではない**」というタイトル的結論は、3か月後の世界では「**どの数字も、どのモデル名も、どのベンチマークも、銀の弾丸ではない**」と一般化されたとも言える。手元のタスクで A/B し、コストと品質のトレードオフを自分で測る、という地味な作業に立ち返るしかない。

そして、**前回記事を読み返したい人へ**。当時のスナップショットとして読む分には今も意味があるが、固有名詞（Opus 4.6, MRCR スコア 76%, autocompact の挙動）は本記事の数字で置き換えて読んでほしい。それが3か月でこの分野が動いた距離だ。

---

## 本記事の情報源（2026/05/12時点）

### Anthropic 公式

### ベンチマーク・分析

### 報道

### GitHub Issues（anthropics/claude-code）

### 前回記事
