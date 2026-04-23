---
id: "2026-03-29-githubを使ったclaude-codeのオーケストレーションツールを作っている-01"
title: "GitHubを使ったClaude Codeのオーケストレーションツールを作っている"
url: "https://qiita.com/getty104/items/6a0c87ba3eeba999e673"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-03-29"
date_collected: "2026-03-30"
summary_by: "auto-rss"
---

## この記事は何

以前、Claude Codeへのタスク依頼やレビュー修正依頼をGitHub上で完結できるようにした「claude-task-worker」というツールについて記事を書きました。

この記事を書いた時点では、GitHub上のラベルをトリガーにしてIssueの実装やPRのレビュー修正を自動化する、というのが主な機能でした。

そこからさらに開発を進め、今ではIssueの作成・更新・トリアージからPRのマージまで、開発ワークフローのほぼ全体をGitHub上でオーケストレーションできるツールになっています。この記事では、現在のclaude-task-workerとclaude-code-marketplaceの全体像と、それを使った開発ワークフローを紹介します。

## claude-task-workerとclaude-code-marketplace

claude-task-workerは、GitHub Issue/PRを定期ポーリングし、特定のラベルを検知するとClaude Code CLIにタスク処理を委譲するCLIツールです。

claude-code-marketplaceは、Claude Codeのプラグインマーケットプレイスです。この中にある`base-tools`プラグインが、Issue管理、PR作成、レビュー対応、トリアージといった実際の処理を担うスキル群を提供しています。

この2つを組み合わせることで、GitHubのラベルをトリガーにClaude Codeのスキルが自動実行される仕組みが構成されます。

```
┌─────────────────────────────────────────────────────┐
│                   GitHub                            │
│  Issue (cc-exec-issue)  ──┐                         │
│  Issue (cc-create-issue) ─┤                         │
│  Issue (cc-update-issue) ─┤    ┌──────────────────┐ │
│  PR (cc-fix-onetime)    ──┼───▶│claude-task-worker│ │
│  PR (cc-fix-repeat)     ──┘    └────────┬─────────┘ │
└─────────────────────────────────────────┼───────────┘
                                          │ invoke
                                          ▼
                               ┌─────────────────────┐
                               │ Claude Code CLI     │
                               │ + base-tools plugin │
                               └─────────────────────┘
```

### ワーカーとスキルの対応

claude-task-workerには以下のワーカーが用意されており、それぞれ対応するbase-toolsのスキルを呼び出します。

| ラベル | ワーカー | 呼び出されるスキル | ポーリング間隔 |
| --- | --- | --- | --- |
| `cc-exec-issue` | exec-issue | `/exec-issue` | 30秒 |
| `cc-create-issue` | create-issue | `/create-issue` | 30秒 |
| `cc-update-issue` | update-issue | `/update-issue` | 30秒 |
| `cc-fix-onetime` | fix-review-point | `/fix-review-point` | 30秒 |
| `cc-fix-repeat` | fix-review-point | `/fix-review-point`（繰り返し） | 30秒 |
| -- | triage-issues | `/triage-issues` | 10分 |
| -- | triage-prs | `/triage-prs` | 10分 |

### 起動モード

通常の運用では`all`または`yolo`コマンドで起動します。

`all`は通常ワーカー4つ（exec-issue, fix-review-point, create-issue, update-issue）を同時にポーリングします。

`yolo`はすべてのワーカー6つ（通常4つ + triage-issues + triage-prs）を同時にポーリングします。triage系のワーカーが追加されることで、IssueやPRのトリアージからマージまでが完全に自動化されます。

`yolo`モードではラベルを自動付与・処理するため、`cc-triage-scope`ラベルが付いているIssue/PRのみが対象になります。スコープ外のIssue/PRには一切手を加えないので、既存の作業が意図せず巻き込まれる心配はありません。

## 開発ワークフロー

ここからは、`yolo`モードを前提とした実際の開発ワークフローを紹介します。`/breakdown-issues`でタスクを洗い出した後は、人間が手を動かすことはありません。あとはすべてclaude-task-workerが自律的に進めてくれます。

### 1. `/breakdown-issues`でタスクの洗い出し（唯一の人間作業）

まず、実装したい機能や対応したい内容をClaude Codeの`/breakdown-issues`スキルに伝えます。

```
> /breakdown-issues ユーザー認証機能を追加したい
```

`/breakdown-issues`の特徴は、タスク間の依存関係を明示しながらIssueを作成することです。「DBスキーマの変更」→「APIの実装」→「フロントエンドの修正」のような依存関係が各Issueのdescriptionに記載され、後続のtriage-issuesがその依存関係を把握した上で着手順序を判断できるようになります。

また、各Issueには初期の実装方針も記載されます。作成されたIssueには`cc-triage-scope`ラベルが自動で付与されるため、そのままtriage-issuesの監視対象となり、後続のワーカーがトリアージ・実装に着手できます。

### 2. `triage-issues`がIssueを自動トリアージ

`claude-task-worker yolo`を起動すると、triage-issuesワーカーが10分ごとに動き始めます。

triage-issuesは以下の処理を自動で行います。

1. 依存関係の解析: `cc-triage-scope`ラベルの付いたIssueを取得し、依存関係グラフを構築する
2. 着手可能なIssueの選定: 依存するIssueがすべて完了しているものだけを対象として選ぶ
3. `cc-create-issue`ラベルの付与: 選定されたIssueにラベルを付与し、create-issueワーカーに移譲する
4. `cc-update-issue`ラベルの付与: 確認が必要な点があればIssueにコメントを残し、update-issueワーカーに移譲してプランをブラッシュアップする
5. `cc-exec-issue`ラベルの付与: プランが固まったIssueに実装開始のラベルを付与し、exec-issueワーカーに引き渡す

