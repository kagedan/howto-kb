---
id: "2026-04-24-anthropicの3エージェントハーネスをrailsに取り入れる-01"
title: "Anthropicの3エージェントハーネスをRailsに取り入れる"
url: "https://zenn.dev/dely_jp/articles/a45bc3a9e69ab1"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "LLM", "OpenAI", "zenn"]
date_published: "2026-04-24"
date_collected: "2026-04-25"
summary_by: "auto-rss"
query: ""
---

## はじめに

こんにちは、クラシルでレシチャレの開発をしているkiyokuroです。

[前回の記事](https://zenn.dev/dely_jp/articles/31bd95c8135d54)では、Claude CodeのHooksでSafety Hookを実装し、決定論的なガードレールを敷いた話を紹介しました。ルール設計、Safety Hook、サブエージェントによる設計調査の自動化と進めてきましたが、1つ残っていた課題がありました。「次にどのskillを実行するか」を人間が判断し、順番に起動していたことです。

この記事では、Anthropicが公開した3エージェントハーネス（Planner / Generator / Evaluator）の設計を自分たちのRailsプロジェクトに取り入れ、実装のchunkを連鎖的に回すループを構築した過程を紹介します。

## Step 1: 自分たちの運用で見えた課題

前回までの状態では、Claude Codeのskillsとsubagentは十数個整備されていて、設計調査・コード生成・テスト実行・PR作成といった個々の作業はエージェントに任せられる状態でした。ただし、作業全体の流れを制御するのは人間です。

```
人間: /design-plan（設計調査を起動）
  ↓ 結果を読んで判断
人間: /implement（実装を起動）
  ↓ 結果を読んで判断
人間: /check-ci（テストを起動）
  ↓ 失敗したら修正を指示
人間: /create-pr（PR作成を起動）
```

この構成で3つの課題がありました。

1つ目は、skill間の判断を全て人間が担うため、人間の指示待ちが挟まるたびに作業が止まり、エージェントに任せられる区間でも待ち時間が発生することです。

2つ目は、コンテキストの飽和です。最近のClaudeの1Mコンテキストモデルではあまり起きないかもしれませんが、1つのセッションでWebリサーチとコード修正を繰り返すようなタスクでは、途中でコンテキストが圧縮されて序盤で読んだ情報が失われます。大きめのリファクタや複数モデル横断の実装では必ず起きる問題でした。

3つ目は自己評価バイアスです。エージェントが自分の成果物を評価すると甘めになりやすい、という問題で、Anthropicも後述のブログで「Evaluatorを分離する動機はGeneratorの自己評価が甘くなりがちだから」と述べています。

2026年3月にAnthropicが[Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)を公開しました。Planner / Generator / Evaluatorのコンテキストを分離し、Generator（生成）とEvaluator（評価）が対になって品質を高める構造です。Anthropicはこれを「GAN-inspired」と呼んでいます。GANは機械学習で、生成する側と判定する側を対立させることで精度を高める構造で、その発想を踏襲した設計という意味です。

この設計を自分たちのプロジェクトに取り入れることにしました。

## Step 2: 3エージェント構成の設計

Anthropicの設計では3エージェント（Planner / Generator / Evaluator）ですが、それらを順に起動して結果を受け渡す「指揮役」が必要です。この役をClaude Codeのmain session自身が担い、Orchestratorと呼ぶことにしました。main sessionはPlanner skillを直接実行し、後続のchunkループではGenerator / EvaluatorをTask tool経由で起動します。Orchestratorはエージェントを新設したわけではなく、main sessionにchunkループの指揮という責務を明示的に割り当てたものです。

結果として、Planner / Orchestrator / Generator / Evaluatorの4役割で構成しています。

```
人間: /planner <要件>
    ↓
Planner が 並列リサーチ → 設計書作成 → chunk分解 → plan.json生成
    ↓
人間が chunk分解をレビュー

人間: /orchestrator
    ↓
Orchestrator が chunkループを回す
  for each chunk:
    Generator subagent（fresh context）→ result.json
    Evaluator subagent（fresh context）→ critique.json
    verdict: APPROVED → 次chunk / NEEDS_REVISION → 再試行（最大3回）
    ↓
全chunk完了 → Draft PR作成 → チャットツール通知
```

| 役割 | 責務 | 実体 |
| --- | --- | --- |
| Planner | 要件をchunk群に分解し、各chunkの完了条件を定義する | skill |
| Orchestrator | chunkを順に実行し、GeneratorとEvaluatorを起動・制御する | skill。main sessionが担う |
| Generator | 1つのchunkを1つのfresh contextで実装する | subagent |
| Evaluator | Generatorの成果物を、完了条件に従って機械的に採点する | subagent |

人間が介入するのは(1)ゴールの提示、(2)chunk分解のレビュー、(3)最終PRのレビューの3箇所です。Orchestratorをmain sessionに置いたのは、Claude CodeのTask toolで起動したsubagentが親のコンテキストを引き継がない性質を利用するためで、Generator / Evaluatorはchunk境界でfresh contextから開始されます。Orchestrator自身のコンテキストは維持されますが、役割は次のエージェント起動を指揮することだけなので、蓄積はできる限り抑えられる構造にしています。

ファイル配置は以下のとおりです。

.claude/ の構成

```
.claude/
├── skills/
│   ├── planner/SKILL.md        # Planner skill
│   └── orchestrator/SKILL.md   # Orchestrator skill
├── agents/
│   ├── generator.md            # Generator subagent
│   └── evaluator.md            # Evaluator subagent
├── hooks/
│   └── stop_next_action.sh     # 停止時に次アクションを提示するStop hook
├── rules/                      # チーム共有ルール（git管理）
└── workspace/                  # 開発者ごとの実装計画と進行状態（gitignoreします）
    └── features/{feature}/
        ├── plan.json
        └── chunks/{chunk_id}/
            ├── spec.json
            ├── result.json
            └── critique.json
```

### Stop hook: ターン境界で次アクションを可視化する

Claude CodeのStop hookは、main sessionが1ターン分の応答を終えるたびに実行されます。これを利用して、ターン境界で「現在どのchunkまで進んでいて、次に何をすべきか」をmain sessionに注入する仕組みを組み込みました。毎ターンworkspaceを読み返さなくても、次の一歩が常にコンテキストに現れる状態を作り、Orchestratorが次の一歩を見失わないための補助にしています（セッションを再開したときにも同じ情報がそのまま出るので、作業の継続がしやすくなります）。

hookの登録は`.claude/settings.json`で行います。

.claude/settings.json（抜粋）

```
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash $CLAUDE_PROJECT_DIR/.claude/hooks/stop_next_action.sh",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

hook側のシェルスクリプトは、`.claude/workspace/ACTIVE`が指す`{feature}/{chunk_id}`と、chunkディレクトリ内のJSONファイル（spec.json / result.json / critique.json）の有無・内容から、次にすべきアクションを判定します。

.claude/hooks/stop\_next\_action.sh（抜粋）

```
ACTIVE_VALUE=$(head -n1 "$ACTIVE_FILE" | tr -d '[:space:]')
FEATURE="${ACTIVE_VALUE%/*}"
CHUNK_ID="${ACTIVE_VALUE##*/}"
CHUNK_DIR="${WORKSPACE}/features/${FEATURE}/chunks/${CHUNK_ID}"

if [ ! -f "${CHUNK_DIR}/result.json" ]; then
  NEXT="Generator 未実行。/orchestrator で Generator を起動してください"
elif [ ! -f "${CHUNK_DIR}/critique.json" ]; then
  NEXT="Evaluator 未実行。/orchestrator で Evaluator を起動してください"
else
  VERDICT=$(jq -r '.verdict // "UNKNOWN"' "${CHUNK_DIR}/critique.json")
  case "$VERDICT" in
    APPROVED)         NEXT="chunk ${CHUNK_ID} は APPROVED です。次の chunk に進んでください" ;;
    NEEDS_REVISION)   NEXT="chunk ${CHUNK_ID} は NEEDS_REVISION。Generator を再試行してください" ;;
    GENERATOR_FAILED) NEXT="GENERATOR_FAILED。FAILURES.md を確認してください" ;;
  esac
