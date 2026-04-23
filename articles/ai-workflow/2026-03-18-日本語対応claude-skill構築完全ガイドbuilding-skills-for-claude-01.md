---
id: "2026-03-18-日本語対応claude-skill構築完全ガイドbuilding-skills-for-claude-01"
title: "【日本語対応】Claude Skill構築完全ガイド（Building Skills for Claude）の要約"
url: "https://zenn.dev/nishiken_zenn/articles/claude-skill-guide-summary"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-03-18"
date_collected: "2026-03-19"
summary_by: "auto-rss"
---

これは、下記の PDF を日本語で要約（AI によって大体原文の 40% 程度の内容での要約）したものです。

* Claude Skill 構築完全ガイドを読みたいが日本語で読みたい方
* 時間がなくて要点だけ知りたい方
* AI に要約させるにしても token がもったいないと思う方

に適していると思います。

> 出典: [Anthropic "The Complete Guide to Building Skills for Claude"](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)

---

## はじめに

Skill とは、Claude に特定のタスクやワークフローの処理方法を教えるための命令セットを、シンプルなフォルダとしてパッケージ化したものである。毎回の会話で好みやプロセスを再説明する代わりに、一度 Skill として教えれば毎回活用できる。繰り返し可能なワークフロー（フロントエンドデザイン生成、調査の一貫した実施、ドキュメント作成、複数ステップのプロセス管理）がある場合に威力を発揮する。MCP（Model Context Protocol: Claude が外部サービスと通信するための標準プロトコル）との連携にも対応している。

本ガイドでは、計画・構造化・テスト・配布まで、効果的な Skill 構築に必要な知識を網羅する。15〜30分で最初の動作する Skill を構築・テストできる。

### 本ガイドの2つの読み方

* **スタンドアロン Skill を構築する場合**：第1章「基礎」と第2章「計画と設計」、カテゴリ1〜2 に集中する
* **MCP 統合を強化する場合**：「Skills + MCP」セクションとカテゴリ3 を重点的に読む

両方の道筋は同じ技術要件を共有しているため、自分のユースケースに関連する部分を選んで読み進めればよい。

---

## 第1章: 基礎

### Skill の構成

Skill は以下を含むフォルダである：

