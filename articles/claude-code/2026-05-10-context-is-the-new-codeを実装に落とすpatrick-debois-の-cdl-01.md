---
id: "2026-05-10-context-is-the-new-codeを実装に落とすpatrick-debois-の-cdl-01"
title: "「Context is the New Code」を実装に落とす：Patrick Debois の CDLC をチームに導入する設計メモ"
url: "https://zenn.dev/aerign/articles/35e44677478bf4"
source: "zenn"
category: "claude-code"
tags: ["CLAUDE-md", "API", "AI-agent", "LLM", "zenn"]
date_published: "2026-05-10"
date_collected: "2026-05-11"
summary_by: "auto-rss"
query: ""
---

## TL;DR

* DevOpsDays の発案者 Patrick Debois が AI Engineer で **「Context is the New Code」** という講演を行い、**CDLC（Context Development Life Cycle）** という概念を提唱した。
* LLM はエンジン、コンテキストはその燃料。プロンプトを「その場限りの文字列」ではなく **生成・テスト・配布・監視・適応のループで管理されるコード** として扱う発想。
* 本記事では CDLC の5ステージを整理し、**`agent.md` ／簡易 Eval ／社内スキルディレクトリ ／コンテキスト改善バックログ** という最小構成でチーム導入する設計メモをまとめる。
* 落とし穴は4つ：依存関係地獄、テストの非決定性、セキュリティ（プロンプトインジェクション）、外部スキルの品質問題（"99.9%は低品質" と Debois 自身が断言）。

## 対象読者と前提

**対象：**

* LLM ／ AI エージェントを業務開発に組み込んでいるエンジニア
* プロンプトや指示書（`agent.md`、`CLAUDE.md`、`.cursorrules` 等）が増えてきて、管理が辛くなってきたチーム
* AI 活用を「個人技」から「組織の規律」に引き上げたいテックリード／プラットフォームエンジニア

**前提：**

* LLM API ／ AI エージェントフレームワーク（Claude Agent SDK、LangGraph、Mastra、独自実装など何でも）の基本を触ったことがある
* Git／CI／レビューフローを通常のソフトウェア開発で運用している

**扱わないこと：**

* 特定モデルのベンチマーク比較
* RAG の埋め込みアルゴリズム選定
* プロンプトエンジニアリングの個別テクニック

## 背景：DevOps から ContextOps へ

Patrick Debois は2009年に DevOpsDays を立ち上げ、Dev と Ops を分離していた前提を壊した人物だ。その本人が AI Engineer の登壇でこう問うた。

> "もしコンテキストがコードであるならば、我々はこれをより一貫した方法でどう扱うべきか？コンテキスト開発ライフサイクルはどのように見えるだろうか？"  
> — Patrick Debois, "Context Is the New Code"

DevOps が SDLC を再定義したように、AI 時代には **コンテキストに対する SDLC、すなわち CDLC** が要る、というのが彼の主張だ。

「Ops が Dev のようになった」のと同じ構造で、**Context が Code のようになる**。これは比喩ではなく運用上の要請である：プロンプトが本番挙動を直接決めるなら、レビュー・テスト・バージョン管理・ロールバック・監視の全部を持つべきだ、ということに他ならない。

## CDLC：5ステージの全体像

各ステージを順に見ていく。

## ① Generate：コンテキスト供給源を整理する

コンテキストは「人がプロンプト欄に打ち込む文字列」だけではない。Debois は次のような供給源を挙げる。

| 供給源 | 例 | 性質 |
| --- | --- | --- |
| 手動プロンプト | チャット欄の入力 | 揮発、非再利用 |
| 再利用可能な指示書 | `agent.md`、`CLAUDE.md`、システムプロンプトファイル | バージョン管理可能 |
| 外部ドキュメント | ライブラリの公式 doc、API リファレンス | LLM の学習データより新しい場合がある |
| 社内ナレッジ | RFC、ADR、Postmortem、設計判断 | 組織固有の前提 |
| 業務ツール | GitLab issue、Slack、Linear、Jira | 進行中の文脈 |
| 仕様 | Spec-driven development の仕様書 | 「正解」の拘束 |

