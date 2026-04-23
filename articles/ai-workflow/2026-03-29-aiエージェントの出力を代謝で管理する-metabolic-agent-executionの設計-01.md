---
id: "2026-03-29-aiエージェントの出力を代謝で管理する-metabolic-agent-executionの設計-01"
title: "AIエージェントの出力を代謝で管理する — Metabolic Agent Executionの設計"
url: "https://zenn.dev/zima11/articles/6622f0a55896e0"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "zenn"]
date_published: "2026-03-29"
date_collected: "2026-03-30"
summary_by: "auto-rss"
---

## はじめに

AIエージェントに何かを生成させるとき、あなたはその出力を信用できますか？

「生成した→OK」ではなく、「生成した→検証した→問題があれば修復した→それでも駄目なら巻き戻した」という流れを**コードレベルで保証する**仕組みが欲しくなった。

そこで辿り着いたのが、生物の「代謝」をモデルにした実行パターン——**Metabolic Agent Execution**だ。

この記事では、broadcast-os（AI放送局を自律制作するOS）に実装した**Metabolic Agent Execution**の設計を紹介する。実装の中心となるのが`run_metabolic_parallel`（Metabolic Execution Kernel）で、既存の並列実行にvalidation層を被せた構造になっている。

---

## なぜ「代謝」なのか

生物の代謝には3つの特性がある。

1. **変換**: 入力（栄養）を出力（エネルギー）に変換する
2. **検証**: 変換が正常に行われたか確認する
3. **修復・排出**: 問題があれば修正し、回収できなければ排出する

AIエージェントの実行も同じ構造で捉えられる。LLMへのプロンプト実行は「変換」、出力の品質チェックは「検証」、失敗時のリトライは「修復」、それでも駄目なら「ロールバック（排出）」だ。

この考え方を**Chunk**という実行単位で実装した。

---

## Chunk — 実行の最小単位

Metabolic Executionでは、すべての実行を**Chunk**という単位に分解する。Chunkは「1つのLLMタスク」に対応し、6種類のタイプがある。

```
AGENT_RUN = "agent_run"       # 複数エージェントの並列実行（独立）
PRIMARY_RUN = "primary_run"   # プライマリエージェントの出力
REVIEW_PASS = "review_pass"   # レビュアーパス（前の出力に依存）
BUILD_STEP = "build_step"     # イテラティブな構築ステップ
INVESTIGATION = "investigation"  # 調査・分析の単一実行
PRODUCTION = "production"     # 最終成果物の生成
```

タイプによって「前の出力に依存するか」「並列実行可能か」が決まる。`AGENT_RUN`は独立しているので並列実行できるが、`REVIEW_PASS`は前の出力が必要なので順次実行になる。

---

## Validator Ladder — 4段階の検証

Chunkの出力は4段階のラダー（梯子）で検証される。

```
L1: output existence  — 出力が存在し、空でない
L2: output quality    — 最低限の品質（文字数、繰り返しなし、エラー混入なし）
L3: brief alignment   — brief（指示）の要件との整合
L4: comparative merit — 比較系modeでの差別化（post-hocで全件比較）
                         例：複数エージェントが同じ結論を出していないか、
                             視点の多様性が確保されているか
```

L1でコケたら即ハードフェイル。L2以降は問題の深刻度によって「hard failure（修復不可）」か「warning（修復可能）」に分類される。

```
def validate_chunk(*, chunk, result, state, sensitivity=None) -> dict:
    # result dict から実行結果を取り出す
    output_text = result.get("output_text", "")
    status = result.get("status", "failed")

    # L1: 存在チェック
    if status == "failed" or not output_text:
        return _hard_fail("output_missing", "agent が出力を生成できなかった", ...)

    if len(output_text.strip()) < 10:
        return _hard_fail("output_too_short", f"出力が短すぎる", ...)

    # L2: 品質チェック（繰り返し、エラー混入など）
    quality_issues = _check_output_quality(output_text, sensitivity)

    # L3: brief整合チェック
    brief_issues = _check_brief_alignment(chunk, result, state)

    # L4: 比較merit（kernel側でpost-hocに実行）
```