この一連の流れがすべて自動で回るため、依存関係の解消に合わせてIssueへの着手が順次行われます。

### 3. `create-issue`が実装プランを作成

`cc-create-issue`ラベルが付いたIssueをcreate-issueワーカーが検知し、`/create-issue`スキルが実行されます。

create-issueはコードベースをExploreサブエージェントで探索し、関連するファイルや設計ドキュメントを読み込んだ上で、以下の構成で実装プランを作成します。

* 概要
* 要件
* 参照すべきファイル・コード
* 具体的な実装プラン
* 影響範囲

作成されたプランはIssueのdescriptionに書き込まれます。不確定な点や確認が必要な事項があれば、Issueにコメントとして残します。

### 4. `update-issue`が実装プランをブラッシュアップ

`cc-update-issue`ラベルが付いたIssueをupdate-issueワーカーが検知し、`/update-issue`スキルが実行されます。

update-issueは既存のIssueを読み込み、コードベースを再探索した上で、実装プランを更新します。triage-issuesがIssueに残したコメントの確認事項への回答や、新たな情報を踏まえたプランの精緻化が行われます。プランが十分に固まるまで、triage-issuesとupdate-issueの間で繰り返しブラッシュアップが行われます。

### 5. `exec-issue`が実装・PRを作成

`cc-exec-issue`ラベルが付いたIssueをexec-issueワーカーが検知し、`/exec-issue`スキルが実行されます。

worktreeを使って独立したブランチで実装が行われるため、複数のIssueが同時に処理されても干渉しません。実装完了後はPRが自動作成され、triage-prsの監視対象になります。

### 6. `triage-prs`がPRを自動マージ

triage-prsワーカーも10分ごとに動いており、`cc-triage-scope`ラベルの付いたPRを対象に以下の判断を自動で行います。

1. CIの結果を確認: CIが完了しているPRのみを対象として処理する
2. レビューコメントの確認: 未解決のレビューコメントが残っているかを確認する
3. 修正 or マージの判断:
   * 修正が必要と判断した場合 → `cc-fix-onetime`ラベルを付与し、fix-review-pointワーカーに引き渡す
   * 修正不要と判断した場合 → そのままマージする
4. コンフリクトの解消: コンフリクトが発生している場合はfix-review-pointワーカーに引き渡す

人間がレビューコメントを残した場合も、triage-prsが自動検知して修正→マージまで進めます。

### 7. `fix-review-point`がレビュー対応・コンフリクト解消

`cc-fix-onetime`または`cc-fix-repeat`ラベルが付いたPRをfix-review-pointワーカーが検知し、`/fix-review-point`スキルが実行されます。

fix-review-pointは以下の流れで修正を行います。

1. PRのブランチをチェックアウトし、未解決のレビューコメントとCIの状態を確認する
2. `/create-review-fix-plan`スキルで修正プランを作成する
3. 各修正タスクをサブエージェントに委譲し、可能な限り並列で実行する
4. テストとLintを実行して品質を確認する
5. 変更をコミット・プッシュし、PRのレビュースレッドを一括Resolveする

`cc-fix-onetime`ラベルの場合は1回だけ修正を実行し、`cc-fix-repeat`ラベルの場合はCIが通るまで繰り返し修正を実行します。修正完了後はtriage-prsの監視対象に戻り、再度マージ判定が行われます。

### ワークフロー全体の流れ

例えば`/breakdown-issues`で5つのIssueが作られると、すべてに`cc-triage-scope`ラベルが自動で付与されるため、あとは依存関係にそって自動で並列にタスクが進んでいきます。

## デイリーの平均コントリビューション数が100を超えた

この仕組みを本格的に運用し始めてから、デイリーの平均コントリビューション数が100を超えるようになりました。

以前のワークフローでは、GitHub上で各タスクに行う処理を人が指定する必要があったため、並列度に限界がありました。claude-task-workerのyoloモードによってタスクの投入からマージまでAIで完結するようになったことで、「人間がGitHub上で実行する処理を選んでいく」ボトルネックがなくなり、タスクの処理が大幅にスケールするようになりました。

[![スクリーンショット 2026-03-29 22.34.38.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F158501%2Fd57b3cca-1664-4826-a901-7a516a93d3cc.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=bac2cbbad50cfa2fb5323533ca108afd)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F158501%2Fd57b3cca-1664-4826-a901-7a516a93d3cc.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=bac2cbbad50cfa2fb5323533ca108afd)

## 今後の課題

細かいPRレベルでの品質担保（CIの通過、レビューコメントへの対応）は自動化できるようになりました。一方で、複数のPRをマージした後に作られた機能全体のQAがボトルネックになっています。

個々のPRは問題なく通っても、機能として組み合わさったときに意図しない挙動が出ることがあります。ここをどのように自動化・効率化していくかが、次に取り組んでいく課題です。

## 最後に

claude-task-workerとclaude-code-marketplaceを組み合わせることで、Claude Codeを使った開発ワークフローをGitHub上で完結させることができます。`yolo`モードであれば、`/breakdown-issues`でタスクを定義した後は、人間がやることは何もありません。

興味がある方はぜひ試してみてください。