> "我々は他のコンテキストも取り込むことができる。日常的に使用するライブラリのドキュメントがあれば、それを引き込みたい。なぜならLLMは最新のドキュメントを持っていないかもしれないからだ。"

実装上は、「そのプロンプトはどのソースを参照しているか」を **明示的に書き出す** ところから始める。

```
# agent.md (例)
agent: code-reviewer
purpose: 自社規約に沿ったPRレビュー
context_sources:
  - team-skills/coding-standards.md
  - team-skills/security-checks.md
  - external-docs/<library>-latest.md
  - internal/postmortems/2026-Q1-summary.md
constraints:
  - 機密情報を出力に含めない
  - 推測は推測として書く
```

## ② Test：Lint／意味評価／Eval／E2E と非決定性の扱い

> "コンテキストの変更による影響を知っているか？我々は物事をテストする方法について考えなければならない。"

Debois が示すテスト階層は4つに整理できる。

| レベル | 何を見るか | 実装 |
| --- | --- | --- |
| Lint | 構文・スキーマ・必須セクションの欠落 | YAML/Markdown linter、自作スクリプト |
| 意味評価 | 文章として通っているか、矛盾がないか | LLM-as-Grammarly（別LLMでレビュー） |
| Eval | 期待出力が得られるか | 入出力ペアを多数走らせて成功率を計測 |
| E2E | 実ツール連携を含めて期待通りに動くか | サンドボックス内で実エージェント起動 |

ポイントは **非決定性** だ。同じコンテキストでも結果はブレる。だから1回の成功/失敗ではなく **複数回実行して成功率（エラーバジェット）で判断** する。

```
# 簡易 Eval スケルトン (擬似コード)
cases = load_cases("evals/code-reviewer/*.yaml")
runs_per_case = 5
threshold = 0.8  # 80% 以上で合格

results = []
for case in cases:
    successes = sum(
        run_agent(case.input, agent_md="agent.md") matches case.expected
        for _ in range(runs_per_case)
    )
    results.append(successes / runs_per_case)

assert sum(r >= threshold for r in results) / len(results) >= 0.9
```

数字（5回試行、80%閾値、全体の90%通過）はチームの SLO として明示し、変更時に下回ったらブロックする運用にする。

## ③ Distribute：スキルとしてパッケージ化する

> "もし複数のプロジェクト、複数のチームで再利用したいコンテキストがあるならどうするか？我々にはライブラリという概念があった。コンテキストの一部をパッケージ化するというのはどうだろうか。"

再利用可能なコンテキストは **「スキル」** としてバージョン管理し、内部レジストリで配布する。最小構成では「社内モノレポの共有ディレクトリ」で十分。

```
team-skills/
├── coding-standards/
│   ├── skill.md
│   ├── examples/
│   └── version.txt        # 1.4.2
├── security-review/
│   ├── skill.md
│   └── version.txt        # 0.3.0
└── postmortem-writer/
    ├── skill.md
    └── version.txt        # 2.0.0
```

各 `skill.md` には、**目的／前提／使い方／既知の制限／変更履歴** を書く。これだけで「誰のローカルにあるか分からない」プロンプトが、組織の検索可能な資産になる。

将来的にレジストリ化を考えるなら、Anthropic Skills、自前の S3+メタデータ、もしくは GitHub Actions で配布するなどの選択肢がある。**最初からマーケットプレイスを作る必要はない。**

## ④ Observe：エージェントログ・PR・本番からのフィードバック収集

> "もし誰もがこのピースを欠いているのなら、我々はこのためのコンテキストを作成すべきだ。そしてそのコンテキストを全員に配布すれば、突然、改善のインパクトは全員のものになる。"

監視のソースは3層ある。

1. **エージェントの実行ログ** — どこでコンテキスト不足が起きたか、どのツール呼び出しで詰まったか
2. **PR レビューでの指摘** — レビュアーが繰り返し指摘するパターンは、コンテキストに昇格させる候補
3. **本番障害／ユーザー報告** — 一番痛いが、一番改善価値が高い

Debois は **本番失敗を自動的に Eval ケースに変換するツール** にも触れている。同じ問題の再発を防ぐだけでなく、Eval スイートそのものが組織のリアルな失敗から育っていく。

