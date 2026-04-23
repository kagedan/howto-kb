---
id: "2026-03-17-完全解説compound-harness-context-engineering-aiエージェント時-01"
title: "【完全解説】Compound / Harness / Context Engineering - AIエージェント時代の3大開発手法を徹底比較"
url: "https://qiita.com/emi_ndk/items/e86ce7def46f440385f9"
source: "qiita"
category: "ai-workflow"
tags: ["OpenAI", "qiita"]
date_published: "2026-03-17"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

**「AIにコードを書かせているが、品質がバラバラで本番に出せない」**

2026年、この悩みを抱えるチームが爆発的に増えている。AIエージェントがコードを書く時代になったが、**エージェントを「管理する技術」が追いついていない**のだ。

この問題に対して、3つの革新的な開発手法が登場した：

1. **Compound Engineering** — Every社が提唱。「作業が蓄積するほど次の作業が楽になる」
2. **Harness Engineering** — OpenAIが提唱。「100万行をゼロ人間コードで書いた」方法論
3. **Context Engineering** — Anthropic/Martin Fowlerが体系化。「モデルが見る世界を設計する」

結論から言うと、**この3つは競合ではなく補完関係にある**。この記事で全貌を解説する。

## なぜ今、新しい開発手法が必要なのか

従来のソフトウェア開発はこうだった：

```
人間がコードを書く → 人間がレビューする → 人間がデプロイする
```

2026年のAIエージェント開発はこうなった：

```
人間が意図を伝える → AIが書く → AIがレビューする → 人間が判断する
```

**問題は、この新しいフローに最適化された開発手法が存在しなかったこと**だ。プロンプトエンジニアリングは単発のやり取りには有効だが、数千回のエージェント実行を管理する方法論ではない。

## 全体像：3つの手法の関係

```
┌─────────────────────────────────────────────────────────┐
│                Context Engineering（最広義）              │
│  「モデルが見る世界を設計する」                             │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │           Harness Engineering（実行制御）           │  │
│  │  「エージェントの行動を制約・検証・修正する」          │  │
│  │                                                   │  │
│  │  ┌───────────────────────────────────────────┐    │  │
│  │  │      Compound Engineering（蓄積）          │    │  │
│  │  │  「各作業が次の作業を加速する仕組み」        │    │  │
│  │  └───────────────────────────────────────────┘    │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

| 手法 | 提唱者 | 一言で言うと | フォーカス |
| --- | --- | --- | --- |
| Context Engineering | Anthropic / Martin Fowler | モデルに何を見せるか | 入力の設計 |
| Harness Engineering | OpenAI (Codex) | モデルをどう制御するか | 実行の制御 |
| Compound Engineering | Every社 | 学びをどう蓄積するか | 知識の複利 |

---

# Part 1: Context Engineering — 全ての土台

## 定義

> 「Context Engineeringとは、モデルが見るものをキュレーションして、より良い結果を得ること」  
> — Bharani Subramaniam

プロンプトエンジニアリングが「何を言うか」なら、Context Engineeringは「**何を見せるか**」だ。

## コンテキストウィンドウの内部構造

エージェントのコンテキストウィンドウは「ワーキングメモリ」として機能する。トークン予算の典型的な内訳：

```
┌─────────────────────────────────────────┐
│  システムプロンプト / ルール    1-2%     │
│  プロジェクトルール           0.5-1.5%  │
│  会話履歴                    5-25%     │
│  ツール実行結果              25-75%    │ ← 最大の消費源
│  モデル推論                  5-15%     │
└─────────────────────────────────────────┘
```

**支配的な失敗モード：「コンテキスト枯渇」** — エージェントが先行命令を忘れ、タスクの連続性を失い、推論品質が劣化する。

## Claude Codeのコンテキストインターフェース

Martin Fowlerのチームが体系化した、Claude Codeにおけるコンテキスト注入の全手段：

| 手段 | タイプ | 誰が決定 | 用途 |
| --- | --- | --- | --- |
| **CLAUDE.md** | ガイダンス | 常時ロード | プロジェクト規約 |
| **Rules** | ガイダンス | ファイルアクセス時に自動ロード | パス別ルール |
| **Skills** | 命令/リソース | LLMまたは人間 | 遅延ロードされるタスク知識 |
| **Slash Commands** | 命令 | 人間 | 頻出カスタムタスク |
| **Subagents** | フル設定 | LLMまたは人間 | 並列ワークフロー |
| **MCP Servers** | プログラムアクセス | LLM | API・外部ツール・データ |
| **Hooks** | スクリプト | ライフサイクル | 決定論的な自動アクション |

### コンテキスト注入の4段階

```
Tier 1: ルールファイル（永続的・自動）
  → CLAUDE.md：~500-3000トークン。コスパ最高。

