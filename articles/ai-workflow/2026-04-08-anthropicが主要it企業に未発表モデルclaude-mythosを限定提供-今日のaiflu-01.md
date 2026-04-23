---
id: "2026-04-08-anthropicが主要it企業に未発表モデルclaude-mythosを限定提供-今日のaiflu-01"
title: "Anthropicが主要IT企業に未発表モデル「Claude Mythos」を限定提供 今日のAI・Flutterニュース10選【2026/04/08】"
url: "https://note.com/blur_brah_lab/n/n1e01f49cfd10"
source: "note"
category: "ai-workflow"
tags: ["note"]
date_published: "2026-04-08"
date_collected: "2026-04-08"
summary_by: "auto-rss"
---

---

  

## Claude / Anthropic系

---

### Claude Codeに `/powerup` コマンド登場——ターミナルを出ずに18のインタラクティブ講座が受けられる

**何が追加されたか：** 2026年4月1日リリースのClaude Code v2.1.90で `/powerup` コマンドが追加。ターミナル内でアニメーション付きの対話型チュートリアルが起動し、Claude Codeの主要機能を実際に動かしながら学べる。

**収録されている18講座：** コンテキスト管理・Hooks・MCP・サブエージェント・`/loop`コマンドなど、多くのユーザーが見落としがちな機能をカバー。1講座あたり3〜10分で完了できる設計。

**対象ユーザー：** サブスクリプションプランを問わず全ユーザーが無料で利用可能。VSCode拡張機能でのUI展開も予告されており、今後さらに進化する見込み。

ソース：<https://daily1bite.com/en/blog/ai-tutorial/claude-code-april-2026-update>

---

### Anthropicが主要IT企業に未発表モデル「Claude Mythos」を限定提供——防衛的サイバーセキュリティ用途に限定

**Project Glasswingとは：** Anthropicが最先端モデル「Claude Mythos」のプレビューをAWS・Apple・Cisco・CrowdStrike・Google・Microsoft・Nvidiaなどの大手企業に限定公開している。用途はサイバーセキュリティの防衛目的に限定され、攻撃的利用は禁止。

**エンタープライズ急拡大：** 2026年4月時点でAnthropicに年間100万ドル以上を支払う企業は1,000社超（2ヶ月前比2倍）。BlacstoneやH&Fなど大手PEファンドとの共同事業も交渉中。

**開発者への示唆：** まだ一般公開されていないモデルが実は存在し、すでに本番稼働している。Anthropicの製品ロードマップが「公開モデル」だけで語れない段階に入ったことを示す。

ソース：<https://fortune.com/2026/04/07/anthropic-claude-mythos-model-project-glasswing-cybersecurity/>

---

## OpenAI / Codex系

---

### OpenAI Codexのモデルラインナップ刷新——旧モデル群が4月14日に完全退役

**モデル整理の概要：** 4月7日より `gpt-5.2-codex` `gpt-5.1-codex-mini` `gpt-5.1-codex-max` `gpt-5.1` などがモデルピッカーから非表示に。4月14日に完全退役となる。

**今後使えるモデル：** `gpt-5.4` `gpt-5.4-mini` `gpt-5.3-codex` `gpt-5.2` の4種が引き続き利用可能。ChatGPT Proユーザーはさらに `gpt-5.3-codex-spark`（1,000+ TPS）も選択可能。

**開発者への影響：** Codex APIを組み込んだワークフローを持つ開発者は、退役モデルを参照していないか今すぐ確認が必要。4月14日を過ぎるとリクエストがエラーになる。

ソース：<https://releasebot.io/updates/openai/codex>

---

### Qodoが$7,000万調達——AIが書いたコードを検証する「コードレビューAI」が急成長

**Qodo 2.0の仕組み：** 2026年2月にリリースされたQodo 2.0はマルチエージェント型レビューアーキテクチャを採用。バグ検出・コード品質・セキュリティ・テストカバレッジの4エージェントが並列で動作し、F1スコア60.1%と他社7ツールを上回るベンチマーク結果を達成。

**資金調達と実績：** Qumra Capital主導のシリーズBで$7,000万（累計$1億2,000万）を調達。Nvidia・Walmart・Red Hat・Intuitなど大手企業が導入済み。2025年にはGartner Magic QuadrantでVisionaryに認定。

**Flutterエンジニアへの視点：** AIが書いたコードをAIがレビューするスタックが整いつつある。PR作成から品質保証まで人間の介入を最小化するワークフローが、個人開発でも現実的になってきた。

ソース：<https://techcrunch.com/2026/03/30/qodo-bets-on-code-verification-as-ai-coding-scales-raises-70m/>

---

## Cursor系

---

### CursorがセルフホストCloud Agentsをリリース——コードを社内に留めたままAIエージェントを動かせる

**何が変わったか：** Cursorのクラウドエージェントがセルフホスト対応に。コードベース・ビルド成果物・シークレットが外部に出ず、すべて自社インフラ内で完結する。アウトバウンド接続のみでVPNや開放ポートが不要な設計。

**技術仕様：** 1ユーザーあたり最大10ワーカー、1チームあたり最大50ワーカー。分離VM・フル開発環境・マルチモデルハーネス・プラグインはクラウド版と同等機能。Brex・Money Forward・Notionが早期採用済み。

