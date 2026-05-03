---
id: "2026-05-02-jj-workspaceでaiエージェントを並列運用する時にagentsmdだけでは足りなかった話-01"
title: "jj workspaceでAIエージェントを並列運用する時に、AGENTS.mdだけでは足りなかった話"
url: "https://zenn.dev/sawacarac/articles/9ca09684d19231"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "LLM", "OpenAI", "Gemini", "zenn"]
date_published: "2026-05-02"
date_collected: "2026-05-03"
summary_by: "auto-rss"
query: ""
---

## はじめに

`jj workspace` を使って複数のAIエージェントを並列で動かす運用を試していたところ、`AGENTS.md` に「`git` を使わない」と書いてもエージェントが `git` を叩いてくる、という問題に何度かぶつかりました。

最終的には、PATHに shim を差し込んで `git` バイナリそのものを遮断する構成に落ち着きました。この記事はその試行錯誤の記録です。

## 結論

| 対策 | 効果 |
| --- | --- |
| `AGENTS.md` に方針を書く | 弱い。エージェントは普通に `git` を叩く |
| 各エージェントの permission 設定で `git` を deny | 中。設定ファイルがエージェントごとに方言違いでスケールしない |
| **PATH に shim を入れて `git` バイナリを潰す** | **強い。エージェント非依存で効く** |
| `jj git colocation disable` で non-colocated に寄せる | 強い。ただし `git` 統合UIが使えなくなるトレードオフあり |

`AGENTS.md` は意図伝達としては書くべきですが、抑止力としては期待しないほうがいいです。OS層で `git` を消すのが結局一番早かった、という話です。

## 何が問題だったか

最初は `AGENTS.md` に「このリポジトリでは `jj` を使う」「`git` は使わない」と書いていました。

実際に動かしてみると、こういう挙動が頻繁に出ます。

* エージェントが `git status` で状況把握しようとする
* IDEが裏で `git fetch` を走らせる
* 別のエージェントが `git log` を叩いて履歴を読む

`jj` と `git` を同じworking copyで混ぜると、たまたま動くことはあっても、bookmarkの位置がズレたり、reachableでなくなったcommitがabandonされたりします。気づいた時には repo の状態が分からなくなっていることもありました。

## `AGENTS.md` だけで足りない訳

`AGENTS.md` は意図を共有する手段としては有効です。ただし強制力がありません。

* 別のAIエージェント
* IDEのGit連携
* 補助ツール
* 初見の人間

これらは `AGENTS.md` を読まないか、読んでも無視します。  
ルールを書いても、使えるコマンドがあれば使われる、というのが実態でした。

### permission設定で縛るのも微妙

「じゃあ各エージェントの設定ファイルで `git` を deny すれば」と最初は考えました。

たとえば Claude Code には `.claude/settings.json` の `permissions.deny` という機構があります。最新の公式表記は `Bash(git *)` で、これを書けば `git` を拒否できます。

<https://code.claude.com/docs/en/permissions>

ただしこれは Claude Code 専用です。Codex CLI も Gemini CLI も Cursor も、このファイルは読みません。

| エージェント | 設定ファイル | `git` 拒否の書き方 |
| --- | --- | --- |
| Claude Code | `.claude/settings.json` | `permissions.deny: ["Bash(git *)"]` |
| OpenAI Codex CLI | `~/.codex/config.toml` 等 | サンドボックスポリシーで shell コマンドを制限 |
| Gemini CLI | `.gemini/settings.json` | `tools.coreTools` から ShellTool を外す or `tools.exclude` |
| Cursor | エージェント設定UI | UI側で個別指定 |

3つのエージェントを使うなら3つの方言で同じことを書きます。新しいエージェントが増えるたびにメンテも増えます。マルチエージェント前提だとこのアプローチはスケールしません。

## `jj workspace` の基本

本題に入る前に `jj workspace` の使い方を整理します。  
AIエージェントを並列で動かすときは、同じworkspaceで `jj new` で分けるよりも、最初から別directoryに分けるほうが安全です。

