---
id: "2026-05-25-hermes-kanban-swarm入門aiエージェントを並列実行検証統合する-01"
title: "Hermes Kanban Swarm入門：AIエージェントを並列実行・検証・統合する"
url: "https://zenn.dev/zennai_ryutaro/articles/20260525-hermes-kanban-swarm-usage"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "zenn"]
date_published: "2026-05-25"
date_collected: "2026-05-26"
summary_by: "auto-rss"
query: ""
---

この記事を読むと、Hermes Kanban Swarmで複数のAIエージェントに調査・検証・統合を分担させる基本設計とCLI実行例が分かります。

Hermes Agentには `delegate_task` という手軽なサブエージェント呼び出しがあります。短い調査やレビューなら、それで十分です。

ただ、仕事が少し大きくなると困ります。

* 調査を3方向に分けたい
* 実装、レビュー、記事化を別の役割に渡したい
* 途中で止まっても再開できるようにしたい
* 人間が途中でコメントして軌道修正したい
* 誰が何を見て、何を完了したのかをあとで追いたい

こういうときに使うのが、HermesのKanbanです。さらに、その上に「並列worker → verifier → synthesizer」という定型の作業グラフを作るのが `hermes kanban swarm` です。

この記事では、HermesのKanban Swarmを「何に使うのか」「どう作るのか」「運用でどこに気をつけるのか」まで、手元で試せる形でまとめます。

## Kanban Swarmはどんなタスクグラフを作るのか

`hermes kanban swarm` は、既存のKanban DBに次のようなタスクグラフを作ります。

```
planning root (done)
  ├─ worker A
  ├─ worker B
  └─ worker C

all workers done
  ↓
verifier
  ↓
synthesizer
```

実際の依存関係としては、rootカードはすぐ完了扱いになり、各workerが並列に `ready` になります。workerがすべて終わるとverifierが動けるようになり、verifierが通したあとにsynthesizerが最後の成果物をまとめます。

記事執筆時点では、Swarmは新しいスケジューラというより、既存のKanban kernelに小さなタスクグラフを書き込むヘルパーに近い位置づけです。共有ブラックボードも特別なサービスではなく、rootタスクへの構造化JSONコメントです。既存のタスク、コメント、イベント、ダッシュボード、dispatcherに乗せられるので、導入時に覚えることが少ないのが利点です。

## `delegate_task` と何が違うのか

ざっくり言うと、`delegate_task` は関数呼び出し、Kanban Swarmは仕事の流れです。

| 観点 | delegate\_task | Kanban Swarm |
| --- | --- | --- |
| 親の挙動 | 子タスクの完了を待つ | 作業キューに流して進める |
| 子の扱い | 匿名に近いサブエージェント | profile名を持つworker |
| 永続性 | 親セッション依存 | SQLiteに残る |
| 再開 | 弱い | block / unblock / promote / reclaim などを使える |
| 人間の介入 | しにくい | コメントやunblockで入れる |
| 監査 | 会話圧縮で失われやすい | タスク、コメント、イベントとして残る |

短い調査なら `delegate_task` のほうが速いです。Swarmは少し重い。そのかわり、長い作業、複数人・複数AIの引き継ぎ、あとからの検証に向きやすいです。

## 試す前に確認すること

この記事のコマンドを試す前に、最低限これだけ確認します。

```
hermes --version
hermes kanban init
hermes gateway status
hermes kanban assignees
hermes profile list
hermes skills list
```

`hermes kanban init` はKanban DBの初期化です。`hermes kanban assignees` や `hermes profile list` に出てこないprofile名は、workerやverifierに指定しても動きません。最初は既存のprofile名を使って、小さい検証用Swarmから始めるのが安全です。

## まずhelpを見る

手元のHermesで次を実行します。

```
hermes kanban swarm --help
```

主な引数はこのあたりです。この記事のCLI例は、人間やcronがSwarmを作るためのものです。dispatcherで起動されたworkerは、通常 `hermes kanban` CLIを叩くのではなく、`kanban_*` tool callsでboardを読み書きします。

```
hermes kanban swarm \
  [--worker PROFILE:TITLE[:SKILL,SKILL]] \
  --verifier VERIFIER \
  --synthesizer SYNTHESIZER \
  [--tenant TENANT] \
  [--priority PRIORITY] \
  [--created-by CREATED_BY] \
  [--idempotency-key IDEMPOTENCY_KEY] \
  [--json] \
  goal
```

最低限必要なのは、goal、1つ以上のworker、verifier、synthesizerです。

## 最小構成で試す

いきなり複数profileやskillを分ける前に、まずは手元に存在するprofile名へ置き換えた最小例で試すのが楽です。以下では `default` というprofileがある前提で書いています。なければ、自分の環境にあるprofile名へ置き換えてください。

```
hermes kanban swarm "テスト用に2つの観点で調査してまとめる" \
  --worker 'default:観点Aを調べて要点を残す' \
  --worker 'default:観点Bを調べて要点を残す' \
  --verifier default \
  --synthesizer default \
  --created-by test \
  --tenant sandbox \
  --idempotency-key swarm-test-001 \
  --json
```