fi

cat <<EOF
[harness] 3エージェントハーネスが進行中です。
  feature: ${FEATURE}
  chunk: ${CHUNK_ID}
  next_action: ${NEXT}
EOF
```

このhookの出力はmain sessionのコンテキストに注入されるので、Orchestratorは次のターン頭で「次はEvaluatorを起動しよう」「次のchunkに進もう」を自力で判断できます。人間が「次はこれをやって」とプロンプトを投げ直さなくても、ループが続く構造です。

## Step 3: JSON Schemaで「完了の定義」を仕様化する

3エージェント構成で最も重要だったのが、GeneratorとEvaluatorの間で「何をもって完了とするか」をJSONで定める仕組み（Sprint Contract。Anthropicの用語を借りています）の設計です。曖昧な「動くこと」を、機械判定できる条件に書き換えるのが目的です。

Anthropicの元ブログは3エージェント構成の思想までで、エージェント間の仕様形式は別途考える必要がありました。ここはOpenAIの[Using PLANS.md for multi-hour problem solving](https://cookbook.openai.com/articles/codex_exec_plans)で紹介されている「リポジトリを知らない初心者でも1枚のドキュメントだけで実装を完走できる」ExecPlanの発想を、chunk単位のJSON仕様に構造化しました。

4種のJSONファイルでエージェント間のデータを受け渡します。

| ファイル | 書き手 | 読み手 | 役割 |
| --- | --- | --- | --- |
| plan.json | Planner | Orchestrator | 機能全体のchunk分解 |
| spec.json | Planner | Generator / Evaluator | 1 chunkのSprint Contract |
| result.json | Generator | Evaluator | 実装結果と自己チェック |
| critique.json | Evaluator | Orchestrator | 機械的な採点結果 |

spec.jsonが仕様の中核です。`acceptance_criteria`フィールドに、Evaluatorが機械的に判定できる条件を列挙します。

spec.json の例（社内情報を抽象化）

```
{
  "chunk_id": "003_controller",
  "context_for_cold_start": {
    "design_doc": "design-docs/{feature}.md",
    "depends_on_results": ["chunks/002_service/result.json"],
    "relevant_files": [
      "app/controllers/api/v1/base_controller.rb",
      "config/routes.rb"
    ],
    "relevant_rules": [".claude/rules/controllers/index.md"]
  },
  "acceptance_criteria": [
    {"type": "file_exists", "path": "app/controllers/api/v1/{feature}_controller.rb"},
    {"type": "route_exists", "method": "POST", "path": "/api/v1/{feature}"},
    {"type": "rubocop", "target": "app/controllers/api/v1/{feature}_controller.rb"},
    {"type": "grep_contains", "path": "app/controllers/api/v1/{feature}_controller.rb", "pattern": "before_action"},
    {"type": "forbidden_pattern", "pattern": "skip_auth_check"}
  ]
}
```

`acceptance_criteria`は6種のチェックタイプに対応しています。`file_exists`、`route_exists`、`rubocop`、`rspec`、`grep_contains`、`forbidden_pattern`です。曖昧な「動くこと」ではなく、機械的に判定できる条件だけを許可しています。

各タイプはEvaluatorがBash toolで決定論的に実行します（例: `rubocop`は`bundle exec rubocop <path>`のexit code判定）。EvaluatorのLLMは結果の解釈を持ち込まず、コマンド実行と記録だけを担当することで判定のブレを排除しています。

ただし、6種の決定論チェックだけでは拾えない観点もあります。「実装が冗長」「命名が不明瞭」など質的な指摘は、ルール化が難しくgrepでも捕まえにくい領域です。ここはEvaluatorから`simplify`（Claude Codeで事前定義されているスキル）を走らせ、その結果もcritique.jsonに取り込むようにしました。決定論チェックで「仕様違反していないか」、simplifyで「書き方として良いか」の二段階で評価する構造です。

なお、verdict（APPROVED / NEEDS\_REVISION）は決定論チェック6種の結果のみで決め、simplifyの出力はcritique.jsonに補助情報として記録するに留めています。Evaluatorが「仕様条件のみで判定する」原則はここでも崩していません。

`context_for_cold_start`は、fresh contextで起動されるGeneratorが過去の文脈なしで完走できるよう、設計書・先行chunkの結果・参照ファイル・ルールを詰め込む情報セットです。「このchunkだけ読めば実装できる」レベルを目指すことで、context resetを成り立たせています。

これらのJSONファイルはJSON Schemaで型を定義し、hookで機械検証しています。

## Step 4: GAN風ループで回してみた結果

Generator（実装する側）とEvaluator（採点する側）をコンテキストレベルで分離することが、この構成の核心です。

Evaluatorのsubagent定義の冒頭にはこう書いています。

.claude/agents/evaluator.md（抜粋）

```
## 原則