Tier 2: 対象ファイル読み込み（手動・精密）
  → 特定ファイル+行範囲を指定

Tier 3: テスト出力の注入
  → 最高のシグナルノイズ比

Tier 4: リポジトリマップ
  → 構造的概要で無目的な探索を防止
```

**アンチパターン：コンテキストダンピング** — コードベース全体を貼り付けるな。コンテキストウィンドウを即座に消耗し、関連情報がノイズに埋もれる。

---

# Part 2: Harness Engineering — OpenAIの100万行実験

## 定義

> 「LLMがCPUなら、Harnessはオペレーティングシステムだ」

Harness Engineeringとは、AIエージェントが**長期間にわたって正しい仕事を一貫して行う**ための制約・検証・フィードバックシステムを設計する手法だ。

## OpenAI Codexの衝撃的実験

```
┌────────────────────────────────────────┐
│         Codex Harness Experiment       │
├────────────────────────────────────────┤
│  期間:        5ヶ月                     │
│  コード量:    100万行                   │
│  手書きコード: 0行                      │
│  PR数:        約1,500                   │
│  エンジニアの役割: 環境設計 + 意図指定    │
└────────────────────────────────────────┘
```

## Harnessの3つの柱

### 柱1: アーキテクチャ制約

```
Types → Config → Repo → Service → Runtime → UI

✅ Service は Repo に依存できる
❌ Repo は Service に依存できない

→ 構造テスト（ArchUnit等）で自動強制
→ 守れない構造を物理的に作れなくした
```

### 柱2: Golden Principles（黄金原則）

```
1. 共有ユーティリティパッケージを優先する
2. データをYOLO式に探索しない
3. ドキュメントは機械可読なアーティファクト
```

### 柱3: フィードバックループ

```
エージェントが苦労する → シグナルとして扱う
→ 欠けているものを特定 → 環境にフィードバック
→ 次回のエージェント実行が改善
```

## 30-60-90日の導入プラン

```
Day 0-30: 最小限のHarness構築
├── 3〜5個のカスタムリンタールール
├── CI/CDパイプライン
└── CLAUDE.md/AGENTS.md の初期設定

Day 31-60: エージェントの自己認識能力
├── ログ・メトリクスへのアクセス
└── 構造テストの追加

Day 61-90: 自動修正と品質ダッシュボード
├── パターンドリフトの自動修正
└── フィードバックのルール化
```

**原則：「検出可能性を確立してから自律性を付与せよ。制約を確立してからスループットを最適化せよ」**

---

# Part 3: Compound Engineering — 知識の複利

## 定義

> 「各作業単位が、次の作業単位をより簡単にする — より難しくするのではなく」  
> — Every社

## 4フェーズループ

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Plan    │───▶│  Work    │───▶│  Review  │───▶│ Compound │
│  (40%)   │    │  (10%)   │    │  (30%)   │    │  (20%)   │
└──────────┘    └──────────┘    └──────────┘    └────┬─────┘
                                                     │
                                                     ▼
                                              次のループが
                                              より速くなる
```

### Phase 4: Compound — ここが革命

**Phase 3で終わるのが「従来のAI開発」。Phase 4があるのが「Compound Engineering」。**

```
問題を解決する
    ↓
6つのサブエージェントが動く
├── Analyzer: 何が解決されたか分析
├── Extractor: 再利用可能なパターンを抽出
├── Classifier: メタデータ付与
├── Writer: docs/solutions/ に構造化ドキュメント作成
├── Updater: CLAUDE.md にパターンを追加
└── Verifier: 次回同じ問題が自動検出されるか確認
```

## 8つの「アンラーン」すべき信念

