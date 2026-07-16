---
id: "2026-07-15-claude-codeとcodexを併用するためにpromptより先にverifyを設計した設計編-01"
title: "Claude CodeとCodexを併用するために、Promptより先にVerifyを設計した【設計編】"
url: "https://zenn.dev/izumuzui/articles/8367e87e403915"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "prompt-engineering", "AI-agent", "Gemini", "GPT"]
date_published: "2026-07-15"
date_collected: "2026-07-17"
summary_by: "auto-rss"
query: ""
---

## TL;DR

* Claude CodeとCodexの共存環境を、\*\*モデルの優劣ではなく「役割を交換しても残る境界」\*\*で設計した
* 規則を **Invariants(不変)/ Policies(交換可能)/ Extensions(3回目で追加)** に分離し、料金・モデル変更の影響をPoliciesに閉じ込める
* **Verify-first**:実装案より先に、要求ソースから受入条件・証明・停止条件をfreezeする
* 共有worktreeは**one writer**、独立reviewは**fresh contextの別インスタンス**、quotaは品質選定でなく**scheduling**にだけ使う
* 最初の**10件を校正期間**とし、結果をmetrics(意思決定journal)に記録してassignmentを更新する
* 初期構成はSmall Coreに絞る。テンプレートは[こちら](https://github.com/izumuzui/agent-orchestrator-template)

## はじめに

Claude CodeとCodexを両方契約していると、「どちらに何をさせれば得か」を考えたくなります。自分も最初は、Codexで計画し、Claudeで実装し、Codexでレビューする、という分担を考えました。

ただ、この決め方ではモデルの更新や料金体系の変更に弱いです。半年後には前提が逆転しているかもしれません。そこでClaudeとCodexに同じ設計を交互にレビューさせ、反論を次の案へ反映しました。使用したモデルは、**Codex側がGPT-5.6 sol、Claude側がClaude Fable 5**です。議論の詳しい経緯——Codexが自薦し、Claudeが利益相反を理由に回答を辞退した話——は[経緯編]にまとめたので、本記事では最終的に合意した設計だけを扱います。

最終的に中心に残ったのは、モデルの優劣ではなく次の規則です。

* 要求から、実装案より先に検証可能な受入条件を作る
* 共通知識は一か所に置き、各Agentの入口は薄くする
* 共有worktreeを書き換えるAgentは常に一つにする
* 独立reviewを行う場合は、実装履歴を引きずらないfresh contextの別インスタンスに渡す
* ループには停止条件と試行上限を付ける
* 役割の割り当ては固定せず、結果を記録して更新する

この記事は完成済みのベストプラクティス集ではありません。現時点で終わったのは設計上の合意とテンプレートの公開までで、後述する10件の試行はまだ実施していません。ここでは、これから検証できる形に落とした環境設計を紹介します。

## 議論で最初の案から変わったこと(要約)

出発点は `Knowledge → Agent Adapter → Script` の3層でした。共有する製品知識を `.ai/` に置き、`AGENTS.md` と `CLAUDE.md` は各ツール向けの入口にし、決定的に実行できる検証はスクリプトへ移す考えです。この方向自体は維持しましたが、初案には40近いファイルがありました。

参考にした `codex-first` は、Claudeがspecとreview、Codexが実装を担う設計です。ただし、その分担は契約コストを含む作者の環境に基づきます。自分のPattern Cで実装側が逆になったこと自体が、**Agent名をcoreへ埋め込むべきでない例**になりました。この記事でのPattern Cは、後述するP2へ現在のAgentを割り当てたpolicy名です。

Claudeから「使う前に分類体系を作りすぎている」と反論され、greenfieldではSmall Coreから始めることにしました。また、知識を分離しても、結局すべて読み込めば入力トークンは減りません。得られるのは重複排除と更新容易性です。トークン効率は、repository mapから必要な文書だけ読むことと、長い手順をスクリプトへ移すことで初めて改善します。

さらに議論を続けて、次も修正しました。

* 「CodexがPlan担当」は恒久ルールではなく、現在の契約に対する初期assignment policyとした
* quotaは品質で担当を選ぶquality routingから外し、合格した候補間のschedulingだけに使うことにした
* 独立reviewの最低線を「別provider」ではなく「別インスタンスかつfresh context」とした
* `.ai/handoffs/current.md` 一つを上書きする案をやめ、taskごとの一時snapshotにした
* Skillの同期基盤は初日から作らず、同じ手順が3回現れた時点でExtension候補として検討することにした

反論の価値は、最初の案に賛同が増えたことではなく、変更に弱い仮定がcoreから追い出されたことにありました。

## まずInvariants、Policies、Extensionsを分ける

この3つを同じ文書に混ぜると、料金変更のたびに安全規則まで編集することになります。

**Invariants** はAgentや契約が変わっても守る規則です。secretはmodel inputやtool出力経由のcontextへ送らない。private dataは承認済みproviderとretention設定の範囲だけで扱い、cloud送信禁止データはlocal-onlyのtoolへrouteする。rawなprivate contentをhandoff、metrics、reportなどの永続artifactへ残さない。外部状態の変更や破壊操作には明示承認を求める。検証結果なしに完了を宣言しない。共有worktreeはone writerとし、並列Agentはread-onlyの調査かレビューに限定する、といった内容です。

**Policies** は交換可能な運用判断です。どのrole patternを使うか、現在どのAgentを割り当てるか、低riskのレビューを何件おきに行うかを置きます。現在試そうとしているPattern Cは、後述するP2への次のassignmentです。

```
Codex: Plan / acceptance draft
  ↓
Claude: Implementation / test / fix
  ↓
別インスタンスのCodex: fresh review
  ↓
Claude: findingsがあればfix
```

これは「Codexの方が計画に優れる」というcore規則ではありません。現在の利用枠を、設計・レビューと実装反復に分配するための初期仮説です。

**Extensions** は、繰り返しが確認されてから追加するSkillやhookです。3回目を候補検討の目安にし、自動では昇格させません。まだ安定していない手順は通常のworkflowに残します。

## GreenfieldのSmall Core

最初に作るなら、次の程度で十分です。この構成はそのまま[テンプレートリポジトリ](https://github.com/izumuzui/agent-orchestrator-template)として公開しています。

```
.
├── .gitignore                 # /.agent-state/
├── AGENTS.md
├── CLAUDE.md
├── .ai/
│   ├── README.md
│   ├── knowledge/
│   │   ├── repository-map.md
│   │   └── decisions.md
│   ├── standards/
│   │   └── security.md
│   ├── verification/
│   │   └── common.md
│   ├── workflows/
│   │   ├── change.md
│   │   ├── review.md
│   │   └── routing.md
│   ├── handoffs/
│   │   └── template.md
│   └── metrics/
│       └── schema.md
├── scripts/agent/
│   └── verify-change.sh
└── .agent-state/              # Git管理外
    ├── handoffs/<task_id>.md
    └── metrics/task-events.jsonl
```

`.ai/README.md` は「何をいつ読むか」の目次です。`repository-map.md` は探索範囲を絞る地図であり、巨大な設計書にはしません。`decisions.md` はpolicyを変えた理由、`security.md` は共通riskとrepository固有riskを持ちます。`common.md` は検証結果の分類と共通コマンド、`change.md` はPlan、実装、review、fixの順序と停止条件、`routing.md` は後述するrole patternを持ちます。

知識更新は自然発生しないため、`change.md` の実装Doneとreview Doneの両方に「仕様・境界・検証手順の更新が必要か」を入れます。更新専用workflowを増やすのではなく、変更を知った時点の完了条件にします。

`template.md` は受け渡しの型だけをGit管理し、実データはtaskごとの `.agent-state/handoffs/<task_id>.md` に保存します。一つの `current.md` では並行taskが衝突し、前taskの情報も混ざるためです。metricsはhandoffの末尾に書かず、自由記述を持たないappend-onlyのJSONLとして別管理します。opaque IDでもcommitや時刻と突合できる仮名化データなので、event logは既定でGit外のアクセス制御された保存先へ置きます。repositoryにはschemaと、policy変更の集約された判断だけを残します。

`verify-change.sh` はlint、型検査、対象テストなどの安定した入口です。Agentが毎回コマンドを推測し直さないためのもので、すべての検証を一つの巨大スクリプトへ押し込む必要はありません。さらに `git check-ignore .agent-state/` が成功し、`git ls-files .agent-state/` が空であることも検査して、private handoffをfail closedでGitから外します。

## AGENTS.mdとCLAUDE.mdは薄くする

常に読む入口には、全知識ではなく「見落とすと危険なこと」とrouteだけを書きます。例えば `AGENTS.md` は次の程度です。

```
# Repository instructions

Before changing files:
1. Read `.ai/README.md`.
2. Use `.ai/knowledge/repository-map.md` to limit exploration.
3. Select the workflow routed from `.ai/README.md`.
4. State a verifiable stop condition before implementation.

Non-negotiable:
- Never send secrets through model input or tool-output context.
- Use private data only with approved providers and retention settings.
- Route cloud-prohibited data only to approved local-only tools.
- Do not persist raw private content in handoffs, metrics, or reports.
- Require explicit approval for destructive or external-state changes.
- Keep one writer on the shared worktree.
- Report verification as passed, failed, skipped, or environment-blocked.
```

`CLAUDE.md` も同じ安全subsetを直接持ち、残りだけClaude Code向けにします。

```
# Claude Code adapter

Read `.ai/README.md` and follow its routing.

Non-negotiable:
- Never send secrets through model input or tool-output context.
- Use private data only with approved providers and retention settings.
- Route cloud-prohibited data only to approved local-only tools.
- Do not persist raw private content in handoffs, metrics, or reports.
- Require explicit approval for destructive or external-state changes.
- Keep one writer on the shared worktree.
- Report verification as passed, failed, skipped, or environment-blocked.

Claude-specific:
- Use a fresh instance for independent review.
- Put task state in `.agent-state/handoffs/<task_id>.md`.
```

安全subsetの重複は意図的な例外です。`.ai/` への間接参照だけだと、その読込みに失敗した瞬間に制約も消えるからです。代わりに `verify-change.sh` で両adapterの安全blockが一致するか検査します。なおClaude Codeの公式文書では、`CLAUDE.md` から `AGENTS.md` をimportする方法も案内されています。adapter固有差分が少なければ、それも選択肢です。

## Promptより先にVerifyを書く

ここでいうVerify-firstは、「テストを多く書く」という意味ではありません。要求の出典から、実装案を見る前に受入条件を導くことです。writerが着手する前にrequirement source、受入条件、`acceptance_version`をhandoffへfreezeし、各acceptance IDをsourceの該当箇所へ対応付けます。着手後に意味を変える場合は旧版を残し、`scope_decision`として新しいversionを作ります。

例えば「期限切れのexport linkを使えなくする」という要求なら、先に次を固定します。

```
## Acceptance
- 期限内のlinkは従来どおり取得できる
- 期限切れのlinkは規定のerrorを返す
- 境界時刻はrepositoryのclock規約に従う
- 既存linkの保存形式を破壊しない

## Proof
- focused test: export link expiry cases
- regression: existing export tests
- common: ./scripts/agent/verify-change.sh

## Stop
- required proofがすべてpassedとなり、overallがpassedになる
- required proofが実行不能ならoverallをblockedとして返す
- 最大2回の修正で満たせなければblockedとして返す
```

実装者が自分の実装に合わせて後からoracle、つまり正解判定を作ると、同じ思い込みがコードとテストの両方に入ります。そこでorchestratorは、最初にtask ID、requirement sources、scopeだけのbootstrap packetをreviewerへ渡します。reviewerが受入条件を独立に再導出した後で、freeze済みacceptance、diff、検証結果を開示して差を見ます。これで循環oracleを完全には消せませんが、弱められます。

検証結果は必ず分けます。

```
overall: blocked
passed: 12
failed: 0
skipped: 1        # 事前にnon-requiredと定義、理由code: optional_platform
environment-blocked: 1  # required、理由code: service_unavailable
```

`skipped` や `environment-blocked` を成功へ丸めないことが重要です。`skipped` は事前にnon-requiredと定義したcheckだけに使い、required checkがblockedなら `overall: blocked` です。失敗と環境不足も、次の判断に必要な証拠です。

## Handoffは会話の要約ではなく、状態snapshotにする

handoffは長文の経緯ではなく、次のAgentが同じtaskを再現できる最小状態にします。

```
task_id: t_01HX8Q2M
risk_class: medium
risk_overlay: data_compatibility
intended_pattern: P2
requirement_sources:
  - docs/requirements/export-link.md
acceptance_version: 1
allowed_scope:
  - src/export/
  - tests/export/
forbidden_scope:
  - deployment/
acceptance:
  - A1: valid link remains usable
  - A2: expired link returns the specified error
acceptance_sources:
  A1: docs/requirements/export-link.md#valid-link
  A2: docs/requirements/export-link.md#expired-link
stop:
  max_fix_rounds: 2
verify:
  overall: blocked
  passed: 12
  failed: 0
  skipped: 1
  environment_blocked: 1
```

task IDは内容を推測できないopaqueな値にします。秘密、個人情報、非公開path、media由来のtext、ターミナルdumpは入れません。必要なら安全なrepository相対pathとテストIDだけを渡します。

## role patternとAgent名を切り離す

役割の構造をP0〜P3で表すと、Claude、Codex、Gemini CLI、Cursorが増えてもworkflowを書き直さずに済みます。

| Pattern | 構成 | 向くtask |
| --- | --- | --- |
| P0 | 1 instanceがplan・write・self-verify。独立reviewなし | 明白で低riskな小変更 |
| P1 | writer + fresh reviewer | 通常変更、独立reviewが欲しい場合 |
| P2 | planner + writer + fresh reviewer | non-trivial、受入条件の分離が効く場合 |
| P3 | primary + read-only explorerを最大2つ。その後P0〜P2へ戻る | 独立したread-heavy調査が2件以上ある場合 |

P3でもshared worktreeのwriterは一つです。複数Agentを並列に使うなら、提案や調査はread-onlyにし、採用案を一人のwriterが反映します。小さく曖昧なtaskを並列化すると、前提の違う案を統合する費用の方が大きくなるため、まず一つのcontextで要求を固めます。P0のself-verifyは独立reviewではなく、sentinel対象になった時点でP1相当へ上げます。

quality routingは例えば次のようにします。表にAgent名は入りません。

| risk / shape | pattern |
| --- | --- |
| high-riskで仕様が明確 | P1 |
| high-riskで新規性・横断性が高い | P2 |
| low-riskで定型・明確 | P0。ただしsentinel対象ならP1相当のreviewを追加 |
| low-riskでも新規性・横断性が高い | P1。独立planが必要ならP2 |
| 独立したread-heavy調査が2件以上 | P3を前置 |

次に、**quality routing** と **scheduling** を分けます。quality routingは、そのroleに必要な品質、安全性、tool accessを満たす候補を選ぶ段階です。schedulingは合格候補の中から、quota、rate limit、待ち時間、速度で実担当を選ぶ段階です。

quotaが余っていることを理由にquality floor未満のAgentへhigh-risk taskを落としてはいけません。候補がいなければ、待つ、scopeを小さくする、人間へ返す、のどれかです。記録では `intended_pattern` と `actual_assignment` を分け、変更時は `fallback_reason=rate_limit` などのenumを残します。

独立reviewを行う場合の最低線は、fresh contextを持つ別Agent instanceです。同じproviderでも成立します。cross-provider reviewは、似た学習やtoolingによる相関した盲点を減らすかもしれないので優先して記録しますが、現時点では仮説であり絶対条件にはしません。

riskは共通classとrepository overlayの二段にします。認証、課金、privacy、破壊操作、migration、infrastructure変更などを共通high-risk候補とし、「このrepositoryでは検索世代の切替もhigh-risk」のような固有条件だけoverlayへ追加します。

## Loopは長く回す仕組みではなく、止める仕組み

Claudeの公式記事では、agentが停止条件まで反復する仕組みを、turn-based、goal-based、time-based、proactiveの4種類に整理しています。この分類を製品機能そのものではなく、モデル中立な判断表として使います。

| Loop | Trigger | Stop | 選ぶ場面 |
| --- | --- | --- | --- |
| Turn-based | 人の依頼 | 完了判断または追加情報待ち | 探索、小変更、曖昧なtask |
| Goal-based | 明示goal | 受入条件達成または最大試行数 | 機械的に判定できる改善 |
| Time-based | 時刻・間隔 | cancel、queue完了、期限 | CIや外部状態の監視 |
| Proactive | event・schedule | 各taskのgoal + routine停止条件 | 成熟した反復業務 |

目標が曖昧なままGoal Loopへ移すと、誤った指標を満たすまで自動化されます。Time-basedは状態が変わる頻度より細かくpollしません。Proactiveは、permission境界、監査log、試行上限、circuit breakerが揃った後にだけ使います。基本はTurn-basedで始め、verifyが安定した部分だけ昇格させます。

## 最初の10件を校正期間にする

初期policyとして、最初の10件のnon-trivial taskはすべてindependent reviewへ回します。最低条件はfresh instanceで、可能ならproviderも変えます。

10件後は、high-riskを常にindependent review、low-riskは決定論的なcounterで5件目ごとにsentinel reviewします。sentinelは普段省略しているreviewを定期的に戻し、品質低下を探る標本です。medium-riskはrepository overlayで条件を定め、未定義ならindependent reviewを継続します。

escaped defect、つまり完了後に見つかった不具合があれば、過去行は書き換えません。新しいbugfix taskの `regression_of` から原因task IDを参照し、同じcounter keyの次の5件をindependent review必須へ昇格します。

v1ではcounter keyを `area_id:task_type` とし、単一orchestratorがtask受付・routing時にkeyごとの `routing_sequence` をatomicに予約します。その番号で5件目かを実装前に判定し、sentinelならindependent reviewをrequiredにします。並行taskも予約順で扱い、完了eventには予約済み番号を記録します。policyを変えたら `policy_version` を上げます。これを直列化できない環境では「5件目」を自動化せず、先にatomicな記録方法を用意します。

この「10件・5件ごと・次の5件」はまだ実測していない運用仮説です。十分な統計検定ができる標本数でもありません。目的は勝者モデルを決めることではなく、レビューを減らす判断を無記録で行わないことです。

## metricsはスコアボードではなく意思決定journal

最小schemaは次のようにします。

```
{
  "task_id": "t_01HX8Q2M",
  "policy_version": "v1",
  "area_id": "backend",
  "task_type": "bugfix",
  "risk_class": "medium",
  "risk_overlay": "data_compatibility",
  "intended_pattern": "P2",
  "actual_assignment": {
    "planner": "agent_a@cap_v1",
    "writer": "agent_b@cap_v2",
    "reviewer": "agent_c@cap_v1"
  },
  "fallback_reason": "none",
  "reviewer_relation": "cross_provider",
  "routing_sequence": 10,
  "sentinel_counter_key": "backend:bugfix",
  "sentinel": false,
  "review_outcome": "changes_requested",
  "rework_rounds": 1,
  "human_interventions": ["acceptance_clarification"],
  "retries": {"implementation": 1, "verification": 0, "plan_correction": 1},
  "verify": {"overall": "blocked", "passed": 12, "failed": 0, "skipped": 1, "environment_blocked": 1},
  "rate_limit": {"hit": false, "stage": null},
  "usage": {"status": "missing", "missing_reason": "provider_not_exposed"},
  "regression_of": "t_01HX7Z4N"
}
```

人間介入は `permission_approval`、`scope_decision`、`acceptance_clarification`、`environment_recovery`、`safety_stop` などの分類値にします。自由記述の「主な摩擦」は、秘密やprivate pathを混ぜやすいので初期schemaから外しました。usageが取れない場合も推定値で埋めず、欠測理由を残します。

reviewの指摘数はKPIにしません。指摘数を増やすと、些末なコメントを量産するreviewerが有利になるからです。見るのはreview outcome、手戻り、retry、人間介入、rate limit、検証の内訳、escaped defectです。10件程度ではAgent間の統計的優劣を主張せず、「次のassignment policyを変える根拠」を残す意思決定journalとして使います。

なお `rate_limit` を初期schemaに含めているのは、「Claude Proの定額枠で実装反復を回す」というPattern Cの前提自体が、レート制限に頻繁に当たるなら崩れるためです。

## Skillはrule of threeで作る

Skillの二重管理はdriftを生みますが、その対策基盤を初日に作るのも過剰です。同じ手順が3回現れたらSkill化を検討します。

Skill化を決めた場合のv1は、共通の `SKILL.md` を各ツールの読込先へ完全複製し、verifyでbyte一致を確認する最小方式です。targetだけにheaderを足すとbyte一致しないため、編集禁止の表示は同期先ディレクトリのREADMEとverifyのerrorに置き、正本から再同期して差分がないことを検査します。

将来、frontmatterやtool呼出しの仕様が分岐したら、共通本文の周りに薄いwrapperを置きます。plugin配布などで各Skillが物理的に自己完結する必要が出た場合だけ、共通正本からadapterを生成する方式を検討します。最初から複雑な変換器を持たないのがポイントです。

## 3人目のAgentはconformanceで追加する

Gemini CLIやCursorを追加するときも、coreのworkflowは複製しません。まず共通coreを読めるadapter、権限とrisk classの対応、共通verify、handoff入出力、usage欠測の記録をbase conformanceとして確認します。その上でplanner、writer、reviewer、read-only explorerごとのcapability matrixを持ちます。

ツール固有ファイルの鮮度も `verify-change.sh` で検査します。例えばfresh reviewができないAgentはreviewer候補からだけ外し、writer適格性は別に判定します。各roleのconformanceを満たさないAgentはそのroleの候補に入れず、利用枠が余っていてもquality floorを下げません。

## テンプレートリポジトリ

以上の設計は、テンプレートとして公開しています。

<https://github.com/izumuzui/agent-orchestrator-template>

Small Core一式(`AGENTS.md`/`CLAUDE.md`のアダプター、`.ai/`配下の知識・標準・検証・workflow、handoffテンプレート、metricsのschema)に加えて、決定的な処理をスクリプトとして含みます。

* `check-agent-env.sh`:環境と構成の整合性チェック
* `create-handoff.sh`:taskごとのhandoff snapshotの作成
* `reserve-routing.py`:routing予約。counter keyごとの`routing_sequence`をatomicに採番し、sentinel対象なら`review_required`を返す
* `record-completion.py`:完了イベントをJSONLへ追記

使い始めるときの手順はREADMEに記載していますが、大まかには `repository-map.md` を対象リポジトリに合わせて更新し、`security.md` のrepository overlayを埋め、`routing.md` のassignment policyを自分の契約に合わせる、という流れです。README冒頭に明記しているとおり、これは実証済みフレームワークではなく、初期policyを10件のnon-trivial taskで校正するための運用テンプレートです。tool別Skillの同期基盤やproactive loopは、意図的に「Not included yet」としています。

## 限界と反証条件

この設計にも未解決の点があります。

まず、fresh reviewerでも同じ要求の読み違いを共有することがあります。cross-providerで相関が下がるという仮説も未検証です。escaped defect率が変わらないなら、provider分離より要求sourceやテスト戦略を見直すべきです。

次に、Verify-firstは誤った受入条件を強く最適化する危険があります。数値だけで判定できないUXや設計判断には、人の確認や別形式の証拠が必要です。またP2/P3のhandoff費用が実装時間を上回るなら、対象riskを狭めるべきです。

Pattern Cも、Claude側の実装反復がrate limitに頻繁に当たる、Codex review後の手戻りが多い、または逆assignmentの方が人間介入を減らすなら反証されます。その場合もcoreは変えず、policyだけを交換します。

そして `.ai/` を置くだけではトークンは節約されません。毎回全ファイルを読ませる、handoffへ会話logを貼る、Skillを増やし続ける運用になれば逆効果です。repository map、選択的読込み、短いsnapshot、決定的scriptが実際に使われているかを測る必要があります。

## まとめ

Claude CodeとCodexを併用する環境で長持ちさせたいのは、Agentの序列ではなく、役割を交換しても残る境界です。

要求から先にVerifyを作る。静的な知識、薄いadapter、taskごとの状態、永続metricsを混ぜない。shared worktreeはone writerにし、独立reviewが必要な変更はfresh instanceへ渡す。loopには停止条件と上限を持たせる。quotaは品質条件を満たした候補のschedulingにだけ使う。

現時点の結論はここまでです。次は最初の10件を実際に回し、Pattern C、cross-provider review、sentinel間隔が本当に手戻りと人間介入を減らすかを確認します。設計を完成品として守るのではなく、反証できるpolicyとして更新できることが、この環境の一番重要な性質だと考えています。

なお、本設計はGPT-5.6 sol(Codex)とClaude Fable 5の相互レビューを経て合意したもので、記事の編集にもClaudeが関わっています。

## 参考リンク
