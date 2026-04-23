---
id: "2026-04-01-claude-codeのskillsでハーネスエンジニアリングを実装した-ルール自動生成でコード品質-01"
title: "Claude CodeのSkillsでハーネスエンジニアリングを実装した — ルール自動生成でコード品質を継続改善する"
url: "https://zenn.dev/shintaroamaike/articles/df3ecc0ddee047"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "zenn"]
date_published: "2026-04-01"
date_collected: "2026-04-02"
summary_by: "auto-rss"
---

## はじめに

CLAUDE.md にプロジェクトのルールを書けば Claude Code は守ってくれます。  
**でも、そのルールを書くのは結局あなた自身です。**

`pathlib.Path` を使うこと、`Decimal` で金額計算すること、bare except を避けること——  
チームの暗黙知をすべて文章に起こし、漏れなく管理し続けるのは意外と手間がかかります。

**AutoHarness スキルはそのルール生成と改善を自動化します。**

* `/autoharness-init` を一度実行するだけで、プロジェクトを解析して  
  型チェック・lint・命名規則を `.claude/rules/harness.md` に自動集約
* ルール違反が起きたら `/autoharness-update` で自動改善。  
  繰り返すほどプロジェクト固有のルールが育つ

小規模な試験的評価（n=5）では、ハーネスなしで `pathlib.Path` 使用率 0/5・  
`Decimal` 使用率 0/5 だったタスクが、ハーネスありで両方 5/5 になりました。  
どちらも **指示文には書かなかったルール** です。

詳細・限界・設計思想は以下で説明します。

---

## AutoHarness とは

