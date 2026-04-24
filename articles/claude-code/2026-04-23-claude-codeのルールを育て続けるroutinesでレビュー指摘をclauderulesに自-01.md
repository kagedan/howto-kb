---
id: "2026-04-23-claude-codeのルールを育て続けるroutinesでレビュー指摘をclauderulesに自-01"
title: "Claude Codeのルールを育て続ける——Routinesでレビュー指摘を.claude/rulesに自動反映する"
url: "https://zenn.dev/zozotech/articles/20260423_pr_review_claude_rules"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "zenn"]
date_published: "2026-04-23"
date_collected: "2026-04-24"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Codeを活用した開発では、まず `.claude/rules/` にコーディングルールを整備するところから始まります。アーキテクチャ方針・命名規則・実装パターンをルールとして定義しておくことで、AIが生成するコードの品質を一定に保てます。

しかし実際に運用してみると、**初期設定の抜け漏れや、プロジェクトの変化に伴うルールの陳腐化**が問題になりました。ルールに記載のないパターンでAIがコードを生成し、レビューで毎回同じ指摘をする——という状況が生まれていたのです。AIの作ったPRをしっかりレビューするほど、「このルールを最初から入れておけば防げた」という指摘が積み上がっていきました。

この課題を解決するために導入したのが、**PRレビュー指摘を週次で自動分析して `.claude/rules/` へ反映する仕組み**です。レビューで発見した知見をルールへ継続的に反映し続けることで、AIによる実装・レビューの精度を底上げするサイクルを作ることが目的です。

この記事では、**Claude Codeのルーチン（Routines）** を使ってこの仕組みを構築する方法を紹介します。単なるログ収集ではなく、**並列サブエージェント**でPRを横断的に分析し、ギャップ分析を経て根拠付きでルールを更新、さらに変更PRのインラインコメントに元のレビュー指摘URLを紐づけるところまでを、Claudeが自律的に行います。

## 前提知識：`.claude/rules/` とは

Claude Codeはプロジェクトルート直下の `.claude/rules/` 配下に置いた `.md` ファイルをコーディング時に参照します。

```
.claude/
  rules/
    architecture.md    # アーキテクチャ方針
    coding-rules.md    # コーディング規約
    dart.md            # 言語固有ルール
    ...
```

`CLAUDE.md` がプロジェクト全体の指示書とすれば、`rules/` 配下はテーマ別の詳細ルール集です。ここを自動更新することで、過去の指摘がコード生成時点でフィードバックされるようになります。

## 前提条件

* Claude Code がインストール済み（`claude` コマンドが使えること）
* `gh` CLI がインストール・認証済み
* 対象リポジトリへの読み取り・書き込み権限

## エージェントプロンプト（汎用版）

この仕組みの核となるプロンプトです。`<REPO_URL>`、`<TARGET_DIR>`、`<LABEL>` の3箇所をプロジェクトに合わせて差し替えるだけで、任意のリポジトリに適用できます。

```
あなたはプロジェクトのコーディングルール管理エージェントです。

## 設定
- リポジトリ: <REPO_URL>（例: https://github.com/org/repo）
- 対象ディレクトリ: <TARGET_DIR>/（例: app/、src/ など）
- ルールディレクトリ: <TARGET_DIR>/.claude/rules/
- PRラベル: <LABEL>（例: chore）

## タスク概要
直近1週間（過去7日間）のGitHub PRのレビュー指摘を分析し、`<TARGET_DIR>/.claude/rules/` のルールファイルを
更新すべき場合はPRを作成し、各変更箇所にインラインコメントで参考コメントのリンクを記録してください。

## 手順

### STEP 1: <TARGET_DIR> に関連する直近1週間のPR番号リストを取得

SINCE=$(date -u -v-7d '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date -d '7 days ago' --utc '+%Y-%m-%dT%H:%M:%SZ')

# マージ済みPR
gh pr list --state merged --limit 100 --json number,title,mergedAt,files \
  | jq --arg since "$SINCE" \
    '[.[] | select(.mergedAt >= $since) | select(any(.files[]; .path | startswith("<TARGET_DIR>/"))) | .number]'

# オープン中のPR
gh pr list --state open --json number,title,createdAt,files \
  | jq --arg since "$SINCE" \
    '[.[] | select(.createdAt >= $since) | select(any(.files[]; .path | startswith("<TARGET_DIR>/"))) | .number]'

対象PR番号の一覧を取得したら STEP 2 に進む。

### STEP 2: 各PRのレビューコメントを並列サブエージェントで収集

対象PRが複数ある場合、1PRにつき1サブエージェントを起動して並列収集する。
すべてのサブエージェントを同時に起動し（並列実行）、全結果が揃ってから次のSTEPに進む。

各サブエージェントへの指示:
  以下のコマンドでPR #<NUMBER> のレビューコメントを取得し、結果をそのまま返してください:

  gh pr view <NUMBER> --json number,title,reviews,comments,reviewThreads

  コード品質・アーキテクチャ・命名・実装パターンに関する指摘を中心に、以下をまとめて返すこと:
  - PR番号
  - コメントID（`id` フィールド）
  - コメント本文
  - 指摘の要約
  - コメントURL（reviewThreadsの場合: `<REPO_URL>/pull/<NUMBER>#discussion_r<ID>`、
    commentsの場合: `<REPO_URL>/pull/<NUMBER>#issuecomment-<ID>`）