**エンタープライズ採用の加速：** 金融・医療など厳格なデータガバナンスが求められる業種でのCursor導入障壁が大幅に下がった。業務委託でセキュリティ要件が厳しいプロジェクトでも選択肢に入ってくる。

ソース：<https://cursor.com/blog/self-hosted-cloud-agents>

---

### Cursor 3、Composer 2搭載——リアルタイムRLで5時間ごとに賢くなるコーディングモデル

**Composer 2とは：** Cursor 3と同時にリリースされたComposer 2は、困難なコーディングタスクでフロンティアレベルの性能を発揮。実ユーザーとのインタラクションをリアルタイムRLに使い、5時間ごとに改善済みチェックポイントをデプロイしている。

**Design Modeの詳細：** Agents Windowから起動できる新機能。ブラウザレンダリングしたUI要素をクリック・ドラッグで直接アノテーションし、AIに指示できる。テキストで説明するより精度が上がり、フロントエンド改修のターンアラウンドが短縮。

**Cursor 3の位置づけ：** 「コードを書くIDE」から「エージェントを管理するプラットフォーム」へのシフトが完結。Cursor自身のPRの1/3以上がすでにエージェント生成であることを公表している。

ソース：<https://cursor.com/blog/cursor-3>

---

## Flutter / Dart系

---

### Flutter 4.0ロードマップが明らかに——Impeller 2.0・Dart 4.x・デザインレイヤー分離が核心

**Flutter 4.0の主要変更：** 次世代レンダリングエンジン「Impeller 2.0」でさらなるGPU最適化、Dart 4.xとの統合、マテリアルデザインからのデザインレイヤー分離が主な柱。デザイン分離が完了次第リリースとされ、2026年中盤が目安。

**なぜ重要か：** デザインレイヤーの分離によってFlutterウィジェットとMaterial 3の結合が解除され、独自デザインシステムを持つプロダクト開発が大幅に楽になる。エフェメラルコードとの組み合わせでアプリのオンデマンド更新にも道が開ける。

**Google I/O 2026（5月19〜20日）での発表に注目：** 正式アナウンスはGoogle Cloud Next（4月22〜24日）またはGoogle I/O（5月19〜20日）が有力。Flutter本業エンジニアは両イベントをウォッチしておくのが必須。

ソース：<https://ripenapps.com/blog/flutter-4-0-outlook-new-features/>

---

### FlutterFlow、2026ロードマップ策定中——コミュニティ投票でAI・バックエンド機能が最優先課題に

**現状のFlutterFlow：** ノーコード/ローコードでFlutterアプリを構築できるビジュアルツール。2026年ロードマップの策定にコミュニティが参加できる形で意見募集中。

**優先課題として浮上：** AI連携機能（LLMウィジェット・プロンプト管理）、バックエンドロジックの柔軟化、カスタムウィジェットとの親和性向上がコミュニティからの最多リクエスト。

**プロエンジニアへの関係：** FlutterFlowがAI機能を標準搭載するほど、ノーコード層とプロコード層の境界が曖昧になる。「AIが生成したFlutterFlow成果物をプロが引き継ぐ」フローが増える可能性。

ソース：<https://community.flutterflow.io/announcements/post/help-shape-the-flutterflow-2026-roadmap-2CGlfh87hrboWKP>

---

### State of Flutter 2026——WebAssemblyデフォルト化・Android 17デイゼロ対応が2026年の2大柱

**WebAssembly（Wasm）デフォルト化：** Flutter Webの出力をWasmにデフォルト切り替えする計画が進行中。ネイティブ品質のWebパフォーマンスが標準になり、モバイルとWebの体験差が縮まる。

**Android 17デイゼロ対応：** 2026年ロードマップにAndroid 17の正式リリース日に対応済みであることが明記された。iOSも同様の方針で、OSアップデートのたびにFlutterアプリが壊れるリスクが減る。

**Dart Bytecodeインタープリタ：** 特定のコード部分をアプリストア更新なしにオンデマンドで配信できる「エフェメラルコード」機能を調査中。実現すればFlutterアプリのアップデートサイクルが根本から変わる。

ソース：<https://devnewsletter.com/p/state-of-flutter-2026/>

---

### n8n・Zapier・Vellum——AIワークフロー自動化ツールの2026年最前線

**ツールの棲み分け：** n8n（フェアコード・柔軟性重視）、Zapier（非技術者向け・シンプル）、Vellum AI（組織横断でAIワークフローを標準化したいチーム向け）が3強として台頭。LLMを使ったフロー自動化が開発ワークフローの外側でも普及している。

**Anthropic内部での実態：** ClaudeのエンジニアリングチームではClaude Code自体を使い続けた結果、Claude Codeのコードの約90%がClaude Code自身によって書かれる状態になっている。「AIがAIのコードを書く」サイクルが現実のものに。

**AWS Agent Plugins：** AWSがコーディングエージェント向けの「Agent Plugins for AWS」を提供開始。エージェントが「AWSにデプロイして」という指示を受けるだけで、アーキテクチャ提案・コスト試算・IaCコード生成まで一気通貫で実行できる。

ソース：<https://blog.n8n.io/best-ai-workflow-automation-tools/>

---
