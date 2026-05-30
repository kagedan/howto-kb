---
id: "2026-05-29-claude-code-dynamic-workflows-入門公式情報から整理する仕組みと注意点-01"
title: "Claude Code Dynamic Workflows 入門：公式情報から整理する仕組みと注意点"
url: "https://zenn.dev/arufian/articles/c1389f2941de90"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "JavaScript"]
date_published: "2026-05-29"
date_collected: "2026-05-30"
summary_by: "auto-rss"
query: ""
---

## はじめに

2026年5月28日、AnthropicはClaude Codeに **Dynamic Workflows** を導入しました。公式ブログでは、Claudeがオーケストレーションスクリプトを動的に書き、1つのセッション内で数十から数百のサブエージェントを並列実行し、結果をユーザーに返す前に検証すると説明されています。

出典：[Introducing dynamic workflows in Claude Code](https://claude.com/blog/introducing-dynamic-workflows-in-claude-code)

この記事では、Anthropicの公式ブログとClaude Code公式ドキュメントで確認できる範囲に絞って、Dynamic Workflowsの仕組み、起動方法、実行管理、権限、コスト、利用可能環境を整理します。

Dynamic Workflowsは、通常のサブエージェント利用を大規模・長時間実行向けに拡張する仕組みです。コードベース全体の調査、大規模移行、複数視点からの計画レビューなど、1つの会話だけでは扱いにくい作業を対象にしています。

なお、この記事では公式ブログとDynamic Workflowsドキュメントで確認できないプラン対応、バージョン番号、未公開の内部挙動は扱いません。

---

## Dynamic Workflowsとは

Dynamic Workflowsは、Claudeが書いたJavaScriptスクリプトをランタイムが実行し、そのスクリプトが多数のサブエージェントを調整する仕組みです。公式ドキュメントでは、Subagents / Skills / Workflowsの違いを「誰が計画を保持するか」で整理しています。

出典：[Orchestrate subagents at scale with dynamic workflows](https://code.claude.com/docs/en/workflows)

|  | Subagents | Skills | Workflows |
| --- | --- | --- | --- |
| 正体 | Claudeが生成するワーカー | Claudeが従う指示 | ランタイムが実行するスクリプト |
| 次の実行を決めるもの | Claude | Claude | スクリプト |
| 中間結果の保存場所 | Claudeのコンテキスト | Claudeのコンテキスト | スクリプト変数 |
| 再利用できるもの | ワーカー定義 | 指示 | オーケストレーション |
| スケール | 1ターンあたり数件の委任 | Subagentsと同程度 | 1実行あたり数十から数百エージェント |
| 中断時 | ターンを再実行 | ターンを再実行 | 同一セッション内で再開可能 |

ポイントは、計画が会話の外にあるスクリプトへ移ることです。これにより、ループ、分岐、中間結果をスクリプト側で扱い、Claudeの会話コンテキストには最終結果だけを戻しやすくなります。

---

## 使いどころ

公式ブログとドキュメントでは、次のような用途が挙げられています。

出典：[公式ブログ](https://claude.com/blog/introducing-dynamic-workflows-in-claude-code)、[公式ドキュメント](https://code.claude.com/docs/en/workflows)

![公式ブログに掲載されているDynamic Workflowsの実行画面](https://res.cloudinary.com/zenn/image/fetch/s--gIC556fO--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://cdn.prod.website-files.com/68a44d4040f98a4adf2207b6/6a186b2e070156fbb2df90ad_166befe7.png?_a=BACMTiGT)

* コードベース全体のバグ調査、プロファイラに基づく最適化監査、セキュリティ監査
* 数百から数千ファイルにまたがるフレームワーク移行、API非推奨対応、言語ポート
* 高い正確性が必要な計画や調査を、複数の独立した角度から検証する作業

特に重要なのは、単に多くのエージェントを並べるだけではない点です。Dynamic Workflowsでは、あるエージェントの発見を別のエージェントが検証したり、複数案を作って互いに弱点を探したりする構成を取りやすくなります。

---

## 実行の流れ

Dynamic Workflowsの基本的な流れは次のように整理できます。

```
ユーザーの依頼
  ↓
Claudeがワークフローを計画
  ↓
JavaScriptスクリプトを生成
  ↓
ランタイムがバックグラウンドで実行
  ↓
複数サブエージェントが並列作業
  ↓
結果を検証・統合
  ↓
単一の回答としてユーザーへ返す
```

公式ドキュメントによると、ワークフローはClaude Codeの会話とは別の隔離された環境で実行され、中間結果はスクリプト変数に保持されます。進行状況も追跡されるため、同一セッション内なら一時停止後に再開できます。

出典：[How a workflow runs](https://code.claude.com/docs/en/workflows#how-a-workflow-runs)

---

## 制約

公式ドキュメントに記載されている主な制約は次の通りです。

出典：[Behavior and limits](https://code.claude.com/docs/en/workflows#behavior-and-limits)

| 制約 | 理由 |
| --- | --- |
| 実行中のユーザー入力は不可 | 承認が必要な段階は別ワークフローに分ける |
| ワークフロー自体はファイルシステムやシェルに直接アクセスしない | 読み書きやコマンド実行はエージェントが担当する |
| 同時実行は最大16エージェント | ローカルリソース使用量を抑える |
| 1実行あたり合計1,000エージェント | 暴走ループを防ぐ |

「最大16並列」「1,000エージェント」は公式ドキュメント上の制限です。ただし、実際の同時実行数はマシンのCPUコア数などにより減る可能性があります。

---

## 起動方法

Dynamic Workflowsを開始する方法は主に3つあります。

出典：[Have Claude write a workflow](https://code.claude.com/docs/en/workflows#have-claude-write-a-workflow)

### 1. プロンプトに`workflow`を含める

単発のタスクをワークフローとして実行したい場合は、プロンプトに`workflow`という単語を入れます。

```
Run a workflow to audit every API endpoint under src/routes/ for missing auth checks
```

Claude Codeは入力中の`workflow`をハイライトし、通常のターン単位の作業ではなくワークフロースクリプトを書き始めます。下の例のように、Claude Code上では`workflow`という単語がDynamic Workflowのトリガーとして自動タグ付けされ、虹色のテキストで表示されます。意図せずトリガーされた場合は、`Alt+W`（macOSでは`Option+W`）でそのプロンプトでは無視できます。

出典：[Ask for a workflow in your prompt](https://code.claude.com/docs/en/workflows#ask-for-a-workflow-in-your-prompt)  
![Claude Codeでworkflowという単語がDynamic Workflowとして虹色にハイライトされる例](https://static.zenn.studio/user-upload/bf0bed914693-20260529.gif)

### 2. `ultracode`を使う

`ultracode`は、`xhigh`推論努力と自動ワークフローオーケストレーションを組み合わせるClaude Code向け設定です。

有効にすると、Claudeは実質的なタスクごとにワークフローを使うか判断します。1つの依頼が、コード理解、変更、検証といった複数のワークフローに分かれることもあります。

`ultracode`は現在のセッションでのみ有効です。通常作業へ戻す場合は`/effort high`に切り替えます。

### 3. 組み込みワークフロー`/deep-research`

Claude Codeには、調査用の組み込みワークフローとして`/deep-research`があります。

```
/deep-research What changed in the Node.js permission model between v20 and v22?
```

公式ドキュメントでは、複数角度からWeb検索を行い、ソースを取得・クロスチェックし、検証を通過した主張を引用付きレポートとして返すワークフローと説明されています。

---

## 実行の監視と保存

ワークフローはバックグラウンドで動作します。実行中・完了済みのワークフローは、いつでも`/workflows`から確認できます。

出典：[Watch the run](https://code.claude.com/docs/en/workflows#watch-the-run)

進行画面では、各フェーズのエージェント数、トークン合計、経過時間を確認できます。

| キー | 操作 |
| --- | --- |
| `↑` / `↓` | フェーズまたはエージェントを選択 |
| `Enter` / `→` | フェーズやエージェントの詳細へ移動 |
| `Esc` | 1階層戻る |
| `j` / `k` | エージェント詳細をスクロール |
| `p` | 一時停止または再開 |
| `x` | 選択中のエージェント、またはワークフロー全体を停止 |
| `r` | 実行中エージェントを再起動 |
| `s` | 実行スクリプトをコマンドとして保存 |

繰り返し使うワークフローは、`/workflows`で対象を選び、`s`キーで保存できます。保存先は次の2つです。

出典：[Save the workflow for reuse](https://code.claude.com/docs/en/workflows#save-the-workflow-for-reuse)

* `.claude/workflows/`：プロジェクト内に保存し、リポジトリ利用者と共有
* `~/.claude/workflows/`：ホームディレクトリに保存し、自分だけが全プロジェクトで利用

保存したワークフローは、以後`/<name>`のコマンドとして実行できます。

---

## 承認と権限

ワークフロー開始時には、CLIで実行計画の確認プロンプトが表示されます。表示されるタイミングは権限モードによって変わります。

出典：[Approve the plan before it runs](https://code.claude.com/docs/en/workflows#approve-the-plan-before-it-runs)

| 権限モード | 承認プロンプト |
| --- | --- |
| Default / accept edits | 毎回表示。ただし「今後このプロジェクトでこのワークフローについて聞かない」を選ぶと以後スキップ |
| Auto | 初回のみ。`ultracode`有効時はスキップ |
| Bypass permissions / `claude -p` / Agent SDK | 表示なし |

重要な点として、権限モードが制御するのはワークフロー起動時のプロンプトです。ワークフローが生成するサブエージェントは常に`acceptEdits`モードで実行され、ツール許可リストを継承します。ファイル編集は自動承認されます。

ただし、許可リストにないシェルコマンド、Web fetch、MCPツールは実行中にプロンプトを出す可能性があります。長時間のワークフローでは、必要なコマンドを事前に許可リストへ入れておく方が安全です。

---

## コストと停止

Dynamic Workflowsは多数のエージェントを起動するため、通常のClaude Codeセッションより多くのトークンを消費します。公式ブログとドキュメントはいずれも、小さくスコープを切ったタスクから試すことを勧めています。

出典：[公式ブログ](https://claude.com/blog/introducing-dynamic-workflows-in-claude-code)、[Cost](https://code.claude.com/docs/en/workflows#cost)

コスト管理の実践例です。

* 大きな実行前に`/model`でモデルを確認する
* 強いモデルが不要な段階では、小さいモデルを使うよう依頼する
* 実行中のワークフローは`/workflows`から停止する
* 完了済み作業は失わずに停止できるため、想定外に大きくなったら早めに止める

ワークフローを無効化する方法も用意されています。

出典：[Turn workflows off](https://code.claude.com/docs/en/workflows#turn-workflows-off)

* `/config`でDynamic workflowsをオフにする
* `~/.claude/settings.json`に`"disableWorkflows": true`を設定する
* `CLAUDE_CODE_DISABLE_WORKFLOWS=1`を設定する
* 組織単位ではmanaged settingsまたはClaude Code admin settingsで無効化する

無効化すると、組み込みワークフローコマンド、`workflow`キーワードによる起動、`ultracode`が使えなくなります。

---

## 利用可能な環境

公式ブログでは、Dynamic Workflowsはresearch previewとして、Claude Code CLI、Desktop、VS Code extensionで利用可能と説明されています。対象プランはMax、Team、Enterpriseです。ただしEnterpriseは管理者が有効化した場合に利用できます。

また、Claude API、Amazon Bedrock、Vertex AI、Microsoft Foundryでも利用可能とされています。

出典：[公式ブログ](https://claude.com/blog/introducing-dynamic-workflows-in-claude-code)

公式ドキュメントでは、MaxまたはTeam、あるいはClaude Code via APIではデフォルトで有効、Enterpriseではローンチ時点でデフォルト無効と説明されています。

出典：[Getting started](https://code.claude.com/docs/en/workflows#getting-started)

| 区分 | 状態 |
| --- | --- |
| Max | デフォルト有効 |
| Team | デフォルト有効 |
| Claude Code via API | デフォルト有効 |
| Enterprise | デフォルト無効。管理者が有効化可能 |

この記事では、公式ブログとDynamic Workflowsドキュメントで確認できないProプランや特定バージョン番号は扱いません。

---

## Bun書き直しの事例

公式ブログでは、大規模事例としてBunのZigからRustへの移植が紹介されています。

出典：[Rewriting Bun with dynamic workflows](https://claude.com/blog/introducing-dynamic-workflows-in-claude-code)

Jarred Sumner氏がDynamic Workflowsを使い、BunをZigからRustへ移植した事例として、次の数字が示されています。

| 項目 | 内容 |
| --- | --- |
| 対象 | BunのZigからRustへの移植 |
| テスト | 既存テストスイートの99.8%がパス |
| コード量 | 約750,000行のRust |
| 期間 | 最初のコミットからマージまで11日 |

ワークフローの内容として、構造体フィールドごとのRustライフタイムのマッピング、`.zig`ファイルに対応する`.rs`ファイルの作成、各ファイルへの2人のレビューア、ビルドとテストが通るまでの修正ループ、不要なデータコピーを修正するPR作成が説明されています。

なお、公式ブログはこの移植について「まだ本番環境には入っていない」とも明記しています。この点は、事例を読む上で重要です。

---

## 実践パターン

### コードベース全体のセキュリティ監査

```
Run a workflow to scan the entire codebase for:
- Missing auth checks on API endpoints
- SQL injection vulnerabilities
- Unsafe deserialization patterns
- Hardcoded secrets
Have independent agents verify each finding.
```

この用途では、サービス全体を並列に探索し、見つかった指摘を別エージェントで検証する構成が考えられます。誤検出をゼロにできるわけではありませんが、単一パスよりレビューを厚くできます。

### 大規模移行

```
Create a workflow to migrate all React class components to functional components with hooks.
Cover all files under src/components/.
Run tests after each batch to verify behavior preservation.
```

大量ファイルにまたがる移行では、対象ファイルごとの作業と検証を分け、段階的に統合する流れに向いています。

### 計画のストレステスト

```
Create a workflow to draft our microservices migration plan from three independent angles,
then have adversarial agents try to find flaws in each approach.
Synthesize the most robust plan.
```

複数案を作り、それぞれの弱点を別エージェントに探させることで、計画の抜けや前提崩れを見つけやすくなります。

---

## 注意点

Dynamic Workflowsは便利ですが、通常のClaude Code作業より重い実行方式です。特に次の点には注意が必要です。

* トークン消費が大きくなりやすい
* 長時間実行では途中で権限プロンプトが出る可能性がある
* ワークフローは同一セッション内では再開できるが、Claude Codeを終了すると次回は新規実行になる
* サブエージェントのファイル編集は自動承認されるため、許可リストと実行範囲を事前に確認する必要がある
* 公式情報にないコマンド、制限、プラン対応は記事に書かない方がよい

まずは小さなコード調査や`/deep-research`から試し、トークン消費、実行時間、権限プロンプトの出方を把握してから大規模タスクに使うのが現実的です。

---

## まとめ

Dynamic Workflowsは、Claude Codeで大規模な並列作業を扱うための新しい実行方式です。Claudeがワークフロー用スクリプトを書き、ランタイムがそのスクリプトをバックグラウンドで実行し、多数のサブエージェントを調整します。

重要な点は次の通りです。

* 計画がスクリプト化され、中間結果は会話コンテキストではなくスクリプト側に保持される
* 数十から数百のサブエージェントを使う作業に向く
* 検証用エージェントや敵対的レビューを組み込みやすい
* 同一セッション内なら一時停止後に再開できる
* トークン消費と権限管理には注意が必要

小さく試して、うまくいったワークフローを保存し、繰り返し使う作業に広げるのがよい使い始め方です。

---

## 参考リンク