```
# パターンA: main から派生（一般的）
jj workspace add ../myproj.feature-a -r main
jj workspace add ../myproj.feature-b -r main

# パターンB: 現在の作業状態を引き継ぐ（-r を省略）
jj workspace add ../myproj.feature-a

# パターンC: 任意のリビジョンから派生
jj workspace add ../myproj.feature-a -r @-
jj workspace add ../myproj.feature-a -r abc123
jj workspace add ../myproj.feature-a -r my-branch
```

| パターン | 用途 |
| --- | --- |
| A | きれいな新規作業を切り出したい時 |
| B | 今いじっている続きを別workspaceでエージェントに任せたい時 |
| C | 親リビジョンを正確にコントロールしたい時 |

ただし、workspaceを分けても `git` を叩けてしまう問題は残ります。これが本記事の主題です。

## 採用したアプローチ ─ PATH shim で `git` を潰す

エージェント非依存で効く対策はOS層しかありません。  
PATHに shim を差し込んで、`git` バイナリそのものをエージェントから見えなくします。

### shim とは

shim は、同じ名前の偽バイナリをPATHの先頭に置いて、本物の呼び出しを横取りする小さなスクリプトです。

Unixのshellは `git` と打たれると、`PATH` 環境変数を先頭から順に探して最初に見つかった `git` を実行します。

```
PATH=/your/workspace/.codex/shims:/usr/bin:/usr/local/bin
```

このPATHで `git status` を実行すると、shellは `/your/workspace/.codex/shims/git` を最初に見つけてそれを実行します。本物の `/usr/bin/git` には到達しません。

asdf、rbenv、direnvなどが使っている古典的な仕組みです。

### `git` を全面禁止にする

shimを作る前に、どこまで止めるかを決めます。  
最初は「`git status` のようなread-onlyなコマンドは許可してもよい」と考えていましたが、結論として全面禁止にしました。

理由は2つです。

* `jj` で全部代替できる
* 一部だけ許可すると、エージェントが「`git` はこのrepoで使ってよい」と誤学習する

`git` の主要コマンドは `jj` で置き換えられます。

| Git | jj |
| --- | --- |
| `git status` | `jj st` |
| `git log` | `jj log` |
| `git diff` | `jj diff` |
| `git fetch` | `jj git fetch` |
| `git push` | `jj git push` |
| `git branch` | `jj bookmark list` |
| `git checkout` | `jj edit` / `jj new` |

入口を1箇所で閉じるほうが運用が安定します。

### shim 本体

.codex/shims/git

```
#!/usr/bin/env bash
set -euo pipefail

cat >&2 <<'EOF'
git is disabled in this repository. Use jj instead.

Common replacements:
  git status        -> jj st
  git log           -> jj log
  git diff          -> jj diff
  git fetch         -> jj git fetch
  git push          -> jj git push
  git branch        -> jj bookmark list
  git checkout      -> jj edit / jj new
  git stash         -> jj new @-
EOF

exit 1
```

エラーメッセージに置き換えコマンドを書いておくと、エージェントが「`jj` を使えばいい」と気づいて自力で復帰しやすくなります。

### wrapper 経由でエージェントを起動する

shim はPATHに入っていなければ意味がありません。  
小さなwrapperでPATHを差し込みます。

.codex/with-agent-path.sh

```
#!/usr/bin/env bash
set -euo pipefail

script_dir="$(
  cd -- "$(dirname -- "$0")" && pwd
)"

export PATH="$script_dir/shims:$PATH"

if [ "$#" -eq 0 ]; then
  exec "${SHELL:-/bin/sh}"
fi

exec "$@"
```

これでエージェントを次のように起動します。

```
# Codexの例
.codex/with-agent-path.sh codex

# shim有効なshellを開く
.codex/with-agent-path.sh zsh
```

PATH解決はOS（shell + filesystem）レイヤーで動くので、Claude Code、Codex、Gemini CLIのどれを起動してもこのshimを経由します。1つ用意すれば全エージェントに同じ制約が効きます。

direnvを使っているなら `.envrc` で済ませるほうが楽です。

.envrc

```
export PATH="$PWD/.codex/shims:$PATH"
```