| 旧信念 | 新信念 |
| --- | --- |
| コードは手で書くべき | 品質が重要、著者は問わない |
| 全行を目視レビュー | 自動システムが同じ問題を検出する |
| コードが主要な成果物 | コードを生む**システム**が主要な成果物 |
| 初回で完璧を目指す | 初回は95%ゴミ、高速に反復 |

## 50/50ルール

```
従来: 90% 機能開発 / 10% 改善 → 技術的負債が蓄積
Compound: 50% 機能開発 / 50% システム改善 → 複利で加速
```

---

# Part 4: AI-Nativeソフトウェアアーキテクチャ

## コンテキスト局所性の原則

```
Context Locality = 1 / avg(|R(C)|)

設計目標:
  90%の変更 → 5ファイル以下、15Kトークン以下で完結
```

## ファイルサイズ＝最もレバレッジの高い指標

| サイズ | 影響 | 推奨 |
| --- | --- | --- |
| <200行 | 最適 | 理想的 |
| 200-400行 | 良好 | ターゲット |
| 500-800行 | 劣化明確 | リファクタリング |
| 800行以上 | 敵対的 | 即時対応必須 |

**実測データ：ファイル分割後、リトライループが30-50%減少、「間違った場所の編集」が40-60%減少した。**

## エージェントフレンドリーなAPI設計

関数シグネチャはエージェントにとって**プロンプト**として機能する。

**敵対的：**

```
def process(data, opts=None):
    """Process the data."""
```

**エージェントフレンドリー：**

```
@dataclass(frozen=True)
class ProcessingOptions:
    """# INVARIANT: threshold must be in [0.0, 1.0]"""
    threshold: float = 0.5
    mode: ProcessingMode = ProcessingMode.FAST

def process_data(
    input_data: ProcessingInput,
    options: ProcessingOptions = ProcessingOptions()
) -> ProcessingResult:
    """# PRECONDITION: input_data.items is non-empty
    # POSTCONDITION: result.processed_count == len(input_data.items)"""
```

## エージェント敵対的アンチパターン

| アンチパターン | 失敗モード | 修正方法 |
| --- | --- | --- |
| メタクラスマジック | メソッドが見えない | 明示的宣言 + 型スタブ |
| 暗黙のグローバル | 隠れた依存関係 | 明示的パラメータ |
| 副作用の未文書化 | save()がメール送信 | 関心の分離 |
| 深い継承（5+レベル） | ~870行の読込が必要 | 継承より合成 |

## AI-Readiness メトリクス

```
コアメトリクス:
  平均ファイルサイズ:    < 300行
  テストカバレッジ:      > 80%
  型カバレッジ:          > 90%

エージェント固有メトリクス:
  初回成功率:      > 70%
  平均リトライ数:  < 2回
  レビュー却下率:  < 15%
```

---

# Part 5: コーディングエージェントのツール設計

## 3つのAIコーディングツールアーキテクチャ

```
Completion型（Copilot） → ツールなし、自律性なし
Chat型（ChatGPT）      → 実行ループなし
Agent型（Claude Code）  → 構造化ループで動作
```

**これらはスペクトル上の点ではなく、根本的に異なるシステム。**

## セキュリティ：5層防御モデル

```
Layer 1: 権限モード（Read-only / Supervised / Autonomous）
Layer 2: Git Worktree隔離
Layer 3: コンテナサンドボックス
Layer 4: ネットワーク出口フィルタリング
Layer 5: プロンプトインジェクション対策
```

## モデルルーティング：コストを10分の1にする

| タスク | モデル | コスト |
| --- | --- | --- |
| 計画生成 | Sonnet | $0.02-0.05 |
| 大規模実装 | Sonnet | $0.15-0.50 |
| アーキテクチャ | Opus | $0.30-1.20 |
| リント | Haiku | $0.002-0.008 |

**最適配分: 80% Haiku / 15% Sonnet / 5% Opus → 60-70%コスト削減**

---

# Part 6: Compound Development Workflows

## Dispatcherパターン

```
┌─────────────────────────────────────────────────┐
│              Human Dispatcher                    │
├──────────┬──────────┬──────────┬─────────────────┤
│ Agent A  │ Agent B  │ Agent C  │    Agent D      │
│ auth/    │ db/      │ api/     │    tests/       │
└──────────┴──────────┴──────────┴─────────────────┘
     │          │          │            │
     ▼          ▼          ▼            ▼
  worktree  worktree  worktree      worktree
```

