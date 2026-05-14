---
id: "2026-05-12-技術調査-personal-ai-infrastructure-pai-01"
title: "技術調査 - Personal AI Infrastructure (PAI)"
url: "https://zenn.dev/suwash/articles/pai_20260513"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "LLM"]
date_published: "2026-05-12"
date_collected: "2026-05-14"
summary_by: "auto-rss"
query: ""
---

![PAI 3 層アーキテクチャ - Engines / PAI Life OS / You](https://static.zenn.studio/user-upload/deployed-images/7f7446333130bb795ec7cbbc.jpg?sha=7374232efd39bd4fd537a1c71cdd61a94b249d64)

## ■概要

Personal AI Infrastructure (PAI) は、Daniel Miessler が Claude Code 上に構築した **Life Operating System (生活 OS)** です。汎用 AI をユーザー個人の知識・目標・価値観と統合し、「現在の状態」から「理想の状態」への移行を継続的に支援します。バージョン 5.0.0 (2026-04-30 リリース) でこのコンセプトが完成形を迎えました。

PAI の設計思想は「AI はトップ 1% だけでなく、あらゆる人を増幅するべき」という命題に基づきます。単なるプロンプト集や agent フレームワークではなく、記憶・目標・スキル・セキュリティ・自己改善ループを統合した **個人用 AI プラットフォーム**です。

### 三層構造

| 層 | 役割 |
| --- | --- |
| PAI OS | スキル・メモリ・Algorithm・ユーザー定義ファイルの基盤 |
| Pulse | Life Dashboard、音声通知、cron、API を提供する統合デーモン |
| DA (Digital Assistant) | ユーザーに固有化された AI の実体。音声・個性を持つ |

### TELOS: PAI の中心軸

TELOS はユーザーが PAI に与える「自己定義」です。ミッション・年間目標・現在の課題・信念・メンタルモデルを記述した複数の Markdown ファイルで構成されます。TELOS が未定義の場合、DA には最適化すべき目標が存在しないため、応答が汎用的になります。

各コンポーネントの関係は以下のとおりです。

* **TELOS** → 目標軸。DA が何を優先するかの基準を提供する
* **Algorithm** → 実行軸。すべてのタスクを 7 フェーズで処理する
* **ISA (Ideal State Artifact)** → 検証軸。タスク単位の「完了状態」を定義する
* **Memory** → 記憶軸。作業・知識・学習・観測データを永続化する

### Claude Code との関係

PAI は Claude Code を実行基盤として使用します。Claude Code が提供する hooks・ツール呼び出し・ファイルシステムアクセスの仕組みを前提として動作します。

Claude Code 単体が「素材」であるとすれば、PAI は Claude Code を「OS」として機能させる層です。PAI は `~/.claude/` ディレクトリ以下にインストールされ、`settings.json` に hook を登録する形で Claude Code と統合されます。

### 他ツール・フレームワークとの比較

| 比較項目 | 素の Claude Code | AutoGen / LangGraph | LangChain Agents | Open Interpreter | PAI |
| --- | --- | --- | --- | --- | --- |
| 実行方式 | 対話型 / 単発エージェント | マルチエージェント コード実行重視 | Chain / Graph ベース | コード解釈・実行 | 7 フェーズ Algorithm (OBSERVE→LEARN) |
| 永続化方式 | なし (セッション限り) | なし〜外部 DB | LangGraph State 外部ストア | なし | Markdown ファイル (WORK / KNOWLEDGE / LEARNING) |
| 対応機能 | ツール呼び出し ファイル操作 | エージェント間会話 コード生成・実行 | 検索・Chain・RAG | コード実行 ファイル操作 | 目標管理 / 自己改善 音声 / セキュリティ スキルルーティング |
| 拡張モデル | MCP サーバー | カスタム Agent 定義 | Custom Chain / Tool | Plugin | Pack 方式 (スキル単位で AI が自律インストール) |
| 対象用途 | 汎用開発補助 | マルチエージェント 開発タスク | エンタープライズ RAG パイプライン | データ分析 スクリプト実行 | 個人の Life OS 目標主導型 AI 生活管理 |
| 学習フィードバック | なし | なし | なし | なし | 満足度シグナル→ 自己改善ループ |

#### 定性的な違い

* **vs. Fabric**: Fabric は特定タスク向けプロンプト集。PAI はメモリ・スキル・ルーティング・改善サイクルを含む完全なインフラ
* **vs. Claude Code 単体**: Claude Code は構成要素を提供する。PAI はそれらを「目標→スキル→記憶→改善」という一貫したシステムに統合する
* **vs. AutoGen / LangGraph**: AutoGen・LangGraph はマルチエージェント開発向け。PAI は個人の生活・仕事全体を対象とした OS

## ■特徴

### スケール指標

2026-05 時点の v5.0.0 における主要指標を示します。GitHub スター数と言語比率は時点値です。

| 指標 | 値 |
| --- | --- |
| パブリックスキル | 45 個 |
| ワークフロー | 171 本 |
| hooks | 37 個 |
| Algorithm バージョン | v6.3.0 |
| Memory バージョン | v7.6 |
| セキュリティゲート | 12 個 |
| GitHub スター (2026-05 時点) | 12.4k |
| 技術スタック (2026-05 時点) | TypeScript 77% / Python 8% / Shell 4% |

### 設計上の特徴

* **テキストファースト**: すべての記憶・ドキュメントを Markdown / プレーンテキストで保持。不透明な DB を排除し、ripgrep による検索で RAG を代替する
* **コードファースト**: 「プロンプトがコードをラップするのではなく、コードがプロンプトをラップする」。スキルは Code → CLI → Workflow → SKILL.md の順で構成する
* **コンテキスト優先**: モデルの性能よりも、正しいコンテキストの供給が回答品質を決定するという哲学
* **UNIX 哲学**: モジュール性・コンポーザビリティを重視する
* **自己改善ループ**: 満足度評価・センチメント・失敗ログを蓄積し、将来のセッションに反映する
* **構造的プライバシー**: コンテナメントゾーン定義と 12 の SecurityGate によって、手続きではなく構造でプライバシーを守る
* **ワンラインインストール**: `curl -sSL https://ourpai.ai/install.sh | bash` で Bun + Git + DA セットアップを自動化する
* **One DA per person**: 1 人の人間に 1 つの DA が対応する。Daniel Miessler 自身の DA は「Kai」と名付けられている

![DA を中心に Skills / Memory / Hooks / Pulse が配置された PAI 構造](https://static.zenn.studio/user-upload/deployed-images/19b6deb5f21169538a1807f6.jpg?sha=a3fa534e8a92d10d925c925f7f99abd794de9bdf)

### Algorithm v6.3.0 の特徴

![Algorithm 7 フェーズループ - CURRENT STATE から IDEAL STATE への遷移](https://static.zenn.studio/user-upload/deployed-images/c12984e0a8654489c322d92c.jpg?sha=b47b7670ed0848ce6ab17aa868c8d41536564dbe)

* 7 フェーズ (OBSERVE → THINK → PLAN → BUILD → EXECUTE → VERIFY → LEARN)
* タスク複雑度に応じた 3 モード (MINIMAL / NATIVE / ALGORITHM) の自動切り替え
* 努力量ティア (E1〜E5) による予算管理
* ISC (Ideal State Criteria) による検証可能な完了判定
* 音声フェーズ告知 (Pulse 経由)

### Memory v7.6 の特徴

* 公式は 3 ティア (WORK / KNOWLEDGE / LEARNING) + 補助ストレージ (RELATIONSHIP / OBSERVABILITY / STATE) で計 6 系統のディレクトリを持つ
* 大量の満足度シグナルを蓄積・分析可能
* JSONL 形式でのオブザーバビリティログ (ツール呼び出し・フック・サブエージェント)
* People / Companies / Ideas / Research の型付きグラフ

### ISA の特徴

![ISA の 12 セクションと 5 つのアイデンティティ](https://static.zenn.studio/user-upload/deployed-images/b4bb12e2f6cd1044baa3e1f3.jpg?sha=e6700856b488345b2f5c9e399b7a45cfec75ff23)

* PRD を代替するユニバーサルな「完了定義」ドキュメント
* Scaffold / Interview / CheckCompleteness / Reconcile / Seed / Append の 6 ワークフローを管理
* Algorithm の OBSERVE フェーズで非自明タスクに自動適用
* ISC (Ideal State Criteria) は二値・テスト可能・具体的な合否条件

### Pulse の特徴

* Bun TypeScript による統合デーモン (ポート 31337)
* 多数の REST API ルート (システム状態・cron 管理・オブザーバビリティ)
* 音声通知 (ElevenLabs TTS)
* Telegram / iMessage ブリッジ (オプション)
* macOS launchd サービスとして自動起動

## ■構造

PAI の内部アーキテクチャを C4 model の 3 段階で図解します。

### ●システムコンテキスト図

PAI 全体を外部から見たとき、誰が・何が関与するかを示します。

#### 要素説明

| 要素名 | 説明 |
| --- | --- |
| Principal | PAI を利用する人間。DA を通じて PAI に意図を伝える |
| Digital Assistant | Principal の分身となる名前付き AI エージェント。PAI の主インタフェース |
| PAI | Personal AI Infrastructure 本体。Life Operating System として機能する |
| Claude API | PAI が推論に使う外部 LLM サービス |
| ElevenLabs | Pulse が音声通知に使う TTS API |
| Telegram | Pulse 経由で DA とチャットするメッセージングサービス |
| iMessage | Pulse 経由で DA とチャットするメッセージングサービス |
| macOS launchd | Pulse デーモンを常駐サービスとして管理する macOS プロセスマネージャ |

### ●コンテナ図

PAI 本体の内部を主要コンテナ単位でドリルダウンします。

#### 要素説明

| 要素名 | 説明 |
| --- | --- |
| Pulse daemon | Bun TypeScript 製の統合デーモン。port 31337 で動作し、音声・フック検証・観測・Telegram/iMessage・cron・Life Dashboard を一元管理する |
| Claude Code Host | Claude Code のセッション実行基盤。DA がプロンプトを受け取り ALGORITHM を動かす |
| ALGORITHM | v6.3.0。OBSERVE → THINK → PLAN → BUILD → EXECUTE → VERIFY → LEARN の 7 フェーズループ。Sonnet-backed モード分類器を持つ |
| MEMORY ファイルツリー | WORK / KNOWLEDGE / LEARNING / RELATIONSHIP / OBSERVABILITY / STATE の階層を持つプレーンテキストストレージ |
| SKILLS | 45 の自己起動型スキル。DA がインテントに応じて自動選択する |
| HOOKS | 37 本の TypeScript ライフサイクルハンドラ。Claude Code イベントに連動する |
| DA Identity | PRINCIPAL\_IDENTITY.md / DA\_IDENTITY.md / TELOS/ で構成される Principal と DA の定義ファイル群 |
| Life Dashboard | Pulse が port 31337 で提供する Next.js 製 UI |

### ●コンポーネント図

#### Pulse daemon の内部

##### Pulse daemon の要素説明

| 要素名 | 説明 |
| --- | --- |
| PULSE.toml | Pulse の全設定ファイル。各モジュールの有効/無効・cron ジョブ定義を保持する |
| Cron Scheduler | heartbeat ループ。cron 式を評価して script / claude ジョブを実行し、結果を voice / telegram / ntfy / log にルーティングする |
| POST /notify | 音声通知エンドポイント。メッセージを受け取り ElevenLabs TTS を呼び出す。VoiceCompletion フックから利用される |
| Wiki API | MEMORY/KNOWLEDGE/ のコンテンツを HTTP で公開するエンドポイント |
| Hook Validation | skill-guard と agent-guard ルートを提供。スキル / エージェント呼び出しをブロック・許可する |
| Observability module | tool-activity.jsonl / tool-failures.jsonl 等の JSONL データを集計し、Life Dashboard の API を提供する |
| Telegram Bridge | grammY ライブラリを使ったポーリング型 Telegram ボット。claude-agent-sdk でセッションを管理する |
| iMessage Bridge | macOS の SQLite DB をポーリングして iMessage を取得するボット。デフォルト無効 |
| DA Assistant module | DA のアイデンティティ・スケジュール・成長ログを管理するモジュール |
| UserIndex module | USER/ ディレクトリを fs.watch で監視し、フロントマター + コレクションを typed JSON に変換して /life ダッシュボードに提供する |

#### Algorithm の内部

Algorithm v6.3.0 の内部コンポーネントを分解します。

##### Algorithm 内部の要素説明

| 要素名 | 説明 |
| --- | --- |
| Mode Classifier | UserPromptSubmit フック内で Sonnet を呼び出し、プロンプトを MINIMAL / NATIVE / ALGORITHM に分類する |
| Tier Evaluator | プロンプトのスコープから E1〜E5 の時間予算を決定する |
| Phase Executor | OBSERVE → THINK → PLAN → BUILD → EXECUTE → VERIFY → LEARN を逐次実行する |
| ISA Scaffold Connector | OBSERVE フェーズで非自明タスクに対し ISA Skill の Scaffold ワークフローを呼ぶ |
| Verifier | ISA の ISC を逐次評価し、未達なら BUILD/EXECUTE へ戻る |
| Learning Capture | LEARN フェーズで MEMORY/LEARNING/ に学習を書き込む |
| Advisor Bus | E4/E5 タスクでアドバイザーサブエージェント (クロスベンダー監査を含む補助レビュー) を起動する設計思想を持つ |

#### Hook System の内部

フックは v5.0.0 時点で計 37 本です。以下の図は系統別の代表的なフックを示しており、実装上の補助ハンドラを含めると図中ノード数は 37 を上回ります。

##### UserPromptSubmit 系

| 要素名 | 説明 |
| --- | --- |
| PromptGuard | PromptInspector を使ったヒューリスティックスキャン。インジェクション・エグレス・セキュリティ無効化を検出し、同期ブロックできる |
| PromptProcessing | Sonnet-backed の統合分析フック。1 回の推論呼び出しでモード分類 (MINIMAL/NATIVE/ALGORITHM)・エフォートティア (E1-E5)・タブタイトル・セッション名・感情評価を一括出力する |
| RepeatDetection | 連続する重複プロンプトを検出してユーザーに警告する |
| SatisfactionCapture | 明示的な評価 (1-10) や感情シグナルを ratings.jsonl に記録する |

##### PreToolUse 系

| 要素名 | 説明 |
| --- | --- |
| SecurityPipeline | 5 つのインスペクタ (Pattern / Egress / Rules / Prompt / Injection) のパイプライン。Bash / Edit / Write / MultiEdit ツール実行前に同期ブロックできる |
| ContainmentGuard | Edit / Write / MultiEdit でプライバシーゾーン外への書き込みをブロックする。containment-zones.ts が単一の真実のソース |
| ContextReduction | Bash コマンド出力を圧縮し、コンテキスト消費を削減する |
| SetQuestionTab | AskUserQuestion ツール使用前にタブをアンバー色に変更する |
| AgentGuard | Pulse HTTP ルート。エージェント生成を検証・ブロックする |
| SkillGuard | Pulse HTTP ルート。不正なスキル呼び出しを防止する |
| SmartApprover | PermissionRequest イベントで trusted/read ツールを自動承認する |

##### PostToolUse 系

| 要素名 | 説明 |
| --- | --- |
| ISASync | Edit / Write ツール実行後に ISA.md フロントマターを work.json に同期し、Cloudflare KV にプッシュする |
| CheckpointPerISC | ISC チェックボックスの遷移を検出して自動 git commit を実行する |
| QuestionAnswered | AskUserQuestion 完了後にタブ状態をリセットする |
| ContentScanner | WebFetch / WebSearch の結果に対して InjectionInspector を実行する |
| ToolActivityTracker | ツール実行結果を tool-activity.jsonl に JSONL エントリとして記録する |
| ToolFailureTracker | ツール失敗を tool-failures.jsonl に記録する |
| FileChanged | ファイル変更を検出してイベントを発火する |
| AgentInvocation | PreToolUse:Agent / PostToolUse:Agent でサブエージェントの起動・停止・所要時間を subagent-events.jsonl に記録する |

##### Stop 系

| 要素名 | 説明 |
| --- | --- |
| VoiceCompletion | タスク完了時に Pulse の POST /notify を呼び出して TTS アナウンスを行う |
| LastResponseCache | 次のセッション分析のために最終応答テキストをキャッシュする |
| ResponseTabReset | 応答完了後にターミナルタブのタイトルとカラーをデフォルト状態にリセットする |
| DocIntegrity | ドキュメントのクロスリファレンス検証とアーキテクチャサマリの自動再生成を行う |
| StopFailureHandler | Stop イベントのエラーを捕捉してリカバリ処理を行う |

##### SessionStart 系

| 要素名 | 説明 |
| --- | --- |
| LoadContext | MEMORY から関係性・学習・作業サマリを読み込み system-reminder としてコンテキストに注入する |
| KittyEnvPersist | Kitty ターミナルの環境変数を kitty-env.json に永続化し、タブタイトルを初期状態にリセットする |
| KVSync | work.json を Cloudflare KV に同期して外部ダッシュボードから参照できるようにする |

##### SessionEnd 系

| 要素名 | 説明 |
| --- | --- |
| WorkCompletionLearning | ISA.md から完了した作業の学習事項を抽出し MEMORY/LEARNING/ に書き込む |
| SessionCleanup | ISA.md の status を COMPLETED に更新し、セッション状態をクリアする |
| RelationshipMemory | セッション中に観察した Principal との関係性ノートを MEMORY/RELATIONSHIP/ に記録する |
| UpdateCounts | スキル数・フック数・ワークフロー数等のシステムカウントを settings.json に更新する |
| IntegrityCheck | PAI ファイルの変更検出とドキュメント整合性チェックを実行する |

##### その他の系

| 要素名 | 説明 |
| --- | --- |
| TeammateIdle | TeammateIdle イベント時にアイドルログを記録する |
| ConfigAudit | ConfigChange イベントでセキュリティ監査ログを MEMORY/OBSERVABILITY/ に書き込む |
| TaskGovernance | タスク実行のガバナンス制約を適用する |
| TelosSummarySync | TELOS/ の変更を検出してサマリファイルに同期する |
| ElicitationHandler | 情報引き出しプロセスを処理する |
| InstructionsLoadedHandler | 指示ファイルのロード完了イベントを処理する |
| PreCompact | コンテキスト圧縮 (compaction) 前の前処理を行う |
| RestoreContext | 圧縮後のコンテキスト復元を行う |

## ■データ

### ●概念モデル

PAI を構成するエンティティと所有・利用関係を示します。

#### エンティティ説明

| エンティティ | 説明 |
| --- | --- |
| Principal | PAI を利用する人間。1 つの DA を所有する |
| DA | Principal の AI 実体。Algorithm を実行する |
| Algorithm Run | Algorithm v6.3.0 の 1 回の実行 |
| Phase | OBSERVE / THINK / PLAN / BUILD / EXECUTE / VERIFY / LEARN |
| Mode | MINIMAL / NATIVE / ALGORITHM |
| Effort Tier | E1〜E5 の時間予算 |
| Work Slug | タスクごとに割り当てられる kebab-case 識別子 |
| Session | Claude Code セッション。5 ワードの自動命名がつく |
| ISA | Ideal State Artifact。完了状態を定義するドキュメント |
| ISC | Ideal State Criteria。ISA 内のチェック可能な合否条件 |
| MEMORY | WORK / KNOWLEDGE / LEARNING の 3 ティア + RELATIONSHIP / OBSERVABILITY / STATE の補助領域 |
| work.json | slug → phase / tier / name のセッションレジストリ |
| session-names.json | session\_id → 5-word name の写像 |
| Skill | DA が自動選択する機能単位 |
| Workflow | Skill が公開するルーティング先 |
| Hook | Claude Code ライフサイクルイベントのハンドラ |
| Pack | 複数 Skill を束ねた配布単位 |
| Pulse Job | PULSE.toml に定義された cron ジョブ |
| Voice Notification | Pulse /notify で送信される TTS 通知 |
| Observability Event | tool-activity.jsonl などに記録される単位イベント |

### ●情報モデル

主要エンティティの属性を示します。

## ■構築方法

### 前提条件

* **macOS** (launchd サービス登録のために必須)
* **Claude Code** (Claude Code が提供するフック・スラッシュコマンド・MCP サーバー等を基盤として利用)
* **Bun ランタイム** (TypeScript ランタイム。インストーラーが自動インストール)
* **Git** (バージョン管理。インストーラーが自動インストール)
* **ElevenLabs API キー** (オプション。音声通知機能に利用)

バージョン確認:

```
bun --version
git --version
```

リリース一覧は GitHub の `Releases/` ディレクトリを参照します。

### one-line installer (推奨)

```
curl -sSL https://ourpai.ai/install.sh | bash
```

インストーラーが以下をすべて処理します。

* Bun / Git / Claude Code の存在確認
* ElevenLabs API キーの入力プロンプト (スキップ可)
* DA (Digital Assistant) アイデンティティのウィザード起動
* Pulse を macOS launchd サービス (`com.pai.pulse`) として登録
* インストールの検証

既存の `~/.claude/` は `~/.claude.backup-{TIMESTAMP}` へ自動バックアップされます。

### 手動セットアップ手順

v5.0.0 README が示す公式手順は、リポジトリを直接 `~/.claude` にクローンする方法です (`PAI.git` は `Personal_AI_Infrastructure` リポジトリのエイリアスとして GitHub 上で解決されます)。

```
# 1. リポジトリを ~/.claude に直接クローン
git clone https://github.com/danielmiessler/PAI.git ~/.claude

# 2. インストーラーを実行
cd ~/.claude && ./install.sh
```

### DA (Digital Assistant) Identity の設定

DA アイデンティティは 2 つのファイルで管理されます。

| ファイル | 内容 |
| --- | --- |
| `PAI/USER/PRINCIPAL_IDENTITY.md` | 使用者自身の情報 (名前・役割・場所・世界観・作業スタイル) |
| `PAI/USER/DA_IDENTITY.md` | DA の情報 (名前・音声 ID・パーソナリティ・文体・好み) |

インストール後、Claude Code で `/interview` を実行すると DA がウィザードを案内します。

1. **Phase 1 — TELOS**: Mission / Goals / Beliefs / Wisdom / Challenges / Books / Mental models / Narratives
2. **Phase 2 — IDEAL\_STATE**: 自分にとっての成功とは何か
3. **Phase 3 — Preferences**: ツール・規約・作業スタイル
4. **Phase 4 — Identity**: DA のパーソナリティの最終調整

TELOS なしでは DA が最適化する軸を持てないため、インストール直後に必ず実施します。セッション開始時、両ファイルは自動でコンテキストへロードされます。

### launchd 設定 (Pulse を macOS サービスとして登録)

インストーラーが自動で `com.pai.pulse` という名前の launchd サービスを登録します。

```
# サービスの状態確認
launchctl list | grep com.pai.pulse

# サービスの再起動
launchctl stop com.pai.pulse
launchctl start com.pai.pulse

# ヘルスチェック
curl -s http://localhost:31337/api/pulse/health | jq
```

Pulse は macOS 起動時に自動起動するよう設定されます。常時稼働させておくことで、音声通知・ダッシュボード・スケジュールジョブが機能します。

### Claude Code との連携 (settings.json / MCP)

PAI は Claude Code の 2 つの拡張機構を併用します。

**1. hooks 登録 (`~/.claude/settings.json`)**

Claude Code は `~/.claude/settings.json` の `hooks` フィールドでイベントごとにスクリプトを呼び出せます。PAI のインストーラーがこの設定を自動生成します。

```
{
  "hooks": {
    "UserPromptSubmit": [
      { "matcher": "*", "hooks": [{ "type": "command", "command": "bun ~/.claude/hooks/PromptProcessing.hook.ts" }] }
    ],
    "PreToolUse": [
      { "matcher": "Edit|Write|MultiEdit", "hooks": [{ "type": "command", "command": "bun ~/.claude/hooks/ContainmentGuard.hook.ts" }] }
    ],
    "PostToolUse": [
      { "matcher": "*", "hooks": [{ "type": "command", "command": "bun ~/.claude/hooks/ToolActivityTracker.hook.ts" }] }
    ],
    "Stop": [
      { "matcher": "*", "hooks": [{ "type": "command", "command": "bun ~/.claude/hooks/VoiceCompletion.hook.ts" }] }
    ]
  }
}
```

各フックは stdin で JSON を受け取り、stdout で JSON を返し、exit code 0 で成功を示します。

**2. MCP サーバー連携**

Pulse は Claude Code クライアントから利用可能な HTTP API を `localhost:31337` で公開し、必要に応じて MCP サーバーとしても露出できます。Telegram Bridge は `claude-agent-sdk` を経由して MCP 越しに Claude Code セッションを発火します。サードパーティの MCP サーバー (例: Context7 / GitHub MCP) は `~/.claude/mcp.json` に登録して、Algorithm の各フェーズから自然言語で呼び出せます。

### PULSE.toml の初期設定

設定ファイルのパス: `~/.claude/PAI/PULSE/PULSE.toml`

公式リポジトリの `PULSE.toml.example` は `[pulse]` / `[modules]` / `[voice]` / `[observability]` / `[telegram]` / `[imessage]` / `[da]` 等のセクション構成を採用します。以下は最小設定の抜粋です。

```
[pulse]
port = 31337

[modules]
hooks = true
observability = true

[voice]
enabled = true

[observability]
dashboard_dir = "Observability/out"

[telegram]
enabled = false

[imessage]
enabled = false

[da]
enabled = false
```

cron ジョブの定義は別途 `[[jobs]]` 形式で記述します (公式ドキュメントの記載に従う場合):

```
[[jobs]]
name = "morning-brief"
schedule = "0 7 * * *"
type = "claude"
prompt = "Run the morning brief and summarize today's priorities from TELOS."
model = "sonnet"
output = ["voice", "dashboard"]
enabled = true
```

主要設定項目:

* `[pulse].port`: Pulse がリッスンするポート (デフォルト 31337)
* `[modules]`: hooks / observability モジュールのオンオフ
* `[voice]`: ElevenLabs TTS の有効化
* `[observability]`: Life Dashboard のディレクトリ指定
* `[telegram]` / `[imessage]`: 外部通知ブリッジ (オプション)
* `[[jobs]]`: cron ジョブの定義 (Context7 ドキュメントで紹介されているスケジュール機構)

## ■利用方法

### Algorithm の起動方法

PAI の Algorithm v6.3.0 は Claude Code セッションで非自明なタスクを依頼すると自動起動します。

```
OBSERVE → THINK → PLAN → BUILD → EXECUTE → VERIFY → LEARN
```

`UserPromptSubmit` フックが Sonnet バックのモード分類器を実行し、プロンプトごとに以下を自動判定します。

* **モード**: MINIMAL / NATIVE / ALGORITHM
* **エフォートティア**: E1 (90 秒未満) 〜 E5 (2 時間以上)

ユーザーは特別なコマンドを打たなくても、タスクを依頼するだけで Algorithm が適切なモードとティアを選択して実行します。

### ISA の作成

ISA (Ideal State Artifact) は PAI における「完了」の普遍的な定義ドキュメントです。

Claude Code セッションで以下のようにプロンプトを送ると ISA Skill が起動し Scaffold ワークフローが実行されます。

```
Skill("ISA", "scaffold from prompt: <user message> at tier E3")
```

あるいは自然言語で:

```
この CLI ツールの ISA を E3 ティアで作成して
```

ISA のフロントマター例:

```
task: "8 word task description"
slug: YYYYMMDD-HHMMSS_kebab-description
project: <name>
effort: <tier>
effort_source: <auto|explicit|gate-floor>
phase: observe
progress: 0/<isc-count>
mode: interactive
started: <ISO-8601>
updated: <ISO-8601>
```

ISA の保存先:

* **プロジェクト ISA**: `<project>/ISA.md`
* **タスク ISA**: `~/.claude/PAI/MEMORY/WORK/{slug}/ISA.md`

### ISA の編集と ISC チェック

ISA は 12 のセクションで構成されます。

```
Problem → Vision → Out of Scope → Principles → Constraints →
Goal → Criteria → Test Strategy → Features → Decisions → Changelog → Verification
```

ISC (Ideal State Criteria) はチェックボックス形式で記述します。

```
## Criteria
- [ ] ISC-1: `bun KnowledgeGraph.ts stats` がドメイン別ノート数を表示する
- [ ] ISC-2: `bun KnowledgeGraph.ts traverse --from <slug> --depth 2` が1件以上返す
- [ ] ISC-3: 200 件のノートで500ms以内に完了する
- [ ] ISC-4: Anti: MEMORY/KNOWLEDGE/ 外への読み書きをしない
```

ISC の完了を確認するには CheckCompleteness ワークフローを利用します。

### Skill の自動発火

![DA を中心に 5 クラスタのスキル群が星座状に配置された図](https://static.zenn.studio/user-upload/deployed-images/33b7c57a66547799caf17ac0.jpg?sha=60e19ad246fa3fc781a0dc5750da5c648cd68fd0)

Skill は `SKILL.md` の `description` フィールドに記載したトリガーワードに基づいて自動発火します。

```
name: SkillName
description: [何をするか]. USE WHEN [発火するインテント]. NOT FOR [代替手段].
```

### Skill の直接呼び出し

スラッシュコマンドで Skill を直接呼び出せます。

```
/context-search authentication
/cs deploy
/interview
```

### Memory への書き込み

Memory ディレクトリ構造:

```
~/.claude/PAI/MEMORY/
├── WORK/                          # アクティブ・アーカイブ済みタスク ISA
│   └── {slug}/ISA.md
├── KNOWLEDGE/                     # 永続的なタイプ付きノート
│   ├── People/
│   ├── Companies/
│   ├── Ideas/
│   ├── Research/
│   └── Blogs/
├── LEARNING/                      # メタパターン
│   ├── feedback_*.md
│   └── patterns.md
├── RELATIONSHIP/                  # DA-Principal 関係ノート
├── OBSERVABILITY/                 # ツール呼び出し + フックイベント (JSONL)
│   ├── tool-activity.jsonl
│   ├── tool-failures.jsonl
│   ├── subagent-events.jsonl
│   └── prompt-processing.jsonl
└── STATE/
    ├── work.json                  # セッションレジストリ
    └── session-names.json
```

Memory への書き込みは DA に自然言語で依頼します。

```
田中さんのことを記録して: エンジニア、React が得意、2026年5月に面談
このアーキテクチャパターンのアイデアを KNOWLEDGE/Ideas に保存して
この調査結果を KNOWLEDGE/Research に追加して
```

### Pulse 経由の voice notification

`/notify` エンドポイントに POST して音声通知を送信します。

```
curl -s -X POST http://localhost:31337/notify \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Build complete. All ISCs verified.",
    "voice_id": "<your-voice-id>",
    "voice_enabled": true
  }'
```

レスポンス例:

```
{ "status": "ok", "spoken": true }
```

### Life Dashboard へのアクセス

```
open http://localhost:31337
```

ダッシュボードは多数のルートを提供します (Life / Health / Finances / Business / Work / Telos / Goals / Performance / Hooks / Skills / Agents / Security / Knowledge / Knowledge Graph / System Docs など)。

### Pack のインストール

Pack は Claude Code 上で AI エージェントが自律的にインストール可能なモジュール型拡張機能です。

```
# Pack ディレクトリへ移動
cd ~/.claude/Packs/ContextSearch

# DA に INSTALL.md を読ませてインストールを依頼
# Claude Code で: "Packs/ContextSearch/INSTALL.md を読んでインストールして"
```

Pack の構造:

```
Packs/<PackName>/
├── README.md      # 概要
├── INSTALL.md     # AI エージェント向けインストール手順
├── VERIFY.md      # 検証ステップ
└── src/           # 実装コード
```

ContextSearch Pack を入れると以下のスラッシュコマンドが追加されます。

```
/context-search [topic]
/cs [topic]
```

### Pulse 経由の cron job 設定

`PULSE.toml` の `[[jobs]]` セクションに cron ジョブを追加します。

```
[[jobs]]
name = "morning-brief"
schedule = "0 7 * * *"
type = "claude"
prompt = "Run the morning brief and summarize today's priorities from TELOS."
model = "sonnet"
output = ["voice", "dashboard"]
enabled = true

[[jobs]]
name = "weekly-review"
schedule = "0 18 * * 5"
type = "claude"
prompt = "Summarize this week's completed ISAs and extract learnings."
model = "sonnet"
output = ["dashboard"]
enabled = true
```

設定変更後は Pulse を再起動します。

```
launchctl stop com.pai.pulse
launchctl start com.pai.pulse
```

## ■運用

### Pulse の起動 / 停止 / 状態確認

Pulse は macOS launchd サービス `com.pai.pulse` として登録されるシングル Bun プロセス (ポート 31337) です。

```
# ロード
launchctl load ~/Library/LaunchAgents/com.pai.pulse.plist

# アンロード
launchctl unload ~/Library/LaunchAgents/com.pai.pulse.plist

# 起動確認
curl -s http://localhost:31337/api/pulse/health | jq

# 音声通知のテスト
curl -s -X POST http://localhost:31337/notify \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello from your DA", "voice_enabled": true}'

# ダッシュボードを開く
open http://localhost:31337
```

Pulse は常時起動が推奨です。launchd 管理のため、クラッシュ時は OS が自動で再起動します。

### Pulse ログの確認場所

公式 `com.pai.pulse.plist` の StandardOutPath / StandardErrorPath は以下に設定されます。

```
tail -f ~/.claude/PAI/PULSE/logs/pulse-stdout.log
tail -f ~/.claude/PAI/PULSE/logs/pulse-stderr.log
```

macOS Console.app から `com.pai.pulse` でフィルタすることも可能です。

### Observability JSONL の確認

すべてのツール呼び出し・フック実行・満足度シグナルは `MEMORY/OBSERVABILITY/` 以下の JSONL ファイルに書き込まれます。

```
# 直近のツール呼び出しを確認
tail -20 ~/.claude/PAI/MEMORY/OBSERVABILITY/tool-activity.jsonl | jq .

# 失敗したツールを確認
cat ~/.claude/PAI/MEMORY/OBSERVABILITY/tool-failures.jsonl | jq .

# Algorithm が選択した mode/tier を確認
cat ~/.claude/PAI/MEMORY/OBSERVABILITY/prompt-processing.jsonl | jq '{mode, tier, prompt}'
```

### Life Dashboard の活用

`http://localhost:31337` で複数ルートのダッシュボードを表示できます。

| ルート例 | 内容 |
| --- | --- |
| Life | 全体ライフ状態 |
| Work | 進行中 ISA / フェーズ状態 |
| Telos | ミッション・目標・信念 |
| Performance | ツール活動・フック実行統計 |
| Hooks | フック一覧・実行状態 |
| Skills | スキル一覧 |
| Knowledge | ナレッジグラフ |
| Security | セキュリティゲート状態 |
| System Docs | PAI ドキュメント |

### Memory のバックアップ

`~/.claude/PAI/MEMORY/` 以下を Git で管理するのが推奨パターンです。

```
cd ~/.claude/PAI/MEMORY
git init
git add .
git commit -m "init: PAI memory baseline"

# 日次バックアップ
cd ~/.claude/PAI/MEMORY && git add -A && git commit -m "backup: $(date +%Y-%m-%d)"

# アップグレード前の手動バックアップ
cp -R ~/.claude ~/.claude.backup-$(date +%Y%m%d)
```

### アップグレード手順

PAIUpgrade Pack は 4 並列スレッド (監査 / ユーザーコンテキスト / 外部リサーチ / スキルドリフト) でアップグレード推奨事項を生成します。

```
# Claude Code セッション内で実行
/pai-upgrade
```

AlgorithmUpgrade ワークフローは Algorithm 自体のパフォーマンス改善を行います。トリガーフレーズ:

* `algorithm upgrade`
* `upgrade algorithm`
* `improve the algorithm`

実行ステップ:

1. 現行 Algorithm spec を読み込みダイジェスト生成
2. 4 ソース (reflections JSONL / ratings / 学習データ / 失敗パターン) からシグナルを収集
3. 汎用エージェントがシグナルを spec にマッピング
4. Claude Code 機能参照を最新で検証
5. 優先度付きアップグレード提案を生成
6. バージョンバンプの必要性を評価

### Skill の追加 / 無効化

最小構成の SKILL.md テンプレート:

```
name: MySkill
description: |
  [何をするか1文]. USE WHEN [トリガー]. NOT FOR [代替手段].

# MySkill

## Workflow Routing
| Workflow | Trigger | File |
|---|---|---|
| Default | "use my skill" | Workflows/Default.md |
```

```
# 手動追加
mkdir -p ~/.claude/skills/MySkill/Workflows
touch ~/.claude/skills/MySkill/SKILL.md
touch ~/.claude/skills/MySkill/Workflows/Default.md
```

プライベートスキルは名前を `_ALLCAPS` にすることで公開リリースから除外されます。Pack 自作の場合は `Packs/<Name>/` に `README.md` / `INSTALL.md` (AI 向けインストール手順) / `VERIFY.md` (検証ステップ) / `src/` を配置します。

```
# ~/.claude/PAI/PULSE/PULSE.toml
[hooks]
enabled = true
blocked_skills = ["ApertureOscillation", "RedTeam"]
```

`blocked_skills` に指定したスキルは DA に選択されなくなります。

## ■ベストプラクティス

### TELOS の継続更新

* TELOS は Principal Identity の核心 (Mission / Goals / Beliefs / Wisdom / Challenges / Mental Models)
* 格納場所: `PAI/USER/TELOS/`
* インストール直後に `/interview` を実行する
* 月次または四半期ごとに Telos スキルで内容を見直す

### ISA を残す習慣

* すべての非自明タスクに ISA を作成し `MEMORY/WORK/{slug}/ISA.md` に保存
* ISA は 12 セクション固定構成
* ISC 完了時は `CheckpointPerISC.hook.ts` が自動 git commit
* タスク完了後も ISA を削除しない (ContextSearch が後で参照する)

### Memory v7.6 の使い分け

| ティア | パス | 用途 |
| --- | --- | --- |
| WORK | `MEMORY/WORK/{slug}/` | 進行中・完了タスクの ISA |
| KNOWLEDGE | `MEMORY/KNOWLEDGE/{People,Companies,Ideas,Research,Blogs}/` | 耐久性のある型付きノート |
| LEARNING | `MEMORY/LEARNING/` | メタパターン・フィードバック |
| RELATIONSHIP | `MEMORY/RELATIONSHIP/` | DA-Principal 関係ノート |
| OBSERVABILITY | `MEMORY/OBSERVABILITY/*.jsonl` | 全ツール呼び出し・フック実行 |
| STATE | `MEMORY/STATE/work.json` | セッションレジストリ |

### セキュリティガード

#### Containment Guard

* `hooks/lib/containment-zones.ts` でディレクトリごとのプライバシーレベルを宣言
* `ContainmentGuard.hook.ts` (PreToolUse) がゾーン外への書き込みをブロック
* `_ALLCAPS` 名スキルはプライベートスキル (公開リリースに含まれない)

#### SecurityPipeline Hook (5 インスペクター)

| インスペクター | 役割 |
| --- | --- |
| Pattern | 既知の悪意あるパターン検出 |
| Egress | 外部への意図しないデータ送信検出 |
| Rules | PAI セキュリティルール適合確認 |
| Prompt | プロンプトインジェクション検出 |
| Injection | インジェクション攻撃パターン検出 |

#### 12 Security Gates

リリース工程は 2 ステージ (ステージング → 公開) に分割され、各段階で 12 のゲートを順に通過します。

| ゲート | 役割 |
| --- | --- |
| G1 ゾーン削除確認 | プライベートゾーンの残骸を検出する |
| G2 アイデンティティ grep | PRINCIPAL\_IDENTITY / DA\_IDENTITY の漏れを grep する |
| G3 Cloudflare ID | KV / Tunnel ID の流出を検出する |
| G4 trufflehog | コミット履歴のシークレットを走査する |
| G5 .env 流出 | 環境変数ファイルの漏出を検出する |
| G6 プライベートトークン | API キー・トークン文字列を grep する |
| G7 参照整合性 | リンク切れと壊れた参照を検出する |
| G8 プライベートスキル参照 | `_ALLCAPS` 名スキルへの参照を遮断する |
| G9 ユーザーパス | `/Users/<name>` 等の絶対パスを検出する |
| G10 ステージングブート | ステージング環境での起動確認 |
| G11 ダッシュボードリーク | Dashboard 経由の機微データ流出を確認する |
| G12 テンプレート専用 USER/MEMORY | テンプレートディレクトリのみの構成を保証する |

ゲートは自動連鎖しません。次のゲートに進むには明示的な承認が必要です。

### Algorithm を信頼する (effort tier)

| Tier | 時間予算 | 用途例 |
| --- | --- | --- |
| E1 | < 90 秒 | 簡単な質問・1 行変更 |
| E2 | < 10 分 | 小規模タスク |
| E3 | < 30 分 | 中規模タスク |
| E4 | < 1 時間 | 大規模タスク |
| E5 | 2 時間以上 | 複雑なプロジェクト |

```
# Tier を明示
"E3 task: refactor the authentication module"

# モード分類を明示
"ALGORITHM: build a new CLI tool for X"
```

Tier の自動判定を信頼して上書きしないのが原則です。

### Skill description の設計 (USE WHEN / NOT FOR)

```
name: SkillName
description: |
  [スキルが何をするか1文で].
  USE WHEN [発火させたい意図・トリガー条件を具体的に].
  NOT FOR [代替スキルがある場合・対象外のケース].
```

DA はランタイムに description を読んでスキルを選択します。`USE WHEN` / `NOT FOR` が曖昧だとスキルが発火しない、または誤発火します。

### Pack によるモジュール拡張

Pack はスキルを `~/.claude/skills/` にインストールするスタンドアロンな拡張セットです。主な公式 Pack:

| Pack | 用途 |
| --- | --- |
| PAIUpgrade | システム改善案を 4 並列 (監査 / コンテキスト / 外部リサーチ / ドリフト) で生成する |
| Migrate | Obsidian / Notion / Apple Notes 等から既存資産を PAI 構造に取り込む |
| Loop | 1 タスクを Algorithm サイクルで反復改善する |
| ContextSearch | 過去の ISA / セッションを横断検索する (`/cs` コマンド) |
| ISA | 完了定義ドキュメントの Scaffold / Interview / CheckCompleteness を提供する |
| CreateSkill | 新規スキルを Anthropic methodology に沿ってスキャフォールドする |

DA に `Install the [PackName] pack` と依頼すると自動インストールされます。

### 観測性を見て LEARNING を更新する

```
# 失敗パターンの確認
jq 'select(.status=="failed")' ~/.claude/PAI/MEMORY/OBSERVABILITY/tool-failures.jsonl

# 満足度シグナルの確認
grep '"rating"' ~/.claude/PAI/MEMORY/OBSERVABILITY/tool-activity.jsonl | jq .
```

週次または月次で JSONL をレビューし、気づきを `MEMORY/LEARNING/feedback_*.md` に手動追記します。

## ■トラブルシューティング

頻出エラーを「症状 → 原因 → 対処」の形式で示します。

| # | 症状 | 原因 | 対処 |
| --- | --- | --- | --- |
| 1 | Pulse が起動しない | ポート 31337 が別プロセスに占有 | `lsof -i :31337` で競合プロセスを終了し、`launchctl unload` → `load` で再起動 |
| 2 | `/notify` が無音 | `voice_enabled` が false / `voice_id` 未設定 / ElevenLabs API キー未設定 | `PULSE.toml` の `[voice] enabled = true` を確認。`/interview` で voice\_id 再設定。`ELEVENLABS_API_KEY` 環境変数を確認 |
| 3 | Skill が発火しない | SKILL.md の description が曖昧 | `USE WHEN` / `NOT FOR` を具体的に書き直す。CreateSkill の実効性テストを再実行 |
| 4 | Hook が失敗 | exit code が不正、JSON 出力フォーマットが不正 | フックは stdin で JSON 受け取り、stdout で JSON を返し、exit 0 で成功を示す。`tool-failures.jsonl` で詳細を確認 |
| 5 | ISA が work.json と非同期 | ISASync hook 無効 / ISA frontmatter に `phase` フィールドなし | `[hooks] enabled = true` を確認。ISA.md に `phase:` フィールドがあることを確認 |
| 6 | Containment Guard で書き込みブロック | プライバシーゾーン外への書き込み | `containment-zones.ts` でゾーン設定を確認。意図した書き込みならゾーン定義を追加 |
| 7 | Algorithm が phase 移動しない | モード分類が MINIMAL/NATIVE を選択し ALGORITHM に入っていない | プロンプトに `ALGORITHM:` を明示。Tier を `E2:` 以上で明示 |
| 8 | `/context-search` が空 | `work.json` または `session-names.json` 未生成 | `ls ~/.claude/PAI/MEMORY/STATE/` で確認。ISA Scaffold でセッションを登録 |

### 詳細トラブルシューティング手順

#### Pulse が起動しない

```
# 競合プロセス確認
lsof -i :31337

# プロセス終了
kill -9 <PID>

# Pulse 再起動
launchctl unload ~/Library/LaunchAgents/com.pai.pulse.plist
launchctl load ~/Library/LaunchAgents/com.pai.pulse.plist

# 起動確認
curl -s http://localhost:31337/api/pulse/health | jq
```

#### /notify が無音

```
# voice 設定の確認
cat ~/.claude/PAI/PULSE/PULSE.toml | grep -A 3 "\[voice\]"

# ElevenLabs API キーの確認
echo $ELEVENLABS_API_KEY

# voice_id なしで試す
curl -s -X POST http://localhost:31337/notify \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "voice_enabled": false}'
```

#### Hook が失敗

```
# Hook 失敗ログの確認
cat ~/.claude/PAI/MEMORY/OBSERVABILITY/tool-failures.jsonl | jq .

# フックを手動でテスト
echo '{"tool_name": "Edit", "tool_input": {"file_path": "/tmp/test.md"}}' \
  | bun ~/.claude/hooks/ContainmentGuard.hook.ts
```

フック正常終了の要件:

* stdin: JSON オブジェクト (hook input)
* stdout: JSON オブジェクト (hook result)
* exit code: 0 = 成功、非 0 = 失敗

#### Containment Guard でブロックされる

```
# containment-zones.ts でゾーンを確認
cat ~/.claude/hooks/lib/containment-zones.ts

# 意図した書き込みの場合: ゾーン定義を追加
```

#### /context-search が結果を返さない

```
ls -la ~/.claude/PAI/MEMORY/STATE/
cat ~/.claude/PAI/MEMORY/STATE/work.json | jq .
cat ~/.claude/PAI/MEMORY/STATE/session-names.json | jq .
ls ~/.claude/PAI/MEMORY/WORK/
```

## ■調査者所感

PAI は単発のフレームワークというより「Claude Code を OS とみなした上で、その上にユーザーの目標と記憶を据える」という思想の実装です。調査して印象的だったのは次の 3 点です。

* **テキストファースト**: すべての記憶を Markdown で保持する設計は、Vendor lock-in を最小化し、grep / ripgrep / Git でそのまま運用できる強みがあります。RAG 用の embedding を持たないにも関わらず Knowledge Graph / ContextSearch が機能するのは、観測ファイル (`tool-activity.jsonl` 等) と work.json レジストリで十分な検索面を確保しているためです
* **Hooks の細かさ**: 37 本のフックはやり過ぎに見えますが、UserPromptSubmit / PreToolUse / PostToolUse / Stop / SessionStart / SessionEnd という Claude Code の主要ライフサイクルに対応させると、副作用の挿入箇所として理にかなっています。ISASync や CheckpointPerISC のように「ISA の進捗を git commit と同期する」発想は、AI 駆動開発の検証性を高めます
* **macOS 依存**: launchd 前提のため Linux / Windows は対象外です。Pulse を systemd 化するコミュニティポートはありますが、現状の本流は macOS 専用と割り切るのが現実的でしょう

## ■まとめ

PAI (Personal AI Infrastructure) は、Claude Code を実行基盤として「TELOS (自己定義) → Algorithm (7 フェーズ実行) → ISA (完了定義) → Memory (永続記憶)」の循環を一貫したシステムとして組み上げた Life Operating System です。45 skills / 171 workflows / 37 hooks / Pulse daemon / 12 security gates によって、テキストファーストで観測可能、かつ自己改善ループを持つ個人用 AI プラットフォームとして機能します。

この記事が少しでも参考になった、あるいは改善点などがあれば、ぜひリアクションやコメント、SNSでのシェアをいただけると励みになります！

## ■参考リンク

### 公式情報

### Daniel Miessler のブログ・動画

### Pack ドキュメント

### コミュニティ実装
