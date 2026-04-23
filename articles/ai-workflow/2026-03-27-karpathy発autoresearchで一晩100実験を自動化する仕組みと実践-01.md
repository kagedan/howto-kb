---
id: "2026-03-27-karpathy発autoresearchで一晩100実験を自動化する仕組みと実践-01"
title: "Karpathy発AutoResearchで一晩100実験を自動化する仕組みと実践"
url: "https://zenn.dev/0h_n0/articles/28e8fe4721f315"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-03-27"
date_collected: "2026-03-28"
summary_by: "auto-rss"
---

# Karpathy発AutoResearchで一晩100実験を自動化する仕組みと実践

## この記事でわかること

* AutoResearchの3ファイルアーキテクチャ（prepare.py / train.py / program.md）の設計思想と役割
* 5分固定予算の実験ループで一晩100回以上のML実験を自律実行する仕組み
* SkyPilotによるマルチGPU並列化で910実験/8時間を実現した拡張手法
* AutoKernelなど派生プロジェクトに見る「AutoResearchパターン」の汎用的な適用方法
* Goodhart's Lawやスケール制約など、自律実験ループ運用時の落とし穴と対策

## 対象読者

* **想定読者**: 中級〜上級のML/AIエンジニア
* **必要な前提知識**:
  + Python 3.10+の基本的なプログラミング
  + PyTorchによるモデル学習の基礎（`torch.nn`、オプティマイザ、学習ループ）
  + GPUを使ったML実験の経験
  + LLM（大規模言語モデル）の基本概念

## 結論・成果

Andrej Karpathyが2026年3月にリリースしたAutoResearchは、**630行のPython + 1つのMarkdownプロンプト**というミニマルな構成で、AIエージェントによる自律的なML実験を実現しました。公開されたリポジトリの報告によると、単一GPU上で2日間に700回の実験を実行し、20個の最適化を発見、それらを大規模モデルに適用したところ**学習時間が11%短縮**されたとのことです。GitHub上では公開5日で25,000スターを獲得し、2026年3月末時点で57,900スターに到達しています。

この記事では、AutoResearchの技術的な仕組みを分解し、実際にセットアップして動かす手順、そしてGPUクラスタへのスケーリングや他ドメインへの応用まで解説します。

## Karpathyの思想を理解する：vibe codingからAutoResearchへ

AutoResearchを理解するには、Karpathyが提唱するAI開発の進化段階を把握すると見通しが良くなります。

### 3つのフェーズ

Karpathyは2025年に「**vibe coding**」という概念を広め、2026年にはその先のフェーズを次のように整理しています。

| フェーズ | 人間の役割 | AIの役割 | 具体例 |
| --- | --- | --- | --- |
| Vibe Coding（2025年〜） | プロンプトを書き、コードをレビュー | コードを生成 | GitHub Copilot、Cursor |
| Agentic Engineering（2026年〜） | エージェントをリアルタイムで指揮 | コード生成 + ツール操作 + 判断 | Claude Code、Devin |
| Autonomous Research | 研究の方向性を設定 | 仮説生成→実験→評価→改善を自律実行 | **AutoResearch** |

Karpathyは自身のX投稿で「2025年11月には80%手動・20%エージェントだったコーディングが、12月には80%エージェント・20%手動に逆転した」と報告しており、その後はほぼすべてをエージェントに委任していると述べています。AutoResearchはこの延長線上にある、**人間が寝ている間にAIが研究を進める**というコンセプトの具体的な実装です。

**注意点:**

> この3フェーズはKarpathyの個人的な分類であり、業界全体で合意された定義ではありません。実際の開発現場ではフェーズが混在しており、タスクの種類に応じて使い分ける必要があります。

## AutoResearchの3ファイルアーキテクチャを分解する

AutoResearchの設計上の最大の特徴は、\*\*3つのファイルに厳密な役割分担を定義する「契約」\*\*にあります。この設計により、評価基準の一貫性を保ちながらエージェントの自由度を確保しています。

### ファイル構成と責務

| ファイル | 編集権限 | 行数 | 役割 |
| --- | --- | --- | --- |
| `prepare.py` | 不変（人間もエージェントも変更不可） | 約200行 | データ準備、BPEトークナイザ（語彙8,192）、評価メトリクス定義 |
| `train.py` | エージェントのみ | 約630行 | GPTモデル定義、オプティマイザ、学習ループ |
| `program.md` | 人間のみ | Markdown | 研究方針、制約条件、実験ルール |

