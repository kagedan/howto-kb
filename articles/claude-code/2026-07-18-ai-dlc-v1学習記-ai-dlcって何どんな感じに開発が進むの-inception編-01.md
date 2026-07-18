---
id: "2026-07-18-ai-dlc-v1学習記-ai-dlcって何どんな感じに開発が進むの-inception編-01"
title: "AI-DLC v1学習記 AI-DLCって何？どんな感じに開発が進むの？ INCEPTION編"
url: "https://zenn.dev/tom1414/articles/112284e90afa57"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "TypeScript", "zenn"]
date_published: "2026-07-18"
date_collected: "2026-07-19"
summary_by: "auto-rss"
query: ""
---

こんにちは。  
とむです。

今回から少しずつ、**AI-DLC**について学んでいこうと思い、まずはv1のワークフローを使ってアプリ開発をしていきます！  
今回作るアプリは、「紅茶検定の初級編対策用アプリ」です。  
完全プライベート用です。

私はよくこういった壁にぶち当たります。  
「AIはサブスク契約しているけど、作りたいものがなかなか見つからないなあ。。。」と。

ただ、ちょうど良いのが見つかりました。  
最近は相方との時間が合いづらくなり、一人時間が増えたのを活用してよく地元を散策しています。  
そんななか、よく行く紅茶店に訪れ、「紅茶に詳しくなったらなんか雰囲気カッコよさそう」という単純な理由から、紅茶検定でも取ろうと思いました（多分）

# はじめに

ゆるーく、けど、AI-DLCってなんだっけーとか、どんな流れで開発が進むのー、といったところを残していけたらなと思います。  
何か間違った記載がありましたら、ご指摘ください！

# AI-DLCとは

