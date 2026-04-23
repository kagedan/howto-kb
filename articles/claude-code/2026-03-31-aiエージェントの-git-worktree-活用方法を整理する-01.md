---
id: "2026-03-31-aiエージェントの-git-worktree-活用方法を整理する-01"
title: "AIエージェントの Git worktree 活用方法を整理する"
url: "https://zenn.dev/to4iki/articles/2026-03-31-git-wt"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-03-31"
date_collected: "2026-03-31"
summary_by: "auto-rss"
---

AIコーディングエージェントの並列開発に限らず、ディレクトリ単位で作業コンテキストを隔離できるので、原則 Git worktree を利用するようにしている。

以下のXのポストのように、人間がマニュアルで worktree を管理（作成や削除など）するのではなく、AIエージェントが自律的に扱うケースが増えてきたと感じているため、AIが扱いやすい worktree ワークフローについて整理してみた。利用しているツールの紹介から、Claude Code との連携方法、カスタムスキルによる自動化までを順に説明する。

## git-wt

当初は組み込みの [git worktree コマンド](https://git-scm.com/docs/git-worktree) を利用したり、VS Code の [extension](https://marketplace.visualstudio.com/items?itemName=jackiotyu.git-worktree-manager) を使っていた。現在は k1Low/git-wt を利用している。worktree 作成時に任意の処理を実行するフックが設定できたり、コピーファイルを指定できたり、ディレクトリ配置を制御できたりと痒いところに手が届く。

gitのサブコマンドのように扱えるため、直感的に操作できるのが嬉しい。

<https://github.com/k1LoW/git-wt>

```
# worktree が存在しない場合には feat/123 が作成される
# 存在していたらそのディレクトリに移動する。
git wt feat/123
```

ちなみに、`.gitconfig` には以下のような設定を記載している。これで、tmux 利用時には、git-wt 経由で worktree を作成した際に、そのディレクトリで新しい window を起動するようになる。

.gitconfig

```
[wt]
  nocd = create
  hook = tmux neww -c \"$PWD\" -n \"$(basename -s .git `git remote get-url origin`):$(git branch --show-current)\"
```

## Claude Code と worktree

CLIから git コマンド経由で worktree を作成できるが、Claude Code 公式では `--worktree`（`-w`）フラグを使用して、worktree を作成し、その中で claude のプロセスを実行できる。ディレクトリは `<repo>/.claude/worktrees/<name>` に作成される。

そのため、`worktrees/` ディレクトリをgit管理から除外することを勧めている。私は、グローバルな ignore 設定で除外している。

~/.config/git/ignore

```
**/.claude/worktrees/
```

`claude -w` の特徴として、変更なしでセッションを終了すると worktree とブランチが自動削除される。変更ありで終了すると、残すか削除するかを確認してくれるなど、クリーンアップの挙動がよく設計されている。

```
claude --worktree feature-auth
# worktree名を省略した際には、ランダムな名前が設定される
claude --worktree
```

[https://code.claude.com/docs/ja/common-workflows#git-worktree-を使用して並列-claude-code-セッションを実行する](https://code.claude.com/docs/ja/common-workflows#git-worktree-%E3%82%92%E4%BD%BF%E7%94%A8%E3%81%97%E3%81%A6%E4%B8%A6%E5%88%97-claude-code-%E3%82%BB%E3%83%83%E3%82%B7%E3%83%A7%E3%83%B3%E3%82%92%E5%AE%9F%E8%A1%8C%E3%81%99%E3%82%8B)

## gitignoreしているファイルのコピー

worktree は `.gitignore` に定義しているファイルをコピーしない（つまり引き継がない）ので、例えばトークン情報などの環境変数を設定しているような`.env` ファイルに関しては、明示的にコピーする必要がある。

git-wt の場合、リポジトリの `.git/config` に対して `wt.copyignored` を利用できる。これは `.gitignore` で定義してあるものをすべてコピーするので、例えば不要な `node_modules/` などは別途 `wt.nocopy` で指定する必要がある。

```
git config wt.copyignored true
# node_modules はコピーしないようにする
git config --add wt.nocopy "node_modules/"
```

もしくは、`wt.copy` でコピー対象のみを指定できる。

```
git config --add wt.copy ".env"
```

### `.worktreeinclude`

Claude Code Desktop 経由で worktree を作成する際には、`.worktreeinclude` に記載されたファイルやディレクトリをコピーできる。

`.worktreeinclude` の Claude Code (CLI) への適用の [Issue](https://github.com/anthropics/claude-code/issues/15327) はクローズ済みなので、近日リリースされる見込み。

コピー対象を明示することに価値があるので、Claude Code Desktop 版を利用するかどうかに関わらず `.worktreeinclude` を作成しておくのが良いと考えている。

## カスタムスキル

Claude Code 起動時に `-w` フラグで簡単に worktree を作成できるようになったのは嬉しいが、できれば実装の単位で自律的に worktree を作成し、かつそれを `git-wt` 管理下で行いたい。

そこで、以下のような `git-wt` スキルを作成した。  
`claude -w` で作成した worktree のクリーンアップ処理と同様に、変更の有無で自動削除するかどうか分岐している。

<https://github.com/to4iki/dotfiles/blob/main/dot_claude/skills/git-wt/SKILL.md>

あとは、`AGENTS.md` / `CLAUDE.md` に以下のように、原則 `git-wt` スキルを利用するように記述しておく。

CLAUDE.md

```
## ワークフロー

軽微な修正以外の実装は、`git-wt` スキルを利用してworktreeで作業する。

- 適用条件:
  - Plan mode終了後、コード変更を伴う実装を開始する時
- 除外条件:
  - 単一ファイルの軽微な修正（typo、コメント追加等）
  - READMEやドキュメントのみの変更
```

### 注意点

今のところ、SubAgent の YAML フロントマターで `isolation: "worktree"` パラメータを設定している場合は、Claude Code の組み込みの worktree 作成が実行される。そのため、worktree の保存先 (.claude/worktrees/) はシステム固定となる。

プロンプトや、`CLAUDE.md` に 「Workerを起動する際には、`/git-wt` を利用すること」と記述することも考えたが、 git-wt 利用による作業ディレクトリの一貫性よりも、手順の簡素化を優先することにした。

例

```
- エージェントを起動する際、`isolation: "worktree"` の代わりに
各エージェントのプロンプト内で `git wt <branch> --nocd` を使わせること。
    - worktreeは `.wt/` 配下に作成する。
```

もしくは、プロンプトではなく、以下の記事のように、`WorktreeCreate` / `WorktreeRemove` Hook を git-wt に置き換えることもできそう。こちらの方が筋は良いが、今のところ困ってはいないのでもう少し運用しながら考えてみようと思う。（プランファイルのディレクトリ指定のように、`settings.json` で worktree の作成場所が指定できるようになったら嬉しい）

<https://sushichan044.hateblo.jp/entry/2026/02/21/174922>

## 最後に

組み込みの `claude -w` / `isolation: worktree` と カスタムスキル `git-wt` の役割について簡単にまとめた。

| 項目 | 組み込み `isolation: worktree` | スキル `git-wt` |
| --- | --- | --- |
| 用途 | subagent の自動分離（Agent ツール経由） | ユーザー主導で、任意の条件で worktree を作成して作業 |
| パス | `.claude/worktrees/` | `wt.basedir` で指定したパス。デフォルトは `.wt/` |
| 制御 | Claude Code ランタイムが管理 | ユーザー/スキルが管理 |
| ライフサイクル | subagent 終了時に自動クリーンアップ | `claude -w` の挙動に合わせ変更の有無でクリーンアップを分岐する |

worktree ディレクトリが分散する可能性はあるが、前述した通り今のところは大きく困っていないので併用している。必要が生じたら Hook を利用して、一元管理してみようと思う。

## 参考
