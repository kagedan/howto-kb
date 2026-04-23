---
id: "2026-03-24-claude-codeを3層に分けたらgithub-issueが勝手に実装されるようになった-bee-01"
title: "Claude Codeを3層に分けたら、GitHub Issueが勝手に実装されるようになった — beeops設計の全記録"
url: "https://zenn.dev/whale_ai/articles/beeops-construction"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-03-24"
date_collected: "2026-03-25"
summary_by: "auto-rss"
---

GitHub Issueを立てる。しばらくすると、PRが上がっている。サブタスク分解、並列実装、コードレビュー、CI確認まで終わっている。

[beeops](https://github.com/YuugouOhno/beeops) はそれをやるnpmパッケージだ。Claude Codeのセッションをtmuxで3層に並べて、Issue単位で自律的に動かす。

```
npm install beeops
npx beeops init
# Claude Code で /bo を実行するだけ
```

この記事では設計の「なぜ」と「どう使うか」を一緒に書く。壊しながら到達した設計判断の記録と、実際の使い方をセットで理解できるようにした。

## 出発点：チームで積み上げる場所がなかった

世の中にあるエージェントシステムを試した。よくできていた。でも、1人で使う前提の設計だった。

やりたかったのはそこじゃない。GitHub Issuesを起点にして、チームのみんながそこに積み上げていって、裏でAIがそれをこなしていく——そういう仕組みが欲しかった。

既存のツールはそこに合わなかったので、自分で作ることにした。Issueが流れ込む入口を作り、それを処理するエージェント層を組む。それがbeeopsになった。

設計の過程で「1エージェントに全部載せると壊れる」という問題に直面した。タスク管理とコード実装とレビューを1セッションでやると、コンテキストウィンドウの中で全部が混ざる。Claude Codeのコンテキストは有限で、古い情報から圧縮される。

分割を試みた。1エージェント → 2ロール → 3ロール と増やすたびに、「責務をどこで切るか」という問題に直面した。

並列Issue処理を実現するためにLeaderを挟み、実装と無関係にレビューするためにReview Leaderを独立させた。これがbeeopsの3層構造になった。

## なぜ3層なのか

2層（Queen + Worker）を最初に試した。ダメだった。

Queenが「サブタスク分解」と「全体のIssue管理」を同時にやると、1エージェント設計で見た問題が名前を変えて再発する。Queenのコンテキストに1つのIssueの実装詳細が入り込み、並列Issue管理の精度が落ちる。

Leaderを挟んだ。各Leaderは自分のIssueだけに閉じてWorkerを管理する。Queenは「どのIssueをいつ始めるか」だけ考えればいい。

各ロールの責務はこう分けている:

* **Queenはコードを書かない**。queue.yamlの管理と起動指示だけ。コードを書こうとしたら即エラーになるよう指示書に書いてある
* **Leaderはgoal判定役**。「このIssueを達成できたか」を判断するのがLeaderの仕事で、実行はWorkerに任せる
* **Workerは実行専門**。与えられたサブタスクだけを見る。Issue全体の文脈は持たない
* **Review Leaderは独立**。実装に関わっていないので、フラットに評価できる

**Leaderの単位はIssue**。これが3層にした最大の理由だ。

## Issue単位のgit worktree隔離

LeaderはIssueごとにgit worktreeを作る。ブランチもワーキングディレクトリも完全に分離される。

```
# launch-leader.sh より
WORKTREE_PATH="$WORKTREES_DIR/$BRANCH"
git -C "$REPO_DIR" worktree add "$WORKTREE_PATH" -b "$BRANCH" main
```

Workerはこのworktreeの中だけで作業する。Issue #42のWorkerがファイルを変更しても、Issue #57のWorkerに影響しない。並列Issueが実行できる根拠はここにある。

```
# Issue #42 と #43 が並列作業しても干渉しない
.beeops/worktrees/feat/issue-42/   # #42専用のリポジトリコピー
.beeops/worktrees/feat/issue-43/   # #43専用のリポジトリコピー
```

`node_modules` や `.next` はsymlinkで共有（ディスク節約）。PRマージ後にworktreeは自動削除される。

tmuxのウィンドウ構成は以下のようになる:

```
tmux session: bo
├── queen          # Queen
├── issue-42       # Leader + Workers（worktree隔離）
├── issue-57       # 別のLeader + Workers（別のworktree）
└── review-42      # Review Leader + Review Workers
```

## 外部依存ゼロ：ファイルとtmuxだけで通信する

ロール間の通信はファイルシステムとtmuxシグナルだけで動かしている。RedisもSQLiteも使っていない。

```
【下向き通信：親→子の指示】
.beeops/tasks/prompts/
  ├── leader-42.md       # Queen → Leader への指示書
  └── worker-42-1.md     # Leader → Worker への指示書

【上向き通信：子→親の完了通知】
.beeops/tasks/reports/
  ├── leader-42-summary.yaml        # 実装サマリー（PR URLなど）
  └── review-leader-42-verdict.yaml # approve / fix_required

【起床シグナル】
tmux wait-for -S queen-wake          # Leader→Queenに「終わったよ」
tmux wait-for -S leader-42-wake      # Worker→Leaderに「終わったよ」
```

Workerが完了したときの流れ:

```
# Worker側: 完了時にYAMLレポートを書き、シグナルを送る
cat > "$REPORTS_DIR/worker-${ISSUE}-${SUBTASK_ID}.yaml" <<REPORT
issue: $ISSUE
subtask_id: $SUBTASK_ID
status: completed
timestamp: $TIMESTAMP
REPORT

tmux wait-for -S leader-${ISSUE}-wake
```

```
# Leader側: シグナルを待つ（ポーリングしない）
tmux wait-for leader-${ISSUE}-wake
# → Worker完了レポートを読んで次の判断
```

`tmux wait-for` はtmuxの組み込み機能で、シグナルが来るまでブロックする。ポーリングではなくイベントドリブンだ。全ての状態がファイルに残るので、途中で死んでも再起動できる。

なぜRedisを使わなかったか。Claude Codeは `npm install` 一発で動く世界にいる。外部依存を1つ足すたびに、セットアップで脱落するユーザーが出る。tmuxはClaude Codeの前提条件として既にインストールされている。追加コストはゼロだ。

トレードオフはある。ファイルベースなので、Worker 5個以上の同時書き込みでYAMLの競合リスクが出る。現実的なIssue規模——Worker 2〜4個——なら問題にならない。

## 環境変数チェーン：ハードコードゼロのパス解決

beeopsはnpmパッケージだ。インストール先は `node_modules/beeops/` で、パスは環境ごとに違う。スクリプトのパスをハードコードできない。

解決策は環境変数のチェーン伝播。`/bo` コマンド実行時にパッケージの場所を解決し、以降のすべてのエージェントに引き継ぐ。

```
# /bo 実行時（bo.md）
PKG_DIR=$(node -e "console.log(require.resolve('beeops/package.json').replace('/package.json',''))")
BO_SCRIPTS_DIR="$PKG_DIR/scripts"
BO_CONTEXTS_DIR="$PKG_DIR/contexts"
```

```
# Leader起動時に環境変数をbakeする
env BO_LEADER=1 \
  BO_SCRIPTS_DIR="$BO_SCRIPTS_DIR" \
  BO_CONTEXTS_DIR="$BO_CONTEXTS_DIR" \
  claude --dangerously-skip-permissions ...
```

`/bo` → Queen → Leader → Worker まで、`BO_SCRIPTS_DIR` と `BO_CONTEXTS_DIR` が途切れずに流れる。ハードコードしたパスは0個。

全エージェントは同じ `claude` CLI プロセスを使っている。起動時に環境変数を付与するだけで役割が変わる。

## 4段階コンテキストフォールバック

各エージェントは起動時に環境変数で自分のロールを知る。`bo-prompt-context.py`（UserPromptSubmitフック）がロールに応じたコンテキストファイルを自動注入する。

```
// contexts/agent-modes.json（抜粋）
{
  "modes": {
    "BO_LEADER":       { "context": ["leader.md"] },
    "BO_WORKER_CODER": { "context": ["worker-base.md", "coder.md"] },
    "BO_WORKER_SECURITY": { "context": ["reviewer-base.md", "security-reviewer.md"] }
  }
}
```

コンテキストファイルの解決順序:

```
# bo-prompt-context.py より（簡略）
def resolve_file(filename, local_dir, locale):
    candidates = [
        local_dir / locale / filename,   # 1. プロジェクトローカル（ロケール別）
        local_dir / filename,            # 2. プロジェクトローカル（ルート）
        PKG_CONTEXT_DIR / locale / filename,  # 3. パッケージ（ロケール別）
        PKG_CONTEXT_DIR / filename,      # 4. パッケージ（ルート）
    ]
    return next((p for p in candidates if p.is_file()), None)
```

プロジェクト固有のコンテキストを置きたければ `npx beeops init --with-contexts` でローカルにコピーして編集する。ファイルを消せばパッケージのデフォルトに戻る。壊れない設計だ。

日本語ロケールにも対応している。`npx beeops init --locale ja` で日本語コンテキストが有効になる。

## レビューは自動で回る

beeopsには実装だけでなく、コードレビューのフローも組み込んである。

QueenがPR作成を検知すると、Review Leaderを起動する。Review Leaderは変更の複雑度を判定し、Review Workerを配置する。

```
simple（変更2ファイル以下、設定/ドキュメントのみ）:
  → code-reviewer のみ

standard（通常の実装）:
  → code-reviewer + security-reviewer

complex（5ファイル以上、認証やマイグレーション含む）:
  → code-reviewer + security-reviewer + test-auditor
```

各Review Workerは独立して動き、YAMLで所見を報告する。Review Leaderがそれを集約し、`approve` か `fix_required` を判定する。`fix_required` なら、Queenが実装Leaderを再起動する。自動で修正ループが回る。

## 使い方

### インストールと初期化

```
npm install beeops
npx beeops init           # 個人利用（デフォルト）
npx beeops init --shared  # チーム共有（.claude/settings.json に登録）
npx beeops init -g        # グローバル（全プロジェクトで有効）
```

インストールすると以下が生成される：

* `.claude/commands/bo.md` — `/bo` コマンド
* `.claude/skills/bee-*/` — エージェント用スキル（10個）
* `.beeops/settings.json` — 実行設定（自動生成）

### 設定ファイル（`.beeops/settings.json`）

`npx beeops init` 時に自動生成される。GitHubのログイン名も自動検出して埋めてくれる。

```
{
  "assignee": "me",          // "me" で自分にアサインされたIssueだけ処理
  "github_username": "GITHUB-ACCOUNT",
  "priority": "low",         // low以上のIssueを処理（high / medium / low）
  "skip_review": false,      // レビューフローをスキップするか
  "max_parallel_leaders": 2  // 並列で走るLeaderの数
}
```

`issues: [42, 55]` や `labels: ["bug"]` で処理対象を絞ることもできる。

### 起動

以下が自動で走る：

1. GitHubのIssue一覧を取得してqueue.yamlに同期
2. 優先度・依存関係を考慮してLeaderを起動
3. Leaderがタスク分解→Worker並列実行→PR作成
4. Review LeaderがPRをチェック
5. Approveされたら次のIssueへ

tmuxが起動してQueenと各Leaderのウィンドウが並ぶので、何が起きているかリアルタイムで見える。

### コンテキストのカスタマイズ

```
npx beeops init --with-contexts
```

このオプションで各エージェントへの指示書（コンテキストファイル）がローカルに展開される。

```
.beeops/contexts/
  ├── ja/
  │   ├── queen.md          # Queenへの指示書
  │   ├── leader.md         # Leaderへの指示書
  │   ├── coder.md          # Coderへの指示書
  │   └── security-reviewer.md
  └── ...
```

これを編集するだけで、「セキュリティレビューはOWASP Top 10を必ずチェックする」「コーディング規約はこのプロジェクトのlintに従う」といったプロジェクト固有のルールを各エージェントに注入できる。

## Agent Teamsとの違い

Claude Codeの公式機能「Agent Teams」とよく比較される。主な違いはここ。

|  | Agent Teams | beeops |
| --- | --- | --- |
| タスクの源泉 | 手動作成 | GitHub Issues自動同期 |
| タスク制御 | LLMが確率的に判断 | queue.yamlで明示的に管理 |
| ファイル競合 | 発生しうる | worktreeで完全分離 |
| セッション復帰 | 難しい（Teammateが消える） | queue.yaml/reportsで完全復帰 |
| レビューフロー | プロンプト指定・LLM判断 | 役割分離＋ループ制御＋YAML記録 |

Agent Teamsは「LLMに全部任せる」設計で、探索的なタスクに向いている。beeopsは「フローを決めて繰り返し動かす」設計で、GitHub Issueベースの開発ワークフローに向いている。

Claude Codeが1タスクをこなす精度はすでに十分高い。beeopsはその能力を「いつも同じフローで動かす」ための仕組みだ。

## まだ解決していないこと

Worker 4個以上の並列実行は十分にテストできていない。Anthropic APIのレートリミットが同時リクエスト数に依存するため、Worker数を増やすと詰まる可能性がある。

1時間を超えるIssueでのコンテキスト圧縮の影響も未検証だ。Leaderのコンテキストが圧縮されて、初期のサブタスク分解計画を忘れるケースがあり得る。

セキュリティレビューWorkerの検出精度も改善の余地がある。OWASPの主要項目はカバーしているが、ビジネスロジック固有の脆弱性は見落とす。

3層が最適解かはわからない。わかっているのは、1層では壊れたということと、3層でIssueが回っているということだ。

---

beeopsのコードはGitHubで公開している: [YuugouOhno/beeops](https://github.com/YuugouOhno/beeops)

```
npm install beeops
npx beeops init
```

フィードバックはIssueでいただけると嬉しい。