重要なのは、**Lが上がるほど「意味的な検証」になる**という構造だ。L1は機械的な存在確認、L4はコンテンツ全体を俯瞰した品質比較。

---

## Repair — 失敗を修復する

検証でfailした場合、すぐに諦めない。`repair_chunk`が「なぜ失敗したか」をヒントに変換して、プロンプトを修正した上で再実行する。

```
async def repair_chunk(*, chunk, contract, state, execute_fn) -> dict:
    original_prompt = chunk.get("prompt", "")  # 元のプロンプトを取得

    hints = []
    for failure in contract.get("failing_checks", []):
        check = failure.get("check", "")
        if check == "repetitive_output":
            hints.append("前回の出力は文の繰り返しが多すぎました。各段落で異なる内容を述べてください。")
        elif check == "output_too_short":
            hints.append("前回の出力は短すぎました。より詳細に説明してください。")
        elif check == "error_in_output":
            hints.append("前回の出力にエラーメッセージが混入していました。")

    hint_text = "\n".join(f"- {h}" for h in hints)

    repair_prompt = (
        f"{original_prompt}\n\n"
        f"※ 前回の生成で検証に失敗しました。以下に注意してください:\n"
        f"{hint_text}"
    )
```

「繰り返しが多い」「短すぎる」「エラーが混入している」——それぞれの失敗タイプに対して具体的なヒントを生成してリトライする。**失敗の理由をフィードバックとして次の実行に渡す**のがポイントだ。

それでも修復できなければ、`rollback_chunk`でその実行をなかったことにする。

---

## Kernel — 並列実行とpost-hoc検証

Kernel（`run_metabolic_parallel`）は3フェーズで動く。

```
Phase 1: 全agentを並列実行（asyncio.gather）
         ↓ 元のparallel_compareと同じレイテンシ特性を維持
Phase 2: 各結果をpost-hocでvalidate → repairableならrepair
         ↓ 並列実行後に順次検証
Phase 3: comparative merit を全件揃った後にチェック
```

**並列実行はそのまま、検証だけpost-hocで追加**というのが設計のキモだ。既存の実行フローを壊さずにvalidation層を上から被せる形になっている。

---

## 実装の結果

Metabolic Execution Phase Aの実装後：

* **769 → 783 passed**（+14テスト）
* `parallel_compare` が metabolic kernel に切り替わった
* `ExecutionStateMemory`（各chunkの実行状態・修復回数・失敗履歴を保持するオブジェクト）がグラフを通じて下流に渡るようになり、実行履歴が追跡可能になった

現時点でPhase Aは「並列実行 + 検証 + 修復」まで。Phase Bでは**knotカタログ**（過去の実行パターンを学習した知識ベース）と**execution profile**（タスク種別ごとの実行設定）を組み合わせたルーティングを実装する予定だ。

---

## 設計の判断と反省

### よかった点

**既存コードを壊さなかった**。`parallel_compare`の並列実行特性を維持したまま、バリデーション層を上から被せる形にしたことで、既存のテストが全部通ったままPhase Aを入れられた。

**失敗を情報として扱った**。repairの際に「なぜ失敗したか」をヒントに変換する仕組みにより、単純なリトライではなく文脈を持ったリトライができている。

### 課題

**L4のcomparative meritはまだ弱い**。全件揃った後に比較するのは正しいが、「何をもって差別化されているか」の基準が曖昧。Phase Bでknot catalogを入れることで、このレイヤーを強化したい。

---

## まとめ

Metabolic Agent Executionをひとことで言うと、「**AIの出力を信用するのではなく、検証・修復のループで品質を保証する**」パターンだ。

生物の代謝は「うまくいくこと」を前提にしていない。変換に失敗することがあっても、修復し、排出し、次のサイクルを回す。AIエージェントの実行も、同じ構造でいいはずだ。

broadcast-osはまだ実機runで検証段階だが、このパターンが実際の動画生成品質にどう影響するかは別の記事で報告したい。

---

*このコードはClaude Opus 4.6との協働で書きました。設計判断はすべて自分で行い、Claudeは実装の実行を担当しています。この記事のドラフトもClaude（Sonnet 4.6）との対話から生まれました。*