## Git Worktreeによる無料の隔離

```
git worktree add ../worktree-auth -b feature/auth-rate-limit
git worktree add ../worktree-db -b feature/db-migration
git worktree add ../worktree-api -b feature/api-activity
# 各エージェントが独立に作業 → コンフリクトゼロ
```

## 6つの並列ワークフローパターン

| パターン | 並列度 | 用途 |
| --- | --- | --- |
| Spike & Converge | 探索的 | アーキテクチャ判断 |
| Test-First Delegation | 低 | 仕様が明確な機能 |
| Refactoring Pipeline | 高 | 大規模変更 |
| Doc Sweep | 高 | 一括ドキュメント更新 |
| Parallel Review | 高 | PRバックログ消化 |
| Security Parallel | 中 | セキュリティクリティカル |

## 実測データ：並列化の効果

| 指標 | 逐次（1エージェント） | 並列（4エージェント） |
| --- | --- | --- |
| 壁時計時間 | ~2時間 | **~35分** |
| 計算コスト | $2.00 | $2.00（同一） |
| コンフリクト | 0 | 0 |

> **「タスクが独立なら並列化は無料 — 同じトークン消費で70%高速」**

---

# Part 7: Anthropicの長時間エージェントハーネス

## 2エージェントパターン

```
Initializer Agent（1回） → Coding Agent（繰り返し）
  init.sh作成               claude-progress.txt を読む
  進捗ファイル初期化          git logで状態把握
  初期コミット              最優先タスクを選択→増分開発
```

**「各セッションは前回の記憶なしに始まる」** — 構造化されたハンドオフが必要。

---

# Part 8: Scaffolding — 第4の概念

```
Scaffolding（足場）: エージェント起動「前」
├── システムプロンプト組み立て
├── ツールスキーマ構築
└── Eager Construction

Harness（手綱）: エージェント起動「後」
├── ツールディスパッチ
├── コンテキストコンパクション
└── 安全性強制
```

---

# 3つの手法を統合する

## 統合アーキテクチャ

```
┌──────────────────────────────────────────────┐
│         Context Engineering Layer            │
├──────────────────────────────────────────────┤
│         Harness Engineering Layer            │
├──────────────────────────────────────────────┤
│       Compound Engineering Layer             │
├──────────────────────────────────────────────┤
│         Scaffolding Layer                    │
└──────────────────────────────────────────────┘
```

## AI出力を検証する3つの質問

1. **「ここで一番難しかった判断は何？」**
2. **「却下した代替案は何？なぜ？」**
3. **「一番自信がないところは？」**

---

# さらに深く学ぶ：System Design Patterns

この記事の内容をさらに深掘りしたい方のために、**118記事の無料リファレンス**を公開している。

Coding Agent Tool Design

AI-Native Software Architecture

Compound Development Workflows

---

## まとめ

* **Context Engineering** = モデルが見る世界を設計する
* **Harness Engineering** = エージェントの行動を制約・検証・修正する
* **Compound Engineering** = 学びを蓄積して次の作業を加速する
* **Scaffolding** = エージェント起動前の環境構築
* **AI-Nativeアーキテクチャ** = ファイル<500行、型カバレッジ>90%、暗黙知をゼロに
* 3つの手法は**競合ではなく補完関係**
* OpenAIは100万行を人間コードゼロで構築済み
* **80% Haiku / 15% Sonnet / 5% Opus**でコスト60-70%削減

**2026年のエンジニアの仕事は「コードを書くこと」から「コードを書くシステムを設計すること」に変わった。**

---

## 参考リンク

Harness engineering: leveraging Codex in an agent-first world - OpenAI

Harness Engineering - Martin Fowler

Context Engineering for Coding Agents - Martin Fowler

Compound Engineering - Every.to

Building AI Coding Agents for the Terminal (arxiv: 2603.05344)

Effective harnesses for long-running agents - Anthropic

Learning from Every's Compound Engineering - Will Larson

System Design Patterns - Compound Engineering Section

---

**この記事が役に立ったら、いいね・ストックをお願いします！**

**質問：あなたのチームではAIエージェントをどう管理していますか？Context / Harness / Compound、どれに一番近い手法を使っていますか？コメントで教えてください！**
