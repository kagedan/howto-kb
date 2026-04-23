---
id: "2026-03-24-claude-code-jujutsu-worktreecreate-hookで並行セッションを自動-01"
title: "Claude Code + Jujutsu: WorktreeCreate hookで並行セッションを自動分離する"
url: "https://zenn.dev/jasagiri/articles/eb07d2d9a8acd1"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-03-24"
date_collected: "2026-03-26"
summary_by: "auto-rss"
---

# 

Claude Codeで複数セッションを同時に走らせると、同一リポジトリ内で変更が混在する。git worktreeなら `claude --worktree` で自動分離できるが、Jujutsu (jj) ユーザーはそのままでは使えない。

本記事では、Claude CodeのWorktreeCreate hookを使って `jj workspace` に委譲し、`claude --worktree` をJujutsuネイティブに動かす方法を解説する。プラグインとして公開済みなので、1コマンドで導入できる。

## TL;DR

```
# プラグインをインストール
claude plugin install jj-worktree@jasagiri/claude-jj-worktree

# jj workspaceで自動分離されたセッションを起動
claude --worktree feature-auth
```

これだけで、Claude Codeの `--worktree` が `jj workspace add` に委譲される。

## 問題: 並行セッションで変更が混ざる

Jujutsu (jj) のco-locatedリポジトリで開発していると、こういう状況が起きる:

```
# ターミナル1: 機能Aの実装
cd ~/project && claude

# ターミナル2: バグBの修正
cd ~/project && claude
```

両セッションが同じワーキングコピーを共有するため、jj statusには両方の変更が混在する。コミット時にどの変更がどのタスクのものか判別できない。

## 解決策の全体像

Claude Codeには `--worktree` フラグがあり、セッションごとに隔離された作業ディレクトリを作る。内部ではgit worktreeを使うが、**WorktreeCreate / WorktreeRemove hook** を設定すると、この動作を完全に置き換えられる。

```
claude --worktree feature-auth
  ↓
WorktreeCreate hook が発火
  ↓
jj workspace add .claude/worktrees/feature-auth
  ↓
Claude Code の内部 cwd が .claude/worktrees/feature-auth/ に切り替わる
  ↓
Edit / Write / Read / Glob 等の全ツールがワークスペース内で動作
```

## セットアップ

### 方法1: プラグインをインストール（推奨）

```
claude plugin install jj-worktree@jasagiri/claude-jj-worktree
```

これだけで完了。hookスクリプトとsettings.jsonの設定がプラグイン経由で自動的に有効になる。

### 方法2: 手動セットアップ

プラグインを使わず手動で設定する場合は以下の通り。

#### hookスクリプトの作成

`~/.claude/hooks/jj-worktree-create.sh`:

```
#!/usr/bin/env bash
# WorktreeCreate hook: jj workspace add に委譲
# stdout には絶対パスのみ出力。他は全て stderr へ。

set -euo pipefail

INPUT=$(cat)
NAME=$(echo "$INPUT" | jq -r '.name // empty')
CWD=$(echo "$INPUT" | jq -r '.cwd // empty')

REPO_DIR="${CWD:-$PWD}"

if ! (cd "$REPO_DIR" && jj root 2>/dev/null 1>/dev/null); then
  echo "Not a jj repository: $REPO_DIR" >&2
  exit 1
fi

REPO_ROOT=$(cd "$REPO_DIR" && jj root 2>/dev/null)

if [ -z "$NAME" ]; then
  NAME="wt-$(date +%s | tail -c 6)"
fi

WORKSPACE_DIR="${REPO_ROOT}/.claude/worktrees/${NAME}"

mkdir -p "$(dirname "$WORKSPACE_DIR")"
echo "Creating jj workspace '${NAME}' at ${WORKSPACE_DIR}" >&2
(cd "$REPO_ROOT" && jj workspace add "$WORKSPACE_DIR" --name "$NAME") >&2

echo "$WORKSPACE_DIR"
```

`~/.claude/hooks/jj-worktree-remove.sh`:

```
#!/usr/bin/env bash
# WorktreeRemove hook: jj workspace forget + ディレクトリ削除

set -euo pipefail

INPUT=$(cat)
WORKTREE_PATH=$(echo "$INPUT" | jq -r '.worktree_path // empty')

if [ -z "$WORKTREE_PATH" ]; then
  echo "No worktree_path provided" >&2
  exit 1
fi

WS_NAME=$(basename "$WORKTREE_PATH")
REPO_ROOT=$(cd "$WORKTREE_PATH" && jj root 2>/dev/null || echo "")

if [ -n "$REPO_ROOT" ]; then
  echo "Forgetting jj workspace '${WS_NAME}'" >&2
  (cd "$REPO_ROOT" && jj workspace forget "$WS_NAME" 2>/dev/null) >&2 || true
fi

if [ -d "$WORKTREE_PATH" ]; then
  echo "Removing worktree directory: ${WORKTREE_PATH}" >&2
  rm -rf "$WORKTREE_PATH"
fi
```

実行権限を付与:

```
chmod +x ~/.claude/hooks/jj-worktree-{create,remove}.sh
```

#### settings.json にhookを登録

`~/.claude/settings.json`:

```
{
  "hooks": {
    "WorktreeCreate": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/jj-worktree-create.sh",
            "timeout": 30
          }
        ]
      }
    ],
    "WorktreeRemove": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/jj-worktree-remove.sh",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

## 使い方

### 起動時に分離

```
# タスク名をworktree名にすると管理しやすい
claude --worktree feature-auth
claude --worktree fix-memory-leak
```

各セッションが独立した jj workspace で動作する:

```
~/project/                          # default workspace (元のまま)
~/project/.claude/worktrees/
  feature-auth/                     # セッション1の作業コピー
  fix-memory-leak/                  # セッション2の作業コピー