```
# context_improvement_backlog.yaml (例)
- id: CIB-2026-0042
  source: prod_incident
  symptom: "エージェントが社内固有の権限モデルを誤解しコマンドを生成"
  root_context_gap: "agent.md に権限モデルの定義が欠落"
  proposed_change:
    - team-skills/permissions-model.md を新設
    - agent.md の context_sources に追加
  affected_agents: [code-reviewer, deploy-helper]
  status: triage
```

## ⑤ Adapt：個人→チーム→組織のフライホイール

最後のステージは、**改善をスケールさせる仕組み** だ。1人が踏んだ問題を、その個人の学習で終わらせず、コンテキストとして還流させる。これを繰り返すと、組織のコンテキスト資産が複利で増えていく。

## 最小実装ステップ：MVP は4ファイル

ここまでの全部を一度に始める必要はない。最初は次の4つだけで十分機能する。

1. **`agent.md` を Git にコミット** — 一番よく使う1エージェント分の指示書を、属人化から引き上げる。
2. **`evals/<agent>/cases/*.yaml` を5〜10件作成** — 重要タスクの入出力ペア。CI に乗せる前に、まずは手動で回す。
3. **`team-skills/` ディレクトリを切る** — 共通の `skill.md` を1つ置くだけでOK。レジストリ化は後でいい。
4. **`context_improvement_backlog.yaml` を1ファイル用意** — Issue でもよい。まずは「気付き」を集約する場所を作る。

```
mkdir -p agents evals/code-reviewer/cases team-skills/coding-standards
touch agents/code-reviewer.agent.md
touch evals/code-reviewer/cases/01_basic_review.yaml
touch team-skills/coding-standards/skill.md
touch context_improvement_backlog.yaml
git add agents evals team-skills context_improvement_backlog.yaml
git commit -m "Bootstrap CDLC minimum scaffold"
```

これだけで、CDLC のループは回り始める。

## 落とし穴

### 1. 依存関係地獄の再来

スキルがスキルを参照しはじめると、npm／pip と同じ依存関係問題が起きる。**最初から SemVer とロックファイルを意識しておく** こと。

### 2. テストの非決定性を CI に乗せるとき

毎回ブレるテストを「赤」で止めると、CI が壊れたまま運用される未来になる。エラーバジェット方式（成功率 SLO）にして、「閾値を下回ったらブロック、上回ったら警告」のような階層化を初期から設計する。

### 3. セキュリティ：プロンプトインジェクションと悪意あるスキル

外部レジストリのスキルを盲信して取り込むと、プロンプトインジェクションや埋め込まれた指示でエージェントが想定外の挙動をしうる。Debois は **コンテキスト用のファイアウォール／スキャナ** という発想に言及している。当面の実用解は次のあたり：

* 信頼できるソースのみを `team-skills/` に取り込む
* 取り込み時に diff レビューを必須化
* 機密データへのアクセスを持つエージェントには外部スキルを使わない

### 4. "99.9% は低品質" 問題

Debois 自身が「現在公開されているスキルの99.9%は品質が低い」と断言している。**外部スキルは"参考資料"、組織で本気で使うものは自前構築** が現実的なポジションになる。

## まとめと次に試すこと

* LLM の性能を引き上げるレバーは、もうモデル選定よりも **コンテキスト管理の質** に移っている。
* CDLC は「生成・テスト・配布・監視・適応」を回すフレームワーク。それぞれを既存の SDLC ツール（Git／CI／レビュー）に重ねれば、ゼロから基盤を作る必要はない。
* MVP は **agent.md ／ Eval ／ team-skills ／ improvement backlog** の4要素。今週末に1時間で始められる。
* スケールしたときの利得は、フライホイール構造で複利になる。早く始めたチームほど差がつく。

次に試すこと：

ここまでが30日でやれる範囲。やってみて学んだことを、また書きます。

## 出典

---

## デプロイチェックリスト（運用メモ）

```
# プレビュー
npx zenn preview

# 公開する場合（frontmatter の published: true に変更してから）
git add articles/cdlc-context-is-new-code.md
git commit -m "Add CDLC implementation note"
git push origin main

# 予約公開する場合
# frontmatter に以下を追加（JST 想定）
# published: true
# published_at: 2026-05-10 09:00
```
