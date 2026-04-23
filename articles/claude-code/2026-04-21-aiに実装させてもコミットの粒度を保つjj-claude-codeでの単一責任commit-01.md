---
id: "2026-04-21-aiに実装させてもコミットの粒度を保つjj-claude-codeでの単一責任commit-01"
title: "AIに実装させてもコミットの粒度を保つ〜jj × Claude Codeでの単一責任Commit〜"
url: "https://zenn.dev/sun_asterisk/articles/jj-hook-with-lefthook"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-21"
date_collected: "2026-04-22"
summary_by: "auto-rss"
---

## はじめに

`Spec Driven` や `Issue Driven` を  
`Claude Code` などのAIエージェントに実行させ、機能実装や修正をしていく  
という方法が定着しつつあるように見えます。

しかし、AIに実装させて、いざ `git` でコミットさせてみると  
AIエージェントの使い方によっては  
**あらゆる変更が1つの巨大なコミットにまとまりがち**です。

この記事では、`jj（Jujutsu）` の **Change** という概念と  
`Claude Code` を組み合わせることで  
AIが実装しても**コミットの単一責任を維持**する方法を紹介します。

前提環境

この記事では以下のツールを使用します。

`jj` と `Lefthook` のセットアップが済んでいない場合は、  
各リンクのインストール手順を参照してください。

## なぜ巨大なコミットはいけないのか

AIに「このIssueを実装して」と頼んだとき、こんなコミットが生まれることもあります。

```
feat: Implement user authentication (#42)
   - src/models/user.ts を追加
   - src/api/auth.ts を追加
   - src/middleware/session.ts を追加
   - tests/auth.test.ts を追加
   - prisma/schema.prisma を変更
   ...（30ファイル）
```

これが問題になる場面を3つ挙げます。