全サブエージェントの結果を集約し、各レビュー指摘について「PR番号・コメントURL・指摘内容」を記録する。

### STEP 3: 現在のルールファイルを読み込む

`<TARGET_DIR>/.claude/rules/` 配下のすべての `.md` ファイルを読み込む:

  find <TARGET_DIR>/.claude/rules/ -name "*.md" -type f

### STEP 4: ギャップ分析

STEP 2 で集約したレビュー指摘と現在のルールを照合し、以下を判定する:
1. 繰り返し指摘されているパターンがルールに未記載か
2. 新たなベストプラクティスとして追加すべき内容があるか
3. 既存ルールの修正・補強が必要な箇所があるか

ギャップが見つかった場合は、各変更について以下を記録する:
- 対象ファイル
- 追加・変更する内容
- 根拠となったコメントURL（複数ある場合はすべて列挙）と指摘の要約

更新不要の場合: 「ルール更新不要」と判定理由を出力してタスク終了。

### STEP 5: ルール更新とPR作成（更新必要な場合のみ）

1. 新ブランチを作成:
  BRANCH_NAME="chore/update-claude-rules-$(date +%Y%m%d)"
  git checkout -b "$BRANCH_NAME"

2. 該当するルールファイルを最小限に編集（根拠のある追加・修正のみ）

3. 変更をコミット:
  git add <TARGET_DIR>/.claude/rules/
  git commit -m "chore: update claude rules based on PR review feedback"

4. ブランチをプッシュ:
  git push origin HEAD

5. PRを作成し、PR番号を取得する:
  NEW_PR_URL=$(gh pr create --base main \
    --label "<LABEL>" \
    --title "chore: update .claude/rules/ based on weekly PR review analysis" \
    --body "<PRの説明。更新したルールファイル・変更内容・根拠となったコメントURLとレビュー指摘の要約を含める>")
  NEW_PR_NUMBER=$(echo "$NEW_PR_URL" | grep -o '[0-9]*$')

### STEP 6: 変更箇所にインラインコメントを追加

STEP 4 で記録した「変更箇所と根拠コメントURL」をもとに、各変更行にインラインコメントを付ける。

  COMMIT_SHA=$(git rev-parse HEAD)
  gh pr diff "$NEW_PR_NUMBER"   # diff から追加行の行番号を特定する

各変更箇所に対してインラインコメントをPOSTする:
  REPO_SLUG="<REPO_OWNER>/<REPO_NAME>"
  gh api repos/${REPO_SLUG}/pulls/${NEW_PR_NUMBER}/comments \
    --method POST \
    -f body="参考コメント: <COMMENT_URL>\n> <レビュー指摘の原文または要約>" \
    -f commit_id="${COMMIT_SHA}" \
    -f path="<TARGET_DIR>/.claude/rules/<FILE>" \
    -F line=<LINE_NUMBER> \
    -f side="RIGHT"

インラインコメントの形式:
  参考コメント: https://github.com/org/repo/pull/123#discussion_r456789
  > （指摘の要約）

複数コメントが根拠の場合は改行して列挙する。
変更箇所ごとに個別のインラインコメントを追加すること。

## 注意事項
- ルールファイルの変更は必要最小限に留める
- 根拠（レビュー指摘）のないルール変更は行わない
- PRはオープン状態で作成する
- インラインコメントはdiff上の追加行（side: RIGHT）に付ける
- 1つの変更箇所に複数のコメントが根拠の場合はまとめて1コメントにする
```

## 全体の仕組み

ポイントは2つです。

* **並列サブエージェントによる収集**: 対象PRが多くても、1PR=1サブエージェントで同時並行処理するためスケールする
* **根拠の追跡可能性**: 更新したルールの各行に、元のレビューコメントURLをインラインコメントとして紐づける

## 各STEPの解説

### STEP 1：対象PRの絞り込み

`gh pr list` の `--json files` オプションで変更ファイル一覧を取得し、`jq` で `<TARGET_DIR>/` に関連するPRのみを抽出します。モノレポ構成でも特定ディレクトリに絞ることでノイズを減らせます。

```
jq --arg since "$SINCE" \
  '[.[] | select(.mergedAt >= $since) | select(any(.files[]; .path | startswith("app/"))) | .number]'