AI-DLCとは、AI-Driven Development Life Cycleの略で、AWSが提唱する「AIが計画をたてて実行し、要所要所で人間が承認する」ソフトウェア開発の方法論だったり、仕組みだったりのことです（あくまで方法論です）。  
[AWS社提供のAI-DLCワークフローのGitHub](https://github.com/awslabs/aidlc-workflows)にて、詳細が公開されています。

色んなCoding Agentに対応しているので、今回はClaude Codeとともに開発を進めていきます。

## v1のワークフローはどんなものか

一応v2もプレビュー版でありますが、そちらは今回は割愛します。  
v1のワークフローでは、**INCEPTION**・**CONSTRUCTION**・**OPERATIONS**の３フェーズで構成されます。  
案件の複雑さに応じてステージの実行/スキップと小サイドといったところが決まっていきます。

表にすると、こんな感じです。

| フェーズ | ステージ | 実行条件 | 概要 |
| --- | --- | --- | --- |
| INCEPTION | Workspace Detection | **ALWAYS** | 既存コードの有無を調べ、Greenfield（新規）かBrownfield（既存）かを判定 |
| INCEPTION | Reverse Engineering | CONDITIONAL（Brownfieldのみ） | 既存コードベースの分析・ドキュメント化 |
| INCEPTION | Requirements Analysis | **ALWAYS**（深さは適応） | 要件を収集・整理。深さはMinimal/Standard/Comprehensiveで可変 |
| INCEPTION | User Stories | CONDITIONAL | ユーザーストーリー・ペルソナの作成 |
| INCEPTION | Workflow Planning | **ALWAYS** | どのステージを実行するか、深さはどうするかを計画し、実行順序を可視化 |
| INCEPTION | Application Design | CONDITIONAL | コンポーネント・サービス層の設計 |
| INCEPTION | Units Generation | CONDITIONAL | 開発単位（Unit of Work）への分解 |
| CONSTRUCTION | Functional Design（ユニットごと） | CONDITIONAL | 技術非依存のビジネスロジック設計 |
| CONSTRUCTION | NFR Requirements（ユニットごと） | CONDITIONAL | 非機能要件の洗い出しと技術スタック選定 |
| CONSTRUCTION | NFR Design（ユニットごと） | CONDITIONAL | 非機能要件パターンの設計への反映 |
| CONSTRUCTION | Infrastructure Design（ユニットごと） | CONDITIONAL | 実インフラサービスへのマッピング |
| CONSTRUCTION | Code Generation（ユニットごと） | **ALWAYS** | Part 1（計画）→ Part 2（生成）の2段構成でコード生成 |
| CONSTRUCTION | Build and Test | **ALWAYS** | 全ユニットのビルド・単体/結合/性能テスト手順の生成 |
| OPERATIONS | Operations | PLACEHOLDER | v1時点ではプレースホルダー。将来デプロイ・監視手順を追加予定 |

フェーズの中はかなり細かく分かれているものの、AIを中心に開発が進んでいくので、現状は思った以上に結構サクサク進んでいっています。

# AI-DLCの運用ルールについて

実際に使ってみたところ、以下の体験がありました。

1. チャット上で質問されるのではなく、mdファイルを通して質問され、ユーザーはそこにあるいくつかの選択肢から回答を選んだ
2. ステージを進む段階で、一旦の認識合わせタイムみたいな感じで、最終生成物の内容が問題ないかの承認フェーズを挟んでいた
3. audit.mdというので、チャット上でのやり取り全てがタイムスタンプ付きで記録されていた（しかも途中で指示を取りやめたものも含め、全て記録されている。。慣れない感覚なのでスギョイ）
4. aidlc-state.mdによって、プロジェクトの進捗状況が可視化（記録）されていた

と、まあこれだけ書かれていてもどんなものか分かりづらいので、それぞれ一部抜粋して載せておきます。

```
~~ 1. 質問の話 ~~

## Question 1
対象とする紅茶検定のレベル（級）はどれですか？
（紅茶検定は「ベーシック（初級）」「アドバンス（中上級）」「プロフェッショナル（上級）」の3レベルがあります）

A) ベーシック（初級）のみ

B) アドバンス（中上級）のみ

C) ベーシック＋アドバンスの両方

D) 全レベル（プロフェッショナル含む）

E) Other (please describe after [Answer]: tag below)

[Answer]: A
```

![](https://static.zenn.studio/user-upload/a3e3a63efaf3-20260718.png)

```
~~ 3. audit.mdの話 ~~

## Requirements Analysis — Partial Answer + Orchestration Policy
**Timestamp**: 2026-07-18T11:05:00Z
**User Input**: "最初は初級版を受けます。
全体の計画だてをFable5, 実装フェーズはCodex Sol, 諸々の作業はOpus4.8やSonnet5に委譲し、あなたがレビュアー担当とかになってあげてください"
**AI Response**: "Recorded Q1 = A (ベーシック/初級のみ). Recorded multi-agent orchestration policy: Fable 5 = planning & review (this session), Codex Sol = implementation phase (via codex exec CLI, v0.144.5 confirmed installed), Opus 4.8 / Sonnet 5 = delegated misc tasks (via Agent tool). Remaining questions Q2-Q8 + 3 extension opt-ins still pending — gate remains active. Presented recommended default answers for quick approval."
**Context**: INCEPTION - Requirements Analysis Step 6 (partial answers)
```

```
~~ 4. aidlc-state.md の話 ~~

## Orchestration Policy (user-defined, 2026-07-18)
| Role | Agent/Model | How |
|---|---|---|
| 計画・全体設計 (Inception) | Claude Fable 5 | このセッション本体 |
| 実装 (Construction/Code Generation) | Codex Sol | `codex exec` CLI (v0.144.5, installed) |
| 諸作業（ドキュメント・整理・生成物量） | Opus 4.8 / Sonnet 5 | Agent tool (model: opus / sonnet) |
| 事実確認・Web探索・出題範囲チェック等の軽い調査 | Haiku 4.5 | Agent tool (model: haiku)（2026-07-18 Tom指示：安いモデルで十分） |
| レビュー・承認ゲート補佐 | Claude Fable 5 | このセッション本体（実装は自分で書かずレビューに回る） |
```

細かい内容は、[リポジトリ内のコチラ](https://github.com/awslabs/aidlc-workflows/blob/main/aidlc-rules/aws-aidlc-rules/core-workflow.md)をご確認ください！

# 進捗と使っていて感じたことについて

数時間やって、INCEPTIONフェーズのWorkflow Plannningまで終わりました。  
ユーザーストーリーの作成とか、受け入れ条件について内容をチェックしてくれというタイミングもあり、ふとこう思いました。

「ちょうど今案件でやっている、アジャイルっぽいことしているなあ。。」

そうなんです。  
実はAI-DLCでは、アジャイルのスプリントと似たような手法が用いられているのです。  
それが、**ボルト**です。

## ボルトって何？

ボルトというのは、これまでのアジャイル開発のスプリントの期間をさらに縮め、数時間＋数日で回していくのが特徴です。  
そんな数時間で何ができるねんと感じる方もいますが、実際に今日、ものの数時間でINCEPTIONフェーズの5/7が終わりました。

この結果から分かるように、AIを中心とすることで高速で要件定義なりペルソナ・ストーリー設計を進められるというのが大きな特徴だと、身をもって感じました。

私のこの程度の要件だった故に数時間というのはもちろんあると思いますが、それでもこれまでアジャイルで数週間のスプリントで回していたものが、さらに短い単位で回っていくと考えるとかなり高速ですよね・・・

# 出来上がった要件定義所の紹介

レビュー待ち、と書いてあるのですが、今のところこんなものができました。  
やるならAWSも学びたい！という欲望を混ぜ込んだ内容になっています。

```
# 要件定義書 — 紅茶検定（ベーシック）対策アプリ

**作成日**: 2026-07-18
**ステージ**: INCEPTION / Requirements Analysis（Standard深度）
**ステータス**: レビュー待ち

---

## 1. 意図分析（Intent Analysis）サマリ

| 項目 | 内容 |
|---|---|
| ユーザーリクエスト | 「ai-dlcのv1を使って、紅茶検定対策アプリを作ってみたい」 |
| リクエスト種別 | New Project（新規・Greenfield） |
| スコープ見積り | Multiple Components（フロントエンド PWA / 認証 / API / DB / 学習ロジック） |
| 複雑度見積り | Moderate〜Complex（AWSフルスタック学習を兼ねるため、個人アプリとしては広め） |
| 要件深度 | Standard |

### プロジェクトの二重目的
1. **実用**: 紅茶検定ベーシック（初級）に合格するための学習ツールとして本気で使う
2. **学習**: AI-DLC方法論の体験 + AWS（認証・ユーザー管理・DB等）の実践学習 + **AWS CDKによるIaC構築の習得**（2026-07-18 追加）

---

## 2. 機能要件（Functional Requirements）

### FR-1: 一問一答クイズ
- 4択問題をランダム出題し、回答直後に正誤と解説を表示する
- 出題分野（カテゴリ）を選んで出題できる
- 間違えた問題は復習対象として記録される

### FR-2: 模擬試験モード
- 本番形式を模した通し試験（制限時間つき・採点・合否判定）
- 試験結果は履歴として保存され、分野別の正答率を確認できる
- 試験形式は公式実施概要で確定済み（2026-07-18調査）: **80問・4者択一・最大60分・合格基準 正答率70%以上・オンライン受験**（出典: kentei-uketsuke.com/sys/tea/entry）。この公式値をデフォルトとし、設定で変更可能にする

### FR-3: フラッシュカード
- 用語・茶葉・産地などの暗記カード（表：設問／裏：答えと解説）
- 「覚えた／まだ」の自己評価を記録し、FR-6の間隔反復に連動する

### FR-4: 問題データ管理
- **初期データ**: AIが紅茶の一般知識からベーシック級レベルの初期問題セット（目安50〜100問、カテゴリ・解説つき）を生成する
- **追加・編集**: アプリ上で問題の追加・編集・削除ができる
- **外部コンテンツ取込**: ユーザーが Claude Desktop 等のAIとの対話で得た紅茶検定対策コンテンツを、定義済みフォーマット（JSON等）でインポートして問題として追加できる経路を用意する（運用イメージ：Claude Desktopに「このフォーマットで問題化して」と依頼 → 出力をアプリにインポート）

### FR-5: 認証・ユーザー管理
- サインアップ／サインイン／サインアウト（AWSマネージド認証サービスの利用を想定）
- 実利用者は本人のみだが、AWS学習のため一般的なユーザー管理構成（複数ユーザー前提のデータ分離）で設計する

### FR-6: 学習進捗記録（本格）
- 正答率・解答数などの基本統計
- 分野別の弱点分析（カテゴリ別正答率の可視化）
- 学習履歴グラフ（日次の学習量・成績推移）
- 間隔反復（忘却曲線ベース）の復習スケジュール：間違えた問題・自己評価の低いカードを最適なタイミングで再出題する

### FR-7: PWA（モバイル対応）
- Next.js製Webアプリをスマホのホーム画面に追加してアプリ風に利用できる（PWA manifest / Service Worker）
- スマホファーストのUI（スキマ時間学習を想定）

---

## 3. 非機能要件（Non-Functional Requirements）

### NFR-1: 技術スタック
- フロントエンド: **Next.js + TypeScript**（PWA対応）
- バックエンド／インフラ: **AWS**（認証・DB・API・ホスティング。具体サービス選定は NFR Requirements / Infrastructure Design ステージで確定）
- **IaC: AWS CDK（TypeScript）を必須とする**。すべてのAWSリソース（認証、DB、API、ホスティング等）はCDKでコード管理し、マネジメントコンソールでの手動構築は行わない（学習目的のため、CDKコードは読んで学べるようコメント・構成を丁寧にする）
  - 副次効果: SECURITY-01/02/06/07/14 等のIaCレベル検証がCDKコード上で実施できる
- テスト: PBTフレームワークは **fast-check**（TypeScript）を第一候補とする（PBT-09）。CDKは **assertions モジュールによるスナップショット/ファインドテスト**も検討対象

### NFR-2: セキュリティ（Security Baseline 拡張 = 有効）
- SECURITY-01〜15 をブロッキング制約として全ステージで適用
- 特に重点: 認証・セッション管理（SECURITY-12）、アプリレベル認可（SECURITY-08）、入力バリデーション（SECURITY-05）、最小権限IAM（SECURITY-06）、シークレット非ハードコード

### NFR-3: テスト（PBT 拡張 = Partial）
- ブロッキング: PBT-02（ラウンドトリップ）、PBT-03（不変条件）、PBT-07（ジェネレータ品質）、PBT-08（縮小・再現性）、PBT-09（フレームワーク選定）
- 適用対象の例: 採点ロジック、間隔反復スケジューラ（忘却曲線計算）、問題データのシリアライズ/インポートのラウンドトリップ
- 例示ベーステストと併用する（PBT-10 は advisory）

### NFR-4: コスト
- 個人学習用のため、AWS無料枠〜月数百円程度で収まる構成を優先する

### NFR-5: レジリエンシー
- Resiliency Baseline 拡張は**適用しない**（個人用途。ただしデータ消失を避けるためDBのバックアップ設定など常識的な範囲は考慮する）

### NFR-6: 可用性・性能
- 利用者1名のため高可用性・スケーラビリティは要求しない
- モバイル回線でもストレスなく使える程度の応答性（ページ表示・出題操作が体感即時）

---

## 4. 制約・前提

- 対象は紅茶検定**ベーシック（初級）のみ**（アドバンス以上は将来拡張）
- 問題文・解説は著作権に配慮し、公式テキストからの転載はせず一般知識ベースでオリジナル作成する
- 開発体制（オーケストレーション方針）: 計画・レビュー = Claude Fable 5 / 実装 = Codex Sol（codex exec） / 諸作業 = Opus 4.8・Sonnet 5
- AI-DLC v1 (1.0.1) のワークフロー・承認ゲートに従って進行する

## 5. 拡張機能の適用状況

| 拡張 | 状態 |
|---|---|
| Security Baseline | **有効**（SECURITY-01..15 ブロッキング） |
| Resiliency Baseline | 無効 |
| Property-Based Testing | **Partial**（PBT-02/03/07/08/09 ブロッキング、他は advisory） |
```

# 終わりに

少し触れただけでも、この開発の方法論のスピード感を体感できたなと思っています。  
他にも、Mob ElaborationやらMob Constructionといった概念も出てくるそうなので、それはまた次回学習してまとめることにします。

運命の巡り合わせで、AI-DLCを実践投入できる案件に行けたらいいなあ（実務でやってみたい）。