| 問題 | 巨大コミットの場合 | 単一責任なら |
| --- | --- | --- |
| **レビューが困難** | 変更の意図と範囲の把握が困難になり レビュワーが一つのコミットから 文脈を読み解かなければならない | 各コミットの責任範囲が明確で 実装の流れを追える |
| **[`git bisect`](https://git-scm.com/docs/git-bisect)  による原因特定が 困難** | 「このコミットが原因」と特定できても 30ファイル混在では更に手動探索が残る | `bisect` の結果がそのまま 「どの変更が原因か」の 答えになる |
| **[`git revert`](https://git-scm.com/docs/git-revert)  で必要以上の 取り消しが発生する** | 関係ない変更まで取り消され ロールバックが困難 | 問題のある変更だけを ピンポイントで取り消せる |

squash merge を採用しているチームである場合

[squash merge](https://docs.github.com/articles/about-pull-request-merges) は**PRの全コミットを1つに統合して指定先ブランチにマージ**する戦略です。  
コミット履歴は `1PR=1コミット` になるため、  
`bisect` と `revert` の粒度は**PR単位**になります。

その文脈であれば、コミットを細かい粒度で分ける意味はなく、  
PRの粒度、またはそのPR内で扱われるIssueの粒度を十分に細かく保つのが重要になります。

ただし、**PRレビュー時点ではブランチのコミットがそのまま**であるため、  
コミットが分かれていれば、以下の実装の流れをレビュワーが追えます。

1. モデルを追加
2. APIエンドポイントの実装
3. テストの実装

`squash merge` を採用しているチームでも、  
PR内のコミット粒度を細かく保つことは **レビュー品質の維持・向上**に影響し、  
最終的に**アプリケーションを構築するコード全体の品質**に良い影響を与えます。

## `jj` の `Change` と単一責任

`jj` では、コミットのことを **Change** と呼びます。  
各 `Change` には **description**（説明文）があり、実装前に記述するのが自然なワークフローです。

この `description` を「**このChangeで何をやるか**の責任範囲宣言」として使います。

```
# ↓ 概念説明。実際の実装では後述の jj safe-new を使います
jj new -m "feat: User modelとDBスキーマを追加する"
# ↑ このChangeで触るのはここまで

jj new -m "feat: 認証APIエンドポイントを追加する"
# ↑ このChangeで触るのはここまで
```

よって、ここでの `description` は、Issueを分解した**原子的な変更単位の宣言**です。  
Issueはそのまま仕様書として残り、`Change` はその実装の刻み方を記録します。

これを実現するため、`jj` の以下の機能を組み合わせます。

余談 （jj runを使いたかった話）

`jj run` は「指定したコミット範囲のすべての `Change` に対して任意のコマンドを実行する」  
という[設計ドキュメントページ](https://www.jj-vcs.dev/latest/design/run/)が存在しており、  
実装されていれば、次のような使い方ができるはずでした。

```
# やりたかったこと（実際には動かない）
jj run --revisions 'remote_bookmarks()..@' -- lefthook run pre-commit
```

しかし2026年4月時点の `jj run` は**スタブ実装**であったため、  
コマンドとして存在はしていますが、実際には何も実行しないようです。  
（使いたかった...。）

## `jj` のカスタムコマンドを作る

`jj` には `fix.tools` という設定があります。  
加えて、`aliases` + `util exec` といった `jj` のコマンドの拡張設定もあります。  
これらのコマンド設定を用いることで  
**「何を実行するか」と「いつ実行するか」の責任を分担**します。

```
# fix.tools.lefthook の登録（jj config set --repo 経由）
jj config set --repo 'fix.tools.lefthook.command' \
  '[".claude/scripts/jj-fix-lefthook.sh", "$path"]'
jj config set --repo 'fix.tools.lefthook.patterns' \
  '["glob:articles/**/*.md", "glob:books/**/*.md"]'
```

| コマンドまたは設定 | 役割 | 本記事での使い方 |
| --- | --- | --- |
| `fix.tools`,   `jj fix` | **実行ツールの宣言** `Lefthook` との 連携設定 | `lefthook` による `pre-commit` hook を `fix.tools` に登録 |
| `aliases`,   `util exec` | **実行タイミングの制御** スコープチェックや  `jj new` を 含めた一連のフロー | `jj safe-new` で   1. `jj fix`   2. `jj new`  を実行 |

`jj safe-new` スクリプト（`aliases` + `util exec`）が `jj fix` を呼び出し  
`fix.tools` に設定した `Lefthook` が実行される構造です。

!

`fix.tools` は本来 `prettier --write` のようなファイル変換ツールを登録するものです。  
登録されたコマンドが **`exit 0` で終了したときに限り、その `stdout` でファイルを上書き**します。  
そのため `lefthook run pre-commit` をそのまま登録するとチェックログがファイルに書き込まれてしまいます。

そこで `.claude/scripts/jj-fix-lefthook.sh` ラッパーを介し、  
`lefthook` の出力を `stderr` に逃がしつつ元ファイルの内容を `stdout` に返します。

ただし `jj fix` はツールの非ゼロ終了コードを自身の終了コードに伝播しないため、  
チェック失敗時はフラグファイル（`.claude/jj-fix-lefthook-failed`）を作成し、  
`jj safe-new` がその存在を確認することで次のChange移行をブロックします。

`prettier --write` や `markdownlint-cli2 --fix` のようなフォーマッタをラッパー内で呼べば  
フォーマットの自動修正も兼ねることができます。

!

**`revsets.fix = "@"` を設定しないと全 mutable commit が書き換わる**

`jj fix` はデフォルトで `reachable(@, mutable())` に含まれる全mutable commitを対象にします。  
設定なしで `jj safe-new` から `jj fix` を呼ぶと、過去のcommitにも遡ってフォーマッタが走り、履歴が意図せず書き換わります。

```
jj config set --repo 'revsets.fix' '"@"'
```

この設定により `jj fix` は常に `@`（working copy）のみを対象にします。

### カスタムコマンドの作成手順

1. スクリプトを `.claude/scripts/` に配置する（プロジェクト内で `git` 管理する）
2. 実行権限を付与する（`chmod +x`）
3. `jj config set --repo` でエイリアスと `fix.tools` を登録する
4. `jj safe-new` で動作確認する

このパターンで3つのスクリプトと2つのカスタムコマンドを作ります。

| スクリプト / カスタムコマンド | 役割 |
| --- | --- |
| `.claude/scripts/jj-fix-lefthook.sh` | `jj fix` から呼ばれる `Lefthook` ラッパー。`pre-commit` チェックを実行し、ファイル内容を `stdout` に返す |
| `jj safe-new` | `Change` 境界の品質チェック（`jj fix` 経由で `lefthook pre-commit`）→ `jj new` |
| `jj safe-push` | `bookmark conflict` チェック + 品質チェック（`lefthook pre-push`）→ `jj git push` |

## コアコンセプト

フローは**計画フェーズ**と**実行フェーズ**の2段階に分かれます。

| フェーズ | `Claude Code` の動き |
| --- | --- |
| **計画（PlanMode）** | 1. Issue を原子的な `Change` に分解  2. `TaskCreate` でタスクをUIに可視化  3. ユーザー承認を得る |
| **実行** | 1. `jj safe-new -m "<タスク名>"` で新 Change を作成（前 Change の品質チェックも兼ねる） 2. `Change` を実装 3. 繰り返す。完了後 `jj safe-push` |

`PreToolUse Hook` が `jj git push` の直接実行をブロックし、  
`PostToolUse Hook` が `TaskUpdate` を検知して `jj safe-new -m` を自動実行するため  
Claudeは必ずカスタムコマンド経由でフローを通過します。  
ターミナルでの `jj new` はStep 6-Bのシェルラッパーで `jj safe-new` にリダイレクトします。

実装完了後の `jj log` はこうなります。

```
◆  test: Integration testを追加
│
◆  feat: セッションミドルウェアを追加
│
◆  feat: 認証APIエンドポイントを追加
│
◆  feat: User modelとDBスキーマを追加
│
◆  initial commit
```

すべてIssue #42の実装ですが、**変更の責任が明確に分割**されています。

## 実装

### 1. `Rules` でフローを定義する

`.claude/rules/jj-change-driven.md` にルールファイルを作成し  
`CLAUDE.md` から参照します。

.claude/rules/jj-change-driven.md

```
# jj Change Driven 実装フロー

## 実装の進め方

Issueや仕様書を実装する場合、以下の手順で進めること。

### 計画フェーズ（実装前に必ず行う）

1. EnterPlanModeでIssueを読み、実装を原子的なChangeに分解する（1 Change = 1つの変更責任）
2. ExitPlanModeで計画をユーザーに提示し、承認を得る
3. 承認後、各ChangeをTaskCreateでタスクとして登録する
4. `.claude/jj-scope.json` を作成し、タスク名をキーに変更してよいファイル一覧を記録する

### 実行フェーズ

1. Changeの開始と同時に責任範囲を宣言する: `jj safe-new -m "<タスク名>"`
   （初回呼び出しはカウンタ 0 のためスコープ・品質チェックはスキップされる）
2. 実装する（`.claude/jj-scope.json` に記載されたファイルのみ変更する）
3. 次のChangeへ移る: `jj safe-new -m "<次のタスク名>"`
   （2回目以降はスコープチェック→品質チェックが自動実行される。失敗時は修正して再実行）
4. 実装する → 繰り返す

### Push

- すべての実装が終わったら `jj safe-push` でプッシュする
- `jj new`・`jj git push` の直接実行は禁止（Hookがブロックする）
- `jj safe-push` は push 成功時にカウンタをリセットするため、次の作業サイクルの初回 `jj safe-new` でも再びチェックがスキップされる
```

`CLAUDE.md` からは `@` で参照します。

```
<!-- CLAUDE.md -->
@.claude/rules/jj-change-driven.md
```

### 2. スコープマニフェスト `.claude/jj-scope.json` を作成する

計画フェーズでClaudeが生成するファイルです。タスク名をキーに  
その `Change` で変更してよいファイルを値として記録します。

.claude/jj-scope.json

```
{
  "feat: User modelとDBスキーマを追加": [
    "src/models/user.ts",
    "prisma/schema.prisma"
  ],
  "feat: 認証APIエンドポイントを追加": [
    "src/api/auth.ts"
  ],
  "feat: セッションミドルウェアを追加": [
    "src/middleware/session.ts"
  ],
  "test: Integration testを追加": [
    "tests/auth.test.ts"
  ]
}
```

キーは `jj safe-new -m "..."`（または `jj new -m "..."`）で設定される `Change` の `description` と完全一致させます。  
`jj safe-new` が現在の `description` をもとにスコープ定義を引くためです。

### 3. `jj safe-new` スクリプトを作る

`Change` 境界でスコープチェック→品質チェックを実行してから  
次の `Change` へ移るスクリプトです。  
`jj log -r @` で現在の `Change` の `description` を取得し  
`.claude/jj-scope.json` と照合します。

.claude/scripts/jj-safe-new.sh

```
#!/bin/bash
set -euo pipefail

SCOPE_FILE=".claude/jj-scope.json"
COUNT_FILE=".claude/jj-new-count"

# カウンタを読み込む（ファイルなし = 0 = 初回）
COUNT=0
if [ -f "$COUNT_FILE" ]; then
    COUNT=$(cat "$COUNT_FILE" 2>/dev/null || echo 0)
    COUNT=${COUNT:-0}
    # 数値以外の値（破損・空行）は 0 にフォールバック（set -e で止まらないよう POSIX グロブで検証）
    case "$COUNT" in
        ''|*[!0-9]*) COUNT=0 ;;
    esac
fi

if [ "$COUNT" -eq 0 ]; then
    echo "━━━ 初回 Change 作成: スコープ/品質チェックをスキップ ━━━"
else
    # スコープチェック（マニフェストが存在する場合のみ）
    if [ -f "$SCOPE_FILE" ]; then
        CURRENT_DESC=$(jj log -r @ --no-graph -T 'description' 2>/dev/null \
            | head -1 | tr -d '\n')

        if [ -n "$CURRENT_DESC" ]; then
            ALLOWED=$(jq -r --arg desc "$CURRENT_DESC" \
                '.[$desc] // [] | .[]' "$SCOPE_FILE" 2>/dev/null)

            if [ -n "$ALLOWED" ]; then
                echo "━━━ スコープチェック: $CURRENT_DESC ━━━"
                # mapfile は bash 4.0 以降のみ有効（macOS デフォルト bash 3.2 では動かない）
                if (( BASH_VERSINFO[0] >= 4 )); then
                    mapfile -t CHANGED < <(jj diff --name-only 2>/dev/null)
                    mapfile -t ALLOWED_ARRAY <<< "$ALLOWED"
                else
                    CHANGED=()
                    while IFS= read -r line; do CHANGED+=("$line"); done \
                        < <(jj diff --name-only 2>/dev/null)
                    ALLOWED_ARRAY=()
                    while IFS= read -r line; do ALLOWED_ARRAY+=("$line"); done \
                        <<< "$ALLOWED"
                fi

                UNAUTHORIZED=()
                for file in ${CHANGED[@]+"${CHANGED[@]}"}; do
                    found=false
                    for allowed in ${ALLOWED_ARRAY[@]+"${ALLOWED_ARRAY[@]}"}; do
                        [ "$file" = "$allowed" ] && found=true && break
                    done
                    [ "$found" = false ] && UNAUTHORIZED+=("$file")
                done

                if [ ${#UNAUTHORIZED[@]} -gt 0 ]; then
                    echo "✗ スコープ外のファイルが変更されています:"
                    printf "  - %s\n" "${UNAUTHORIZED[@]}"
                    echo "このChangeの責任範囲を確認し、別のChangeに切り出してください。"
                    exit 1
                fi
                echo "✓ スコープチェック通過"
            fi
        fi
    fi

    # 品質チェック（fix.tools 経由で Lefthook pre-commit を実行）
    # jj fix は fix.tools の非ゼロを exit code に伝播しないため
    # jj-fix-lefthook.sh がフラグファイルで失敗を通知する
    SENTINEL=".claude/jj-fix-lefthook-failed"
    rm -f "$SENTINEL" 2>/dev/null || true

    echo "━━━ Change境界チェック: jj fix ━━━"
    if ! jj fix; then
        echo "✗ チェック失敗。このChangeの実装を修正してから再実行してください。"
        exit 1
    fi

    if [ -f "$SENTINEL" ]; then
        rm -f "$SENTINEL" 2>/dev/null || true
        echo "✗ チェック失敗。このChangeの実装を修正してから再実行してください。"
        exit 1
    fi
    echo "✓ jj fix 通過"
fi

# チェック通過（またはスキップ）後にカウンタをインクリメント
echo $((COUNT + 1)) > "$COUNT_FILE"

echo "→ jj new $*"
# alias をバイパスして本来の jj new を呼ぶ（無限ループ防止）
command jj new "$@"
```

### 4. `jj safe-push` スクリプトを作る

プッシュ前の最終品質チェックとbookmarkのconflictチェック（diverge検出）を行うスクリプトです。

.claude/scripts/jj-safe-push.sh

```
#!/bin/bash
set -euo pipefail

COUNT_FILE=".claude/jj-new-count"

# bookmark conflict チェック（diverge 検出）
CONFLICTS=$(jj bookmark list --conflicted 2>/dev/null)
if [ -n "$CONFLICTS" ]; then
    echo "✗ bookmark に conflict があります。先に解消してください:"
    echo "$CONFLICTS"
    exit 1
fi

# pre-push 品質チェック（node を直接呼び出す）
# ※ lefthook 経由でなく node を直接呼ぶのは、Claude Code sandbox 内では
#    adhoc署名済みの lefthook binary が node を spawn できないため
MD_FILES=$(jj diff --name-only --from main -- 'glob:articles/**/*.md' 'glob:books/**/*.md' 2>/dev/null || true)
if [ -n "$MD_FILES" ]; then
    echo "━━━ pre-push チェック: textlint + markdownlint-cli2 ━━━"
    FAILED=0
    # shellcheck disable=SC2086  # 意図的なword split（記事ファイル名にスペースなし）
    node node_modules/textlint/bin/textlint.js $MD_FILES || FAILED=1
    # shellcheck disable=SC2086
    node node_modules/markdownlint-cli2/markdownlint-cli2-bin.mjs $MD_FILES || FAILED=1
    if [ "$FAILED" -eq 1 ]; then
        echo "✗ チェック失敗。コードを修正してから再実行してください。"
        exit 1
    fi
else
    echo "━━━ 変更された Markdown なし。pre-push チェックをスキップ ━━━"
fi

echo "✓ チェック通過 → jj git push"
# alias をバイパスして本来の jj git push を呼ぶ
command jj git push "$@"

# push 成功後にカウンタをリセット（次のサイクルで初回チェックスキップを再有効化）
rm -f "$COUNT_FILE"
```

### 4-B. `jj-fix-lefthook.sh` スクリプトを作る

`jj fix` の `fix.tools` から呼ばれるラッパーです。  
`fix.tools` に登録したコマンドは **`exit 0` のとき `stdout` の内容でファイルを上書き**するため、  
lint出力を `stderr` に逃がしつつ元ファイルの内容を `stdout` に返す必要があります。

!

**なぜ lefthook 経由でなく node を直接呼ぶのか**

lefthookはパッケージマネージャーが生成したシェルラッパーを介して起動するadhoc署名済みGoバイナリです。  
Claude CodeのBashツールは\*\*`sandbox` が有効なとき\*\*、adhoc署名済みバイナリのサブプロセスがnodeをspawnするパターンをブロックします。  
（`sandbox` 無効時は通常どおり動作します。）  
`jj fix` → `jj-fix-lefthook.sh` → `node` のチェーンはjjバイナリが親になるため、`sandbox` 有効時でも問題ありません。

.claude/scripts/jj-fix-lefthook.sh

```
#!/bin/bash
# jj fix の fix.tools から呼び出されるラッパー
# textlint と markdownlint-cli2 で pre-commit チェックを実行し、ファイル内容を stdout に返す
# stdout をファイル内容にしないと jj fix がファイルを空にしてしまうため cat が必要
#
# jj fix は fix.tools の非ゼロ終了を自身の exit code に伝播しないため
# チェック失敗時はフラグファイル（.claude/jj-fix-lefthook-failed）で jj-safe-new.sh に通知する
#
# ※ lefthook 経由でなく node を直接呼ぶのは、Claude Code sandbox 内では
#    adhoc署名済みの lefthook binary が node を spawn できないため
set -euo pipefail

FILE="$1"
SENTINEL=".claude/jj-fix-lefthook-failed"

FAILED=0
if [ -f "node_modules/textlint/bin/textlint.js" ]; then
    node node_modules/textlint/bin/textlint.js "$FILE" >&2 || FAILED=1
fi
if [ -f "node_modules/markdownlint-cli2/markdownlint-cli2-bin.mjs" ]; then
    node node_modules/markdownlint-cli2/markdownlint-cli2-bin.mjs "$FILE" >&2 || FAILED=1
fi

if [ "$FAILED" -eq 1 ]; then
    touch "$SENTINEL" 2>/dev/null || true
fi
cat "$FILE"
```

linterが失敗するとフラグファイルを作成します。  
その後 `cat "$FILE"` で元ファイルの内容を返すため `jj fix` 自体は終了コード0で完了しますが、  
`jj-safe-new.sh` がフラグファイルの存在を検知して失敗扱いにします。

### 5. `jj aliases` に登録する

スクリプトを配置したら、実行権限を付与します。

```
chmod +x .claude/scripts/jj-safe-new.sh .claude/scripts/jj-safe-push.sh .claude/scripts/jj-fix-lefthook.sh
```

設定の管理方針に応じて2つのパターンがあります。

パターン A: ユーザー設定（全リポジトリ共通）

すべての `jj` リポジトリで同じ設定を使いたい場合は `--user` に登録します。

```
# fix.tools（Lefthook ラッパー経由）をユーザー設定に登録
jj config set --user 'fix.tools.lefthook.command' '[".claude/scripts/jj-fix-lefthook.sh", "$path"]'
jj config set --user 'fix.tools.lefthook.patterns' '["glob:articles/**/*.md", "glob:books/**/*.md"]'

# jj fix のスコープを現在の change のみに限定
jj config set --user 'revsets.fix' '"@"'

# aliases をユーザー設定に登録
jj config set --user 'aliases.safe-new' '["util", "exec", "--", ".claude/scripts/jj-safe-new.sh"]'
jj config set --user 'aliases.safe-push' '["util", "exec", "--", ".claude/scripts/jj-safe-push.sh"]'
```

パターン B: リポジトリ設定（プロジェクト固有）

このプロジェクト専用の設定にしたい場合は `--repo` に登録します。  
`.jj/repo/config.toml` は `git` で追跡されないため、リポジトリを使う全員が一度実行します。

```
# fix.tools（Lefthook ラッパー経由）をリポジトリ設定に登録
jj config set --repo 'fix.tools.lefthook.command' '[".claude/scripts/jj-fix-lefthook.sh", "$path"]'
jj config set --repo 'fix.tools.lefthook.patterns' '["glob:articles/**/*.md", "glob:books/**/*.md"]'

# jj fix のスコープを現在の change のみに限定
jj config set --repo 'revsets.fix' '"@"'

# aliases をリポジトリ設定に登録
jj config set --repo 'aliases.safe-new' '["util", "exec", "--", ".claude/scripts/jj-safe-new.sh"]'
jj config set --repo 'aliases.safe-push' '["util", "exec", "--", ".claude/scripts/jj-safe-push.sh"]'
```

これで `jj safe-new` と `jj safe-push` が使えるようになります。

```
# 動作確認
jj safe-new -m "feat: 認証APIエンドポイントを追加する"
jj safe-push --dry-run
```

[`jj util exec`](https://www.jj-vcs.dev/latest/cli-reference/#jj-util-exec) を経由することで、エイリアスに追加した引数（`-m "..."` や `--dry-run`）は  
そのままスクリプトに転送されます。

bypassPermissionsモードで動かす方へ

`Claude Code` を  
`--dangerously-skip-permissions`（`bypassPermissions` モード）で起動すると、  
`PreToolUse Hook` を含む**すべての権限チェックが無効**になります。  
`deny` ルールや `hooks` が効かなくなるため、`Hook` だけに頼るのは危険です。

通常の開発で自動的に許可して運用したい場合は、`deny` ルールと `Hook` が維持される  
`dontAsk` モードの使用を検討してください。

```
claude --permission-mode dontAsk
```

`jj` は組み込みコマンド（`new` など）を `aliases` で上書きできないため、  
`bypassPermissions` モードで `jj new` の直接実行を確実にブロックする仕組みはありません。  
`CLAUDE.md` の `Rules` ファイルで `jj safe-new` を使うよう指示する運用上の対策に留まります。

参考: [Permission modes — Claude Code](https://code.claude.com/docs/ja/permission-modes) / [Permissions — Claude Code](https://code.claude.com/docs/ja/permissions)

### 6. `Hook` で `jj git push` の直接実行をブロックする

`jj git push` の直接実行をブロックする `PreToolUse Hook` を設定します。  
`jj safe-push` 内部からの `command jj git push` はサブプロセスのためHookの影響を受けません。

`jj new` のリダイレクトは後述のStep 6-Bシェルラッパーで対応します  
（`jj aliases` では組み込みコマンドを上書きできないため、`Hook` でのブロックは行いません）。

dry-run TTL バイパスの仕組み

`/jj-safe-push` skillは `jj git push --dry-run` と `jj git push` を別々の `Bash` ツール呼び出しで実行します。  
`PreToolUse Hook` は呼び出しごとに発火するため、そのままだと本番pushもブロックされてしまいます。  
そこで `--dry-run` を検知したタイミングでセッションID＋リポジトリ識別子を含む状態ファイルを書き出しておき、  
同じセッションからの本番pushが300秒以内に来た場合は通過させることで二重ブロックを防ぎます。

.claude/hooks/jj-lefthook.sh

```
#!/bin/bash
set -euo pipefail

INPUT=$(cat)

# jq が無い環境では Hook を失敗させず、安全側でブロックしない
if ! command -v jq > /dev/null 2>&1; then
    exit 0
fi

COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // empty' 2>/dev/null)

[ -z "$COMMAND" ] && exit 0

# SESSION_ID をファイル名に安全な文字列に正規化（パストラバーサル防止）
SESSION_SAFE=$(printf '%s' "$SESSION_ID" | tr -cd 'a-zA-Z0-9_-' | head -c 64)

# リポジトリごとに状態ファイルを分離（別リポジトリの dry-run が誤許可されるのを防ぐ）
STATE_DIR="$HOME/.cache/jj-safe-push"
REPO_ROOT=$(jj root 2>/dev/null || pwd)
REPO_KEY=$(printf '%s' "$REPO_ROOT" | cksum | awk '{print $1}')
STATE_PREFIX="${STATE_DIR}/${REPO_KEY}"
TTL=300

# --dry-run は /jj-safe-push skill のワークフローの一部として許可し、フラグを記録
# awk で &&/||/; を改行に展開し、文の先頭から始まる jj git push のみを対象にする（echo 等の引数内は除外）
if printf '%s\n' "$COMMAND" | awk '{gsub(/&&|\|\||;/, "\n"); print}' | grep -qE '^\s*(command[[:space:]]+)?jj[[:space:]]+git[[:space:]]+push[[:space:]].*--dry-run'; then
    mkdir -p "$STATE_DIR" 2>/dev/null || true
    [ -n "$SESSION_SAFE" ] && date +%s > "${STATE_PREFIX}-${SESSION_SAFE}" 2>/dev/null || true
    date +%s > "${STATE_PREFIX}-dry-run-done" 2>/dev/null || true
    exit 0
fi

# dry-run 実行済みの場合は push を許可（TTL: ${TTL}秒以内のみ有効）
NOW=$(date +%s)
if [ -n "$SESSION_SAFE" ] && [ -f "${STATE_PREFIX}-${SESSION_SAFE}" ]; then
    CREATED=$(cat "${STATE_PREFIX}-${SESSION_SAFE}" 2>/dev/null || echo 0)
    rm -f "${STATE_PREFIX}-${SESSION_SAFE}" 2>/dev/null || true
    if [ $((NOW - CREATED)) -lt $TTL ]; then
        exit 0
    fi
fi
if [ -f "${STATE_PREFIX}-dry-run-done" ]; then
    CREATED=$(cat "${STATE_PREFIX}-dry-run-done" 2>/dev/null || echo 0)
    rm -f "${STATE_PREFIX}-dry-run-done" 2>/dev/null || true
    if [ $((NOW - CREATED)) -lt $TTL ]; then
        exit 0
    fi
fi

# jj git push の直接実行をブロック
# jj new のリダイレクトはシェルラッパー（Step 6-B）で対応（aliases でビルトインは上書き不可）
# サブプロセス（スクリプト内部）からの呼び出しは Hook の対象外のため safe-push 内の push は通る
# awk で &&/||/; を改行に展開し、文の先頭から始まる jj git push のみをブロック（echo 等の引数内は除外）
if printf '%s\n' "$COMMAND" | awk '{gsub(/&&|\|\||;/, "\n"); print}' | grep -qE '^\s*(command[[:space:]]+)?jj[[:space:]]+git[[:space:]]+push([[:space:]]|$)'; then
    jq -n '{
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: "jj git push は直接実行できません。jj safe-push を使ってください（diverge チェックと品質チェックが実行されます）"
      }
    }'
    exit 0
fi

exit 0
```

実行権限の付与

念のため、実行権限付与コマンドを実行しておきましょう。

```
chmod +x .claude/hooks/jj-lefthook.sh
```

**`Claude Code` の設定**

このフックはリポジトリ固有の設定のため `.claude/settings.json`（リポジトリ設定）に登録します。  
ユーザーレベルの `~/.claude/settings.json` ではなく、プロジェクトルートの `.claude/settings.json` に記述することで  
リポジトリを共有するすべてのメンバーに自動的に適用されます。

.claude/settings.json

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/jj-lefthook.sh",
            "statusMessage": "jj git push の直接実行をチェック中..."
          }
        ]
      }
    ]
  }
}
```

!

`PreToolUse Hook` で `hookSpecificOutput.permissionDecision: "deny"` を返すと、`Claude Code` は  
そのツール呼び出しを**ブロック**します（[Hooks reference — Claude Code](https://code.claude.com/docs/en/hooks)）。  
`permissionDecisionReason` でブロック理由を構造化して渡せるため、  
Claudeはその理由を読み取り、自分で `jj safe-push` に切り替えて再実行してくれます。

`jj` の `aliases` では `git push` などの組み込みコマンドを上書きできないため、`Hook` でブロックしています。  
`jj new` のリダイレクトは後述のシェルラッパー（Step 6-B）で対応しています。

### 6-B. ターミナルでも `jj new` をリダイレクトする（シェルラッパー）

`PreToolUse Hook` は `Claude Code` からの実行のみを対象とします。  
ターミナルでの `jj new` も `jj safe-new` に自動リダイレクトしたい場合は  
シェルの関数でラップします。

~/.zshrc

```
jj() {
    if [[ "${1:-}" == "new" ]]; then
        shift
        echo "→ jj safe-new $*" >&2
        jj safe-new "$@"
        return $?
    fi
    if [[ "${1:-}" == "git" && "${2:-}" == "push" ]]; then
        shift 2
        echo "→ jj safe-push $*" >&2
        jj safe-push "$@"
        return $?
    fi
    command jj "$@"
}
```

シェルラッパーの実装詳細（再帰設計と return $? の理由）

関数内の `jj safe-new` / `jj safe-push` は `command` を付けません。  
シェル関数 `jj()` を再度呼び出し、どの `if` にもマッチしない場合のみ  
末尾の `command jj "$@"` に到達してjjバイナリへ渡る構造になっています。  
`command jj safe-new` と直接書くと一部環境で `safe-*` エイリアスの解決が  
不安定になるため、この再帰＋デフォルト分岐のパターンを採用します。  
（末尾の `command jj "$@"` のみ無限ループ防止のため `command` 付きで記述します）

`return $?` は直前の `jj safe-*` のexit codeを明示的に呼び出し元へ伝えます。  
`&& return` のチェーンにすると `jj safe-new "$@"` が失敗したとき `return` がスキップされ、  
`shift` 済みの `$@`（`new` が抜けた引数）で `command jj "$@"` が実行されてしまいます。  
`if` ブロックと `return $?` を組み合わせることで、失敗時に末尾の分岐へ流れ込むのを防いでいます。

### 7. `TaskUpdate` フックで `Change` 遷移を自動化する

これまでのステップでは `jj safe-new -m "<次のタスク名>"` をClaudeが明示的に呼ぶ前提でした。  
しかし、Claudeが実行し忘れると品質チェックがスキップされてしまいます。

`PostToolUse Hook` で `TaskUpdate` を監視し、`in_progress` に遷移したタイミングで  
自動的に `jj safe-new -m` を実行することで、**実行漏れをフックの仕組みで防ぎます**。

.claude/hooks/jj-task-start.sh

```
#!/bin/bash
set -euo pipefail

