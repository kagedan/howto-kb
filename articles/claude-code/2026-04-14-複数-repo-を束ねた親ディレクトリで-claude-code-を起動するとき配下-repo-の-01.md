---
id: "2026-04-14-複数-repo-を束ねた親ディレクトリで-claude-code-を起動するとき配下-repo-の-01"
title: "複数 repo を束ねた親ディレクトリで Claude Code を起動するとき、配下 repo の skills も使いたい"
url: "https://zenn.dev/tasteck/articles/3d1f044aeaf491"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-14"
date_collected: "2026-04-15"
summary_by: "auto-rss"
---

## TL;DR

`Claude Code` の `project skills` は、普通に各リポジトリの中で運用していると思います。

ただ、自分は複数 repo をまたいで調査することが多く、そういうときは repo ごとに `Claude Code` を起動するより、関連する repo を束ねた親ディレクトリから起動したくなります。

そのままだと配下 repo の `project skills` をまとめて扱いにくいので、起動時だけ親ディレクトリ側の `.claude/skills` に symlink を張るようにしています。

## やりたいこと

イメージとしてはこんな構成です。

```
workspace/
├─ repos/
│  ├─ repo-a/
│  │  └─ .claude/skills/
│  │     └─ skill-a/
│  │        └─ SKILL.md
│  ├─ repo-b/
│  │  └─ .claude/skills/
│  │     └─ skill-b/
│  │        └─ SKILL.md
│  └─ repo-c/
│     └─ .claude/skills/
│        └─ skill-c/
│           └─ SKILL.md
└─ ...
```

この親ディレクトリで `Claude Code` を起動したときに、配下 repo の `project skills` も使えるようにしたい、という話です。

なお、この記事では `repos/*/.claude/skills/*` という構成を例にしていますが、ここは自分の運用に合わせたものです。  
同じ考え方で、手元のディレクトリ構成に合わせて読み替えてください。

## 関数

使っている関数はこれです。

```
claude() {
  emulate -L zsh

  local sd=".claude/skills"
  local -a links=()
  mkdir -p "$sd"

  local dir name
  for dir in repos/*/.claude/skills/*(/N); do
    [[ -f "$dir/SKILL.md" ]] || continue
    name=${dir:t}
    [[ -e "$sd/$name" ]] && { print -u2 "skip: $name"; continue }
    ln -s "${dir:A}" "$sd/$name"
    links+=("$sd/$name")
  done

  {
    command claude "$@"
  } always {
    rm -f "${links[@]}"
  }
}
```

やっていることは単純で、

* 配下 repo の `.claude/skills` を走査する
* `SKILL.md` があるものだけ拾う
* 親ディレクトリの `.claude/skills` に symlink を張る
* `claude` 終了後、その回で作った symlink だけ消す

という流れです。

ちなみに、こういう `shell wrapper` はCLIツールでわりとよくあるやり方みたいです。  
CLI 単体では親シェルの `cd` や環境変数変更を直接反映できないので、`.zshrc` に関数を生やしたり `eval "$(tool init zsh)"` で `shell` 側にコードを読ませたりします。  
今回も `claude` 自体を変えたいというより、起動前後に少しだけ親シェル側で準備と後始末をしたいので、この形にしています。

## ポイント

### `SKILL.md` があるものだけ対象にする

```
[[ -f "$dir/SKILL.md" ]] || continue
```

skill として成立しているものだけを拾っています。

### 作った symlink だけ後で消す

```
local -a links=()
...
links+=("$sd/$name")
...
rm -f "${links[@]}"
```

起動時に作った link だけを配列に積んでおいて、終了時にそれだけ消します。  
親ディレクトリ側にある別のものを巻き込みにくいので、この形にしています。

### 同名 skill があれば skip する

```
[[ -e "$sd/$name" ]] && { print -u2 "skip: $name"; continue }
```

同名の skill がすでにあれば上書きせずに skip します。  
単純ですが、挙動は明確です。

## この形の良いところ

このやり方の良いところは、元の運用をほとんど変えなくていいことです。

`project skills` の実体は各 repo に置いたままでよく、共通ディレクトリへのコピーもいりません。  
repo 側を更新すれば、次回起動時にそのまま反映されます。

親ディレクトリ側も常設の管理場所にはせず、`Claude Code` を起動するときだけ一時的に集約するだけで済みます。

## 注意点

同名の skill が複数 repo にあると、後続は `skip` されます。

また、この関数は skills を統合管理するものではありません。  
やっているのはあくまで、親ディレクトリから `Claude Code` を起動するときの見え方を揃えることです。

## 宣伝

このディレクトリ運用の背景にもなっている以下のようなツールを開発してます！  
<https://zenn.dev/tasteck/articles/59f56f67aa5584>  
<https://zenn.dev/tasteck/articles/50ecb1926a26a9>