`--tenant sandbox` は検証用の名前空間です。必須ではありませんが、定期運用や複数案件を扱う場合は、後から絞り込みやすくなります。

`--json` を付けると、概ね次のようなIDが返ります。実際のIDは環境ごとに変わります。

```
{
  "root_id": "task_...",
  "worker_ids": ["task_...", "task_..."],
  "verifier_id": "task_...",
  "synthesizer_id": "task_..."
}
```

この `root_id` や `worker_ids` を使って、あとから状態を追います。

## 例1: 調査記事をSwarmで作る

たとえば、Hermes Agentの週次キャッチアップ記事を作るなら、こんな分け方ができます。

```
hermes kanban swarm "Hermes Agentの今週の変更を調査してZenn記事の下書きを作る" \
  --worker 'researcher:公式GitHubとDocsの変更点と根拠URLを残す' \
  --worker 'researcher:周辺OSSとプラグイン候補を調べる' \
  --worker 'editor:読者に刺さる記事構成を考える' \
  --verifier reviewer \
  --synthesizer writer \
  --created-by author \
  --idempotency-key hermes-weekly-zenn-20260525 \
  --json
```

`--worker` は繰り返し指定できます。引数全体はquoteしておくと安全です。`TITLE` に半角コロン `:` を入れると区切りとして解釈されるので、タイトル内では避けます。形式は次の通りです。

```
PROFILE:TITLE[:SKILL,SKILL]
```

* `PROFILE`: そのタスクを担当するHermes profile名
* `TITLE`: Kanban上のタスク名。workerの本文にも使われます
* `SKILL,SKILL`: そのworkerに持たせるskill名。省略できます

ここで使っているprofile名やskill名は、筆者環境の例です。手元では `hermes profile list` や `hermes skills list` で存在を確認し、自分のprofile名に置き換えてください。

`--idempotency-key` はかなり大事です。cronやスクリプトから同じSwarm作成を再実行したときに、同じrootを重複作成しにくくなります。週次記事や定期運用では入れておくほうが安全です。既存の非archived rootがある場合はそれを再利用するため、別用途で同じkeyを使い回さないようにします。

## 例2: 実装タスクを分解する

アプリ実装でも使えます。

```
hermes kanban swarm "顧客問い合わせフォームを実装してPRを作る" \
  --worker 'backend:APIとDB保存処理を実装する' \
  --worker 'frontend:フォームUIとバリデーションを実装する' \
  --worker 'qa:受入条件とテスト観点を整理する' \
  --verifier reviewer \
  --synthesizer integrator \
  --created-by pm \
  --priority 10 \
  --json
```

この形だと、backendとfrontendが先に動き、qaも並列で観点を出せます。全workerが終わったあと、reviewerが成果を見て、integratorがPRとしてまとめる流れです。

ただし、実装系で使うならworkspace設計が重要です。Kanbanには `scratch`、`dir:<path>`、`worktree` などのworkspace概念があります。一方で、現状の `hermes kanban swarm` CLIは `--workspace` を直接露出していません。成果物を確実に残したいコード変更では、通常のKanbanタスクで `worktree` / `dir:<absolute path>` を使うか、Swarm作成側のworkspace指定に対応しているかを確認してください。最初は記事や調査メモのように、最終出力がコメントやsummaryに残る用途から試すのが安全です。

## Kanban Swarmの作成結果を確認する

`--json` を付けると、root、workers、verifier、synthesizerのIDが返ります。IDが取れたら、Kanbanの通常コマンドで追えます。

```
hermes kanban show <root_id>
hermes kanban show <worker_id>
hermes kanban list --status ready
```

worker側は、本文にSwarm protocolが追記されます。そこにはrootの共有ブラックボード、兄弟・親タスクのhandoffを読むこと、完了メタデータに機械可読な事実を置くこと、rootへ構造化コメントを残すことが書かれます。

つまり、Swarmは「作って終わり」ではありません。各workerがKanbanのコメントや完了メタデータを使って、あとからverifierとsynthesizerが読める形で情報を残すのが前提です。

## dispatcherが動いているか確認する

Swarmはタスクグラフを作るだけです。実際にworkerを起動するのはKanban dispatcherです。

Hermesの設定では、dispatcherはgateway内で動く構成が基本です。もしタスクが `ready` のまま進まない場合は、次を確認します。

```
hermes gateway status
hermes kanban assignees
hermes kanban list --status ready
hermes kanban list --status blocked
hermes kanban diagnostics
```

profile名の間違い、workspaceの問題、連続spawn失敗などがあると、設定されたfailure limit到達後にdispatcherがタスクをauto-blockすることがあります。止まったら、まず `hermes kanban show <task_id>` でコメントとイベントを見ます。profile名のミスなら正しいprofile名で作り直すのが早いです。検証用Swarmを片付けたい場合は、不要なtask idを確認してから `hermes kanban archive <task_id>` でarchiveできます。

## verifierでAIエージェント出力を検証する

Swarmで一番効くのはverifierです。

並列workerは速いですが、出力の粒度が揃わないことがあります。調査タスクなら、URLだけ貼るworkerもいれば、推測を書いてしまうworkerもいます。実装タスクなら、片方のworkerが前提を壊すこともあります。

