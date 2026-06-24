---
id: "2026-06-23-claude-code-git-worktree-で安全に並列作業する-今どのセッションのどのブラン-01"
title: "Claude Code × git worktree で安全に並列作業する — 「今どのセッションの、どのブランチ？」を statusline で解決する"
url: "https://qiita.com/11akajet/items/083ba7ad03f2c158e04b"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-06-23"
date_collected: "2026-06-24"
summary_by: "auto-rss"
query: ""
---

はじめましての方ははじめまして、そうでない方はこんにちは。社内では「じぇっと」と呼ばれています。なぜそう呼ばれているかは追々お伝えできればいいかなと思います。

## 1. 並列で動かしたいけど、混ざるのが怖い

Claude Code を使っていると、「片方で機能を作りながら、もう片方で別のバグを直したい」と思う場面が出てきます。ターミナルをもう1枚開いて `claude` を起動すれば、確かに2つのセッションは同時に動きます。

ところが、ここに落とし穴があります。**同じディレクトリで2つのセッションを動かすと、両方が同じファイルを編集してしまう**のです。片方が `src/auth.ts` を書き換えている最中に、もう片方も同じファイルを触る。git のブランチは1つしかチェックアウトできないので、作業が混ざり、コミットも分けられません。結局「片方が終わるまでもう片方は待つ」ことになり、並列のうまみがありません。

この「混ざるのが怖い」を正面から解決するのが **git worktree** です。そして Claude Code は、この worktree をネイティブにサポートしています。この記事では、git worktree を知らない人でも追えるように基礎から説明し、最後に私が使っている「**今どのセッションがどのブランチで動いているか**を statusline に出す」工夫まで紹介します。

## 2. git worktree とは（はじめての人向けに）

まず前提から。普段の git では、1つのリポジトリにつき作業ディレクトリは1つ、チェックアウトできるブランチも一度に1つだけです。ブランチを切り替えたいときは `git switch` で「今いる場所」を丸ごと切り替えます。

**git worktree は、同じリポジトリに対して作業ディレクトリを複数持てるようにする機能**です。履歴やリモートは共有したまま、ディレクトリとブランチだけを分けられます。図にするとこんなイメージです。

```text
my-repo/                ← メインの作業ディレクトリ（例: main ブランチ）
my-repo-feature-auth/   ← worktree その1（feature-auth ブランチ）
my-repo-bugfix-123/     ← worktree その2（bugfix-123 ブランチ）
        ↑ どれも同じ .git の履歴・リモートを共有している
```

コマンドは3つ覚えれば十分です。

```bash
# 新しいブランチで worktree を作る（隣のディレクトリに作られる）
git worktree add ../my-repo-feature-auth -b feature-auth

# いま存在する worktree の一覧を見る
git worktree list

# 使い終わった worktree を片付ける
git worktree remove ../my-repo-feature-auth
```

これだけで、`my-repo-feature-auth/` の中では `feature-auth` ブランチを、元の `my-repo/` では `main` を、**同時に・別々に**触れるようになります。ファイルが物理的に別ディレクトリにあるので、作業中に同じファイルを直接上書きし合う事故を避けられます。もちろん後で同じ箇所を merge / rebase すれば競合は起こり得ますが、「機能開発」と「別件バグ修正」のように**文脈がはっきり違う作業を並列で進めたいとき**の土台になります。

> 各 worktree は独立したチェックアウトなので、`node_modules` や仮想環境などはそれぞれでセットアップが必要です。この点は後の「ハマりどころ」でも触れます。

## 3. Claude Code の worktree 連携

git worktree を手で管理してもいいのですが、Claude Code は worktree の作成・起動・後片付けまで面倒を見てくれます。

### `--worktree` で起動する

`claude` に `--worktree`（短縮形 `-w`）を渡すと、隔離された worktree を作り、その中でセッションを始めます。

```bash
claude --worktree feature-auth
```

これで `.claude/worktrees/feature-auth/` というディレクトリが作られ、`worktree-feature-auth` という新しいブランチ上でセッションが立ち上がります。別のターミナルで名前を変えて実行すれば、2つ目の隔離セッションが始まります。

```bash
claude --worktree bugfix-123
```

名前を省くと、`bright-running-fox` のような名前を自動で付けてくれます。

```bash
claude --worktree
```

### セッションの途中からでも

すでに起動しているセッションの中で「worktree で作業して」と頼めば、Claude が `EnterWorktree` ツールで worktree を作って移動してくれます。元の worktree はディスク上にそのまま残るので、あとで戻れます。

### gitignore されたファイルを持ち込む（`.worktreeinclude`）

