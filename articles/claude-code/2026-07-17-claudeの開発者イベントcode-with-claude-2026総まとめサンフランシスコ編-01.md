---
id: "2026-07-17-claudeの開発者イベントcode-with-claude-2026総まとめサンフランシスコ編-01"
title: "Claudeの開発者イベント「Code with Claude 2026」総まとめ〜サンフランシスコ編〜"
url: "https://zenn.dev/galirage/articles/code-with-claude-2026-sf-summary"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "cowork", "zenn"]
date_published: "2026-07-17"
date_collected: "2026-07-18"
summary_by: "auto-rss"
query: ""
---

はじめまして、ますみです！

[株式会社Galirage（ガリレージ）](https://bit.ly/galirage_homepage_zenn_intro)というAIスタートアップで、代表をしております^^

その他にも、「[AIとコミュニケーションする技術（インプレス出版）](https://bit.ly/amazon_book_ai_communication_skill_from_zenn_inside_body)」という書籍を執筆させていただいたり、[生成AIアカデミー](https://bit.ly/youtube_masumi_engineer_zenn_intro)というYouTubeチャンネルを運営したり、上智大学で非常勤講師をしたりしています！

[![自己紹介.png](https://res.cloudinary.com/zenn/image/fetch/s--9tzCxv3U--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://storage.googleapis.com/zenn-contents/images/intro/introduction_banner.png?_a=BACMTiAE)](https://bit.ly/banner_intro_masumi_creator_zenn)  
今回は、2026年5月6日にサンフランシスコで開催されたAnthropicの開発者カンファレンス **「Code with Claude 2026 サンフランシスコ編」** の内容をまとめてご紹介します！

「ClaudeとClaude Codeを実開発でどう使うか」をテーマに、Anthropicの最新機能発表からCursor・Replit・Asanaなど先行企業の実事例まで、全19セッションが公開された濃密なカンファレンスでした。

現地に行けなかった方や、動画を1本ずつ見る時間はないけど要点だけ押さえたいという方に向けて、全セッションの内容を1つの記事にまとめました。情報量が多いため、各セッションごとに **サマリ** も用意しています。お忙しい方は、まずサマリだけでも目を通してみてください！

## Code with Claudeとは？

**Code with Claude**は、Anthropicが主催するソフトウェアエンジニア向けカンファレンスです。AnthropicのエンジニアからClaude・Claude Codeの設計思想や最新APIが発表されるほか、Claudeをすでに実プロダクトで活用しているパートナー企業の登壇も多く、設計上の判断や試行錯誤を実例ベースで知ることができます。

**Code with Claude 2026** は、サンフランシスコ・ロンドン・東京の3都市で順次開催されます。

* **サンフランシスコ編**：2026年5月6日（水）← 本記事
* **ロンドン編**：2026年5月19日（月）
* **東京編**：2026年6月10日（火）

本記事では **サンフランシスコ編（5月6日）** の全19セッションをまとめています。

ロンドン編はこちらにまとめていますので、ぜひ併せてご覧ください！

<https://zenn.dev/galirage/articles/code-with-claude-2026-london-summary>

## サンフランシスコ編の全セッション一覧

| # | セッション名 | 登壇者 | 概要 | 動画 |
| --- | --- | --- | --- | --- |
| 1 | Opening Keynote | Ami Vora（CPO）ほか Anthropic | Managed Agentsの発表を中心に、自動化・コードレビュー・エージェント設計パターンなどを幅広く紹介した基調講演。 | [▶](https://www.youtube.com/watch?v=GMIWm5y90xA) |
| 2 | What's new in Claude Code | Dickson Tsai（Anthropic） | リモート制御・Gitワークツリー・デスクトップ操作など、Claude Codeに追加された最新機能を網羅的に紹介。 | [▶](https://www.youtube.com/watch?v=IMZa42k6L6M) |
| 3 | Memory and dreaming for self-learning agents | Mahesh Murag（Anthropic） | エージェントの永続メモリとバックグラウンド非同期処理（Dreaming）を深掘り。Harvey・楽天（Rakuten）の導入実績も交えて解説。 | [▶](https://www.youtube.com/watch?v=RtywqDFBYnQ) |
| 4 | Caching, harnesses, and advisors: Building on Claude at GitHub scale | Mario Rodriguez + Brad Abrams（Anthropic） | キャッシュ最適化・ハーネス設計・アドバイザーパターンなど、本番AIシステムを支える3つの設計パターンを解説。 | [▶](https://www.youtube.com/watch?v=y5TmF_6o6xk) |
| 5 | The expanding toolkit | Lucas Gonzalez（Anthropic） | モデルを補うための制御コードがモデル自身に吸収されつつあるというテーマのもと、コンピュータ操作・コンテキスト管理などの最新ツールを紹介。 | [▶](https://www.youtube.com/watch?v=KLCuxMDZSDg) |
| 6 | How to get to production faster with Claude Managed Agents | Jess Yan + Lance Martin（Anthropic） | 「ボトルネックは知能ではなくインフラ」を軸に、本番環境での安定稼働に必要な隔離実行・状態保存・権限管理を解説。 | [▶](https://www.youtube.com/watch?v=E9gaQHrw_rg) |
| 7 | A conversation with Dario & Daniela Amodei | Dario Amodei（CEO） + Daniela Amodei（President） | 計画比80倍の成長実績と今後の展望を、DarioとDanielaが率直に語った対談。 | [▶](https://www.youtube.com/watch?v=7xco5Qd2Oo8) |
| 8 | Live coding session with Boris Cherny & Jarred Sumner | Boris Cherny（Head of Claude Code） + Jarred Sumner（Creator of Bun） | Bunのバグをエージェントが自律修正してプルリクエストまで完結させる「Robobun」を披露したライブデモ。 | [▶](https://www.youtube.com/watch?v=DlTCu_pNDHE) |
| 9 | Building with Claude Managed Agents and Asana AI teammates | Arnab Bose（Asana VP, Vice President of Product） | 21種類のAIチームメイトによるプロジェクト管理を中心に、メモリ共有・権限管理・成果検証の設計を語ったAsanaの実例。 | [▶](https://www.youtube.com/watch?v=BrpB-h1e--k) |
| 10 | Running an AI-native engineering org | Fiona Fung（Anthropic） | ボトルネックの移動・JIT計画・フラット組織など、AI活用で変化したAnthropicのエンジニアリング組織設計を語った。 | [▶](https://www.youtube.com/watch?v=igO8iyca2_g) |
| 11 | Building AI-native: Inside the stacks powering Cognition, Gamma, and Harvey | Walden Yan（Cognition） + Deeni Fatiha（Gamma） + Niko Grupen（Harvey） | モデルの大きな進化がアーキテクチャ書き直しのきっかけになるという経験を、Cognition・Gamma・Harveyの3社が語ったパネル。 | [▶](https://www.youtube.com/watch?v=OFDm3T7pVlc) |
| 12 | How Vercel Builds for Model Step-Changes: A Tactical Playbook | Guillermo Rauch（Vercel CEO） | 上位モデルがコストの70%超を占めるという経済設計の課題とともに、Vercel v0でのモデル進化への対応戦略を語った。 | [▶](https://www.youtube.com/watch?v=bJKdXhnw7NU) |
| 13 | The thinking lever | Matt Bleifer（Anthropic PM） | 推論量を5段階で調整する方法を解説し、思考の自律調整・トークン上限設定という2つの新機能を発表。 | [▶](https://www.youtube.com/watch?v=OXJO4LldSnc) |
| 14 | How Datadog built a universal machine tool for Claude Code | Sesh Nalla（Datadog VP of Engineering） | 導入4ヶ月でエンジニアの90%が採用したClaude Code活用事例と、ツール乱立を解決する「Temper」フレームワークの設計思想を語ったDatadogの事例。 | [▶](https://www.youtube.com/watch?v=EdmuYPBt_EM) |
| 15 | Building with Claude on Google Cloud | Ivan Nardini（Google Cloud） | 3つのエージェントを並列で動かしながら、30分以内にアプリを本番デプロイするライブデモ。 | [▶](https://www.youtube.com/watch?v=SqHsS737CeA) |
| 16 | Getting more out of the Claude Platform | Brad Abrams（Anthropic） | キャッシュ活用・遅延読み込み・会話圧縮・アドバイザーパターンなど、APIのコストと精度を最適化する4つのパターンを解説。 | [▶](https://www.youtube.com/watch?v=7oO37GRhwGk) |
| 17 | Evaluating and improving Replit Agent at scale | Michele Catasta（Replit） + Hannah Moran（Anthropic） | バイブコーディング専用ベンチマーク「ViBench」を正式公開し、失敗の自動分類から修正・リリースまでを回す継続的な改善ループも紹介。 | [▶](https://www.youtube.com/watch?v=snroDwX1-JU) |
| 18 | The capability curve | Alex Albert（Anthropic MTS, Member of Technical Staff） | 1年でSWEベンチマークが62%→87%に向上したモデルの進化曲線を提示。未来のモデルを前提にアーキテクチャを設計することを促したクロージング。 | [▶](https://www.youtube.com/watch?v=tP4MGcJ80Y0) |
| 19 | Giving coding agents their own computers: How Cursor built cloud agents | Alexi Robbins（Cursor） | エージェントが自ら問題を報告・分類・修正する自己改善ループを軸に、Cursor Cloud Agentsの設計と実績を語ったCursorの事例。 | [▶](https://www.youtube.com/watch?v=BbYSGxtsMic) |

ここからは各セッションの内容を順番に見ていきます。

---

## セッション1：Opening Keynote

<https://www.youtube.com/watch?v=GMIWm5y90xA>

**登壇者**：Ami Vora（CPO、Chief Product Officer）、Dianne Penn、Angela Jiang、Katelyn Lesse、Cat Wu、Boris Cherny

基調講演ではまず、**Claude APIの利用が前年比17倍に成長した**ことが公表されました。

セッションを通じて繰り返されたのは「コードを書く量を増やすことが目標ではなく、成し遂げる量を増やすことが目標だ」というメッセージです。AIで生産性を測る指標を「書いた行数」ではなく「届けた価値」に置き換える、という姿勢が随所に表れていました。

発表されたClaude APIの主な新機能・新コンセプトは以下のとおりです。

* **Routines**：繰り返しワークフローの自動化機能
* **Code Review**：PR差分の自動レビュー機能
* **Managed Agents**：3つのコア能力として「Dreaming（非同期バッチ処理）」「[マルチエージェント](https://zenn.dev/umi_mori/books/generative-ai-glossary/viewer/what-is-multi-agent)オーケストレーション」「Outcomes（目標・制約の宣言）」を発表
* **Advisor Strategy**：小モデルが通常タスクを処理し、難しいケースのみ大モデルに委ねる設計パターン

Managed Agentsは、エージェントをチャットツールの延長ではなくサーバーやデータベースと同じように「インフラ」として扱うコンセプトです。人間が逐一指示しなくても、タスクを自律的にこなす存在として設計されています。

![Opening Keynoteの4つの主要発表](https://static.zenn.studio/user-upload/deployed-images/1ab7bed1af69f723c09f2c3b.png?sha=30e442dbecbfa6059d42064aae6120a0369e5e02)  
*Opening Keynoteの4つの主要発表 — Routines・Code Review・Managed Agents・Advisor Strategyという2026年の柱が一度に出揃った*

!

**サマリ**

* カンファレンス全体の方向性を示す基調講演
* 後続セッションで深掘りされるManaged Agents・Advisor Strategy・Routines・Code Reviewがまとめて登場

---

## セッション2：What's new in Claude Code

<https://www.youtube.com/watch?v=IMZa42k6L6M>

**登壇者**：Dickson Tsai（Anthropic）

Claude Codeの最新機能を網羅的に紹介したセッションです。  
特に注目は **Remote Control Mode**。ローカルのClaude Codeを外部サービスや自動化パイプラインからリモート制御できる機能で、CIパイプラインや定期実行ジョブからClaude Codeを呼び出すといった使い方が可能になります。開発者が手動で操作しなくても、外部トリガーに応じてClaude Codeが自律的に動作する仕組みです。

その他に発表された主な新機能は以下のとおりです。

* **デスクトップGUI操作**：ブラウザやデスクトップアプリの自律操作
* **Git worktrees**：複数の独立した作業環境を並列管理
* **メモリ管理**：より長期的なコンテキスト保持
* **Auto mode安全機能**：強力な自律実行モードに対する[ガードレール](https://zenn.dev/umi_mori/books/generative-ai-glossary/viewer/what-is-guardrail)

全体を通じて「Claude Codeは開発者のレバレッジを高めるために設計されている」というメッセージが繰り返されました。

!

**サマリ**

* Claude Codeに追加された新機能をまとめて紹介するアップデート報告
* 最大の目玉は、CIや外部システムからClaude Codeを自律動作させられるRemote Control Mode

---

## セッション3：Memory and dreaming for self-learning agents

<https://www.youtube.com/watch?v=RtywqDFBYnQ>

**登壇者**：Mahesh Murag（Anthropic）

**Memory API**と**Dreaming**という2つのコア機能を深掘りしたセッションです。

Memory APIはファイルシステム的な設計思想で、エージェントが情報を**書き込み・読み取り・バージョン管理**できる仕組みです。  
楽観的並行制御によりマルチエージェントでの安全な並列アクセスを実現しています。

Dreamingはエージェントが**バックグラウンドで非同期処理**を行う機能です。  
ユーザーが待たなくていい設計で、計算集約的なタスクをオフラインで実行します。

実績として紹介されたのは以下の2社です。

* **Harvey**：Dreamingの導入でタスク完了率が **6倍**に向上
* **楽天（Rakuten）**：Memory APIの導入で重大エラーが **97%削減**（[公式情報](https://claude.com/customers/rakuten)）

Memory APIは独立したAPIとしてスタンドアロンで利用可能です。

![Memory APIとDreaming — エージェントの2つの新基盤](https://static.zenn.studio/user-upload/deployed-images/e799e054b95254fffa59341f.png?sha=ebcd1b86d04e5fada10e693edfb32baa90a70bdb)  
*Memory APIとDreaming — 長期記憶と非同期実行をそれぞれ独立したAPIとして提供する2機能*

!

**サマリ**

* エージェントの長期記憶（Memory API）と非同期実行（Dreaming）を技術的に深掘りしたセッション
* Harvey（タスク完了率6倍）・楽天（Rakuten）（重大エラー97%削減）という2社の導入実績も具体的に示される

---

## セッション4：Caching, harnesses, and advisors: Building on Claude at GitHub scale

<https://www.youtube.com/watch?v=y5TmF_6o6xk>

**登壇者**：Mario Rodriguez + Brad Abrams（Anthropic）

GitHubスケールのClaude活用を題材に、本番AIシステムのコスト・精度・信頼性を同時に最適化する3つの設計パターンを解説したセッションです。

* **プロンプトキャッシング**：同じプロンプトの先頭部分を再利用することでAPIコストを大幅に削減できる手法。高いキャッシュヒット率を維持することがコスト削減の鍵です。
* **Harness（制御コードの枠組み）設計**：エージェントを動かすための周辺コードの設計方法。モデル単体では対応できない状態管理やエラー処理を適切に補うことで、モデルの能力を最大限に引き出せます。
* **Advisor Strategy**：通常タスクは軽量な小モデルが処理し、判断が難しいケースだけ高精度な大モデルに相談する役割分担パターン。「Opusクラスの精度を低コストで実現できる」というのが核心です。

さらに、**Rubber Duckパターン**も紹介されました。問題を他者に説明することで思考が整理される「ラバーダック効果」を応用したもので、エージェントが自分の計画や実装を適切なタイミングで自己レビューする仕組みです。見落としやバグを早期に発見する効果があります。

!

**サマリ**

* GitHubでのClaude本番運用の知見を、Anthropicの解説とあわせて紹介する事例セッション
* 本番AIシステムを支える3つの設計パターン（プロンプトキャッシング・Harness・Advisor Strategy）に踏み込んだ内容

---

<https://www.youtube.com/watch?v=KLCuxMDZSDg>

**登壇者**：Lucas Gonzalez（Anthropic）

Claude APIの最新ツール群を紹介したセッションです。 **「モデルを補うための制御コードが、モデル自身の中に移動した」** がキーメッセージです。

以前はモデルが不得意なことを補うために、ツール選択のルーターや複雑な制御コードを開発者が自前で書く必要がありました。しかしモデルの進化により、その多くをモデル自身が担えるようになっています。モデルが更新されるたびに、前のバージョンで必要だったワークアラウンドが次々と不要になっていくのです。

具体的に紹介された機能は以下のとおりです。

* **ツール選択の自律化**：ルーターなしでモデルが状況に応じてツールを自律選択
* **コンテキスト管理**：100万トークンの一括管理＋長い会話をサーバー側で自動圧縮
* **コード実行ツール**：単一のAPIターンでコードを実行して結果まで取得
* **Computer Use（Opus 4.7）**：ネイティブ1440p対応、コンピュータ操作ベンチマークで**78%達成**

!

**サマリ**

* モデル進化にあわせてAPIに追加された新ツールを俯瞰するセッション
* 「モデルを補うために書いていた制御コードが、モデル自身に取り込まれていく」という流れと、それを裏付ける個別アップデート（コンテキスト管理・Computer Useなど）に注目した内容

---

## セッション6：How to get to production faster with Claude Managed Agents

<https://www.youtube.com/watch?v=E9gaQHrw_rg>

**登壇者**：Jess Yan + Lance Martin（Anthropic）

本番で動くエージェントを素早くリリースするための実践知見を共有したセッションです。

「エージェントの本番化で詰まる原因は、モデルの能力ではなくその周辺インフラにある」と登壇者は指摘します。安全な実行環境の構築・状態管理・権限設計・モデル更新のたびの設計見直しといったインフラ対応に、多くの開発工数が取られがちです。Managed Agentsはそのインフラ部分を肩代わりし、開発者がエージェントのロジックに集中できる環境を提供します。

Managed Agentsが提供する主な機能は以下の3つです。

* **サンドボックス実行**：安全にコードを実行できる隔離環境をマネージドで提供。セキュリティ設計を自前で実装する必要がなくなる
* **チェックポイント**：長時間タスクの途中状態を保存し、失敗・再起動後の回復を確保。リカバリーロジックを自前で書くコストが減る
* **権限スコーピング**：エージェントに与えるアクセス権を細かく制御し、最小権限の原則をシステムレベルで実現

![Managed Agentsが肩代わりする3つの本番化基盤](https://static.zenn.studio/user-upload/deployed-images/40ad81c615f8b00c669cead0.png?sha=54147471a0ee77f45df8d2960caf3ba9023f1cf4)  
*Managed Agentsが肩代わりする3つの本番化基盤 — サンドボックス・チェックポイント・権限スコーピングを自前で組まずに済む*

!

**サマリ**

* 「本番でエージェントを安定稼働させるには」をテーマにした実装解説のセッション
* サンドボックス・状態管理・権限スコーピングといったインフラ部分をManaged Agentsがどう肩代わりするかについて解説

---

## セッション7：A conversation with Dario & Daniela Amodei

<https://www.youtube.com/watch?v=7xco5Qd2Oo8>

**登壇者**：Ami Vora（CPO、モデレーター）+ Dario Amodei（CEO）+ Daniela Amodei（President）

Anthropicの共同創業者による対談セッションです。  
**Anthropicの急成長**の実態と今後の展望が率直に語られました。

注目すべき数字は以下のとおりです。

* 年間収益ランレート：2024年1月の **8,700万ドル** → 2026年4月 **300億ドル**
* 成長率：計画10倍のところ実績は **80倍**
* この需要に対応するため、xAIが運営する **Colossusデータセンター**（Memphis）との容量提携を発表

Danielaは **「開発者はClaudeにとって最も重要なユーザーだ」** と明言しました。

Darioは、1年前に語った予測「2026年に一人で運営する十億ドル企業が生まれる」の現状に触れ、「まだ実現していないが残り7ヶ月ある」とコメントしました。また、「モデルは指数関数的に改善し続けるので、以前のモデルで失敗したユースケースを新しいモデルで定期的に試し直してほしい」と開発者に呼びかけました。

!

**サマリ**

* AnthropicのDario（CEO）・Daniela（President）に、CPOのAmi Voraがインタビューする対談セッション
* 計画比80倍の事業成長、xAI Colossusとの容量提携、「一人十億ドル企業」の将来予測など、経営目線の話題が中心

---

## セッション8：Live coding session with Boris Cherny & Jarred Sumner

<https://www.youtube.com/watch?v=DlTCu_pNDHE>

**登壇者**：Boris Cherny（Head of Claude Code）+ Jarred Sumner（Creator of Bun）

Claude Codeチームが実際の日常ワークフローをライブで披露したセッションです。

最大の見どころは **「Robobun」** の紹介。  
BunのissueをClaudeが自律的に再現し、回帰テストがパスしたタイミングでPR作成まで完結させるコーディングエージェントです。

Robobunによって、Bunのバグ修正やPR作成の多くがAIによって自動化されています。

!

**サマリ**

* Claude Code責任者のBorisと、Bun作者のJarredによるライブコーディングセッション
* BunのバグをAIが自律修正する「Robobun」のライブデモを中心に、Claude CodeチームのリアルなAI活用ワークフローを公開

---

## セッション9：Building with Claude Managed Agents and Asana AI teammates

<https://www.youtube.com/watch?v=BrpB-h1e--k>

**登壇者**：Arnab Bose（Asana VP of Product）

AsanaがClaude Managed Agentsを使ってAIチームメイト機能を本番導入した事例を紹介したセッションです。

Arnab Boseが問題提起したのは「ほとんどの企業は[AIエージェント](https://zenn.dev/umi_mori/books/generative-ai-glossary/viewer/what-is-ai-agent)を個人が使って結果を渡すだけの**シングルプレイヤーモード**にとどまっている」という現実です。Asanaが目指すのはAIを本当のチームメンバーとして扱う**フルマルチプレイヤーモード**。組織のコンテキストをエージェントが把握し、複数人と協力しながら仕事を進める設計で、2026年3月に**21種類のAIチームメイト**を正式提供しました。

デモでは、マーケターがキャンペーンブリーフとランディングページのモックアップ作成をエージェントに依頼。「プライマリーカラーを青にして」とコメントすると修正が反映され、その学習が次のユーザーにも引き継がれます。やり取りはすべてAsana上に記録され、そのまま承認フローにも使えます。

![シングルプレイヤー → フルマルチプレイヤーモード](https://static.zenn.studio/user-upload/deployed-images/e4c6791c955498bed86887aa.png?sha=78cd0ab4fb1fdf0f7c382f9fec812022a8bfaf90)  
*シングルプレイヤー → フルマルチプレイヤーモード — AIを個人ツールから組織のチームメイトへ昇格させる発想*

!

**サマリ**

* SaaSプロダクトにAIエージェントを本番導入したAsanaの事例セッション
* タスク割り当て・メモリ共有・権限管理など、21種類のAIチームメイトを実際に機能させるための設計判断を具体的に語った内容

---

## セッション10：Running an AI-native engineering org

<https://www.youtube.com/watch?v=igO8iyca2_g>

**登壇者**：Fiona Fung（Manager of the Claude Code and Cowork Team, Anthropic）

AIを前提に設計されたエンジニアリング組織の作り方を、Claude CodeチームのFiona Fungが実体験をもとに語ったセッションです。モデルの使い方だけでなく、チームのプロセスや組織設計の見直しまで踏み込んだ内容でした。

セッションを通じて語られたのは「ボトルネックの移動」についてでした。Claude Codeチームではコーディング自体のスピードはもはや問題ではなく、コードレビュー・検証・セキュリティがボトルネックになっています。

Fionaが紹介した主な取り組みは以下のとおりです。

* **コードレビューの役割分担**：スタイル・lint・テスト追加はClaudeに任せ、人間は法務・セキュリティ・製品としての判断が必要な箇所だけレビューする
* **設計ドキュメントの廃止**：事前に詳細な設計書を書く慣習をやめ、まずPRやプロトタイプを作って議論する「ジャストインタイム計画」に移行
* **技術的な議論はコードで決着**：「どちらの実装が良いか」という議論はホワイトボードではなく、両方のPRを実際に生成して比較する
* **採用基準の変化**：コードを大量に書ける人よりも、製品センスのあるビルダーやシステムの深い専門知識を持つ人を重視するようになった
* **古いプロセスを捨てる許可**：プロセスは放置すると積み上がるだけで自然には消えない。チーム全員に「意味がなくなったプロセスを廃止する明示的な許可」を与えている

![AI導入後、ボトルネックは下流に移動する](https://static.zenn.studio/user-upload/deployed-images/27a82d0f88639170f9811349.png?sha=b9651f41052c42fd6278dd4ec570f5fb32bbbf92)  
*ボトルネックの移動 — AIでコーディングが速くなった結果、開発の詰まりはレビューや検証など下流工程に移った*

!

**サマリ**

* Claude Codeチーム自身がどう開発しているかを語る、組織運営寄りのセッション
* モデルの使い方そのものよりも、チームのプロセスや採用基準、組織設計の見直しが主な話題

---

## セッション11：Building AI-native: Inside the stacks powering Cognition, Gamma, and Harvey

<https://www.youtube.com/watch?v=OFDm3T7pVlc>

**登壇者**：Beth Robertson（Anthropic、モデレーター）+ Walden Yan（Cognition Co-founder）+ Deeni Fatiha（Gamma Head of Product for AI）+ Niko Grupen（Harvey Head of Applied AI）

Cognition・Gamma・Harveyの3社が、AI製品のアーキテクチャ設計で経験してきた判断や学びを語ったパネルセッションです。

3社に共通していたのは「モデルの大きな能力向上がアーキテクチャを書き直すきっかけになった」という経験です。新しいモデルが登場するたびに、それまで開発者が手書きしていた制御コードをモデル自身が担えるようになり、設計を根本から見直すことになったと語られました。

各社のアプローチは以下のとおりです。

* **Cognition（自律コーディングAI）**：早い段階から複数エージェントが協調する設計を採用。モデルが進化するたびに制御コードが不要になり、設計がシンプルになっていく
* **Harvey（法律AI）**：弁護士向けツールとして精度と信頼性が最優先。どこまでエージェントに自律させてどこから人間がレビューするかのバランスが常に主なトレードオフになっている
* **Gamma（プレゼンAI）**：マルチエージェント設計を採用し、生成物の品質向上に取り組む

**MCP（Model Context Protocol）** を本番で使う際は、コンテキスト管理とエラーハンドリングの設計が特に重要というのが3社の共通見解でした。

![AIネイティブスタートアップ3社のアーキテクチャ判断](https://static.zenn.studio/user-upload/deployed-images/1b401bce053f300b872a6b5a.png?sha=f8d8b6aa43f33bb516b364af57595d69b1ca6b58)  
*3社のアーキテクチャ判断 — 自律コーディング・法律AI・プレゼンAIで異なる設計判断が、モデル進化のたびに見直されている*

!

**サマリ**

* Cognition・Gamma・Harveyの技術リーダー3名によるアーキテクチャパネル
* 「モデルが進化するたびにアーキテクチャを書き直してきた」という3社共通の経験と、それぞれの設計判断の共有

---

## セッション12：How Vercel Builds for Model Step-Changes: A Tactical Playbook

<https://www.youtube.com/watch?v=bJKdXhnw7NU>

**登壇者**：Angela Jiang（Anthropic、モデレーター）+ Guillermo Rauch（Vercel CEO）

Vercelが提供するAI UIジェネレーター **「v0」** の開発経験をもとに、モデルの急速な性能向上にどう対応してきたかを語ったセッションです。

Guillermoが最初に紹介したのが、コストに関するデータです。**Vercel AI GatewayではOpusへのリクエストはAPI全体の23%にとどまるにもかかわらず、コスト全体の70%超を占めています**。リクエスト数は少なくても1回あたりの単価が高いため、請求額への影響は大きくなります。どのタスクにOpusを使い、どのタスクに安価なモデルを使うかを設計しないと、コストが想定以上に膨らむということです。

モデルが進化するにつれ、v0では次のような変化が起きました。

* **コスト増**：最新モデルへの切り替えでv0のクレジット消費が大幅に増加しました。モデルが賢くなるほど複雑なタスクに取り組もうとするため、トークン消費が増えます
* **処理方式の変化**：以前はタスクを細かく分けて複数のサブエージェントが順番に処理する設計でしたが、今はモデルがサンドボックス内で直接コードを書いて解決する形になり、外部ツールへの依存が減りました
* **デザイン判断の変化**：「良いデザインとは何か」という判断基準を、以前はVercelが細かいルールとしてモデルに与える必要がありました。今のモデルはそうした基準をすでに持っており、明示的に教える手間が減っています

**「今のエンジニアリングで重要なのは、モデルに何をやらせて何をやらせないかを設計すること、つまり適切なガードレールを設けることに移ってきた」** とGuillermoは語りました。

![Opusはリクエストの23%でコストの70%超を占める](https://static.zenn.studio/user-upload/deployed-images/8158f20931b9976bf5ccfa84.png?sha=e67e72a1c1fb2880425384ac1d56a379c481d96f)  
*コスト非対称性 — リクエスト数では23%にとどまるOpusが、コストでは70%超を占めるという構造*

!

**サマリ**

* VercelのGuillermo Rauch CEOが、AI UIジェネレーター「v0」の開発経験をもとにモデル進化への対応戦略を語った対談セッション
* 「Opusはリクエスト全体の23%に対してコストの70%超を占める」というコスト構造の数字が話題の中心

---

## セッション13：The thinking lever

<https://www.youtube.com/watch?v=OXJO4LldSnc>

**登壇者**：Matt Bleifer（Anthropic PM、Product Manager）

Claudeの推論量を開発者が制御する「思考のレバー」を解説したセッションです。Claudeが使うトークンには以下の3種類があり、このうち thinking tokens（思考トークン）の量を調整する仕組みが「思考のレバー」です。

| トークン種別 | 内容 |
| --- | --- |
| thinking tokens（思考トークン） | 推論プロセスに使用。最もコストが高い |
| tool call tokens（ツール呼び出しトークン） | ツールの実行に使用 |
| text tokens（テキストトークン） | 最終的な回答の生成に使用 |

thinking tokensの量は **low / medium / high / xhigh / max** の5段階で開発者が設定できます（`xhigh` は extra high の意）。\*\*Opus 4.7（Claude Codeも同様）のデフォルトは `xhigh`\*\*のため、単純なタスクではこのレベルを下げることでコストを抑えられます。

実証例として「Claude Plays Pokémon」のスピードラン（できるだけ早くゲームをクリアするタスク）が紹介されました。`xhigh` に設定してもクリアは速くならず、むしろ**考えすぎて遅くなる**という結果でした。単純なタスクに高い思考量を設定しても逆効果になるという好例です。

発表された新機能は以下のとおりです。

* **アダプティブ思考**：これまでは推論と回答生成を交互に繰り返す方式でしたが、新機能ではClaudeが「今この瞬間に考える必要があるか」を自律的に判断して動きます。不要な思考トークンの消費を抑えられます
* **タスクバジェット**：エージェントが使えるトークン数に上限を設定し、上限に近づいたタイミングで一度立ち止まって確認する仕組みです。長時間タスクでエージェントが意図しない方向に進んでしまうことを防ぎます

!

**サマリ**

* Claudeの思考量（thinking tokens）を開発者側から制御するAPI機能の解説セッション
* 「アダプティブ思考」と「タスクバジェット」という2つの新機能に踏み込んだ内容

---

<https://www.youtube.com/watch?v=EdmuYPBt_EM>

**登壇者**：Sesh Nalla（Datadog VP of Engineering）

DatadogにおけるClaude Codeの大規模導入事例を紹介したセッションです。

導入からわずか4ヶ月で**エンジニアの90%がAIコーディングツールを本番業務で採用し、その利用の3分の2をClaude Codeが占める**という数字が公開されました。

急速な普及の副作用として起きたのが、チームごとにツールが乱立する問題です。これを解決するためにDatadogが構築したのが **「Temper」** フレームワークです。検証・調整・確認・運用の4軸でツールを設計することで、チームをまたいで再利用できる共通基盤が生まれました。

セッションを通じて提唱されたのが **「マシンツールコンセプト」** という考え方です。エージェントがその場しのぎでツールを作るのではなく、「何を達成したいか」と「どの問題を解くか」を明確に定義したうえでツールを設計する形にシフトすることで、エンジニアの仕事は「コードを書くこと」から「フィードバックと検証を提供すること」へと変わっていきます。

![Temperフレームワーク — ツール設計の4軸](https://static.zenn.studio/user-upload/deployed-images/ed6ba51e482e08cf73d9acd2.png?sha=3fe6a156bc4e681893fd8e8a8e668b34b08785e0)  
*Temperフレームワークの4軸 — 検証・調整・確認・運用でツールを設計し、チーム横断で再利用できる共通基盤にする*

!

**サマリ**

* DatadogがClaude Codeを社内に大規模導入した経験を共有する事例セッション
* 「4ヶ月でエンジニアの90%がAIコーディングツールを採用（うち3分の2がClaude Code）」というスピード感と、副作用として発生したツール乱立を整理する「Temper」フレームワークに踏み込んだ内容

---

## セッション15：Building with Claude on Google Cloud

<https://www.youtube.com/watch?v=SqHsS737CeA>

**登壇者**：Ivan Nardini（Developer Relations Engineer (AI/ML), Google Cloud）

PM・UXデザイナー・ソフトウェアエンジニア・セキュリティエンジニア・データアナリストという**5つのロールを一人でこなしながら**、Claude + Google Cloudで30分以内にフィードバック収集アプリを本番デプロイするライブデモを行ったセッションです。

デモで使われた主なGoogle Cloudとの連携機能は以下のとおりです。

* **Developer Knowledge API + MCPサーバー**：Google Cloudの最新ドキュメントをClaude Codeが直接参照できるため、Cloud Runの詳細を知らなくてもデプロイできます
* **Google Cloud Skills**：Cloud Run・Firestoreなど各サービスの実装ブロックをエージェントに提供
* **3つのサブエージェントの並列実行**：API・データ取り込みパイプライン・ダッシュボードを別々のエージェントが同時に実装
* **ADC（Application Default Credentials）**：APIキー不要でシンプルに認証できるセットアップ

デモの最後には会場でリアルタイムにフィードバックを収集し、Claudeがその分析サマリーを即座に生成するシーンも披露されました。

!

**サマリ**

* 1人で5役のロールをこなしながら、30分でアプリを本番デプロイまで進めるライブデモ
* Google CloudのMCPサーバー・Skills・並列サブエージェント実行など、Claude × GCPの統合機能を実際に動かして見せるデモ

---

## セッション16：Getting more out of the Claude Platform

<https://www.youtube.com/watch?v=7oO37GRhwGk>

**登壇者**：Brad Abrams（Anthropic Platform PM Lead）

コスト削減・コンテキスト管理・精度向上を同時に実現するClaude APIの活用パターンを紹介したセッションです。

紹介された4つのパターンは以下のとおりです。

1. **プロンプトキャッシング**：システムプロンプトなどリクエストをまたいで変わらない部分をキャッシュしてAPIコストを削減します。本番エージェントでは80%以上のキャッシュヒット率を目標にすることが推奨されています
2. **ツールの遅延読み込み（`defer_loading: true`）**：ツールの定義情報を最初は概要だけ渡しておき、モデルが実際にツールを選んだタイミングで詳細な仕様を読み込む仕組みです。ツール数が多い場合にコンテキストの消費を抑えられます
3. **会話のコンパクション**：コンテキストウィンドウが上限に近づく前に、それまでの会話を要約して新しいセッションに引き継ぎます。長時間稼働するエージェントタスクには欠かせません
4. **Advisorパターン**：処理の大半は小さなモデルが担い、判断が難しいケースだけ高性能なモデルに委ねる設計パターンです。「Opus級の精度を低コストで実現できる」というのがこのパターンの肝です

大規模運用においては、わずかな最適化でもコストへの影響が大きく、API活用の設計が重要であることが強調されました。

![Claude API最適化の4パターン](https://static.zenn.studio/user-upload/deployed-images/317ea7d95b1e5700b670ef5d.png?sha=27041645441281b1753073bbcea1a98f03bfd3ca)  
*Claude API最適化の4パターン — プロンプトキャッシング・遅延読み込み・コンパクション・Advisorパターンを場面に応じて使い分ける*

!

**サマリ**

* Claude APIのコスト・コンテキスト・精度を同時に最適化するための4パターンを整理した解説セッション
* プロンプトキャッシング、ツールの遅延読み込み、会話のコンパクション、Advisorパターンの順に紹介

---

## セッション17：Evaluating and improving Replit Agent at scale

<https://www.youtube.com/watch?v=snroDwX1-JU>

**登壇者**：Michele Catasta（Replit President & Head of AI）+ Hannah Moran（Anthropic MTS）

AIエージェントの評価と継続的改善をテーマに、Replitの実践例を紹介したセッションです。

Catastaは「本番でモデルがどう動くかを予測できる評価を持っているチームは少ない」と問題提起し、この課題に対してReplitが開発したのが**ViBench**（**vibench.ai**）です。「コードが文法的に正しいか」ではなく「生成されたアプリが実際に動くか」で評価するオープンソースのベンチマークで、計測の結果、フロンティアモデルとオープンウェイトモデルの間に**3倍以上のスコア差**（クローズドな最良モデルでもPass@1は40%台にとどまる一方、オープンウェイトは軒並み12%未満）があることなどが明らかになりました。

本番データの評価には内製ツールの**Telescope**も活用されています。実行ログから失敗パターンを自動検出し、修正PRの作成・検証・リリースまでを自動化したループを毎日回しています。

Catastaは「評価とはリリース前に一度だけ通過するチェックボックスではなく、毎日より良いエージェントを届け続けるためのエンジンであるべきだ」と語り、セッションを締めくくりました。

![ViBench + Telescope — 評価の継続ループ](https://static.zenn.studio/user-upload/deployed-images/cd879ae166451d3354dbf9a3.png?sha=e9dde6938f02c70ab190295c11d6281dd601f983)  
*ViBench + Telescope — 本番ログ収集から失敗パターン検出・修正PR・検証まで自動で回し続ける改善ループ*

!

**サマリ**

* ReplitがAIエージェントの評価と継続的改善をどう運用しているかを共有する事例セッション
* バイブコーディング向けベンチマーク「ViBench」と、本番ログ分析ツール「Telescope」の正式公開

---

## セッション18：The capability curve

<https://www.youtube.com/watch?v=tP4MGcJ80Y0>

**登壇者**：Alex Albert（Anthropic Member of Technical Staff）

フロンティアモデルの進化速度と、開発者がそれをどう活かすべきかを語ったセッションです。

Albertが示したのは、コーディング能力のベンチマーク「SWE-bench Verified」での進捗です。

| モデル | SWE-bench Verified |
| --- | --- |
| Claude Sonnet 3.7（約1年前） | 62% |
| Claude Opus 4.7（2026年5月現在） | 87% |

わずか1年で25ポイント以上伸びており、Albertはこのような急速な進化の軌跡を **「ケイパビリティカーブ」** と呼びました。

Albertが開発者に向けて語ったのは、今のモデル性能を前提にアーキテクチャを設計しないという点です。モデルは今後も大幅に改善し続けるため、評価の仕組みを整えて、以前のモデルで動かなかったユースケースを新しいモデルで定期的に試し直すことを勧めました。以前は精度が出なくて諦めたユースケースも、新しいモデルで試し直せば動くようになっている可能性があります。

!

**サマリ**

* Alex Albertがフロンティアモデルの進化速度を示す講演
* SWE-benchが1年で62%→87%まで伸びたデータをもとに、未来のモデルを前提にしたアーキテクチャ設計の重要性を説く

---

## セッション19：Giving coding agents their own computers: How Cursor built cloud agents

<https://www.youtube.com/watch?v=BbYSGxtsMic>

**登壇者**：Alexi Robbins（Cursor Head of Engineering for Async Agents）

Cursor Cloud Agentsの設計と実績を紹介した、カンファレンス最後のセッションです。

Robbinsが語ったのは「エージェントを段階的に解放する3ステップ」でした。

| ステージ | 内容 |
| --- | --- |
| ① ツールとコンテキストを与える | cursor.com/onboardでリポジトリを探索するエージェント + AnEnv CLIで開発環境を整備 |
| ② より大きな仕事を任せる | 大きなタスクを委任。コンピュータ操作が次のフロンティア |
| ③ エージェント自身が仕組みを改善する | WTFスキルによるエージェント自己改善ループ |

中でも注目を集めたのが、③の **WTFスキル（Work on the Factory）** です。全てのCloud Agentに付与されるこのスキルは、「何かが煩わしい・壊れている・わからない場合は、乗り越えるのではなく報告する」という設計思想に基づいています。報告された問題は技術的な問題・権限の問題・知識不足の3種類に分類され、別のエージェントが検証しながら修正します。このサイクルを回すことで人間の関与を少しずつ減らし、エージェントが自分自身を改善し続ける仕組みを実現しています。

またRobbinsは、エージェントをクラウドで動かすことで開発者自身もリソース管理やコンテキストの切り替えから解放され、プログラミングがより楽しくなったと語りました。実績として、**Cursor社内のマージ済みPRの30%以上がCloud Agents由来**という数字も公開されています。

!

**サマリ**

* CursorのCloud Agentsの設計と運用実績を紹介するセッション
* 「エージェントを段階的に解放する3ステップ」と、エージェントが自分自身を改善するWTFスキルが中心テーマ

---

## 全体を通じた3つの共通テーマ

19セッションを通じて、複数の登壇者が共通して語っていた学びを3点に整理します。

![全19セッションから見えてきた3つの学び](https://static.zenn.studio/user-upload/deployed-images/3141412604700d42b649d2e9.png?sha=1fd046be7e98600b644a92118348fb490d84bbcb)  
*全19セッションから見えてきた3つの学び — アーキテクチャ・インフラ・評価の3軸が、これからのAI開発の設計指針になる*

### 1. アーキテクチャはモデルの進化を前提に設計する

Cognition・Gamma・Harvey・Vercelなど複数の登壇者が共通して語っていたのが、「モデルが賢くなるたびに、以前は必要だった制御コードが不要になってアーキテクチャを書き直してきた」という経験です。モデルが苦手なことを補うために書いた制御コードが、数ヶ月後には「モデルが自力でこなせるようになった処理」になっているというわけです。Lucas Gonzalezはこれを「モデルの信頼性不足を補うコードの半減期は数ヶ月」と表現しました。

今のモデル性能を基準にアーキテクチャを設計してしまうと、数ヶ月後には不要な制御コードが積み上がった複雑なシステムになりかねません。「今日のモデルではなく、6〜12ヶ月後のモデルを前提に設計する」という発想が、長期的に保守しやすいシステムにつながります。

### 2. エージェントはすでにインフラになっている

Managed Agents・Cursor Cloud Agents・Robobunなど、今回のセッションではエージェントを「対話するAIアシスタント」としてではなく、**システムの構成要素として組み込む**事例が多く登場しました。コードレビューやPR作成、テスト実行、デプロイまでをエージェントが自律的に担うようになっています。

Jess Yanが「エージェントのボトルネックはインテリジェンスではなくインフラだ」と指摘したように、モデルの賢さよりも、エージェントをどう安全に動かすかというインフラ面の整備が、今の開発現場の実質的な課題になっています。具体的にはサンドボックスの設計、処理の途中経過を保存するチェックポイント、複数エージェントの並列実行管理などが挙げられます。

### 3. 評価（evals）の設計が開発の質を左右する

Alex Albert・Hannah Moran・Michele Catastaなど多くの登壇者が共通して課題として挙げたのが、**評価（evals）の設計**です。「本番でモデルがどう動くかを事前に予測できる評価を持っているチームは少ない」という指摘があったように、感覚や手動確認に頼った開発では、モデルを更新するたびに品質が安定しません。

重要なのは評価の「中身」と「頻度」の2点です。中身については、コードが文法的に正しいかではなく生成されたアプリが実際に動くかどうかを基準にするViBenchのように、実際のユースケースに即した指標を持つことが重要です。頻度については、リリース前に一度だけ確認するのではなく、本番ログから失敗パターンを継続的に検出して修正・検証・リリースのループを回すことが求められます。Replitが毎日数百万件の実行ログをTelescopeで分析しているのは、その実践例です。

---

## まとめ

Code with Claude 2026 SFは、議論の焦点が「AIをどう使うか」から「AIを前提にした開発組織をどう作るか」へと移ったことを象徴するイベントでした。Anthropicの最新API発表に加え、Harvey・Vercel・Cursorといった企業も登壇し、19セッションを通じて扱われたトピックは多岐にわたります。なかでも、設計の書き直しやコスト構造の見直しなど、ふだんは表に出てこない各社の意思決定にまで踏み込んでいる点が、このカンファレンスの大きな特徴であったと言えるでしょう。

ロンドン編のまとめはこちらからご覧いただけます！

<https://zenn.dev/galirage/articles/code-with-claude-2026-london-summary>

Tokyo編（6月10日）のまとめも公開予定ですので、ぜひお楽しみに！

## 最後に

最後まで読んでくださり、ありがとうございました！  
この記事を通して、少しでもあなたの学びに役立てば幸いです✨

## 参考文献

<https://claude.com/blog/code-w-claude-sf-2026-sf>

<https://www.infoq.com/news/2026/05/code-with-claude/>

<https://chrisebert.net/notes-from-code-with-claude-2026/>

<https://venturebeat.com/technology/anthropic-says-it-hit-a-30-billion-revenue-run-rate-after-crazy-80x-growth>

<https://bun.com/blog/bun-joins-anthropic>

<https://www.youtube.com/watch?v=GMIWm5y90xA>

<https://www.youtube.com/watch?v=IMZa42k6L6M>

<https://www.youtube.com/watch?v=RtywqDFBYnQ>

<https://www.youtube.com/watch?v=y5TmF_6o6xk>

<https://www.youtube.com/watch?v=KLCuxMDZSDg>

<https://www.youtube.com/watch?v=E9gaQHrw_rg>

<https://www.youtube.com/watch?v=7oO37GRhwGk>

<https://www.youtube.com/watch?v=bJKdXhnw7NU>

<https://www.youtube.com/watch?v=OFDm3T7pVlc>

<https://www.youtube.com/watch?v=SqHsS737CeA>

<https://www.youtube.com/watch?v=7xco5Qd2Oo8>

<https://www.youtube.com/watch?v=DlTCu_pNDHE>

<https://www.youtube.com/watch?v=BrpB-h1e--k>

<https://www.youtube.com/watch?v=igO8iyca2_g>

<https://www.youtube.com/watch?v=EdmuYPBt_EM>

<https://www.youtube.com/watch?v=OXJO4LldSnc>

<https://www.youtube.com/watch?v=snroDwX1-JU>

<https://www.youtube.com/watch?v=tP4MGcJ80Y0>

<https://www.youtube.com/watch?v=BbYSGxtsMic>

<https://vibench.ai>