- Generator を信頼しない: result.json の acceptance_self_check は参考までにし、
  全 criteria を独立して再検証する
- 仕様条件のみで判定: spec.acceptance_criteria 以外の観点で
  NEEDS_REVISION を出さない
- strict 出力: 全項目に対して必ず pass/fail/skip/error を返す
```

同じコンテキストで実装と評価を行うと「さっき自分が書いたから動くはず」というバイアスが入ります。Evaluatorを別のfresh contextから起動し、result.jsonを参考情報に留めて全criteriaを独立再検証することで、このバイアスを排除しています。

### 実際に動かして起きたこと

ここで紹介する3回のテストに至るまでに、chunk分解の指針やacceptance\_criteriaのテンプレート、Evaluatorの原則などを何度か整え直しています。以下はその整備が一通り落ち着いた段階での結果です。

同じ機能A（ユーザー情報を自動で補填する機能）を2回テスト実行しました。1回目は5 chunk、2回目はchunk分解を改善して4 chunkで構成しています。3回目は別の機能B（特定操作のブロック処理）を5 chunkで実行しました。

試作段階の小さなサンプルであることを前置きしますが、3回のテスト（機能Aを2回、機能Bを1回、合計14 chunk）を通じて、12 chunkがattempt 1（初回）でAPPROVEDとなり、残り2 chunkはRSpecのchunkでNEEDS\_REVISIONが出てattempt 2で解決しました。

NEEDS\_REVISIONが出た具体的な例を紹介します。

1回目のテストで、RSpecのchunkのcritique.jsonに`grep_contains`のfailが記録されました。spec.jsonの`acceptance_criteria`が`spec/requests/api/v1/{resource}_spec.rb`というパスにテストファイルが存在することを要求していたのですが、Generatorは`spec/requests/api/v1/{resource}/create_spec.rb`という別のパスに作成していました。Generatorの実装内容自体は要件を満たしていましたが、仕様の書き方が曖昧だったためEvaluatorがNEEDS\_REVISIONを返した形です。

attempt 2ではGeneratorがcritique.jsonの`required_fixes`を読み、指定されたパスにファイルを作成し直してAPPROVEDとなりました。

critique.json（実際の出力を抽象化）

```
{
  "chunk_id": "005_rspec",
  "attempt": 1,
  "verdict": "NEEDS_REVISION",
  "checks": [
    {"type": "file_exists", "result": "pass"},
    {"type": "rspec", "result": "pass", "detail": "16 examples, 0 failures"},
    {"type": "rubocop", "result": "pass"},
    {"type": "grep_contains", "result": "fail",
     "detail": "指定パスにファイルが存在しない。Generatorは別パスに作成している"}
  ],
  "required_fixes": [
    "acceptance_criteria で指定されたパスにテストファイルを作成すること"
  ]
}
```

もう1件のNEEDS\_REVISIONは、プロジェクトのRSpec規約（`allow` + `have_received`パターン）違反をEvaluatorが検知した例で、こちらはループが想定通り機能したケースです。

一方で、ループでは検知できなかった問題もあります。3回目のテスト（機能B）では、全chunkがAPPROVEDで完走したものの、最終PRのレビューで2つの問題が見つかりました。1つはプロジェクト内で非推奨になっているモデル経由でデータを取得していたこと。もう1つはユーザー向けエラーメッセージがプロジェクトのガイドラインに沿っていなかったことです。

どちらも`acceptance_criteria`に落とし込めていない観点（ルール未明文化の暗黙知、6種のチェックタイプでは判定できない適切さの問題）で、人間のPRレビューが必要な領域として残っています。

同じ機能を2回実行したことで、chunk分解自体は実行ごとに変わることが見られました。1回目の5 chunk構成から、2回目はjobとcontrollerを1つに統合して4 chunkに削減しています。

## まとめ

Anthropicの3エージェントハーネスをRailsプロジェクトに取り入れた過程を紹介しました。試作段階のサンプル（3回のテスト・合計14 chunk）で12 chunkが初回APPROVED、2 chunkがattempt 2で解決し、ループの基本動作は確認できました。人間の役割は「次にどのskillを実行するか判断する」から「ゴールを定義し、chunk分解を確認し、最終PRをレビューする」に変化した一方、機械判定できない観点（非推奨パスの使用、エラーメッセージの文言）はEvaluatorでは捕まえられず、最終PRのレビューは引き続き人間の仕事として残っています。