INPUT=$(cat)

# jq が無い環境では Hook を失敗させず安全にスキップ
if ! command -v jq > /dev/null 2>&1; then
    exit 0
fi

TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty' 2>/dev/null)
STATUS=$(echo "$INPUT" | jq -r '.tool_input.status // empty' 2>/dev/null)
# TaskUpdate の正式フィールドは tool_input.subject（旧: title）
TITLE=$(echo "$INPUT" | jq -r '.tool_input.subject // .tool_input.title // empty' 2>/dev/null)

# TaskUpdate で in_progress になったタイミングで jj safe-new -m を実行
# （前Changeの品質チェック + 新Change作成を一括で行う）
if [ "$TOOL" = "TaskUpdate" ] && [ "$STATUS" = "in_progress" ] && [ -n "$TITLE" ]; then
    # jj が無い or jj リポジトリでない場合はスキップ
    if ! command -v jj > /dev/null 2>&1; then
        echo "━━━ Change遷移をスキップ: jj コマンドが見つかりません ━━━"
        exit 0
    fi
    if ! jj root > /dev/null 2>&1; then
        echo "━━━ Change遷移をスキップ: jj リポジトリではありません ━━━"
        exit 0
    fi

    # 既に同じ description の Change であればスキップ（jj safe-new -m で作成済みの場合）
    CURRENT_DESC=$(jj log -r @ --no-graph -T 'description' 2>/dev/null | head -1 | tr -d '\n')
    if [ "$CURRENT_DESC" = "$TITLE" ]; then
        echo "━━━ Change既存: $TITLE ━━━"
        exit 0
    fi

    echo "━━━ Change遷移: jj safe-new -m \"$TITLE\" ━━━"
    # jj safe-new が未定義の場合は .claude/scripts/jj-safe-new.sh を直接実行する
    if jj help safe-new > /dev/null 2>&1; then
        jj safe-new -m "$TITLE"
    elif [ -f ".claude/scripts/jj-safe-new.sh" ]; then
        bash .claude/scripts/jj-safe-new.sh -m "$TITLE"
    else
        echo "━━━ Change遷移をスキップ: jj safe-new が未設定かつフォールバックスクリプトが見つかりません ━━━"
    fi
