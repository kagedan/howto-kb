---
id: "2026-07-17-claudeの開発者イベントcode-with-claude-2026総まとめロンドン編-01"
title: "Claudeの開発者イベント「Code with Claude 2026」総まとめ〜ロンドン編〜"
url: "https://zenn.dev/galirage/articles/code-with-claude-2026-london-summary"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "prompt-engineering", "API", "AI-agent"]
date_published: "2026-07-17"
date_collected: "2026-07-18"
summary_by: "auto-rss"
query: ""
---

はじめまして、ますみです！

[株式会社Galirage（ガリレージ）](https://bit.ly/galirage_homepage_zenn_intro)というAIスタートアップで、代表をしております^^

その他にも、「[AIとコミュニケーションする技術（インプレス出版）](https://bit.ly/amazon_book_ai_communication_skill_from_zenn_inside_body)」という書籍を執筆させていただいたり、[生成AIアカデミー](https://bit.ly/youtube_masumi_engineer_zenn_intro)というYouTubeチャンネルを運営したり、上智大学で非常勤講師をしたりしています！

[![自己紹介.png](https://res.cloudinary.com/zenn/image/fetch/s--9tzCxv3U--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://storage.googleapis.com/zenn-contents/images/intro/introduction_banner.png?_a=BACMTiAE)](https://bit.ly/banner_intro_masumi_creator_zenn)  
今回は、2026年5月19日にロンドンで開催されたAnthropicの開発者カンファレンス **「Code with Claude 2026 ロンドン編」** の内容をまとめてご紹介します！

「ClaudeとClaude Codeを実開発でどう使うか」をテーマに、Anthropicの最新機能発表からSpotify・Man Group・Delivery Heroなどヨーロッパ企業の実事例まで、全24セッションが公開されました。

現地に行けなかった方や、動画を1本ずつ見る時間はないけど要点だけ押さえたいという方に向けて、全セッションの内容を1つの記事にまとめました。情報量が多いため、各セッションごとに **サマリ** も用意しています。お忙しい方は、まずサマリだけでも目を通してみてください！

## Code with Claudeとは？

**Code with Claude** は、Anthropicが主催するソフトウェアエンジニア向けカンファレンスです。AnthropicのエンジニアからClaude・Claude Codeの設計思想や最新APIが発表されるほか、Claudeをすでに実プロダクトで活用しているパートナー企業の登壇も多く、設計上の判断や試行錯誤を実例ベースで知ることができます。

**Code with Claude 2026** は、サンフランシスコ・ロンドン・東京の3都市で順次開催されます。

* **サンフランシスコ編**：2026年5月6日（水）
* **ロンドン編**：2026年5月19日（月）← 本記事
* **東京編**：2026年6月10日（火）

本記事では **ロンドン編（5月19日）** の全24セッションをまとめています。

サンフランシスコ編はこちらにまとめていますので、ぜひ併せてご覧ください！

<https://zenn.dev/galirage/articles/code-with-claude-2026-sf-summary>

## ロンドン編の全セッション一覧

| # | セッション名 | 登壇者 | 概要 | 動画 |
| --- | --- | --- | --- | --- |
| 1 | Opening Keynote | Boris Cherny ほか Anthropic | Self-hosted sandboxesとMCP tunnelsの発表を中心に、エージェント時代の到来とClaude Codeの進化を語った基調講演。 | [▶](https://www.youtube.com/watch?v=6amLO7I9xdg) |
| 2 | What's new in Claude Code | Ralph Ramos（Anthropic） | Claude Codeに最近追加された機能の概要を20分でまとめた発表。 | [▶](https://www.youtube.com/watch?v=sRvUXLquiRg) |
| 3 | Memory and dreaming for self-learning agents | Ravi Trivedi（Anthropic） | エージェントの永続メモリとバックグラウンド非同期処理（Dreaming）を深掘り。楽天（Rakuten）・Harveyの導入実績も紹介。 | [▶](https://www.youtube.com/watch?v=IGo225tfF2I) |
| 4 | Picking the right model | Lucas Smedley（Anthropic） | コスト・レイテンシ・品質の3軸でモデル選択を最適化する戦略を解説。プロンプトキャッシュとコンテキストエンジニアリングも紹介。 | [▶](https://www.youtube.com/watch?v=P0uMXS6emHA) |
| 5 | Coding is no longer the constraint: Scaling devex to teams and agents at Spotify | Niklas Gustavsson（Spotify） | 99%のエンジニアがAIを活用するSpotifyが、HonkエージェントとFleetshiftでコードベース移行を自動化した事例。 | [▶](https://www.youtube.com/watch?v=zFslvuvYifQ) |
| 6 | Designing with Claude: From prompt to production | Dan Cary（Anthropic） | 3人チームが10週間で構築したClaude Designの開発プロセスとプロトタイプ主導の設計手法を紹介。 | [▶](https://www.youtube.com/watch?v=Uvl-tRga98g) |
| 7 | Beyond the basics with Claude Code | Daisy Hollman（Anthropic） | CLAUDE.md・MCPサーバー接続・スキル設計・Auto modeの安全な使い方をハンズオン形式で解説したワークショップ。 | [▶](https://www.youtube.com/watch?v=tuY2ChJIx48) |
| 8 | How to get to production faster with Claude Managed Agents | Michael Cohen + Harrison Stall（Anthropic）ほか | Managed Agentsの4つのプリミティブ解説とSelf-hosted sandboxes・MCPトンネルの発表、パートナー4社のパネル。 | [▶](https://www.youtube.com/watch?v=zenIB7XLZxQ) |
| 9 | From one person to 80: Scaling a hypergrowth engineering org with Claude Code | Gabriel Grinberg + Yoav Orlev（Base44） | エンジニア1人からWix買収・80人体制へ成長したBase44が、Claude Codeを使って3つのボトルネックを乗り越えた事例。 | [▶](https://www.youtube.com/watch?v=VueeyKcquoA) |
| 10 | Stop babysitting your agents | Sid Bidasaria（Anthropic） | Routinesを使ってエージェントの手動監視から脱却し、自律的に動くワークフローへ移行する実践ワークショップ。 | [▶](https://www.youtube.com/watch?v=wI0ptqCSL0I) |
| 11 | AI with Claude on AWS: From code to orchestration | Antonio Rodriguez（AWS） | AWSとAnthropicのパートナーシップとClaude Platform on AWSの紹介。Amazon Bedrock上でClaude Codeを動かすワークショップ。 | [▶](https://www.youtube.com/watch?v=5YHIrTYxM3w) |
| 12 | How Lovable vibecodes production software at scale | Fabian Hedin（Lovable） | 月間6億以上のセッションを持つLovableが、コンシューマースケールでClaude Codeを安定稼働させる仕組みを解説。 | [▶](https://www.youtube.com/watch?v=mhW-XXnDFSU) |
| 13 | The thinking lever | Alexander Bricken（Anthropic） | Test-time computeの仕組みとEffort level（low〜max）の使い分けを、交通シミュレーションのデモで実演。 |  |
| 14 | Build a production-ready agent with Claude Managed Agents | Michael Cohen（Anthropic） | Managed Agentsを使ってM&A分析エージェントをゼロから本番まで構築するライブコーディングワークショップ。 | [▶](https://www.youtube.com/watch?v=jWWsLe4Gh5Y) |
| 15 | Building AI-native at enterprise scale: monday.com, Doctolib, and Delivery Hero | Ruslan Semenov + Alex Kaluzny + Rodrigue Schäfer | Delivery Hero（1日100本以上のPR自動マージ）・Doctolib・monday.comが語ったエンタープライズAI導入の実態。 | [▶](https://www.youtube.com/watch?v=XFaeIbL-lvE) |
| 16 | Running an AI-native engineering org | Fiona Fung（Anthropic） | コーディングがボトルネックでなくなった後、チームのプロセス・採用・組織設計をどう変えたかを語ったセッション。 | [▶](https://www.youtube.com/watch?v=IA5LWIGqnyM) |
| 17 | The capability curve | Jeremy Hadfield（Anthropic） | 「Claudeが完全に書いたPRを先週出荷した人」という問いかけで始まった、モデルの急速な能力向上と開発者への示唆を語ったセッション。 | [▶](https://www.youtube.com/watch?v=DNRddIEoH3c) |
| 18 | Building signals that trade themselves | Tushara Fernando（Man Group） | 2,000億ドルの資産を運用するMan GroupでAIが考案・バックテストした取引シグナルが本番稼働するまでの道のり。 | [▶](https://www.youtube.com/watch?v=EOg4gY0Yln0) |
| 19 | Build AI agents using Claude in Microsoft Foundry | Marlene Mhangami ほか（Microsoft） | Microsoft FoundryでClaude Sonnet 4.6をデプロイし、カップケーキショップのエージェントをMCPサーバーと接続するワークショップ。 | [▶](https://www.youtube.com/watch?v=TQd_YQvydVg) |
| 20 | What legal agents inherit from coding agents: Lessons from Legora | Jakob Emmerling（Legora） | コーディングエージェントの設計原則を法律AIエージェントに適用する際の「再利用・翻訳・発明」の3パターンを解説。 | [▶](https://www.youtube.com/watch?v=nho1YAEPuwA) |
| 21 | Building with Claude on Google Cloud | Ivan Nardini（Google Cloud） | Claude + Google Cloudで30分以内にフィードバックアプリを本番デプロイするライブビルドワークショップ。 | [▶](https://www.youtube.com/watch?v=l8fxVYIP4HQ) |
| 22 | Build a proactive agent workflow with Claude Code | Maya Nielan（Anthropic） | Routinesを使ってドキュメント自動更新などのプロアクティブなワークフローを構築するワークショップ。 | [▶](https://www.youtube.com/watch?v=eSP7PLTXNy8) |
| 23 | Getting more out of the Claude Platform | Punit Shah（Anthropic） | プロンプトキャッシング・コンテキスト管理・Advisorストラテジーを活用してコストと精度を最適化する手法を紹介。 | [▶](https://www.youtube.com/watch?v=QIriO1-vHYw) |
| 24 | The prompting playbook | Margot van Laar（Anthropic） | 既存プロンプトのモデル移行と新規エージェント構築という2シナリオをEval駆動で体系的に改善するワークショップ。 | [▶](https://www.youtube.com/watch?v=G2B0YWuJUgI) |

ここからは各セッションの内容を順番に見ていきます。

---

## セッション1：Opening Keynote

<https://www.youtube.com/watch?v=6amLO7I9xdg>

**登壇者**：Boris Cherny（Head of Claude Code）、Angela Jiang、Katelyn Lesse、Cat Wu、Lisa

基調講演ではまず、 **Claude APIの利用量が前年比17倍規模に拡大した** ことと、Claude Codeユーザーの利用時間が **週平均20時間以上** に達したことが発表されました。Boris Chernyは「BASIC（1970〜80年代に普及した入門向けプログラミング言語）にはアイデアをすぐコードにできるシンプルさがあったが、ビルドシステムやパッケージマネージャーが加わるたびにステップが増えた。Claude Codeはアイデアをすぐコードにできる、あのシンプルな感覚を取り戻す手段になる」と語りました。

導入事例としてSpotifyのコードベース移行で工数90%削減、Shopifyでのコード生成の過半をAIが担う活用、Mercado Libreでの数千人規模の活用、Anthropic社内のPR件数200%増が紹介されました。

また、新機能として以下の6つが一挙に発表されました。

* **Self-hosted sandboxes**（パブリックベータ）
* **MCP tunnels**（リサーチプレビュー）
* **Routines**（スケジュール・Webhook対応）
* **CI Autofix**（PRマージまでを自動処理）
* **Claude Code Desktop**（デスクトップアプリ）
* **Agent view**（エージェント状態の可視化）

![Opening Keynoteで発表された6つの新機能](https://static.zenn.studio/user-upload/deployed-images/fe78f3c16c28972b6d6fa97a.png?sha=82d3eec24d7e8b3641af1a33772b77f7351e5fd6)  
*Opening Keynoteで発表された6つの新機能 — Self-hosted sandboxes・MCP tunnels・Routines・CI Autofix・Claude Code Desktop・Agent viewの6機能が一挙に発表された*

!

**サマリ**

* カンファレンス全体の方向性を示す基調講演
* API利用量が前年比17倍規模に拡大、Anthropic社内PRが200%増という成長実績を発表
* Self-hosted sandboxesとMCP tunnelsを中心に6つの新機能が正式発表

---

## セッション2：What's new in Claude Code

<https://www.youtube.com/watch?v=sRvUXLquiRg>

**登壇者**：Ralph Ramos（Anthropic）

Anthropicがここ数ヶ月でリリースしたClaude Codeの機能を、設計の背景・意図・導入手順とともに解説したセッションです。基調講演で発表されたRoutines・CI Autofix・Agent view CLIをはじめ、Remote Control Mode・Gitワークツリー・コンテキスト管理の改善も含めた、Claude Codeの全アップデートを網羅しています。

特に取り上げられたアップデートは以下のとおりです。

* **Auto Mode**：許可を毎回求めて止まるのではなく、「破壊的な操作かどうか」「プロンプトインジェクションの兆候がないか」という2段階の安全チェックを通過した操作は自律的に続行する実行モード
* **Auto Memory**：プロジェクトのコンテキスト・コーディングスタイル・アーキテクチャ上の選択・デバッグの記録を、ローカルのメモリファイルに自動で蓄積する仕組み
* **Routines**：スケジュール・GitHubのWebhook・API呼び出しをトリガーに、リモート環境でClaudeのセッションを自動起動するワークフロー機能
* **CI Autofix**：PRの作成からマージまでの間に発生する、レビューコメント・セキュリティ指摘・マージコンフリクト・不安定なCIの失敗を自動で処理する機能
* **MCP tunnels**：ファイアウォール内のプライベートMCPサーバーへ、外部公開せずにセキュアに接続する仕組み
* **レート制限の拡大**：Pro・Max・Team・Enterpriseの全プランで、Claude Codeの5時間あたりのレート制限を2倍に拡大

![Claude Codeの最新アップデート一覧](https://static.zenn.studio/user-upload/deployed-images/8dfaabe39b2520724335a916.png?sha=ecb52e3c7d8eba7d690cf754adbaa60d76b38d75)  
*Claude Codeの最新アップデート一覧 — Auto Mode・Auto Memory・Routines・CI Autofixを中心に、自律実行とコンテキスト管理を強化する6つの機能アップデート*

!

**サマリ**

* Claude Codeの最新アップデートをまとめて紹介するキャッチアップセッション
* リリース内容・設計の背景や意図・導入手順を機能ごとに解説
* Auto Mode・Auto Memory・Routines・CI Autofixなど、自律実行とコンテキスト管理を強化する機能が中心

---

## セッション3：Memory and dreaming for self-learning agents

<https://www.youtube.com/watch?v=IGo225tfF2I>

**登壇者**：Ravi Trivedi（Anthropic）

**Memory API** と **Dreaming** という2つのコア機能を深掘りしたセッションです。

Memory APIはファイルシステムに近い設計で、エージェントが情報を **書き込み・読み取り・バージョン管理** できる仕組みです。スコープが2種類あり、 **org-wide（組織全体で読み取り可能）** と **task-specific（タスク実行エージェントのみ書き込み可能）** のアクセス制御を持ちます。競合を後処理で解決する設計により、[マルチエージェント](https://zenn.dev/umi_mori/books/generative-ai-glossary/viewer/what-is-multi-agent)環境でも安全に並列アクセスできます。Memory APIはスタンドアロンのAPIとして他のシステムからも独立して利用可能です。

Dreamingはエージェントが **バックグラウンドで非同期処理** を行う機能です。実際のセッションデータを横断分析し、新しいメモリを生成・既存メモリを最適化することでエージェントの品質を継続的に改善します。Ravi Trivediは「Dreamingは単なるメモリ保存ではない。過去のインタラクションを振り返って学ぶ仕組みだ」と語りました。

実績として紹介された2社は以下のとおりです。

* **楽天（Rakuten）**：Memory APIの導入で重大エラーが **97%削減**
* **Harvey**：Dreamingの導入でタスク完了率が **6倍**に向上

デモでは、SRE（Site Reliability Engineering）のオンコール対応を自動化するプラットフォームをMemory API + Dreamingで構築する様子が披露されました。アラートが届くと、エージェントが過去の対応履歴をメモリから参照しながら原因調査を行い、対応後は学習した知識を次のセッションに引き継ぎます。

!

**サマリ**

* エージェントの長期記憶（Memory API）と非同期学習（Dreaming）を技術的に深掘りしたセッション
* 楽天（Rakuten）重大エラー97%削減・Harvey タスク完了率6倍という2社の導入実績が示された

---

## セッション4：Picking the right model

<https://www.youtube.com/watch?v=P0uMXS6emHA>

**登壇者**：Lucas Smedley（Anthropic）

コスト・[レイテンシ](https://zenn.dev/umi_mori/books/generative-ai-glossary/viewer/what-is-latency)・品質の **3つのトレードオフ** を軸に、正しいモデルを選ぶための実践的な戦略を解説したセッションです。

Lucas Smedleyは「正しいモデルとは、タスクあたり最も安いモデルではなく、成功したアウトカムあたり最も安いモデルだ」と定義しました。トークンあたりの単価だけで比較すると、精度が低くリトライが増えて結果的に高くつくケースが多いという指摘です。

モデル選択の3つの柱についての解説は以下のとおりです。

* **品質**：公開[ベンチマーク](https://zenn.dev/umi_mori/books/generative-ai-glossary/viewer/what-is-benchmark)より自社タスク向けの評価（private eval）を優先する。ベンチマークのノイズ・インフラ障害・サチュレーション（上位モデルでは差が消える現象）という3つの落とし穴に注意
* **レイテンシ**：Thinking（内部思考）とEffort（推論量）は独立したパラメータとして扱う
* **コスト**：プロンプトキャッシングで **1/10の価格**でキャッシュヒット時のリクエストが処理できる。本番エージェントでは80〜90%のヒット率が目標

コンテキストエンジニアリングの効果として、ある事例では **66.4%のトークン削減** を達成。別の実装では **77%のトークン削減・65%のコスト削減・9%の精度向上** を同時に実現したと紹介されました。

ワークショップでは、スケジューリングエージェントのベンチマーク（τ-bench）を使った実演も行われ、Opus 4.7がSonnet 4.6より高速かつ高精度という意外な結果が示されました。

![モデル選択の3軸トレードオフ](https://static.zenn.studio/user-upload/deployed-images/974cbfebd979fcb3fee684df.png?sha=171732cfa72af4960beb9562f5826242d8037013)  
*モデル選択の3軸トレードオフ — コスト・レイテンシ・品質の3軸を最適化し「成功アウトカムあたり最安のモデル」を選ぶ考え方を図解した*

!

**サマリ**

* コスト・レイテンシ・品質の3軸でモデル選択を最適化する実践的なセッション
* 「正しいモデル = トークンあたり最安ではなく、成功アウトカムあたり最安」という考え方が軸
* プロンプトキャッシングで1/10価格、コンテキストエンジニアリングで70%前後のトークン削減という具体的な目標値が示された

---

## セッション5：Coding is no longer the constraint: Scaling devex to teams and agents at Spotify

<https://www.youtube.com/watch?v=zFslvuvYifQ>

**登壇者**：Niklas Gustavsson（Chief Architect & VP of Engineering, Spotify）

Spotifyがどのようにして全エンジニアリング組織にAIを浸透させ、エージェントによるコードベース自動化を実現したかを語ったセッションです。

Spotifyが直面していた課題は、コードベースが **エンジニア数の7倍のペースで増大** し、開発者の多くが機能開発ではなくコードベースの保守（特にマイグレーション）に時間を取られていたことです。

エンジニアの **99%** がAIコーディングツールを週次で使用し、 **94%** が生産性向上を実感、PRの頻度が **76%増加** しています。

この変化を牽引しているのが **「Honk」** というバックグラウンドコーディングエージェントです。Claude Agent SDK上で動作し、Kubernetes上で複数インスタンスを並列起動できます。HonkはFleetshiftと組み合わせたFleet Managementシステムの中でコード修正を担当しており、システム全体で累計 **250万本以上** のPRを自動マージしています。また、数週間かかっていたJavaマイグレーションを **3日** で完了しています。

「Claudeに大量のコードを見せたとき、一貫して見えれば見えるほど良い仕事をする」とNiklasは語りました。HonkはBackstage・Soundcheck・golden stateといった **15年分のインフラ投資** の上に動いています。

!

**サマリ**

* Spotifyのエンジニアリング全組織へのAI浸透事例と、Honkエージェントによるマイグレーション自動化を紹介したセッション
* AIによってコードを書く工程がボトルネックでなくなった今、意思決定と優先順位付けが新たなボトルネックになっているというメッセージが中心

---

## セッション6：Designing with Claude: From prompt to production

<https://www.youtube.com/watch?v=Uvl-tRga98g>

**登壇者**：Dan Cary（Anthropic）

Claude Codeを使って、デザインを生成するツール「Claude Design」を開発した経緯を公開したセッションです。自社のAIで自社のAIプロダクトを開発するというアプローチと、プロトタイプ主導の開発手法が紹介されました。

Claude Designは、テキストのプロンプトからデザイン・プロトタイプ・スライド・UIモックアップを生成するビジュアル作成ツールです。チームのコードベースやデザインファイルを読み込み、カラーパレット・タイポグラフィ・コンポーネントといったデザインシステムを自動で組み立てます。完成したデザインはエクスポートしてClaude Codeに引き継げるため、 **デザインから実装までを1つのループでつなげられる** のが特徴です。

セッションでは、この製品をわずか3人・10週間で作り上げた背景として、Claude自身に試作を繰り返させるプロトタイプ主導の進め方が紹介されました。仕様を固めてから作るのではなく、動くプロトタイプを早く出して判断するというAnthropic流の開発スタイルが、小規模チームでの高速な立ち上げを支えています。

!

**サマリ**

* Anthropicのデザインチームが自社製品「Claude Design」を構築した開発プロセスを語ったセッション
* テキストからデザイン・プロトタイプ・UIを生成し、Claude Codeへ引き継いで実装までつなげるツール
* 小規模チームで短期間にプロトタイプから本番まで仕上げたプロセスに注目

---

## セッション7：Beyond the basics with Claude Code

<https://www.youtube.com/watch?v=tuY2ChJIx48>

**登壇者**：Daisy Hollman（Anthropic）

CLAUDE.md・MCPサーバー接続・スキル設計・Auto modeの安全な使い方など、Claude Codeの応用的な機能をハンズオン形式で体験するワークショップです。Claude Codeをチームに導入し、組織のコンテキストを教え込む実践的な手順が紹介されました。

Daisy Hollmanが繰り返し強調したのは「 **あなたがClaudeにプロンプトを書くのではなく、Claudeが自分自身でプロンプトを書くシステムを作るべきだ** 」という考え方です。

特に強調されたのが、[コンテキストウィンドウ](https://zenn.dev/umi_mori/books/generative-ai-glossary/viewer/what-is-context-window)の使い方です。「コンテキストウィンドウという有限の領域に何を入れるかを選ぶことが、最も難しいエンジニアリング上の課題だ」と述べ、CLAUDE.mdにチームの規約や略語をすべて詰め込むと、毎ターン全トークンを消費してパフォーマンス低下とコスト増を招くと警告しました。Hooksは条件に合致したときだけ動作するため、他の拡張機能と異なりコンテキストウィンドウを事前に消費せず、エージェントが実行中に問題を検知するとその場で動作を修正できる[ガードレール](https://zenn.dev/umi_mori/books/generative-ai-glossary/viewer/what-is-guardrail)として機能します。

また「エージェントは夜間に動かすべきだ」とも語り、半年前には非現実的だったこの運用が、auto modeによる数時間の自律動作で可能になったと紹介しました。

![Claude Codeの5つの拡張レイヤー](https://static.zenn.studio/user-upload/deployed-images/f7c031a02bb962b9523602c7.png?sha=f4e204d32c081fb5a5187b6eb2fb18266521f5b8)  
*Claude Codeの5つの拡張レイヤー — CLAUDE.md・MCP・Skills・Hooks・Subagentsそれぞれの役割と使いどころを整理した*

!

**サマリ**

* Claude Codeの上級機能をハンズオンで学ぶワークショップ
* CLAUDE.md・MCP・Skills・Hooks・Subagentsの5つの拡張レイヤーの使いどころを整理

---

## セッション8：How to get to production faster with Claude Managed Agents

<https://www.youtube.com/watch?v=zenIB7XLZxQ>

**登壇者**：Michael Cohen + Harrison Stall（Anthropic）、ゲスト：Luke（Vercel）・Ashot（Modal）・Ivonne（Daytona）・Mike（Cloudflare）

Claude Managed Agentsの技術解説と新機能発表、4社パートナーによるエージェントインフラのパネルディスカッションで構成されたセッションです。

4社に共通していたのは、モデルの性能よりも周辺インフラの整備が今の課題だという認識です。

開発者が本番でエージェントを動かす際の3大課題として以下が挙げられました。

1. **コンテキスト管理とメモリ**：うまく機能すれば強力だが、失敗するとエージェントのパフォーマンスを完全に破壊する
2. **インフラ**：信頼性・スケーラビリティ・セキュリティ・レイテンシ（最も多く挙げられた課題）
3. **オブザーバビリティ**：エージェントが成功しているかを把握できなければ評価も改善もできない

Managed Agentsが扱う4種類のイベントは以下のとおりです。

| 種別 | 内容 |
| --- | --- |
| User events | テキスト・画像・ドキュメント、割り込み、カスタムツール結果、[Human-in-the-loop](https://zenn.dev/umi_mori/books/generative-ai-glossary/viewer/what-is-human-in-the-loop)の確認、Outcomes定義 |
| Agent events | Claudeのメッセージ、ツール実行、マルチエージェント協調 |
| Session events | ライフサイクル変化、エラーリカバリー、Outcomes処理 |
| Span events | 長時間処理の開始・終了通知 |

パートナーパネルでは4社がそれぞれのアプローチを紹介しました。Vercelはビルド・サンドボックス・ファンクションを統合する"fluid compute"、Modalは独自スケジューラで数十万のサンドボックスをGPU対応で起動、Daytonaは「エージェントは人間が必要とするものを必要とする」を設計原則に、CloudflareはMicroVMとIsolatesの2種類のサンドボックス技術を展開しています。4社に共通する課題として、**エージェントのID管理**（エージェントがエージェントを呼び出すときの権限チェーン）が挙げられました。

![Managed Agentsが扱う4種類のイベント](https://static.zenn.studio/user-upload/deployed-images/b9ac759e9a217982a3811640.png?sha=0ff2635e9947219bf2c2bf28b2fb8f688cd7b6d6)  
*Managed Agentsが扱う4種類のイベント — User・Agent・Session・Spanの4カテゴリでエージェントの状態と処理を管理する構造*

!

**サマリ**

* Managed Agentsの技術解説とSelf-hosted sandboxes・MCPトンネルの詳細を紹介したセッション
* Vercel・Modal・Daytona・Cloudflareのパートナー4社が、エージェントインフラの未来をそれぞれの視点で語ったパネルも収録

---

## セッション9：From one person to 80: Scaling a hypergrowth engineering org with Claude Code

<https://www.youtube.com/watch?v=VueeyKcquoA>

**登壇者**：Gabriel Grinberg（AI Engineering Manager）+ Yoav Orlev（Head of Product）（Base44）

Base44はノーコードのAIアプリビルダーで、創業からわずか半年で約25万ユーザーを獲得し、2025年にWixが約8,000万ドルで買収しました。買収後はユーザーが200万規模へと拡大し、エンジニアも1人から80人規模へ急増、ARR（年間経常収益）も数ヶ月で1億ドルから1億5,000万ドルへと急伸しています。この急拡大の過程で生じた3つのボトルネック（新エンジニアのオンボーディング・実験検証サイクルの圧縮・拡大するコードベースの品質維持）を、Claude Codeでどう乗り越えたかが本セッションのテーマです。

セッションで繰り返し強調されたのは「 **AIの活用が広がるほど、それに合わせて開発プロセスも進化させるべきだ** 」という原則です。これはプロダクトにもプロセスにも当てはまり、「モデルが更新されたときに自然と改善されないプロセスは、設計が間違っている」と表現されました。その土台になっているのが **「エレガントシンプリシティ」原則** です。アーキテクチャをあえてシンプルに保つことで、モデルの進化に追従しやすい設計を維持しています。

!

**サマリ**

* ハイパーグロースを経験したBase44が、Claude Codeで組織スケールの課題を乗り越えた事例セッション
* AIの活用が広がるほど開発プロセスも進化させるべきという原則が中心メッセージ
* アーキテクチャをシンプルに保つ「エレガントシンプリシティ」原則がキーワード

---

## セッション10：Stop babysitting your agents

<https://www.youtube.com/watch?v=wI0ptqCSL0I>

**登壇者**：Sid Bidasaria（Anthropic）

Routinesを使ってエージェントの手動監視から脱却し、自律的に動くワークフローへ移行する方法を解説したワークショップです。検証ループの実装・タスクの並列化・バックグラウンドプロセスの活用という3つの戦略を通じて、ソフトウェア品質を保ちながら開発者の時間を解放するアプローチが紹介されました。

「 **babysitting（エージェントの手動監視）をやめて、オーケストレーションに移行しよう** 」をテーマに、Claude Codeのエンジニアが実際に使っているワークフローを実演しました。多くのユーザーがClaude Codeをターンごとに応答するチャットとして使っているが、それは多段階のタスクではボトルネックになると指摘し、「タスクを渡したらその場を離れ、完成した成果・明確なブロッカー・作業の経過報告を受け取る」のが理想の使い方だと示しました。

その鍵になるのが `/goal` コマンドです。エージェントに検証可能なゴールを与えると、別の小さなモデルが各ラウンドの後に達成度を確認し、満たすまで自律的に反復します。人が逐一確認しなくても品質を維持できる仕組みを実演しました。

![babysittingからRoutinesへの移行](https://static.zenn.studio/user-upload/deployed-images/761a383662e407b480060723.png?sha=086311dbac2e0ba9b2ac7c1632777c11e0082d56)  
*babysittingからRoutinesへの移行 — ターンごとの手動確認をやめ、検証可能なゴールを与えて自律的に反復させるオーケストレーション設計*

!

**サマリ**

* babysitting（エージェントの手動監視）をやめてRoutinesで自律化する実践ワークショップ
* ターンごとのチャット利用が多段階タスクのボトルネックになるという問題提起
* 検証可能なゴールを与える `/goal` コマンドで、人が逐一確認せずに品質を保つ仕組みを実演

---

## セッション11：AI with Claude on AWS: From code to orchestration

<https://www.youtube.com/watch?v=5YHIrTYxM3w>

**登壇者**：Antonio Rodriguez（Principal Solutions Architect, AWS）

AWSとAnthropicの3年以上にわたるパートナーシップの背景を解説しつつ、ClaudeをAWSで使う方法をハンズオンで学ぶワークショップです。

AWSとAnthropicの関係を整理すると次のとおりです。

* AmazonはAnthropicに **数十億ドル規模の投資** を実施
* AnthropicはAWSを主要クラウドプロバイダーとし **1,000億ドル以上のAWSインフラ利用** を確約
* **Project Rainier**：ClaudeのトレーニングとホスティングのためにAWSが構築した最大規模のAI計算インフラ
* **Trainium（第3世代）**：Claude向けカスタムチップセット。コスト効率と速度を両立

ClaudeをAWSで使う3つの方法として、Amazon Bedrock API・Claude Platform on AWS（カンファレンスの数日前に正式リリース）・Claude Desktop / Claude Code（AWS Marketplaceまたは3P経由）が紹介されました。 **Claude Platform on AWSはAnthropicの直接利用と完全な機能パリティ** を持ち、AWSのIAMロール・SSO・Oktaと直接統合できます。

ワークショップはExcalidrawリポジトリを題材に、以下の3つのモジュールで構成されていました。

1. Bedrock上でのセットアップ
2. Playwright MCPを使ったスクリーンショット取得と自動修正
3. サブエージェント・プラグイン・カスタムスキル・Hooksの活用

![ClaudeをAWSで使う3つの方法](https://static.zenn.studio/user-upload/deployed-images/927254b61046dae5bc0217ba.png?sha=29f0448a3f10abb9f40473ed015bef6f9f76d33a)  
*ClaudeをAWSで使う3つの方法 — Amazon Bedrock API・Claude Platform on AWS（完全パリティ・IAM統合）・Claude Desktop/Codeの3つの選択肢*

!

**サマリ**

* AWSとAnthropicのパートナーシップ解説と、Amazon Bedrock上でClaude Codeを動かすハンズオンワークショップ
* カンファレンス直前に正式リリースされたClaude Platform on AWSの機能（完全パリティ・AWSの統合請求・IAM連携）が話題の中心

---

## セッション12：How Lovable vibecodes production software at scale

<https://www.youtube.com/watch?v=mhW-XXnDFSU>

**登壇者**：Fabian Hedin（Co-founder & CTO, Lovable）

非エンジニアが本番ソフトウェアを構築するプラットフォームとして **月間6億以上のセッション** を提供するLovableが、コンシューマースケールでClaudeを信頼性高く運用するための仕組みを紹介したセッションです。コーディングミスを検出・修正する **フリートラーニングレイヤー** 、すべてのモデルリリースをゲートする **Evalループ** 、エージェント主導のフィードバックループで問題を自動解消する **セルフヒーリング機構** の3本柱を詳しく解説しています。

Lovableは2024年11月のローンチ以降、累計5,000万件以上のプロジェクトが構築され、1週間あたり100万件以上の新規プロジェクトが作られています。年間経常収益も12ヶ月以内に2億ドルへ到達し、その後4億ドルまで伸びました。Fabian Hedinは **「プロトタイプを作るのは簡単でも、非エンジニアが本番ソフトウェアを作れるプラットフォームを安定運用するのはまったく別の難しさがある」** という問いに正面から向き合い、その解決策として3本柱の仕組みを構築しました。

アーキテクチャは、ビルド全体を推論するメインエージェントが、細分化したタスクをサブエージェントへ委譲し、各タスクに最適なモデルを割り当てる構造です。Fabian Hedinは、Claude Sonnet 3.5が「初めて実用的に機能したエージェント」を実現したモデルであり、その後Claude Opus 4.5が長時間タスクの信頼性を大きく高め、現在メインで使うClaude Opus 4.6が設計品質と自律性をさらに引き上げたと、モデルの進化を実体験ベースで振り返りました。

!

**サマリ**

* 月間6億セッションのプロダクションプラットフォームがClaude運用の信頼性をどう担保しているかを解説したセッション
* フリートラーニング・Evalループ・セルフヒーリングという3つの仕組みが柱
* メインエージェントがタスクごとに最適なモデルを割り当てる構成。Sonnet 3.5からOpus 4.6までのモデル進化を実体験で振り返った

---

## セッション13：The thinking lever

**登壇者**：Alexander Bricken（Applied AI Research, Anthropic）

**Test-time compute**（推論時にトークンを多く使うことで性能を向上させる技術）の仕組みと実践的な使い分けを解説したセッションです。

内部のコーディングベンチマークでは、モデルサイズを上げることで性能が約80%まで向上しますが、 **同じスコアをThinkingトークンを増やすことでも達成できる** ことが示されています。

Claudeの Effort level は5段階で、 **xhigh** がClaude CodeとClaude.aiのデフォルトです。

| Level | トークン目安 | 特徴 |
| --- | --- | --- |
| low | 最小 | 4,600トークン・約50秒。基本的な結果 |
| medium | 小 | 標準的な思考 |
| high | 中 | 約2倍のトークン・時間 |
| **xhigh** | 大 | **Claude Code / Claude.aiのデフォルト** |
| max | 最大 | 約10倍のトークン・時間。最も詳細な結果 |

Thinkingは Extended thinking → Interleaved thinking → Adaptive thinking（モデルが自律的に要否を判断）と進化しています。「 **Thinkingのトグルはあくまでもプロキシ。ClaudeにThinkingツールを与えて自分で判断させるほうが良い結果を生む** 」というのがセッションの結論です。

モデル選択の原則として「 **タスクに少しでも知性が必要なら、低Effortでも大きいモデルを使うべき** 」であることが強調されました。

!

**サマリ**

* Test-time computeの仕組みとEffort levelの使い分けを解説したセッション
* xhighがClaude CodeとClaude.aiのデフォルト。迷ったらxhighを選ぶという実践的な推奨
* Thinkingのトグルはプロキシにすぎず、Thinkingツールでモデル自身に判断させるほうが良い結果につながるという結論

---

## セッション14：Build a production-ready agent with Claude Managed Agents

<https://www.youtube.com/watch?v=jWWsLe4Gh5Y>

**登壇者**：Michael Cohen（Anthropic）

Managed Agentsの4つのコアプリミティブ（Agent・Environment・Session・Events）を解説し、M&A分析ツール「Deal」をBunとAnthropicSDKでライブコーディングするワークショップです。

**Outcomes** 機能が特に注目されました。ファイルまたはテキストblobとして **ルーブリック（仕様書）** をClaudeに渡すと、ClaudeはそのルーブリックをFirst passで実装し、 **満たすまで自律的にループして自己検証・改善** を繰り返します。Michael Cohenは「エージェントを成功に導く最良の方法」と表現しました。

Managed Agentsが提供するその他の機能は以下のとおりです。

* **Credential vaults**：MCP認証トークンを安全に保管。Claudeのコンテキストウィンドウに一切入らず、必要なときだけ注入
* **Memory stores**：読み書き可能なメモリストア。セッションをまたいでClaudeが学習・改善する
* **マルチエージェントオーケストレーション**：独立コンテキストウィンドウを持つサブエージェントをClaudeが生成

デモではM&A分析エージェントがコーディネーターとして4つのサブエージェント（マクロトレンド調査・財務分析など）を生成し、各エージェントが並列でLinear MCPやウェブ検索を活用しながら分析を進める様子が披露されました。

Claude Code内には **Claude API skill** がデフォルトで搭載されており、このスキルによりClaude CodeがManaged Agents APIを含むAnthropic APIを正確に使えるようになっています。

!

**サマリ**

* Managed Agentsを使ってM&A分析エージェントをゼロから本番まで構築するライブコーディングワークショップ
* Outcomes機能（ルーブリックベースの自己改善ループ）とマルチエージェントオーケストレーションのデモが中心

---

## セッション15：Building AI-native at enterprise scale: monday.com, Doctolib, and Delivery Hero

<https://www.youtube.com/watch?v=XFaeIbL-lvE>

**登壇者**：Ruslan Semenov（Engineering Director, monday.com）・Alex Kaluzny（CTO, Doctolib）・Rodrigue Schäfer（VP Platform, Delivery Hero）・Rebecca Harbeck（Anthropic、モデレーター）

ヨーロッパを代表するテック企業3社が、Claudeへの異なるアプローチと教訓を語ったパネルセッションです。

なかでも際立った数字を示したのが **Delivery Hero（Herogen）** の事例です。Jiraからタスクを拾い、コードを書き・テストし・PRを提出するまでを自律的に行う「Herogen」エージェントの実績は以下のとおりです。

* **1日100本以上** のPRを自動マージ（全PRの約9%）
* 割り当てられたタスクの **成功率85%**
* 2026年Q1の当初目標の **18倍** を達成
* クロスリポジトリ変更を以前の数日から **数分** で完了

Rodrigue Schäferは「エージェント型開発とは、厳密な構文ではなく自然言語で意図を伝え、開発者の介入を最小限にしながら目的を達成することだ」と語りました。

**Doctolib** は規制の厳しいヘルスケア業界で、エンジニアリング組織全体にClaude Codeのガバナンスを確立しました。 **monday.com** はコードを書いたことのないユーザーが使えるプロダクト内機能としてClaudeを統合するという、異なるアプローチを選択しました。

!

**サマリ**

* Delivery Hero（Herogen：1日100本以上のPR自動マージ）・Doctolib・monday.comが語ったエンタープライズAI導入パネル
* 「開発者の介入を最小限にしながら意図を実現する」というDelivery Heroの設計哲学が印象的

---

## セッション16：Running an AI-native engineering org

<https://www.youtube.com/watch?v=IA5LWIGqnyM>

**登壇者**：Fiona Fung（Manager of the Claude Code and Cowork Team, Anthropic）

エージェント型コーディングが「個人ツール」から「組織全体のデフォルト」になったとき、ツール自体ではなくプロセスが課題になるという問いを起点に、Anthropicのエンジニアリング組織運営の変化を語ったセッションです。

Fionaは「コーディングはもはやボトルネックではない」と述べ、上流（計画・設計）と下流（検証・レビュー・維持管理）のプロセスを見直す必要性を強調しました。

組織内で見直したルールの主なものは以下のとおりです。

* **議論よりコードを書く**：設計を言葉で議論する代わりに、複数のPRを生成して比較する
* **設計書よりプロトタイプ**：詳細な設計ドキュメントを書く文化から、PRやプロトタイプで議論する文化へ
* **バグはユーザーに届く前に自動で捕まえる**：テストを早い段階に組み込み、問題を下流に流さない
* **「Claudeでできるならやらせる」を合言葉に**：コードを書くたびに「これはClaudeに任せられるか」と自問する
* **古いプロセスは意識的に手放す**：AIで不要になったルールは放置すると残り続けるため、廃止の判断を明示的に行う

採用では製品センスを持つビルダーとシステム専門知識のあるエキスパートを重視し、マネージャー全員がまず自ら手を動かすエンジニアとして参加する体制にしています。

![AI時代の組織ルール変更](https://static.zenn.studio/user-upload/deployed-images/dcc09052d2f3d28ac6a469de.png?sha=37cfacbd72b4acdcefad44789bf14ddcc7c8b276)  
*AI時代の組織ルール変更 — 設計書よりプロトタイプ・議論よりコード・Claudeでできるならやらせるという5つの組織ルールを従来と比較した*

!

**サマリ**

* コーディングがボトルネックでなくなった後の組織設計をAnthropicの視点で語ったセッション
* 議論よりコード・設計書よりプロトタイプ・Claudeでできるならやらせるという3つが組織文化として定着している

---

## セッション17：The capability curve

<https://www.youtube.com/watch?v=DNRddIEoH3c>

**登壇者**：Jeremy Hadfield（Anthropic）

「 **Anthropicで書かれるソフトウェアのほとんどは、今やClaudeが書いている** 」というメッセージを起点に、過去1年間のコーディング能力の向上をベンチマークで示したセッションです。この向上曲線を **「ケイパビリティカーブ」** と呼び、プランニング・エラーリカバリー・長期タスクの推論という3軸での改善が現場を変えつつあると強調しました。

開発者への示唆として、急速に進化するモデルをアプリケーションに組み込む戦略と、その前提となる評価フレームワークの構築が中心テーマになりました。

![コーディング能力のケイパビリティカーブ](https://static.zenn.studio/user-upload/deployed-images/eb8a80ccc947ab0a7e04afb3.png?sha=552ee881409e05cb55383a46275e6c8b08b6c5a6)  
*コーディング能力のケイパビリティカーブ — プランニング・エラーリカバリー・長期タスク推論の3軸で急速に向上したモデルの能力変化を表した*

!

**サマリ**

* モデルのコーディング能力が急速に向上していることをベンチマーク（ケイパビリティカーブ）で示したセッション
* 「Anthropicで書かれるソフトウェアのほとんどは今やClaudeが書いている」という現実を会場全体に示した

---

## セッション18：Building signals that trade themselves

<https://www.youtube.com/watch?v=EOg4gY0Yln0>

**登壇者**：Tushara Fernando（Managing Director – Head of Data and AI, Man Group）

2,000億ドルを超える資産を運用するオルタナティブ投資会社Man Groupが、AIによる取引シグナルを実際の資本運用に組み込むまでの経緯と設計思想を語ったセッションです。アイデア立案・データ取得・バックテスト・提案書作成・本番化までをAIが担い、 **全アウトカムのレビューだけ人間が行う** 体制です。

ただし、導入の過程では大きな失敗もありました。最初は「まず使ってもらう」を優先してハッカソンやワークショップを積極的に開いたところ、スキルを書くのが業務責任者ではなく一部のパワーユーザーに偏ってしまいました。その結果、経費精算スキルのコードに特定部門のコストセンターがハードコーディングされ、別部門に大量の精算が届くという事態が起きました。

この失敗を受けて構築したのが **スキルガバナンスフレームワーク** です。全スキルを組織内のマーケットプレイスで一元管理し、業務責任者がスキルのオーナーになる体制に改めました。公式スキルと現場発のコミュニティスキルの2層構造で、現在1,700名中 **750名** が利用し、管理済みスキルは **100本以上** が稼働しています。

「 **自社に蓄積された知識や文脈こそが武器になる。それはAIベンダーが用意してくれるものではない** 」というのがセッションのキーメッセージです。

!

**サマリ**

* Man GroupのAI活用と、スキルガバナンス設計の変遷を語ったセッション
* 「まず使ってもらう」優先で失敗し、ガバナンス体制を作り直した実体験が具体的
* 「自社の文脈はAIベンダーが用意してくれない」がキーメッセージ

---

## セッション19：Build AI agents using Claude in Microsoft Foundry

<https://www.youtube.com/watch?v=TQd_YQvydVg>

**登壇者**：Marlene Mhangami + Liam Hampton + Chris Noring（Microsoft）

Microsoft Foundry上にClaude Sonnet 4.6をセットアップし、MCPサーバーに接続してエージェントを構築するハンズオンワークショップです。カップケーキショップ「Sparkles」の[AIエージェント](https://zenn.dev/umi_mori/books/generative-ai-glossary/viewer/what-is-ai-agent)を実際に構築し、参加者が本物のカップケーキを注文・受け取るライブデモで会場を盛り上げました。

**Microsoft Foundry** は1,400以上のコネクターとMCPツールを持つ統合AIプラットフォームです。Microsoft Defender・Purview・Entra IDと統合したエンタープライズセキュリティがビルトインで提供されます。

ワークショップの構成は以下のとおりです。

1. FoundryにClaude Sonnet 4.6をデプロイ → プレイグラウンドでシステムプロンプトをテスト
2. VS Codeへ接続（ターゲットURIとAPIキーをFoundryの詳細タブから取得して.envに設定）
3. **Microsoft Agent Framework**（Python）でcupcake-agentを定義
4. Sparklesカップケーキショップの **MCPサーバー** に接続（URLを1本指定するだけで全APIが利用可能）
5. MCPのプロンプトからエージェントのウェルカムバナーと指示を読み込む

MCPが提供する3種類のリソース（Tools・Prompts・Resources）を通じて、エージェントがメニュー情報・顧客登録・注文処理を処理する様子が実演されました。

![Microsoft Foundryでのエージェント構築フロー](https://static.zenn.studio/user-upload/deployed-images/7a9879355728daebfa62a17f.png?sha=d55e408b507086932973dbaaf5ca4df29d91d272)  
*Microsoft Foundryでのエージェント構築フロー — FoundryへのデプロイからVS Code接続・Agent Framework定義・MCPサーバー接続まで5ステップで構築する流れ*

!

**サマリ**

* Microsoft FoundryでClaude Sonnet 4.6をデプロイし、MCPサーバーと接続してエージェントを構築するワークショップ
* カップケーキ注文のライブデモで、参加者が実際にエージェント経由でカップケーキを注文・受け取るという体験型演出が特徴

---

## セッション20：What legal agents inherit from coding agents: Lessons from Legora

<https://www.youtube.com/watch?v=nho1YAEPuwA>

**登壇者**：Jakob Emmerling（Staff Software Engineer, Legora）

コーディングエージェントの設計原則を法律AIエージェントにどう適用したかを、 **「再利用（Reuse）・翻訳（Translate）・発明（Invent）」** の3パターンで整理したセッションです。文書編集・リンティング・一括レビューといった法律業務特有のタスクに対して、コーディングエージェントの知見がどこまで通用し、どこから新規開発が必要だったかが解説されました。

Legoraはスウェーデン発のリーガルAIスタートアップで、1,000社以上の法律事務所・企業が利用しています。このセッションの主張は、 **コーディングエージェントとリーガルエージェントは本質的に同じ構造を持っている** というものです。具体的には、次のような共通点が挙げられました。

* テキストを正確に扱う作業で、ミスが直接結果に響く
* コードライブラリと条項ライブラリのように、テンプレートやパターンの再利用が基本
* バージョン管理・反復・チーム協働が前提になっている
* コードベース全体や案件履歴のような、大量のコンテキストをまたぐ推論が必要

こうした共通点があるからこそ、Cursorやコーディングエージェントで培われた設計パターンの多くがそのまま法律領域に「再利用」でき、一部は法律業務向けに「翻訳」し、残りだけを「発明」すればよかった、というのがLegoraの結論です。

!

**サマリ**

* コーディングエージェントの設計原則を法律ドメインに転用した際の「再利用・翻訳・発明」の3パターンを語ったセッション
* コーディングとリーガルは「テキスト中心・テンプレート依存・低いエラー許容度」など構造的に共通するという主張が軸
* 垂直特化ドメインへのエージェント展開における汎化可能な知見が中心

---

## セッション21：Building with Claude on Google Cloud

<https://www.youtube.com/watch?v=l8fxVYIP4HQ>

**登壇者**：Ivan Nardini（Developer Relations Engineer (AI/ML), Google Cloud）

Vertex AI上のClaudeとGoogle ADK（Agent Development Kit）を使い、 **30分以内にゼロからデプロイまで** 完了するライブビルドワークショップです。PM・UXデザイナー・ソフトウェアエンジニア・セキュリティエンジニア・データアナリストの5つのロールにまたがるフィードバックアプリを、サブエージェント・MCPサーバー・カスタムスキルを組み合わせて構築し、セッション終了時に参加者がそのままリアルタイムで試用できる状態まで仕上げました。

!

**サマリ**

* Google Cloud上でClaudeを使い30分でアプリを本番デプロイするライブビルドワークショップ
* Vertex AIとGoogle ADKを組み合わせてエージェントを構築するアプローチが軸
* 5つの開発ロールをカバーするフルライフサイクルのデモが特徴

---

## セッション22：Build a proactive agent workflow with Claude Code

<https://www.youtube.com/watch?v=eSP7PLTXNy8>

**登壇者**：Maya Nielan（Anthropic）

**Routines** を使ってClaude Codeを「enterを押して待つツール」から「問題に気づいて自分で動くチームメイト」に変える方法を解説したワークショップです。

従来のCron+エージェント構成には、ラップトップを閉じると処理が終了する・cronのインフラ管理が煩雑・ヘッドレスセッションの監視が難しい、という3つの課題がありました。Routinesはこれらをまとめて解決します。定義するのは **プロンプト・接続するリポジトリ・コネクター・トリガー** の4つだけで、ホスティング・セッション状態・コネクター認証はClaude Codeが処理します。

Routine設計の3つの判断は以下のとおりです。

* **Trigger（いつ起動するか）**：スケジュールベース（毎週月曜10時など）またはイベントベース（GitHubイベント・カスタムWebhook）
* **Context（何を与えるか）**：リポジトリ・ファイル・コネクター（Slack・Google Drive・GitHub MCP等）。「Claudeが持てるコンテキストが成功の上限になる」
* **Steerability（品質をどう担保するか）**：エージェント・オン・エージェントレビュー（ジェネレーター・クリティークパターン）またはClaude Code on webでのリアルタイム監視・操舵

実例として紹介されたのはAnthropicのドキュメント自動化です。Claude CodeのPRが年初から **200%増加** したことで、ドキュメント担当エンジニアが対応しきれない状況が生まれ、以下の2つのRoutineで自動化されています。

1. **週次ドキュメント同期**：毎週月曜10時にソースコードとドキュメントの差分を確認 → PRを作成
2. **GitHub Issue対応**：Issueがオープンされたとき → ドキュメントギャップを調査 → PRを作成 → Slackで通知

ライブデモでは、GitHubでIssueを作成した直後にRoutineがトリガーし、セッション進行中に「この変更は既に済んでいます」と入力してリアルタイムで軌道修正できる様子が示されました。

!

**サマリ**

* Routinesを使ってClaude Codeをプロアクティブなチームメイトにするワークショップ
* `/schedule` コマンド1つで作成でき、スケジュール・GitHubイベント両方をトリガーに設定できることをライブデモで実演
* Anthropic社内でのドキュメント自動化という実例を通じて、3つの設計判断（Trigger・Context・Steerability）を体系的に整理

---

## セッション23：Getting more out of the Claude Platform

<https://www.youtube.com/watch?v=QIriO1-vHYw>

**登壇者**：Punit Shah（Anthropic）

コスト削減・コンテキスト管理・インテリジェンス向上の3軸で、Claudeプラットフォームの最新機能を活用する方法をライブデモで紹介したセッションです。

紹介された主なパターンは以下のとおりです。

* **プロンプトキャッシング**：繰り返し使うシステムプロンプトをキャッシュしてAPIコストを最大1/10に削減
* **Tool search（ツールサーチ）**：多数のツールが定義されている場合に、コンテキストウィンドウを圧迫せず必要なツールだけを動的に取得する仕組み
* **Programmatic tool calling（プログラマティックなツール呼び出し）**：ツールをAPIの往復ではなくコードでオーケストレーションする手法。75個のツールを持つプロジェクト管理エージェントのベンチマークでは、タスク精度を保ったまま課金対象の入力トークンを約38%削減
* **Compaction（コンパクション）**：会話が一定のコンテキスト上限に近づくと、古い文脈を自動で要約・圧縮し、長時間タスクでもウィンドウ上限に達しないように管理する手法
* **Advisorストラテジー**：コスト効率の良いモデル（Sonnet 4.6やHaiku 4.5）がタスクを実行し、複雑な判断が必要なときだけ同じAPIコール内でClaude Opus 4.6に助言を求める設計パターン。SWE-bench Multilingualで2.7ポイントの精度向上と11.9%のコスト削減を両立

![Claude Platformのコスト・精度最適化パターン](https://static.zenn.studio/user-upload/deployed-images/602bb3bd2e07de91472ffd43.png?sha=5a87a2f74dcccd705005feb3a2e11a95b28e5759)  
*Claude Platformのコスト・精度最適化パターン — プロンプトキャッシング・ツールサーチ・コンパクション・Advisorストラテジーを組み合わせてコストと精度を両立する5つの手法*

!

**サマリ**

* プロンプトキャッシング・ツールサーチ・コンパクション・Advisorストラテジーを活用してAPIのコストと精度を最適化する実践的なセッション
* プログラマティックなツール呼び出しで入力トークン約38%削減、Advisorストラテジーで精度向上とコスト削減を両立といった具体的な数字も提示

---

## セッション24：The prompting playbook

<https://www.youtube.com/watch?v=G2B0YWuJUgI>

**登壇者**：Margot van Laar（Anthropic）

プロンプティングは今もAIシステム構築の最重要スキルです。「既存プロンプトをモデル移行で修正する」「ゼロからエージェントを構築する」という2つのシナリオをEval駆動で体系的に改善するプロセスをライブデモで解説したワークショップです。

通信会社「Meridian Mobile」のカスタマーサポートBotを題材に、5つのテストケース（コントロール・計算・ポリシー・エスカレーション・ホットスポット）に対してプロンプトを段階的に改善していく様子が実演されました。

まず行うべき基本整備として、XMLタグで構造化・冗長な指示の削除・出力フォーマットの定義が挙げられました。プロンプトを読んでガイドラインとポリシーとデータが区別できないなら、モデルにも区別できていない、というのが実務上の指針です。

続いて、失敗したケースを1つずつ原因ごとに修正しました。

* **ホットスポット不開示**：古い防御的なパッチ指示が新モデルで逆効果に。モデルは[幻覚](https://zenn.dev/umi_mori/books/generative-ai-glossary/viewer/what-is-hallucination)するだけでなく、知っている情報をあえて出力しないこともある。プロンプトのバージョン管理で変更理由を記録することが推奨された
* **日割り計算の精度不足**：**指示は能力を追加しない**。計算が必要なら計算ツールを与えるのが正しいアプローチ
* **エスカレーション不足**：コストの片面（$8）だけを伝えていた。 **トレードオフの両面を伝える** ことで、モデルが状況に応じて適切に判断できる

新規エージェント構築のシナリオでは、週次スタッフシフトスケジューリングを題材に複数のアプローチを比較しました。

| アプローチ | 結果 |
| --- | --- |
| シンプルなプロンプト + Sonnet 4.6 | 5/5 失敗 |
| Opus 4.7（プロンプトそのまま） | 5/5 失敗だが違反数が大幅減少 |
| Opus 4.7 + Adaptive thinking | 安定成功（トークン3倍・レイテンシ3倍） |
| **生成→評価→修復のエージェントループ** | **5/5 成功・低トークン・低レイテンシ** |

「 **1つの巨大プロンプトより、生成・評価・修復の3つのシンプルなプロンプトに分けるほうが精度・効率ともに優れている** 」というのが最大の教訓です。エージェント型の評価ループには、Pythonコードを変更せずソフト制約をランタイムで追加できるという追加メリットもあります。

![プロンプティングの3つの教訓](https://static.zenn.studio/user-upload/deployed-images/75a195735b107f48afcdd1c6.png?sha=4781be7f0381546ad968cf107cd756e9bf7feba3)  
*プロンプティングの3つの教訓 — 「指示は能力を追加しない」「トレードオフの両面を伝える」「1つより3つのシンプルなプロンプト」という実践的な3原則*

!

**サマリ**

* 既存プロンプトのモデル移行と新規エージェント構築という2シナリオをEval駆動で体系的に改善するワークショップ
* 「指示は能力を追加しない（ツールを与えよ）」「トレードオフの両面を伝えよ」「1つの大きなプロンプトより3つの小さなプロンプト」という3つの教訓が核心

---

## 全体を通じた3つの共通テーマ

24セッションを通じて、複数の登壇者が共通して語っていた学びを3点に整理します。

![ロンドン編 3つの共通テーマ](https://static.zenn.studio/user-upload/deployed-images/750c50373c992da521cb9a57.png?sha=38b3b677c6de0e16484ad5db7338b213c5ab55c5)  
*ロンドン編 3つの共通テーマ — エージェントはすでにインフラ・自社コンテキストが競争優位・コスト×品質はプロンプトで設計、という24セッションを貫く共通テーマ*

### 1. エージェントはすでにインフラになった

Managed Agents・Routines・Self-hosted sandboxes・Delivery Heroのヘロゲン・SpotifyのHonkなど、今回のセッションではエージェントを「対話するアシスタント」としてではなく、 **システムインフラの構成要素として組み込む** 事例が多く登場しました。

Delivery Heroは1日100本以上のPRを自動マージするエージェントを本番運用し、SpotifyではHonkとFleetshiftを組み合わせたFleet Managementシステムが累計250万本以上の自動PRをマージしています。Man GroupではAIが考案した取引シグナルが実際の資本を運用しています。

Michael Cohenが「ボトルネックはモデルの知性ではなくインフラだ」と指摘したように、エージェントをどう安全に・大規模に・観測可能な形で動かすかというインフラ面の整備が、今の開発現場の実質的な課題になっています。

### 2. 組織のコンテキストが最大の競争優位になる

Man Groupのスキルガバナンス・Spotify 15年分のインフラ・Delivery HeroのHerogen。3社に共通するのは、AIの性能そのものではなく **自社固有の文脈（コンテキスト）をいかにAIに与えるか** が差別化の源泉だという認識です。

Tushara Fernandoは「AIベンダーは自社固有のコンテキストを解決してくれない。そのデータはインターネット上には存在しない」と語りました。Spotifyが強調した「コードの一貫性がClaude Codeのパフォーマンスの上限を決める」という言葉も、組織のインフラとプロセスへの長期投資が先行条件であることを示しています。

単純にClaude Codeを導入するだけでは組織固有の生産性は得られません。スキル設計・CLAUDE.md・データレイヤーへの投資を通じて、自社の文脈をClaudeに教え込む作業こそが、今後の競争優位を決定づけます。

### 3. コストと品質のトレードオフはプロンプトで設計する

「モデル選択」「思考量の調整」「プロンプト設計」を扱った3つのセッションに共通していたのは、コストと品質のトレードオフは設計の問題であり、「とりあえず大きいモデルを使う」という判断は最適ではないという主張です。

* 「正しいモデル = 成功アウトカムあたり最安のモデル」（Picking the right model）
* 「タスクに少しでも知性が必要なら低Effortでも大きいモデルを使う。小モデルは分類・要約・抽出のみ」（The thinking lever）
* 「指示は能力を追加しない。計算が必要ならツールを与えよ」（The prompting playbook）

プロンプトキャッシング・コンテキスト設計・Advisorパターン・生成→評価→修復ループを組み合わせれば、コストを下げながら品質を上げることは十分に実現できます。

---

## まとめ

Code with Claude 2026 ロンドン編は、エージェントが「AIツール」から「組織インフラの一部」へと移行しつつあることを示すイベントでした。Self-hosted sandboxesとMCP tunnelsという新機能発表に加え、Delivery Hero・Man Group・Spotifyというヨーロッパ企業の本番事例が多く登場し、AIエージェントの活用が「実験」フェーズを超えて「運用」フェーズに入っていることが示されました。

サンフランシスコ編のまとめはこちらからご覧いただけます！

<https://zenn.dev/galirage/articles/code-with-claude-2026-sf-summary>

Tokyo編（6月10日）のまとめも公開予定ですので、ぜひお楽しみに！

## 最後に

最後まで読んでくださり、ありがとうございました！  
この記事を通して、少しでもあなたの学びに役立てば幸いです✨

## 参考文献

<https://claude.com/blog/code-w-claude-london-2026-rethinking-how-we-build>

<https://claude.com/code-with-claude/london>

<https://engineering.atspotify.com/2026/6/code-with-claude-coding-is-no-longer-the-constraint>

<https://claude.com/customers/delivery-hero>

<https://claude.com/customers/spotify>

<https://www.youtube.com/watch?v=6amLO7I9xdg>

<https://www.youtube.com/watch?v=sRvUXLquiRg>

<https://www.youtube.com/watch?v=IGo225tfF2I>

<https://www.youtube.com/watch?v=P0uMXS6emHA>

<https://www.youtube.com/watch?v=zFslvuvYifQ>

<https://www.youtube.com/watch?v=Uvl-tRga98g>

<https://www.youtube.com/watch?v=tuY2ChJIx48>

<https://www.youtube.com/watch?v=zenIB7XLZxQ>

<https://www.youtube.com/watch?v=VueeyKcquoA>

<https://www.youtube.com/watch?v=wI0ptqCSL0I>

<https://www.youtube.com/watch?v=5YHIrTYxM3w>

<https://www.youtube.com/watch?v=mhW-XXnDFSU>

<https://www.youtube.com/watch?v=DNRddIEoH3c>

<https://www.youtube.com/watch?v=jWWsLe4Gh5Y>

<https://www.youtube.com/watch?v=XFaeIbL-lvE>

<https://www.youtube.com/watch?v=IA5LWIGqnyM>

<https://www.youtube.com/watch?v=EOg4gY0Yln0>

<https://www.youtube.com/watch?v=TQd_YQvydVg>

<https://www.youtube.com/watch?v=nho1YAEPuwA>

<https://www.youtube.com/watch?v=l8fxVYIP4HQ>

<https://www.youtube.com/watch?v=eSP7PLTXNy8>

<https://www.youtube.com/watch?v=QIriO1-vHYw>

<https://www.youtube.com/watch?v=G2B0YWuJUgI>