verifierは、全workerのhandoffとblackboard更新を読みます。十分な証拠がある場合にだけタスクをcompleteし、そのときのメタデータ慣例として `{"gate": "pass"}` のような情報を残します。不足があれば具体的にblockします。

これを挟むことで、「並列で速くしたけど最後に雑に混ぜた」という事故を減らしやすくなります。

## synthesizerは最後の編集者

synthesizerは、verifiedな出力だけを使って最終成果物を作るよう指示される役です。

記事なら本文化、実装ならPR統合、調査なら意思決定メモ化、営業なら提案書化。ここで大事なのは、synthesizerに全部を再調査させないことです。workerとverifierが残した材料を使い、足りないところだけ明示します。

私の運用では、synthesizerには次を必ず求めたいです。

* 何を採用したか
* 何を捨てたか
* どの情報が未確認か
* 人間が見るべき判断点は何か
* 次に動くならどのタスクか

Swarmは魔法の全自動ではありません。最後のまとめ方を雑にすると、ただの並列メモ製造機になります。

## どういう場面で使うか

記事、開発、調査、運用改善が同時に走るチームでは、Swarmと相性がよいです。

たとえば次のような仕事に向いています。

* AIツールの週次キャッチアップ記事
* OSS比較と採用判断
* 顧客向けPoCの要件整理、実装、レビュー
* 既存アプリの品質改善スプリント
* 営業資料の調査、構成、レビュー、清書
* 複数SNS向けの素材分解と最終統合

逆に、10分で終わる単発質問には向きません。Swarmを作るだけで少し重いので、短い仕事まで全部Swarm化すると運用が散らかります。

私ならこう使い分けます。

```
短い調査・その場のレビュー: delegate_task
数時間〜数日の作業・人間レビューあり: Kanban
並列調査 + 検証 + 統合が必要: Kanban Swarm
定期実行: cron + idempotency-key付きSwarm
```

## 運用で気をつけること

### profile名は先に整える

`--worker`、`--verifier`、`--synthesizer` にはprofile名を渡します。存在しないprofileを指定するとworker起動で詰まります。

最初は少数のprofileで試すほうがいいです。

```
researcher
reviewer
writer
integrator
pm
```

名前を増やすのは簡単ですが、役割が曖昧なprofileを増やすと、あとで誰が何を担当するのか分からなくなります。

### `--idempotency-key` を使う

cronやCIからSwarmを作るなら、同じ作業が重複しないようにkeyを入れます。

```
--idempotency-key hermes-weekly-zenn-20260525
```

日次・週次なら日付を含める。固定の運用なら案件IDやissue番号を含める。ここを雑にすると、同じSwarmが何個もできて、後から整理が難しくなります。

### workerに期待する出力を具体化する

`TITLE` だけでworkerに投げると、出力が浅くなりがちです。現状のCLI形式ではworker本文もtitleベースなので、タイトルに成果物を含めると安定します。

悪い例:

```
--worker 'researcher:調べる'
```

良い例:

```
--worker 'researcher:公式DocsとGitHub Releasesを確認し、変更点・根拠URL・未確認点を箇条書きで残す'
```

長すぎるtitleは読みづらいですが、「何を残すか」までは入れたほうがよいです。

### 何でもSwarmにしない

Swarmは「チーム作業」に向いています。小さい作業をSwarmにすると、管理コストのほうが高くなります。

迷ったら、まずこう判断します。

* 1つの答えがほしいだけなら `delegate_task`
* 状態を残したいならKanban
* 並列に分けて、最後に検証と統合が必要ならSwarm

## コピペ用チートシート

```
使い分け:
- 単発調査: delegate_task
- 状態管理あり: Kanban
- 並列調査 + 検証 + 統合: Kanban Swarm

最小構成:
- worker 2〜3個
- verifier 1個
- synthesizer 1個
- idempotency-key を付ける

最初に見るもの:
- hermes kanban assignees
- hermes kanban show <task_id>
- hermes kanban diagnostics
```

## まとめ

HermesのKanban Swarmは、AIエージェントを増やすための派手な演出ではありません。仕事を分け、残し、検証し、統合するための地味な仕組みです。

派手ではないぶん、実運用に乗せやすいのが良いところです。

AIエージェント運用で本当に困るのは、「賢いかどうか」より「途中経過が残らない」「誰が何を見たか分からない」「最後に雑に混ざる」ことだったりします。Swarmはその課題に対する一つの選択肢になります。

まずは記事作成や調査のような低リスクな仕事で試すのがおすすめです。`hermes kanban swarm` は実際にKanban DBへタスクを作るので、最初は検証用のprofileやtenantで動かすと安心です。workerを2つだけ作り、この記事のCLI例を自分のprofile名に置き換えて試してみてください。うまく回ったら、週次調査、記事作成、開発レビュー、営業資料づくりへ広げていくのがよいと思います。

AIを1人の万能アシスタントとして使う段階から、役割を持った小さなチームとして運用する段階へ。HermesのSwarmは、その移行にちょうどいい足場になります。

## 参考リンク