DeepMind が 2026 年に発表した論文 [AutoHarness（arXiv:2603.03329）](https://arxiv.org/abs/2603.03329v1) は、ゲームAIの「不正手」を自動検出するハーネスを自動生成するフレームワークを提示しています。

> **is\_legal\_action()** が True を返した手だけをAIに実行させる → 不正手を根本から排除できる

論文のコアは、**Thompson sampling を用いた木探索**で環境フィードバックを自動収集し、`is_legal_action()` を反復的に洗練させる点にあります。

このスキルは論文の**着想**（「不正手を定義して排除する」）をClaude Codeのコード生成に借用したものです。対応は以下のようになりますが、論文の厳密な最適化アルゴリズムとは本質的に異なります：

| 論文の概念 | このスキルでの対応 | 違い |
| --- | --- | --- |
| `is_legal_action()` | `harness_check.py` の検証ルール | 論文は自動生成・最適化、スキルは手動管理 |
| `propose_action()` | Claude Code のコード生成 | 同等 |
| Refinement loop | `/autoharness-update` を手動実行 | 論文は自動、スキルはユーザーが起点 |
| Environment feedback | エラーメッセージ・テスト結果 | 同等 |

---

## スキルの使い方とコマンド

リポジトリ: [shintaro-amaike/autoharness-skill](https://github.com/shintaro-amaike/autoharness-skill)

**セットアップ**はリポジトリをチェックアウトし、`.claude/skills` の3つのディレクトリを自身のプロジェクトの `.claude/skills/` にコピーするだけです。コピー後VS Code等を再読み込みすることでコマンドが実行できるようになります。

![](https://static.zenn.studio/user-upload/24bf91957e53-20260401.png)

![](https://static.zenn.studio/user-upload/843efa8c92f0-20260401.png)

### `/autoharness-init` — 初回セットアップ

![](https://static.zenn.studio/user-upload/707f89d604e3-20260401.png)

プロジェクトを解析（`pyproject.toml` / `tsconfig.json` / `.eslintrc` 等）して以下を自動生成します：

* **`.claude/rules/harness.md`** — 型アノテーション・命名規則・禁止パターン等の自然言語ルール
* **`.claude/rules/harness_check.py`** — lint / 型チェック / テストを実行して JSON で結果を返す検証スクリプト
* **`CLAUDE.md`** への `@.claude/rules/harness.md` 追記（自動読み込み用）

> **注意**: `CLAUDE.md` への `@ファイルパス` 記法による自動読み込みは、現時点の Claude Code で動作を確認していますが、公式仕様として明文化されたものではありません。Claude Code のバージョンによって動作が変わる可能性があります。

### `/autoharness-update` — ルールの改善

**コマンドを入力しなくても自動で動きます。**

コード生成タスクが一段落したとき、型エラーやテスト失敗が発生したとき、「この出力はおかしい」「うちではこう書く」というフィードバックを伝えたとき——これらのシグナルを検知して自律的にハーネスを改善します。

手動で明示的に実行したい場合は `/autoharness-update` と入力します。失敗を分析してルールと検証スクリプトを更新します。繰り返すほどプロジェクト固有のルールが育ち、毎回同じ指摘をしなくて済むようになります。

---

## スキルを使うメリット・デメリット

### メリット

* **ルールの一元管理**: 「型アノテーション必須」「`pathlib.Path` を使う」といったルールを `.claude/rules/harness.md` に集約。毎回プロンプトに書かなくてよくなる
* **プロジェクト適応**: `/autoharness-update` を繰り返すことで、チーム固有の命名規則・禁止パターンがルールに蓄積される
* **検証の自動化**: `python .claude/rules/harness_check.py` を CI に組み込めば、生成コードを自動検証できる

### デメリット・注意点

* **ルールをコンテキストに載せるコストがかかる**: `harness.md` が毎回コンテキストに載るため、トークン消費が増える。短い単発タスクではコスト増の割に効果が小さい場合がある（実測はしていない）
* **ルールの陳腐化リスク**: プロジェクトの技術スタックが変わったときにルールを更新しないと逆効果になる（`/autoharness-update` で対処）
* **初回セットアップが必要**: `/autoharness-init` を実行するまで効果なし

---

## 小規模試験的評価

### 評価の目的と限界

**この評価はあくまで参考程度のものです。** 各条件 n=5 の小規模実行であり、統計的有意性はありません。「傾向として差が見られた」という観察にとどめてください。

また、測定指標の多く（`has_type_annotations` など）はエージェント自身の自己申告値です。実際に mypy や ruff を実行した結果ではないため、正確性に限界があります。

### 評価の設計

#### 対象システムと背景

**シフト管理システム**を題材にしました。給与計算・スケジュール管理など実務でよくあるドメインで、バグが潜みやすいロジック（日付境界・金額計算）を含む点が特徴です。

#### 使用したタスク

![](https://static.zenn.studio/user-upload/f42ae5affe4d-20260401.png)

3種類のタスクを Claude Code エージェントに各 5 回実行させ、harness あり / なし の出力を比較しました（計 30 エージェント実行）。

**タスク1: 機能追加（`shift_manager.py`）**

型アノテーションなし・`pathlib` 未使用・テストなしの 120 行のベースコードに対して、以下を追加実装するよう指示しました：

* `calculate_hourly_pay(shift: dict) -> Decimal` — 時給計算（深夜割増 25% 込み）
* `calculate_weekly_summary(shifts: list) -> dict` — 週次集計
* `export_payroll_csv(shifts: list, output_path: Path) -> None` — CSV 出力

**ポイント**: 指示文にはコーディング規約（型アノテーション・pathlib・Decimal）を明示**せず**、harness があるかどうかでルールが伝わるかを見た。

**タスク2: バグ修正（`payroll.py`）**

意図的に 5 種類のバグを埋め込んだ 180 行のコードと 14 件の失敗テストだけを渡し、「テストをパスさせてください」と指示しました。ヒントは与えませんでした。

埋め込んだバグ：

1. **深夜跨ぎ計算バグ** — `23:00〜01:00` のシフトを正しく計算できない（日付境界の処理漏れ）
2. **週境界バグ** — 週の区切りが日〜土になっており、月〜日で集計すべきところを誤る
3. **浮動小数点誤差** — `float` で給与計算しており `0.1 + 0.2 ≠ 0.3` 問題が発生
4. **エンコーディングバグ** — CSV 出力時に `encoding` を指定せず、Windows で文字化け
5. **bare except** — `except:` が全例外を握りつぶして実際のエラーが隠れる

**ポイント**: バグの種類と場所はテスト名からある程度推測できるが、修正方針（`Decimal` 使用・週境界の仕様など）は harness ルールに書いてある場合のみ明示的に伝わる。

**タスク3: 機能拡張・リファクタリング（`schedule.py`）**

206 行の `ScheduleManager` クラスに対して以下の追加を指示しました：

* `optimize_schedule(constraints: dict) -> list` — 制約（最大連続勤務日数・休日数など）に基づくスケジュール最適化
* `export_schedule(format: str, output_path: Path) -> None` — CSV / JSON 両対応のエクスポート

**ポイント**: 既存クラスのスタイル（型アノテーションなし・`os.path` 使用）に合わせるか、harness のルールに従うかの判断が分かれる。

#### 測定項目

エージェントが完了後に自己採点した metrics.json の値を集計しました（自己申告）：

**機能追加タスク**:

* `has_type_annotations` — 型アノテーションが付いているか
* `uses_pathlib` — `pathlib.Path` を使っているか
* `uses_decimal` — `Decimal` で金額計算しているか
* `test_count` — テスト関数の数
* `handles_midnight_span` — 深夜跨ぎシフトを正しく処理しているか
* `estimated_lint_issues` / `estimated_type_errors` / `estimated_bugs` — 推定問題数

**バグ修正タスク**:

* `fixed_midnight_span` / `fixed_week_boundary` / `fixed_encoding` / `fixed_bare_except` — 各バグを修正したか（bool）
* `bugs_fixed_count` — 修正できたバグ数（0〜5）
* `has_type_annotations` / `uses_pathlib` / `uses_decimal` — 修正時に品質改善もしたか

**機能拡張タスク**:

* `has_type_annotations` / `uses_pathlib` — コーディング規約への準拠
* `test_count` — 追加したテスト数
* `handles_constraints` — 制約付きスケジューリングを正しく実装したか
* `exports_csv` / `exports_json` — 両フォーマット対応しているか

### 観察された傾向

#### Figure 1: 品質フラグ通過率

![品質フラグ比較](https://static.zenn.studio/user-upload/b68bd9507091-20260401.png)  
*Figure 1: タスク別・指標別の通過率（with/without harness、n=5）。左から機能追加・バグ修正・機能拡張。*

**機能追加タスク**（`shift_manager.py` に給与計算を追加・n=5）：

| 指標 | with harness | without harness | 観察 |
| --- | --- | --- | --- |
| 型アノテーション（5回中） | 5/5 | 3/5 | harness あり全件 |
| pathlib.Path 使用（5回中） | 5/5 | 0/5 | 明確な差 |
| Decimal 使用（5回中） | 5/5 | 0/5 | 明確な差 |
| 深夜跨ぎ対応（5回中） | 5/5 | 4/5 | ほぼ同等 |

`pathlib` と `Decimal` はハーネスルールに明記されていた項目で、差が顕著です。一方、「深夜跨ぎを正しく処理する」というロジック正確性は harness なしでもほぼ達成できており、ルールが効く場面と効かない場面があることがわかります。

**バグ修正タスク**（`payroll.py` の 14 件テスト修正・n=5）：

| 指標 | with harness | without harness | 観察 |
| --- | --- | --- | --- |
| 4バグ全修正（5回中） | 5/5 | 5/5 | 同等 |
| 型アノテーション追加（5回中） | 5/5 | 1/5 | 明確な差 |
| pathlib.Path 移行（5回中） | 5/5 | 0/5 | 明確な差 |
| Decimal 移行（5回中） | 5/5 | 0/5 | 明確な差 |

バグ修正率自体（テストパス）は harness あり/なしで差がありませんでした。`pathlib`・`Decimal` 移行や型アノテーション追加はハーネスルールで明示された場合のみ行われました。

**機能拡張タスク**（`schedule.py` に optimize/export 追加・n=5）：

| 指標 | with harness | without harness | 観察 |
| --- | --- | --- | --- |
| 型アノテーション（5回中） | 5/5 | 4/5 | わずかな差 |
| pathlib 使用（5回中） | 5/5 | 4/5 | わずかな差 |
| CSV エクスポート（5回中） | 5/5 | 5/5 | 同等 |
| JSON エクスポート（5回中） | 5/5 | 5/5 | 同等 |
| 制約対応（5回中） | 5/5 | 5/5 | 同等 |

機能拡張タスクでは機能要件（CSV/JSON エクスポート・制約対応）は両条件で差がなく、差はコーディング規約（型アノテーション・pathlib）にのみ現れました。

#### Figure 2: テスト数・バグ修正数

![テスト数・バグ修正数](https://static.zenn.studio/user-upload/f48c8f1800e9-20260401.png)

*Figure 2: （左）機能追加・機能拡張タスクのテスト数平均、（右）バグ修正タスクの修正バグ数平均（最大 5）。*

| タスク | 指標 | with harness | without harness |
| --- | --- | --- | --- |
| 機能追加 | テスト数（平均） | 24.2 | 16.8 |
| 機能拡張 | テスト数（平均） | 27.0 | 20.0 |
| バグ修正 | 修正バグ数（平均） | 4.4 | 4.0 |

テスト数は両タスクで with harness の方が多く、ハーネスにテスト要件が明記されていることが影響していると考えられます。バグ修正数は with: 4.4 vs without: 4.0 とわずかな差にとどまり、14 件のテストという明示的なゴールがあれば harness の有無に関わらず修正できることを示しています。

#### Figure 3: 推定エラー数

![推定エラー数](https://static.zenn.studio/user-upload/09915e26012a-20260401.png)  
*Figure 3: 推定エラー数（lint issues・type errors・bug count）の平均。エージェントの自己申告値、lower is better。*

| タスク | 指標 | with harness | without harness |
| --- | --- | --- | --- |
| 機能追加 | lint issues（平均） | 0.0 | 0.8 |
| 機能追加 | type errors（平均） | 0.0 | 0.2 |
| バグ修正 | type errors（平均） | 0.2 | 1.6 |
| 機能拡張 | lint issues（平均） | 0.6 | 1.0 |

機能追加・バグ修正タスクで推定 lint issues・type errors に差が出ました。ただしこれらはエージェントの自己申告値であり、実際に linter や mypy を通した結果ではないため、参考程度にとどめてください。

### 解釈の注意

* **「ルールに書いたから守った」**: `uses_pathlib` や `uses_decimal` の差はハーネスの効果というより「プロンプトに明示されたから従った」という側面が大きい。タスク自体が難しければ（バグ修正率など）ルール有無に関係なく達成される
* **n=5 の限界**: 5回の試行結果は確率的にばらつく。同じ設定で再実行すると異なる結果になり得る
* **自己申告の限界**: `estimated_type_errors` 等は実際の型チェッカーを通した数値ではなく、エージェントが「あると思う」と報告した推定値

---

## さいごに

Claude Code はプロンプトに書いたことは守ってくれます。でも「プロジェクトのルールを毎回書き続ける」のは結局あなたの仕事です。

AutoHarness スキルはそのコストを下げる試みです。`/autoharness-init` で一度セットアップすれば、あとは開発を続けながらハーネスが育っていきます。型エラーが出たとき、「この書き方はうちでは使わない」と伝えたとき——そのたびにルールが更新され、同じ指摘を繰り返さなくて済むようになります。

評価は n=5 の小規模なものですが、「指示文に書かなかったルールが適用される」という体験の変化は実感できます。ぜひ試してみてください。

**リポジトリ**: [shintaro-amaike/autoharness-skill](https://github.com/shintaro-amaike/autoharness-skill)（MIT ライセンス・改変自由）

より厳密な評価（実際の linter 実行・規模の大きな試験）や、ハーネスの自動最適化（論文の Thompson sampling に近い実装）は今後の課題です。

AIが書いたコードをレビューする時間より、AIにルールを覚えさせる時間に投資する——そういう使い方の一例として参考になれば幸いです。

いろいろな技術の組み合わせで、より良い開発環境を構築しましょう。

**関連する記事**  
<https://zenn.dev/shintaroamaike/articles/86187d64045449>  
<https://zenn.dev/shintaroamaike/articles/90040ef0b2a769>