この設計の要は`prepare.py`の不変性です。評価メトリクス（**val\_bpb**: validation bits-per-byte、値が低いほど良い）が固定されることで、すべての実験が同じ物差しで比較可能になります。

### prepare.pyが固定する評価基準

`prepare.py`はBPEトークナイザの構築とデータの前処理を担当し、評価関数を提供します。このファイルを不変にすることで、エージェントが「メトリクスを操作して見かけ上の改善を作り出す」ことを防止しています。

```
# prepare.pyの役割（概念的な実装）
# 実際のAutoResearchリポジトリではnanochatベースの実装

import tiktoken

VOCAB_SIZE = 8192  # 固定: エージェントは変更不可

def build_tokenizer(corpus_path: str) -> tiktoken.Encoding:
    """BPEトークナイザを構築する。語彙サイズは固定。"""
    # コーパスからBPEトークナイザを学習
    # この関数の出力は全実験で共通
    ...

def evaluate(model, val_data) -> float:
    """検証データでbits-per-byteを計算する。

    Returns:
        val_bpb: 低いほどモデルの予測が正確
    """
    total_loss = 0.0
    total_bytes = 0
    for batch in val_data:
        loss = model.compute_loss(batch)
        total_loss += loss.item() * batch.num_bytes
        total_bytes += batch.num_bytes
    return total_loss / total_bytes
```

### train.pyのエージェント編集可能領域

`train.py`はGPTモデルの定義、オプティマイザの設定、学習ループを含むファイルです。エージェントはこのファイル内のあらゆる要素を変更できます。

```
# train.pyの構造（概念的な実装）
# エージェントが自由に変更できる領域

import torch
import torch.nn as nn

class GPT(nn.Module):
    """エージェントが構造を変更可能なGPTモデル。

    エージェントは以下を変更できる:
    - レイヤー数、ヘッド数、埋め込み次元
    - 正規化の種類（LayerNorm → RMSNorm等）
    - 位置エンコーディング（RoPE, ALiBi等）
    - Attention機構のバリエーション
    """
    def __init__(self, vocab_size: int = 8192, n_layer: int = 6,
                 n_head: int = 6, n_embd: int = 384):
        super().__init__()
        self.transformer = nn.ModuleDict({
            "wte": nn.Embedding(vocab_size, n_embd),
            "h": nn.ModuleList([Block(n_embd, n_head) for _ in range(n_layer)]),
            "ln_f": nn.LayerNorm(n_embd),
        })
        self.lm_head = nn.Linear(n_embd, vocab_size, bias=False)
        # tied embeddings: エージェントが発見する可能性のある最適化
        self.lm_head.weight = self.transformer["wte"].weight

# 学習設定もエージェントの変更対象
TRAIN_CONFIG = {
    "learning_rate": 3e-4,      # エージェントが調整
    "weight_decay": 0.1,        # エージェントが調整
    "batch_size": 64,           # エージェントが調整
    "max_steps": None,          # 5分の壁時計時間で自動制限
    "warmup_steps": 100,        # エージェントが調整
}
```

### program.mdによる研究方針の定義

`program.md`は人間が書くMarkdownファイルで、エージェントへの指示書として機能します。ここには研究の方向性、禁止事項、実験のルールが自然言語で記述されています。

```
# program.mdの構造例（概念的な例）

## 目標
train.pyを修正し、val_bpb（validation bits-per-byte）を最小化する。

## ルール
- 1回の実験は壁時計時間で5分以内
- prepare.pyは変更しない
- 実験ごとにtrain.pyを1つだけ変更する（複数変更の同時適用は禁止）
- 変更がval_bpbを改善しなかった場合、変更を元に戻す

## 探索方針
1. まずハイパーパラメータ（学習率、バッチサイズ）を探索
2. 次にアーキテクチャ変更（正規化、位置エンコーディング）
3. 最後にオプティマイザの改良

## 禁止事項
- 検証データをトレーニングに使わない
- prepare.pyの出力を改変しない
```

**なぜこの設計を選んだか:**

* **3ファイル分離**: 評価基準の信頼性を維持しつつ、エージェントの実験自由度を最大化するため
* **Markdown指示書**: コードではなく自然言語で研究方針を書くことで、ML知識のない人でも実験方針を設定できるため