worktree は新しいチェックアウトなので、`.env` のような git 管理外のファイルは存在しません。プロジェクトルートに `.worktreeinclude` を置くと、指定したファイルを新しい worktree に自動コピーしてくれます。書式は `.gitignore` と同じです。

```text
.env
.env.local
config/secrets.json
```

### 後片付け

セッションを終えるとき、Claude はクリーンアップしてくれます。

- **変更も新規コミットも無い場合**: worktree とブランチは自動で削除されます。
- **コミットされていない変更・新規コミットがある場合**: 残すか削除するか聞かれます。残せばあとで戻れます。
- **`-p`（非対話実行）の場合**: 終了プロンプトが無いので自動削除されません。`git worktree remove` で手動削除します。

> ヒント: `.claude/worktrees/` を `.gitignore` に追加しておくと、worktree の中身がメインのチェックアウトで「未追跡ファイル」として見えてしまうのを防げます。

ここまでで「複数セッションを安全に並列で回す」土台はできました。公式ドキュメント（[code.claude.com/docs/ja/worktrees](https://code.claude.com/docs/ja/worktrees)）にはさらに細かい設定（ベースブランチの選択、PR からの分岐、`WorktreeCreate` フック、非 Git VCS 対応）も載っています。

## 4. それでも起きる「今のセッションは、どのブランチ？」問題

並列で回せるようになると、今度は別の悩みが出てきます。**ターミナルが3枚、4枚と並んだとき、目の前のセッションがどのブランチで動いているのか分からなくなる**のです。

`feature-auth` のつもりで指示を出していたら、実は `bugfix-123` のセッションだった——これは地味に怖い事故です。worktree でファイルこそ分かれていても、「自分の認識」が迷子になると、間違ったセッションにコミットや指示を出しかねません。

この対策として、Claude Code の `/rename` コマンドでセッションに分かりやすい名前を付けておくのも役立ちます。たとえば `auth 実装`、`bugfix-123 対応` のように名前を付けておけば、あとからセッションを見返したり再開したりするときに迷いにくくなります。

ディレクトリ名やブランチ名で見分けることはできますが、作業に集中していると毎回確認するのは面倒です。**常に目に入る場所に、今のブランチも出ていてほしい**。そこで使えるのが Claude Code の statusline です。

## 5. statusline に作業ブランチを出す ★

Claude Code には **statusline**（画面下部の常時表示エリア）があり、`type: "command"` を指定すると、自作スクリプトの標準出力をそのまま表示できます。スクリプトには Claude Code から JSON が標準入力で渡され、その中に作業ディレクトリや **worktree のブランチ情報**が入っています。これを使って「今のセッションのブランチ」を常に表示してしまおう、というのが今回の工夫です。

私が使っているスクリプトの全文がこちらです。

```sh
#!/bin/sh
# Claude Code statusLine — git branch (worktree-aware)
# Input: JSON from stdin

input=$(cat)
cwd=$(echo "$input" | jq -r '.workspace.current_dir // empty')

# ANSI カラー
RESET=$(printf '\033[0m')
GREEN=$(printf '\033[32m')
RED=$(printf '\033[31m')

# Git ブランチ: --worktree セッションでは JSON の branch を優先し、無ければ git コマンド
branch=$(echo "$input" | jq -r '.worktree.branch // empty')
if [ -z "$branch" ] && [ -n "$cwd" ]; then
  branch=$(git -C "$cwd" --no-optional-locks symbolic-ref --short HEAD 2>/dev/null)
fi
if [ -z "$branch" ]; then
  branch=$(echo "$input" | jq -r '.workspace.git_worktree // empty')
fi

[ -z "$branch" ] && exit 0

# ブランチの色: main/master=赤, それ以外=緑
if [ "$branch" = "main" ] || [ "$branch" = "master" ]; then
  branch_color="$RED"
else
  branch_color="$GREEN"
fi

printf "%s%s%s\n" "$branch_color" "$branch" "$RESET"
```

### 何を表示しているか

出力はこんな見た目になります（実際は色付き）。

```text
------------------------------------------------
ステータスライン
------------------------------------------------
worktree-feature-auth
```

表示しているのは**worktree踏まえた今のブランチ名**だけです。`claude --worktree feature-auth` なら、Claude Code が作る実際のブランチ名は `worktree-feature-auth` なので、その名前が表示されます。これがセッションごとに出ることで「今どのブランチにいるのか」が一目で分かります。

### worktree を正しく拾う仕組み

肝はブランチの取り方です。`git symbolic-ref` で取るだけだと、状況によっては意図したブランチを拾えないことがあります。そこでこのスクリプトは、**Claude Code が JSON で渡してくれる `worktree.branch` を最優先**し、無いときだけ git コマンドにフォールバックしています。`workspace.git_worktree` はブランチ名ではなく worktree 名なので、最後の表示用ラベルとしてだけ使っています。

```sh
branch=$(echo "$input" | jq -r '.worktree.branch // empty')             # ① --worktree のブランチ名
[ -z "$branch" ] && branch=$(git -C "$cwd" ... symbolic-ref --short HEAD) # ② 任意の git worktree
[ -z "$branch" ] && branch=$(echo "$input" | jq -r '.workspace.git_worktree // empty') # ③ 最後の表示用
```

`claude --worktree feature-auth` で起動したセッションなら ① が効くので、`worktree-feature-auth` のような各 worktree のブランチがそれぞれの statusline に正しく出ます。3章で作った隔離セッションと、この表示がここでつながります。

### 色で「事故りやすい状態」を知らせる

もうひとつの工夫が色分けです。ブランチ名を `main` / `master` のときだけ**赤**、それ以外は緑で表示しています。

ブランチ名の赤は「**今 main にいるよ**」という警告色です。worktree を使っていても、うっかり元の `main` セッションで直接作業・コミットしかけることはあります。常に赤で目に入れば、その事故をかなり減らせます。

```text
main
  ↑ 赤 = main で作業中の警告
```

### 設定手順

1. スクリプトを保存します（例: `~/.claude/statusline-command.sh`）。`jq` が必要なので未導入なら入れておきます。

   ```bash
   chmod +x ~/.claude/statusline-command.sh
   ```

2. `~/.claude/settings.json` の `statusLine` に登録します。

   ```json
   {
     "statusLine": {
       "type": "command",
       "command": "~/.claude/statusline-command.sh"
     }
   }
   ```

3. Claude Code を開き直すと、画面下にブランチ名が出ます。`claude --worktree xxx` を別ターミナルで起動すれば、それぞれに別のブランチ名が表示されるはずです。

## 6. 並列ワークフロー実例

実際の1日の流れにすると、worktree のありがたみが分かります。たとえばこんな具合です。

1. **ターミナルA**で、本命の機能開発を始める。
   ```bash
   claude --worktree feature-auth
   ```
2. レビュー指摘が飛んできたので、**ターミナルB**で別ブランチを立てて修正に着手する。Aはそのまま動かしておく。
   ```bash
   claude --worktree bugfix-123
   ```
3. それぞれの statusline に `worktree-feature-auth` / `worktree-bugfix-123` が出ているので、**どちらのターミナルで何をしているか一目で分かる**。指示の出し間違いがない。
4. bugfix が終わったら、Bのセッションを閉じる。変更があれば「残す／削除」を聞かれるので、PR を出すまで残しておく。
5. Aに戻って機能開発の続き。Bの作業は一切混ざっていない。

ポイントは、**ファイルの隔離（worktree）と、認識の迷子防止（statusline）はセットで効く**ということです。片方だけだと、「混ざらないけど今どこか分からない」または「どこか分かるけど混ざる」の片手落ちになります。

## 7. まとめ・ハマりどころ

- **git worktree** は、1つのリポジトリで作業ディレクトリとブランチを複数持てる機能。並列作業でファイルが混ざらない土台になる。
- **Claude Code** は `claude --worktree` で worktree の作成・起動・後片付けまでやってくれる。
- それでも複数ターミナルだと「今どのセッション？」で迷うので、**statusline に作業ブランチを出す**と事故が減る。

最後に、ハマりやすい点を3つ。

- **初回は信頼ダイアログ**: あるディレクトリで初めて `--worktree` を使う前に、一度そのディレクトリで `claude` を実行して信頼ダイアログを承認しておく必要があります（未承認だと `--worktree` はエラーで終了します）。
- **`.claude/worktrees/` は `.gitignore` へ**: 未追跡ファイルとして見えるのを防ぐため。
- **各 worktree で環境構築が要る**: `node_modules` や `.env` は新しい worktree には無いので、`.worktreeinclude` でコピーするか、各 worktree で `npm install` などを実行します。

---

### 参考

- Claude Code 公式ドキュメント「worktree を使用して並列セッションを実行する」: <https://code.claude.com/docs/ja/worktrees>
- git worktree（git-scm）: <https://git-scm.com/docs/git-worktree>
- 参考にさせていただいた記事（hiraoku 氏 / Zenn）: <https://zenn.dev/hiraoku/articles/74f4b3083b582f>
