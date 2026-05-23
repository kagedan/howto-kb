---
id: "2026-05-22-claude-code-に-git-status-を読み込ませない設定とリポジトリ情報の記録を避ける-01"
title: "Claude Code に git status を読み込ませない設定と、リポジトリ情報の記録を避けるラッパー関数"
url: "https://qiita.com/CookieBox26/items/73eb7b280d5d6f9f1159"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-05-22"
date_collected: "2026-05-23"
summary_by: "auto-rss"
query: ""
---

Claude Code は、<b>デフォルトで起動時の `git status` の結果をシステムプロンプトに取り込みます。</b>この記事では、その取り込みを止める設定と、さらに `~/.claude.json` にリポジトリ情報を記録させたくない場合の回避策を記します。

### 要点

Claude Code は、<b>デフォルトで起動時の `git status` の結果をシステムプロンプトに取り込みます。</b>これを止めたい (`git status` の結果を勝手に判断材料として使ってほしくない) 場合は、`settings.json` に `"includeGitInstructions": false` を記入するか、環境変数 `CLAUDE_CODE_DISABLE_GIT_INSTRUCTIONS=1` を設定します。
<b>なお、`deny` 設定で `git` コマンド実行を禁止していたとしてもこれらの設定が必要です。</b>

ただし、上記の設定だけでは `~/.claude.json` の `"githubRepoPaths"` への記録は止まりません。そこまで避けるなら、Claude Code 起動時だけ `.git/` を退避する方法があります。

### `git status` の取り込みを止める方法
:::note info
**参考文献：** [Claude Code の設定 - Claude Code Docs](https://code.claude.com/docs/ja/settings)
:::

システムプロンプトに `git status` の結果が取り込まれるのを防ぐには、スコープの `settings.json` に次のように書きます。

```json
{
  "includeGitInstructions": false
}
```
または、環境変数として次を設定します (こちらが優先)。
```sh
export CLAUDE_CODE_DISABLE_GIT_INSTRUCTIONS=1
```

#### `deny` 設定だけでは取り込みが止まらない理由
`settings.json` で `"deny": ["Bash(git:*)"]` していればよいのでは、と思うかもしれませんが、これだけでは取り込みを防げません。`git status` の実行主体は AI エージェントでなく Claude 本体 (ハーネス) であり、権限設定が及ばないためです。

### `~/.claude.json` に記録されるリポジトリ情報
`git status` の取り込みを止めてもなお、Claude Code はワークルートが GitHub リポジトリかどうかを確認します。確認された結果は、状態ストアファイル `~/.claude.json` の `"githubRepoPaths"` キーに記録されます。つまり、「このワークルートはこのリポジトリである」という対応関係が保存されます。

このキーの中身を手動で削除しても、Claude Code を起動すると再び記録されます。記録を止めたい場合は、起動時だけ `.git/` を別名に退避し、起動後に戻す方法があります。

### Claude Code 起動時のみ `.git/` を退避するラッパー関数
:::note warn
- このラッパー関数は、10 秒間 `.git/` を `.abc/` にリネームします。Claude 起動時に git 操作をフックしているとか、リネームの影響がある場合は使えません。
- そのように使用に注意が必要な割に、何か効果があるわけではない (はず) です。AI エージェントに Git の情報を隠蔽したいなら、`"includeGitInstructions": false` とし、エージェントから git まわりの権限を奪っておけば足りるはずです。`~/.claude.json` 経由でリポジトリが漏洩するリスク (そんなリスクがあるかは不明) まで潰したい人とか、少しでも余計な情報を記録させたくない人向けです。
:::


以下のラッパー関数を `~/.bashrc` や `~/.zshrc` に書いておくと、`claude` 実行時に `.git/` を `.abc/` に退避し、10 秒後に戻します。

```sh:~/.bashrc ( claude Code 起動時のみ .git を .abc に退避して 10 秒で戻す )
_claude_run() {
  local hid=0
  [ -e .git ] && {  mv .git .abc && hid=1; }
  [ "$hid" = 1 ] && ( sleep 10; mv .abc .git ) &
  command claude "$@"
}
claude() {
  _claude_run "$@"
}
```
これにより、Claude Code 起動時のリポジトリ判定を回避し、`~/.claude.json` にワークルートと GitHub リポジトリの対応を記録させずに済みます。

### (参考) 起動ディレクトリ確認との併用
ちなみに、別の記事で[意図しないディレクトリでの Claude Code 起動を防ぐラッパー関数](https://qiita.com/CookieBox26/items/903122eaaf92e977baae)を書いていましたが、`.git/` 退避と併用できます。
```sh:~/.bashrc ( claude Code 起動時のみ .git を .abc に退避して 10 秒で戻す + 意図しないディレクトリでの起動時は警告 )
_claude_run() {
  local hid=0
  [ -e .git ] && {  mv .git .abc && hid=1; }
  [ "$hid" = 1 ] && ( sleep 10; mv .abc .git ) &
  command claude "$@"
}
claude_allowed_dirs=(
  # Claude Code 許可ディレクトリをここに書いておく
  "${HOME}/aaa"
  "${HOME}/bbb/ccc"
)
claude() {
  local current_dir
  current_dir=$(pwd)
  for dir in "${claude_allowed_dirs[@]}"; do
    [ "$current_dir" = "$dir" ] && { _claude_run "$@"; return; }
  done
  echo 'このディレクトリでは Claude Code の起動が想定されていません'
  read -p '本当に続行しますか？ (y/n): ' ans
  [ "$ans" = 'y' ] || { echo '中止します'; return; }
  _claude_run "$@"
}
```

### この対応を入れた経緯
- Claude Code エージェントに作業を依頼したら、意図しない判断をされ、理由を問うと「`git status` の結果にこうあったので」などと許可していない `git` コマンドの結果を持ち出してきたので、デフォルトで `git status` 結果が注入される仕様を知りました (最近ディレクトリ構成を変更するまで Claude Code 起動ルートが Git リポジトリではなかったので知りませんでした)。`git status` の結果を勝手に判断材料に入れてほしくないので、`"includeGitInstructions": false` と `CLAUDE_CODE_DISABLE_GIT_INSTRUCTIONS=1` を導入しました。
- それでも `~/.claude.json` へのリポジトリ情報の記録が止まらなかったので、リポジトリ情報のスキャンを防ぐラッパー関数も導入しました。