fi

exit 0
```

**`Claude Code` の設定**（`.claude/settings.json` — リポジトリ共有設定）

Step 6の `PreToolUse` と合わせて、`.claude/settings.json` に一括で記述します。

.claude/settings.json

```
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "TaskUpdate",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/jj-task-start.sh",
            "statusMessage": "Change宣言・スコープ読み込み中..."
          }
        ]
      },
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'lefthook_bin=\"\"; if command -v lefthook > /dev/null 2>&1; then lefthook_bin=$(command -v lefthook); elif [ -x ./node_modules/.bin/lefthook ]; then lefthook_bin=./node_modules/.bin/lefthook; fi; if [ -n \"$lefthook_bin\" ]; then result=$(\"$lefthook_bin\" run pre-commit 2>&1 | head -50); [ -n \"$result\" ] && printf \"%s\" \"$result\" | jq -Rs '\\''{ hookSpecificOutput: { hookEventName: \"PostToolUse\", additionalContext: . } }'\\''; fi; exit 0'"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/jj-lefthook.sh",
            "statusMessage": "jj git push の直接実行をチェック中..."
          }
        ]
      }
    ]
  }
}
```

### 8. `Lefthook` の設定

以下は `TypeScript/JavaScript` プロジェクト向けの例です。  
プロジェクトの言語・ツールチェーンに合わせて `run:` を差し替えてください  
（例: `cargo fmt --check` / `pnpm exec tsc --noEmit` / `markdownlint-cli2` など）。

lefthook.yml

```
pre-commit:
  parallel: true
  commands:
    lint:
      files: jj diff --name-only
      run: pnpm exec eslint {files}
    format:
      files: jj diff --name-only
      run: pnpm exec prettier --check {files}