```

### STEP 2：並列サブエージェントによる収集

ここがこの仕組みの核心です。PRが10件あれば10個のサブエージェントを**同時に起動**して並列収集します。

```
対象PRが複数ある場合、1PRにつき1サブエージェントを起動して並列収集する。
すべてのサブエージェントを同時に起動し（並列実行）、全結果が揃ってから次のSTEPに進む。
```

Claude Codeはこの指示を受けて、エージェントを並列実行します。順次処理に比べて収集時間が大幅に短縮されます。

各サブエージェントは `gh pr view` の `--json reviewThreads` を使って、コードへのインラインコメントも含めて取得します。

### STEP 3：現在のルールファイルを読み込む

`find` コマンドで `.claude/rules/` 配下の全 `.md` ファイルを動的に取得します。ファイルを固定列挙しないことで、ルールファイルが増えても対応できます。

収集したレビュー指摘と現在のルールを突き合わせるための「現在地」として機能します。

### STEP 4：ギャップ分析

単純に「指摘をルールに追記する」のではなく、現在のルールファイルと突き合わせてギャップを判定します。

* 既存ルールで網羅済みなら更新しない
* 繰り返し指摘されているパターンのみをルール化する
* 更新不要な場合はPRを作らずに終了する

この判定ロジックをClaudeに委ねることで、意味のない差分コミットを防ぎます。

### STEP 5：ルール更新とPR作成

ギャップが見つかった場合のみ実行されます。日付入りのブランチを作成し、対象のルールファイルを**根拠のある箇所だけ**最小限に編集してコミット・プッシュします。

PR作成後に番号を取得しておくのは、続くSTEP 6でインラインコメントをAPIから付けるために必要なためです。更新不要と判定された場合はこのSTEPを実行せずにタスクが終了するため、意味のない空PRは作られません。

### STEP 6：インラインコメントで根拠を追跡可能にする

更新したルールファイルのPR上で、変更した各行に元のレビューコメントURLをインラインコメントとして付けます。

```
参考コメント:
- https://github.com/org/repo/pull/123#discussion_r456789
- https://github.com/org/repo/pull/124#issuecomment-789012
> AsyncValue.guardを使わずstateを直接更新しているケースが複数見られる
```

「なぜこのルールが追加されたのか」を後から追跡できる状態にしておくことで、ルールのメンテナンスが格段に楽になります。

## ルーチンへの登録

Claude Codeの `/schedule` スキルを使ってルーチンを登録します。ルーチンはClaudeのWebインフラ上で動作するため、**ラップトップを開いていなくても実行されます**。

対話形式でプロンプトを貼り付け、実行タイミングを設定します。

```
どのくらいの頻度で実行しますか？
> 毎週月曜の朝9時

タスクの詳細を教えてください：
> （上記のエージェントプロンプトを貼り付ける）
```

設定が完了すると、指定したスケジュールでルーチンが自動起動します。実行のたびにClaudeが新しいセッションを作成し、プロンプトの手順をそのまま実行します。

## なぜこの方法が効果的なのか

### 暗黙知が形式知として積み上がっていく

チームのコーディング規約は「なんとなくの共通認識」に留まりがちです。口頭のレビューで共有されていた知見が、週次で `.claude/rules/` に文書化されていきます。新規メンバーのオンボーディングにも効果的です。

### Claudeが「チームの記憶」を持ち続ける

`.claude/rules/` に反映されたルールは次のコーディングセッションからClaudeが参照します。「この書き方は過去にレビューで指摘された」という文脈をAIが持ち続けることで、同じ失敗パターンをコード生成の時点で防げます。

### ルールに根拠が紐づき、キャッチアップが容易になる

インラインコメントによってルールの出所が追跡可能になるため、「このルールはなぜあるのか」がわかります。根拠が薄いルールは削除しやすく、ルールセット自体が健全に保たれます。

さらに、ルール変更のPRをレビューするだけで「先週どんな指摘が多かったか」を把握できます。元のレビューコメントURLがインラインに記載されているため、背景を深掘りしたいときも1クリックで原文に飛べます。毎週のスプリントレトロスペクティブで確認する材料としても活用できます。

## 運用上の注意点

## まとめ

| STEP | 内容 |
| --- | --- |
| STEP 1 | `gh` CLIで直近1週間の対象PR番号を取得 |
| STEP 2 | 1PR=1サブエージェントで並列収集 |
| STEP 3 | 現在の `.claude/rules/` を読み込む |
| STEP 4 | ギャップ分析で更新の要否を判定 |
| STEP 5 | ルール更新・ブランチ作成・PR作成 |
| STEP 6 | 変更行に元のレビューコメントURLを紐づける |

Claude Codeのルーチン（Routines）は、単発タスクの自動化だけでなく、チームの知識を継続的に蓄積する仕組みづくりに活用できます。「同じ指摘を繰り返す」というコストを減らし、レビューをより本質的な議論に集中させるための一手として、ぜひ試してみてください。

## 参考