## 実験ループの仕組みを理解する

AutoResearchの実験ループは「**ラチェットメカニズム**」と呼ばれる、改善のみを蓄積する仕組みで動作します。

### ラチェットループの動作フロー

1. **仮説生成**: AIエージェント（Claude Code、Codex CLI等）が`train.py`のコードと過去の実験結果を読み、改善仮説を立てる
2. **コード編集**: 仮説に基づいて`train.py`を変更する
3. **学習実行**: 5分の壁時計時間でモデルを学習する（起動やコンパイルの時間は除く）
4. **評価**: `prepare.py`の評価関数でval\_bpbを計算する
5. **判定**: val\_bpbが改善していれば変更を保持、そうでなければ元に戻す

### 5分固定予算の意味

実験あたりの学習時間は壁時計で5分に固定されています。この設計には以下の意図があります。

| 特性 | 説明 |
| --- | --- |
| スループット | 12実験/時間、一晩（8時間）で約100実験 |
| 公平性 | すべての実験が同じ計算予算で比較される |
| 高速フィードバック | 5分ごとに結果が得られ、エージェントが素早く方針転換できる |

**ハマりポイント:**

> 5分の固定予算はナノスケール（数百万パラメータ）のモデルには適切ですが、より大きなモデルでは学習が収束せず意味のあるシグナルが得られない場合があります。GPU性能が低い場合も同様で、同じ5分でもステップ数が減るため実験の質が低下します。

### 実際に発見された最適化

Karpathyの報告および関連記事によると、AutoResearchのエージェントは2日間の実行で以下のような最適化を独立に「再発見」したとされています。

* **RMSNorm**: LayerNormからRMSNormへの置換（Google Brainの研究者らが形式化に数年かかった手法）
* **Tied Embeddings**: 入力埋め込みと出力層の重み共有
* **QK NormとRoPEの適用順序変更**: Attention機構内での正規化と位置エンコーディングの順序最適化
* **学習率スケジューリングの改善**: ウォームアップ比率とコサイン減衰の調整

これらの最適化を組み合わせて大規模モデルに適用したところ、GPT-2相当の性能に到達するまでの学習時間が2.02時間から1.80時間に短縮（約11%の効率改善）されたとKarpathyは報告しています。

## セットアップと実行手順

実際にAutoResearchを動かす手順を見ていきましょう。

### 前提条件