```

### セッション内から切り替え

通常モードで起動した後からでも、セッション内で「worktreeで作業して」と伝えれば EnterWorktree ツールが発動する。

### ワークスペースの確認

```
default: xyzabc12 (empty) (no description set)
feature-auth: pqrs3456 feat(auth): add OAuth2 flow
fix-memory-leak: uvwx7890 fix(core): prevent double-free
```

### 作業の流れ

1. `claude --worktree feature-auth` でセッション起動
2. Claude Codeが `.claude/worktrees/feature-auth/` 内で作業
3. コミット: `jj describe -m "feat(auth): add OAuth2 flow"` + `jj new`
4. セッション終了時、ExitWorktreeでworkspaceがcleanup
5. 変更はリポジトリのDAGに残っている — default workspaceから `jj log` で確認可能

### 変更をdefault workspaceに統合

worktree内でコミットした変更は、jjのDAGに記録されている。default workspaceに統合するには:

```
# default workspace に戻ってから
cd ~/project

# worktreeで作ったチェンジを確認
jj log

# default workspace の上に rebase
jj rebase -s <worktree-change-id> -d @

# または squash で統合
jj squash --from <worktree-change-id> --into @
```

## なぜgit worktreeではなくjj workspaceか

jj co-locatedリポジトリは `.git` ディレクトリを持つため、Claude Codeのデフォルト動作では `git worktree add` が実行される。しかし:

|  | git worktree | jj workspace |
| --- | --- | --- |
| jj statusで認識 | されない | される |
| jj logに反映 | されない | される |
| jj rebase/squashで統合 | 不可 | 可能 |
| co-located repoで動作 | 動くがjjと断絶 | ネイティブ |

git worktreeで作った作業コピーでは `jj status` が `Error: There is no jj repo` を返す。jjのコミットグラフから完全に切り離されてしまう。

## hookの仕組み: なぜこれで動くのか

EnterWorktreeのドキュメントには以下の記述がある:

> Outside a git repository: delegates to WorktreeCreate/WorktreeRemove hooks for VCS-agnostic isolation

そして重要なのは:

> **WorktreeCreate hookが設定されている場合、hookがgit worktreeの動作を完全に置き換える。**

つまりgitリポジトリ内であっても、hookが優先される。hookは以下の契約を守る:

* **stdin**: セッション情報のJSON (`name`, `cwd` 等)
* **stdout**: 作成したワークスペースの**絶対パスのみ**(他の出力はstderrへ)
* **exit code 0**: 成功

Claude Codeはstdoutのパスを受け取り、内部cwdをそのパスに変更する。これにより Edit, Write, Read, Glob 等の全ツールがワークスペース内のファイルを操作する。

プラグインとして配布する場合、hookスクリプト内のパスには `${CLAUDE_PLUGIN_ROOT}` 変数が使える。これによりインストール先に依存しないポータブルな設定が実現できる。

```
{
  "hooks": {
    "WorktreeCreate": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/jj-worktree-create.sh"
          }
        ]
      }
    ]
  }
}
```

## stdout汚染に注意

hookスクリプトで最もハマりやすいポイントは **stdout汚染** だ。Claude Codeはstdoutの内容をそのままワークスペースのパスとして解釈する。

```
# NG: jj root の出力がstdoutに漏れる
if ! (cd "$REPO_DIR" && jj root --quiet); then

# OK: stdout と stderr の両方を抑制
if ! (cd "$REPO_DIR" && jj root 2>/dev/null 1>/dev/null); then
```

`jj workspace add` の出力も  `>&2` でstderrにリダイレクトする:

```
(cd "$REPO_ROOT" && jj workspace add "$WORKSPACE_DIR" --name "$NAME") >&2
```

最終行の `echo "$WORKSPACE_DIR"` だけがstdoutに出力されるようにする。

## .gitignore でworktreeディレクトリを除外

`.claude/worktrees/` はjj/gitで追跡する必要がない。`.gitignore` に追加:

## 応用: 入れ子リポジトリの横断管理

モノレポ風の構造で複数のjjリポジトリが入れ子になっている場合:

```
organization/
  sources/
    foundation/
      nilvm/.jj          # 独立リポジトリ
      nim-mitmproxy/.jj   # 独立リポジトリ
      ...                 # 50+ repos
    cognitive/.jj
    services/.jj
```

親ディレクトリをjjリポジトリとして初期化し、ホワイトリスト `.gitignore` で横断的な設定ファイルだけを管理できる:

```
# Ignore everything
*
# Allow cross-repo config
!.gitignore
!.claude/
!.claude/**
```

子リポジトリは各自の `.git` を持つため、親からは自動的に不可視。新しい子リポジトリを追加しても `.gitignore` の変更は不要。

## まとめ

### プラグイン利用（推奨）

```
claude plugin install jj-worktree@jasagiri/claude-jj-worktree
claude --worktree my-task
```

### 手動設定

| 設定ファイル | 役割 |
| --- | --- |
| `~/.claude/hooks/jj-worktree-create.sh` | `jj workspace add` に委譲 |
| `~/.claude/hooks/jj-worktree-remove.sh` | `jj workspace forget` + ディレクトリ削除 |
| `~/.claude/settings.json` | WorktreeCreate/Remove hook登録 |

git worktreeの仕組みをjj workspaceにそのまま載せ替えられるのは、Claude Codeのhookシステムが VCS-agnostic な設計になっているおかげだ。Jujutsuに限らず、Mercurial や Pijul など他のVCSでも同じアプローチが取れる。

---

Source: [jasagiri/claude-jj-worktree](https://github.com/jasagiri/claude-jj-worktree)