pre-push:
  commands:
    test:
      run: pnpm test
```

!

**`jj` では `{staged_files}` が使えない**

`jj` にはステージングエリアがないため、Lefthookの `{staged_files}` は常に空になります。  
`files:` フィールドに `jj diff --name-only` を指定することで、  
現在のChange（`@`）に含まれる変更ファイルを取得できます。

`pre-push` で `main` からの全変更ファイルを対象にしたい場合は  
`jj diff --name-only --from main` を使います。

また `jj` のコロケーテッドリポジトリでは、Git Hooksとして自動実行させるのではなく  
`lefthook run <hook>` を `jj safe-new` / `jj safe-push` スクリプトから明示的に呼び出す運用にします。  
`lefthook install` は不要です。

フロー全体図（シーケンス図）

## まとめ

| 要素 | 役割 |
| --- | --- |
| Issue / 仕様書 | 実装の一次情報（`Claude Code` が読む） |
| `jj new -m "..."` | その `Change` の責任範囲を宣言して開始する |
| `.claude/jj-scope.json` | 各 `Change` が変更してよいファイルを宣言したスコープマニフェスト |
| `jj safe-new`  カスタムコマンド | 初回（COUNT=0）はスキップ。2 回目以降: 1. スコープチェック（`jj-scope.json` 照合） 2. `jj fix`（`fix.tools.lefthook` → `Lefthook pre-commit`） 3. カウンタ更新 → `jj new` |
| `jj safe-push`  カスタムコマンド | `bookmark conflict` チェック + 品質チェック（`Lefthook pre-push`）→ `jj git push` → カウンタリセット |
| Step 6-B  シェルラッパー | ターミナルからの `jj new` を `jj safe-new` にリダイレクト（`jj` の `aliases` はビルトインを上書きできないためシェル関数で対応） |
| `PreToolUse` `Hook`（`Bash`） `.claude/hooks/jj-lefthook.sh` | `jj git push` の直接実行を `permissionDecision: "deny"` でブロックし `jj safe-push` 経由を強制。`--dry-run` 実行後は TTL=300 秒以内の push を許可 |
| `PostToolUse` `Hook`（`TaskUpdate`） `.claude/hooks/jj-task-start.sh` | `in_progress` 遷移時に `jj safe-new -m "<タスク名>"` を自動実行。重複ガードで二重作成を防ぐ |

**`fix.tools`** で `Lefthook` との連携設定を宣言し  
**`[aliases]`** + **[`jj util exec`](https://www.jj-vcs.dev/latest/cli-reference/#jj-util-exec)** でそれを呼び出すコマンドを作ることで  
品質ゲートをユーザーが自由にカスタマイズできます。

`Claude Code` の `PreToolUse Hook`（直接実行ブロック）と `PostToolUse Hook`（`Change` 遷移の自動化）を  
組み合わせることで、AIが実装してもコミット履歴の単一責任を**フックの仕組みで**維持できます。