* NVIDIA GPU（H100で検証済み、RTXシリーズでも動作するコミュニティフォークあり）
* Python 3.10+
* [uv](https://docs.astral.sh/uv/)パッケージマネージャ
* LLMプロバイダのAPIキー（Claude、Codex等）

### インストールと初回実行

```
# 1. リポジトリのクローン
git clone https://github.com/karpathy/autoresearch.git
cd autoresearch

# 2. uvでの依存関係インストール
# uvが未インストールの場合: curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync

# 3. データ準備とトークナイザ構築（約2分）
uv run prepare.py

# 4. 単一実験の動作確認（約5分）
uv run train.py
```

手順4が正常に完了し、val\_bpbの値が出力されれば環境構築は成功です。

### エージェントループの起動

AutoResearchのエージェントループは、お好みのコーディングエージェント（Claude Code、Codex CLI等）を使って起動します。

```
# Claude Codeで起動する例
# autoresearchディレクトリ内で以下を実行
claude "program.mdの指示に従って、train.pyを改善する実験を繰り返してください"
```

エージェントは`program.md`を読み取り、`train.py`を編集→実行→評価のループを自律的に繰り返します。

**注意点:**

> LLM APIの呼び出し回数に応じてコストが発生します。API費用はモデルや構成によって大きく異なり、1実験あたり約$0.10、100実験で$10〜25程度が目安とされています（SkyPilotの910実験では約$9）。ただし、エージェントの推論量やコンテキスト長によっては$50以上になる場合もあります。長時間の実行前にAPIの利用制限と予算を確認してください。

## SkyPilotでGPUクラスタに拡張する

単一GPUでの逐次実験はスループットに限界があります。SkyPilotチームは2026年3月にAutoResearchをKubernetesクラスタ上で並列実行する実験を行い、その結果をブログで公開しています。

### 単一GPU vs マルチGPU

SkyPilotブログの報告によると、16台のGPU（H100 13台 + H200 3台）を使用した8時間の実験で以下の結果が得られたとのことです。

| 指標 | 単一GPU（逐次） | SkyPilot 16GPU（並列） |
| --- | --- | --- |
| 実験数/8時間 | 約96 | 約910 |
| val\_bpb改善 | ベースラインから2%程度 | 1.003 → 0.974（2.87%改善） |
| エージェントの振る舞い | 貪欲な山登り法 | 10-13実験の一括グリッド探索 |
| 総コスト | GPU $16 + API $5 | GPU $260 + API $9 |

### 並列化がエージェントの行動を変える

SkyPilotブログで報告された興味深い発見は、**GPU数が増えるとエージェントの探索戦略が質的に変化する**という点です。

単一GPUでは1つずつ仮説を検証する「貪欲な山登り法」になりますが、16GPUを与えると、エージェントは10〜13個の実験を「波」として同時に投入し、パラメータ間の交互作用を効率的に発見できるようになったとされています。

さらに、SkyPilotの報告によれば、エージェントはH100とH200の性能差を自律的に検出し、**探索的な実験はH100で、有望な候補の検証はH200で実行する**という2層戦略を自発的に採用したとされています。

### SkyPilotでの実行手順（概要）

SkyPilotを使ったスケーリングの基本的な流れは以下の通りです。

```
# experiment.yaml（SkyPilot設定ファイルの概念例）
# SkyPilotブログの説明に基づく構成

resources:
  accelerators: H100:1
  cloud: kubernetes

setup: |
  git clone https://github.com/karpathy/autoresearch.git
  cd autoresearch && uv sync && uv run prepare.py

run: |
  cd autoresearch && uv run train.py
```

```
# SkyPilotでクラスタに実験をサブミット
sky launch experiment.yaml -d  # -d: デタッチモード（非同期実行）

# ログの確認
sky logs <job-id>
```

**制約条件:**

> SkyPilotによる並列化は強力ですが、課題もあります。SkyPilotブログによれば、並列実験間で「良い変更」が衝突する場合のマージ戦略や、GPUクラスタのコスト管理（8時間で$260のGPU費用）が実用上の検討事項となります。

## AutoResearchパターンの他ドメインへの応用

AutoResearchの公開からわずか1週間で、同じパターンを他のドメインに適用する派生プロジェクトが複数登場しました。

### 主要な派生プロジェクト

### AutoResearchパターンの抽象化

これらの派生プロジェクトに共通する「AutoResearchパターン」は、以下の3要素に抽象化できます。

```
# AutoResearchパターンの概念的な実装

from dataclasses import dataclass
from typing import Protocol

class Evaluator(Protocol):
    """不変の評価関数（prepare.pyに相当）"""
    def evaluate(self) -> float:
        """スカラーメトリクスを返す。低いほど良い。"""
        ...

class Sandbox(Protocol):
    """エージェントが編集可能なコード（train.pyに相当）"""
    def run(self) -> None:
        """固定時間予算で実行する。"""
        ...

@dataclass
class AutoResearchLoop:
    """ラチェット式の自律実験ループ"""
    evaluator: Evaluator
    sandbox: Sandbox
    time_budget_seconds: int = 300  # 5分固定

    def run_experiment(self, agent) -> bool:
        """1回の実験を実行し、改善したかを返す。"""
        baseline = self.evaluator.evaluate()

        # エージェントがsandboxを編集
        agent.edit(self.sandbox)

        # 固定時間で実行
        self.sandbox.run()

        # 評価
        result = self.evaluator.evaluate()

        if result < baseline:  # 改善した
            return True
        else:
            agent.revert(self.sandbox)  # 変更を元に戻す
            return False
```

**なぜこのパターンが汎用的か:**

* **評価の不変性**: メトリクスが固定されていることで、エージェントが「ゲーム」できない
* **固定予算**: 時間制約があることで、実験が終了しないリスクを排除
* **ラチェット**: 改善のみを蓄積するため、長期的に必ずベースライン以上の成果が得られる

## よくある問題と対策

AutoResearchを実践する際に遭遇しやすい問題と、その対策をまとめます。

| 問題 | 原因 | 対策 |
| --- | --- | --- |
| val\_bpbが改善しなくなる（プラトー） | 局所最適に到達、または5分予算で収束しない変更を試行 | `program.md`で探索方針を変更（ハイパラ→アーキテクチャ等） |
| GPU OOMエラー | エージェントがバッチサイズや隠れ層を大きくしすぎる | `program.md`にメモリ上限の制約を追記 |
| LLM APIコストの増大 | 長時間の実行でAPI呼び出しが蓄積 | 予算上限の設定、実行時間の制限 |
| 実験結果の再現不可能 | ハードウェア差異で同じ5分でもステップ数が異なる | 同一ハードウェアでの比較に限定、ステップ数も記録 |
| Goodhart's Lawによるメトリクス悪用 | val\_bpb以外の品質が低下 | 複数メトリクスの監視、人間による定期的なサンプルチェック |

### Goodhart's Lawへの対処

AutoResearchの設計上、最も根本的なリスクは**Goodhart's Law**（メトリクスが目標になった時、それは良いメトリクスではなくなる）です。val\_bpbを最小化するためにモデルが「近道」を学習し、実際のテキスト生成品質が低下する可能性があります。

この問題に対する現実的な対策は以下の通りです。

1. **人間による定期チェック**: 50実験ごとに生成サンプルを人間が確認する
2. **複数メトリクスの監視**: val\_bpbだけでなく、生成テキストの多様性やperplexityも記録する
3. **変更の解釈可能性**: 各実験の差分（diff）をログに記録し、後から「何が効いたか」を追跡可能にする

## Sakana AI「AI Scientist」との比較

AutoResearchと同時期に注目を集めている自律研究システムとして、Sakana AIの「AI Scientist」があります。両者のアプローチの違いを整理します。

| 観点 | AutoResearch | AI Scientist（Sakana AI） |
| --- | --- | --- |
| スコープ | 単一ファイルのML学習最適化 | 研究アイデア生成→実装→論文執筆→査読 |
| 複雑度 | 630行 + Markdown | 大規模マルチエージェントシステム |
| コスト/実験 | GPU時間 + API数ドル | 約$15/論文（AI Scientist-v2の報告値） |
| 評価 | 単一スカラー（val\_bpb） | 複数段階（実装→結果→論文品質→査読） |
| オープンソース | MIT License | 一部公開 |
| 設計思想 | ミニマリズム（1メトリクス、1ループ） | 包括的（研究ライフサイクル全体） |

Sakana AIの報告によれば、AI Scientist-v2はワークショップレベルの査読で平均スコア6.33（上位約45%相当）を獲得し、査読プロセスを通過した論文を生成したとされています。ただし、これはメインカンファレンスではなくワークショップへの投稿であり、Sakana AI自身が透明性の観点から掲載前に論文を取り下げています。また、外部評価では実験実行の42%がコーディングエラーで失敗するなどの限界も指摘されています。一方、AutoResearchはML学習の最適化に特化することで、**「一晩で100実験」というシンプルさと実用性**を追求しています。

両者は競合関係ではなく、目的が異なります。AutoResearchは「**実験の自動化**」、AI Scientistは「**研究プロセス全体の自動化**」を目指しています。

## まとめと次のステップ

**まとめ:**

* AutoResearchは**3ファイル契約**（prepare.py不変、train.py可変、program.md人間指示）により、評価の信頼性とエージェントの自由度を両立している
* **5分固定予算のラチェットループ**で一晩100実験を実行し、改善のみを蓄積する仕組みが核心
* SkyPilotによる並列化で**910実験/8時間**にスケールでき、エージェントの探索戦略も逐次型からグリッド探索型に質的に変化する
* **AutoResearchパターン**（不変の評価関数 + 可変のサンドボックス + 固定時間予算）は、GPUカーネル最適化やApple Silicon対応など、ML学習以外のドメインにも適用可能
* **Goodhart's Law**やスケール制約など、自律実験ループ固有の課題への対策が運用上不可欠

**次にやるべきこと:**

1. [AutoResearchリポジトリ](https://github.com/karpathy/autoresearch)をクローンし、`prepare.py` → `train.py`の単一実験を手元のGPUで動かしてみる
2. `program.md`を自分のプロジェクトに合わせてカスタマイズし、一晩の自律実験を試す
3. 自分のドメイン（GPU最適化、ビルドパイプラインなど）に「AutoResearchパターン」を適用する構成を検討する

## 参考

---

## 関連する深掘り記事

この記事で紹介した技術について、さらに深掘りした記事を書きました：

---