ディレクトリに入った瞬間に `git` が消えます。

## non-colocated も検討した

shimだけでも十分実用的ですが、根本対策としてはnon-colocatedのほうが強いです。  
`.git` 自体が見えなくなるので、エージェントが `git` を発想する経路が消えます。

### コマンド

既存リポを変換する場合:

```
jj git colocation disable
```

新規にcloneする場合:

```
jj git clone --no-colocate <url>
```

`jj git colocation disable` はバージョン0.34.0以降で利用可能です。  
0.34.0以降は `jj git init` / `jj git clone` のデフォルトがcolocatedに変わっているので、non-colocatedにしたい場合は明示が必要です。

### トレードオフ

non-colocatedはメリットだけではありません。

| 項目 | non-colocatedの挙動 |
| --- | --- |
| `git` コマンド直接実行 | 動かない（→ 今回の目的そのもの） |
| GitHub/GitLabへのpush/fetch | `jj git push` / `jj git fetch` で問題なく動作 |
| CI（リモート側からは普通のgitリポ） | 問題なし |
| VS CodeのGitパネル | 動かない |
| SourceTree/GitKraken/Forkなどの GUI Git クライアント | 動かない |
| `pre-commit` / `husky` などの `.git/hooks/` 前提ツール | 動かないことがある |

ターミナル中心で `jj log` と `jj st` で生きていくスタイルなら、ほぼノーペナルティでnon-colocatedに移行できます。  
VS CodeのGitパネルを常用しているなら、そこは妥協ポイントになります。

shim層だけでも実用上は問題なく回るので、non-colocated化は再発防止のための念押しという位置付けで後追いでも問題ありません。

## ハーネス層の整理

ここまでの対策をまとめます。  
下に行くほど強制力が高くなります。

| レイヤー | 何で縛るか | 強制力 |
| --- | --- | --- |
| プロンプト層 | `AGENTS.md` などの自然言語ルール | 弱い |
| 設定層 | 各エージェントの permission 設定 | 中。方言が多くスケールしない |
| 環境層 | OSのPATHで `git` バイナリを遮断 | 強い。エージェント非依存 |
| 構造層 | non-colocatedで `.git` を見せない | 強い。トレードオフあり |

`AGENTS.md` だけで運用していた時はプロンプト層しか機能していませんでした。環境層（shim）を入れた時点で、エージェントの種類を増やしても運用が崩れなくなります。

最近この手の話は harness engineering と呼ばれ方をすることが増えてきました。  
LLMの重みと、LLMが外界に作用するための仕組み（実行環境・ツール群・制約）を切り分けて、後者をharnessと呼ぶ用語法です。バズワード気味ではありますが、「プロンプト→設定→環境→構造」という強制力の階層を意識する考え方は実務で役立ちます。

## おすすめ構成

最終的にこの順番で運用しています。

1. `jj workspace` で 兄弟ディレクトリ に分ける
2. `AGENTS.md` に `jj` 前提の運用を書く（意図伝達のため）
3. **`git` shim を入れる**
4. wrapper経由でエージェントを起動する
5. 可能なら `jj git colocation disable` でnon-colocatedに寄せる

`jj` を使っていてエージェントを複数走らせたい場合、まずはshimで `git` を物理的に止めるところから始めるのが現実的です。

## まとめ

* `AGENTS.md` だけではAIエージェントの `git` 利用は止まらない
* 各エージェントのpermission設定は方言違いで、マルチエージェント運用にはスケールしない
* PATHにshimを差し込んで `git` バイナリを遮断するのが、エージェント非依存で一番効く
* 根本対策としては `jj git colocation disable` でnon-colocatedに寄せる選択肢もあるが、GUI Gitクライアントが使えなくなるトレードオフがある

将来的にはこのあたり、もっと標準化されたツールが出てくると思います。それまではshimとwrapperで凌いでみるのはどうでしょうか。

## 参考

<https://docs.jj-vcs.dev/latest/git-compatibility/>  
<https://docs.jj-vcs.dev/latest/cli-reference/>  
<https://code.claude.com/docs/en/permissions>