* **SKILL.md**（必須）：YAML フロントマター付き Markdown の命令書
* **scripts/**（任意）：実行可能コード（Python、Bash 等）
* **references/**（任意）：必要に応じて Claude が参照するドキュメント
* **assets/**（任意）：テンプレート、フォント、アイコンなど出力に使用する素材

### 段階的開示（Progressive Disclosure）

Skill は3段階で情報を開示する：

1. **YAML フロントマター**（第1レベル）：常にシステムプロンプトに読み込まれ、Skill の使用タイミングを Claude が判断する。全内容をコンテキストに読み込むことなく、各 Skill をいつ使うべきかを Claude が知るのに十分な情報を提供する
2. **SKILL.md 本文**（第2レベル）：Claude がタスクに関連すると判断した時に読み込まれる完全な命令とガイダンス
3. **同梱ファイル**（第3レベル）：Skill ディレクトリ内にバンドルされた追加ファイルで、Claude が必要に応じてナビゲートし参照する

この仕組みでトークン使用量を最小化しつつ専門知識を保持する。

### その他の設計原則

* **構成可能性**：Claude は複数の Skill を同時に読み込める。自分の Skill が唯一の機能であると仮定せず、他の Skill と共存する設計にする
* **移植性**：Claude.ai、Claude Code、API のすべてで同一に動作する。一度作成すれば、環境が依存関係をサポートしている限り、修正なしですべてのサーフェスで動作する

### MCP との関係

MCP がツール・食材・設備（プロのキッチン）を提供し、Skill がレシピ（手順）を提供する。

**MCP と Skill の役割対比：**

| 観点 | MCP（接続性） | Skill（知識） |
| --- | --- | --- |
| 役割 | Claude をサービス（Notion, Asana, Linear 等）に接続する | Claude にサービスの効果的な使い方を教える |
| 提供するもの | リアルタイムデータアクセスとツール実行 | ワークフローとベストプラクティスの蓄積 |
| 定義 | Claude が「何を」できるか | Claude が「どのように」すべきか |

**Skill がない場合の問題：**

* ユーザーは MCP 接続後に何をすべきかわからない
* 「このインテグレーションで X をどうやるの？」というサポートチケットが発生する
* 毎回の会話がゼロからの開始になる
* ユーザーが異なるプロンプトを使うため結果が一貫しない

**Skill がある場合の利点：**

* 事前構築されたワークフローが必要時に自動起動する
* 一貫した信頼性の高いツール使用が実現する
* すべてのインタラクションにベストプラクティスが埋め込まれる
* インテグレーションの学習コストが低下する

---

## 第2章: 計画と設計

### ユースケースから始める

コードを書く前に2〜3の具体的なユースケースを特定する。「ユーザーは何を達成したいか」「どのステップが必要か」「どのツールが必要か（ビルトインか MCP か）」「どの専門知識を埋め込むべきか」を自問する。

**良いユースケース定義の例：**

```
Use Case: Project Sprint Planning

Trigger: User says "help me plan this sprint" or "create sprint tasks"

Steps:
  1. Fetch current project status from Linear (via MCP)
  2. Analyze team velocity and capacity
  3. Suggest task prioritization
  4. Create tasks in Linear with proper labels and estimates

Result: Fully planned sprint with tasks created
```

このようにトリガー条件、実行ステップ、期待する結果を明確に記述することで、Skill の設計方針が定まる。

### 2つのアプローチ：問題起点 vs ツール起点

Home Depot（ホームセンター）の例えで説明される。「キッチンの棚を直したい」という問題を持って来店し、店員が適切な工具を教えてくれる場合と、新しいドリルを買って「これを自分の作業にどう使うか」を聞く場合の2パターンがある。

* **問題起点**：「プロジェクトワークスペースを設定したい」→ Skill が適切な MCP コールを正しい順序で調整する。ユーザーは成果を記述し、Skill がツールを扱う
* **ツール起点**：「Notion MCP を接続した」→ Skill が Claude に最適なワークフローとベストプラクティスを教える。ユーザーはアクセスを持っており、Skill が専門知識を提供する

ほとんどの Skill はどちらか一方に寄る。自分のユースケースにどちらのフレーミングが合うかを把握することで、適切なパターンの選択につながる。

### 3つのユースケースカテゴリ

**カテゴリ1: ドキュメント＆アセット作成** - 一貫した高品質出力（ドキュメント、プレゼン、アプリ、コード等）の作成。スタイルガイド埋め込み、テンプレート構造、品質チェックリストが主要テクニック。外部ツール不要で Claude のビルトイン機能を使う。実例として frontend-design Skill や docx, pptx, xlsx, ppt 向けの Skill がある。

**カテゴリ2: ワークフロー自動化** - 一貫した方法論が有益な複数ステップのプロセス（複数 MCP サーバー間の連携を含む）。ステップバイステップのバリデーションゲート、テンプレート、改善ループが主要テクニック。実例として skill-creator Skill がある。

**カテゴリ3: MCP 強化** - MCP サーバーのツールアクセスを強化するワークフローガイダンス。複数 MCP 呼び出しの連続的な調整、ドメイン専門知識埋め込み、ユーザーが指定しなくても済むコンテキストの提供、エラーハンドリングが主要テクニック。実例として Sentry の sentry-code-review skill がある。

### 成功基準

定量的には、Skill が関連クエリの90%でトリガーされること、ワークフロー完了までのツール呼び出し数、API 呼び出し失敗0回を目指す。定性的には、ユーザーが次のステップを Claude に指示する必要がないこと、修正なしでワークフローが完了すること、セッション間で一貫した結果が得られることを目指す。

これらは厳密な閾値ではなく、大まかなベンチマーク（目安）である。厳密さを目指しつつ、感覚ベースの評価の要素があることを受け入れる。Anthropic はより堅牢な測定ガイダンスとツールを現在開発中である。

### 技術要件

**ファイル構造：**

```
your-skill-name/
├── SKILL.md           # 必須
├── scripts/           # 任意
│   ├── process_data.py
│   └── validate.sh
├── references/        # 任意
│   ├── api-guide.md
│   └── examples/
└── assets/            # 任意
    └── report-template.md
```

**重要なルール：**

* ファイル名は正確に `SKILL.md`（大文字小文字区別）。SKILL.MD や skill.md は不可
* フォルダ名はケバブケース（`notion-project-setup` ✅、スペース・アンダースコア・大文字 ❌）
* Skill フォルダ内に README.md は不要（すべてのドキュメントは SKILL.md または references/ に置く）

**YAML フロントマター（最重要）：**

```
---
name: your-skill-name
description: What it does. Use when user asks to [specific phrases].
---
```

name はケバブケース、description は「何をするか」と「いつ使うか」の両方を含み、1024文字以内。XML タグ（< >）は禁止。名前の接頭辞に「claude」「anthropic」は使用禁止（予約済み）。

### description の書き方

構造は `[何をするか] + [いつ使うか] + [主要な機能]`。Anthropic のエンジニアリングブログによれば「このメタデータは…全内容をコンテキストに読み込むことなく、各 Skill をいつ使うべきかを Claude が知るのに十分な情報を提供する」とされている。これが段階的開示の第1レベルである。

**良い description の例：**

```
# 良い例 - 具体的かつ実行可能
description: Analyzes Figma design files and generates developer handoff
  documentation. Use when user uploads .fig files, asks for "design specs",
  "component documentation", or "design-to-code handoff".

# 良い例 - トリガーフレーズを含む
description: Manages Linear project workflows including sprint planning,
  task creation, and status tracking. Use when user mentions "sprint",
  "Linear tasks", "project planning", or asks to "create tickets".

# 良い例 - 明確な価値提案
description: End-to-end customer onboarding workflow for PayFlow. Handles
  account creation, payment setup, and subscription management. Use when
  user says "onboard new customer", "set up subscription", or "create
  PayFlow account".
```

**悪い description の例：**

```
# 悪い例 - 曖昧すぎる
description: Helps with projects.

# 悪い例 - トリガーが欠落
description: Creates sophisticated multi-page documentation systems.

# 悪い例 - 技術的すぎてユーザートリガーがない
description: Implements the Project entity model with hierarchical
  relationships.
```

### 命令書のベストプラクティス

* 具体的で実行可能にする（「データを検証せよ」ではなく、具体的なコマンドと失敗時の対処を記述）
* エラーハンドリングを含める
* バンドルリソースを明確に参照する（例：`references/api-patterns.md` にレート制限ガイダンス、ページネーションパターン、エラーコードと処理方法がある旨を記述）
* SKILL.md はコア命令に集中し、詳細は `references/` に移動する（段階的開示の仕組みを参照）

---

## 第3章: テストと改善

### テスト方法

3つのレベルがある：

* **手動テスト**（Claude.ai）：直接クエリを実行し観察。高速、セットアップ不要
* **スクリプトテスト**（Claude Code）：反復可能なバリデーション自動化
* **プログラマティックテスト**（Skills API）：定義済みテストセットに対する体系的実行

自分の品質要件と Skill の公開範囲に応じてアプローチを選択する。少人数チーム内部で使う Skill と、数千のエンタープライズユーザーに展開する Skill では、テスト要件が異なる。

**ヒント：** 効果的な Skill 作成者は、まず単一の難しいタスクで反復し、成功したアプローチを Skill に抽出する。Claude のインコンテキスト学習を活用し、幅広いテストよりも速いシグナルを得る。動作する基盤ができたら、カバレッジのために複数テストケースに拡大する。

### 3つのテスト領域

**1. トリガーテスト** - Skill が適切なタイミングで読み込まれるか確認。明確なタスクと言い換えでトリガーされ、無関係なトピックではトリガーされないことを検証する。

**テストスイートの例：**

```
トリガーされるべきケース：
- "Help me set up a new ProjectHub workspace"
- "I need to create a project in ProjectHub"
- "Initialize a ProjectHub project for Q4 planning"

トリガーされてはいけないケース：
- "What's the weather in San Francisco?"
- "Help me write Python code"
- "Create a spreadsheet"（ProjectHub Skill がシート処理を
  含まない場合）
```

**2. 機能テスト** - 正しい出力が生成されるか検証。有効な出力、API 成功、エラーハンドリング、エッジケースをカバーする。

テスト例：

```
テスト: 5つのタスクを含むプロジェクトを作成
  前提: プロジェクト名 "Q4 Planning"、5つのタスク記述
  実行: Skill がワークフローを実行
  期待結果:
    - ProjectHub にプロジェクトが作成される
    - 正しいプロパティで5つのタスクが作成される
    - すべてのタスクがプロジェクトにリンクされる
    - API エラーが発生しない
```

**3. パフォーマンス比較** - Skill がベースラインに比べ結果を改善することを証明する。

**比較の例：**

| 指標 | Skill なし（ベースライン） | Skill あり |
| --- | --- | --- |
| やり取り回数 | 15往復 | 2回の確認質問のみ |
| API 失敗回数 | 3回（リトライ必要） | 0回 |
| トークン消費量 | 12,000トークン | 6,000トークン |
| ワークフロー | ユーザーが毎回手順を指示 | 自動的にワークフローを実行 |

### skill-creator の活用

Claude.ai のプラグインディレクトリまたは Claude Code で利用可能。

**作成機能：**

* 自然言語の説明から Skill を生成する
* フロントマター付きの適切にフォーマットされた SKILL.md を出力する
* トリガーフレーズと構造を提案する

**レビュー機能：**

* 一般的な問題（曖昧な description、トリガー不足、構造的問題）をフラグする
* 過剰/不足トリガーのリスクを特定する
* Skill の目的に基づいてテストケースを提案する

**反復的改善：** エッジケースや失敗に遭遇した後、それらの例を skill-creator に持ち込み、「このチャットで特定された問題と解決策を使って、Skill の[特定のエッジケース]の処理方法を改善して」と依頼する。

なお、skill-creator は設計と改善を支援するが、自動テストスイートの実行や定量的評価結果の生成は行わない。

### フィードバックによる反復

Skill は生きたドキュメントであり、フィードバックに基づいた反復を計画する。

* **トリガー不足**（読み込まれない、手動有効化が必要、使い方のサポート質問が来る）→ description に詳細とキーワード（特に技術用語）を追加する
* **過剰トリガー**（無関係なクエリで読み込まれる、ユーザーが無効化する、目的の混乱）→ ネガティブトリガーを追加し、より具体的にする
* **実行の問題**（一貫しない結果、API 呼び出し失敗、ユーザーの修正が必要）→ 命令を改善し、エラーハンドリングを追加する

---

## 第4章: 配布と共有

### 配布方法

個人ユーザーは Skill フォルダをダウンロードし、Claude.ai の Settings > Capabilities > Skills からアップロードするか、Claude Code の skills ディレクトリに配置する。組織レベルでは管理者がワークスペース全体に展開でき、自動更新と集中管理が行える（2025年12月18日出荷）。

### API 経由の利用

プログラマティックなユースケース（アプリケーション構築、エージェント作成、自動ワークフロー）では、API が Skill 管理と実行を直接制御する。

**主要な機能：**

* `/v1/skills` エンドポイントで Skill の一覧表示と管理を行う
* `container.skills` パラメータで Messages API リクエストに Skill を追加する
* Claude Console を通じたバージョン管理
* Claude Agent SDK との連携によるカスタムエージェント構築

\*\*API 利用には Code Execution Tool ベータが必要である。\*\*これは Skill が実行に必要とするセキュア環境を提供する。

**API の使い分けテーブル：**

| ユースケース | 最適なサーフェス |
| --- | --- |
| エンドユーザーが Skill を直接操作する | Claude.ai / Claude Code |
| 開発中の手動テストと反復 | Claude.ai / Claude Code |
| 個人のアドホックワークフロー | Claude.ai / Claude Code |
| アプリケーションで Skill をプログラマティックに使用する | API |
| 本番環境での大規模デプロイ | API |
| 自動パイプラインとエージェントシステム | API |

### オープンスタンダード

Anthropic は Agent Skills をオープンスタンダードとして公開した。MCP と同様に、Skill はツールやプラットフォーム間で移植可能であるべきとの考えに基づく。同じ Skill が Claude でも他の AI プラットフォームでも動作するべきである。ただし、特定のプラットフォームの機能を最大限活用するよう設計された Skill もあり、その場合は compatibility フィールドに記載する。

### Skill のポジショニング

成果に焦点を当て、機能ではなく価値を伝える。

* ✅ 良い例：「ProjectHub Skill により、チームはページ、データベース、テンプレートを含む完全なプロジェクトワークスペースを数秒でセットアップできる。手動セットアップの30分が不要になる。」
* ❌ 悪い例：「ProjectHub Skill は YAML フロントマターと Markdown 命令を含むフォルダで、MCP サーバーツールを呼び出す。」

MCP + Skills のストーリーも強調する：「MCP サーバーは Claude に Linear プロジェクトへのアクセスを提供する。Skill はチームのスプリント計画ワークフローを教える。両者の組み合わせで AI 駆動のプロジェクト管理が実現する。」

---

## 第5章: パターンとトラブルシューティング

以下のパターンは、早期採用者と内部チームが作成した Skill から浮かび上がったものである。一般的にうまく機能するアプローチを示しており、規範的なテンプレートではない。

### 5つの設計パターン

**パターン1: 逐次ワークフロー統合** - 特定の順序で複数ステップを実行する場合に使う。

コード例：

```
## Workflow: Onboard New Customer

### Step 1: Create Account
Call MCP tool: `create_customer`
Parameters: name, email, company

### Step 2: Setup Payment
Call MCP tool: `setup_payment_method`
Wait for: payment method verification

### Step 3: Create Subscription
Call MCP tool: `create_subscription`
Parameters: plan_id, customer_id (from Step 1)

### Step 4: Send Welcome Email
Call MCP tool: `send_email`
Template: welcome_email_template
```

主要テクニック：明示的なステップ順序、ステップ間の依存関係、各段階でのバリデーション、失敗時のロールバック手順。

**パターン2: マルチ MCP 連携** - 複数サービスにまたがるワークフロー。フェーズ分離（例：Figma MCP でデザインエクスポート → Drive MCP でアセット保存 → Linear MCP でタスク作成 → Slack MCP で通知）、MCP 間のデータ受け渡し、各フェーズ前のバリデーション、集中エラーハンドリングが特徴。

**パターン3: 反復的改善** - 反復で出力品質が向上するケース。初稿生成 → バリデーションスクリプトで品質チェック → 問題のある箇所を修正 → 再バリデーション → 品質閾値を満たすまで繰り返す、という流れ。品質基準の明示、バリデーションスクリプト、停止タイミングの把握が特徴。

**パターン4: コンテキスト対応ツール選択** - 同じ成果に対し、コンテキストに応じて異なるツールを選択する。例えばファイル保存で、大きなファイル（10MB超）はクラウドストレージ MCP、共同ドキュメントは Notion/Docs MCP、コードファイルは GitHub MCP、一時ファイルはローカルストレージというように判断する。判断基準の明確化、フォールバック、選択理由のユーザーへの説明が特徴。

**パターン5: ドメイン固有インテリジェンス** - ツールアクセスを超えた専門知識の提供。例えば決済処理のコンプライアンスチェックでは、取引処理前に制裁リストチェック、管轄許可の検証、リスクレベル評価を行い、コンプライアンスを通過した場合のみ処理を実行する。ドメイン知識のロジック埋め込み、アクション前のコンプライアンス確認、監査証跡の生成が特徴。

### トラブルシューティング

**アップロードできない場合：**

エラー「Could not find SKILL.md in uploaded folder」→ ファイル名が正確に SKILL.md（大文字小文字区別）か確認する。`ls -la` で確認する。

エラー「Invalid frontmatter」→ YAML フォーマットの問題。よくある間違いを以下に示す。

```
# 間違い - デリミタ(---)がない
name: my-skill
description: Does things

# 間違い - 引用符が閉じていない
---
name: my-skill
description: "Does things
---

# 間違い - name にスペースや大文字がある
---
name: My Cool Skill
description: Does things
---

# 正しい形式
---
name: my-cool-skill
description: Does things
---
```

**トリガーされない場合：** description が一般的すぎないか確認。ユーザーが実際に言うフレーズを含める。関連するファイルタイプがあれば言及する。Claude に「When would you use the [skill name] skill?」と聞くと、Claude が description を引用して返すため、何が欠けているかを把握してデバッグできる。

**過剰トリガーの場合：** ネガティブトリガーを追加する。例：

```
description: Advanced data analysis for CSV files. Use for statistical
  modeling, regression, clustering. Do NOT use for simple data exploration
  (use data-viz skill instead).
```

スコープを明確にする。例：「PayFlow payment processing for e-commerce. Use specifically for online payment workflows, not for general financial queries.」

**命令に従わない場合：** 命令を簡潔にし箇条書きを使用する。重要な命令を先頭に配置し、`## Important` や `## Critical` ヘッダーを使う。曖昧な言語を避け具体的な条件を明示する。

**高度なテクニック：** 重要なバリデーションは、言語命令に頼るのではなく、プログラムでチェックを実行するスクリプトをバンドルすることを検討する。コードは決定論的であり、言語の解釈はそうではない。Office 系 Skill にこのパターンの例がある。

**モデルの「怠惰さ」への対処：** 明示的な励ましを追加する。「時間をかけて徹底的に行う」「品質はスピードより重要」「バリデーションステップを省略しない」。なお、これを SKILL.md に追加するよりも、ユーザーのプロンプトに追加する方が効果的である。

**MCP 接続の問題：** Skill は読み込まれるが MCP 呼び出しが失敗する場合、以下を確認する。サーバー接続状態（Claude.ai: Settings > Extensions で「Connected」ステータスを確認）、認証（API キーの有効性、権限/スコープの付与、OAuth トークンの更新）、ツール名（大文字小文字区別で正確か、MCP サーバーのドキュメントを確認）。Skill なしで MCP を直接テストし（「Use [Service] MCP to fetch my projects」）、失敗すれば問題は MCP 側にあると切り分けられる。

**コンテキストが大きすぎる場合：** SKILL.md を5,000ワード以内に保ち、詳細を references/ に移動する。同時有効 Skill が20〜50以上の場合は選択的に有効化する。関連する機能の「Skill パック」を検討する。

---

## 第6章: リソースとリファレンス

### 公式ドキュメント

* Best Practices Guide、Skills Documentation、API Reference、MCP Documentation

### ブログ投稿

* Introducing Agent Skills、Engineering Blog: Equipping Agents for the Real World、Skills Explained、How to Create Skills for Claude、Building Skills for Claude Code、Improving Frontend Design through Skills

### サンプル Skill

* GitHub: anthropics/skills（Anthropic 作成の Skill、カスタマイズ可能）

### ツール

* **skill-creator skill**：Claude.ai / Claude Code で利用可能。説明文から Skill を生成、レビュー・改善提案も行う。「Help me build a skill using skill-creator」で起動する

### サポート

* 技術質問：Claude Developers Discord
* バグ報告：GitHub Issues（anthropics/skills/issues）。Skill 名、エラーメッセージ、再現手順を含める

---

## 付録A: クイックチェックリスト

**開始前：** ユースケース特定、ツール特定、ガイドレビュー、フォルダ構造計画

**開発中：** ケバブケースフォルダ名、SKILL.md 存在確認、YAML フロントマター（--- デリミタ、name はケバブケース、description に WHAT と WHEN）、XML タグなし、明確な命令、エラーハンドリング、例の提供、リファレンスのリンク

**アップロード前：** トリガーテスト（明確なタスク・言い換え・無関係なトピック）、機能テスト合格、ツール統合確認、zip 圧縮

**アップロード後：** 実会話テスト、過剰/不足トリガー監視、フィードバック収集、反復改善、バージョン更新

---

## 付録B: YAML フロントマターリファレンス

### 必須フィールド

```
---
name: skill-name-in-kebab-case
description: What it does and when to use it. Include specific trigger phrases.
---
```

* **name**（必須）：ケバブケースのみ。スペースや大文字は不可。フォルダ名と一致させる
* **description**（必須）：「何をするか」と「いつ使うか（トリガー条件）」の両方を必ず含める。1024文字以内。XML タグ（< >）は禁止。ユーザーが実際に言うタスクのフレーズを含め、関連するファイルタイプがあれば言及する

### 任意フィールド

| フィールド | 説明 | 制約・備考 |
| --- | --- | --- |
| `license` | オープンソース公開時のライセンス | MIT、Apache-2.0 など |
| `allowed-tools` | ツールアクセスの制限 | 例：`"Bash(python:*) Bash(npm:*) WebFetch"` |
| `compatibility` | 環境要件の記載 | 1〜500文字。対象プロダクト、必要なシステムパッケージ、ネットワークアクセス要件など |
| `metadata` | カスタムキーバリューペア | author、version、mcp-server、category、tags、documentation、support など |

**metadata の記述例：**

```
metadata:
  author: Company Name
  version: 1.0.0
  mcp-server: server-name
  category: productivity
  tags: [project-management, automation]
  documentation: https://example.com/docs
  support: support@example.com
```

### セキュリティ上の制限

フロントマターで禁止されている事項：

* **XML の山括弧（< >）**：フロントマターは Claude のシステムプロンプトに表示されるため、悪意あるコンテンツがプロンプトインジェクション攻撃の経路になる
* **「claude」「anthropic」を接頭辞に持つ Skill 名**：予約済みの名前である
* **YAML でのコード実行**：安全な YAML パーシングが使用されるため、コード実行は行われない

フロントマターで許可されている事項：

* 任意の標準 YAML 型（文字列、数値、ブーリアン、リスト、オブジェクト）
* カスタムメタデータフィールド
* 長い description（1024文字まで）

---

## 付録C: 完全な Skill の例

完全な本番対応の Skill の例は以下のリポジトリで公開されている：

* **Document Skills** - PDF、DOCX、PPTX、XLSX 作成の Skill
* **Example Skills** - 様々なワークフローパターンの Skill
* **Partner Skills Directory** - Asana、Atlassian、Canva、Figma、Sentry、Zapier 等のパートナー提供 Skill

これらのリポジトリは最新に保たれており、本ガイドの範囲を超えた追加の例を含む。クローンして、自分のユースケースに合わせて修正し、テンプレートとして使用する。
